#!/usr/bin/env python3
"""Generate DuetNet workflow DSL examples from a template.

Produces 8 DSLs in ``docs/ModelNet/examples/workflow_mode/``:

    duet_net_<combo>.yml

where ``<combo>`` is one of the 6 dual-model pairs from the paper
(Tables 4-5) plus one 3-model and one 4-model variant. Each emitted
DSL is a deterministic transformation of the canonical 2-model
``duet_net_q1q2.yml`` template — only the per-source nodes and the
``token_sources`` list change; the runner/aggregator config and the
End wiring are constant.

Run:

    python dev/modelnet/generate_duet_net_dsls.py

Idempotent — overwrites existing files. Aliases must already be
declared in ``api/configs/model_net.yaml`` with
``expose_raw_logits: true``; otherwise ``duet_net`` will refuse to
aggregate at the first decode step (CapabilityNotSupportedError).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
EXAMPLES_DIR = REPO_ROOT / "docs" / "ModelNet" / "examples" / "workflow_mode"

# Paper's four self-hosted models (Table 1).
ALIAS_DESCRIPTIONS: dict[str, str] = {
    "q1": "Qwen1.5-7B-Chat",
    "q2": "Qwen2.5-7B-Instruct",
    "g4": "GLM-4-9B-Chat",
    "L3": "Meta-Llama-3.1-8B-Instruct",
}

# Combinations from the paper:
#  - 6 dual-model rows of Tables 4 / 5
#  - one 3-model (Table 7's q1&q2&g4)
#  - one 4-model (Table 7's q1&q2&g4&L3)
COMBOS: list[tuple[str, ...]] = [
    ("q1", "q2"),
    ("q1", "g4"),
    ("q1", "L3"),
    ("q2", "g4"),
    ("q2", "L3"),
    ("g4", "L3"),
    ("q1", "q2", "g4"),
    ("q1", "q2", "g4", "L3"),
]


def _node_y(index: int, total: int) -> int:
    """Stack token-source nodes vertically, centred on y=252."""
    spacing = 152
    top = 252 - (total - 1) * spacing // 2
    return top + index * spacing


def _start_to_source_edges(aliases: tuple[str, ...]) -> list[dict]:
    return [
        {
            "id": f"start-to-{a}",
            "source": "start_node",
            "sourceHandle": "source",
            "target": f"{a}_source",
            "targetHandle": "target",
            "type": "custom",
            "zIndex": 0,
            "data": {
                "isInIteration": False,
                "isInLoop": False,
                "sourceType": "start",
                "targetType": "token-model-source",
            },
        }
        for a in aliases
    ]


def _source_to_ensemble_edges(aliases: tuple[str, ...]) -> list[dict]:
    return [
        {
            "id": f"{a}-to-ensemble",
            "source": f"{a}_source",
            "sourceHandle": "source",
            "target": "ensemble",
            "targetHandle": "target",
            "type": "custom",
            "zIndex": 0,
            "data": {
                "isInIteration": False,
                "isInLoop": False,
                "sourceType": "token-model-source",
                "targetType": "parallel-ensemble",
            },
        }
        for a in aliases
    ]


def _ensemble_to_end_edge() -> dict:
    return {
        "id": "ensemble-to-end",
        "source": "ensemble",
        "sourceHandle": "source",
        "target": "end_node",
        "targetHandle": "target",
        "type": "custom",
        "zIndex": 0,
        "data": {
            "isInIteration": False,
            "isInLoop": False,
            "sourceType": "parallel-ensemble",
            "targetType": "end",
        },
    }


def _start_node() -> dict:
    return {
        "id": "start_node",
        "type": "custom",
        "data": {
            "desc": "User question routed to all parallel token sources.",
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
        "position": {"x": 30, "y": 252},
        "positionAbsolute": {"x": 30, "y": 252},
        "selected": False,
        "sourcePosition": "right",
        "targetPosition": "left",
        "width": 244,
    }


def _token_source_node(alias: str, y: int) -> dict:
    desc = (
        f"Renders the prompt for {alias} ({ALIAS_DESCRIPTIONS[alias]}) — yields a "
        "ModelInvocationSpec; does NOT call the model directly."
    )
    return {
        "id": f"{alias}_source",
        "type": "custom",
        "data": {
            "desc": desc,
            "extra": {},
            "model_alias": alias,
            "prompt_template": "{{#start_node.question#}}",
            "sampling_params": {
                "max_tokens": 1024,
                "temperature": 0.7,
                "top_k": 10,
            },
            "selected": False,
            "title": f"Token Source ({alias})",
            "type": "token-model-source",
        },
        "height": 130,
        "position": {"x": 334, "y": y},
        "positionAbsolute": {"x": 334, "y": y},
        "selected": False,
        "sourcePosition": "right",
        "targetPosition": "left",
        "width": 244,
    }


def _ensemble_node(aliases: tuple[str, ...]) -> dict:
    token_sources = [
        {
            "source_id": a,
            "spec_selector": [f"{a}_source", "spec"],
            "weight": 1.0,
        }
        for a in aliases
    ]
    return {
        "id": "ensemble",
        "type": "custom",
        "data": {
            "desc": (
                "DuetNet token aggregator — joint τ_K/τ_P truncation, "
                "raw-logit sum across the union, Top-T sampling."
            ),
            "ensemble": {
                "aggregator_config": {
                    "seed": None,
                    "tau_k": 10,
                    "tau_p": 0.75,
                    "top_t": 1,
                    "use_weights": False,
                },
                "aggregator_name": "duet_net",
                "diagnostics": {
                    "include_aggregator_reasoning": True,
                    "include_per_backend_errors": True,
                    "include_response_timings": True,
                    "include_token_candidates": True,
                    "max_trace_tokens": 2000,
                    "storage": "metadata",
                },
                "runner_config": {
                    "enable_think": False,
                    "max_len": 512,
                },
                "runner_name": "token_step",
                "token_sources": token_sources,
            },
            "selected": False,
            "title": "Parallel Ensemble (DuetNet)",
            "type": "parallel-ensemble",
        },
        "height": 200,
        "position": {"x": 638, "y": 252},
        "positionAbsolute": {"x": 638, "y": 252},
        "selected": False,
        "sourcePosition": "right",
        "targetPosition": "left",
        "width": 244,
    }


def _end_node() -> dict:
    return {
        "id": "end_node",
        "type": "custom",
        "data": {
            "desc": "Emit the joint-decoded answer.",
            "outputs": [
                {
                    "value_selector": ["ensemble", "text"],
                    "value_type": "string",
                    "variable": "answer",
                },
                {
                    "value_selector": ["ensemble", "metadata"],
                    "value_type": "object",
                    "variable": "metadata",
                },
            ],
            "selected": False,
            "title": "End",
            "type": "end",
        },
        "height": 116,
        "position": {"x": 942, "y": 252},
        "positionAbsolute": {"x": 942, "y": 252},
        "selected": False,
        "sourcePosition": "right",
        "targetPosition": "left",
        "width": 244,
    }


def build_dsl(aliases: tuple[str, ...]) -> dict:
    combo_label = "&".join(aliases)
    pretty = ", ".join(f"{a} ({ALIAS_DESCRIPTIONS[a]})" for a in aliases)
    description = (
        f"DuetNet (Wang et al., 2025) reproduction — {len(aliases)} models "
        f"({combo_label}).\n\n"
        f"Token sources: {pretty}.\n\n"
        "Each token-model-source node renders the prompt; the parallel-ensemble "
        "node drives token_step runner + duet_net aggregator with paper defaults "
        "(τ_K=10, τ_P=0.75, T=1). Every spec must declare LOGITS_RAW (set "
        "expose_raw_logits: true on the matching alias in "
        "api/configs/model_net.yaml). Vary aggregator_config to reproduce "
        "the parameter sweeps from paper Figs. 12-13."
    )
    nodes = [_start_node()]
    n = len(aliases)
    for i, a in enumerate(aliases):
        nodes.append(_token_source_node(a, _node_y(i, n)))
    nodes.append(_ensemble_node(aliases))
    nodes.append(_end_node())
    edges = (
        _start_to_source_edges(aliases)
        + _source_to_ensemble_edges(aliases)
        + [_ensemble_to_end_edge()]
    )
    return {
        "app": {
            "description": description,
            "icon": "🎵",
            "icon_background": "#DCE5FF",
            "mode": "workflow",
            "name": f"duet_net_{'_'.join(aliases)} (workflow)",
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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out-dir",
        default=str(EXAMPLES_DIR),
        help=f"output directory (default: {EXAMPLES_DIR})",
    )
    args = parser.parse_args()

    try:
        import yaml
    except ImportError:  # pragma: no cover - requirement check, not test path
        print(
            "PyYAML required: pip install pyyaml (only needed for the generator)",
            file=sys.stderr,
        )
        return 1

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[str] = []
    for combo in COMBOS:
        dsl = build_dsl(combo)
        fname = f"duet_net_{'_'.join(combo)}.yml"
        path = out_dir / fname
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
