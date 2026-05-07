#!/usr/bin/env python3
"""Generate AI-ModelNet paper-reproduction workflow DSLs.

Emits 13 workflow-mode DSLs covering 4 paradigms (SI / PI / S2P / P2S)
× 3 paper models {Q=Qwen2.5-7B, D=DeepSeek-R1-Distill-Qwen-7B,
Y=GLM-4-9B-Chat} into ``docs/ModelNet/examples/workflow_mode/paper_*.yml``.
Idempotent — overwrites existing files.

Reproduction context:

* Framing: ``docs/ModelNet/UNDERGRAD_RESEARCH_PLAYBOOK.md`` §6 (direction D).
* Stage plan: ``docs/ModelNet/PAPER_REPRODUCTION_PLAN.md`` §5 (Stage B).

Pre-flight:

1. SI / S2P / P2S use Dify's standard ``llm`` node, which does NOT read
   ``api/configs/model_net.yaml``. Pre-configure the 3 paper models
   once via Dify Web → Settings → Model Provider → OpenAI-Compatible
   API plugin. ``--provider`` defaults to
   ``langgenius/openai_api_compatible/openai_api_compatible``;
   override if your install registers a different provider.
2. PI uses ``parallel-ensemble`` + ``token-model-source`` and *does*
   read ``model_net.yaml``. Aliases ``5`` / ``27`` / ``6`` must be
   present (they already are at HEAD).

Phase fidelity gap (until ``majority_vote`` lands per
``PAPER_REPRODUCTION_PLAN.md`` §4.1): the S2P paths fall back to the
``concat`` response-aggregator strategy because ``majority_vote`` is
not yet registered. The S2P DSLs continue to import and run, but the
final aggregated text is a *concatenation* of the two parallel
answers, not a vote — accuracy will undercount the paper. Regenerate
this directory after Phase 3 lands.

Run::

    uv run --project api python dev/modelnet/generate_paper_dsls.py
"""

from __future__ import annotations

import argparse
import sys
import uuid
from dataclasses import dataclass
from itertools import permutations
from pathlib import Path
from typing import Any

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
D = PaperModel("D", "27", "deepseek-r1-distill-qwen-7b-q4", "DeepSeek-R1-Distill-Qwen-7B")
Y = PaperModel("Y", "6", "glm-4-9b-chat-q4k", "GLM-4-9B-Chat")

PAPER_MODELS: list[PaperModel] = [Q, D, Y]


# ── Prompt templates ─────────────────────────────────────────────────
#
# Approximation of paper Table 2: each model is asked to reason and
# produce a final answer; serial steps see the prior step's reply for
# refinement; the synthesis model sees concatenated peer answers.

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
    "Candidate answers from peer models:\n{{{{#{aggregator}.text#}}}}\n\n"
    "Provide your unified final answer:"
)


def _refine_user(prev_node: str) -> str:
    return _USR_REFINE_TPL.format(prev_node=prev_node)


def _synthesize_user(aggregator: str) -> str:
    return _USR_SYNTHESIZE_TPL.format(aggregator=aggregator)


# ── Helpers ───────────────────────────────────────────────────────────


def _uid(*parts: str) -> str:
    """Deterministic UUID from a slash-joined seed (idempotent generation)."""
    return str(uuid.uuid5(uuid.NAMESPACE_OID, "/".join(parts)))


def _stack_y(index: int, total: int, anchor: int = 252, spacing: int = 152) -> int:
    """Stack siblings vertically, centred on ``anchor``."""
    top = anchor - (total - 1) * spacing // 2
    return top + index * spacing


# ── Node builders ────────────────────────────────────────────────────


def _start_node(y: int = 252) -> dict:
    return {
        "id": "start_node",
        "type": "custom",
        "data": {
            "desc": "User question routed to the paradigm topology.",
            "selected": False,
            "title": "Start",
            "type": "start",
            "variables": [
                {
                    "label": "question",
                    "max_length": 4096,
                    "options": [],
                    "required": True,
                    "type": "paragraph",
                    "variable": "question",
                }
            ],
        },
        "height": 90,
        "position": {"x": 30, "y": y},
        "positionAbsolute": {"x": 30, "y": y},
        "selected": False,
        "sourcePosition": "right",
        "targetPosition": "left",
        "width": 244,
    }


def _end_node(answer_selector: list[str], x: int, y: int = 252) -> dict:
    return {
        "id": "end_node",
        "type": "custom",
        "data": {
            "desc": "Emit the paradigm's final answer.",
            "outputs": [
                {
                    "value_selector": answer_selector,
                    "value_type": "string",
                    "variable": "answer",
                },
            ],
            "selected": False,
            "title": "End",
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


def _token_source_node(model: PaperModel, x: int, y: int) -> dict:
    return {
        "id": f"token_{model.letter}",
        "type": "custom",
        "data": {
            "desc": (
                f"Renders the prompt for {model.title}, "
                f"alias {model.model_alias}; emits a ModelInvocationSpec."
            ),
            "extra": {},
            "model_alias": model.model_alias,
            "prompt_template": "{{#start_node.question#}}",
            "sampling_params": {
                "max_tokens": LLM_MAX_TOKENS,
                "temperature": 0.7,
                "top_k": 10,
            },
            "selected": False,
            "title": f"Token Source ({model.letter})",
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


def _ensemble_node(models: list[PaperModel], x: int, y: int = 252) -> dict:
    return {
        "id": "ensemble",
        "type": "custom",
        "data": {
            "desc": (
                "Token-level parallel ensemble — sum_score aggregator "
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
                        "spec_selector": [f"token_{m.letter}", "spec"],
                        "weight": 1.0,
                    }
                    for m in models
                ],
            },
            "selected": False,
            "title": "Parallel Ensemble (PI)",
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


def _response_aggregator_node(
    *,
    node_id: str,
    title: str,
    desc: str,
    inputs: list[tuple[str, list[str]]],
    strategy_name: str,
    strategy_config: dict[str, Any],
    x: int,
    y: int = 252,
) -> dict:
    return {
        "id": node_id,
        "type": "custom",
        "data": {
            "desc": desc,
            "inputs": [
                {"source_id": sid, "variable_selector": list(sel)}
                for sid, sel in inputs
            ],
            "selected": False,
            "strategy_config": strategy_config,
            "strategy_name": strategy_name,
            "title": title,
            "type": "response-aggregator",
        },
        "height": 150,
        "position": {"x": x, "y": y},
        "positionAbsolute": {"x": x, "y": y},
        "selected": False,
        "sourcePosition": "right",
        "targetPosition": "left",
        "width": 244,
    }


def _edge(*, src: str, dst: str, src_type: str, dst_type: str) -> dict:
    return {
        "id": f"{src}-to-{dst}",
        "source": src,
        "sourceHandle": "source",
        "target": dst,
        "targetHandle": "target",
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
    """S2P: serial → [parallel] → response-aggregator(concat fallback).

    The paper specifies majority_vote at the aggregator. Until the
    ``majority_vote`` strategy lands (Phase 3 of
    ``PAPER_REPRODUCTION_PLAN.md`` §4.1), the DSL falls back to ``concat``,
    so the output is a concatenation of the two parallel answers, not a
    vote. Re-import after Phase 3 to recover paper fidelity.
    """
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

    # Stage 2 — parallel branches read from the serial stage
    parallel_ids: list[str] = []
    for i, m in enumerate(parallel):
        node_id = f"llm_{m.letter}_par"
        nodes.append(
            _llm_node(
                node_id=node_id,
                title=f"{m.letter} (parallel)",
                desc=f"S2P stage 2 — {m.description} refines stage-1 reply.",
                model_name=m.model_name,
                provider=provider,
                system=SYS_REFINE,
                user=_refine_user(serial_id),
                x=638,
                y=_stack_y(i, len(parallel)),
            )
        )
        edges.append(_edge(src=serial_id, dst=node_id, src_type="llm", dst_type="llm"))
        parallel_ids.append(node_id)

    # Aggregator (Phase 2 placeholder — concat instead of majority_vote)
    nodes.append(
        _response_aggregator_node(
            node_id="aggregator",
            title="Response Aggregator (S2P)",
            desc=(
                "Phase 2 placeholder: concat (paper specifies majority_vote; "
                "swap once Phase 3 lands per PAPER_REPRODUCTION_PLAN.md §4.1)."
            ),
            inputs=[(m.letter, [pid, "text"]) for m, pid in zip(parallel, parallel_ids)],
            strategy_name="concat",
            strategy_config={"include_source_label": True, "separator": "\n\n---\n\n"},
            x=942,
        )
    )
    for pid in parallel_ids:
        edges.append(
            _edge(src=pid, dst="aggregator", src_type="llm", dst_type="response-aggregator")
        )

    nodes.append(_end_node(["aggregator", "text"], x=1246))
    edges.append(
        _edge(src="aggregator", dst="end_node", src_type="response-aggregator", dst_type="end")
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
            f"{', '.join(m.description for m in parallel)}.\n\n"
            "⚠ Phase 2 fidelity gap: response-aggregator falls back to concat "
            "(paper specifies majority_vote at this junction). Regenerate "
            "after Phase 3 lands — see PAPER_REPRODUCTION_PLAN.md §4.1."
        ),
        nodes=nodes,
        edges=edges,
    )


def build_p2s(parallel: list[PaperModel], serial: PaperModel, provider: str) -> dict:
    """P2S: [parallel] → response-aggregator(concat) → serial."""
    nodes: list[dict] = [_start_node()]
    edges: list[dict] = []

    # Stage 1 — parallel branches off start
    parallel_ids: list[str] = []
    for i, m in enumerate(parallel):
        node_id = f"llm_{m.letter}_par"
        nodes.append(
            _llm_node(
                node_id=node_id,
                title=f"{m.letter} (parallel)",
                desc=f"P2S stage 1 — {m.description} answers in parallel.",
                model_name=m.model_name,
                provider=provider,
                system=SYS_LEAF,
                user=USR_LEAF,
                x=334,
                y=_stack_y(i, len(parallel)),
            )
        )
        edges.append(_edge(src="start_node", dst=node_id, src_type="start", dst_type="llm"))
        parallel_ids.append(node_id)

    # Aggregator — concat with source labels feeds the synthesizer
    nodes.append(
        _response_aggregator_node(
            node_id="aggregator",
            title="Response Aggregator (P2S)",
            desc="Concatenate stage-1 parallel answers; pipe to stage-2 model for synthesis.",
            inputs=[(m.letter, [pid, "text"]) for m, pid in zip(parallel, parallel_ids)],
            strategy_name="concat",
            strategy_config={"include_source_label": True, "separator": "\n\n---\n\n"},
            x=638,
        )
    )
    for pid in parallel_ids:
        edges.append(
            _edge(src=pid, dst="aggregator", src_type="llm", dst_type="response-aggregator")
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
        _edge(src="aggregator", dst=serial_id, src_type="response-aggregator", dst_type="llm")
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
            f"{serial.description} synthesizes."
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


def all_paths(provider: str) -> list[tuple[str, dict]]:
    """Enumerate the 13 paper paths used to reproduce paper Tables 6-7."""
    paths: list[tuple[str, dict]] = []

    # SI: 3! = 6 permutations
    for perm in permutations(PAPER_MODELS):
        letters = "".join(m.letter for m in perm)
        paths.append((f"paper_si_{letters}", build_si(list(perm), provider)))

    # PI: single 3-model PI
    paths.append(("paper_pi_QDY", build_pi(PAPER_MODELS)))

    # S2P: one path per serial choice (3 paths)
    for serial in PAPER_MODELS:
        parallel = [m for m in PAPER_MODELS if m is not serial]
        name = f"paper_s2p_{serial.letter}_{''.join(m.letter for m in parallel)}"
        paths.append((name, build_s2p(serial, parallel, provider)))

    # P2S: one path per serial choice (3 paths)
    for serial in PAPER_MODELS:
        parallel = [m for m in PAPER_MODELS if m is not serial]
        name = f"paper_p2s_{''.join(m.letter for m in parallel)}_{serial.letter}"
        paths.append((name, build_p2s(parallel, serial, provider)))

    return paths


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
    for name, dsl in all_paths(args.provider):
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
        written.append(str(path.relative_to(REPO_ROOT)))
    for p in written:
        print(f"wrote {p}")
    print(f"\nGenerated {len(written)} DSL files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
