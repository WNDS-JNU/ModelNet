"""Service layer for ModelNet Kubernetes registry refresh."""

from __future__ import annotations

import json
import os
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

from configs import dify_config
from core.workflow.nodes.parallel_ensemble import backends as _modelnet_backends  # noqa: F401
from core.workflow.nodes.parallel_ensemble.registry.k8s_discovery import (
    K8sDiscoverySettings,
    discover_model_registry,
    parse_namespaces,
)
from core.workflow.nodes.parallel_ensemble.registry.model_registry import ModelRegistry
from extensions.ext_redis import redis_client

_LOCK_KEY = "model_net:k8s_refresh:lock"
_STATUS_KEY = "model_net:k8s_refresh:last_status"
_LOCK_TTL_SECONDS = 10 * 60


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _settings_from_config() -> K8sDiscoverySettings:
    kubeconfig_path = str(dify_config.MODEL_NET_K8S_KUBECONFIG_PATH or "").strip() or None
    return K8sDiscoverySettings(
        namespaces=parse_namespaces(dify_config.MODEL_NET_K8S_NAMESPACES),
        kubeconfig_path=kubeconfig_path,
        probe_timeout_seconds=float(dify_config.MODEL_NET_K8S_PROBE_TIMEOUT_SECONDS),
        route_default_scheme=str(dify_config.MODEL_NET_K8S_ROUTE_DEFAULT_SCHEME),
        default_backend=str(dify_config.MODEL_NET_K8S_DEFAULT_BACKEND),
        request_timeout_ms=int(dify_config.MODEL_NET_K8S_REQUEST_TIMEOUT_MS),
    )


def _json_safe(value: Any) -> Any:
    try:
        json.dumps(value)
        return value
    except TypeError:
        return str(value)


def _save_status(status: dict[str, Any]) -> None:
    try:
        redis_client.set(_STATUS_KEY, json.dumps(status, ensure_ascii=False, default=_json_safe))
    except Exception:
        # Status reporting must not make a successful registry refresh fail.
        return


def get_model_net_k8s_refresh_status() -> dict[str, Any]:
    try:
        raw = redis_client.get(_STATUS_KEY)
    except Exception:
        raw = None
    if not raw:
        return {
            "status": "never_run",
            "enabled": bool(dify_config.MODEL_NET_K8S_DISCOVERY_ENABLED),
            "updated_at": None,
        }
    if isinstance(raw, bytes):
        raw = raw.decode("utf-8")
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {
            "status": "status_unreadable",
            "enabled": bool(dify_config.MODEL_NET_K8S_DISCOVERY_ENABLED),
            "updated_at": _now(),
        }


def _acquire_lock() -> str | None:
    token = str(uuid.uuid4())
    try:
        acquired = redis_client.set(_LOCK_KEY, token, nx=True, ex=_LOCK_TTL_SECONDS)
    except Exception:
        # Development fallback: keep the operation usable even if Redis is
        # unavailable. Production deployments should have Redis.
        return token
    return token if acquired else None


def _release_lock(token: str) -> None:
    try:
        current = redis_client.get(_LOCK_KEY)
        if isinstance(current, bytes):
            current = current.decode("utf-8")
        if current == token:
            redis_client.delete(_LOCK_KEY)
    except Exception:
        return


def _registry_path() -> Path:
    return Path(str(dify_config.MODEL_NET_REGISTRY_PATH))


def _render_registry_yaml(models: list[dict[str, Any]], generated_at: str) -> str:
    body = yaml.safe_dump({"models": models}, sort_keys=False, allow_unicode=True)
    return (
        "# ModelNet model registry - generated from Kubernetes Ingress discovery.\n"
        f"# Generated: {generated_at}\n"
        "# Do not edit by hand while MODEL_NET_K8S_DISCOVERY_ENABLED is true.\n"
        f"{body}"
    )


def _write_registry_file(models: list[dict[str, Any]], generated_at: str) -> None:
    path = _registry_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_name(f".{path.name}.tmp.{os.getpid()}")
    tmp_path.write_text(_render_registry_yaml(models, generated_at), encoding="utf-8")

    # Validate through the same registry loader before replacing the live
    # file. A bad backend default or inferred field should fail the refresh,
    # not corrupt the runtime registry file.
    ModelRegistry.for_testing(str(tmp_path))
    tmp_path.replace(path)
    ModelRegistry.reload()


def refresh_model_net_registry_from_k8s(*, triggered_by: str = "manual") -> dict[str, Any]:
    if not bool(dify_config.MODEL_NET_K8S_DISCOVERY_ENABLED):
        status = {
            "status": "disabled",
            "enabled": False,
            "triggered_by": triggered_by,
            "updated_at": _now(),
            "applied": False,
            "message": "MODEL_NET_K8S_DISCOVERY_ENABLED is false",
        }
        _save_status(status)
        return status

    token = _acquire_lock()
    if token is None:
        return {
            "status": "locked",
            "enabled": True,
            "triggered_by": triggered_by,
            "updated_at": _now(),
            "applied": False,
        }

    try:
        settings = _settings_from_config()
        discovery = discover_model_registry(settings)
        models = discovery["models"]
        applied = False
        status_name = "success"
        message = ""

        if models:
            _write_registry_file(models, discovery["generated_at"])
            applied = True
        else:
            status_name = "no_healthy_models"
            message = "No discovered route answered /v1/models; existing registry was left unchanged."

        status = {
            "status": status_name,
            "enabled": True,
            "triggered_by": triggered_by,
            "updated_at": _now(),
            "generated_at": discovery["generated_at"],
            "applied": applied,
            "message": message,
            "registry_path": str(_registry_path()),
            "model_count": len(models),
            "candidate_count": len(discovery["candidates"]),
            "skipped_count": len(discovery["skipped"]),
            "models": [
                {
                    "id": item.get("id"),
                    "backend": item.get("backend"),
                    "model_name": item.get("model_name"),
                }
                for item in models
            ],
            "candidates": discovery["candidates"],
            "skipped": discovery["skipped"],
        }
        _save_status(status)
        return status
    except Exception as exc:
        status = {
            "status": "failed",
            "enabled": True,
            "triggered_by": triggered_by,
            "updated_at": _now(),
            "applied": False,
            "error": str(exc),
        }
        _save_status(status)
        return status
    finally:
        _release_lock(token)
