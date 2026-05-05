#!/usr/bin/env python3
"""DuetNet paper reproduction harness — Wang et al. 2025.

Runs the DuetNet aggregator + the sum_score (≈ GaC) baseline against the
four datasets the paper benchmarks (SimpleMath, C-Eval, BoolQ, MMLU) by
hitting Dify's workflow run API with a deterministic prompt template per
dataset, then computes accuracy / per-question token count / per-token
latency in the form of paper Tables 4–5 / Fig. 7 / Fig. 11.

Single-model baselines and any other comparison method (Unite, GaC, DK,
DP) are configured the same way: register a workflow app per method in
Dify, then list its API key in the config under ``workflow_keys``. The
eval script does not care what is inside each workflow — it only sees
the API contract.

Usage::

    python dev/modelnet/duet_net_eval.py --config dev/modelnet/eval.yaml
    python dev/modelnet/duet_net_eval.py --config dev/modelnet/eval.yaml --resume

Config (YAML)::

    base_url: http://localhost:5001/v1
    user: eval-runner
    response_mode: blocking
    request_timeout_s: 600

    workflow_keys:
      # Combo → workflow API key (Dify console → app → API → API key).
      # Add any combo / baseline you want benchmarked.
      duet_net_q1_q2: app-XXXX
      duet_net_q2_g4: app-XXXX
      sum_score_q1_q2: app-XXXX     # GaC-equivalent baseline
      single_q2:        app-XXXX    # single-model baseline

    datasets:
      simple_math: { n: 50, seed: 42 }
      c_eval:      { n: 50 }
      bool_q:      { n: 50 }
      mmlu:        { n: 50 }

    checkpoint_path: dev/modelnet/eval_checkpoint.json
    report_path:     dev/modelnet/eval_report.json

Checkpointing is per-(workflow_key, dataset, item_index): re-running with
``--resume`` skips items already in the checkpoint and continues from
where the last run stopped.

Datasets are pulled once from HuggingFace via the ``datasets`` library
(SimpleMath is synthesised in-process). Set ``HF_HOME`` to control where
the cache lands.
"""

from __future__ import annotations

import argparse
import dataclasses
import json
import logging
import random
import re
import time
from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger("duet_net_eval")

# ── Datasets ────────────────────────────────────────────────────────────


@dataclass
class EvalItem:
    """One evaluation question, normalised across datasets."""

    item_id: str
    """Stable ID for checkpoint keys (e.g. "mmlu_high_school_chemistry_007")."""

    question: str
    """Prompt to feed into the workflow's ``question`` input."""

    answer: str
    """Ground-truth answer in extractor-comparable form
    (lowercase letter for MCQ, ``true``/``false`` for boolean,
    decimal string for math)."""

    extractor: str
    """Name of the extractor function — see ``EXTRACTORS`` mapping."""


def _simple_math(n: int, seed: int) -> Iterator[EvalItem]:
    """Synthesise ``a + b * c + d - e * f`` with 0–30 ints (paper §4.1)."""
    rng = random.Random(seed)
    for i in range(n):
        a, b, c, d, e, f_ = (rng.randint(0, 30) for _ in range(6))
        expr = f"{a}+{b}*{c}+{d}-{e}*{f_}"
        result = a + b * c + d - e * f_
        question = (
            f"What is the answer to {expr}? "
            "Please make sure to repeat the answer at the very end of your reply."
        )
        yield EvalItem(
            item_id=f"simple_math_{i:03d}",
            question=question,
            answer=str(result),
            extractor="last_integer",
        )


def _c_eval(n: int) -> Iterator[EvalItem]:
    """C-Eval (4-choice MCQ, Chinese)."""
    from datasets import load_dataset

    ds = load_dataset("ceval/ceval-exam", "computer_network", split="val")
    rng = random.Random(0)
    indices = rng.sample(range(len(ds)), min(n, len(ds)))
    for i in indices:
        row = ds[i]
        opts = "\n".join(f"{k}. {row[k]}" for k in ("A", "B", "C", "D"))
        question = (
            f"{row['question']}\n{opts}\n"
            "你必须在回答的最后重申你的答案（只写一个字母 A/B/C/D）。"
        )
        yield EvalItem(
            item_id=f"c_eval_cn_{i:04d}",
            question=question,
            answer=row["answer"].strip().upper(),
            extractor="last_abcd",
        )


def _bool_q(n: int) -> Iterator[EvalItem]:
    """BoolQ true/false."""
    from datasets import load_dataset

    ds = load_dataset("google/boolq", split="validation")
    rng = random.Random(0)
    indices = rng.sample(range(len(ds)), min(n, len(ds)))
    for i in indices:
        row = ds[i]
        question = (
            f"Read the following background: {row['passage']}\n"
            f"Based on the above background, please answer the True-false "
            f"question: {row['question']}\n"
            "If you think it is correct, answer (True), otherwise answer (False). "
            "You must reiterate your answer at the end of the response."
        )
        yield EvalItem(
            item_id=f"bool_q_{i:05d}",
            question=question,
            answer="true" if row["answer"] else "false",
            extractor="last_bool",
        )


def _mmlu(n: int) -> Iterator[EvalItem]:
    """MMLU (4-choice MCQ, broad domain)."""
    from datasets import load_dataset

    ds = load_dataset("cais/mmlu", "all", split="test")
    rng = random.Random(0)
    indices = rng.sample(range(len(ds)), min(n, len(ds)))
    letters = ["A", "B", "C", "D"]
    for i in indices:
        row = ds[i]
        opts = "\n".join(f"{letter}. {choice}" for letter, choice in zip(letters, row["choices"]))
        question = (
            f"Can you answer the following question as accurately as possible?\n"
            f"{row['question']}\n{opts}\n"
            "Explain your answer, putting the answer (i.e., A or B or C or D) "
            "in the form (X) at the end of your response."
        )
        yield EvalItem(
            item_id=f"mmlu_{i:05d}",
            question=question,
            answer=letters[int(row["answer"])],
            extractor="paren_abcd",
        )


DATASET_LOADERS: dict[str, Any] = {
    "simple_math": _simple_math,
    "c_eval": _c_eval,
    "bool_q": _bool_q,
    "mmlu": _mmlu,
}

# ── Answer extractors ────────────────────────────────────────────────────

_INT_RE = re.compile(r"-?\d+")
_ABCD_RE = re.compile(r"[A-D]")
_PAREN_ABCD_RE = re.compile(r"\(\s*([A-D])\s*\)")
_BOOL_RE = re.compile(r"\b(true|false)\b", re.IGNORECASE)


def _extract_last_integer(text: str) -> str:
    matches = _INT_RE.findall(text)
    return matches[-1] if matches else ""


def _extract_last_abcd(text: str) -> str:
    matches = _ABCD_RE.findall(text)
    return matches[-1].upper() if matches else ""


def _extract_paren_abcd(text: str) -> str:
    """MMLU template asks for ``(X)`` format; fall back to last A/B/C/D."""
    paren = _PAREN_ABCD_RE.findall(text)
    if paren:
        return paren[-1].upper()
    return _extract_last_abcd(text)


def _extract_last_bool(text: str) -> str:
    matches = _BOOL_RE.findall(text)
    return matches[-1].lower() if matches else ""


EXTRACTORS: dict[str, Any] = {
    "last_integer": _extract_last_integer,
    "last_abcd": _extract_last_abcd,
    "paren_abcd": _extract_paren_abcd,
    "last_bool": _extract_last_bool,
}

# ── Dify workflow client ─────────────────────────────────────────────────


@dataclass
class WorkflowResult:
    """Result of one workflow run, normalised across response modes."""

    answer: str
    elapsed_ms: int
    """Wall-clock latency the *client* observed; the server-side trace
    has finer-grained per-step times when ``include_response_timings``
    is on."""
    token_count: int
    """Approximate token count from ``metadata.usage.total_tokens`` if
    surfaced; ``0`` if the workflow did not expose it."""
    raw: dict
    """Full response payload, kept for ad-hoc diagnostics."""


class DifyWorkflowClient:
    """Thin wrapper over Dify's blocking ``/workflows/run`` endpoint."""

    def __init__(
        self,
        base_url: str,
        user: str,
        response_mode: str = "blocking",
        request_timeout_s: int = 600,
    ) -> None:
        # Imported here so the script can ``--help`` without ``requests``.
        import requests  # noqa: PLC0415  (deferred import is intentional)

        self._requests = requests
        self._base_url = base_url.rstrip("/")
        self._user = user
        self._response_mode = response_mode
        self._timeout = request_timeout_s

    def run(self, api_key: str, question: str) -> WorkflowResult:
        """POST one question, return the parsed answer + diagnostics."""
        url = f"{self._base_url}/workflows/run"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        body = {
            "inputs": {"question": question},
            "user": self._user,
            "response_mode": self._response_mode,
        }
        t0 = time.perf_counter()
        resp = self._requests.post(url, headers=headers, json=body, timeout=self._timeout)
        elapsed_ms = int((time.perf_counter() - t0) * 1000)
        resp.raise_for_status()
        payload = resp.json()
        data = payload.get("data") or {}
        outputs = data.get("outputs") or {}
        answer_text = outputs.get("answer") or outputs.get("text") or ""
        usage = (data.get("metadata") or {}).get("usage") or {}
        token_count = int(usage.get("total_tokens", 0) or 0)
        return WorkflowResult(
            answer=str(answer_text),
            elapsed_ms=elapsed_ms,
            token_count=token_count,
            raw=payload,
        )


# ── Eval driver ──────────────────────────────────────────────────────────


@dataclass
class EvalConfig:
    base_url: str
    user: str
    response_mode: str
    request_timeout_s: int
    workflow_keys: dict[str, str]
    datasets: dict[str, dict[str, Any]]
    checkpoint_path: Path
    report_path: Path

    @classmethod
    def load(cls, path: Path) -> EvalConfig:
        import yaml  # noqa: PLC0415

        with path.open("r", encoding="utf-8") as fh:
            raw = yaml.safe_load(fh)
        return cls(
            base_url=raw["base_url"],
            user=raw.get("user", "duet-net-eval"),
            response_mode=raw.get("response_mode", "blocking"),
            request_timeout_s=int(raw.get("request_timeout_s", 600)),
            workflow_keys=dict(raw["workflow_keys"]),
            datasets=dict(raw.get("datasets", {})),
            checkpoint_path=Path(raw.get("checkpoint_path", "eval_checkpoint.json")),
            report_path=Path(raw.get("report_path", "eval_report.json")),
        )


@dataclass
class ItemRecord:
    workflow: str
    dataset: str
    item_id: str
    expected: str
    predicted: str
    correct: bool
    elapsed_ms: int
    token_count: int

    def key(self) -> str:
        return f"{self.workflow}|{self.dataset}|{self.item_id}"


@dataclass
class Checkpoint:
    """Records keyed by ``workflow|dataset|item_id``."""

    records: dict[str, dict] = field(default_factory=dict)

    @classmethod
    def load(cls, path: Path) -> Checkpoint:
        if not path.exists():
            return cls()
        with path.open("r", encoding="utf-8") as fh:
            return cls(records=json.load(fh))

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as fh:
            json.dump(self.records, fh, ensure_ascii=False, indent=2)

    def has(self, key: str) -> bool:
        return key in self.records

    def add(self, rec: ItemRecord) -> None:
        self.records[rec.key()] = dataclasses.asdict(rec)


def _items_for_dataset(name: str, dcfg: dict[str, Any]) -> Iterator[EvalItem]:
    loader = DATASET_LOADERS.get(name)
    if loader is None:
        raise KeyError(f"unknown dataset {name!r}; known: {sorted(DATASET_LOADERS)}")
    if name == "simple_math":
        yield from loader(n=int(dcfg.get("n", 50)), seed=int(dcfg.get("seed", 42)))
    else:
        yield from loader(n=int(dcfg.get("n", 50)))


def evaluate(cfg: EvalConfig, *, resume: bool, every: int = 10) -> list[ItemRecord]:
    client = DifyWorkflowClient(
        base_url=cfg.base_url,
        user=cfg.user,
        response_mode=cfg.response_mode,
        request_timeout_s=cfg.request_timeout_s,
    )
    checkpoint = Checkpoint.load(cfg.checkpoint_path) if resume else Checkpoint()
    records: list[ItemRecord] = [
        ItemRecord(**rec) for rec in checkpoint.records.values()
    ]

    progress_since_save = 0
    for workflow, api_key in cfg.workflow_keys.items():
        for dataset_name, dcfg in cfg.datasets.items():
            logger.info("== %s × %s ==", workflow, dataset_name)
            for item in _items_for_dataset(dataset_name, dcfg):
                rec_key = f"{workflow}|{dataset_name}|{item.item_id}"
                if checkpoint.has(rec_key):
                    continue
                try:
                    result = client.run(api_key, item.question)
                except Exception as exc:  # noqa: BLE001 - surface every error in trace
                    logger.warning("%s: %s", rec_key, exc)
                    rec = ItemRecord(
                        workflow=workflow,
                        dataset=dataset_name,
                        item_id=item.item_id,
                        expected=item.answer,
                        predicted="",
                        correct=False,
                        elapsed_ms=0,
                        token_count=0,
                    )
                else:
                    extractor = EXTRACTORS[item.extractor]
                    predicted = extractor(result.answer)
                    correct = _matches(predicted, item.answer, item.extractor)
                    rec = ItemRecord(
                        workflow=workflow,
                        dataset=dataset_name,
                        item_id=item.item_id,
                        expected=item.answer,
                        predicted=predicted,
                        correct=correct,
                        elapsed_ms=result.elapsed_ms,
                        token_count=result.token_count,
                    )
                records.append(rec)
                checkpoint.add(rec)
                progress_since_save += 1
                if progress_since_save >= every:
                    checkpoint.save(cfg.checkpoint_path)
                    progress_since_save = 0
    if progress_since_save:
        checkpoint.save(cfg.checkpoint_path)
    return records


def _matches(predicted: str, expected: str, extractor: str) -> bool:
    if not predicted:
        return False
    if extractor == "last_integer":
        try:
            return int(predicted) == int(expected)
        except ValueError:
            return False
    if extractor in {"last_abcd", "paren_abcd"}:
        return predicted.upper() == expected.upper()
    if extractor == "last_bool":
        return predicted.lower() == expected.lower()
    return predicted == expected


# ── Reporting ────────────────────────────────────────────────────────────


def _summarise(records: list[ItemRecord]) -> dict:
    """Group records by (workflow, dataset) → accuracy / latency / tokens."""
    buckets: dict[tuple[str, str], list[ItemRecord]] = {}
    for r in records:
        buckets.setdefault((r.workflow, r.dataset), []).append(r)
    summary: dict[str, dict[str, dict[str, float]]] = {}
    for (wf, ds), group in buckets.items():
        accuracy = sum(1 for r in group if r.correct) / len(group)
        avg_ms = sum(r.elapsed_ms for r in group) / len(group)
        avg_tokens = sum(r.token_count for r in group) / len(group)
        summary.setdefault(wf, {})[ds] = {
            "n": len(group),
            "accuracy": round(accuracy * 100, 2),
            "avg_elapsed_ms": round(avg_ms, 1),
            "avg_token_count": round(avg_tokens, 1),
        }
    # Add a "mean" row across datasets per workflow.
    for wf, by_ds in summary.items():
        accs = [v["accuracy"] for v in by_ds.values()]
        toks = [v["avg_token_count"] for v in by_ds.values()]
        lats = [v["avg_elapsed_ms"] for v in by_ds.values()]
        if accs:
            by_ds["__mean__"] = {
                "n": sum(v["n"] for v in by_ds.values()),
                "accuracy": round(sum(accs) / len(accs), 2),
                "avg_elapsed_ms": round(sum(lats) / len(lats), 1),
                "avg_token_count": round(sum(toks) / len(toks), 1),
            }
    return summary


def _print_table(summary: dict) -> None:
    workflows = sorted(summary)
    datasets = sorted({ds for wf in summary.values() for ds in wf})
    if "__mean__" in datasets:
        datasets.remove("__mean__")
        datasets.append("__mean__")
    col_w = max(8, max((len(w) for w in workflows), default=8))
    header = "workflow".ljust(col_w) + " | " + " | ".join(d.rjust(10) for d in datasets)
    print(header)
    print("-" * len(header))
    for wf in workflows:
        row = wf.ljust(col_w)
        for ds in datasets:
            acc = summary[wf].get(ds, {}).get("accuracy")
            row += " | " + (f"{acc:>10.2f}" if acc is not None else " " * 10)
        print(row)


# ── Entry point ──────────────────────────────────────────────────────────


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True, help="path to eval.yaml")
    parser.add_argument("--resume", action="store_true", help="skip items in checkpoint")
    parser.add_argument(
        "--checkpoint-every",
        type=int,
        default=10,
        help="flush checkpoint every N items (default: 10)",
    )
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.WARNING if args.quiet else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    cfg = EvalConfig.load(args.config)
    records = evaluate(cfg, resume=args.resume, every=args.checkpoint_every)
    summary = _summarise(records)

    cfg.report_path.parent.mkdir(parents=True, exist_ok=True)
    with cfg.report_path.open("w", encoding="utf-8") as fh:
        json.dump(
            {
                "summary": summary,
                "records": [dataclasses.asdict(r) for r in records],
            },
            fh,
            ensure_ascii=False,
            indent=2,
        )

    print()
    print("=== Accuracy (%) ===")
    _print_table(summary)
    print()
    print(f"Full report: {cfg.report_path}")
    print(f"Checkpoint:  {cfg.checkpoint_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
