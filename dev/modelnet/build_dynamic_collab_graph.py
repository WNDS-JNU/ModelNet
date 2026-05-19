#!/usr/bin/env python3
"""Build a collaboration graph for dynamic collaborative routing.

The script implements the paper's offline mutual-evaluation stage over the
current ModelNet backend registry. It intentionally produces a plain JSON
artifact that can be pasted into ``dynamic_collab_route.runner_config`` as
``collaboration_graph_json``.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
API_ROOT = REPO_ROOT / "api"
if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))

from core.helper.ssrf_proxy import graphon_ssrf_proxy  # noqa: E402
from core.workflow.nodes.parallel_ensemble import backends as _backends  # noqa: E402,F401
from core.workflow.nodes.parallel_ensemble.registry import BackendRegistry  # noqa: E402
from core.workflow.nodes.parallel_ensemble.registry.model_registry import ModelRegistry  # noqa: E402
from core.workflow.nodes.parallel_ensemble.spi.backend import GenerationParams, ModelBackend  # noqa: E402


ANSWER_PROMPT_TEMPLATE = "{question}"
EVAL_PROMPT_TEMPLATE = (
    "这是任务: {question} , 这是某个模型有关分类及其解释的回答: {answer} . "
    "它的回答可能不正确, 但请你作为一个通用领域的专家, 在目前有A, B, C三个评分等级的情况下, "
    "为这个回答评级. 请你仅回答等级, 而不输出其他任何信息."
)


@dataclass(frozen=True)
class Source:
    source_id: str
    alias: str


def _parse_source(raw: str) -> Source:
    if "=" in raw:
        source_id, alias = raw.split("=", 1)
        source_id = source_id.strip()
        alias = alias.strip()
    else:
        source_id = raw.strip()
        alias = source_id
    if not source_id or not alias:
        raise argparse.ArgumentTypeError("sources must be ALIAS or SOURCE_ID=ALIAS")
    return Source(source_id=source_id, alias=alias)


def _load_questions(path: Path, limit: int | None) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    with path.open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            if limit is not None and len(items) >= limit:
                break
            stripped = line.strip()
            if not stripped:
                continue
            payload = json.loads(stripped)
            if not isinstance(payload, dict) or not isinstance(payload.get("question"), str):
                raise ValueError(f"{path}:{line_no} must be a JSON object with a string 'question'")
            item_id = payload.get("id")
            items.append(
                {
                    "id": str(item_id) if item_id is not None else f"item_{line_no}",
                    "question": payload["question"],
                }
            )
    if not items:
        raise ValueError(f"{path} did not contain any questions")
    return items


def _make_backends(sources: list[Source], registry_path: str | None) -> dict[str, ModelBackend]:
    registry = ModelRegistry.for_testing(registry_path) if registry_path else ModelRegistry.instance()
    out: dict[str, ModelBackend] = {}
    for source in sources:
        spec = registry.get(source.alias)
        backend_cls = BackendRegistry.get(spec.backend)
        out[source.source_id] = backend_cls(spec, http=graphon_ssrf_proxy)
    return out


def _call_model(
    backend: ModelBackend,
    prompt: str,
    *,
    max_tokens: int,
    temperature: float,
) -> str:
    params: GenerationParams = {
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    result = backend.generate(prompt, params)
    return result.get("text", "").strip()


def _parse_grade(raw: str, grades: list[str]) -> str:
    normalized = raw.strip().upper()
    for grade in grades:
        if grade.upper() in normalized:
            return grade
    return grades[-1]


def _score_grade(grade: str, grades: list[str]) -> int:
    return len(grades) - grades.index(grade)


def _percentile_flags(values: dict[str, float], d1: float) -> tuple[set[str], set[str]]:
    if not values:
        return set(), set()
    ordered = sorted(values.items(), key=lambda item: item[1], reverse=True)
    high_count = max(1, round(len(ordered) * d1 / 100.0))
    high = {source_id for source_id, _ in ordered[:high_count]}
    low = set(values) - high
    return high, low


def _low_scorers_for_target(pair_scores: dict[str, dict[str, list[int]]], target: str, d2: float) -> set[str]:
    averages: dict[str, float] = {}
    for judge_id, by_target in pair_scores.items():
        values = by_target.get(target, [])
        if values:
            averages[judge_id] = statistics.fmean(values)
    if not averages:
        return set()
    ordered = sorted(averages.items(), key=lambda item: item[1])
    count = max(1, round(len(ordered) * d2 / 100.0))
    return {source_id for source_id, _ in ordered[:count]}


def build_graph(
    *,
    backends: dict[str, ModelBackend],
    questions: list[dict[str, str]],
    grades: list[str],
    d1: float,
    d2: float,
    answer_max_tokens: int,
    eval_max_tokens: int,
    temperature: float,
) -> dict[str, Any]:
    answers: dict[str, dict[str, str]] = {sid: {} for sid in backends}
    for item in questions:
        for source_id, backend in backends.items():
            prompt = ANSWER_PROMPT_TEMPLATE.format(question=item["question"])
            answers[source_id][item["id"]] = _call_model(
                backend,
                prompt,
                max_tokens=answer_max_tokens,
                temperature=temperature,
            )

    pair_scores: dict[str, dict[str, list[int]]] = {
        judge_id: {target_id: [] for target_id in backends if target_id != judge_id}
        for judge_id in backends
    }
    raw_grades: list[dict[str, str]] = []
    for item in questions:
        for target_id, by_item in answers.items():
            answer = by_item[item["id"]]
            for judge_id, backend in backends.items():
                if judge_id == target_id:
                    continue
                prompt = EVAL_PROMPT_TEMPLATE.format(question=item["question"], answer=answer)
                raw = _call_model(
                    backend,
                    prompt,
                    max_tokens=eval_max_tokens,
                    temperature=0.0,
                )
                grade = _parse_grade(raw, grades)
                pair_scores[judge_id][target_id].append(_score_grade(grade, grades))
                raw_grades.append(
                    {
                        "item_id": item["id"],
                        "judge_source_id": judge_id,
                        "target_source_id": target_id,
                        "raw": raw,
                        "grade": grade,
                    }
                )

    given_scores = {
        judge_id: statistics.fmean(score for values in by_target.values() for score in values)
        for judge_id, by_target in pair_scores.items()
    }
    received_scores: dict[str, float] = {}
    for target_id in backends:
        values: list[int] = []
        for judge_id, by_target in pair_scores.items():
            if judge_id != target_id:
                values.extend(by_target.get(target_id, []))
        received_scores[target_id] = statistics.fmean(values) if values else 0.0

    high_given, low_given = _percentile_flags(given_scores, d1)
    high_received, low_received = _percentile_flags(received_scores, d1)

    states: dict[str, str] = {}
    for source_id in backends:
        if source_id in low_given and source_id in high_received:
            states[source_id] = "low_given_high_received"
        elif source_id in high_given and source_id in high_received:
            states[source_id] = "high_given_high_received"
        elif source_id in high_given and source_id in low_received:
            states[source_id] = "high_given_low_received"
        else:
            states[source_id] = "low_given_low_received"

    collaboration_graph: dict[str, list[str]] = {}
    supplemental_graph: dict[str, list[str]] = {}
    for target_id in backends:
        low_scorers = _low_scorers_for_target(pair_scores, target_id, d2)
        collaboration_graph[target_id] = sorted(
            source_id
            for source_id in low_scorers
            if states[source_id] == "low_given_high_received"
        )
        supplemental_graph[target_id] = sorted(
            source_id
            for source_id in low_scorers
            if states[source_id] == "low_given_low_received"
        )

    return {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "params": {
            "grades": grades,
            "d1": d1,
            "d2": d2,
            "answer_max_tokens": answer_max_tokens,
            "eval_max_tokens": eval_max_tokens,
            "temperature": temperature,
        },
        "given_scores": given_scores,
        "received_scores": received_scores,
        "states": states,
        "pair_scores": pair_scores,
        "collaboration_graph": collaboration_graph,
        "supplemental_graph": supplemental_graph,
        "raw_grades": raw_grades,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tasks", required=True, type=Path, help="JSONL with at least a 'question' field")
    parser.add_argument("--sources", required=True, nargs="+", type=_parse_source, help="ALIAS or SOURCE_ID=ALIAS")
    parser.add_argument("--output", type=Path, default=Path("dev/modelnet/dynamic_collab_graph.json"))
    parser.add_argument("--registry-path", default=None)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--grades", default="A,B,C")
    parser.add_argument("--d1", type=float, default=50.0)
    parser.add_argument("--d2", type=float, default=50.0)
    parser.add_argument("--answer-max-tokens", type=int, default=512)
    parser.add_argument("--eval-max-tokens", type=int, default=8)
    parser.add_argument("--temperature", type=float, default=0.0)
    args = parser.parse_args()

    grades = [part.strip().upper() for part in args.grades.split(",") if part.strip()]
    if len(grades) < 2:
        raise SystemExit("--grades must contain at least two ordered grade labels")
    if len(args.sources) < 2:
        raise SystemExit("--sources must contain at least two entries for pairwise mutual evaluation")
    source_ids = [source.source_id for source in args.sources]
    if len(set(source_ids)) != len(source_ids):
        raise SystemExit(f"--sources source_id values must be unique, got {source_ids!r}")

    questions = _load_questions(args.tasks, args.limit)
    backends = _make_backends(args.sources, args.registry_path)
    result = build_graph(
        backends=backends,
        questions=questions,
        grades=grades,
        d1=args.d1,
        d2=args.d2,
        answer_max_tokens=args.answer_max_tokens,
        eval_max_tokens=args.eval_max_tokens,
        temperature=args.temperature,
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    runner_graph = {
        "collaboration_graph": result["collaboration_graph"],
        "supplemental_graph": result["supplemental_graph"],
    }
    print(json.dumps(runner_graph, ensure_ascii=False))
    print(f"wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
