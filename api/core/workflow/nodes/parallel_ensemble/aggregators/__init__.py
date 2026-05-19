"""Built-in aggregators for the parallel-ensemble node (v3 P3.B.0).

ADR-v3-9 retired the old response-mode runner + ``aggregators/response/*``;
response strategies live under ``response_aggregator`` instead. The
parallel-ensemble node now ships token-scope aggregators plus a route-scope
adapter for response-level serial routing:

* ``token/`` — PN.py-style per-step aggregators (``sum_score`` /
  ``max_score``). Pair with ``TokenStepRunner``.
* ``route/`` — no-op adapter for runners that perform their own dynamic
  response routing.

Importing this package executes the ``@register_aggregator``
side-effects, populating ``AggregatorRegistry`` before any node-level
``aggregator_registry.get(...)`` lookup happens.
"""

from __future__ import annotations

from . import route as route
from . import token as token

__all__ = ["route", "token"]
