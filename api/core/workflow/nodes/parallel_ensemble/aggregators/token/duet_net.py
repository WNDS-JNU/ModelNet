"""Token-scope ``duet_net`` aggregator — DuetNet (Wang et al., 2025).

Implements the three-step joint reasoning loop described in
"Token-Level Collaborative Reasoning for Parallel Multi-Models"
(``docs/ModelNet/Token-Level Collaborative Reasoning for Parallel
Multi-Models.pdf``):

  1. Per model: τ_K + τ_P joint truncation (paper Eq. 2). Take each
     model's top-τ_K candidates by post-sampling probability, then
     keep the smallest cumulative-prob prefix that crosses τ_P.
  2. Aggregation: sum **raw logits** across models on the candidate
     union U (paper Eqs. 4-5). Models that did not propose a token
     contribute 0 — the paper deliberately does not penalise absent
     voters, only rewards present ones.
  3. Top-T stochastic sampling on the cumulative-logit ranking
     (paper Eq. 6). T=1 is greedy and deterministic; T>1 picks one
     of the top-T tokens by softmax-weighted multinomial sampling.

Aggregating raw logits requires every contributing backend to declare
:class:`Capability.LOGITS_RAW`. The token-step runner only validates
``TOKEN_STEP`` + ``TOP_PROBS`` (``runners/token_step.py``), so this
aggregator self-checks ``context.capabilities`` on every call. A
missing capability surfaces as :class:`CapabilityNotSupportedError`
naming the offending source so the operator knows which spec to flip
``expose_raw_logits=true`` on, instead of silently summing through
softmax-renormalised probs (which is the ``sum_score`` aggregator,
the paper's GaC-equivalent baseline).

Determinism: T=1 uses argmax over cumulative logits with lex
tie-break (mirroring ``sum_score``'s no-``random.choice`` rule). T>1
seeds ``random.Random(seed)`` so trace replays are bit-stable when a
seed is provided.
"""

from __future__ import annotations

import math
import operator
import random
from typing import ClassVar

from pydantic import BaseModel, ConfigDict, Field

from ...exceptions import CapabilityNotSupportedError, ParallelEnsembleError
from ...registry.aggregator_registry import register_aggregator
from ...spi.aggregator import (
    BackendAggregationContext,
    TokenAggregator,
    TokenPick,
    TokenSignals,
)
from ...spi.capability import Capability


class DuetNetConfig(BaseModel):
    """Hyperparameters mirroring the DuetNet paper's notation."""

    model_config = ConfigDict(extra="forbid")

    tau_k: int = Field(default=10, gt=0)
    """Per-model Top-K truncation (paper τ_K, default 10)."""

    tau_p: float = Field(default=0.75, gt=0, le=1.0)
    """Per-model cumulative-prob threshold for the Top-P pass that
    follows Top-K (paper τ_P, default 0.75)."""

    top_t: int = Field(default=1, gt=0)
    """Number of cumulative-logit candidates to sample from (paper T,
    default 1 = deterministic argmax)."""

    seed: int | None = None
    """RNG seed for ``top_t > 1`` multinomial sampling. ``None`` makes
    each step independently random — only acceptable for ablation runs
    where bit-stable replay is not needed."""

    use_weights: bool = False
    """Apply ``BackendAggregationContext.weights`` to per-model logit
    contributions. Off by default — the paper sums logits unweighted;
    flip on to demote a noisy backend in ablations."""


@register_aggregator("duet_net", scope="token")
class DuetNetAggregator(TokenAggregator[DuetNetConfig]):
    """DuetNet's joint truncation + logit-sum + Top-T sampling."""

    config_class: ClassVar[type[BaseModel]] = DuetNetConfig
    i18n_key_prefix: ClassVar[str] = "parallelEnsemble.aggregators.duetNet"
    ui_schema: ClassVar[dict] = {
        "tau_k": {"control": "number_input", "min": 1, "step": 1},
        "tau_p": {"control": "number_input", "min": 0.01, "max": 1.0, "step": 0.05},
        "top_t": {"control": "number_input", "min": 1, "step": 1},
        "seed": {"control": "number_input"},
        "use_weights": {"control": "switch"},
    }

    def aggregate(
        self,
        signals: TokenSignals,
        context: BackendAggregationContext,
        config: DuetNetConfig,
    ) -> TokenPick:
        per_model = signals["per_model"]
        per_model_errors = signals.get("per_model_errors", {})

        # The runner only validates TOKEN_STEP + TOP_PROBS at startup,
        # so DuetNet has to confirm LOGITS_RAW per-source itself. Doing
        # this on the first decode step lets a stale model_net.yaml
        # that forgot ``expose_raw_logits=true`` fail fast with the
        # offending alias named, instead of silently summing through
        # softmax-renormalised probs (which is what sum_score does).
        for alias in per_model:
            caps = context.capabilities.get(alias, frozenset())
            if Capability.LOGITS_RAW not in caps:
                raise CapabilityNotSupportedError(alias, Capability.LOGITS_RAW.value)

        # Step 1: τ_K + τ_P joint truncation (paper Eq. 2). Backends
        # are expected to return top-k sorted by prob, but resort
        # defensively so a future adapter that emits in a different
        # order does not violate the truncation invariant. ``kept``
        # always contains at least one candidate when the model
        # contributed anything, since the loop runs once before the
        # cumulative threshold check.
        per_model_truncated: dict[str, list] = {}
        for alias, candidates in per_model.items():
            sorted_cands = sorted(
                candidates, key=operator.itemgetter("prob"), reverse=True
            )[: config.tau_k]
            cum, kept = 0.0, []
            for c in sorted_cands:
                kept.append(c)
                cum += c["prob"]
                if cum >= config.tau_p:
                    break
            per_model_truncated[alias] = kept

        # Step 2: candidate union + cumulative raw logits (paper Eqs. 4-5).
        # X_m(u) = logit_m(u) if u in π_m, else 0; C_u = Σ_m X_m(u).
        weights = context.weights if config.use_weights else {}
        token_logits: dict[str, float] = {}
        token_per_model: dict[str, dict[str, float]] = {}
        for alias, kept in per_model_truncated.items():
            w = weights.get(alias, 1.0) if config.use_weights else 1.0
            for c in kept:
                logit = c.get("logit")
                if logit is None:
                    # The capability gate above passed, but the
                    # candidate dict lacks the field. This is an
                    # adapter bug — the backend declared LOGITS_RAW
                    # without populating the field — surface it
                    # explicitly so a fork that flipped the capability
                    # flag without wiring the parser noticed.
                    raise ParallelEnsembleError(
                        f"duet_net: source {alias!r} returned candidate "
                        f"without raw logit; backend declared LOGITS_RAW "
                        f"but adapter did not populate the field"
                    )
                contribution = float(logit) * w
                tok = c["token"]
                token_logits[tok] = token_logits.get(tok, 0.0) + contribution
                token_per_model.setdefault(tok, {})[alias] = contribution

        if not token_logits:
            return {
                "token": "",
                "score": 0.0,
                "reasoning": {
                    "per_token_logit": {},
                    "empty_voters": list(per_model_errors),
                    "all_voters_empty": True,
                },
            }

        # Step 3: Top-T stochastic sampling (paper Eq. 6). Sort items
        # by score desc then lex asc so ties are broken deterministically
        # at T=1 (sum_score / max_score do the same). At T>1 the lex
        # ordering also makes the candidate slice stable across runs,
        # so the seeded multinomial below is genuinely replayable.
        sorted_items = sorted(
            token_logits.items(),
            key=lambda kv: (-kv[1], kv[0]),
        )
        top_t_items = sorted_items[: config.top_t]
        top_score = sorted_items[0][1]
        tied_top_count = sum(1 for _, s in sorted_items if s == top_score)

        if config.top_t == 1 or len(top_t_items) == 1:
            winner_tok, winner_score = top_t_items[0]
            tie_break_applied = tied_top_count > 1
        else:
            tokens = [t for t, _ in top_t_items]
            scores = [s for _, s in top_t_items]
            mx = max(scores)
            unnormalised = [math.exp(s - mx) for s in scores]
            total = sum(unnormalised)
            probs = [u / total for u in unnormalised]
            # The token selection is research-grade sampling, not a
            # security primitive — ``random.Random`` is exactly the right
            # tool. The seed lets the trace replay bit-stably so a
            # downstream reader can reconstruct the decode path.
            rng = random.Random(config.seed)  # noqa: S311
            winner_tok = rng.choices(tokens, weights=probs, k=1)[0]
            winner_score = token_logits[winner_tok]
            tie_break_applied = False

        reasoning: dict = {
            "per_token_logit": dict(token_logits),
            "winner_per_model": token_per_model.get(winner_tok, {}),
            "topT_candidates": [t for t, _ in top_t_items],
            "tau_k": config.tau_k,
            "tau_p": config.tau_p,
            "top_t": config.top_t,
            "tie_break_applied": tie_break_applied,
        }
        if per_model_errors:
            reasoning["empty_voters"] = list(per_model_errors)

        return {
            "token": winner_tok,
            "score": winner_score,
            "reasoning": reasoning,
        }
