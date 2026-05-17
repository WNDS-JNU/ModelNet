"""Generic data-loader workflow node.

The node is the reusable graphon binding for dataset loading. Concrete datasets
are plugged in through the loader registry; this node owns common behaviour:
loader lookup, typed config validation, deterministic paging/shuffling metadata,
and a stable output contract for downstream workflow nodes.
"""

from __future__ import annotations

import logging
from collections.abc import Generator
from typing import Any, ClassVar

from pydantic import ValidationError

from graphon.enums import NodeType, WorkflowNodeExecutionStatus
from graphon.node_events.base import NodeEventBase, NodeRunResult
from graphon.node_events.node import StreamCompletedEvent
from graphon.nodes.base.node import Node

from . import DATA_LOADER_NODE_TYPE

# Import built-in loaders for registration side effects.
from . import loaders as _loaders  # noqa: F401
from .entities import DataLoaderNodeData
from .exc import DataLoaderConfigError, DataLoaderExecutionError, DataLoaderNodeError
from .registry import DataLoaderResult, DataLoaderRunOptions, get_loader

logger = logging.getLogger(__name__)


class DataLoaderNode(Node[DataLoaderNodeData]):
    """Workflow node that runs a registered data loader."""

    node_type: ClassVar[NodeType] = DATA_LOADER_NODE_TYPE

    @classmethod
    def version(cls) -> str:
        return "1"

    def _run(self) -> Generator[NodeEventBase, None, None]:
        node_data = self.node_data
        options = DataLoaderRunOptions(
            limit=node_data.limit,
            offset=node_data.offset,
            shuffle=node_data.shuffle,
            seed=node_data.seed,
        )

        try:
            loader = get_loader(node_data.loader_name)
            try:
                parsed_config = loader.parse_config(node_data.loader_config)
            except ValidationError as exc:
                raise DataLoaderConfigError(node_data.loader_name, str(exc)) from exc
            try:
                result = loader.load(parsed_config, options)
            except DataLoaderNodeError:
                raise
            except Exception as exc:
                raise DataLoaderExecutionError(node_data.loader_name, str(exc)) from exc
        except DataLoaderNodeError as exc:
            logger.warning("DataLoaderNode %s failed: %s", self._node_id, exc, exc_info=True)
            yield StreamCompletedEvent(
                node_run_result=NodeRunResult(
                    status=WorkflowNodeExecutionStatus.FAILED,
                    inputs=self._run_inputs(node_data),
                    error=str(exc),
                    error_type=type(exc).__name__,
                ),
            )
            return

        yield StreamCompletedEvent(
            node_run_result=NodeRunResult(
                status=WorkflowNodeExecutionStatus.SUCCEEDED,
                inputs=self._run_inputs(node_data),
                outputs=self._build_outputs(result, options, node_data.loader_name),
            ),
        )

    @staticmethod
    def _run_inputs(node_data: DataLoaderNodeData) -> dict[str, Any]:
        return {
            "loader_name": node_data.loader_name,
            "limit": node_data.limit,
            "offset": node_data.offset,
            "shuffle": node_data.shuffle,
            "seed": node_data.seed,
        }

    @staticmethod
    def _build_outputs(
        result: DataLoaderResult,
        options: DataLoaderRunOptions,
        loader_name: str,
    ) -> dict[str, Any]:
        count = len(result.items)
        next_offset = options.offset + count
        has_more = next_offset < result.total
        questions = [item.get("question", "") for item in result.items]
        answers = [item.get("answer", "") for item in result.items]
        return {
            "dataset": result.dataset,
            "split": result.split,
            "items": result.items,
            "count": count,
            "total": result.total,
            "has_more": has_more,
            "next_offset": next_offset if has_more else None,
            "questions": questions,
            "answers": answers,
            "metadata": {
                **result.metadata,
                "loader_name": loader_name,
                "limit": options.limit,
                "offset": options.offset,
                "shuffle": options.shuffle,
                "seed": options.seed,
            },
        }
