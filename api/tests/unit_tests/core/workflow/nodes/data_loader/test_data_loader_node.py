import pytest
from pydantic import BaseModel, ConfigDict

from core.workflow.nodes.data_loader import DATA_LOADER_NODE_TYPE, DataLoaderNode
from core.workflow.nodes.data_loader.entities import DataLoaderNodeData
from core.workflow.nodes.data_loader.exc import DataLoaderRegistrationError
from core.workflow.nodes.data_loader.registry import (
    DataLoader,
    DataLoaderResult,
    DataLoaderRunOptions,
    list_loaders,
    register_loader,
)
from graphon.enums import WorkflowNodeExecutionStatus
from graphon.node_events.node import StreamCompletedEvent
from graphon.runtime.variable_pool import VariablePool


def _make_node(payload: dict) -> DataLoaderNode:
    node = DataLoaderNode.__new__(DataLoaderNode)
    node._node_id = "loader_1"

    class _RS:
        pass

    rs = _RS()
    rs.variable_pool = VariablePool()
    node.graph_runtime_state = rs
    node._node_data = DataLoaderNode._node_data_type.model_validate(payload)
    return node


def _payload(**overrides) -> dict:
    payload = {
        "title": "loader",
        "type": DATA_LOADER_NODE_TYPE,
        "loader_name": "inline_json",
        "loader_config": {
            "dataset_name": "demo",
            "split": "test",
            "items": [
                {"id": "a", "question": "1+1", "answer": "2", "topic": "math"},
                {"id": "b", "question": "2+2", "answer": "4", "topic": "math"},
                {"id": "c", "question": "3+3", "answer": "6", "topic": "math"},
            ],
            "id_key": "id",
            "metadata_keys": ["topic"],
        },
        "limit": 2,
        "offset": 0,
    }
    payload.update(overrides)
    return payload


def test_inline_json_loader_is_registered():
    assert {"name": "inline_json", "description": "Load rows embedded in loader_config.items."} in list_loaders()


def test_jsonl_file_loader_is_registered():
    assert {
        "name": "jsonl_file",
        "description": "Load rows from a local JSONL file at loader_config.path.",
    } in list_loaders()


def test_jsonl_file_loader_reads_from_disk(tmp_path):
    dataset_path = tmp_path / "boolq.jsonl"
    dataset_path.write_text(
        '{"id": "q1", "question": "is the sky blue?", "answer": "true", "topic": "world"}\n'
        "\n"  # blank line should be skipped
        '{"id": "q2", "question": "is fire cold?", "answer": "false", "topic": "world"}\n'
        '{"id": "q3", "question": "do birds fly?", "answer": "true", "topic": "world"}\n',
        encoding="utf-8",
    )

    payload = {
        "title": "loader",
        "type": DATA_LOADER_NODE_TYPE,
        "loader_name": "jsonl_file",
        "loader_config": {
            "path": str(dataset_path),
            "dataset_name": "boolq",
            "split": "dev",
            "id_key": "id",
            "metadata_keys": ["topic"],
        },
        "limit": 2,
        "offset": 1,
    }

    result = list(_make_node(payload)._run())[0].node_run_result

    assert result.status == WorkflowNodeExecutionStatus.SUCCEEDED
    outputs = result.outputs
    assert outputs["dataset"] == "boolq"
    assert outputs["split"] == "dev"
    assert outputs["total"] == 3
    assert outputs["count"] == 2
    assert outputs["has_more"] is False
    assert outputs["next_offset"] is None
    assert [item["id"] for item in outputs["items"]] == ["q2", "q3"]
    assert outputs["questions"] == ["is fire cold?", "do birds fly?"]
    assert outputs["metadata"]["path"] == str(dataset_path)


def test_jsonl_file_loader_falls_back_to_filename_stem(tmp_path):
    dataset_path = tmp_path / "simple_math.jsonl"
    dataset_path.write_text('{"question": "1+1", "answer": "2"}\n', encoding="utf-8")

    payload = {
        "title": "loader",
        "type": DATA_LOADER_NODE_TYPE,
        "loader_name": "jsonl_file",
        "loader_config": {"path": str(dataset_path)},
        "limit": 5,
        "offset": 0,
    }

    outputs = list(_make_node(payload)._run())[0].node_run_result.outputs

    assert outputs["dataset"] == "simple_math"
    assert outputs["items"][0]["id"] == "0"  # falls back to row index
    assert outputs["items"][0]["question"] == "1+1"


def test_jsonl_file_loader_missing_path_reports_execution_error(tmp_path):
    payload = {
        "title": "loader",
        "type": DATA_LOADER_NODE_TYPE,
        "loader_name": "jsonl_file",
        "loader_config": {"path": str(tmp_path / "does_not_exist.jsonl")},
        "limit": 1,
        "offset": 0,
    }

    result = list(_make_node(payload)._run())[0].node_run_result

    assert result.status == WorkflowNodeExecutionStatus.FAILED
    assert result.error_type == "DataLoaderExecutionError"
    assert "does_not_exist.jsonl" in result.error


def test_jsonl_file_loader_rejects_invalid_json(tmp_path):
    dataset_path = tmp_path / "broken.jsonl"
    dataset_path.write_text('{"question": "ok"}\nnot-json\n', encoding="utf-8")

    payload = {
        "title": "loader",
        "type": DATA_LOADER_NODE_TYPE,
        "loader_name": "jsonl_file",
        "loader_config": {"path": str(dataset_path)},
        "limit": 5,
        "offset": 0,
    }

    result = list(_make_node(payload)._run())[0].node_run_result

    assert result.status == WorkflowNodeExecutionStatus.FAILED
    assert result.error_type == "DataLoaderExecutionError"
    assert ":2" in result.error  # points to the failing line


def test_jsonl_file_loader_rejects_non_object_rows(tmp_path):
    dataset_path = tmp_path / "arrays.jsonl"
    dataset_path.write_text("[1, 2, 3]\n", encoding="utf-8")

    payload = {
        "title": "loader",
        "type": DATA_LOADER_NODE_TYPE,
        "loader_name": "jsonl_file",
        "loader_config": {"path": str(dataset_path)},
        "limit": 1,
        "offset": 0,
    }

    result = list(_make_node(payload)._run())[0].node_run_result

    assert result.status == WorkflowNodeExecutionStatus.FAILED
    assert result.error_type == "DataLoaderExecutionError"
    assert "must be a JSON object" in result.error


def test_jsonl_file_loader_respects_max_rows(tmp_path):
    dataset_path = tmp_path / "long.jsonl"
    dataset_path.write_text(
        "".join(f'{{"id": "{i}", "question": "q{i}", "answer": "a{i}"}}\n' for i in range(10)),
        encoding="utf-8",
    )

    payload = {
        "title": "loader",
        "type": DATA_LOADER_NODE_TYPE,
        "loader_name": "jsonl_file",
        "loader_config": {"path": str(dataset_path), "id_key": "id", "max_rows": 3},
        "limit": 100,
        "offset": 0,
    }

    outputs = list(_make_node(payload)._run())[0].node_run_result.outputs

    assert outputs["total"] == 3
    assert [item["id"] for item in outputs["items"]] == ["0", "1", "2"]


def test_node_data_defaults_to_inline_json():
    node_data = DataLoaderNodeData(title="loader")

    assert node_data.type == DATA_LOADER_NODE_TYPE
    assert node_data.loader_name == "inline_json"
    assert node_data.limit == 100
    assert node_data.offset == 0


def test_blank_loader_name_rejected():
    with pytest.raises(ValueError, match="loader_name must not be blank"):
        DataLoaderNodeData(title="loader", loader_name="   ")


def test_inline_json_loader_outputs_common_contract():
    node = _make_node(_payload())

    events = list(node._run())

    assert len(events) == 1
    assert isinstance(events[0], StreamCompletedEvent)
    result = events[0].node_run_result
    assert result.status == WorkflowNodeExecutionStatus.SUCCEEDED
    assert result.inputs == {
        "loader_name": "inline_json",
        "limit": 2,
        "offset": 0,
        "shuffle": False,
        "seed": None,
    }
    assert result.outputs["dataset"] == "demo"
    assert result.outputs["split"] == "test"
    assert result.outputs["count"] == 2
    assert result.outputs["total"] == 3
    assert result.outputs["has_more"] is True
    assert result.outputs["next_offset"] == 2
    assert result.outputs["questions"] == ["1+1", "2+2"]
    assert result.outputs["answers"] == ["2", "4"]
    assert result.outputs["items"] == [
        {
            "id": "a",
            "data": {"id": "a", "question": "1+1", "answer": "2", "topic": "math"},
            "question": "1+1",
            "answer": "2",
            "metadata": {"topic": "math"},
        },
        {
            "id": "b",
            "data": {"id": "b", "question": "2+2", "answer": "4", "topic": "math"},
            "question": "2+2",
            "answer": "4",
            "metadata": {"topic": "math"},
        },
    ]


def test_inline_json_loader_supports_seeded_shuffle():
    payload = _payload(shuffle=True, seed=7, limit=3)
    first = list(_make_node(payload)._run())[0].node_run_result.outputs["items"]
    second = list(_make_node(payload)._run())[0].node_run_result.outputs["items"]

    assert first == second
    assert [item["id"] for item in first] != ["a", "b", "c"]


def test_unknown_loader_fails_with_structured_error():
    node = _make_node(_payload(loader_name="missing_loader"))

    result = list(node._run())[0].node_run_result

    assert result.status == WorkflowNodeExecutionStatus.FAILED
    assert result.error_type == "DataLoaderNotFoundError"
    assert "missing_loader" in result.error


def test_duplicate_loader_registration_is_rejected():
    class _DummyConfig(BaseModel):
        model_config = ConfigDict(extra="forbid")

    class _DummyLoaderA(DataLoader[_DummyConfig]):
        name = "dup_loader_for_test"
        config_model = _DummyConfig

        def load(self, config: _DummyConfig, options: DataLoaderRunOptions) -> DataLoaderResult:
            return DataLoaderResult(dataset="x", split="y", items=[], total=0, metadata={})

    class _DummyLoaderB(DataLoader[_DummyConfig]):
        name = "dup_loader_for_test"
        config_model = _DummyConfig

        def load(self, config: _DummyConfig, options: DataLoaderRunOptions) -> DataLoaderResult:
            return DataLoaderResult(dataset="x", split="y", items=[], total=0, metadata={})

    register_loader("dup_loader_for_test")(_DummyLoaderA)
    try:
        with pytest.raises(DataLoaderRegistrationError, match="dup_loader_for_test"):
            register_loader("dup_loader_for_test")(_DummyLoaderB)
        # Re-registering the *same* class is a no-op (handles double-import).
        register_loader("dup_loader_for_test")(_DummyLoaderA)
    finally:
        from core.workflow.nodes.data_loader.registry import _LOADERS

        _LOADERS.pop("dup_loader_for_test", None)


def test_loader_config_validation_error_fails_node():
    node = _make_node(
        _payload(loader_config={"items": [], "unexpected": True})
    )

    result = list(node._run())[0].node_run_result

    assert result.status == WorkflowNodeExecutionStatus.FAILED
    assert result.error_type == "DataLoaderConfigError"
    assert "unexpected" in result.error
