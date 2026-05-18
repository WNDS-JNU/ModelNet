"""``TokenModelSourceNode`` — graphon binding for ADR-v3-4 / v3-10.

The node is a *configuration holder*, not an executor: ``_run`` resolves
the prompt template against the variable pool and yields a single
:class:`StreamCompletedEvent` carrying a :class:`ModelInvocationSpec`.
Calling the model is deferred to the downstream ``parallel-ensemble``
node (P3.B.3) — keeping the two responsibilities split is what makes
"same model, different sampling" trivial to express on the canvas
without duplicating endpoint plumbing per source.

Why ``VariableTemplateParser`` instead of an extracted
``core/workflow/utils/prompt_render.py``: the LLM node lives in the
vendored ``graphon`` package and uses ``VariableTemplateParser``
directly with a stack of LLM-specific wrappers (jinja, chat-template,
files, memory, vision). Pulling out a shared util that this node
would be the only consumer of is the kind of premature abstraction
CLAUDE.md asks us to avoid; the ``VariableTemplateParser`` it would
wrap is itself the canonical seam already shared across nodes
(``agent_node`` / ``datasource_node`` use it the same way).
"""

from __future__ import annotations

import logging
from collections.abc import Generator, Mapping, Sequence
from typing import Any, ClassVar

from graphon.enums import NodeType, WorkflowNodeExecutionStatus
from graphon.node_events.base import NodeEventBase, NodeRunResult
from graphon.node_events.node import StreamCompletedEvent
from graphon.nodes.base.node import Node
from graphon.nodes.base.variable_template_parser import VariableTemplateParser

from . import TOKEN_MODEL_SOURCE_NODE_TYPE
from .entities import ChatMessageDict, ChatMessageTemplate, ModelInvocationSpec, TokenModelSourceNodeData
from .exceptions import PromptRenderError, TokenModelSourceNodeError

logger = logging.getLogger(__name__)


class TokenModelSourceNode(Node[TokenModelSourceNodeData]):
    node_type: ClassVar[NodeType] = TOKEN_MODEL_SOURCE_NODE_TYPE

    @classmethod
    def version(cls) -> str:
        return "1"

    def _run(self) -> Generator[NodeEventBase, None, None]:
        node_data = self.node_data
        try:
            # Two render branches; the schema validator already ruled out
            # the "both set" ambiguity. ``messages_template`` is rendered
            # row-by-row so ``PromptRenderError`` blames the right
            # surface (panel can show "row 2 system content references
            # missing #foo#" instead of a generic prompt-render fail).
            if node_data.messages_template is not None:
                rendered_messages = self._render_messages(node_data.messages_template)
                rendered_prompt = ""
            else:
                rendered_messages = None
                rendered_prompt = self._render_prompt(node_data.prompt_template)
        except TokenModelSourceNodeError as exc:
            logger.warning(
                "TokenModelSourceNode %s failed: %s",
                self._node_id,
                exc,
                exc_info=True,
            )
            yield StreamCompletedEvent(
                node_run_result=NodeRunResult(
                    status=WorkflowNodeExecutionStatus.FAILED,
                    inputs={"model_alias": node_data.model_alias},
                    error=str(exc),
                    error_type=type(exc).__name__,
                ),
            )
            return

        spec: ModelInvocationSpec = {
            "model_alias": node_data.model_alias,
            "prompt": rendered_prompt,
            "sampling_params": node_data.sampling_params.model_dump(),
            # ``dict(...)`` decouples the spec from ``node_data.extra`` so
            # any downstream mutation (an aggregator that injects a
            # backend-private key per call) does not bleed back into the
            # parsed node-data instance.
            "extra": dict(node_data.extra),
            # ``None`` means "inherit the registered alias"; a boolean
            # is a per-source override the parallel-ensemble consumer
            # applies only on the registry-backed path.
            "expose_raw_logits": node_data.expose_raw_logits,
            "messages": rendered_messages,
            "raw_completion": node_data.raw_completion,
            # ``inline_spec`` rides through to the parallel-ensemble
            # consumer untouched. ``None`` (the registry-backed path)
            # is left in the dict on purpose so the wire shape stays
            # stable across both modes — the consumer treats absent
            # and ``None`` identically.
            "inline_spec": (
                dict(node_data.inline_spec) if node_data.inline_spec is not None else None
            ),
        }
        # Surface ``model_alias`` as a top-level output too: downstream
        # nodes that only need the alias to fan out (panels / debug
        # views) can read ``outputs.model_alias`` directly without
        # reaching into the spec dict.
        yield StreamCompletedEvent(
            node_run_result=NodeRunResult(
                status=WorkflowNodeExecutionStatus.SUCCEEDED,
                inputs={"model_alias": node_data.model_alias},
                outputs={
                    "spec": spec,
                    "model_alias": node_data.model_alias,
                },
            ),
        )

    def _render_messages(
        self,
        templates: list[ChatMessageTemplate],
    ) -> list[ChatMessageDict]:
        """Render every ``content`` in ``messages_template`` against the pool.

        Each row's ``role`` rides through verbatim (the chat scaffold
        decides whether it is a valid role for the target model — the
        backend's ``apply_template`` is the canonical authority on that).
        ``content`` reuses :meth:`_render_prompt`'s rendering so research
        configs that mix raw and chat sources see byte-identical
        substitution semantics across both paths.
        """
        return [
            {"role": tmpl.role, "content": self._render_prompt(tmpl.content)}
            for tmpl in templates
        ]

    def _render_prompt(self, template: str) -> str:
        """Resolve ``{{#node.field#}}`` placeholders against the variable pool.

        ``VariableTemplateParser.format`` already handles non-string
        segments (lists / dicts / numbers / bools) via ``str(...)``;
        we additionally use ``Segment.text`` so ``NoneSegment``
        renders as ``""`` and ``ObjectSegment`` / ``ArrayStringSegment``
        render as JSON — matches the canonical renderer used by
        ``response_aggregator/node.py`` and the rest of graphon.

        Raises ``PromptRenderError`` when any selector fails to
        resolve so the node FAILs with a structured error instead of
        silently leaving the placeholder in the rendered prompt.
        """
        parser = VariableTemplateParser(template)
        selectors = parser.extract_variable_selectors()
        if not selectors:
            return template

        variable_pool = self.graph_runtime_state.variable_pool
        inputs: dict[str, str] = {}
        for selector in selectors:
            segment = variable_pool.get(list(selector.value_selector))
            if segment is None:
                raise PromptRenderError(
                    template=template,
                    missing_var=selector.variable,
                    reason="variable not present in pool",
                )
            inputs[selector.variable] = segment.text
        return parser.format(inputs)

    @classmethod
    def _extract_variable_selector_to_variable_mapping(
        cls,
        *,
        graph_config: Mapping[str, Any],
        node_id: str,
        node_data: TokenModelSourceNodeData,
    ) -> Mapping[str, Sequence[str]]:
        # Expose every ``{{#upstream.field#}}`` reference in the prompt
        # template to the draft-variable preload path so the
        # workflow runtime materialises the upstream value before
        # ``_run`` resolves it. ``selector.variable`` is the full
        # ``#upstream.field#`` form (with hashes) — the framework
        # convention is to namespace the key with the consuming
        # ``node_id`` so multiple nodes can reference the same
        # upstream variable without colliding (matches the LLM /
        # agent / datasource node pattern; see graphon
        # ``Node.extract_variable_selector_to_variable_mapping``
        # docstring).
        mapping: dict[str, Sequence[str]] = {}
        # Walk both surfaces — ``prompt_template`` and every
        # ``messages_template[i].content`` — so the preload path
        # materialises upstream values the chat-mode renderer needs too.
        # The schema validator forbids both being set simultaneously, so
        # in practice only one branch contributes; iterating both is
        # cheaper than re-deriving "which mode?" here, and keeps the
        # mapping correct if a future schema change ever loosens the
        # mutex.
        templates: list[str] = [node_data.prompt_template]
        if node_data.messages_template is not None:
            templates.extend(msg.content for msg in node_data.messages_template)
        for template in templates:
            for selector in VariableTemplateParser(template).extract_variable_selectors():
                mapping[f"{node_id}.{selector.variable}"] = list(selector.value_selector)
        return mapping
