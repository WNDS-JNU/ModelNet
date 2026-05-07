"""Majority-vote response strategy.

Used by the AI-ModelNet S2P paradigm at the Stage-2 aggregation
junction: each parallel branch produces a candidate answer, and the
strategy returns the text whose extracted *vote key* wins a (weighted)
plurality across sources. Inspired by the response-level vote variant
in paper Fig. 5a.

Vote-key extraction:

* If ``answer_extract_regex`` is set, the first capture group of the
  first match is used as the vote key. Inputs that do not match are
  dropped from the tally (their full text is still surfaced under
  ``metadata.contributions`` for diagnostics).
* Otherwise the full text is whitespace-normalised and used as the key
  directly. This is rare in practice — most use cases want a regex.

Tie-break:

* ``"first"`` (default) — pick the first source (in declared input
  order) whose vote key equals the winning key; mirrors ``concat``'s
  insertion-order convention.
* ``"longest"`` — pick the source whose raw signal text is longest
  among the winners. Handy when verifiers vary in verbosity and you
  want the most-detailed agreeing reply.
"""

from __future__ import annotations

import re
from typing import ClassVar, Literal

from pydantic import BaseModel, ConfigDict

from .base import (
    ResponseAggregationResult,
    ResponseAggregator,
    ResponseSignal,
    SourceAggregationContext,
)
from .registry import register


class _MajorityVoteConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    answer_extract_regex: str = ""
    """Python ``re`` regex applied to each input's text; the first
    capture group of the first match becomes the vote key. Empty
    string (default) = vote on the whitespace-normalised full text.
    Inputs that do not match are dropped from the tally — their full
    text remains in ``metadata.contributions`` for inspection."""

    case_sensitive: bool = False
    """When ``False`` (default) vote keys are compared
    case-insensitively (lower-cased both sides). Off matches the
    permissive accuracy criterion most multi-LLM benchmarks use."""

    weighted: bool = True
    """When ``True`` (default) per-source ``SourceAggregationContext.
    weights`` accrue to the vote key. When ``False`` every source
    contributes a flat vote of ``1.0`` regardless of the input's
    ``weight`` — useful when the upstream weights are known to be
    miscalibrated and you want a true unweighted majority."""

    tie_break: Literal["first", "longest"] = "first"
    """Tie-break policy when two or more vote keys end with equal
    tallies. ``"first"`` = first-declared source wins (preserves the
    declared ``inputs`` order); ``"longest"`` = source with the
    longest raw signal text wins."""


@register("majority_vote")
class MajorityVoteStrategy(ResponseAggregator[_MajorityVoteConfig]):
    config_class: ClassVar[type[BaseModel]] = _MajorityVoteConfig
    i18n_key_prefix: ClassVar[str] = "nodes.responseAggregator.majorityVote"
    ui_schema: ClassVar[dict] = {
        "answer_extract_regex": {"control": "text_input"},
        "case_sensitive": {"control": "switch"},
        "weighted": {"control": "switch"},
        "tie_break": {"control": "select"},
    }

    def aggregate(
        self,
        signals: list[ResponseSignal],
        context: SourceAggregationContext,
        config: _MajorityVoteConfig,
    ) -> ResponseAggregationResult:
        pattern: re.Pattern[str] | None = None
        if config.answer_extract_regex:
            pattern = re.compile(config.answer_extract_regex)

        contributions: dict[str, str] = {s["source_id"]: s["text"] for s in signals}
        per_source_keys: dict[str, str] = {}
        vote_counts: dict[str, float] = {}

        for s in signals:
            text = s["text"]
            if pattern is not None:
                match = pattern.search(text)
                if match is None:
                    # No regex match → this source abstains.
                    continue
                raw_key = match.group(1) if match.groups() else match.group(0)
            else:
                # Whitespace-normalise so trivial spacing differences don't
                # split votes.
                raw_key = " ".join(text.split())

            key = raw_key if config.case_sensitive else raw_key.lower()
            per_source_keys[s["source_id"]] = key
            weight = (
                context.weights.get(s["source_id"], 1.0) if config.weighted else 1.0
            )
            vote_counts[key] = vote_counts.get(key, 0.0) + weight

        if not vote_counts:
            # No source produced an extractable key. Surface the empty
            # tally so the downstream extractor short-circuits to a
            # miss instead of receiving an arbitrary first-source text.
            return {
                "text": "",
                "metadata": {
                    "strategy": "majority_vote",
                    "vote_counts": {},
                    "winner_key": None,
                    "winner_source": None,
                    "contributions": contributions,
                    "tie_break": config.tie_break,
                    "weighted": config.weighted,
                    "case_sensitive": config.case_sensitive,
                },
            }

        max_count = max(vote_counts.values())
        winners = {k for k, c in vote_counts.items() if c == max_count}

        # Resolve to a concrete source. ``signals`` order is the declared
        # input order, so iterating it preserves the ``"first"`` policy.
        winning_signals = [
            s for s in signals
            if per_source_keys.get(s["source_id"]) in winners
        ]
        if config.tie_break == "longest":
            chosen = max(winning_signals, key=lambda s: len(s["text"]))
        else:
            chosen = winning_signals[0]

        return {
            "text": chosen["text"],
            "metadata": {
                "strategy": "majority_vote",
                "vote_counts": vote_counts,
                "winner_key": per_source_keys[chosen["source_id"]],
                "winner_source": chosen["source_id"],
                "contributions": contributions,
                "tie_break": config.tie_break,
                "weighted": config.weighted,
                "case_sensitive": config.case_sensitive,
            },
        }
