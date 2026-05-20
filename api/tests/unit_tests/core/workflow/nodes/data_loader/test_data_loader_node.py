import base64

import pytest
from pydantic import BaseModel, ConfigDict

import core.workflow.nodes.data_loader.node as data_loader_node_module
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
from graphon.file import File, FileTransferMethod, FileType
from graphon.node_events.node import StreamCompletedEvent
from graphon.runtime.variable_pool import VariablePool


def _make_node(payload: dict, variables: list[tuple[list[str], object]] | None = None) -> DataLoaderNode:
    node = DataLoaderNode.__new__(DataLoaderNode)
    node._node_id = "loader_1"

    class _RS:
        pass

    rs = _RS()
    rs.variable_pool = VariablePool()
    for selector, value in variables or []:
        rs.variable_pool.add(selector, value)
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


def _file(
    *,
    filename: str,
    extension: str,
    mime_type: str,
    reference: str,
    size: int = 10,
) -> File:
    return File(
        file_type=FileType.CUSTOM,
        transfer_method=FileTransferMethod.LOCAL_FILE,
        reference=reference,
        filename=filename,
        extension=extension,
        mime_type=mime_type,
        size=size,
    )


def _uploaded_payload(**overrides) -> dict:
    payload = _payload(
        source_mode="uploaded_code",
        data_file_selector=["start", "data_file"],
        code_file_selector=["start", "code_file"],
        code_language="python3",
        limit=2,
        offset=0,
    )
    payload.update(overrides)
    return payload


def _uploaded_variables() -> list[tuple[list[str], object]]:
    return [
        (
            ["start", "data_file"],
            _file(
                filename="demo.jsonl",
                extension=".jsonl",
                mime_type="application/jsonl",
                reference="data-file-id",
                size=12,
            ),
        ),
        (
            ["start", "code_file"],
            _file(
                filename="loader.py",
                extension=".py",
                mime_type="text/x-python",
                reference="code-file-id",
                size=20,
            ),
        ),
    ]


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


def test_uploaded_code_loader_executes_user_python(monkeypatch):
    payload = _uploaded_payload(limit=2)
    variables = _uploaded_variables()

    def fake_download(file: File) -> bytes:
        if file.filename == "loader.py":
            return b"def main(data_b64, filename, metadata):\n    return {}\n"
        return b'{"question":"1+1","answer":"2"}\n'

    def fake_execute(language, code, inputs):
        assert str(language) == "python3"
        assert "def main" in code
        assert base64.b64decode(inputs["data_b64"]) == b'{"question":"1+1","answer":"2"}\n'
        assert inputs["filename"] == "demo.jsonl"
        assert inputs["metadata"]["filename"] == "demo.jsonl"
        return {
            "dataset": "uploaded-demo",
            "split": "eval",
            "items": [
                {"id": "a", "question": "1+1", "answer": "2", "topic": "math"},
                {"id": "b", "question": "2+2", "answer": "4", "data": {"prompt": "2+2"}, "metadata": {"topic": "math"}},
                {"id": "c", "question": "3+3", "answer": "6"},
            ],
            "metadata": {"source": "user-code"},
        }

    monkeypatch.setattr(data_loader_node_module.file_manager, "download", fake_download)
    monkeypatch.setattr(
        data_loader_node_module.CodeExecutor,
        "execute_workflow_code_template",
        staticmethod(fake_execute),
    )

    result = list(_make_node(payload, variables)._run())[0].node_run_result

    assert result.status == WorkflowNodeExecutionStatus.SUCCEEDED
    assert result.inputs["source_mode"] == "uploaded_code"
    assert result.outputs["dataset"] == "uploaded-demo"
    assert result.outputs["split"] == "eval"
    assert result.outputs["count"] == 2
    assert result.outputs["total"] == 3
    assert result.outputs["has_more"] is True
    assert result.outputs["next_offset"] == 2
    assert result.outputs["questions"] == ["1+1", "2+2"]
    assert result.outputs["answers"] == ["2", "4"]
    assert result.outputs["items"][0]["data"]["topic"] == "math"
    assert result.outputs["items"][1]["data"] == {"prompt": "2+2"}
    assert result.outputs["items"][1]["metadata"] == {"topic": "math"}
    assert result.outputs["metadata"]["loader_name"] == "uploaded_code"
    assert result.outputs["metadata"]["source"] == "user-code"
    assert result.outputs["metadata"]["data_file"]["filename"] == "demo.jsonl"


def test_uploaded_code_loader_supports_single_file_array(monkeypatch):
    payload = _uploaded_payload()
    variables = _uploaded_variables()
    variables[0] = (["start", "data_file"], [variables[0][1]])

    monkeypatch.setattr(
        data_loader_node_module.file_manager,
        "download",
        lambda file: b"def main(): pass" if file.filename == "loader.py" else b"data",
    )
    monkeypatch.setattr(
        data_loader_node_module.CodeExecutor,
        "execute_workflow_code_template",
        staticmethod(lambda language, code, inputs: {"items": [{"question": "q"}]}),
    )

    result = list(_make_node(payload, variables)._run())[0].node_run_result

    assert result.status == WorkflowNodeExecutionStatus.SUCCEEDED
    assert result.outputs["items"][0]["id"] == "0"
    assert result.outputs["questions"] == ["q"]


@pytest.mark.parametrize(
    ("payload_overrides", "variables", "message"),
    [
        ({"data_file_selector": []}, _uploaded_variables(), "data_file_selector"),
        ({}, _uploaded_variables()[1:], "File variable not found"),
        (
            {},
            [(["start", "data_file"], "not-a-file"), _uploaded_variables()[1]],
            "must resolve to File or Array[File]",
        ),
        (
            {},
            [
                (["start", "data_file"], [_uploaded_variables()[0][1], _uploaded_variables()[0][1]]),
                _uploaded_variables()[1],
            ],
            "exactly one file",
        ),
        (
            {},
            [
                _uploaded_variables()[0],
                (
                    ["start", "code_file"],
                    _file(filename="loader.txt", extension=".txt", mime_type="text/plain", reference="code-file-id"),
                ),
            ],
            "Python .py file",
        ),
    ],
)
def test_uploaded_code_loader_file_errors(payload_overrides, variables, message):
    result = list(_make_node(_uploaded_payload(**payload_overrides), variables)._run())[0].node_run_result

    assert result.status == WorkflowNodeExecutionStatus.FAILED
    assert message in result.error


@pytest.mark.parametrize(
    ("sandbox_result", "message"),
    [
        ([], "must return an object"),
        ({}, "must return an 'items' array"),
        ({"items": ["bad"]}, "item at index 0 must be an object"),
        ({"items": [{"data": "bad"}]}, "non-object data"),
        ({"items": [{"metadata": "bad"}]}, "non-object metadata"),
        ({"items": [], "metadata": "bad"}, "metadata must be an object"),
    ],
)
def test_uploaded_code_loader_rejects_invalid_sandbox_result(monkeypatch, sandbox_result, message):
    monkeypatch.setattr(
        data_loader_node_module.file_manager,
        "download",
        lambda file: b"def main(data_b64, filename, metadata): return {}",
    )
    monkeypatch.setattr(
        data_loader_node_module.CodeExecutor,
        "execute_workflow_code_template",
        staticmethod(lambda language, code, inputs: sandbox_result),
    )

    result = list(_make_node(_uploaded_payload(), _uploaded_variables())._run())[0].node_run_result

    assert result.status == WorkflowNodeExecutionStatus.FAILED
    assert message in result.error


def test_uploaded_code_loader_wraps_sandbox_parse_error(monkeypatch):
    monkeypatch.setattr(
        data_loader_node_module.file_manager,
        "download",
        lambda file: b"def main(data_b64, filename, metadata): return {}",
    )
    monkeypatch.setattr(
        data_loader_node_module.CodeExecutor,
        "execute_workflow_code_template",
        staticmethod(lambda *_args, **_kwargs: (_ for _ in ()).throw(ValueError("bad sandbox response"))),
    )

    result = list(_make_node(_uploaded_payload(), _uploaded_variables())._run())[0].node_run_result

    assert result.status == WorkflowNodeExecutionStatus.FAILED
    assert "bad sandbox response" in result.error


def test_node_data_defaults_to_inline_json():
    node_data = DataLoaderNodeData(title="loader")

    assert node_data.type == DATA_LOADER_NODE_TYPE
    assert node_data.source_mode == "configured"
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
