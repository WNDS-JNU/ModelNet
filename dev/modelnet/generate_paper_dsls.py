#!/usr/bin/env python3
"""Generate AI-ModelNet paper-reproduction workflow DSLs.

Emits one AI-ModelNet hybrid router workflow-mode DSL. The router selects
among the 6 S2P / P2S token-level fusion paths at runtime via a required
``path`` input. The paper-model roles are {Q=Qwen2.5-7B,
D=Qwen3-8B thinking-model substitute, Y=GLM-4-9B-Chat}. The file is written to
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
   present. Alias ``22`` is the current reachable D-role substitute because
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
D = PaperModel("D", "22", "qwen3-8b-bf16", "Qwen3-8B-BF16（D 角色替代模型）")
Y = PaperModel("Y", "6", "glm-4-9b-chat-q4k", "GLM-4-9B-Chat")

PAPER_MODELS: list[PaperModel] = [Q, D, Y]


# ── Prompt templates ─────────────────────────────────────────────────
#
# Approximation of paper Table 2: each model is asked to reason and
# produce a final answer; serial steps see the prior step's reply for
# refinement; the synthesis model sees the token-level parallel answer.

SYS_LEAF = "你是严谨的问题求解助手。请阅读问题，逐步推理，并在回答末尾给出最终答案。"
SYS_REFINE = (
    "你是严谨的问题求解助手。已有一个模型给出了候选答案。请阅读问题和候选答案，"
    "判断是否需要保留或修正，然后给出你自己的最终答案。"
)
SYS_SYNTHESIZE = (
    "你是严谨的问题求解助手。请阅读问题和 token 级并行融合得到的候选答案，"
    "核验后给出统一的最终答案。"
)

USR_LEAF = "{{#start_node.question#}}"
_USR_REFINE_TPL = (
    "问题：\n{{{{#start_node.question#}}}}\n\n"
    "上一阶段模型给出的候选答案：\n{{{{#{prev_node}.text#}}}}\n\n"
    "请给出你自己的最终答案："
)
_USR_SYNTHESIZE_TPL = (
    "问题：\n{{{{#start_node.question#}}}}\n\n"
    "token 级并行融合得到的候选答案：\n{{{{#{aggregator}.text#}}}}\n\n"
    "请给出核验后的统一最终答案："
)

_USR_S2P_PARALLEL_TPL = (
    "问题：\n{{{{#start_node.question#}}}}\n\n"
    "第一阶段语义草稿：\n{{{{#{serial_node}.text#}}}}\n\n"
    "请基于该草稿继续推理或修正，并在回答末尾给出最终答案。"
)


PATH_LABELS = {
    "paper_s2p_Q_DY": "S2P：Q 串行 → [D, Y] 并行",
    "paper_s2p_D_QY": "S2P：D 串行 → [Q, Y] 并行",
    "paper_s2p_Y_QD": "S2P：Y 串行 → [Q, D] 并行",
    "paper_p2s_QD_Y": "P2S：[Q, D] 并行 → Y 综合",
    "paper_p2s_QY_D": "P2S：[Q, Y] 并行 → D 综合",
    "paper_p2s_DY_Q": "P2S：[D, Y] 并行 → Q 综合",
}


def _path_label(path_name: str) -> str:
    return PATH_LABELS.get(path_name, path_name)


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
                "label": "实验路径（使用下方 ID）",
                "max_length": 128,
                "options": path_options,
                "required": True,
                "type": "select",
                "variable": "path",
            }
        )
    variables.append(
        {
            "label": "问题",
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
            "desc": "选择实验路径并输入待推理问题。",
            "selected": False,
            "title": "开始",
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
    title: str = "结束",
    desc: str = "输出该路径的最终答案。",
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
                or f"为 {model.title} 渲染提示词，使用 alias {model.model_alias}，"
                "并输出 ModelInvocationSpec。"
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
            "title": title or f"Token Source（{model.letter}）",
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
    title: str = "并行融合",
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
                or "token 级并行融合，使用 sum_score 聚合器；每个解码步在各后端 "
                "top-k 候选 token 的并集上做概率求和投票。"
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
            "desc": "根据 path 输入选择一个 S2P/P2S 混合推理分支。",
            "_targetBranches": [{"id": name, "name": _path_label(name)} for name in path_names],
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
            "title": "路由：实验路径",
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
    path_label = _path_label(path_name)
    nodes.append(
        _llm_node(
            node_id=serial_id,
            title=f"{path_label}：{serial.letter} 串行草稿",
            desc=f"{path_label} 第一阶段：由 {serial.description} 生成语义草稿。",
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
                title=f"{path_label}：{m.letter} 并行源",
                desc=(
                    f"{path_label} 并行源：{m.description} 接收第一阶段语义草稿，"
                    "参与 token 级融合。"
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
            title=f"{path_label}：token 级并行融合",
            desc=f"{path_label} 的 S2P 第二阶段，使用 sum_score 做 token 级并行融合。",
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
            title=f"结束：{path_label}",
            desc=f"输出 {path_label} 的最终答案。",
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
    path_label = _path_label(path_name)
    for i, m in enumerate(parallel):
        node_id = f"{path_name}__token_{m.letter}_par"
        nodes.append(
            _token_source_node(
                model=m,
                x=638,
                y=base_y + i * 152,
                node_id=node_id,
                title=f"{path_label}：{m.letter} 并行源",
                desc=f"{path_label} 并行源：{m.description} 参与 token 级融合。",
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
            title=f"{path_label}：token 级并行融合",
            desc=f"{path_label} 的 P2S 第一阶段，使用 sum_score 做 token 级并行融合。",
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
            title=f"{path_label}：{serial.letter} 串行综合",
            desc=f"{path_label} 第二阶段：由 {serial.description} 综合融合后的中间答案。",
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
            title=f"结束：{path_label}",
            desc=f"输出 {path_label} 的最终答案。",
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
        name="AI-ModelNet 混合路径总入口 (workflow)",
        desc=(
            "AI-ModelNet 混合推理总入口。必填输入 `path` 选择六条 S2P/P2S "
            "token 级融合路径之一，`question` 会被路由到对应分支。"
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

    class _DslDumper(yaml.SafeDumper):
        pass

    def _str_representer(dumper: yaml.SafeDumper, value: str):
        style = "|" if "\n" in value else None
        return dumper.represent_scalar("tag:yaml.org,2002:str", value, style=style)

    _DslDumper.add_representer(str, _str_representer)

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
            yaml.dump(
                dsl,
                fh,
                Dumper=_DslDumper,
                allow_unicode=True,
                sort_keys=False,
                width=100,
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
