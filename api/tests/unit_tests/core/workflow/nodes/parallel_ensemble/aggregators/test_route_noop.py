from __future__ import annotations

from core.workflow.nodes.parallel_ensemble.aggregators.route.noop import (
    NoopRouteAggregator,
    NoopRouteConfig,
)
from core.workflow.nodes.parallel_ensemble.registry.aggregator_registry import AggregatorRegistry
from core.workflow.nodes.parallel_ensemble.spi.aggregator import SourceAggregationContext


def test_noop_route_aggregator_registered_with_route_scope():
    cls = AggregatorRegistry.get("noop_route")
    assert cls is NoopRouteAggregator
    assert cls.scope == "route"


def test_noop_route_aggregator_returns_signals_unchanged():
    signals = {"route": ["a", "b"]}
    ctx = SourceAggregationContext(sources=["a", "b"], weights={"a": 1.0, "b": 1.0})

    out = NoopRouteAggregator().aggregate(signals, ctx, NoopRouteConfig())

    assert out is signals
