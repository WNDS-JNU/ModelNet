"""Unit tests for the majority_vote response strategy.

Covers regex-based vote-key extraction, case sensitivity, weighting,
tie-break behaviour, and the empty-tally fallback. Mirrors the
``test_strategies.py`` style — schema-level coverage stays in
``test_entities.py``.
"""

import pytest
from pydantic import ValidationError

from core.workflow.nodes.response_aggregator.strategies import (
    MajorityVoteStrategy,
    ResponseSignal,
    SourceAggregationContext,
)
from core.workflow.nodes.response_aggregator.strategies.majority_vote import (
    _MajorityVoteConfig,
)


def _signals(*pairs: tuple[str, str]) -> list[ResponseSignal]:
    return [
        ResponseSignal(
            source_id=sid,
            text=text,
            finish_reason="stop",
            elapsed_ms=0,
            error=None,
        )
        for sid, text in pairs
    ]


def _ctx(
    sources: list[str],
    weights: dict[str, float] | None = None,
) -> SourceAggregationContext:
    return SourceAggregationContext(
        sources=sources,
        weights=weights if weights is not None else dict.fromkeys(sources, 1.0),
        source_meta={},
        strategy_config={},
    )


class TestMajorityVoteRegexExtraction:
    """Cover the answer_extract_regex path used by the AI-ModelNet S2P paradigm."""

    def test_majority_wins_with_regex(self):
        strategy = MajorityVoteStrategy()
        signals = _signals(
            ("m1", "I think the answer is (B)."),
            ("m2", "Final answer: (B)"),
            ("m3", "I'll go with (C)"),
        )
        cfg = _MajorityVoteConfig(answer_extract_regex=r"\(([A-D])\)")
        result = strategy.aggregate(
            signals,
            _ctx(["m1", "m2", "m3"]),
            cfg,
        )
        # Two votes for "b" (lowercased), one for "c".
        assert result["metadata"]["vote_counts"] == {"b": 2.0, "c": 1.0}
        assert result["metadata"]["winner_key"] == "b"
        # First source whose key matches the winner takes the text.
        assert result["metadata"]["winner_source"] == "m1"
        assert result["text"] == "I think the answer is (B)."

    def test_no_regex_match_drops_that_source(self):
        strategy = MajorityVoteStrategy()
        signals = _signals(
            ("m1", "answer is (A)"),
            ("m2", "Sorry, I cannot answer."),  # no parenthesised letter
            ("m3", "the answer is (A)"),
        )
        result = strategy.aggregate(
            signals,
            _ctx(["m1", "m2", "m3"]),
            _MajorityVoteConfig(answer_extract_regex=r"\(([A-D])\)"),
        )
        # m2 abstains; m1 and m3 both vote "a".
        assert result["metadata"]["vote_counts"] == {"a": 2.0}
        assert result["metadata"]["winner_source"] == "m1"
        # Diagnostics still surface the abstaining source's full text.
        assert result["metadata"]["contributions"]["m2"] == "Sorry, I cannot answer."

    def test_zero_matches_returns_empty_text(self):
        strategy = MajorityVoteStrategy()
        signals = _signals(
            ("m1", "I cannot answer"),
            ("m2", "Refusing"),
        )
        result = strategy.aggregate(
            signals,
            _ctx(["m1", "m2"]),
            _MajorityVoteConfig(answer_extract_regex=r"\(([A-D])\)"),
        )
        # Empty text so the downstream extractor short-circuits to a miss.
        assert result["text"] == ""
        assert result["metadata"]["vote_counts"] == {}
        assert result["metadata"]["winner_key"] is None
        assert result["metadata"]["winner_source"] is None

    def test_regex_without_capture_group_uses_full_match(self):
        strategy = MajorityVoteStrategy()
        signals = _signals(
            ("m1", "true"),
            ("m2", "true"),
            ("m3", "false"),
        )
        # Regex with no capture group — full match becomes the key.
        result = strategy.aggregate(
            signals,
            _ctx(["m1", "m2", "m3"]),
            _MajorityVoteConfig(answer_extract_regex=r"\b(?:true|false)\b"),
        )
        assert result["metadata"]["vote_counts"] == {"true": 2.0, "false": 1.0}
        assert result["metadata"]["winner_source"] == "m1"


class TestMajorityVoteCaseSensitivity:
    def test_case_insensitive_default_collapses_keys(self):
        strategy = MajorityVoteStrategy()
        signals = _signals(("m1", "Yes"), ("m2", "yes"), ("m3", "no"))
        result = strategy.aggregate(
            signals,
            _ctx(["m1", "m2", "m3"]),
            _MajorityVoteConfig(),  # no regex; full normalised text vote
        )
        assert result["metadata"]["vote_counts"] == {"yes": 2.0, "no": 1.0}
        # First "Yes" preserved verbatim — the case is only collapsed for
        # the *vote key*; the surfaced text remains the source's original.
        assert result["text"] == "Yes"

    def test_case_sensitive_keeps_keys_distinct(self):
        strategy = MajorityVoteStrategy()
        signals = _signals(("m1", "Yes"), ("m2", "yes"), ("m3", "yes"))
        result = strategy.aggregate(
            signals,
            _ctx(["m1", "m2", "m3"]),
            _MajorityVoteConfig(case_sensitive=True),
        )
        # Now "Yes" and "yes" are distinct keys; "yes" wins 2-1.
        assert result["metadata"]["vote_counts"] == {"Yes": 1.0, "yes": 2.0}
        assert result["metadata"]["winner_source"] == "m2"


class TestMajorityVoteWeighting:
    def test_weighted_majority_can_overcome_count_minority(self):
        strategy = MajorityVoteStrategy()
        signals = _signals(("expert", "(A)"), ("intern1", "(B)"), ("intern2", "(B)"))
        # The expert is worth more than two interns combined.
        ctx = _ctx(
            ["expert", "intern1", "intern2"],
            weights={"expert": 5.0, "intern1": 1.0, "intern2": 1.0},
        )
        cfg = _MajorityVoteConfig(answer_extract_regex=r"\(([A-D])\)")
        result = strategy.aggregate(signals, ctx, cfg)
        assert result["metadata"]["vote_counts"] == {"a": 5.0, "b": 2.0}
        assert result["metadata"]["winner_source"] == "expert"

    def test_unweighted_falls_back_to_one_vote_per_source(self):
        strategy = MajorityVoteStrategy()
        signals = _signals(("expert", "(A)"), ("intern1", "(B)"), ("intern2", "(B)"))
        # Same upstream weights, but the strategy is told to ignore them.
        ctx = _ctx(
            ["expert", "intern1", "intern2"],
            weights={"expert": 5.0, "intern1": 1.0, "intern2": 1.0},
        )
        cfg = _MajorityVoteConfig(
            answer_extract_regex=r"\(([A-D])\)",
            weighted=False,
        )
        result = strategy.aggregate(signals, ctx, cfg)
        assert result["metadata"]["vote_counts"] == {"a": 1.0, "b": 2.0}
        assert result["metadata"]["winner_key"] == "b"
        assert result["metadata"]["winner_source"] == "intern1"


class TestMajorityVoteTieBreak:
    def test_tie_break_first_picks_declared_order(self):
        strategy = MajorityVoteStrategy()
        signals = _signals(
            ("late", "(A) — short"),
            ("mid", "(B) — medium length"),
            ("early", "(A) — but the longest of the three"),
        )
        cfg = _MajorityVoteConfig(answer_extract_regex=r"\(([A-D])\)")
        # ``a`` and ``b`` both have count=1+1=? Actually a=2, b=1 → a wins.
        # We need a real tie. Add a fourth source on b:
        signals.append(
            ResponseSignal(
                source_id="extra",
                text="(B) — also voted",
                finish_reason="stop",
                elapsed_ms=0,
                error=None,
            )
        )
        result = strategy.aggregate(
            signals,
            _ctx(["late", "mid", "early", "extra"]),
            cfg,
        )
        # Now a=2 (late, early), b=2 (mid, extra). Tie → "first" picks
        # whichever winning source comes earliest in the input list.
        # ``late`` is earliest among winners (its key "a" is in winners).
        assert result["metadata"]["winner_key"] in {"a", "b"}  # both tied
        assert result["metadata"]["winner_source"] == "late"

    def test_tie_break_longest_picks_longest_signal(self):
        strategy = MajorityVoteStrategy()
        signals = _signals(
            ("late", "(A) — short"),
            ("mid", "(B) — also short"),
            ("early", "(A) — but the longest of the three replies, by far"),
        )
        signals.append(
            ResponseSignal(
                source_id="extra",
                text="(B) ok",
                finish_reason="stop",
                elapsed_ms=0,
                error=None,
            )
        )
        cfg = _MajorityVoteConfig(
            answer_extract_regex=r"\(([A-D])\)",
            tie_break="longest",
        )
        result = strategy.aggregate(
            signals,
            _ctx(["late", "mid", "early", "extra"]),
            cfg,
        )
        # ``early`` has the longest text among winners (a or b tied).
        assert result["metadata"]["winner_source"] == "early"


class TestMajorityVoteSchema:
    def test_extra_keys_rejected_by_pydantic(self):
        # ``extra="forbid"`` mirrors concat — guards against DSL drift.
        with pytest.raises(ValidationError):
            _MajorityVoteConfig(answer_extract_regex="", invented_field=True)  # type: ignore[call-arg]

    def test_tie_break_literal_validated(self):
        with pytest.raises(ValidationError):
            _MajorityVoteConfig(tie_break="random")  # type: ignore[arg-type]
