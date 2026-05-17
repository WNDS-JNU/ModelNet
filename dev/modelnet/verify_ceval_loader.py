"""Verify C-Eval JSONL format against Dify's jsonl_file Data Loader.

Runs the actual ``JsonlFileDataLoader`` in isolation (no Dify server needed)
to confirm every row parses cleanly and the expected fields are present.

Usage::

    cd /home/duxianghe/dify/api && uv run python ../dev/modelnet/verify_ceval_loader.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
API_DIR = PROJECT_ROOT / "api"
JSONL_PATH = SCRIPT_DIR / "datasets" / "c_eval.jsonl"


def main() -> None:
    if API_DIR not in sys.path:
        sys.path.insert(0, str(API_DIR))

    if not JSONL_PATH.is_file():
        print(f"ERROR: {JSONL_PATH} not found. Run download_datasets.py first.")
        sys.exit(1)

    from core.workflow.nodes.data_loader.loaders import JsonlFileDataLoader
    from core.workflow.nodes.data_loader.registry import DataLoaderRunOptions, list_loaders

    print("Registered loaders:", [l["name"] for l in list_loaders()])
    print()

    loader = JsonlFileDataLoader()

    config = loader.parse_config({
        "path": str(JSONL_PATH),
        "dataset_name": "c_eval",
        "split": "val",
        "question_key": "question",
        "answer_key": "answer",
        "id_key": "id",
        "metadata_keys": ["subject", "extractor"],
    })

    options = DataLoaderRunOptions(limit=5, offset=0, shuffle=False, seed=None)
    result = loader.load(config, options)

    print(f"Dataset:   {result.dataset}")
    print(f"Split:     {result.split}")
    print(f"Total:     {result.total}")
    print(f"Loaded:    {len(result.items)} items")
    print(f"Metadata:  {result.metadata}")
    print()

    for i, item in enumerate(result.items):
        print(f"--- Item {i} ---")
        print(f"  id:       {item.get('id')}")
        question = item.get("question", "")
        print(f"  question: {question[:80]}{'...' if len(question) > 80 else ''}")
        print(f"  answer:   {item.get('answer')}")
        meta = item.get("metadata", {})
        if meta:
            print(f"  metadata: {meta}")
        print()

    questions = [item.get("question", "") for item in result.items if item.get("question")]
    answers = [item.get("answer", "") for item in result.items if item.get("answer")]
    print(f"Questions extracted: {len(questions)}/{len(result.items)}")
    print(f"Answers extracted:   {len(answers)}/{len(result.items)}")

    if len(questions) == len(result.items) and len(answers) == len(result.items):
        print("\n✅ PASS: All items have question and answer fields.")
    else:
        print("\n❌ FAIL: Some items are missing question or answer fields.")
        sys.exit(1)

    print(f"\nFull first item JSON:")
    print(json.dumps(result.items[0], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
