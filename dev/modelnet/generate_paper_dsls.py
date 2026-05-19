#!/usr/bin/env python3
"""Generate AI-ModelNet paper-reproduction workflow DSLs.

Emits one AI-ModelNet hybrid router workflow-mode DSL. The router selects
among the 6 S2P / P2S token-level fusion paths at runtime via a required
``path`` input. The paper-model roles are {Q=Qwen2.5-7B,
D=Qwen3-8B thinking stand-in, Y=GLM-4-9B-Chat}. The file is written to
``docs/ModelNet/examples/workflow_mode/paper_hybrid_router.yml``.
Idempotent — overwrites the router file and removes stale ``paper_*.yml``
files from older multi-file generations.

Reproduction context:

* Framing: ``docs/ModelNet/research/UNDERGRAD_RESEARCH_PLAYBOOK.md`` §6 (direction D).
* Stage plan: ``docs/ModelNet/research/PAPER_REPRODUCTION_PLAN.md`` §5.

Pre-flight:

1. S2P / P2S serial stages use Dify's standard ``llm`` node, which does NOT read
   ``api/configs/model_net.yaml``. Pre-configure the 3 paper models
   once via Dify Web → Settings → Model Provider → OpenAI-Compatible
   API plugin. ``--provider`` defaults to
   ``langgenius/openai_api_compatible/openai_api_compatible``;
   override if your install registers a different provider.
2. Hybrid parallel stages use ``parallel-ensemble`` + ``token-model-source`` and *do*
   read ``model_net.yaml``. Aliases ``5`` / ``22`` / ``6`` must be
   present. Alias ``22`` is the current reachable D-role stand-in because
   the original DeepSeek endpoint is unavailable on this host.

S2P and P2S use ``parallel-ensemble`` for their parallel stage so the
generated workflows match the paper's token-level fusion semantics.
They do not use the legacy response-level ``strategy_name`` /
``strategy_config`` response-aggregator surface.

Run::

    uv run --project api python dev/modelnet/generate_paper_dsls.py
"""

from __future__ import annotations

import argparse
import sys
import uuid
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
EXAMPLES_DIR = REPO_ROOT / "docs" / "ModelNet" / "examples" / "workflow_mode"

DEFAULT_LLM_PROVIDER = "langgenius/openai_api_compatible/openai_api_compatible"
LLM_MODE = "chat"
LLM_TEMPERATURE = 0.0
LLM_MAX_TOKENS = 512


# ── Paper model registry ──────────────────────────────────────────────


@dataclass(frozen=True)
class PaperModel:
    letter: str         # paper notation: Q / D / Y
    model_alias: str    # PI / token-model-source — matches model_net.yaml id
    model_name: str     # standard llm node — matches Dify provider entity name
    description: str

    @property
    def title(self) -> str:
        return f"{self.letter} ({self.description})"


Q = PaperModel("Q", "5", "qwen25-7b-instruct-q5km", "Qwen2.5-7B-Instruct")
D = PaperModel("D", "22", "qwen3-8b-bf16", "Qwen3-8B-BF16 (D-role stand-in)")
Y = PaperModel("Y", "6", "glm-4-9b-chat-q4k", "GLM-4-9B-Chat")

PAPER_MODELS: list[PaperModel] = [Q, D, Y]


# ── Prompt templates ─────────────────────────────────────────────────
#
# Approximation of paper Table 2: each model is asked to reason and
# produce a final answer; serial steps see the prior step's reply for
# refinement; the synthesis model sees the token-level parallel answer.

SYS_LEAF = (
    "You are a careful problem-solver. Read the question, reason step "
    "by step, and provide your final answer at the end of the reply."
)
SYS_REFINE = (
    "You are a careful problem-solver. A peer model has produced a "
    "candidate answer to the same question. Read it, decide whether to "
    "keep or correct it, then provide your own final answer."
)
SYS_SYNTHESIZE = (
    "You are a careful problem-solver. Read the question and the "
    "candidate answers from peer models, then provide a unified final "
    "answer that you have validated."
)

USR_LEAF = "{{#start_node.question#}}"
_USR_REFINE_TPL = (
    "Question:\n{{{{#start_node.question#}}}}\n\n"
    "A peer model proposed:\n{{{{#{prev_node}.text#}}}}\n\n"
    "Provide your own final answer:"
)
_USR_SYNTHESIZE_TPL = (
    "Question:\n{{{{#start_node.question#}}}}\n\n"
    "Candidate answer from the parallel token-level ensemble:\n{{{{#{aggregator}.text#}}}}\n\n"
    "Provide your unified final answer:"
)

_USR_S2P_PARALLEL_TPL = (
    "Question:\n{{{{#start_node.question#}}}}\n\n"
    "Stage-1 semantic draft:\n{{{{#{serial_node}.text#}}}}\n\n"
    "Use the draft as shared context, refine it, and put the final answer at the end."
)


def _refine_user(prev_node: str) -> str:
    return _USR_REFINE_TPL.format(prev_node=prev_node)


def _synthesize_user(aggregator: str) -> str:
    return _USR_SYNTHESIZE_TPL.format(aggregator=aggregator)


def _s2p_parallel_prompt(serial_node: str) -> str:
    return _USR_S2P_PARALLEL_TPL.format(serial_node=serial_node)


# ── Helpers ───────────────────────────────────────────────────────────


def _uid(*parts: str) -> str:
    """Deterministic UUID from a slash-joined seed (idempotent generation)."""
    return str(uuid.uuid5(uuid.NAMESPACE_OID, "/".join(parts)))


def _stack_y(index: int, total: int, anchor: int = 252, spacing: int = 152) -> int:
    """Stack siblings vertically, centred on ``anchor``."""
    top = anchor - (total - 1) * spacing // 2
    return top + index * spacing


# ── Node builders ────────────────────────────────────────────────────


def _start_node(y: int = 252, *, path_options: list[str] | None = None) -> dict:
    variables: list[dict] = []
    if path_options:
        variables.append(
            {
                "label": "path",
                "max_length": 128,
                "options": path_options,
                "required": True,
                "type": "select",
                "variable": "path",
            }
        )
    variables.append(
        {
            "label": "question",
            "max_length": 4096,
            "options": [],
            "required": True,
            "type": "paragraph",
            "variable": "question",
        }
    )
    return {
        "id": "start_node",
        "type": "custom",
        "data": {
            "desc": "User question routed to the paradigm topology.",
            "selected": False,
            "title": "Start",
            "type": "start",
            "variables": variables,
        },
        "height": 112 if path_options else 90,
        "position": {"x": 30, "y": y},
        "positionAbsolute": {"x": 30, "y": y},
        "selected": False,
        "sourcePosition": "right",
        "targetPosition": "left",
        "width": 244,
    }


def _end_node(
    answer_selector: list[str],
    x: int,
    y: int = 252,
    *,
    node_id: str = "end_node",
    title: str = "End",
    desc: str = "Emit the paradigm's final answer.",
) -> dict:
    return {
        "id": node_id,
        "type": "custom",
        "data": {
            "desc": desc,
            "outputs": [
                {
                    "value_selector": answer_selector,
                    "value_type": "string",
                    "variable": "answer",
                },
            ],
            "selected": False,
            "title": title,
            "type": "end",
        },
        "height": 90,
        "position": {"x": x, "y": y},
        "positionAbsolute": {"x": x, "y": y},
        "selected": False,
        "sourcePosition": "right",
        "targetPosition": "left",
        "width": 244,
    }


def _llm_node(
    *,
    node_id: str,
    title: str,
    desc: str,
    model_name: str,
    provider: str,
    system: str,
    user: str,
    x: int,
    y: int,
) -> dict:
    return {
        "id": node_id,
        "type": "custom",
        "data": {
            "context": {"enabled": False, "variable_selector": []},
            "desc": desc,
            "memory": {
                "query_prompt_template": "{{#sys.query#}}",
                "role_prefix": {"assistant": "", "user": ""},
                "window": {"enabled": False, "size": 50},
            },
            "model": {
                "completion_params": {
                    "max_tokens": LLM_MAX_TOKENS,
                    "temperature": LLM_TEMPERATURE,
                },
                "mode": LLM_MODE,
                "name": model_name,
                "provider": provider,
            },
            "prompt_template": [
                {"id": _uid(node_id, "system"), "role": "system", "text": system},
                {"id": _uid(node_id, "user"), "role": "user", "text": user},
            ],
            "selected": False,
            "title": title,
            "type": "llm",
            "variables": [],
            "vision": {"enabled": False},
        },
        "height": 90,
        "position": {"x": x, "y": y},
        "positionAbsolute": {"x": x, "y": y},
        "selected": False,
        "sourcePosition": "right",
        "targetPosition": "left",
        "width": 244,
    }


def _token_source_node(
    model: PaperModel,
    x: int,
    y: int,
    *,
    node_id: str | None = None,
    prompt_template: str = "{{#start_node.question#}}",
    title: str | None = None,
    desc: str | None = None,
) -> dict:
    actual_id = node_id or f"token_{model.letter}"
    return {
        "id": actual_id,
        "type": "custom",
        "data": {
            "desc": (
                desc
                or f"Renders the prompt for {model.title}, "
                f"alias {model.model_alias}; emits a ModelInvocationSpec."
            ),
            "extra": {},
            "model_alias": model.model_alias,
            "prompt_template": prompt_template,
            "sampling_params": {
                "max_tokens": LLM_MAX_TOKENS,
                "temperature": 0.7,
                "top_k": 10,
            },
            "selected": False,
            "title": title or f"Token Source ({model.letter})",
            "type": "token-model-source",
        },
        "height": 130,
        "position": {"x": x, "y": y},
        "positionAbsolute": {"x": x, "y": y},
        "selected": False,
        "sourcePosition": "right",
        "targetPosition": "left",
        "width": 244,
    }


def _ensemble_node(
    models: list[PaperModel],
    x: int,
    y: int = 252,
    *,
    node_id: str = "ensemble",
    title: str = "Parallel Ensemble (PI)",
    desc: str | None = None,
    token_node_ids: list[str] | None = None,
) -> dict:
    source_node_ids = token_node_ids or [f"token_{m.letter}" for m in models]
    return {
        "id": node_id,
        "type": "custom",
        "data": {
            "desc": (
                desc
                or "Token-level parallel ensemble — sum_score aggregator "
                "(probability-sum vote across the union of top-k "
                "candidates from each backend per decode step)."
            ),
            "ensemble": {
                "aggregator_config": {"seed": None, "tau_p": 1.0, "use_weights": False},
                "aggregator_name": "sum_score",
                "diagnostics": {
                    "include_aggregator_reasoning": True,
                    "include_per_backend_errors": True,
                    "include_response_timings": True,
                    "include_token_candidates": False,
                    "max_trace_tokens": 2000,
                    "storage": "metadata",
                },
                "runner_config": {"enable_think": False, "max_len": LLM_MAX_TOKENS},
                "runner_name": "token_step",
                "token_sources": [
                    {
                        "source_id": m.letter,
                        "spec_selector": [source_node_id, "spec"],
                        "weight": 1.0,
                    }
                    for m, source_node_id in zip(models, source_node_ids)
                ],
            },
            "selected": False,
            "title": title,
            "type": "parallel-ensemble",
        },
        "height": 200,
        "position": {"x": x, "y": y},
        "positionAbsolute": {"x": x, "y": y},
        "selected": False,
        "sourcePosition": "right",
        "targetPosition": "left",
        "width": 244,
    }


def _edge(
    *,
    src: str,
    dst: str,
    src_type: str,
    dst_type: str,
    source_handle: str = "source",
    target_handle: str = "target",
) -> dict:
    return {
        "id": f"{src}-{source_handle}-to-{dst}",
        "source": src,
        "sourceHandle": source_handle,
        "target": dst,
        "targetHandle": target_handle,
        "type": "custom",
        "zIndex": 0,
        "data": {
            "isInIteration": False,
            "isInLoop": False,
            "sourceType": src_type,
            "targetType": dst_type,
        },
    }


# ── Paradigm builders ────────────────────────────────────────────────


def build_si(models: list[PaperModel], provider: str) -> dict:
    """SI: serial chain M1 → M2 → M3."""
    nodes: list[dict] = [_start_node()]
    edges: list[dict] = []
    prev_id = "start_node"
    prev_type = "start"
    for i, m in enumerate(models):
        node_id = f"llm_{m.letter}_step{i + 1}"
        if i == 0:
            system = SYS_LEAF
            user = USR_LEAF
        else:
            system = SYS_REFINE
            user = _refine_user(prev_id)
        nodes.append(
            _llm_node(
                node_id=node_id,
                title=f"{m.letter} (step {i + 1})",
                desc=f"Step {i + 1} of SI chain — {m.description}.",
                model_name=m.model_name,
                provider=provider,
                system=system,
                user=user,
                x=334 + 304 * i,
                y=252,
            )
        )
        edges.append(_edge(src=prev_id, dst=node_id, src_type=prev_type, dst_type="llm"))
        prev_id, prev_type = node_id, "llm"
    nodes.append(_end_node([prev_id, "text"], x=334 + 304 * len(models)))
    edges.append(_edge(src=prev_id, dst="end_node", src_type="llm", dst_type="end"))
    chain = " → ".join(m.letter for m in models)
    desc_chain = " → ".join(m.description for m in models)
    return _wrap(
        name=f"paper_si_{''.join(m.letter for m in models)} (workflow)",
        desc=(
            f"AI-ModelNet paper SI path {chain} ({desc_chain}). Each "
            "model in the chain refines the previous answer via paper "
            "Table 2's refine template (approximated)."
        ),
        nodes=nodes,
        edges=edges,
    )


def build_pi(models: list[PaperModel]) -> dict:
    """PI: token-level parallel ensemble (paper Fig. 5b)."""
    nodes: list[dict] = [_start_node()]
    n = len(models)
    for i, m in enumerate(models):
        nodes.append(_token_source_node(m, x=334, y=_stack_y(i, n)))
    nodes.append(_ensemble_node(models, x=638))
    nodes.append(_end_node(["ensemble", "text"], x=942))
    edges: list[dict] = []
    for m in models:
        edges.append(
            _edge(
                src="start_node",
                dst=f"token_{m.letter}",
                src_type="start",
                dst_type="token-model-source",
            )
        )
        edges.append(
            _edge(
                src=f"token_{m.letter}",
                dst="ensemble",
                src_type="token-model-source",
                dst_type="parallel-ensemble",
            )
        )
    edges.append(
        _edge(src="ensemble", dst="end_node", src_type="parallel-ensemble", dst_type="end")
    )
    return _wrap(
        name=f"paper_pi_{''.join(m.letter for m in models)} (workflow)",
        desc=(
            "AI-ModelNet paper PI path "
            f"[{', '.join(m.letter for m in models)}] "
            f"({', '.join(m.description for m in models)}). Token-level "
            "parallel ensemble using sum_score (probability-sum vote across "
            "the union of top-k per decode step), matching paper Fig. 5b. "
            "Reads aliases directly from api/configs/model_net.yaml; the "
            "standard llm node is not used."
        ),
        nodes=nodes,
        edges=edges,
    )


def build_s2p(serial: PaperModel, parallel: list[PaperModel], provider: str) -> dict:
    """S2P: serial LLM → token-level parallel ensemble."""
    nodes: list[dict] = [_start_node()]
    edges: list[dict] = []

    # Stage 1 — serial
    serial_id = f"llm_{serial.letter}_serial"
    nodes.append(
        _llm_node(
            node_id=serial_id,
            title=f"{serial.letter} (serial)",
            desc=f"S2P stage 1 — {serial.description}.",
            model_name=serial.model_name,
            provider=provider,
            system=SYS_LEAF,
            user=USR_LEAF,
            x=334,
            y=252,
        )
    )
    edges.append(_edge(src="start_node", dst=serial_id, src_type="start", dst_type="llm"))

    # Stage 2 — token-level parallel branches read from the serial stage.
    token_ids: list[str] = []
    for i, m in enumerate(parallel):
        node_id = f"token_{m.letter}_par"
        nodes.append(
            _token_source_node(
                model=m,
                x=638,
                y=_stack_y(i, len(parallel)),
                node_id=node_id,
                title=f"Token Source ({m.letter}, S2P)",
                desc=(
                    f"S2P stage 2 source — {m.description} receives the "
                    "stage-1 semantic draft and participates in token-level fusion."
                ),
                prompt_template=_s2p_parallel_prompt(serial_id),
            )
        )
        edges.append(_edge(src=serial_id, dst=node_id, src_type="llm", dst_type="token-model-source"))
        token_ids.append(node_id)

    nodes.append(
        _ensemble_node(
            parallel,
            x=942,
            node_id="aggregator",
            title="Parallel Ensemble (S2P)",
            desc=(
                "S2P stage 2 token-level parallel ensemble. Each selected "
                "token is fused with sum_score across the parallel models, "
                "matching the paper's parallel branch semantics."
            ),
            token_node_ids=token_ids,
        )
    )
    for pid in token_ids:
        edges.append(
            _edge(src=pid, dst="aggregator", src_type="token-model-source", dst_type="parallel-ensemble")
        )

    nodes.append(_end_node(["aggregator", "text"], x=1246))
    edges.append(
        _edge(src="aggregator", dst="end_node", src_type="parallel-ensemble", dst_type="end")
    )

    return _wrap(
        name=(
            f"paper_s2p_{serial.letter}_"
            f"{''.join(m.letter for m in parallel)} (workflow)"
        ),
        desc=(
            f"AI-ModelNet paper S2P path {serial.letter} → "
            f"[{', '.join(m.letter for m in parallel)}]. Stage 1 = "
            f"{serial.description}; Stage 2 (parallel) = "
            f"{', '.join(m.description for m in parallel)}; Stage-2 outputs "
            "are fused by a token-level parallel-ensemble node."
        ),
        nodes=nodes,
        edges=edges,
    )


def build_p2s(parallel: list[PaperModel], serial: PaperModel, provider: str) -> dict:
    """P2S: token-level parallel ensemble → serial LLM."""
    nodes: list[dict] = [_start_node()]
    edges: list[dict] = []

    # Stage 1 — token-level parallel branches off start.
    token_ids: list[str] = []
    for i, m in enumerate(parallel):
        node_id = f"token_{m.letter}_par"
        nodes.append(
            _token_source_node(
                model=m,
                x=334,
                y=_stack_y(i, len(parallel)),
                node_id=node_id,
                title=f"Token Source ({m.letter}, P2S)",
                desc=f"P2S stage 1 source — {m.description} participates in token-level fusion.",
                prompt_template=USR_LEAF,
            )
        )
        edges.append(_edge(src="start_node", dst=node_id, src_type="start", dst_type="token-model-source"))
        token_ids.append(node_id)

    nodes.append(
        _ensemble_node(
            parallel,
            x=638,
            node_id="aggregator",
            title="Parallel Ensemble (P2S)",
            desc=(
                "P2S stage 1 token-level parallel ensemble. The fused "
                "intermediate sequence feeds the serial synthesizer."
            ),
            token_node_ids=token_ids,
        )
    )
    for pid in token_ids:
        edges.append(
            _edge(src=pid, dst="aggregator", src_type="token-model-source", dst_type="parallel-ensemble")
        )

    # Stage 2 — serial synthesizer
    serial_id = f"llm_{serial.letter}_serial"
    nodes.append(
        _llm_node(
            node_id=serial_id,
            title=f"{serial.letter} (synthesizer)",
            desc=f"P2S stage 2 — {serial.description} synthesizes peer answers.",
            model_name=serial.model_name,
            provider=provider,
            system=SYS_SYNTHESIZE,
            user=_synthesize_user("aggregator"),
            x=942,
            y=252,
        )
    )
    edges.append(
        _edge(src="aggregator", dst=serial_id, src_type="parallel-ensemble", dst_type="llm")
    )

    nodes.append(_end_node([serial_id, "text"], x=1246))
    edges.append(_edge(src=serial_id, dst="end_node", src_type="llm", dst_type="end"))

    return _wrap(
        name=(
            f"paper_p2s_{''.join(m.letter for m in parallel)}_{serial.letter} (workflow)"
        ),
        desc=(
            "AI-ModelNet paper P2S path "
            f"[{', '.join(m.letter for m in parallel)}] → {serial.letter}. "
            "Stage 1 (parallel) = "
            f"{', '.join(m.description for m in parallel)}; Stage 2 = "
            f"{serial.description} synthesizes the fused token-level intermediate answer."
        ),
        nodes=nodes,
        edges=edges,
    )


def _route_node(path_names: list[str], *, x: int = 334, y: int = 1180) -> dict:
    return {
        "id": "route_path",
        "type": "custom",
        "data": {
            "desc": "Route one unified hybrid workflow to the requested S2P/P2S path.",
            "_targetBranches": [{"id": name, "name": name} for name in path_names],
            "cases": [
                {
                    "case_id": name,
                    "logical_operator": "and",
                    "conditions": [
                        {
                            "id": f"cond_{name}",
                            "varType": "string",
                            "variable_selector": ["start_node", "path"],
                            "comparison_operator": "is",
                            "value": name,
                        }
                    ],
                }
                for name in path_names
            ],
            "isInIteration": False,
            "isInLoop": False,
            "selected": False,
            "title": "Route: hybrid path",
            "type": "if-else",
        },
        "height": 250,
        "position": {"x": x, "y": y},
        "positionAbsolute": {"x": x, "y": y},
        "selected": False,
        "sourcePosition": "right",
        "targetPosition": "left",
        "width": 244,
    }


def _add_s2p_router_branch(
    *,
    path_name: str,
    serial: PaperModel,
    parallel: list[PaperModel],
    provider: str,
    base_y: int,
    nodes: list[dict],
    edges: list[dict],
) -> None:
    serial_id = f"{path_name}__llm_{serial.letter}_serial"
    nodes.append(
        _llm_node(
            node_id=serial_id,
            title=f"{path_name}: {serial.letter} serial",
            desc=f"{path_name} stage 1 — {serial.description}.",
            model_name=serial.model_name,
            provider=provider,
            system=SYS_LEAF,
            user=USR_LEAF,
            x=638,
            y=base_y + 76,
        )
    )
    edges.append(
        _edge(
            src="route_path",
            dst=serial_id,
            src_type="if-else",
            dst_type="llm",
            source_handle=path_name,
        )
    )

    token_ids: list[str] = []
    for i, m in enumerate(parallel):
        node_id = f"{path_name}__token_{m.letter}_par"
        nodes.append(
            _token_source_node(
                model=m,
                x=942,
                y=base_y + i * 152,
                node_id=node_id,
                title=f"{path_name}: token source {m.letter}",
                desc=(
                    f"{path_name} parallel source — {m.description} receives the "
                    "stage-1 semantic draft and participates in token-level fusion."
                ),
                prompt_template=_s2p_parallel_prompt(serial_id),
            )
        )
        edges.append(_edge(src=serial_id, dst=node_id, src_type="llm", dst_type="token-model-source"))
        token_ids.append(node_id)

    aggregator_id = f"{path_name}__aggregator"
    nodes.append(
        _ensemble_node(
            parallel,
            x=1246,
            y=base_y + 76,
            node_id=aggregator_id,
            title=f"{path_name}: parallel ensemble",
            desc=f"{path_name} token-level S2P parallel ensemble.",
            token_node_ids=token_ids,
        )
    )
    for token_id in token_ids:
        edges.append(
            _edge(
                src=token_id,
                dst=aggregator_id,
                src_type="token-model-source",
                dst_type="parallel-ensemble",
            )
        )

    end_id = f"{path_name}__end"
    nodes.append(
        _end_node(
            [aggregator_id, "text"],
            x=1550,
            y=base_y + 76,
            node_id=end_id,
            title=f"End: {path_name}",
            desc=f"Emit answer for {path_name}.",
        )
    )
    edges.append(_edge(src=aggregator_id, dst=end_id, src_type="parallel-ensemble", dst_type="end"))


def _add_p2s_router_branch(
    *,
    path_name: str,
    parallel: list[PaperModel],
    serial: PaperModel,
    provider: str,
    base_y: int,
    nodes: list[dict],
    edges: list[dict],
) -> None:
    token_ids: list[str] = []
    for i, m in enumerate(parallel):
        node_id = f"{path_name}__token_{m.letter}_par"
        nodes.append(
            _token_source_node(
                model=m,
                x=638,
                y=base_y + i * 152,
                node_id=node_id,
                title=f"{path_name}: token source {m.letter}",
                desc=f"{path_name} parallel source — {m.description} participates in token-level fusion.",
                prompt_template=USR_LEAF,
            )
        )
        edges.append(
            _edge(
                src="route_path",
                dst=node_id,
                src_type="if-else",
                dst_type="token-model-source",
                source_handle=path_name,
            )
        )
        token_ids.append(node_id)

    aggregator_id = f"{path_name}__aggregator"
    nodes.append(
        _ensemble_node(
            parallel,
            x=942,
            y=base_y + 76,
            node_id=aggregator_id,
            title=f"{path_name}: parallel ensemble",
            desc=f"{path_name} token-level P2S parallel ensemble.",
            token_node_ids=token_ids,
        )
    )
    for token_id in token_ids:
        edges.append(
            _edge(
                src=token_id,
                dst=aggregator_id,
                src_type="token-model-source",
                dst_type="parallel-ensemble",
            )
        )

    serial_id = f"{path_name}__llm_{serial.letter}_serial"
    nodes.append(
        _llm_node(
            node_id=serial_id,
            title=f"{path_name}: {serial.letter} synthesizer",
            desc=f"{path_name} serial synthesizer — {serial.description}.",
            model_name=serial.model_name,
            provider=provider,
            system=SYS_SYNTHESIZE,
            user=_synthesize_user(aggregator_id),
            x=1246,
            y=base_y + 76,
        )
    )
    edges.append(_edge(src=aggregator_id, dst=serial_id, src_type="parallel-ensemble", dst_type="llm"))

    end_id = f"{path_name}__end"
    nodes.append(
        _end_node(
            [serial_id, "text"],
            x=1550,
            y=base_y + 76,
            node_id=end_id,
            title=f"End: {path_name}",
            desc=f"Emit answer for {path_name}.",
        )
    )
    edges.append(_edge(src=serial_id, dst=end_id, src_type="llm", dst_type="end"))


def build_hybrid_router(provider: str) -> dict:
    """One workflow DSL that routes to any S2P/P2S hybrid path."""
    specs = hybrid_specs()
    path_names = [name for name, *_ in specs]
    nodes: list[dict] = [_start_node(y=1180, path_options=path_names), _route_node(path_names)]
    edges: list[dict] = [_edge(src="start_node", dst="route_path", src_type="start", dst_type="if-else")]

    for i, spec in enumerate(specs):
        path_name = spec[0]
        kind = spec[1]
        base_y = 80 + i * 360
        if kind == "s2p":
            _, _, serial, parallel = spec
            _add_s2p_router_branch(
                path_name=path_name,
                serial=serial,
                parallel=parallel,
                provider=provider,
                base_y=base_y,
                nodes=nodes,
                edges=edges,
            )
        else:
            _, _, parallel, serial = spec
            _add_p2s_router_branch(
                path_name=path_name,
                parallel=parallel,
                serial=serial,
                provider=provider,
                base_y=base_y,
                nodes=nodes,
                edges=edges,
            )

    return _wrap(
        name="paper_hybrid_router (workflow)",
        desc=(
            "Unified AI-ModelNet hybrid workflow. The required `path` input selects "
            "one of the six S2P/P2S token-level fusion paths, while `question` is "
            "routed into that branch."
        ),
        nodes=nodes,
        edges=edges,
    )


# ── Workflow envelope ────────────────────────────────────────────────


def _wrap(*, name: str, desc: str, nodes: list[dict], edges: list[dict]) -> dict:
    return {
        "app": {
            "description": desc,
            "icon": "🎼",
            "icon_background": "#DCE5FF",
            "mode": "workflow",
            "name": name,
            "use_icon_as_answer_icon": False,
        },
        "kind": "app",
        "version": "0.3.1",
        "workflow": {
            "conversation_variables": [],
            "environment_variables": [],
            "features": {
                "file_upload": {"enabled": False},
                "opening_statement": "",
                "retriever_resource": {"enabled": False},
                "sensitive_word_avoidance": {"enabled": False},
                "speech_to_text": {"enabled": False},
                "suggested_questions": [],
                "suggested_questions_after_answer": {"enabled": False},
                "text_to_speech": {"enabled": False},
            },
            "graph": {
                "edges": edges,
                "nodes": nodes,
                "viewport": {"x": 0, "y": 0, "zoom": 0.7},
            },
        },
    }


# ── Path enumeration ─────────────────────────────────────────────────


def hybrid_specs() -> list[tuple[str, str, PaperModel | list[PaperModel], PaperModel | list[PaperModel]]]:
    """The six S2P/P2S hybrid paths the current reproduction keeps."""
    return [
        ("paper_s2p_Q_DY", "s2p", Q, [D, Y]),
        ("paper_s2p_D_QY", "s2p", D, [Q, Y]),
        ("paper_s2p_Y_QD", "s2p", Y, [Q, D]),
        ("paper_p2s_QD_Y", "p2s", [Q, D], Y),
        ("paper_p2s_QY_D", "p2s", [Q, Y], D),
        ("paper_p2s_DY_Q", "p2s", [D, Y], Q),
    ]


def all_paths(provider: str) -> list[tuple[str, dict]]:
    """Enumerate managed DSLs: the single unified hybrid router."""
    return [("paper_hybrid_router", build_hybrid_router(provider))]


# ── main ─────────────────────────────────────────────────────────────


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out-dir",
        default=str(EXAMPLES_DIR),
        help=f"output directory (default: {EXAMPLES_DIR})",
    )
    parser.add_argument(
        "--provider",
        default=DEFAULT_LLM_PROVIDER,
        help=(
            "Dify provider identifier for the standard llm nodes used by "
            "SI / S2P / P2S (default: %(default)s — the OpenAI-Compatible "
            "API plugin). Override if your install registers a different "
            "provider."
        ),
    )
    args = parser.parse_args()

    try:
        import yaml  # noqa: PLC0415
    except ImportError:
        print(
            "PyYAML required: pip install pyyaml (only needed for the generator)",
            file=sys.stderr,
        )
        return 1

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[str] = []
    paths = all_paths(args.provider)
    expected_files = {f"{name}.yml" for name, _ in paths}
    for stale in sorted(out_dir.glob("paper_*.yml")):
        if stale.name not in expected_files:
            stale.unlink()
            try:
                display_path = str(stale.relative_to(REPO_ROOT))
            except ValueError:
                display_path = str(stale)
            print(f"removed {display_path}")

    for name, dsl in paths:
        path = out_dir / f"{name}.yml"
        with path.open("w", encoding="utf-8") as fh:
            yaml.safe_dump(
                dsl,
                fh,
                allow_unicode=True,
                sort_keys=True,
                width=80,
                default_flow_style=False,
            )
        try:
            display_path = str(path.relative_to(REPO_ROOT))
        except ValueError:
            display_path = str(path)
        written.append(display_path)
    for p in written:
        print(f"wrote {p}")
    print(f"\nGenerated {len(written)} DSL files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
