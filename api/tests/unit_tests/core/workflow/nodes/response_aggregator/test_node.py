"""Unit tests for ResponseAggregatorNode.

Covers:
- ``_collect_inputs`` segment-text normalization (NoneSegment / ObjectSegment
  / ArrayStringSegment) and weight resolution branches.
- ``extract_variable_selector_to_variable_mapping`` exposing each input and
  dynamic-weight selector.
- End-to-end ``_run`` with a fake streaming aggregation model: synthesis
  prompt assembly, success outputs/metadata, and FAILED paths.
"""

import pytest

from core.workflow.nodes.response_aggregator import ResponseAggregatorNode
from core.workflow.nodes.response_aggregator.exceptions import (
    MissingInputError,
    ModelSynthesisError,
    WeightResolutionError,
)
from graphon.enums import WorkflowNodeExecutionStatus
from graphon.model_runtime.entities.llm_entities import (
    LLMResultChunk,
    LLMResultChunkDelta,
    LLMUsage,
)
from graphon.model_runtime.entities.message_entities import AssistantPromptMessage
from graphon.runtime.variable_pool import VariablePool


def _model_payload() -> dict:
    return {
        "provider": "openai",
        "name": "gpt-4o-mini",
        "mode": "chat",
        "completion_params": {"temperature": 0.2},
    }


class _PromptSerializer:
    def serialize(self, *, model_mode, prompt_messages):
        return [
            {"role": message.role.value, "content": message.content}
            for message in prompt_messages
        ]


class _StreamingAggregationModel:
    provider = "openai"
    model_name = "gpt-4o-mini"
    stop = None

    def __init__(self, text: str = "Synthesized answer") -> None:
        self.parameters = {"temperature": 0.2}
        self.text = text
        self.prompt_messages = []

    def invoke_llm(self, *, prompt_messages, model_parameters, tools, stop, stream):
        self.prompt_messages = list(prompt_messages)
        self.parameters_seen = dict(model_parameters)
        assert stream is True

        def _chunks():
            yield LLMResultChunk(
                model=self.model_name,
                delta=LLMResultChunkDelta(
                    index=0,
                    message=AssistantPromptMessage(content=self.text),
                    usage=LLMUsage.empty_usage(),
                    finish_reason="stop",
                ),
            )

        return _chunks()

    def invoke_llm_with_structured_output(self, **kwargs):  # pragma: no cover
        raise NotImplementedError


def _make_node(
    pool: VariablePool,
    node_data_payload: dict,
    model: _StreamingAggregationModel | None = None,
    *,
    inject_model: bool = True,
) -> ResponseAggregatorNode:
    """Build a node bypassing Node.__init__ (which needs full graph_init_params).

    We only exercise `_run` / `_collect_inputs`, which read `_node_data`,
    `_node_id`, `graph_runtime_state.variable_pool`, and the LLM deps.
    """
    node = ResponseAggregatorNode.__new__(ResponseAggregatorNode)
    node._node_id = "agg_1"

    class _RS:
        pass

    rs = _RS()
    rs.variable_pool = pool
    node.graph_runtime_state = rs
    node._node_data = ResponseAggregatorNode._node_data_type.model_validate(
        node_data_payload
    )
    if inject_model:
        node._model_instance = model or _StreamingAggregationModel()
        node._prompt_message_serializer = _PromptSerializer()
        node._llm_file_saver = object()
    else:
        node._model_instance = None
        node._prompt_message_serializer = None
        node._llm_file_saver = None
    return node


def _two_input_payload(extra: dict | None = None) -> dict:
    payload: dict = {
        "title": "agg",
        "inputs": [
            {"source_id": "a", "variable_selector": ["llm_a", "text"]},
            {"source_id": "b", "variable_selector": ["llm_b", "text"]},
        ],
        "model": _model_payload(),
    }
    if extra:
        payload.update(extra)
    return payload


class TestSegmentTextNormalization:
    """`_collect_inputs` must use Segment.text (graphon canonical) not
    str(segment.value)."""

    def test_none_segment_renders_as_empty_string(self):
        pool = VariablePool()
        pool.add(["llm_a", "text"], "real")
        pool.add(["llm_b", "text"], None)  # NoneSegment, .text == ""
        node = _make_node(pool, _two_input_payload())

        signals, _, _ = node._collect_inputs()
        assert [s["text"] for s in signals] == ["real", ""]

    def test_object_segment_renders_as_json_not_python_repr(self):
        pool = VariablePool()
        pool.add(["llm_a", "text"], "hello")
        pool.add(["llm_b", "text"], {"city": "Paris", "score": 0.9})
        node = _make_node(pool, _two_input_payload())

        signals, _, _ = node._collect_inputs()
        rendered = signals[1]["text"]
        assert '"city": "Paris"' in rendered
        assert "'city': 'Paris'" not in rendered

    def test_array_string_segment_renders_as_json_not_python_repr(self):
        pool = VariablePool()
        pool.add(["llm_a", "text"], "alpha")
        pool.add(["llm_b", "text"], ["one", "two", "three"])
        node = _make_node(pool, _two_input_payload())

        signals, _, _ = node._collect_inputs()
        rendered = signals[1]["text"]
        assert rendered == '["one", "two", "three"]'

    def test_empty_array_renders_as_empty_string(self):
        # ArraySegment.text specializes empty arrays to "" rather than "[]".
        pool = VariablePool()
        pool.add(["llm_a", "text"], "kept")
        pool.add(["llm_b", "text"], [])
        node = _make_node(pool, _two_input_payload())

        signals, _, _ = node._collect_inputs()
        assert [s["text"] for s in signals] == ["kept", ""]


class TestExtractVariableSelectorMapping:
    """`_extract_variable_selector_to_variable_mapping` must expose every
    inputs[*].variable_selector so single-step debug + draft-variable preload
    can load upstream vars before `_run`."""

    def _build_config(self, node_id: str, inputs_payload: list[dict]) -> dict:
        return {
            "id": node_id,
            "data": {
                "title": "agg",
                "inputs": inputs_payload,
                "model": _model_payload(),
            },
        }

    def test_mapping_exposes_each_input_selector(self):
        config = self._build_config(
            "agg_node_1",
            [
                {"source_id": "a", "variable_selector": ["llm_a", "text"]},
                {"source_id": "b", "variable_selector": ["llm_b", "text"]},
                {"source_id": "c", "variable_selector": ["llm_c", "text"]},
            ],
        )
        mapping = ResponseAggregatorNode.extract_variable_selector_to_variable_mapping(
            graph_config={}, config=config
        )

        assert dict(mapping) == {
            "agg_node_1.inputs.a": ["llm_a", "text"],
            "agg_node_1.inputs.b": ["llm_b", "text"],
            "agg_node_1.inputs.c": ["llm_c", "text"],
        }

    def test_mapping_preserves_multi_segment_selectors(self):
        config = self._build_config(
            "n1",
            [
                {
                    "source_id": "deep",
                    "variable_selector": ["llm_a", "structured_output", "city"],
                },
                {"source_id": "shallow", "variable_selector": ["llm_b", "text"]},
            ],
        )
        mapping = ResponseAggregatorNode.extract_variable_selector_to_variable_mapping(
            graph_config={}, config=config
        )
        assert mapping["n1.inputs.deep"] == [
            "llm_a",
            "structured_output",
            "city",
        ]
        assert mapping["n1.inputs.shallow"] == ["llm_b", "text"]

    def test_dynamic_weight_selector_surfaces_in_mapping(self):
        config = self._build_config(
            "agg_node",
            [
                {
                    "source_id": "a",
                    "variable_selector": ["llm_a", "text"],
                    "weight": ["weights", "a"],
                },
                {
                    "source_id": "b",
                    "variable_selector": ["llm_b", "text"],
                    # Static weight → no extra mapping entry.
                },
            ],
        )
        mapping = ResponseAggregatorNode.extract_variable_selector_to_variable_mapping(
            graph_config={}, config=config
        )
        assert dict(mapping) == {
            "agg_node.inputs.a": ["llm_a", "text"],
            "agg_node.inputs.a.weight": ["weights", "a"],
            "agg_node.inputs.b": ["llm_b", "text"],
        }


class TestRunSynthesis:
    """End-to-end `_run()` invoking the aggregation model with all upstream replies."""

    def test_synthesize_invokes_model_with_complete_upstream_responses(self):
        pool = VariablePool()
        pool.add(["llm_a", "text"], "First model says Paris.")
        pool.add(["llm_b", "text"], "Second model agrees: Paris.")
        model = _StreamingAggregationModel("Final: Paris.")
        node = _make_node(
            pool,
            _two_input_payload({"instruction": "Return the shared final answer."}),
            model,
        )

        events = list(node._run())

        nrr = events[-1].node_run_result
        assert nrr.status == WorkflowNodeExecutionStatus.SUCCEEDED
        assert nrr.outputs["text"] == "Final: Paris."
        assert nrr.outputs["metadata"]["model_name"] == "gpt-4o-mini"
        assert nrr.outputs["metadata"]["contributions"] == {
            "a": "First model says Paris.",
            "b": "Second model agrees: Paris.",
        }
        assert nrr.inputs == {
            "source_count": 2,
            "model_provider": "openai",
            "model_name": "gpt-4o-mini",
        }

        user_prompt = model.prompt_messages[1].content
        assert "Return the shared final answer." in user_prompt
        assert "First model says Paris." in user_prompt
        assert "Second model agrees: Paris." in user_prompt

    def test_default_instruction_used_when_unset(self):
        pool = VariablePool()
        pool.add(["llm_a", "text"], "A")
        pool.add(["llm_b", "text"], "B")
        model = _StreamingAggregationModel()
        node = _make_node(pool, _two_input_payload(), model)

        events = list(node._run())

        nrr = events[-1].node_run_result
        assert nrr.status == WorkflowNodeExecutionStatus.SUCCEEDED
        user_prompt = model.prompt_messages[1].content
        # The default instruction starts with the literal "Synthesize" verb.
        assert "Synthesize the upstream responses" in user_prompt

    def test_missing_model_instance_fails(self):
        # Defense in depth: factory should always inject the model, but a
        # mis-wired call site must surface a clear FAILED event, not crash.
        pool = VariablePool()
        pool.add(["llm_a", "text"], "A")
        pool.add(["llm_b", "text"], "B")
        node = _make_node(pool, _two_input_payload(), inject_model=False)

        events = list(node._run())

        nrr = events[-1].node_run_result
        assert nrr.status == WorkflowNodeExecutionStatus.FAILED
        assert nrr.error_type == "ModelSynthesisError"


class TestRunFailurePaths:
    """`_run` catches ResponseAggregatorNodeError descendants and emits
    exactly one FAILED StreamCompletedEvent carrying the exception class."""

    def test_missing_upstream_input_becomes_failed_event(self):
        pool = VariablePool()
        pool.add(["llm_a", "text"], "only-a-present")
        # llm_b deliberately not added.
        node = _make_node(pool, _two_input_payload())

        events = list(node._run())

        assert len(events) == 1
        nrr = events[0].node_run_result
        assert nrr.status == WorkflowNodeExecutionStatus.FAILED
        assert nrr.error_type == "MissingInputError"
        assert "llm_b" in nrr.error or "'b'" in nrr.error
        # inputs metadata still populated for observability of the failed run.
        assert nrr.inputs == {"source_count": 2}
        assert nrr.outputs == {}

    def test_exceptions_are_importable_and_distinct(self):
        # Sanity: import path + hierarchy.
        assert issubclass(MissingInputError, Exception)
        assert issubclass(WeightResolutionError, Exception)
        assert issubclass(ModelSynthesisError, Exception)


class TestDynamicWeightResolution:
    """Weight-resolution branches (ADR-v3-15):

    * happy path (selector resolves to a finite number),
    * fail-fast (no fallback → WeightResolutionError → FAILED),
    * graceful degrade (fallback set → swap in fallback + log warning).
    """

    @staticmethod
    def _two_inputs_pool(*, with_weight_var: bool, weight_value=None) -> VariablePool:
        pool = VariablePool()
        pool.add(["llm_a", "text"], "A")
        pool.add(["llm_b", "text"], "A")
        if with_weight_var:
            pool.add(["weights_node", "m1"], weight_value)
        return pool

    @staticmethod
    def _payload(weight_a, fallback_a=None, weight_b=1.0) -> dict:
        ref_a: dict = {
            "source_id": "m1",
            "variable_selector": ["llm_a", "text"],
            "weight": weight_a,
        }
        if fallback_a is not None:
            ref_a["fallback_weight"] = fallback_a
        return {
            "title": "agg",
            "inputs": [
                ref_a,
                {
                    "source_id": "m2",
                    "variable_selector": ["llm_b", "text"],
                    "weight": weight_b,
                },
            ],
            "model": _model_payload(),
        }

    def test_dynamic_weight_resolves_from_pool(self):
        pool = self._two_inputs_pool(with_weight_var=True, weight_value=3.0)
        node = _make_node(pool, self._payload(weight_a=["weights_node", "m1"]))

        _, weights, fallbacks = node._collect_inputs()
        assert weights == {"m1": 3.0, "m2": 1.0}
        assert fallbacks == []

        events = list(node._run())
        nrr = events[-1].node_run_result
        assert nrr.status == WorkflowNodeExecutionStatus.SUCCEEDED
        assert nrr.outputs["metadata"]["weights"] == {"m1": 3.0, "m2": 1.0}

    def test_dynamic_weight_missing_var_fail_fast(self):
        pool = self._two_inputs_pool(with_weight_var=False)
        node = _make_node(pool, self._payload(weight_a=["weights_node", "m1"]))

        events = list(node._run())
        nrr = events[-1].node_run_result
        assert nrr.status == WorkflowNodeExecutionStatus.FAILED
        assert nrr.error_type == "WeightResolutionError"
        assert "m1" in nrr.error
        assert nrr.inputs == {"source_count": 2}

    def test_dynamic_weight_non_numeric_fail_fast(self):
        pool = self._two_inputs_pool(with_weight_var=True, weight_value="three")
        node = _make_node(pool, self._payload(weight_a=["weights_node", "m1"]))

        events = list(node._run())
        nrr = events[-1].node_run_result
        assert nrr.status == WorkflowNodeExecutionStatus.FAILED
        assert nrr.error_type == "WeightResolutionError"
        assert "not numeric" in nrr.error or "str" in nrr.error

    def test_dynamic_weight_bool_fail_fast(self):
        pool = self._two_inputs_pool(with_weight_var=True, weight_value=True)
        node = _make_node(pool, self._payload(weight_a=["weights_node", "m1"]))

        events = list(node._run())
        nrr = events[-1].node_run_result
        assert nrr.status == WorkflowNodeExecutionStatus.FAILED
        assert nrr.error_type == "WeightResolutionError"
        assert "bool" in nrr.error or "not numeric" in nrr.error

    def test_dynamic_weight_falls_back_when_fallback_set(self):
        pool = self._two_inputs_pool(with_weight_var=False)
        node = _make_node(
            pool,
            self._payload(
                weight_a=["weights_node", "m1"],
                fallback_a=0.5,
                weight_b=2.0,
            ),
        )

        _, weights, fallbacks = node._collect_inputs()
        assert weights == {"m1": 0.5, "m2": 2.0}
        assert [fb["source_id"] for fb in fallbacks] == ["m1"]

        events = list(node._run())
        nrr = events[-1].node_run_result
        assert nrr.status == WorkflowNodeExecutionStatus.SUCCEEDED
        assert nrr.process_data["weight_fallback_warnings"] == [
            {
                "source_id": "m1",
                "selector": ["weights_node", "m1"],
                "reason": "variable not present in pool",
                "fallback_weight": 0.5,
            }
        ]

    def test_static_weight_no_pool_lookup_required(self):
        pool = self._two_inputs_pool(with_weight_var=False)
        node = _make_node(pool, self._payload(weight_a=2.0, weight_b=1.0))

        _, weights, _ = node._collect_inputs()
        assert weights == {"m1": 2.0, "m2": 1.0}

        events = list(node._run())
        nrr = events[-1].node_run_result
        assert nrr.status == WorkflowNodeExecutionStatus.SUCCEEDED

    def test_dynamic_weight_none_value_fail_fast(self):
        pool = self._two_inputs_pool(with_weight_var=True, weight_value=None)
        node = _make_node(pool, self._payload(weight_a=["weights_node", "m1"]))

        events = list(node._run())
        nrr = events[-1].node_run_result
        assert nrr.status == WorkflowNodeExecutionStatus.FAILED
        assert nrr.error_type == "WeightResolutionError"
        assert (
            "None" in nrr.error
            or "not present" in nrr.error
            or "not numeric" in nrr.error
        )

    def test_dynamic_weight_nan_value_fail_fast(self):
        pool = self._two_inputs_pool(with_weight_var=True, weight_value=float("nan"))
        node = _make_node(pool, self._payload(weight_a=["weights_node", "m1"]))

        events = list(node._run())
        nrr = events[-1].node_run_result
        assert nrr.status == WorkflowNodeExecutionStatus.FAILED
        assert nrr.error_type == "WeightResolutionError"
        assert "not finite" in nrr.error or "nan" in nrr.error.lower()

    def test_dynamic_weight_inf_value_fail_fast(self):
        pool = self._two_inputs_pool(with_weight_var=True, weight_value=float("inf"))
        node = _make_node(pool, self._payload(weight_a=["weights_node", "m1"]))

        events = list(node._run())
        nrr = events[-1].node_run_result
        assert nrr.status == WorkflowNodeExecutionStatus.FAILED
        assert nrr.error_type == "WeightResolutionError"
        assert "not finite" in nrr.error or "inf" in nrr.error.lower()

    def test_multiple_fallbacks_recorded_in_declared_order(self):
        pool = VariablePool()
        pool.add(["llm_a", "text"], "A")
        pool.add(["llm_b", "text"], "A")
        # Neither weight selector is present → both fall back.
        payload = {
            "title": "agg",
            "inputs": [
                {
                    "source_id": "m1",
                    "variable_selector": ["llm_a", "text"],
                    "weight": ["weights_node", "m1"],
                    "fallback_weight": 0.6,
                },
                {
                    "source_id": "m2",
                    "variable_selector": ["llm_b", "text"],
                    "weight": ["weights_node", "m2"],
                    "fallback_weight": 0.4,
                },
            ],
            "model": _model_payload(),
        }
        node = _make_node(pool, payload)

        _, weights, _ = node._collect_inputs()
        assert weights == {"m1": 0.6, "m2": 0.4}

        events = list(node._run())
        nrr = events[-1].node_run_result
        assert nrr.status == WorkflowNodeExecutionStatus.SUCCEEDED
        warnings = nrr.process_data["weight_fallback_warnings"]
        assert [w["source_id"] for w in warnings] == ["m1", "m2"]
        assert [w["fallback_weight"] for w in warnings] == [0.6, 0.4]


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(pytest.main([__file__, "-v"]))
