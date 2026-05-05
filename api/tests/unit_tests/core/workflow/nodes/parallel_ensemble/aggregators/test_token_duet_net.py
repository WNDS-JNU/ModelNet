"""Token-scope ``duet_net`` aggregator — DuetNet (Wang et al., 2025) paper
reproduction.

Covers:
* Registration under token scope
* Capability gate: every source must declare ``LOGITS_RAW``
* Adapter contract: ``logit=None`` despite declared capability surfaces
  a clear error pointing at the bad source
* Step 1 — τ_K and τ_P joint truncation (paper Eq. 2)
* Step 2 — candidate union + raw-logit cumulative score (Eqs. 4-5)
* Step 3 — Top-T sampling determinism (T=1) and seeded replay (T>1)
* ``use_weights`` propagation from ``BackendAggregationContext``
* Config schema rejects extra fields and out-of-range values
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from core.workflow.nodes.parallel_ensemble.aggregators.token.duet_net import (
    DuetNetAggregator,
    DuetNetConfig,
)
from core.workflow.nodes.parallel_ensemble.exceptions import (
    CapabilityNotSupportedError,
    ParallelEnsembleError,
)
from core.workflow.nodes.parallel_ensemble.registry.aggregator_registry import (
    AggregatorRegistry,
)
from core.workflow.nodes.parallel_ensemble.spi.capability import Capability


def _caps(*aliases: str) -> dict[str, frozenset[Capability]]:
    """LOGITS_RAW + the runner-required basics for every alias."""
    base = frozenset({Capability.LOGITS_RAW, Capability.TOKEN_STEP, Capability.TOP_PROBS})
    return dict.fromkeys(aliases, base)


# ── 1. Registration ─────────────────────────────────────────────────────


def test_registered_under_token_scope():
    cls = AggregatorRegistry.get("duet_net")
    assert cls is DuetNetAggregator
    assert cls.scope == "token"


# ── 2. Capability gate ──────────────────────────────────────────────────


def test_missing_logits_raw_raises_naming_source(make_ctx, cand):
    """Any source missing ``LOGITS_RAW`` → CapabilityNotSupportedError
    naming the offending source so the operator knows which spec to
    flip ``expose_raw_logits=true`` on."""
    ctx = make_ctx(
        weights={"m1": 1.0, "m2": 1.0},
        capabilities={
            "m1": frozenset({Capability.LOGITS_RAW}),
            "m2": frozenset(),
        },
    )
    signals = {
        "per_model": {
            "m1": [cand("hi", 0.9, 5.0)],
            "m2": [cand("hi", 0.8, 4.5)],
        },
        "per_model_errors": {},
    }
    agg = DuetNetAggregator()
    with pytest.raises(CapabilityNotSupportedError) as exc_info:
        agg.aggregate(signals, ctx, DuetNetConfig())
    assert exc_info.value.backend_name == "m2"
    assert exc_info.value.capability_name == Capability.LOGITS_RAW.value


def test_logit_none_despite_capability_raises(make_ctx, cand):
    """LOGITS_RAW declared but adapter forgot to fill the field → clear
    SPI-violation error so a fork that flipped the flag without wiring
    the parser fails on the first decode step."""
    ctx = make_ctx(weights={"m1": 1.0}, capabilities=_caps("m1"))
    signals = {
        "per_model": {"m1": [cand("hi", 0.9, logit=None)]},
        "per_model_errors": {},
    }
    agg = DuetNetAggregator()
    with pytest.raises(ParallelEnsembleError) as exc_info:
        agg.aggregate(signals, ctx, DuetNetConfig())
    assert "duet_net" in str(exc_info.value)
    assert "logit" in str(exc_info.value).lower()
    assert "m1" in str(exc_info.value)


# ── 3. Step 1 — τ_K + τ_P truncation (Eq. 2) ───────────────────────────


def test_tau_k_truncation_drops_excess_candidates(make_ctx, cand):
    """``tau_k=2`` keeps only the first two prob-sorted candidates per
    model; the third never enters the union."""
    ctx = make_ctx(weights={"m1": 1.0}, capabilities=_caps("m1"))
    signals = {
        "per_model": {
            "m1": [
                cand("a", 0.5, 10.0),
                cand("b", 0.3, 5.0),
                cand("c", 0.2, 3.0),
            ],
        },
        "per_model_errors": {},
    }
    agg = DuetNetAggregator()
    pick = agg.aggregate(signals, ctx, DuetNetConfig(tau_k=2, tau_p=1.0, top_t=1))
    assert "c" not in pick["reasoning"]["per_token_logit"]
    assert pick["reasoning"]["per_token_logit"] == {
        "a": pytest.approx(10.0),
        "b": pytest.approx(5.0),
    }


def test_tau_p_keeps_minimal_prefix_above_threshold(make_ctx, cand):
    """``tau_p=0.7`` should stop after cumulative prob first crosses
    the threshold (here probs 0.5+0.3=0.8 ≥ 0.7 with two candidates)."""
    ctx = make_ctx(weights={"m1": 1.0}, capabilities=_caps("m1"))
    signals = {
        "per_model": {
            "m1": [
                cand("a", 0.5, 10.0),
                cand("b", 0.3, 5.0),
                cand("c", 0.2, 3.0),
            ],
        },
        "per_model_errors": {},
    }
    agg = DuetNetAggregator()
    pick = agg.aggregate(signals, ctx, DuetNetConfig(tau_k=10, tau_p=0.7, top_t=1))
    assert sorted(pick["reasoning"]["per_token_logit"].keys()) == ["a", "b"]


def test_tau_p_boundary_inclusive(make_ctx, cand):
    """``cum >= tau_p`` rather than ``>``: a candidate that lands the
    cumsum exactly on the threshold is still kept."""
    ctx = make_ctx(weights={"m1": 1.0}, capabilities=_caps("m1"))
    signals = {
        "per_model": {
            "m1": [
                cand("a", 0.4, 10.0),
                cand("b", 0.35, 5.0),  # 0.4 + 0.35 = 0.75 == tau_p
                cand("c", 0.25, 3.0),
            ],
        },
        "per_model_errors": {},
    }
    agg = DuetNetAggregator()
    pick = agg.aggregate(signals, ctx, DuetNetConfig(tau_k=10, tau_p=0.75, top_t=1))
    assert sorted(pick["reasoning"]["per_token_logit"].keys()) == ["a", "b"]


# ── 4. Step 2 — union + raw-logit sum (Eqs. 4-5) ────────────────────────


def test_union_and_logit_sum(make_ctx, cand):
    """Token in both models gets ``logit_m1 + logit_m2``; tokens in
    only one model contribute only that model's logit."""
    ctx = make_ctx(weights={"m1": 1.0, "m2": 1.0}, capabilities=_caps("m1", "m2"))
    signals = {
        "per_model": {
            "m1": [cand("hello", 0.6, 8.0), cand("world", 0.4, 4.0)],
            "m2": [cand("hello", 0.5, 7.0), cand("foo", 0.5, 6.0)],
        },
        "per_model_errors": {},
    }
    agg = DuetNetAggregator()
    pick = agg.aggregate(signals, ctx, DuetNetConfig(tau_k=10, tau_p=1.0, top_t=1))
    assert pick["reasoning"]["per_token_logit"] == {
        "hello": pytest.approx(15.0),  # 8 + 7
        "world": pytest.approx(4.0),
        "foo": pytest.approx(6.0),
    }
    assert pick["token"] == "hello"
    assert pick["score"] == pytest.approx(15.0)
    assert pick["reasoning"]["winner_per_model"] == {
        "m1": pytest.approx(8.0),
        "m2": pytest.approx(7.0),
    }


def test_use_weights_scales_logit_contribution(make_ctx, cand):
    """``use_weights=True`` lets a high-weight backend overrule a
    low-weight backend's higher single logit."""
    ctx = make_ctx(weights={"m1": 1.0, "m2": 3.0}, capabilities=_caps("m1", "m2"))
    signals = {
        "per_model": {
            "m1": [cand("a", 0.6, 10.0)],  # contribution: 10
            "m2": [cand("b", 0.6, 5.0)],   # contribution: 15 (after weight 3)
        },
        "per_model_errors": {},
    }
    agg = DuetNetAggregator()
    pick = agg.aggregate(
        signals, ctx, DuetNetConfig(tau_k=10, tau_p=1.0, top_t=1, use_weights=True)
    )
    assert pick["token"] == "b"
    assert pick["score"] == pytest.approx(15.0)


def test_use_weights_false_ignores_ctx_weights(make_ctx, cand):
    """Default off: even an extreme weight on the wrong source has no
    effect, matching the paper's unweighted formulation."""
    ctx = make_ctx(weights={"m1": 1.0, "m2": 1000.0}, capabilities=_caps("m1", "m2"))
    signals = {
        "per_model": {
            "m1": [cand("a", 0.6, 10.0)],
            "m2": [cand("b", 0.6, 5.0)],
        },
        "per_model_errors": {},
    }
    agg = DuetNetAggregator()
    pick = agg.aggregate(
        signals, ctx, DuetNetConfig(tau_k=10, tau_p=1.0, top_t=1, use_weights=False)
    )
    assert pick["token"] == "a"  # raw logit 10 > 5


# ── 5. Step 3 — Top-T sampling (Eq. 6) ─────────────────────────────────


def test_top_t_one_is_argmax(make_ctx, cand):
    ctx = make_ctx(weights={"m1": 1.0}, capabilities=_caps("m1"))
    signals = {
        "per_model": {"m1": [cand("a", 0.7, 10.0), cand("b", 0.3, 5.0)]},
        "per_model_errors": {},
    }
    agg = DuetNetAggregator()
    picks = [
        agg.aggregate(signals, ctx, DuetNetConfig(top_t=1, tau_p=1.0))
        for _ in range(5)
    ]
    assert all(p["token"] == "a" for p in picks)
    assert picks[0]["reasoning"]["topT_candidates"] == ["a"]
    assert picks[0]["reasoning"]["tie_break_applied"] is False


def test_top_t_one_lex_tie_break(make_ctx, cand):
    """Equal cumulative logits at T=1 → lex-smallest token, no
    randomness (same contract as ``sum_score``)."""
    ctx = make_ctx(weights={"m1": 1.0, "m2": 1.0}, capabilities=_caps("m1", "m2"))
    signals = {
        "per_model": {
            "m1": [cand("zebra", 0.5, 5.0), cand("apple", 0.5, 5.0)],
            "m2": [cand("zebra", 0.5, 5.0), cand("apple", 0.5, 5.0)],
        },
        "per_model_errors": {},
    }
    agg = DuetNetAggregator()
    pick = agg.aggregate(signals, ctx, DuetNetConfig(top_t=1, tau_p=1.0))
    assert pick["token"] == "apple"
    assert pick["reasoning"]["tie_break_applied"] is True


def test_top_t_seed_replays(make_ctx, cand):
    """T>1 with a seed produces an identical sequence of picks across
    runs — replayable trace contract."""
    ctx = make_ctx(weights={"m1": 1.0}, capabilities=_caps("m1"))
    signals = {
        "per_model": {
            "m1": [
                cand("a", 0.4, 5.0),
                cand("b", 0.3, 4.0),
                cand("c", 0.2, 3.5),
                cand("d", 0.1, 3.0),
            ]
        },
        "per_model_errors": {},
    }
    agg = DuetNetAggregator()
    cfg = DuetNetConfig(top_t=4, tau_p=1.0, seed=42)
    runs = [
        [agg.aggregate(signals, ctx, cfg)["token"] for _ in range(5)] for _ in range(2)
    ]
    assert runs[0] == runs[1]


def test_top_t_records_candidate_slice(make_ctx, cand):
    ctx = make_ctx(weights={"m1": 1.0}, capabilities=_caps("m1"))
    signals = {
        "per_model": {
            "m1": [cand("a", 0.4, 5.0), cand("b", 0.3, 4.0), cand("c", 0.2, 3.0)],
        },
        "per_model_errors": {},
    }
    agg = DuetNetAggregator()
    pick = agg.aggregate(signals, ctx, DuetNetConfig(top_t=2, tau_p=1.0, seed=0))
    # Top 2 by cumulative logit: a (5.0) and b (4.0).
    assert sorted(pick["reasoning"]["topT_candidates"]) == ["a", "b"]


def test_negative_logits_supported(make_ctx, cand):
    """Raw logits are commonly negative; the math must work without
    the aggregator silently truncating them at zero."""
    ctx = make_ctx(weights={"m1": 1.0, "m2": 1.0}, capabilities=_caps("m1", "m2"))
    signals = {
        "per_model": {
            "m1": [cand("a", 0.5, -2.0), cand("b", 0.5, -3.0)],
            "m2": [cand("a", 0.5, -1.5), cand("b", 0.5, -1.0)],
        },
        "per_model_errors": {},
    }
    agg = DuetNetAggregator()
    pick = agg.aggregate(signals, ctx, DuetNetConfig(top_t=1, tau_p=1.0))
    # a: -2 + -1.5 = -3.5; b: -3 + -1 = -4.0; a wins despite being negative.
    assert pick["token"] == "a"
    assert pick["score"] == pytest.approx(-3.5)


# ── 6. Empty / error paths ──────────────────────────────────────────────


def test_all_voters_empty(make_ctx):
    ctx = make_ctx(weights={}, capabilities={})
    signals = {"per_model": {}, "per_model_errors": {"m1": "timeout", "m2": "timeout"}}
    agg = DuetNetAggregator()
    pick = agg.aggregate(signals, ctx, DuetNetConfig())
    assert pick["token"] == ""
    assert pick["score"] == 0.0
    assert pick["reasoning"]["all_voters_empty"] is True
    assert sorted(pick["reasoning"]["empty_voters"]) == ["m1", "m2"]


def test_partial_errors_recorded_in_reasoning(make_ctx, cand):
    """Mixed success/failure step: one backend fails, the other still
    drives the pick. ``empty_voters`` carries the failed alias for the
    trace consumer."""
    ctx = make_ctx(weights={"m1": 1.0}, capabilities=_caps("m1"))
    signals = {
        "per_model": {"m1": [cand("hi", 1.0, 7.0)]},
        "per_model_errors": {"m2": "timeout"},
    }
    agg = DuetNetAggregator()
    pick = agg.aggregate(signals, ctx, DuetNetConfig())
    assert pick["token"] == "hi"
    assert pick["reasoning"]["empty_voters"] == ["m2"]


# ── 7. Config schema ────────────────────────────────────────────────────


def test_config_rejects_extra_fields():
    with pytest.raises(ValidationError):
        DuetNetConfig.model_validate({"tau_k": 5, "rogue_field": 1})


def test_config_validates_ranges():
    with pytest.raises(ValidationError):
        DuetNetConfig.model_validate({"tau_p": 1.5})  # must be <= 1.0
    with pytest.raises(ValidationError):
        DuetNetConfig.model_validate({"tau_p": 0.0})  # must be > 0
    with pytest.raises(ValidationError):
        DuetNetConfig.model_validate({"tau_k": 0})  # must be > 0
    with pytest.raises(ValidationError):
        DuetNetConfig.model_validate({"top_t": 0})  # must be > 0


def test_config_paper_defaults():
    """The defaults match the paper's main experimental setting."""
    cfg = DuetNetConfig()
    assert cfg.tau_k == 10
    assert cfg.tau_p == 0.75
    assert cfg.top_t == 1
    assert cfg.seed is None
    assert cfg.use_weights is False
