"""JSONL file data loader.

Reads newline-delimited JSON from a local path. The DuetNet benchmark suite
(SimpleMath / C-Eval / BoolQ / MMLU) ships as JSONL, so a workflow can point
this loader at the file on disk instead of inlining 50+ rows in the node
config.

Trust model: the loader reads any path the workflow author configured. The
node runs in the same trust boundary as ``code`` / ``http-request`` nodes, so
restricting filesystem reach is the operator's responsibility — guard via
container mount points or a wrapper loader if you need a sandbox.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from ..registry import (
    DataLoader,
    DataLoaderItem,
    DataLoaderResult,
    DataLoaderRunOptions,
    page_items,
    register_loader,
)


class JsonlFileLoaderConfig(BaseModel):
    """Configuration for reading JSONL rows from a local file."""

    model_config = ConfigDict(extra="forbid")

    path: str = Field(min_length=1)
    dataset_name: str | None = None
    split: str = Field(default="custom", min_length=1)
    encoding: str = "utf-8"
    id_key: str | None = None
    question_key: str = "question"
    answer_key: str = "answer"
    metadata_keys: list[str] = Field(default_factory=list)
    max_rows: int | None = Field(default=None, gt=0)


@register_loader("jsonl_file")
class JsonlFileDataLoader(DataLoader[JsonlFileLoaderConfig]):
    """Load rows from a newline-delimited JSON file on local disk."""

    name = "jsonl_file"
    description = "Load rows from a local JSONL file at loader_config.path."
    config_model = JsonlFileLoaderConfig

    def load(self, config: JsonlFileLoaderConfig, options: DataLoaderRunOptions) -> DataLoaderResult:
        rows = self._read_rows(config)
        selected = page_items(rows, options=options)
        normalized = [
            self._normalize_item(raw_row, index=original_index, config=config)
            for original_index, raw_row in selected
        ]
        resolved_path = str(Path(config.path).expanduser())
        return DataLoaderResult(
            dataset=config.dataset_name or Path(config.path).stem or self.name,
            split=config.split,
            items=normalized,
            total=len(rows),
            metadata={
                "loader": self.name,
                "path": resolved_path,
                "question_key": config.question_key,
                "answer_key": config.answer_key,
            },
        )

    @staticmethod
    def _read_rows(config: JsonlFileLoaderConfig) -> list[dict[str, Any]]:
        path = Path(config.path).expanduser()
        if not path.is_file():
            raise FileNotFoundError(f"JSONL file not found: {config.path}")
        rows: list[dict[str, Any]] = []
        with path.open(encoding=config.encoding) as handle:
            for line_no, raw_line in enumerate(handle, start=1):
                line = raw_line.strip()
                if not line:
                    continue
                try:
                    parsed = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise ValueError(
                        f"Invalid JSON at {path}:{line_no}: {exc.msg}"
                    ) from exc
                if not isinstance(parsed, dict):
                    raise ValueError(
                        f"Row at {path}:{line_no} must be a JSON object, got {type(parsed).__name__}"
                    )
                rows.append(parsed)
                if config.max_rows is not None and len(rows) >= config.max_rows:
                    break
        return rows

    def _normalize_item(
        self,
        raw_item: dict[str, Any],
        *,
        index: int,
        config: JsonlFileLoaderConfig,
    ) -> DataLoaderItem:
        item_id = self._resolve_id(raw_item, index=index, id_key=config.id_key)
        item: DataLoaderItem = {
            "id": item_id,
            "data": dict(raw_item),
        }
        question = raw_item.get(config.question_key)
        answer = raw_item.get(config.answer_key)
        if question is not None:
            item["question"] = str(question)
        if answer is not None:
            item["answer"] = str(answer)
        metadata = {
            key: raw_item[key]
            for key in config.metadata_keys
            if key in raw_item
        }
        if metadata:
            item["metadata"] = metadata
        return item

    @staticmethod
    def _resolve_id(raw_item: dict[str, Any], *, index: int, id_key: str | None) -> str:
        if id_key:
            value = raw_item.get(id_key)
            if value is not None:
                return str(value)
        return str(index)
