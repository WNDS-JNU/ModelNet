from __future__ import annotations

import json
from collections.abc import Iterable

import pytest

from core.workflow.nodes.parallel_ensemble.aggregators.route.noop import (
    NoopRouteAggregator,
    NoopRouteConfig,
)
from core.workflow.nodes.parallel_ensemble.registry.runner_registry import RunnerRegistry
from core.workflow.nodes.parallel_ensemble.runners.dynamic_collab_route import (
    DynamicCollabRouteConfig,
    DynamicCollabRouteRunner,
)
from core.workflow.nodes.parallel_ensemble.spi.backend import GenerationParams, GenerationResult
from core.workflow.nodes.parallel_ensemble.spi.trace import DiagnosticsConfig, TraceCollector

from .conftest import FakeBackend, make_sources


class ScriptedGenerateBackend(FakeBackend):
    def __init__(self, alias: str, replies: Iterable[str | Exception]) -> None:
        super().__init__(alias)
        self._replies = list(replies)

    def generate(self, prompt: str, params: GenerationParams) -> GenerationResult:
        self.generate_calls.append((prompt, params))
        if not self._replies:
            return GenerationResult(text="", finish_reason="stop", metadata={})
        item = self._replies.pop(0)
        if isinstance(item, Exception):
            raise item
        return GenerationResult(text=item, finish_reason="stop", metadata={})


def _run(backends: dict[str, ScriptedGenerateBackend], config: DynamicCollabRouteConfig):
    runner = DynamicCollabRouteRunner(executor=None, aggregator_config=NoopRouteConfig())  # type: ignore[arg-type]
    trace = TraceCollector(
        DiagnosticsConfig(
            include_model_outputs=True,
            include_per_backend_errors=True,
            include_response_timings=True,
        )
    )
    events = list(
        runner.run(
            sources=make_sources(backends, prompt="Question?"),
            backends=backends,
            aggregator=NoopRouteAggregator(),
            config=config,
            trace=trace,
        )
    )
    trace_data = trace.finalize(
        runner_name="dynamic_collab_route",
        runner_config=config.model_dump(),
        aggregator_name="noop_route",
        aggregator_config={},
        backends=[],
    )
    return events, trace_data


def test_registered_with_route_scope():
    cls = RunnerRegistry.get("dynamic_collab_route")
    assert cls is DynamicCollabRouteRunner
    assert cls.aggregator_scope == "route"
    assert cls.required_capabilities == frozenset()


def test_consensus_stops_after_initial_answer():
    backends = {
        "a": ScriptedGenerateBackend("a", ["initial answer"]),
        "b": ScriptedGenerateBackend("b", ["认可"]),
        "c": ScriptedGenerateBackend("c", ["认可"]),
    }
    config = DynamicCollabRouteConfig(
        initial_source_id="a",
        collaboration_graph_json=json.dumps({"a": ["b", "c"]}),
    )

    events, trace_data = _run(backends, config)

    assert [e["kind"] for e in events] == ["done"]
    done = events[0]
    assert done["text"] == "initial answer"  # type: ignore[typeddict-item]
    assert done["metadata"]["stopped_by"] == "consensus"  # type: ignore[typeddict-item]
    assert done["metadata"]["route"] == ["a"]  # type: ignore[typeddict-item]
    assert trace_data["summary"]["hops_count"] == 0


def test_rejecting_model_refines_next_hop():
    backends = {
        "a": ScriptedGenerateBackend("a", ["rough answer"]),
        "b": ScriptedGenerateBackend("b", ["不认可", "refined by b"]),
        "c": ScriptedGenerateBackend("c", ["认可"]),
    }
    config = DynamicCollabRouteConfig(
        initial_source_id="a",
        collaboration_graph_json=json.dumps({"a": ["b", "c"], "b": []}),
        seed=123,
        max_hops=3,
    )

    events, trace_data = _run(backends, config)

    done = events[-1]
    assert done["text"] == "refined by b"  # type: ignore[typeddict-item]
    assert done["metadata"]["route"] == ["a", "b"]  # type: ignore[typeddict-item]
    assert done["metadata"]["stopped_by"] == "no_candidates"  # type: ignore[typeddict-item]
    assert trace_data["summary"]["route_steps"][0]["rejecting_sources"] == ["b"]
    assert trace_data["summary"]["route_steps"][0]["selected_source_id"] == "b"


def test_supplemental_graph_is_used_when_primary_has_no_candidates():
    backends = {
        "a": ScriptedGenerateBackend("a", ["rough answer"]),
        "b": ScriptedGenerateBackend("b", ["不认可", "refined by b"]),
    }
    config = DynamicCollabRouteConfig(
        initial_source_id="a",
        collaboration_graph_json=json.dumps({"a": [], "b": []}),
        supplemental_graph_json=json.dumps({"a": ["b"], "b": []}),
        max_hops=3,
    )

    events, trace_data = _run(backends, config)

    done = events[-1]
    assert done["text"] == "refined by b"  # type: ignore[typeddict-item]
    assert done["metadata"]["route"] == ["a", "b"]  # type: ignore[typeddict-item]
    assert trace_data["summary"]["route_steps"][0]["candidate_graph"] == "supplemental"


def test_graph_builder_artifact_json_embeds_supplemental_graph():
    backends = {
        "a": ScriptedGenerateBackend("a", ["rough answer"]),
        "b": ScriptedGenerateBackend("b", ["不认可", "refined by b"]),
    }
    artifact = {
        "collaboration_graph": {"a": [], "b": []},
        "supplemental_graph": {"a": ["b"], "b": []},
    }
    config = DynamicCollabRouteConfig(
        initial_source_id="a",
        collaboration_graph_json=json.dumps(artifact),
        max_hops=3,
    )

    events, trace_data = _run(backends, config)

    done = events[-1]
    assert done["text"] == "refined by b"  # type: ignore[typeddict-item]
    assert done["metadata"]["route"] == ["a", "b"]  # type: ignore[typeddict-item]
    assert trace_data["summary"]["route_steps"][0]["candidate_graph"] == "supplemental"


def test_max_hops_after_refinement_budget_is_exhausted():
    backends = {
        "a": ScriptedGenerateBackend("a", ["rough answer"]),
        "b": ScriptedGenerateBackend("b", ["不认可", "refined by b"]),
    }
    config = DynamicCollabRouteConfig(
        initial_source_id="a",
        collaboration_graph_json=json.dumps({"a": ["b"], "b": ["a"]}),
        max_hops=1,
    )

    events, _trace_data = _run(backends, config)

    done = events[-1]
    assert done["text"] == "refined by b"  # type: ignore[typeddict-item]
    assert done["metadata"]["stopped_by"] == "max_hops"  # type: ignore[typeddict-item]
    assert done["metadata"]["route"] == ["a", "b"]  # type: ignore[typeddict-item]


def test_unparseable_judgement_defaults_to_acceptance():
    backends = {
        "a": ScriptedGenerateBackend("a", ["initial answer"]),
        "b": ScriptedGenerateBackend("b", ["maybe"]),
    }
    config = DynamicCollabRouteConfig(
        initial_source_id="a",
        collaboration_graph_json=json.dumps({"a": ["b"]}),
    )

    events, trace_data = _run(backends, config)

    done = events[-1]
    assert done["text"] == "initial answer"  # type: ignore[typeddict-item]
    assert done["metadata"]["stopped_by"] == "consensus"  # type: ignore[typeddict-item]
    judgement = trace_data["summary"]["route_steps"][0]["judgements"][0]
    assert judgement["accepted"] is True
    assert judgement["parsed"] == "unparseable"


def test_initial_source_error_fails_fast():
    backends = {
        "a": ScriptedGenerateBackend("a", [RuntimeError("boom")]),
        "b": ScriptedGenerateBackend("b", ["认可"]),
    }
    config = DynamicCollabRouteConfig(initial_source_id="a")
    runner = DynamicCollabRouteRunner(executor=None, aggregator_config=NoopRouteConfig())  # type: ignore[arg-type]

    with pytest.raises(RuntimeError, match="boom"):
        list(
            runner.run(
                sources=make_sources(backends, prompt="Question?"),
                backends=backends,
                aggregator=NoopRouteAggregator(),
                config=config,
                trace=TraceCollector(DiagnosticsConfig(include_per_backend_errors=True)),
            )
        )


def test_unknown_graph_candidates_fail_before_generation():
    backends = {
        "a": ScriptedGenerateBackend("a", ["rough answer"]),
        "b": ScriptedGenerateBackend("b", ["认可"]),
    }
    config = DynamicCollabRouteConfig(
        initial_source_id="a",
        collaboration_graph_json=json.dumps({"a": ["missing"]}),
    )

    with pytest.raises(Exception, match="known source_id"):
        _run(backends, config)
    assert backends["a"].generate_calls == []
