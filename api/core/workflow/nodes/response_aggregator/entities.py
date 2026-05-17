import math
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from graphon.entities.base_node_data import BaseNodeData
from graphon.enums import NodeType
from graphon.nodes.llm.entities import ModelConfig

from . import RESPONSE_AGGREGATOR_NODE_TYPE
from .strategies.synthesize import DEFAULT_SYNTHESIS_INSTRUCTION


class AggregationInputRef(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_id: str = Field(..., min_length=1)
    variable_selector: list[str] = Field(..., min_length=2)
    weight: float | list[str] = 1.0
    """Static float (per-source weight) OR a ``VariableSelector``-shaped
    ``list[str]`` (resolved at runtime against the variable pool, ADR-v3-15).
    Default ``1.0`` keeps inputs neutral relative to peers.

    A ``list[str]`` here MUST have ≥ 2 segments — same shape as
    ``variable_selector`` — so the runtime resolver can read it via
    ``variable_pool.get(...)``."""

    fallback_weight: float | None = None
    """Numeric fallback when a dynamic ``weight`` selector fails to
    resolve (variable not in pool / wrong type). ``None`` (default) =
    fail fast: the node raises ``WeightResolutionError`` and FAILs.
    Setting this to a number opts into a graceful-degrade mode where
    the per-source weight collapses to ``fallback_weight`` and the
    trace records a warning (ADR-v3-15)."""

    extra: dict[str, Any] = Field(default_factory=dict)
    """Per-source pass-through metadata. The synthesis prompt does not
    consume ``extra`` directly today, but it stays on the schema so DSL
    authors can ride extra context (e.g. ``{"confidence_tier": "high"}``)
    without forking the schema."""

    @field_validator("source_id")
    @classmethod
    def _source_id_not_blank(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("source_id must not be blank")
        # Normalize leading/trailing whitespace: the frontend dedup check
        # (default.ts) compares trimmed values, but the uniqueness guard on
        # this model runs against the raw value — without normalization,
        # `"model_a"` and `"model_a "` would survive as distinct keys in
        # `metadata.contributions`.
        return stripped

    @field_validator("variable_selector")
    @classmethod
    def _selector_segments_not_blank(cls, v: list[str]) -> list[str]:
        for i, seg in enumerate(v):
            if not seg or not seg.strip():
                raise ValueError(
                    f"variable_selector segment [{i}] must not be blank; "
                    "each segment must be a non-empty identifier"
                )
        return v

    @field_validator("weight", mode="before")
    @classmethod
    def _weight_selector_well_formed(cls, v: Any) -> float | list[str]:
        # ``bool`` is an ``int`` subclass — accepting it would silently
        # coerce ``True``/``False`` to ``1.0``/``0.0`` and mask schema
        # drift upstream. NaN / ±Inf would corrupt weighted-sum tallying.
        if isinstance(v, bool):
            raise ValueError(
                "weight must be a finite number or a VariableSelector list, "
                "not a bool (bool is an int subclass and would coerce silently)"
            )
        if isinstance(v, (int, float)):
            f = float(v)
            if not math.isfinite(f):
                raise ValueError(
                    f"weight must be finite; got {f} (NaN / Inf is rejected to "
                    "avoid corrupting weighted-sum tallying)"
                )
            return f
        if not isinstance(v, list):
            raise ValueError(
                "weight must be a finite number or a VariableSelector list"
            )
        if len(v) < 2:
            raise ValueError(
                "weight selector must have at least 2 segments "
                "(same shape as variable_selector)"
            )
        for i, seg in enumerate(v):
            if not isinstance(seg, str) or not seg or not seg.strip():
                raise ValueError(
                    f"weight selector segment [{i}] must not be blank"
                )
        return v

    @field_validator("fallback_weight", mode="before")
    @classmethod
    def _fallback_weight_finite(cls, v: Any) -> float | None:
        if v is None:
            return None
        if isinstance(v, bool):
            raise ValueError(
                "fallback_weight must be a finite number, not a bool"
            )
        if not isinstance(v, (int, float)):
            raise ValueError(
                f"fallback_weight must be a finite number, got {type(v).__name__}"
            )
        f = float(v)
        if not math.isfinite(f):
            raise ValueError(
                f"fallback_weight must be finite; got {f}"
            )
        return f


# Legacy fields from the pre-strip schema. ``BaseNodeData`` uses
# ``extra='allow'`` so unknown keys would otherwise drop into
# ``model_extra`` and silently be ignored — confusing for operators
# importing an old DSL who still see ``strategy_name: majority_vote``
# in the JSON but get the synthesis path at runtime. We reject them
# explicitly with a migration hint instead.
_DEPRECATED_FIELDS: tuple[str, ...] = ("strategy_name", "strategy_config")


class ResponseAggregatorNodeData(BaseNodeData):
    type: NodeType = RESPONSE_AGGREGATOR_NODE_TYPE

    inputs: list[AggregationInputRef] = Field(..., min_length=2)
    instruction: str = DEFAULT_SYNTHESIS_INSTRUCTION
    """Task instruction sent to the aggregation model alongside every
    upstream complete reply. Blank / whitespace-only values fall back
    to ``DEFAULT_SYNTHESIS_INSTRUCTION`` so the i18n tooltip ("Leave
    empty to use the built-in synthesis instruction") matches actual
    runtime behaviour."""

    model: ModelConfig
    """LLM that reads all upstream complete responses and writes the
    collaborative final answer. Always required — this node IS the
    full-response synthesis path."""

    @field_validator("instruction", mode="after")
    @classmethod
    def _blank_instruction_falls_back_to_default(cls, v: str) -> str:
        return v if v.strip() else DEFAULT_SYNTHESIS_INSTRUCTION

    @model_validator(mode="after")
    def _check_cross_field_rules(self) -> "ResponseAggregatorNodeData":
        # Reject legacy strategy fields. ``BaseNodeData`` is permissive
        # (extra='allow') so without this guard a stale DSL would import
        # successfully but ignore the configured strategy.
        extra = self.__pydantic_extra__ or {}
        stale = [name for name in _DEPRECATED_FIELDS if name in extra]
        if stale:
            raise ValueError(
                "response-aggregator no longer supports "
                f"{', '.join(repr(name) for name in stale)}; "
                "the node is now a synthesis-only path. Remove these "
                "fields and configure ``instruction`` + ``model`` instead."
            )

        seen: set[str] = set()
        for ref in self.inputs:
            if ref.source_id in seen:
                raise ValueError(
                    f"Duplicate source_id '{ref.source_id}' in inputs; "
                    "source_id must be unique within a single response-aggregator node"
                )
            seen.add(ref.source_id)

        if not self.model.provider.strip() or not self.model.name.strip():
            raise ValueError("model.provider and model.name are required")
        return self
