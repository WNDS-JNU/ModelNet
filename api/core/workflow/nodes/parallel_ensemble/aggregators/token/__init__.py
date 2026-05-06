"""Token-scope aggregators (PN.py-style ensemble at decode time).

Importing this package executes the ``@register_aggregator`` side
effects so the built-in token aggregators appear in
``AggregatorRegistry.by_scope("token")``.
"""

from __future__ import annotations

from .duet_net import DuetNetAggregator, DuetNetConfig
from .max_score import MaxScoreAggregator, MaxScoreConfig
from .sum_score import SumScoreAggregator, SumScoreConfig

__all__ = [
    "DuetNetAggregator",
    "DuetNetConfig",
    "MaxScoreAggregator",
    "MaxScoreConfig",
    "SumScoreAggregator",
    "SumScoreConfig",
]
