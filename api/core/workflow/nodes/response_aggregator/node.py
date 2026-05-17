import logging
import math
from collections.abc import Generator, Mapping, Sequence
from typing import Any, ClassVar

from graphon.enums import (
    NodeType,
    WorkflowNodeExecutionMetadataKey,
    WorkflowNodeExecutionStatus,
)
from graphon.model_runtime.entities.llm_entities import LLMUsage
from graphon.model_runtime.entities.message_entities import (
    PromptMessage,
    SystemPromptMessage,
    UserPromptMessage,
)
from graphon.node_events.base import NodeEventBase, NodeRunResult
from graphon.node_events.node import (
    ModelInvokeCompletedEvent,
    StreamChunkEvent,
    StreamCompletedEvent,
)
from graphon.nodes.base.node import Node
from graphon.nodes.llm import llm_utils
from graphon.nodes.llm.file_saver import LLMFileSaver
from graphon.nodes.llm.node import LLMNode
from graphon.nodes.llm.runtime_protocols import (
    PreparedLLMProtocol,
    PromptMessageSerializerProtocol,
)

from . import RESPONSE_AGGREGATOR_NODE_TYPE
from .entities import AggregationInputRef, ResponseAggregatorNodeData
from .exceptions import (
    MissingInputError,
    ModelSynthesisError,
    ResponseAggregatorNodeError,
    WeightResolutionError,
)
from .strategies import ResponseSignal
from .strategies.synthesize import SYSTEM_PROMPT, build_synthesis_user_prompt

logger = logging.getLogger(__name__)


class ResponseAggregatorNode(Node[ResponseAggregatorNodeData]):
    """Synthesize all upstream complete replies into one collaborative answer.

    The node collects every declared upstream reply, then invokes the
    configured aggregation model with a single prompt that fences each
    response as a candidate contribution. Output is the model's
    synthesized final answer.
    """

    node_type: ClassVar[NodeType] = RESPONSE_AGGREGATOR_NODE_TYPE
    _model_instance: PreparedLLMProtocol | None
    _prompt_message_serializer: PromptMessageSerializerProtocol | None
    _llm_file_saver: LLMFileSaver | None

    def __init__(
        self,
        node_id: str,
        config: ResponseAggregatorNodeData,
        *,
        graph_init_params: Any,
        graph_runtime_state: Any,
        model_instance: PreparedLLMProtocol | None = None,
        prompt_message_serializer: PromptMessageSerializerProtocol | None = None,
        llm_file_saver: LLMFileSaver | None = None,
    ) -> None:
        super().__init__(
            node_id=node_id,
            config=config,
            graph_init_params=graph_init_params,
            graph_runtime_state=graph_runtime_state,
        )
        self._model_instance = model_instance
        self._prompt_message_serializer = prompt_message_serializer
        self._llm_file_saver = llm_file_saver

    @classmethod
    def version(cls) -> str:
        return "1"

    @property
    def model_instance(self) -> PreparedLLMProtocol | None:
        """Prepared aggregation model; surfaced for the LLM quota layer."""
        return self._model_instance

    def _run(self) -> Generator[NodeEventBase, None, None]:
        node_data = self.node_data
        declared_source_count = len(node_data.inputs)

        try:
            signals, weights, weight_fallbacks = self._collect_inputs()
            yield from self._run_synthesis(
                signals=signals,
                weights=weights,
                weight_fallbacks=weight_fallbacks,
            )
        except ResponseAggregatorNodeError as e:
            logger.warning(
                "ResponseAggregatorNode %s failed: %s", self._node_id, e, exc_info=True
            )
            yield StreamCompletedEvent(
                node_run_result=NodeRunResult(
                    status=WorkflowNodeExecutionStatus.FAILED,
                    inputs={"source_count": declared_source_count},
                    error=str(e),
                    error_type=type(e).__name__,
                ),
            )

    def _run_synthesis(
        self,
        *,
        signals: list[ResponseSignal],
        weights: dict[str, float],
        weight_fallbacks: list[dict[str, Any]],
    ) -> Generator[NodeEventBase, None, None]:
        node_data = self.node_data
        model_instance = self._model_instance
        if model_instance is None:
            raise ModelSynthesisError(
                "aggregation model was not prepared for response-aggregator node"
            )
        llm_file_saver = self._llm_file_saver
        if llm_file_saver is None:
            raise ModelSynthesisError(
                "LLM file saver was not prepared for response-aggregator node"
            )

        model_instance.parameters = llm_utils.resolve_completion_params_variables(
            model_instance.parameters,
            self.graph_runtime_state.variable_pool,
        )
        prompt_messages: list[PromptMessage] = [
            SystemPromptMessage(content=SYSTEM_PROMPT),
            UserPromptMessage(
                content=build_synthesis_user_prompt(
                    instruction=node_data.instruction,
                    signals=signals,
                    weights=weights,
                )
            ),
        ]

        usage = LLMUsage.empty_usage()
        finish_reason: str | None = None
        completed = False
        final_text = ""
        streamed_text = ""

        try:
            invoke_events = LLMNode.invoke_llm(
                model_instance=model_instance,
                prompt_messages=prompt_messages,
                stop=model_instance.stop,
                structured_output_enabled=False,
                structured_output=None,
                file_saver=llm_file_saver,
                file_outputs=[],
                node_id=self._node_id,
                reasoning_format="separated",
            )
            for event in invoke_events:
                if isinstance(event, StreamChunkEvent):
                    streamed_text += event.chunk
                    yield event
                    continue
                if isinstance(event, ModelInvokeCompletedEvent):
                    completed = True
                    usage = event.usage
                    finish_reason = event.finish_reason
                    final_text = event.text
        except Exception as e:
            raise ModelSynthesisError(str(e)) from e

        if not completed:
            final_text = streamed_text

        process_data = self._build_process_data(
            prompt_messages=prompt_messages,
            usage=usage,
            finish_reason=finish_reason,
            weight_fallbacks=weight_fallbacks,
        )

        yield StreamChunkEvent(
            selector=[self._node_id, "text"],
            chunk="",
            is_final=True,
        )
        yield StreamCompletedEvent(
            node_run_result=NodeRunResult(
                status=WorkflowNodeExecutionStatus.SUCCEEDED,
                inputs={
                    "source_count": len(signals),
                    "model_provider": model_instance.provider,
                    "model_name": model_instance.model_name,
                },
                process_data=process_data,
                outputs={
                    "text": final_text,
                    "metadata": {
                        "model_provider": model_instance.provider,
                        "model_name": model_instance.model_name,
                        "finish_reason": finish_reason,
                        "contributions": {
                            s["source_id"]: s["text"] for s in signals
                        },
                        "weights": weights,
                    },
                },
                metadata={
                    WorkflowNodeExecutionMetadataKey.TOTAL_TOKENS: usage.total_tokens,
                    WorkflowNodeExecutionMetadataKey.TOTAL_PRICE: usage.total_price,
                    WorkflowNodeExecutionMetadataKey.CURRENCY: usage.currency,
                },
                llm_usage=usage,
            ),
        )

    def _build_process_data(
        self,
        *,
        prompt_messages: Sequence[PromptMessage],
        usage: LLMUsage,
        finish_reason: str | None,
        weight_fallbacks: list[dict[str, Any]],
    ) -> dict[str, Any]:
        model = self.node_data.model
        process_data: dict[str, Any] = {
            "model_provider": model.provider,
            "model_name": model.name,
            "finish_reason": finish_reason,
            "usage": usage.model_dump(mode="json"),
        }
        serializer = self._prompt_message_serializer
        if serializer is not None:
            process_data["prompts"] = serializer.serialize(
                model_mode=model.mode,
                prompt_messages=prompt_messages,
            )
        else:
            process_data["prompts"] = [
                {"role": message.role.value, "content": message.content}
                for message in prompt_messages
            ]
        if weight_fallbacks:
            process_data["weight_fallback_warnings"] = weight_fallbacks
        return process_data

    def _collect_inputs(
        self,
    ) -> tuple[
        list[ResponseSignal],
        dict[str, float],
        list[dict[str, Any]],
    ]:
        """Read upstream texts + resolve per-source weights.

        Returns:
            signals: ``ResponseSignal`` rows fed to the synthesis prompt.
            weights: ``source_id`` → effective float weight (surfaced
                inline in the user prompt and in ``outputs.metadata``).
            weight_fallbacks: per-source fallback events (surfaced on
                ``process_data`` so silent degrades are visible — empty
                in the happy path).

        Failure modes (ADR-v3-15 fail-fast):
            * Missing upstream variable → ``MissingInputError``.
            * Dynamic weight selector unresolvable AND no
              ``fallback_weight`` → ``WeightResolutionError``.
            * Dynamic weight selector unresolvable WITH
              ``fallback_weight`` → use fallback, log warning, append
              to ``weight_fallbacks``.
        """
        variable_pool = self.graph_runtime_state.variable_pool
        signals: list[ResponseSignal] = []
        weights: dict[str, float] = {}
        weight_fallbacks: list[dict[str, Any]] = []

        for ref in self.node_data.inputs:
            segment = variable_pool.get(ref.variable_selector)
            if segment is None:
                raise MissingInputError(
                    source_id=ref.source_id,
                    variable_selector=list(ref.variable_selector),
                )
            # Use ``Segment.text`` (graphon canonical text rendering) rather than
            # ``str(segment.value)``: the former normalizes NoneSegment -> "",
            # ObjectSegment / ArrayStringSegment -> JSON, empty arrays -> "".
            signals.append(
                ResponseSignal(
                    source_id=ref.source_id,
                    text=segment.text,
                    finish_reason="stop",
                    elapsed_ms=0,
                    error=None,
                )
            )

            weights[ref.source_id] = self._resolve_weight(
                ref, variable_pool, weight_fallbacks
            )

        return signals, weights, weight_fallbacks

    def _resolve_weight(
        self,
        ref: AggregationInputRef,
        variable_pool: Any,
        weight_fallbacks: list[dict[str, Any]],
    ) -> float:
        """Resolve ``ref.weight`` to a float.

        Static numeric branch returns directly. Dynamic
        ``VariableSelector``-shaped list branch reads the pool and
        coerces to float; coercion failure escalates to
        ``WeightResolutionError`` unless ``fallback_weight`` opts into
        the graceful-degrade path (ADR-v3-15).
        """
        weight_value = ref.weight
        if isinstance(weight_value, (int, float)):
            return float(weight_value)

        selector = list(weight_value)
        try:
            segment = variable_pool.get(selector)
            if segment is None:
                raise WeightResolutionError(
                    input_id=ref.source_id,
                    selector=selector,
                    reason="variable not present in pool",
                )
            value = segment.value
            if value is None:
                raise WeightResolutionError(
                    input_id=ref.source_id,
                    selector=selector,
                    reason="resolved value is None",
                )
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                # ``bool`` is a subclass of ``int`` — exclude explicitly so
                # ``True`` / ``False`` aren't silently coerced to ``1.0`` /
                # ``0.0`` (would mask schema drift upstream).
                raise WeightResolutionError(
                    input_id=ref.source_id,
                    selector=selector,
                    reason=f"resolved value is not numeric (got {type(value).__name__})",
                )
            resolved = float(value)
            if not math.isfinite(resolved):
                raise WeightResolutionError(
                    input_id=ref.source_id,
                    selector=selector,
                    reason=f"resolved value is not finite (got {resolved})",
                )
            return resolved
        except WeightResolutionError as exc:
            if ref.fallback_weight is None:
                raise
            logger.warning(
                "ResponseAggregatorNode %s: weight selector for source '%s' "
                "failed (%s); falling back to %s",
                self._node_id,
                ref.source_id,
                exc.reason,
                ref.fallback_weight,
            )
            weight_fallbacks.append(
                {
                    "source_id": ref.source_id,
                    "selector": selector,
                    "reason": exc.reason,
                    "fallback_weight": ref.fallback_weight,
                }
            )
            return float(ref.fallback_weight)

    @classmethod
    def _extract_variable_selector_to_variable_mapping(
        cls,
        *,
        graph_config: Mapping[str, Any],
        node_id: str,
        node_data: ResponseAggregatorNodeData,
    ) -> Mapping[str, Sequence[str]]:
        # Expose each input's upstream selector to the draft-variable preload
        # path (workflow_entry / workflow_app_runner). source_id is unique per
        # node (enforced in entities.py), so {node_id}.inputs.{source_id} is a
        # stable unique key — same shape as knowledge_retrieval_node.py:314.
        # Dynamic ``weight`` selectors are also surfaced so the variable is
        # preloaded ahead of resolution at runtime (ADR-v3-15).
        mapping: dict[str, Sequence[str]] = {}
        for ref in node_data.inputs:
            mapping[f"{node_id}.inputs.{ref.source_id}"] = list(ref.variable_selector)
            if isinstance(ref.weight, list):
                mapping[f"{node_id}.inputs.{ref.source_id}.weight"] = list(ref.weight)
        return mapping
