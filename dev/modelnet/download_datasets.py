"""Download C-Eval and BoolQ from HuggingFace and export to JSONL.

Output files are compatible with Dify's ``jsonl_file`` Data Loader node.
Each JSONL line is a JSON object with ``id``, ``question``, ``answer`` keys,
plus dataset-specific metadata.

Usage::

    # Default: export all subjects, 50 samples per dataset
    uv run --project api python dev/modelnet/download_datasets.py

    # Custom output dir and sample count
    uv run --project api python dev/modelnet/download_datasets.py \
        --output-dir dev/modelnet/datasets \
        --n 100

    # Only C-Eval, specific subjects
    uv run --project api python dev/modelnet/download_datasets.py \
        --datasets c_eval \
        --subjects computer_network mathematics
"""

from __future__ import annotations

import argparse
import json
import logging
import random
import sys
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

_C_EVAL_DEFAULT_SUBJECTS = [
    "computer_network",
    "advanced_mathematics",
    "high_school_history",
    "basic_medicine",
    "business_administration",
]


def download_ceval(
    output_dir: Path,
    n: int,
    seed: int,
    subjects: list[str] | None,
) -> Path:
    from datasets import load_dataset

    chosen = subjects or _C_EVAL_DEFAULT_SUBJECTS
    rng = random.Random(seed)
    pool: list[tuple[str, dict]] = []

    logger.info("C-Eval: downloading subjects %s ...", chosen)
    for subject in chosen:
        ds = load_dataset("ceval/ceval-exam", subject, split="val")
        for idx in range(len(ds)):
            pool.append((f"{subject}_{idx:04d}", ds[idx]))

    rng.shuffle(pool)
    selected = pool[: min(n, len(pool))]

    out_path = output_dir / "c_eval.jsonl"
    count = 0
    with out_path.open("w", encoding="utf-8") as f:
        for tag, row in selected:
            opts = "\n".join(f"{k}. {row[k]}" for k in ("A", "B", "C", "D"))
            question = (
                f"{row['question']}\n{opts}\n"
                "你必须在回答的最后重申你的答案（只写一个字母 A/B/C/D）。"
            )
            record = {
                "id": f"c_eval_{tag}",
                "question": question,
                "answer": row["answer"].strip().upper(),
                "subject": tag.split("_")[0],
                "extractor": "last_abcd",
            }
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
            count += 1

    logger.info("C-Eval: wrote %d items -> %s", count, out_path)
    return out_path


def download_boolq(
    output_dir: Path,
    n: int,
    seed: int,
) -> Path:
    from datasets import load_dataset

    logger.info("BoolQ: downloading ...")
    ds = load_dataset("google/boolq", split="validation")
    rng = random.Random(seed)
    indices = rng.sample(range(len(ds)), min(n, len(ds)))

    out_path = output_dir / "bool_q.jsonl"
    count = 0
    with out_path.open("w", encoding="utf-8") as f:
        for i in indices:
            row = ds[i]
            question = (
                f"Read the following background: {row['passage']}\n"
                f"Based on the above background, please answer the True-false "
                f"question: {row['question']}\n"
                "If you think it is correct, answer (True), otherwise answer (False). "
                "You must reiterate your answer at the end of the response."
            )
            record = {
                "id": f"bool_q_{i:05d}",
                "question": question,
                "answer": "true" if row["answer"] else "false",
                "extractor": "last_bool",
            }
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
            count += 1

    logger.info("BoolQ: wrote %d items -> %s", count, out_path)
    return out_path


DATASET_BUILDERS = {
    "c_eval": download_ceval,
    "bool_q": download_boolq,
}


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Download benchmark datasets and export to JSONL for Dify Data Loader.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("dev/modelnet/datasets"),
        help="Directory to write JSONL files (default: dev/modelnet/datasets).",
    )
    parser.add_argument(
        "--n",
        type=int,
        default=50,
        help="Number of samples per dataset (default: 50). Use -1 for all.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for shuffling/sampling (default: 42).",
    )
    parser.add_argument(
        "--datasets",
        nargs="+",
        choices=list(DATASET_BUILDERS.keys()),
        default=list(DATASET_BUILDERS.keys()),
        help="Which datasets to download (default: all).",
    )
    parser.add_argument(
        "--subjects",
        nargs="*",
        default=None,
        help="C-Eval subjects to include (default: 5 subjects from DuetNet paper).",
    )
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)

    results: list[Path] = []
    for name in args.datasets:
        builder = DATASET_BUILDERS[name]
        if name == "c_eval":
            path = builder(
                output_dir=args.output_dir,
                n=args.n if args.n > 0 else 999_999,
                seed=args.seed,
                subjects=args.subjects,
            )
        else:
            path = builder(
                output_dir=args.output_dir,
                n=args.n if args.n > 0 else 999_999,
                seed=args.seed,
            )
        results.append(path)

    logger.info("Done. %d file(s) written to %s", len(results), args.output_dir)

    print("\n--- Data Loader node config reference ---")
    for path in results:
        stem = path.stem
        print(f"\n# {stem}.jsonl")
        print(json.dumps({
            "loader_name": "jsonl_file",
            "loader_config": {
                "path": str(path.resolve()),
                "dataset_name": stem,
                "split": "val",
                "question_key": "question",
                "answer_key": "answer",
                "id_key": "id",
                "metadata_keys": ["subject", "extractor"] if stem == "c_eval" else ["extractor"],
            },
        }, indent=2))


if __name__ == "__main__":
    main()
