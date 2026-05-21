"""Built-in runners for the parallel-ensemble node (v3 P3.B.0).

After ADR-v3-9 the parallel-ensemble node kept the PN.py-style token mode,
and now also exposes a route-mode runner for paper reproduction without
reintroducing the old response aggregation path:

* ``token_step`` — PN.py-style per-step voting (``TokenStepRunner``,
  paired with ``aggregator_scope = "token"``). Optional ``enable_think``
  triggers a one-shot ``ThinkPhaseRunner`` pre-pass for ``type=think``
  models so chain-of-thought completes before the joint token loop
  starts.
* ``dynamic_collab_route`` — response-level serial routing based on
  pairwise collaborative relationships. Pair with ``noop_route``.

The submodule import below runs the ``@register_runner`` decorator as a
side effect, populating ``RunnerRegistry`` before any node-level
``runner_registry.get(...)`` lookup happens. Importing this package is
therefore enough to make the built-in discoverable.
"""

from __future__ import annotations

from . import dynamic_collab_route as dynamic_collab_route
from . import load_aware_route as load_aware_route
from . import token_step as token_step

__all__ = ["dynamic_collab_route", "load_aware_route", "token_step"]
