"""No-op aggregator for runners that own their own route decision loop."""

from __future__ import annotations

from typing import Any, ClassVar

from pydantic import BaseModel, ConfigDict

from ...registry.aggregator_registry import register_aggregator
from ...spi.aggregator import Aggregator, SourceAggregationContext


class NoopRouteConfig(BaseModel):
    """No configuration: the paired runner performs all routing work."""

    model_config = ConfigDict(extra="forbid")


@register_aggregator("noop_route", scope="route")
class NoopRouteAggregator(Aggregator[NoopRouteConfig, Any, Any, SourceAggregationContext]):
    """Framework adapter for route-scope runners.

    ``parallel-ensemble`` validates every runner against an aggregator scope.
    Dynamic collaborative routing does not need an external reducer, but this
    tiny aggregator keeps the existing runner/aggregator contract intact.
    """

    scope: ClassVar[str] = "route"
    config_class: ClassVar[type[BaseModel]] = NoopRouteConfig
    i18n_key_prefix: ClassVar[str] = "parallelEnsemble.aggregators.noopRoute"
    ui_schema: ClassVar[dict] = {}

    def aggregate(
        self,
        signals: Any,
        context: SourceAggregationContext,
        config: NoopRouteConfig,
    ) -> Any:
        del context, config
        return signals
