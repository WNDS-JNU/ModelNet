from __future__ import annotations

import pytest

from core.workflow.nodes.parallel_ensemble.aggregators.route.noop import (
    NoopRouteAggregator,
    NoopRouteConfig,
)
from core.workflow.nodes.parallel_ensemble.registry.runner_registry import RunnerRegistry
from core.workflow.nodes.parallel_ensemble.runners import load_aware_route as module
from core.workflow.nodes.parallel_ensemble.runners.load_aware_route import (
    LoadAwareRouteConfig,
    LoadAwareRouteRunner,
)
from core.workflow.nodes.parallel_ensemble.spi.backend import GenerationResult
from core.workflow.nodes.parallel_ensemble.spi.trace import DiagnosticsConfig, TraceCollector

from .conftest import FakeBackend, make_sources


def test_registered_with_route_scope():
    cls = RunnerRegistry.get("load_aware_route")
    assert cls is LoadAwareRouteRunner
    assert cls.aggregator_scope == "route"
    assert cls.required_capabilities == frozenset()


def test_load_aware_route_selects_alias_and_generates(monkeypatch):
    backends = {
        "source_a": FakeBackend(
            "alias-a", scripted_generate=GenerationResult(text="A", finish_reason="stop", metadata={})
        ),
        "source_b": FakeBackend(
            "alias-b", scripted_generate=GenerationResult(text="B", finish_reason="stop", metadata={})
        ),
    }

    def route_model_from_load(candidate_aliases, required_capabilities, policy):
        assert candidate_aliases == ["alias-a", "alias-b"]
        assert required_capabilities == ["chat"]
        assert policy == {"top_k": 1, "include_unhealthy": False}
        return {
            "selected_alias": "alias-b",
            "selected_aliases": ["alias-b"],
            "ranked_candidates": [{"id": "alias-b", "score": 0.9}],
            "fallback_reason": None,
        }

    monkeypatch.setattr(module, "route_model_from_load", route_model_from_load)
    runner = LoadAwareRouteRunner(executor=None, aggregator_config=NoopRouteConfig())
    trace = TraceCollector(DiagnosticsConfig(include_model_outputs=True))

    events = list(
        runner.run(
            sources=make_sources(backends, prompt="Question?", top_k=7),
            backends=backends,
            aggregator=NoopRouteAggregator(),
            config=LoadAwareRouteConfig(required_capabilities=["chat"]),
            trace=trace,
        )
    )

    assert events == [
        {
            "kind": "done",
            "text": "B",
            "metadata": {
                "selected_alias": "alias-b",
                "selected_source_id": "source_b",
                "route": {
                    "selected_alias": "alias-b",
                    "selected_aliases": ["alias-b"],
                    "ranked_candidates": [{"id": "alias-b", "score": 0.9}],
                    "fallback_reason": None,
                },
                "finish_reason": "stop",
            },
        }
    ]
    assert backends["source_a"].generate_calls == []
    assert backends["source_b"].generate_calls[0][0] == "Question?"
    assert backends["source_b"].generate_calls[0][1]["top_k"] == 7


def test_load_aware_route_raises_when_no_model_is_selected(monkeypatch):
    backends = {
        "source_a": FakeBackend(
            "alias-a", scripted_generate=GenerationResult(text="A", finish_reason="stop", metadata={})
        ),
    }

    monkeypatch.setattr(
        module,
        "route_model_from_load",
        lambda **kwargs: {"selected_alias": None, "fallback_reason": "no_healthy_eligible_models"},
    )
    runner = LoadAwareRouteRunner(executor=None, aggregator_config=NoopRouteConfig())

    with pytest.raises(Exception, match="no_healthy_eligible_models"):
        list(
            runner.run(
                sources=make_sources(backends),
                backends=backends,
                aggregator=NoopRouteAggregator(),
                config=LoadAwareRouteConfig(),
                trace=TraceCollector(DiagnosticsConfig()),
            )
        )
