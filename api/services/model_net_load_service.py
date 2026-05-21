"""ModelNet load status and load-aware routing service."""

from __future__ import annotations

import math
from datetime import UTC, datetime
from operator import itemgetter
from typing import Any, TypedDict

from configs import dify_config
from core.helper import ssrf_proxy
from core.workflow.nodes.parallel_ensemble import backends as _modelnet_backends  # noqa: F401
from core.workflow.nodes.parallel_ensemble.registry import ModelRegistry


class PrometheusSample(TypedDict):
    value: float | None
    observed_at: str | None


_METRIC_TO_QUERY_CONFIG: dict[str, str] = {
    "healthy": "MODEL_NET_PROMETHEUS_HEALTH_QUERY",
    "qps": "MODEL_NET_PROMETHEUS_QPS_QUERY",
    "p95_latency_ms": "MODEL_NET_PROMETHEUS_P95_LATENCY_QUERY",
    "queue_depth": "MODEL_NET_PROMETHEUS_QUEUE_DEPTH_QUERY",
    "gpu_utilization": "MODEL_NET_PROMETHEUS_GPU_UTILIZATION_QUERY",
    "gpu_memory_used_ratio": "MODEL_NET_PROMETHEUS_GPU_MEMORY_USED_RATIO_QUERY",
    "error_rate": "MODEL_NET_PROMETHEUS_ERROR_RATE_QUERY",
}

_PENALTY_WEIGHTS = {
    "p95_latency_ms": 0.35,
    "queue_depth": 0.20,
    "gpu_utilization": 0.15,
    "gpu_memory_used_ratio": 0.15,
    "error_rate": 0.15,
}


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _to_float(value: object) -> float | None:
    try:
        number = float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None
    if not math.isfinite(number):
        return None
    return number


def _timestamp_to_iso(value: object) -> str | None:
    timestamp = _to_float(value)
    if timestamp is None:
        return None
    return datetime.fromtimestamp(timestamp, tz=UTC).isoformat()


def _sample_age_seconds(observed_at: str | None) -> float | None:
    if not observed_at:
        return None
    try:
        observed = datetime.fromisoformat(observed_at)
    except ValueError:
        return None
    if observed.tzinfo is None:
        observed = observed.replace(tzinfo=UTC)
    return max(0.0, (datetime.now(UTC) - observed).total_seconds())


def _prometheus_url() -> str:
    return str(dify_config.MODEL_NET_PROMETHEUS_URL or "").strip().rstrip("/")


def _prometheus_enabled() -> bool:
    return bool(_prometheus_url())


def _configured_metric_names() -> list[str]:
    return [
        metric_name
        for metric_name, config_name in _METRIC_TO_QUERY_CONFIG.items()
        if str(getattr(dify_config, config_name, "") or "").strip()
    ]


def _query_prometheus(query: str) -> PrometheusSample | None:
    base_url = _prometheus_url()
    if not base_url:
        return None

    response = ssrf_proxy.get(
        f"{base_url}/api/v1/query",
        max_retries=0,
        params={"query": query},
        timeout=float(dify_config.MODEL_NET_PROMETHEUS_TIMEOUT_SECONDS),
    )
    response.raise_for_status()
    payload = response.json()
    if payload.get("status") != "success":
        raise RuntimeError(str(payload.get("error") or "Prometheus query failed"))

    data = payload.get("data")
    result = data.get("result") if isinstance(data, dict) else None
    if not isinstance(result, list) or not result:
        return None

    first = result[0]
    if not isinstance(first, dict):
        return None
    sample = first.get("value")
    if not isinstance(sample, list) or len(sample) < 2:
        return None

    return {
        "value": _to_float(sample[1]),
        "observed_at": _timestamp_to_iso(sample[0]),
    }


def _render_query(template: str, *, alias: str, model_name: str) -> str:
    return template.format(alias=alias, model_name=model_name)


def _read_metric(
    metric_name: str,
    *,
    alias: str,
    model_name: str,
    errors: list[dict[str, str]],
) -> PrometheusSample | None:
    config_name = _METRIC_TO_QUERY_CONFIG[metric_name]
    template = str(getattr(dify_config, config_name, "") or "").strip()
    if not template:
        return None
    try:
        query = _render_query(template, alias=alias, model_name=model_name)
    except Exception as exc:
        errors.append({"metric": metric_name, "error": f"invalid query template: {exc}"})
        return None

    try:
        return _query_prometheus(query)
    except Exception as exc:
        errors.append({"metric": metric_name, "error": str(exc)})
        return None


def _as_ratio(value: float | None) -> float | None:
    if value is None:
        return None
    if value > 1.0:
        return max(0.0, min(value / 100.0, 1.0))
    return max(0.0, min(value, 1.0))


def _bounded_penalty(metric_name: str, value: float | None) -> float:
    if value is None:
        return 0.0

    if metric_name == "p95_latency_ms":
        return max(0.0, min(value / 30000.0, 1.0))
    if metric_name == "queue_depth":
        return max(0.0, min(value / 64.0, 1.0))
    if metric_name in {"gpu_utilization", "gpu_memory_used_ratio", "error_rate"}:
        return _as_ratio(value) or 0.0
    return 0.0


def _build_score(*, healthy: bool, weight: float, metrics: dict[str, float | None]) -> float:
    if not healthy:
        return 0.0

    penalty = 0.0
    for metric_name, penalty_weight in _PENALTY_WEIGHTS.items():
        penalty += penalty_weight * _bounded_penalty(metric_name, metrics.get(metric_name))

    return round(max(0.0, weight * (1.0 - min(penalty, 1.0))), 6)


def _status_for_model(info: dict[str, Any], *, registry: ModelRegistry) -> dict[str, Any]:
    alias = str(info["id"])
    model_name = str(info["model_name"])
    errors: list[dict[str, str]] = []
    samples: dict[str, PrometheusSample | None] = {}

    for metric_name in _METRIC_TO_QUERY_CONFIG:
        samples[metric_name] = _read_metric(metric_name, alias=alias, model_name=model_name, errors=errors)

    health_sample = samples["healthy"]
    health_value = health_sample["value"] if health_sample else None
    healthy = True if health_value is None else health_value > 0.0

    metrics = {
        "qps": samples["qps"]["value"] if samples["qps"] else None,
        "p95_latency_ms": samples["p95_latency_ms"]["value"] if samples["p95_latency_ms"] else None,
        "queue_depth": samples["queue_depth"]["value"] if samples["queue_depth"] else None,
        "gpu_utilization": _as_ratio(samples["gpu_utilization"]["value"] if samples["gpu_utilization"] else None),
        "gpu_memory_used_ratio": _as_ratio(
            samples["gpu_memory_used_ratio"]["value"] if samples["gpu_memory_used_ratio"] else None
        ),
        "error_rate": _as_ratio(samples["error_rate"]["value"] if samples["error_rate"] else None),
    }
    observed_values = [sample["observed_at"] for sample in samples.values() if sample and sample["observed_at"]]
    last_seen_at = max(observed_values) if observed_values else None
    stale = False
    age = _sample_age_seconds(last_seen_at)
    if age is not None and age > int(dify_config.MODEL_NET_LOAD_METRIC_STALE_SECONDS):
        stale = True

    spec = registry.get(alias)
    score = _build_score(healthy=healthy and not stale, weight=float(spec.weight), metrics=metrics)
    reasons: list[str] = []
    if not _prometheus_enabled():
        reasons.append("prometheus_not_configured")
    if _prometheus_enabled() and not _configured_metric_names():
        reasons.append("prometheus_queries_not_configured")
    if health_value is None:
        reasons.append("health_metric_missing")
    if not healthy:
        reasons.append("unhealthy")
    if stale:
        reasons.append("metrics_stale")
    if errors:
        reasons.append("metric_query_errors")

    return {
        "id": alias,
        "backend": info["backend"],
        "model_name": model_name,
        "capabilities": info.get("capabilities", []),
        "metadata": info.get("metadata", {}),
        "weight": float(spec.weight),
        "load": {
            "healthy": healthy and not stale,
            "qps": metrics["qps"],
            "p95_latency_ms": metrics["p95_latency_ms"],
            "queue_depth": metrics["queue_depth"],
            "gpu_utilization": metrics["gpu_utilization"],
            "gpu_memory_used_ratio": metrics["gpu_memory_used_ratio"],
            "error_rate": metrics["error_rate"],
            "last_seen_at": last_seen_at,
            "stale": stale,
        },
        "score": score,
        "reasons": reasons,
        "errors": errors,
    }


def _normalize_string_list(value: object) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list):
        return []
    out: list[str] = []
    seen: set[str] = set()
    for item in value:
        text = str(item).strip()
        if not text or text in seen:
            continue
        seen.add(text)
        out.append(text)
    return out


def _filter_models(
    models: list[dict[str, Any]],
    *,
    candidate_aliases: list[str],
    required_capabilities: list[str],
) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    errors: list[dict[str, str]] = []
    candidate_set = set(candidate_aliases)
    required_set = set(required_capabilities)
    known_ids = {str(item["id"]) for item in models}

    for alias in candidate_aliases:
        if alias not in known_ids:
            errors.append({"alias": alias, "error": "unknown_model_alias"})

    filtered: list[dict[str, Any]] = []
    for item in models:
        alias = str(item["id"])
        if candidate_set and alias not in candidate_set:
            continue
        capabilities = {str(capability) for capability in item.get("capabilities", [])}
        missing = sorted(required_set - capabilities)
        item = {**item, "eligible": not missing, "missing_capabilities": missing}
        filtered.append(item)

    return filtered, errors


def get_model_net_load_status(
    *,
    candidate_aliases: list[str] | None = None,
    required_capabilities: list[str] | None = None,
) -> dict[str, Any]:
    registry = ModelRegistry.instance()
    aliases = [dict(item) for item in registry.list_aliases()]
    models, filter_errors = _filter_models(
        aliases,
        candidate_aliases=candidate_aliases or [],
        required_capabilities=required_capabilities or [],
    )
    statuses = [_status_for_model(item, registry=registry) for item in models]
    status_by_id = {item["id"]: item for item in statuses}

    for item in models:
        status_by_id[item["id"]]["eligible"] = item["eligible"]
        status_by_id[item["id"]]["missing_capabilities"] = item["missing_capabilities"]

    return {
        "updated_at": _now(),
        "source": {
            "prometheus_configured": _prometheus_enabled(),
            "status": "prometheus" if _prometheus_enabled() else "static_fallback",
            "configured_metrics": _configured_metric_names(),
        },
        "models": statuses,
        "errors": filter_errors,
    }


def route_model_from_load(
    *,
    candidate_aliases: list[str] | None = None,
    required_capabilities: list[str] | None = None,
    policy: dict[str, Any] | None = None,
) -> dict[str, Any]:
    policy = policy or {}
    top_k = int(policy.get("top_k") or dify_config.MODEL_NET_ROUTE_TOP_K)
    include_unhealthy = bool(policy.get("include_unhealthy", False))
    top_k = max(1, top_k)

    status = get_model_net_load_status(
        candidate_aliases=candidate_aliases,
        required_capabilities=required_capabilities,
    )
    ranked = sorted(status["models"], key=itemgetter("score", "weight"), reverse=True)
    eligible = [item for item in ranked if item.get("eligible", True)]
    selectable = [
        item for item in eligible if include_unhealthy or item.get("load", {}).get("healthy") is True
    ]
    selected = selectable[:top_k]
    fallback_reason = None
    if not selected:
        if not ranked:
            fallback_reason = "no_candidate_models"
        elif not eligible:
            fallback_reason = "no_eligible_models"
        else:
            fallback_reason = "no_healthy_eligible_models"

    return {
        "updated_at": status["updated_at"],
        "source": status["source"],
        "selected_alias": selected[0]["id"] if selected else None,
        "selected_aliases": [item["id"] for item in selected],
        "selected": selected[0] if selected else None,
        "ranked_candidates": ranked,
        "fallback_reason": fallback_reason,
        "errors": status["errors"],
    }


def route_model_from_payload(payload: dict[str, Any] | None) -> dict[str, Any]:
    payload = payload or {}
    return route_model_from_load(
        candidate_aliases=_normalize_string_list(payload.get("candidate_aliases")),
        required_capabilities=_normalize_string_list(payload.get("required_capabilities")),
        policy=payload.get("policy") if isinstance(payload.get("policy"), dict) else {},
    )
