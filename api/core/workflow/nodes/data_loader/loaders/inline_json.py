"""Reference loader backed by JSON rows embedded in ``loader_config``.

This loader is deliberately simple and doubles as the fork template for
dataset-specific loaders: validate a typed config, normalize each raw row into
``DataLoaderItem``, then delegate paging/shuffling to ``page_items``.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from ..registry import DataLoader, DataLoaderItem, DataLoaderResult, DataLoaderRunOptions, page_items, register_loader


class InlineJsonLoaderConfig(BaseModel):
    """Inline JSON rows with optional question/answer field extraction."""

    model_config = ConfigDict(extra="forbid")

    dataset_name: str = Field(default="inline_json", min_length=1)
    split: str = Field(default="custom", min_length=1)
    items: list[dict[str, Any]] = Field(default_factory=list)
    id_key: str | None = None
    question_key: str = "question"
    answer_key: str = "answer"
    metadata_keys: list[str] = Field(default_factory=list)


@register_loader("inline_json")
class InlineJsonDataLoader(DataLoader[InlineJsonLoaderConfig]):
    """Load rows supplied directly in the node config."""

    name = "inline_json"
    description = "Load rows embedded in loader_config.items."
    config_model = InlineJsonLoaderConfig

    def load(self, config: InlineJsonLoaderConfig, options: DataLoaderRunOptions) -> DataLoaderResult:
        selected = page_items(config.items, options=options)
        normalized_items = [
            self._normalize_item(raw_item, index=original_index, config=config)
            for original_index, raw_item in selected
        ]
        return DataLoaderResult(
            dataset=config.dataset_name,
            split=config.split,
            items=normalized_items,
            total=len(config.items),
            metadata={
                "loader": self.name,
                "question_key": config.question_key,
                "answer_key": config.answer_key,
            },
        )

    def _normalize_item(
        self,
        raw_item: dict[str, Any],
        *,
        index: int,
        config: InlineJsonLoaderConfig,
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
