"""Route-scope aggregators for response-level routing runners."""

from __future__ import annotations

from .noop import NoopRouteAggregator, NoopRouteConfig

__all__ = ["NoopRouteAggregator", "NoopRouteConfig"]
