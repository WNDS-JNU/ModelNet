import pytest
from pydantic import ValidationError

from core.workflow.nodes.response_aggregator import RESPONSE_AGGREGATOR_NODE_TYPE
from core.workflow.nodes.response_aggregator.entities import (
    AggregationInputRef,
    ResponseAggregatorNodeData,
)
from core.workflow.nodes.response_aggregator.strategies.synthesize import (
    DEFAULT_SYNTHESIS_INSTRUCTION,
)


class TestAggregationInputRef:
    def test_valid_two_segment_selector(self):
        ref = AggregationInputRef(source_id="gpt4", variable_selector=["node_a", "text"])
        assert ref.source_id == "gpt4"
        assert ref.variable_selector == ["node_a", "text"]

    def test_valid_path_segments_allowed(self):
        ref = AggregationInputRef(
            source_id="gpt4",
            variable_selector=["node_a", "text", "0", "content"],
        )
        assert len(ref.variable_selector) == 4

    def test_selector_too_short_rejected(self):
        with pytest.raises(ValidationError):
            AggregationInputRef(source_id="gpt4", variable_selector=["only_one"])

    def test_selector_empty_rejected(self):
        with pytest.raises(ValidationError):
            AggregationInputRef(source_id="gpt4", variable_selector=[])

    def test_blank_selector_segment_rejected(self):
        with pytest.raises(ValidationError):
            AggregationInputRef(source_id="gpt4", variable_selector=["node_a", "  "])

    def test_empty_selector_segment_rejected(self):
        with pytest.raises(ValidationError):
            AggregationInputRef(source_id="gpt4", variable_selector=["node_a", ""])

    def test_blank_source_id_rejected(self):
        with pytest.raises(ValidationError):
            AggregationInputRef(source_id="  ", variable_selector=["node_a", "text"])

    def test_empty_source_id_rejected(self):
        with pytest.raises(ValidationError):
            AggregationInputRef(source_id="", variable_selector=["node_a", "text"])

    def test_extra_field_rejected(self):
        with pytest.raises(ValidationError):
            AggregationInputRef.model_validate(
                {
                    "source_id": "gpt4",
                    "variable_selector": ["node_a", "text"],
                    "unknown_field": "x",
                }
            )

    def test_static_weight_defaults_to_one(self):
        ref = AggregationInputRef(source_id="m1", variable_selector=["n", "text"])
        assert ref.weight == 1.0
        assert ref.fallback_weight is None
        assert ref.extra == {}

    def test_static_weight_accepts_float(self):
        ref = AggregationInputRef(
            source_id="m1", variable_selector=["n", "text"], weight=0.7
        )
        assert ref.weight == 0.7

    def test_dynamic_weight_accepts_variable_selector(self):
        ref = AggregationInputRef(
            source_id="m1",
            variable_selector=["n", "text"],
            weight=["weights_node", "m1"],
        )
        assert ref.weight == ["weights_node", "m1"]

    def test_dynamic_weight_too_short_rejected(self):
        with pytest.raises(ValidationError, match="at least 2 segments"):
            AggregationInputRef(
                source_id="m1",
                variable_selector=["n", "text"],
                weight=["only_one"],
            )

    def test_dynamic_weight_blank_segment_rejected(self):
        with pytest.raises(ValidationError, match="must not be blank"):
            AggregationInputRef(
                source_id="m1",
                variable_selector=["n", "text"],
                weight=["weights_node", "  "],
            )

    def test_fallback_weight_accepts_numeric(self):
        ref = AggregationInputRef(
            source_id="m1",
            variable_selector=["n", "text"],
            weight=["w", "m1"],
            fallback_weight=0.5,
        )
        assert ref.fallback_weight == 0.5

    def test_static_weight_bool_rejected(self):
        # ``True`` is an int subclass — would silently coerce to 1.0,
        # masking schema drift. Reject explicitly.
        with pytest.raises(ValidationError, match="bool"):
            AggregationInputRef(
                source_id="m1",
                variable_selector=["n", "text"],
                weight=True,
            )

    def test_static_weight_nan_rejected(self):
        with pytest.raises(ValidationError, match="finite"):
            AggregationInputRef(
                source_id="m1",
                variable_selector=["n", "text"],
                weight=float("nan"),
            )

    def test_static_weight_inf_rejected(self):
        with pytest.raises(ValidationError, match="finite"):
            AggregationInputRef(
                source_id="m1",
                variable_selector=["n", "text"],
                weight=float("inf"),
            )

    def test_fallback_weight_bool_rejected(self):
        with pytest.raises(ValidationError, match="bool"):
            AggregationInputRef(
                source_id="m1",
                variable_selector=["n", "text"],
                weight=["w", "m1"],
                fallback_weight=False,
            )

    def test_fallback_weight_nan_rejected(self):
        with pytest.raises(ValidationError, match="finite"):
            AggregationInputRef(
                source_id="m1",
                variable_selector=["n", "text"],
                weight=["w", "m1"],
                fallback_weight=float("nan"),
            )

    def test_fallback_weight_inf_rejected(self):
        with pytest.raises(ValidationError, match="finite"):
            AggregationInputRef(
                source_id="m1",
                variable_selector=["n", "text"],
                weight=["w", "m1"],
                fallback_weight=float("-inf"),
            )

    def test_extra_accepts_arbitrary_dict(self):
        ref = AggregationInputRef(
            source_id="m1",
            variable_selector=["n", "text"],
            extra={"confidence_tier": "high", "score": 0.95},
        )
        assert ref.extra == {"confidence_tier": "high", "score": 0.95}

    def test_source_id_leading_trailing_whitespace_is_stripped(self):
        # Frontend dedup (default.ts) compares trimmed values — backend
        # must normalize too, otherwise `"model_a"` and `"model_a "` survive
        # as distinct contributions/keys.
        ref = AggregationInputRef(
            source_id="  gpt4  ",
            variable_selector=["node_a", "text"],
        )
        assert ref.source_id == "gpt4"


def _valid_model_payload() -> dict:
    return {
        "provider": "openai",
        "name": "gpt-4o-mini",
        "mode": "chat",
        "completion_params": {"temperature": 0.2},
    }


class TestResponseAggregatorNodeData:
    @staticmethod
    def _valid_inputs():
        return [
            {"source_id": "gpt4", "variable_selector": ["node_a", "text"]},
            {"source_id": "claude", "variable_selector": ["node_b", "text"]},
        ]

    def test_defaults_applied(self):
        data = ResponseAggregatorNodeData(
            inputs=self._valid_inputs(), model=_valid_model_payload()
        )
        assert data.type == RESPONSE_AGGREGATOR_NODE_TYPE
        assert data.instruction == DEFAULT_SYNTHESIS_INSTRUCTION
        assert data.model.name == "gpt-4o-mini"

    def test_instruction_override_accepted(self):
        data = ResponseAggregatorNodeData(
            inputs=self._valid_inputs(),
            instruction="merge the answers",
            model=_valid_model_payload(),
        )
        assert data.instruction == "merge the answers"

    def test_inputs_too_few_rejected(self):
        with pytest.raises(ValidationError):
            ResponseAggregatorNodeData(
                inputs=[{"source_id": "gpt4", "variable_selector": ["node_a", "text"]}],
                model=_valid_model_payload(),
            )

    def test_duplicate_source_id_rejected(self):
        with pytest.raises(ValidationError) as exc:
            ResponseAggregatorNodeData(
                inputs=[
                    {"source_id": "gpt4", "variable_selector": ["node_a", "text"]},
                    {"source_id": "gpt4", "variable_selector": ["node_b", "text"]},
                ],
                model=_valid_model_payload(),
            )
        assert "Duplicate source_id" in str(exc.value)

    def test_duplicate_source_id_rejected_after_trim(self):
        # Regression for the frontend/backend divergence: `"gpt4"` and
        # `"gpt4 "` must collide at the uniqueness guard because the
        # field validator strips before the model-level check runs.
        with pytest.raises(ValidationError) as exc:
            ResponseAggregatorNodeData(
                inputs=[
                    {"source_id": "gpt4", "variable_selector": ["node_a", "text"]},
                    {"source_id": "gpt4 ", "variable_selector": ["node_b", "text"]},
                ],
                model=_valid_model_payload(),
            )
        assert "Duplicate source_id" in str(exc.value)

    def test_model_is_required(self):
        with pytest.raises(ValidationError):
            ResponseAggregatorNodeData(inputs=self._valid_inputs())  # type: ignore[call-arg]

    def test_blank_model_provider_rejected(self):
        with pytest.raises(ValidationError) as exc:
            ResponseAggregatorNodeData(
                inputs=self._valid_inputs(),
                model={
                    "provider": "  ",
                    "name": "gpt-4o-mini",
                    "mode": "chat",
                    "completion_params": {},
                },
            )
        assert "model.provider" in str(exc.value)

    def test_blank_instruction_falls_back_to_default(self):
        # The i18n tooltip promises "leave empty to use the built-in
        # synthesis instruction" — the backend must honour that promise.
        data = ResponseAggregatorNodeData(
            inputs=self._valid_inputs(),
            instruction="",
            model=_valid_model_payload(),
        )
        assert data.instruction == DEFAULT_SYNTHESIS_INSTRUCTION

    def test_whitespace_only_instruction_falls_back_to_default(self):
        data = ResponseAggregatorNodeData(
            inputs=self._valid_inputs(),
            instruction="   \n\t  ",
            model=_valid_model_payload(),
        )
        assert data.instruction == DEFAULT_SYNTHESIS_INSTRUCTION

    @pytest.mark.parametrize(
        ("deprecated_field", "deprecated_value"),
        [
            ("strategy_name", "majority_vote"),
            ("strategy_config", {"answer_extract_regex": r"\(([A-D])\)"}),
        ],
    )
    def test_legacy_strategy_fields_rejected(
        self, deprecated_field: str, deprecated_value: object
    ):
        # BaseNodeData uses extra='allow', so without an explicit check
        # legacy DSL keys would silently land in model_extra. The
        # node-level validator must surface them with a migration hint.
        with pytest.raises(ValidationError) as exc:
            ResponseAggregatorNodeData.model_validate(
                {
                    "inputs": self._valid_inputs(),
                    "model": _valid_model_payload(),
                    deprecated_field: deprecated_value,
                }
            )
        message = str(exc.value)
        assert deprecated_field in message
        assert "synthesis-only" in message
