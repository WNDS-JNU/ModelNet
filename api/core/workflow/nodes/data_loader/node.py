"""Generic data-loader workflow node.

The node is the reusable graphon binding for dataset loading. Concrete datasets
are plugged in through the loader registry; this node owns common behaviour:
loader lookup, typed config validation, deterministic paging/shuffling metadata,
and a stable output contract for downstream workflow nodes.
"""

from __future__ import annotations

import base64
import logging
from collections.abc import Generator, Mapping, Sequence
from pathlib import Path
from typing import Any, ClassVar

from pydantic import ValidationError

from core.helper.code_executor.code_executor import CodeExecutionError, CodeExecutor
from graphon.enums import NodeType, WorkflowNodeExecutionStatus
from graphon.file import File, file_manager
from graphon.node_events.base import NodeEventBase, NodeRunResult
from graphon.node_events.node import StreamCompletedEvent
from graphon.nodes.base.node import Node
from graphon.nodes.code.entities import CodeLanguage
from graphon.variables.segments import ArrayFileSegment, FileSegment

from . import DATA_LOADER_NODE_TYPE

# Import built-in loaders for registration side effects.
from . import loaders as _loaders  # noqa: F401
from .entities import DataLoaderNodeData
from .exc import DataLoaderConfigError, DataLoaderExecutionError, DataLoaderNodeError
from .registry import DataLoaderItem, DataLoaderResult, DataLoaderRunOptions, get_loader, page_items

logger = logging.getLogger(__name__)

_UPLOADED_CODE_LOADER_NAME = "uploaded_code"
_PYTHON_CODE_EXTENSIONS = frozenset((".py",))
_PYTHON_CODE_MIME_TYPES = frozenset((
    "text/x-python",
    "text/python",
    "application/x-python-code",
))


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

        loader_name = node_data.loader_name
        try:
            if node_data.source_mode == _UPLOADED_CODE_LOADER_NAME:
                loader_name = _UPLOADED_CODE_LOADER_NAME
                result = self._run_uploaded_code_loader(node_data, options)
            else:
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
                outputs=self._build_outputs(result, options, loader_name),
            ),
        )

    def _run_uploaded_code_loader(
        self,
        node_data: DataLoaderNodeData,
        options: DataLoaderRunOptions,
    ) -> DataLoaderResult:
        data_file = self._resolve_single_file(
            node_data.data_file_selector,
            field_name="data_file_selector",
        )
        code_file = self._resolve_single_file(
            node_data.code_file_selector,
            field_name="code_file_selector",
        )
        self._validate_code_file(code_file)
        data_bytes = self._download_file(data_file, field_name="data_file_selector")
        code_bytes = self._download_file(code_file, field_name="code_file_selector")
        code_text = self._decode_code(code_bytes)
        raw_result = self._execute_uploaded_code(
            code_text=code_text,
            data_file=data_file,
            data_bytes=data_bytes,
        )
        return self._normalize_uploaded_result(
            raw_result,
            data_file=data_file,
            options=options,
        )

    @staticmethod
    def _run_inputs(node_data: DataLoaderNodeData) -> dict[str, Any]:
        inputs = {
            "loader_name": node_data.loader_name,
            "limit": node_data.limit,
            "offset": node_data.offset,
            "shuffle": node_data.shuffle,
            "seed": node_data.seed,
        }
        if node_data.source_mode == _UPLOADED_CODE_LOADER_NAME:
            inputs.update({
                "source_mode": node_data.source_mode,
                "data_file_selector": node_data.data_file_selector,
                "code_file_selector": node_data.code_file_selector,
                "code_language": node_data.code_language,
            })
        return inputs

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

    def _resolve_single_file(self, selector: Sequence[str], *, field_name: str) -> File:
        if len(selector) < 2:
            raise DataLoaderConfigError(
                _UPLOADED_CODE_LOADER_NAME,
                f"{field_name} must select a File or Array[File] variable.",
            )
        variable = self.graph_runtime_state.variable_pool.get(selector)
        if variable is None:
            raise DataLoaderExecutionError(
                _UPLOADED_CODE_LOADER_NAME,
                f"File variable not found for selector: {list(selector)}",
            )
        if isinstance(variable, FileSegment):
            return variable.value
        if isinstance(variable, ArrayFileSegment):
            files = [file for file in variable.value if file]
            if len(files) != 1:
                raise DataLoaderExecutionError(
                    _UPLOADED_CODE_LOADER_NAME,
                    f"{field_name} must contain exactly one file, got {len(files)}.",
                )
            return files[0]
        raise DataLoaderExecutionError(
            _UPLOADED_CODE_LOADER_NAME,
            f"{field_name} must resolve to File or Array[File], got {type(variable).__name__}.",
        )

    @staticmethod
    def _validate_code_file(code_file: File) -> None:
        extension = (code_file.extension or Path(code_file.filename or "").suffix or "").lower()
        mime_type = (code_file.mime_type or "").lower()
        if extension in _PYTHON_CODE_EXTENSIONS or mime_type in _PYTHON_CODE_MIME_TYPES:
            return
        raise DataLoaderConfigError(
            _UPLOADED_CODE_LOADER_NAME,
            "code_file_selector must point to a Python .py file.",
        )

    @staticmethod
    def _download_file(file: File, *, field_name: str) -> bytes:
        try:
            return file_manager.download(file)
        except Exception as exc:
            raise DataLoaderExecutionError(
                _UPLOADED_CODE_LOADER_NAME,
                f"Failed to read {field_name}: {exc}",
            ) from exc

    @staticmethod
    def _decode_code(code_bytes: bytes) -> str:
        try:
            return code_bytes.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise DataLoaderConfigError(
                _UPLOADED_CODE_LOADER_NAME,
                "Python loader code must be UTF-8 encoded.",
            ) from exc

    @staticmethod
    def _execute_uploaded_code(
        *,
        code_text: str,
        data_file: File,
        data_bytes: bytes,
    ) -> Mapping[str, Any]:
        try:
            result = CodeExecutor.execute_workflow_code_template(
                CodeLanguage.PYTHON3,
                code_text,
                {
                    "data_b64": base64.b64encode(data_bytes).decode("ascii"),
                    "filename": data_file.filename or "",
                    "metadata": _file_metadata(data_file),
                },
            )
        except CodeExecutionError as exc:
            raise DataLoaderExecutionError(_UPLOADED_CODE_LOADER_NAME, str(exc)) from exc
        except Exception as exc:
            raise DataLoaderExecutionError(_UPLOADED_CODE_LOADER_NAME, str(exc)) from exc
        if not isinstance(result, Mapping):
            raise DataLoaderExecutionError(
                _UPLOADED_CODE_LOADER_NAME,
                f"Uploaded loader code must return an object, got {type(result).__name__}.",
            )
        return result

    @staticmethod
    def _normalize_uploaded_result(
        raw_result: Mapping[str, Any],
        *,
        data_file: File,
        options: DataLoaderRunOptions,
    ) -> DataLoaderResult:
        raw_items = raw_result.get("items")
        if not isinstance(raw_items, list):
            raise DataLoaderExecutionError(
                _UPLOADED_CODE_LOADER_NAME,
                "Uploaded loader code must return an 'items' array.",
            )
        metadata = raw_result.get("metadata") or {}
        if not isinstance(metadata, Mapping):
            raise DataLoaderExecutionError(
                _UPLOADED_CODE_LOADER_NAME,
                "Uploaded loader code metadata must be an object.",
            )

        normalized_items = [
            _normalize_uploaded_item(raw_item, index=index)
            for index, raw_item in enumerate(raw_items)
        ]
        selected_items = [
            item
            for _, item in page_items(normalized_items, options=options)
        ]
        dataset = raw_result.get("dataset") or data_file.filename or _UPLOADED_CODE_LOADER_NAME
        split = raw_result.get("split") or "custom"
        return DataLoaderResult(
            dataset=str(dataset),
            split=str(split),
            items=selected_items,
            total=len(normalized_items),
            metadata={
                **dict(metadata),
                "loader": _UPLOADED_CODE_LOADER_NAME,
                "data_file": _file_metadata(data_file),
            },
        )

    @classmethod
    def _extract_variable_selector_to_variable_mapping(
        cls,
        *,
        graph_config: Mapping[str, Any],
        node_id: str,
        node_data: DataLoaderNodeData,
    ) -> Mapping[str, Sequence[str]]:
        _ = graph_config
        if node_data.source_mode != _UPLOADED_CODE_LOADER_NAME:
            return {}
        mapping: dict[str, Sequence[str]] = {}
        if node_data.data_file_selector:
            mapping[f"{node_id}.data_file"] = node_data.data_file_selector
        if node_data.code_file_selector:
            mapping[f"{node_id}.code_file"] = node_data.code_file_selector
        return mapping


def _normalize_uploaded_item(raw_item: Any, *, index: int) -> DataLoaderItem:
    if not isinstance(raw_item, Mapping):
        raise DataLoaderExecutionError(
            _UPLOADED_CODE_LOADER_NAME,
            f"Uploaded loader item at index {index} must be an object.",
        )
    raw_mapping = dict(raw_item)
    data = raw_mapping.get("data", raw_mapping)
    if not isinstance(data, Mapping):
        raise DataLoaderExecutionError(
            _UPLOADED_CODE_LOADER_NAME,
            f"Uploaded loader item at index {index} has non-object data.",
        )
    item_id = raw_mapping.get("id")
    item: DataLoaderItem = {
        "id": str(index if item_id is None else item_id),
        "data": dict(data),
    }
    question = raw_mapping.get("question")
    answer = raw_mapping.get("answer")
    if question is not None:
        item["question"] = str(question)
    if answer is not None:
        item["answer"] = str(answer)
    metadata = raw_mapping.get("metadata")
    if metadata is not None:
        if not isinstance(metadata, Mapping):
            raise DataLoaderExecutionError(
                _UPLOADED_CODE_LOADER_NAME,
                f"Uploaded loader item at index {index} has non-object metadata.",
            )
        item["metadata"] = dict(metadata)
    return item


def _file_metadata(file: File) -> dict[str, Any]:
    return {
        "filename": file.filename,
        "extension": file.extension,
        "mime_type": file.mime_type,
        "size": file.size,
    }
