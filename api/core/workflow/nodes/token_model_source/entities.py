"""Pydantic schema for the ``token-model-source`` DSL surface (P3.B.1).

Two layers, on purpose — same split the parallel-ensemble node uses:

* :class:`SamplingParams` is the strongly-typed knob block. ``extra="forbid"``
  rejects yaml typos (``temprature: 0.7``) at boot rather than letting them
  silently no-op at run time. The fields are the cross-backend intersection
  surfaced through ``TokenStepParams`` (P3.B.0); backend-specific knobs
  (vLLM ``repetition_penalty`` etc.) ride on ``extra`` on the parent
  :class:`TokenModelSourceNodeData`.

* :class:`ModelInvocationSpec` is a :class:`TypedDict`, **not** a pydantic
  model. The wire shape crosses graph nodes via ``VariablePool``
  serialization (this node yields it as ``outputs.spec``, the
  parallel-ensemble node reads it back); using a TypedDict keeps the
  payload narrow and avoids forcing extension authors to import a
  Pydantic class just to consume the spec (mirrors the SPI's
  ``ChatMessage`` / ``GenerationParams`` choice — see
  ``parallel_ensemble/spi/backend.py``).

* :class:`TokenModelSourceNodeData` inherits ``BaseNodeData(extra="allow")``
  so legacy graph extras (``selected``, ``params``, ``paramSchemas``,
  ``datasource_label``, …) survive validation. Unlike the
  ``parallel-ensemble`` node, this node carries no SSRF / credential
  attack surface (no URL / api_key fields anywhere on it), so the
  forbidden-key validator from ``parallel_ensemble.entities`` is not
  duplicated here.
"""

from __future__ import annotations

from typing import Any, ClassVar, NotRequired, TypedDict

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from graphon.entities.base_node_data import BaseNodeData
from graphon.enums import NodeType

from . import TOKEN_MODEL_SOURCE_NODE_TYPE


class ChatMessageTemplate(BaseModel):
    """One chat-style message in chat-mode (``messages_template``).

    ``content`` accepts the same ``{{#node.field#}}`` placeholders as
    ``prompt_template``; the source node renders each entry against the
    variable pool at run time and emits the result as
    :class:`ModelInvocationSpec.messages` so the parallel-ensemble node
    can fan it through each backend's ``apply_template`` (e.g. llama.cpp's
    ``/apply-template`` endpoint, which knows the model's chat scaffold).

    Why a pydantic model here but a TypedDict on the wire
    (:class:`ChatMessageDict`): same split as ``SamplingParams`` →
    ``sampling_params: dict[str, Any]``. The DSL surface gets pydantic's
    ``extra="forbid"`` seat-belt against typos; the cross-node payload
    stays narrow so downstream consumers don't need to import a
    pydantic class to read it.
    """

    model_config = ConfigDict(extra="forbid")

    role: str = Field(..., min_length=1)
    content: str = ""


class ChatMessageDict(TypedDict):
    """Wire shape :class:`ModelInvocationSpec.messages` carries.

    Mirrors ``parallel_ensemble.spi.backend.ChatMessage`` field-for-field;
    duplicated locally so this package does not depend on the
    parallel-ensemble package's SPI surface (the dependency arrow points
    the other way — parallel-ensemble consumes specs, not vice versa).
    """

    role: str
    content: str


class SamplingParams(BaseModel):
    """Per-source sampling knobs the user types in the panel.

    Defaults match DEVELOPMENT_PLAN_v3 §4.3 (``top_k=10``,
    ``temperature=0.7``, ``max_tokens=1024``); the optional fields
    (``top_p`` / ``seed`` / ``stop``) default to "let the backend
    decide". The runtime aggregator merges these with
    ``TokenSourceRef.top_k_override`` (ADR-v3-6) and constructs the
    actual ``TokenStepParams`` per call (P3.B.3) — this layer is
    deliberately the user-facing form, not the
    ``MappingProxyType``-frozen runtime form.
    """

    model_config = ConfigDict(extra="forbid")

    top_k: int = Field(default=10, gt=0)
    temperature: float = Field(default=0.7, ge=0.0)
    max_tokens: int = Field(default=1024, gt=0)
    top_p: float | None = Field(default=None, gt=0.0, le=1.0)
    seed: int | None = None
    stop: list[str] = Field(default_factory=list)


class ModelInvocationSpec(TypedDict):
    """Cross-node payload yielded by ``token-model-source.outputs.spec``.

    Consumed by the ``parallel-ensemble`` node (P3.B.3) which reads N
    of these from the variable pool, instantiates one backend per
    ``model_alias`` via ``LocalModelRegistry``, and feeds each
    backend its own ``prompt`` + ``sampling_params`` per call. The
    TypedDict shape is the contract between the two nodes — kept
    narrow on purpose so a third-party token strategy can extend the
    payload via ``extra`` without forking the schema (Rv3-5).
    """

    model_alias: str
    prompt: str
    sampling_params: dict[str, Any]
    extra: dict[str, Any]
    messages: NotRequired[list[ChatMessageDict] | None]
    """Explicit chat-mode payload. Set when the source node was
    configured with ``messages_template``; the parallel-ensemble node
    detects this and routes through each backend's ``apply_template``
    so the model sees a properly-scaffolded chat turn instead of raw
    completion text. Absent / ``None`` means "no explicit messages" —
    in that case the consumer falls back to ``prompt`` (raw mode) or
    auto-wraps it as a single user-role message (chat-mode default for
    chat-template-capable backends) depending on ``raw_completion``."""
    raw_completion: NotRequired[bool]
    """Explicit opt-out of chat-template auto-wrap. When ``True`` the
    parallel-ensemble node sends ``prompt`` to the backend verbatim,
    even if the backend declares ``CHAT_TEMPLATE`` — i.e. the legacy
    PN.py raw-completion path stays available as a research escape
    hatch (chain-of-thought scaffolding the user wrote themselves,
    completion-style benchmarks, …). Absent / ``False`` means "fix
    chat-template-capable sources by default" so existing graphs that
    only set ``prompt_template`` stop emitting echo-the-question
    output without requiring a DSL migration. Mutually exclusive with
    a populated ``messages`` field — the schema validator on the
    source side rejects that combo at boot."""


class TokenModelSourceNodeData(BaseNodeData):
    """DSL payload for the ``token-model-source`` node.

    ``model_alias`` is the registry key the parallel-ensemble node
    will resolve against ``LocalModelRegistry`` at run start;
    validating it here against the registry would couple this schema
    to a runtime singleton — defer to the parallel-ensemble node's
    §9 startup validation, which already owns alias resolution.

    ``prompt_template`` accepts ``{{#node.field#}}`` placeholders
    parsed by ``VariableTemplateParser`` at run time; an empty
    template is allowed (``Field(default="")`` would also be valid)
    so the user can wire a single-variable pass-through without
    typing ``"{{#start.user_input#}}"`` literally.
    """

    type: NodeType = TOKEN_MODEL_SOURCE_NODE_TYPE

    model_alias: str = Field(..., min_length=1)
    prompt_template: str = ""
    messages_template: list[ChatMessageTemplate] | None = None
    """Explicit chat-mode template — list of ``{role, content}`` rows,
    each ``content`` accepting the same ``{{#node.field#}}``
    placeholders as ``prompt_template``. Mutually exclusive with a
    non-empty ``prompt_template`` (see model validator below) so the
    wire shape is unambiguous. Most users do *not* need to set this —
    the parallel-ensemble node auto-wraps ``prompt_template`` into a
    single user-role message when the target backend supports
    ``CHAT_TEMPLATE`` and ``raw_completion=False``. ``messages_template``
    is for the case where the user genuinely needs multi-role
    scaffolding (system prompt + few-shot examples + user turn)."""
    raw_completion: bool = False
    """Opt out of the chat-template auto-wrap. Default ``False``:
    chat-template-capable backends receive a properly-scaffolded
    user-role message (this is what fixes the
    "model echoes the question" failure mode for existing graphs that
    only set ``prompt_template``). Set ``True`` to force PN.py-style
    raw completion — research configs that intentionally feed naked
    priming text (chain-of-thought scaffolding the user wrote
    themselves, completion-style benchmarks, …) need this escape
    hatch. Mutually exclusive with ``messages_template`` (rejected by
    the model validator below)."""
    sampling_params: SamplingParams = Field(default_factory=SamplingParams)
    extra: dict[str, Any] = Field(default_factory=dict)

    NODE_TYPE: ClassVar[str] = TOKEN_MODEL_SOURCE_NODE_TYPE

    @field_validator("model_alias")
    @classmethod
    def _model_alias_not_blank(cls, v: str) -> str:
        # ``min_length=1`` rejects only the empty string; trim and
        # re-check so ``"   "`` is rejected too. Matches the
        # ``AggregationInputRef.source_id`` normalization rule.
        stripped = v.strip()
        if not stripped:
            raise ValueError("model_alias must not be blank")
        return stripped

    @model_validator(mode="after")
    def _check_chat_vs_raw_mutex(self) -> TokenModelSourceNodeData:
        # Empty ``messages_template`` is "chat mode set but useless" —
        # reject so the user cannot accidentally save an unusable config.
        # Also forbid setting both a non-empty ``prompt_template`` and
        # ``messages_template`` because there is no defined precedence;
        # one of the two is silently dropped at run time, which is the
        # exact ambiguity ADR-v3-16 split this responsibility out to
        # avoid.
        if self.messages_template is not None:
            if not self.messages_template:
                raise ValueError("messages_template must not be empty when set")
            if self.prompt_template:
                raise ValueError(
                    "prompt_template and messages_template are mutually exclusive; "
                    "use prompt_template (auto-wrapped for chat backends) or messages_template "
                    "for explicit multi-role scaffolding"
                )
            if self.raw_completion:
                # ``raw_completion=True`` says "send prompt verbatim" —
                # combining it with ``messages_template`` makes no sense
                # because the latter has no ``prompt`` slot to send.
                # Reject loudly so the contradiction surfaces at boot
                # rather than as a silently-dropped knob at run time.
                raise ValueError(
                    "raw_completion=True is incompatible with messages_template; "
                    "raw_completion only applies to prompt_template-based sources"
                )
        return self
