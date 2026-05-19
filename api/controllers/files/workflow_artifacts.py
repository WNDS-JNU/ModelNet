from __future__ import annotations

import json
from typing import Any
from urllib.parse import quote

import sqlalchemy as sa
from flask import Response, request
from flask_restx import Resource
from pydantic import BaseModel, Field
from werkzeug.exceptions import Forbidden, NotFound

from controllers.files import files_ns
from core.workflow.artifact_downloads import verify_workflow_artifact_signature
from extensions.ext_database import db
from extensions.ext_storage import storage
from models.workflow import WorkflowNodeExecutionModel, WorkflowRun

DEFAULT_REF_TEMPLATE_SWAGGER_2_0 = "#/definitions/{model}"


class WorkflowArtifactQuery(BaseModel):
    timestamp: str = Field(..., description="Unix timestamp")
    nonce: str = Field(..., description="Random nonce")
    sign: str = Field(..., description="HMAC signature")
    as_attachment: bool = Field(default=False, description="Download as attachment")


files_ns.schema_model(
    WorkflowArtifactQuery.__name__,
    WorkflowArtifactQuery.model_json_schema(ref_template=DEFAULT_REF_TEMPLATE_SWAGGER_2_0),
)


def _jsonable(value: Any) -> Any:
    try:
        json.dumps(value)
        return value
    except TypeError:
        if isinstance(value, dict):
            return {str(k): _jsonable(v) for k, v in value.items()}
        if isinstance(value, list):
            return [_jsonable(v) for v in value]
        if isinstance(value, tuple):
            return [_jsonable(v) for v in value]
        return str(value)


def _node_execution_to_dict(node: WorkflowNodeExecutionModel) -> dict[str, Any]:
    return {
        "id": node.id,
        "index": node.index,
        "node_execution_id": node.node_execution_id,
        "predecessor_node_id": node.predecessor_node_id,
        "node_id": node.node_id,
        "node_type": node.node_type,
        "title": node.title,
        "status": node.status,
        "error": node.error,
        "elapsed_time": node.elapsed_time,
        "created_at": node.created_at,
        "finished_at": node.finished_at,
        "inputs": node.load_full_inputs(db.session, storage),
        "process_data": node.load_full_process_data(db.session, storage),
        "outputs": node.load_full_outputs(db.session, storage),
        "execution_metadata": node.execution_metadata_dict,
    }


def _run_to_dict(workflow_run: WorkflowRun) -> dict[str, Any]:
    return {
        "id": workflow_run.id,
        "tenant_id": workflow_run.tenant_id,
        "app_id": workflow_run.app_id,
        "workflow_id": workflow_run.workflow_id,
        "type": workflow_run.type,
        "triggered_from": workflow_run.triggered_from,
        "version": workflow_run.version,
        "inputs": workflow_run.inputs_dict,
        "status": workflow_run.status,
        "outputs": workflow_run.outputs_dict,
        "error": workflow_run.error,
        "elapsed_time": workflow_run.elapsed_time,
        "total_tokens": workflow_run.total_tokens,
        "total_steps": workflow_run.total_steps,
        "created_by_role": workflow_run.created_by_role,
        "created_by": workflow_run.created_by,
        "created_at": workflow_run.created_at,
        "finished_at": workflow_run.finished_at,
        "exceptions_count": workflow_run.exceptions_count,
    }


def _load_node_executions(workflow_run_id: str) -> list[WorkflowNodeExecutionModel]:
    stmt = (
        WorkflowNodeExecutionModel.preload_offload_data_and_files(
            sa.select(WorkflowNodeExecutionModel),
        )
        .where(WorkflowNodeExecutionModel.workflow_run_id == workflow_run_id)
        .order_by(WorkflowNodeExecutionModel.created_at, WorkflowNodeExecutionModel.index)
    )
    return list(db.session.scalars(stmt).all())


def _build_artifact_payload(workflow_run: WorkflowRun, artifact_name: str) -> dict[str, Any]:
    nodes = [_node_execution_to_dict(node) for node in _load_node_executions(workflow_run.id)]
    run = _run_to_dict(workflow_run)

    if artifact_name == "result":
        return {
            "artifact": "result",
            "workflow_run": run,
            "outputs": workflow_run.outputs_dict,
        }

    if artifact_name == "trace":
        return {
            "artifact": "trace",
            "workflow_run": run,
            "node_executions": nodes,
        }

    if artifact_name == "full-trace":
        return {
            "artifact": "full-trace",
            "workflow_run": {
                **run,
                "graph": workflow_run.graph_dict,
            },
            "node_executions": nodes,
        }

    raise NotFound("Workflow artifact not found.")


@files_ns.route("/workflow-runs/<uuid:workflow_run_id>/artifacts/<string:artifact_name>.json")
class WorkflowArtifactApi(Resource):
    @files_ns.doc("get_workflow_run_artifact")
    @files_ns.doc(description="Download workflow run result and trace artifacts using signed parameters")
    def get(self, workflow_run_id, artifact_name: str):
        workflow_run_id = str(workflow_run_id)
        artifact_name = artifact_name.removesuffix(".json").replace("_", "-")
        args = WorkflowArtifactQuery.model_validate(request.args.to_dict())
        if not verify_workflow_artifact_signature(
            workflow_run_id=workflow_run_id,
            artifact_name=artifact_name,
            timestamp=args.timestamp,
            nonce=args.nonce,
            sign=args.sign,
        ):
            raise Forbidden("Invalid request.")

        workflow_run = db.session.get(WorkflowRun, workflow_run_id)
        if workflow_run is None:
            raise NotFound("Workflow run not found.")

        payload = _build_artifact_payload(workflow_run, artifact_name)
        body = json.dumps(_jsonable(payload), ensure_ascii=False, indent=2).encode("utf-8")
        filename = f"workflow-{artifact_name}-{workflow_run_id[:8]}.json"
        response = Response(
            body,
            mimetype="application/json; charset=utf-8",
            headers={
                "Content-Length": str(len(body)),
                "Cache-Control": "private, max-age=0, no-store",
            },
        )
        if args.as_attachment:
            encoded_filename = quote(filename)
            response.headers["Content-Disposition"] = f"attachment; filename*=UTF-8''{encoded_filename}"
        return response
