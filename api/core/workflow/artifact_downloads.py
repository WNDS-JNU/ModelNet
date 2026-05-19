from __future__ import annotations

import base64
import hashlib
import hmac
import os
import time
from collections.abc import Mapping

from configs import dify_config
from graphon.file import FILE_MODEL_IDENTITY

ARTIFACT_ACCESS_TIMEOUT_SECONDS = 24 * 60 * 60
ARTIFACT_FILE_OUTPUT_KEY = "download_files"

WORKFLOW_ARTIFACTS: Mapping[str, str] = {
    "result": "workflow-result",
    "trace": "workflow-trace",
    "full-trace": "workflow-full-trace",
}


def _normalise_artifact_name(artifact_name: str) -> str:
    name = artifact_name.removesuffix(".json").replace("_", "-")
    if name not in WORKFLOW_ARTIFACTS:
        raise ValueError(f"unsupported workflow artifact: {artifact_name}")
    return name


def _sign_payload(*, workflow_run_id: str, artifact_name: str, timestamp: str, nonce: str) -> str:
    return f"workflow-artifact|{workflow_run_id}|{artifact_name}|{timestamp}|{nonce}"


def _sign(*, workflow_run_id: str, artifact_name: str, timestamp: str, nonce: str) -> str:
    secret_key = dify_config.SECRET_KEY.encode() if dify_config.SECRET_KEY else b""
    signature = hmac.new(
        secret_key,
        _sign_payload(
            workflow_run_id=workflow_run_id,
            artifact_name=artifact_name,
            timestamp=timestamp,
            nonce=nonce,
        ).encode(),
        hashlib.sha256,
    ).digest()
    return base64.urlsafe_b64encode(signature).decode()


def sign_workflow_artifact_url(*, workflow_run_id: str, artifact_name: str, for_external: bool = True) -> str:
    artifact_name = _normalise_artifact_name(artifact_name)
    base_url = dify_config.FILES_URL if for_external else (dify_config.INTERNAL_FILES_URL or dify_config.FILES_URL)
    timestamp = str(int(time.time()))
    nonce = os.urandom(16).hex()
    signature = _sign(
        workflow_run_id=workflow_run_id,
        artifact_name=artifact_name,
        timestamp=timestamp,
        nonce=nonce,
    )
    return (
        f"{base_url}/files/workflow-runs/{workflow_run_id}/artifacts/{artifact_name}.json"
        f"?timestamp={timestamp}&nonce={nonce}&sign={signature}"
    )


def verify_workflow_artifact_signature(
    *,
    workflow_run_id: str,
    artifact_name: str,
    timestamp: str,
    nonce: str,
    sign: str,
) -> bool:
    try:
        artifact_name = _normalise_artifact_name(artifact_name)
        issued_at = int(timestamp)
    except (TypeError, ValueError):
        return False

    expected = _sign(
        workflow_run_id=workflow_run_id,
        artifact_name=artifact_name,
        timestamp=timestamp,
        nonce=nonce,
    )
    if not hmac.compare_digest(sign, expected):
        return False

    current_time = int(time.time())
    age = current_time - issued_at
    return 0 <= age <= ARTIFACT_ACCESS_TIMEOUT_SECONDS


def build_workflow_artifact_file_outputs(*, workflow_run_id: str) -> list[dict[str, object]]:
    files: list[dict[str, object]] = []
    for artifact_name, filename_prefix in WORKFLOW_ARTIFACTS.items():
        filename = f"{filename_prefix}-{workflow_run_id[:8]}.json"
        url = sign_workflow_artifact_url(workflow_run_id=workflow_run_id, artifact_name=artifact_name)
        files.append(
            {
                "dify_model_identity": FILE_MODEL_IDENTITY,
                "id": f"{workflow_run_id}:{artifact_name}",
                "related_id": f"{workflow_run_id}:{artifact_name}",
                "filename": filename,
                "extension": ".json",
                "size": -1,
                "mime_type": "application/json",
                "type": "document",
                "transfer_method": "remote_url",
                "remote_url": url,
                "url": url,
                "upload_file_id": "",
            }
        )
    return files


def append_workflow_artifact_file_outputs(
    *,
    outputs: Mapping[str, object] | None,
    workflow_run_id: str,
) -> Mapping[str, object]:
    merged = dict(outputs or {})
    merged[ARTIFACT_FILE_OUTPUT_KEY] = build_workflow_artifact_file_outputs(workflow_run_id=workflow_run_id)
    return merged
