"""Read-only Kubernetes data plane snapshot for ModelNet.

This service does not mutate Kubernetes resources. It normalizes the
runtime state Dify needs to display and later consume for load-aware
model routing: resources, metrics-server samples, Prometheus samples,
OpenAI-compatible probes, and vLLM metrics.
"""

from __future__ import annotations

import json
import math
import os
import re
from collections import defaultdict
from datetime import UTC, datetime
from operator import itemgetter
from pathlib import Path
from typing import Any
from urllib.parse import quote, urlencode, urlunparse

import httpx

from configs import dify_config
from core.helper import ssrf_proxy
from core.workflow.nodes.parallel_ensemble.registry.k8s_discovery import (
    KubernetesAuth,
    _build_probe_url,
    _extract_first_model_id,
    _load_in_cluster_auth,
    _load_kubeconfig,
    _route_scheme,
    parse_namespaces,
)
from extensions.ext_redis import redis_client

_CACHE_KEY = "model_net:k8s_data:last_snapshot"

_PROMETHEUS_QUERIES: dict[str, str] = {
    "dcgm_gpu_utilization": "DCGM_FI_DEV_GPU_UTIL",
    "dcgm_fb_used_mb": "DCGM_FI_DEV_FB_USED",
    "dcgm_fb_free_mb": "DCGM_FI_DEV_FB_FREE",
    "dcgm_gpu_temperature_c": "DCGM_FI_DEV_GPU_TEMP",
    "dcgm_power_usage_watts": "DCGM_FI_DEV_POWER_USAGE",
    "jetson_temperature_c": 'temperature_C{job="jetson-node-exporter"}',
    "jetson_ram_kb": 'ram_kB{job="jetson-node-exporter"}',
}

_VLLM_GAUGE_NAMES = {
    "vllm:num_requests_running": "num_requests_running",
    "vllm:num_requests_waiting": "num_requests_waiting",
    "vllm:kv_cache_usage_perc": "kv_cache_usage_perc",
}

_VLLM_COUNTER_NAMES = {
    "vllm:request_success_total": "request_success_total",
    "vllm:prompt_tokens_total": "prompt_tokens_total",
    "vllm:generation_tokens_total": "generation_tokens_total",
}

_VLLM_HISTOGRAMS = {
    "vllm:time_to_first_token_seconds_bucket": "time_to_first_token_p95_seconds",
    "vllm:e2e_request_latency_seconds_bucket": "e2e_request_latency_p95_seconds",
    "vllm:request_queue_time_seconds_bucket": "request_queue_time_p95_seconds",
}


class KubernetesApiClient:
    """Tiny Kubernetes JSON client using the configured kube credentials."""

    def __init__(self, *, kubeconfig_path: str | None, timeout_seconds: float):
        self._auth = _load_kubeconfig(kubeconfig_path) if kubeconfig_path else _load_in_cluster_auth()
        self._timeout_seconds = timeout_seconds

    @property
    def auth(self) -> KubernetesAuth:
        return self._auth

    def get_json(self, path: str) -> dict[str, Any]:
        headers = {"Accept": "application/json"}
        if self._auth.token:
            headers["Authorization"] = f"Bearer {self._auth.token}"
        with httpx.Client(timeout=self._timeout_seconds, verify=self._auth.verify) as client:
            response = client.get(f"{self._auth.server}{path}", headers=headers)
        response.raise_for_status()
        payload = response.json()
        return payload if isinstance(payload, dict) else {}


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _items(payload: dict[str, Any]) -> list[dict[str, Any]]:
    items = payload.get("items")
    return [item for item in items if isinstance(item, dict)] if isinstance(items, list) else []


def _metadata(item: dict[str, Any]) -> dict[str, Any]:
    value = item.get("metadata")
    return value if isinstance(value, dict) else {}


def _name(item: dict[str, Any]) -> str:
    return str(_metadata(item).get("name") or "")


def _namespace(item: dict[str, Any]) -> str:
    return str(_metadata(item).get("namespace") or "")


def _labels(item: dict[str, Any]) -> dict[str, str]:
    value = _metadata(item).get("labels")
    if not isinstance(value, dict):
        return {}
    return {str(key): str(item) for key, item in value.items() if item is not None}


def _spec(item: dict[str, Any]) -> dict[str, Any]:
    value = item.get("spec")
    return value if isinstance(value, dict) else {}


def _status(item: dict[str, Any]) -> dict[str, Any]:
    value = item.get("status")
    return value if isinstance(value, dict) else {}


def _parse_cpu_cores(value: object) -> float | None:
    text = str(value or "").strip()
    if not text:
        return None
    try:
        if text.endswith("n"):
            return float(text[:-1]) / 1_000_000_000
        if text.endswith("u"):
            return float(text[:-1]) / 1_000_000
        if text.endswith("m"):
            return float(text[:-1]) / 1_000
        return float(text)
    except ValueError:
        return None


def _parse_memory_bytes(value: object) -> int | None:
    text = str(value or "").strip()
    if not text:
        return None
    units = {
        "Ki": 1024,
        "Mi": 1024**2,
        "Gi": 1024**3,
        "Ti": 1024**4,
        "K": 1000,
        "M": 1000**2,
        "G": 1000**3,
        "T": 1000**4,
    }
    for suffix, multiplier in units.items():
        if text.endswith(suffix):
            try:
                return int(float(text[: -len(suffix)]) * multiplier)
            except ValueError:
                return None
    try:
        return int(float(text))
    except ValueError:
        return None


def _float(value: object) -> float | None:
    try:
        number = float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def _labels_match(selector: dict[str, Any], labels: dict[str, str]) -> bool:
    if not selector:
        return False
    return all(labels.get(str(key)) == str(value) for key, value in selector.items())


def _node_ready(node: dict[str, Any]) -> bool:
    for condition in _status(node).get("conditions", []) or []:
        if not isinstance(condition, dict):
            continue
        if condition.get("type") == "Ready":
            return condition.get("status") == "True"
    return False


def _pod_ready(pod: dict[str, Any]) -> bool:
    for condition in _status(pod).get("conditions", []) or []:
        if not isinstance(condition, dict):
            continue
        if condition.get("type") == "Ready":
            return condition.get("status") == "True"
    return False


def _container_restarts(pod: dict[str, Any]) -> int:
    total = 0
    for item in _status(pod).get("containerStatuses", []) or []:
        if isinstance(item, dict):
            total += int(item.get("restartCount") or 0)
    return total


def _container_ready_count(pod: dict[str, Any]) -> int:
    total = 0
    for item in _status(pod).get("containerStatuses", []) or []:
        if isinstance(item, dict) and item.get("ready") is True:
            total += 1
    return total


def _metric_timestamp(payload: dict[str, Any]) -> str | None:
    timestamp = _metadata(payload).get("creationTimestamp")
    return str(timestamp) if timestamp else None


def _node_metrics_by_name(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for item in _items(payload):
        usage = item.get("usage") if isinstance(item.get("usage"), dict) else {}
        out[_name(item)] = {
            "timestamp": item.get("timestamp"),
            "window": item.get("window"),
            "cpu_cores": _parse_cpu_cores(usage.get("cpu")),
            "memory_bytes": _parse_memory_bytes(usage.get("memory")),
        }
    return out


def _pod_metrics_by_name(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for item in _items(payload):
        containers = []
        for container in item.get("containers", []) or []:
            if not isinstance(container, dict):
                continue
            usage = container.get("usage") if isinstance(container.get("usage"), dict) else {}
            containers.append(
                {
                    "name": container.get("name"),
                    "cpu_cores": _parse_cpu_cores(usage.get("cpu")),
                    "memory_bytes": _parse_memory_bytes(usage.get("memory")),
                }
            )
        out[_name(item)] = {
            "timestamp": item.get("timestamp"),
            "window": item.get("window"),
            "containers": containers,
        }
    return out


def _source_status(
    name: str,
    *,
    status: str,
    updated_at: str | None = None,
    error: str | None = None,
) -> dict[str, Any]:
    result: dict[str, Any] = {"name": name, "status": status, "updated_at": updated_at}
    if error:
        result["error"] = error
    return result


def _safe_get(client: KubernetesApiClient, path: str, errors: list[dict[str, str]]) -> dict[str, Any]:
    try:
        return client.get_json(path)
    except Exception as exc:
        errors.append({"path": path, "error": str(exc)})
        return {}


def _prometheus_path(query: str) -> str:
    namespace = quote(str(dify_config.MODEL_NET_K8S_DATA_MONITORING_NAMESPACE), safe="")
    service = str(dify_config.MODEL_NET_K8S_DATA_PROMETHEUS_SERVICE_PROXY).strip()
    return f"/api/v1/namespaces/{namespace}/services/{service}/proxy/api/v1/query?{urlencode({'query': query})}"


def _kubeconfig_path_from_config() -> str | None:
    configured = str(dify_config.MODEL_NET_K8S_KUBECONFIG_PATH or "").strip()
    if configured:
        return configured
    if os.getenv("KUBERNETES_SERVICE_HOST"):
        return None
    default_path = Path.home() / ".kube" / "config"
    return str(default_path) if default_path.exists() else None


def _query_prometheus(client: KubernetesApiClient, query: str) -> list[dict[str, Any]]:
    payload = client.get_json(_prometheus_path(query))
    if payload.get("status") != "success":
        raise RuntimeError(str(payload.get("error") or "Prometheus query failed"))
    data = payload.get("data") if isinstance(payload.get("data"), dict) else {}
    result = data.get("result") if isinstance(data, dict) else []
    return [item for item in result if isinstance(item, dict)] if isinstance(result, list) else []


def _sample_value(sample: dict[str, Any]) -> float | None:
    value = sample.get("value")
    if not isinstance(value, list) or len(value) < 2:
        return None
    return _float(value[1])


def _sample_time(sample: dict[str, Any]) -> str | None:
    value = sample.get("value")
    if not isinstance(value, list) or not value:
        return None
    timestamp = _float(value[0])
    if timestamp is None:
        return None
    return datetime.fromtimestamp(timestamp, tz=UTC).isoformat()


def _collect_prometheus(client: KubernetesApiClient, errors: list[dict[str, str]]) -> dict[str, Any]:
    samples: dict[str, list[dict[str, Any]]] = {}
    statuses: list[dict[str, Any]] = []
    for name, query in _PROMETHEUS_QUERIES.items():
        try:
            values = _query_prometheus(client, query)
            samples[name] = values
            observed_at = next((_sample_time(item) for item in values if _sample_time(item)), None)
            statuses.append(_source_status(f"prometheus:{name}", status="available", updated_at=observed_at))
        except Exception as exc:
            samples[name] = []
            errors.append({"source": f"prometheus:{name}", "error": str(exc)})
            statuses.append(_source_status(f"prometheus:{name}", status="unavailable", error=str(exc)))
    return {"samples": samples, "statuses": statuses}


def _node_prometheus_summary(samples: dict[str, list[dict[str, Any]]]) -> dict[str, dict[str, Any]]:
    nodes: dict[str, dict[str, Any]] = defaultdict(lambda: {"gpu": {"devices": []}, "jetson": {}})
    gpu_by_node_device: dict[tuple[str, str], dict[str, Any]] = {}

    gpu_field_map = {
        "dcgm_gpu_utilization": "utilization_percent",
        "dcgm_fb_used_mb": "memory_used_mb",
        "dcgm_fb_free_mb": "memory_free_mb",
        "dcgm_gpu_temperature_c": "temperature_c",
        "dcgm_power_usage_watts": "power_watts",
    }
    for sample_key, field_name in gpu_field_map.items():
        for sample in samples.get(sample_key, []):
            metric = sample.get("metric") if isinstance(sample.get("metric"), dict) else {}
            node_name = str(metric.get("instance") or "")
            device = str(metric.get("device") or metric.get("gpu") or "gpu")
            if not node_name:
                continue
            entry = gpu_by_node_device.setdefault(
                (node_name, device),
                {
                    "device": device,
                    "gpu": metric.get("gpu"),
                    "model_name": metric.get("modelName"),
                    "uuid": metric.get("UUID"),
                },
            )
            entry[field_name] = _sample_value(sample)
            entry["observed_at"] = _sample_time(sample)

    for (node_name, _device), entry in gpu_by_node_device.items():
        nodes[node_name]["gpu"]["devices"].append(entry)

    for sample in samples.get("jetson_temperature_c", []):
        metric = sample.get("metric") if isinstance(sample.get("metric"), dict) else {}
        node_name = str(metric.get("instance") or "")
        statistic = str(metric.get("statistic") or "")
        if node_name and statistic:
            jetson = nodes[node_name].setdefault("jetson", {})
            jetson.setdefault("temperatures_c", {})[statistic] = _sample_value(sample)
            nodes[node_name]["jetson"]["observed_at"] = _sample_time(sample)

    for sample in samples.get("jetson_ram_kb", []):
        metric = sample.get("metric") if isinstance(sample.get("metric"), dict) else {}
        node_name = str(metric.get("instance") or "")
        statistic = str(metric.get("statistic") or "")
        if node_name and statistic:
            nodes[node_name].setdefault("jetson", {}).setdefault("ram_kb", {})[statistic] = _sample_value(sample)
            nodes[node_name]["jetson"]["observed_at"] = _sample_time(sample)

    return dict(nodes)


def _ingress_routes(ingresses: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    by_service: dict[str, list[dict[str, Any]]] = defaultdict(list)
    default_scheme = str(dify_config.MODEL_NET_K8S_ROUTE_DEFAULT_SCHEME)
    for ingress in ingresses:
        namespace = _namespace(ingress)
        ingress_name = _name(ingress)
        spec = _spec(ingress)
        tls_hosts: set[str] = set()
        for tls in spec.get("tls", []) or []:
            if isinstance(tls, dict) and isinstance(tls.get("hosts"), list):
                tls_hosts.update(str(host) for host in tls["hosts"] if host)
        for rule in spec.get("rules", []) or []:
            if not isinstance(rule, dict):
                continue
            host = str(rule.get("host") or "")
            http = rule.get("http") if isinstance(rule.get("http"), dict) else {}
            paths = http.get("paths") if isinstance(http.get("paths"), list) else []
            scheme = _route_scheme(host, tls_hosts, default_scheme)
            for path_item in paths:
                if not isinstance(path_item, dict):
                    continue
                backend = path_item.get("backend") if isinstance(path_item.get("backend"), dict) else {}
                service = backend.get("service") if isinstance(backend.get("service"), dict) else {}
                service_name = str(service.get("name") or "")
                if not service_name:
                    continue
                path = str(path_item.get("path") or "/")
                clean_path = path if path.startswith("/") else f"/{path}"
                if clean_path != "/":
                    clean_path = clean_path.rstrip("/")
                base_url = urlunparse((scheme, host, "" if clean_path == "/" else clean_path, "", "", ""))
                by_service[service_name].append(
                    {
                        "namespace": namespace,
                        "ingress": ingress_name,
                        "host": host,
                        "path": path,
                        "base_url": base_url,
                    }
                )
    return by_service


def _endpoint_summary(endpoint_slices: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    by_service: dict[str, dict[str, Any]] = defaultdict(lambda: {"total": 0, "ready": 0, "addresses": []})
    for item in endpoint_slices:
        service_name = _labels(item).get("kubernetes.io/service-name", "")
        if not service_name:
            continue
        for endpoint in item.get("endpoints", []) or []:
            if not isinstance(endpoint, dict):
                continue
            conditions = endpoint.get("conditions") if isinstance(endpoint.get("conditions"), dict) else {}
            ready = conditions.get("ready") is not False
            addresses = [str(address) for address in endpoint.get("addresses", []) or []]
            by_service[service_name]["total"] += len(addresses) or 1
            if ready:
                by_service[service_name]["ready"] += len(addresses) or 1
            by_service[service_name]["addresses"].extend(addresses)
    return dict(by_service)


def _deployment_pods(deployment: dict[str, Any], pods: list[dict[str, Any]]) -> list[dict[str, Any]]:
    selector = _spec(deployment).get("selector")
    match_labels = selector.get("matchLabels") if isinstance(selector, dict) else {}
    if not isinstance(match_labels, dict):
        return []
    return [pod for pod in pods if _labels_match(match_labels, _labels(pod))]


def _service_pods(
    service: dict[str, Any],
    pods: list[dict[str, Any]],
    endpoint_addresses: list[str],
) -> list[dict[str, Any]]:
    selector = _spec(service).get("selector")
    if isinstance(selector, dict) and selector:
        matched = [pod for pod in pods if _labels_match(selector, _labels(pod))]
        if matched:
            return matched
    address_set = set(endpoint_addresses)
    return [pod for pod in pods if _status(pod).get("podIP") in address_set]


def _service_base_url(service: dict[str, Any], routes: list[dict[str, Any]]) -> tuple[str | None, str, list[str]]:
    if routes:
        return str(routes[0]["base_url"]), "ingress", []
    service_type = str(_spec(service).get("type") or "")
    if service_type != "NodePort":
        return None, service_type or "cluster_ip", ["no_public_route"]
    nodeport_host = str(dify_config.MODEL_NET_K8S_DATA_NODEPORT_HOST or "").strip()
    if not nodeport_host:
        return None, "nodeport", ["nodeport_host_missing"]
    for port in _spec(service).get("ports", []) or []:
        if isinstance(port, dict) and port.get("nodePort"):
            return f"http://{nodeport_host}:{port['nodePort']}", "nodeport", []
    return None, "nodeport", ["nodeport_missing"]


def _backend_for_model(namespace: str, pods: list[dict[str, Any]]) -> str:
    if namespace == "llama-cpp":
        return "llama_cpp"
    for pod in pods:
        for container in _spec(pod).get("containers", []) or []:
            if not isinstance(container, dict):
                continue
            image = str(container.get("image") or "").lower()
            if "llama-cpp" in image:
                return "llama_cpp"
            if "vllm" in image:
                return "vllm"
    return "vllm" if namespace == "inference" else "unknown"


def _model_name_for_service(service: dict[str, Any], pods: list[dict[str, Any]]) -> str:
    labels = _labels(service)
    for key in ("model_name", "k8s.kuboard.cn/model-name", "k8s.kuboard.cn/name"):
        if labels.get(key):
            return labels[key]
    for pod in pods:
        for container in _spec(pod).get("containers", []) or []:
            if isinstance(container, dict) and container.get("name"):
                return str(container["name"])
    return _name(service)


def _probe_openai(base_url: str | None) -> dict[str, Any]:
    if not base_url:
        return {"status": "skipped", "reason": "missing_base_url"}
    probe_url = _build_probe_url(base_url)
    if not probe_url:
        return {"status": "failed", "reason": "invalid_base_url"}
    try:
        response = ssrf_proxy.get(
            probe_url,
            max_retries=0,
            timeout=float(dify_config.MODEL_NET_K8S_DATA_PROBE_TIMEOUT_SECONDS),
        )
        status_code = int(getattr(response, "status_code", 0) or 0)
        payload = response.json()
        model_name = _extract_first_model_id(payload)
        return {
            "status": "available" if status_code // 100 == 2 else "unavailable",
            "status_code": status_code,
            "probe_url": probe_url,
            "model_name": model_name,
        }
    except Exception as exc:
        return {"status": "unavailable", "probe_url": probe_url, "error": str(exc)}


_METRIC_LINE_RE = re.compile(r"^([a-zA-Z_:][a-zA-Z0-9_:]*)(?:\{([^}]*)\})?\s+([-+0-9.eE]+)")


def _parse_label_block(raw: str | None) -> dict[str, str]:
    if not raw:
        return {}
    labels: dict[str, str] = {}
    for item in raw.split(","):
        if "=" not in item:
            continue
        key, value = item.split("=", 1)
        labels[key.strip()] = value.strip().strip('"')
    return labels


def _histogram_quantile(q: float, buckets: dict[float, float]) -> float | None:
    finite = sorted((le, value) for le, value in buckets.items() if math.isfinite(le))
    if not finite:
        return None
    total = finite[-1][1]
    if total <= 0:
        return None
    rank = q * total
    previous_le = 0.0
    previous_value = 0.0
    for le, value in finite:
        if value >= rank:
            bucket_count = value - previous_value
            if bucket_count <= 0:
                return le
            bucket_start_rank = previous_value
            fraction = max(0.0, min((rank - bucket_start_rank) / bucket_count, 1.0))
            return previous_le + (le - previous_le) * fraction
        previous_le = le
        previous_value = value
    return finite[-1][0]


def parse_vllm_metrics(text: str) -> dict[str, Any]:
    gauges: dict[str, float] = {}
    counters: dict[str, float] = defaultdict(float)
    histogram_buckets: dict[str, dict[float, float]] = defaultdict(lambda: defaultdict(float))

    for line in text.splitlines():
        if not line or line.startswith("#"):
            continue
        match = _METRIC_LINE_RE.match(line)
        if not match:
            continue
        metric_name, raw_labels, raw_value = match.groups()
        value = _float(raw_value)
        if value is None:
            continue
        if metric_name in _VLLM_GAUGE_NAMES:
            gauges[_VLLM_GAUGE_NAMES[metric_name]] = value
        elif metric_name in _VLLM_COUNTER_NAMES:
            counters[_VLLM_COUNTER_NAMES[metric_name]] += value
        elif metric_name in _VLLM_HISTOGRAMS:
            labels = _parse_label_block(raw_labels)
            le = labels.get("le")
            if le == "+Inf":
                continue
            le_value = _float(le)
            if le_value is not None:
                histogram_buckets[_VLLM_HISTOGRAMS[metric_name]][le_value] += value

    histograms = {
        output_name: _histogram_quantile(0.95, buckets)
        for output_name, buckets in histogram_buckets.items()
    }
    return {**gauges, **dict(counters), **histograms}


def _fetch_vllm_metrics(base_url: str | None) -> dict[str, Any]:
    if not base_url:
        return {"status": "skipped", "reason": "missing_base_url"}
    metrics_url = base_url.rstrip("/") + "/metrics"
    try:
        response = ssrf_proxy.get(
            metrics_url,
            max_retries=0,
            timeout=float(dify_config.MODEL_NET_K8S_DATA_VLLM_METRICS_TIMEOUT_SECONDS),
        )
        status_code = int(getattr(response, "status_code", 0) or 0)
        if status_code // 100 != 2:
            return {"status": "unavailable", "status_code": status_code, "metrics_url": metrics_url}
        return {"status": "available", "metrics_url": metrics_url, "metrics": parse_vllm_metrics(response.text)}
    except Exception as exc:
        return {"status": "unavailable", "metrics_url": metrics_url, "error": str(exc)}


def _events_for_objects(events: list[dict[str, Any]], object_names: set[str]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for event in events:
        involved = event.get("involvedObject") if isinstance(event.get("involvedObject"), dict) else {}
        if str(involved.get("name") or "") not in object_names:
            continue
        out.append(
            {
                "type": event.get("type"),
                "reason": event.get("reason"),
                "message": event.get("message"),
                "last_timestamp": event.get("lastTimestamp") or event.get("eventTime"),
                "object": {
                    "kind": involved.get("kind"),
                    "name": involved.get("name"),
                },
            }
        )
    return out


def _model_skip_reasons(
    *,
    endpoint_ready_count: int,
    pods: list[dict[str, Any]],
    deployment: dict[str, Any] | None,
    probe: dict[str, Any],
    route_reasons: list[str],
    events: list[dict[str, Any]],
) -> list[str]:
    reasons = list(route_reasons)
    if endpoint_ready_count <= 0:
        reasons.append("no_ready_endpoint")
    if not pods:
        reasons.append("no_pod")
    elif not any(_status(pod).get("phase") == "Running" and _pod_ready(pod) for pod in pods):
        reasons.append("no_running_ready_pod")
    if deployment and int(_status(deployment).get("readyReplicas") or 0) <= 0:
        reasons.append("no_ready_replicas")
    if probe.get("status") == "unavailable":
        status_code = probe.get("status_code")
        reasons.append(f"probe_failed_{status_code}" if status_code else "probe_failed")
    for event in events:
        reason = str(event.get("reason") or "")
        if reason in {"BackOff", "FailedScheduling", "Unhealthy", "Failed"}:
            reasons.append(f"event_{reason}")
    return sorted(set(reasons))


def _build_node_snapshots(
    nodes: list[dict[str, Any]],
    node_metrics: dict[str, dict[str, Any]],
    prometheus_by_node: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    snapshots = []
    for node in nodes:
        node_name = _name(node)
        labels = _labels(node)
        snapshots.append(
            {
                "name": node_name,
                "ready": _node_ready(node),
                "schedulable": not bool(_spec(node).get("unschedulable")),
                "labels": labels,
                "internal_ip": next(
                    (
                        address.get("address")
                        for address in _status(node).get("addresses", []) or []
                        if isinstance(address, dict) and address.get("type") == "InternalIP"
                    ),
                    None,
                ),
                "device_type": labels.get("device-type") or ("pc-gpu" if node_name.startswith("pc-") else "unknown"),
                "metrics": node_metrics.get(node_name, {}),
                "prometheus": prometheus_by_node.get(node_name, {}),
            }
        )
    return sorted(snapshots, key=itemgetter("name"))


def _build_model_snapshots(
    *,
    namespaces: tuple[str, ...],
    resources: dict[str, dict[str, list[dict[str, Any]]]],
    pod_metrics: dict[str, dict[str, dict[str, Any]]],
    events_by_namespace: dict[str, list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    models: list[dict[str, Any]] = []
    probe_enabled = bool(dify_config.MODEL_NET_K8S_DATA_PROBE_ENABLED)
    vllm_metrics_enabled = bool(dify_config.MODEL_NET_K8S_DATA_VLLM_METRICS_ENABLED)

    for namespace in namespaces:
        data = resources.get(namespace, {})
        pods = data.get("pods", [])
        deployments = {_name(item): item for item in data.get("deployments", [])}
        routes_by_service = _ingress_routes(data.get("ingresses", []))
        endpoints_by_service = _endpoint_summary(data.get("endpoint_slices", []))
        events = events_by_namespace.get(namespace, [])

        for service in data.get("services", []):
            service_name = _name(service)
            endpoints = endpoints_by_service.get(service_name, {"ready": 0, "total": 0, "addresses": []})
            service_pods = _service_pods(service, pods, list(endpoints.get("addresses") or []))
            deployment = deployments.get(service_name)
            if not service_pods and deployment:
                service_pods = _deployment_pods(deployment, pods)
            base_url, exposure, route_reasons = _service_base_url(service, routes_by_service.get(service_name, []))
            backend = _backend_for_model(namespace, service_pods)
            endpoint_ready_count = int(endpoints.get("ready") or 0)
            if probe_enabled and endpoint_ready_count > 0:
                probe = _probe_openai(base_url)
            elif probe_enabled:
                probe = {"status": "skipped", "reason": "no_ready_endpoint"}
            else:
                probe = {"status": "disabled"}
            model_name = str(probe.get("model_name") or _model_name_for_service(service, service_pods))
            object_names = {service_name}
            if deployment:
                object_names.add(_name(deployment))
            object_names.update(_name(pod) for pod in service_pods)
            model_events = _events_for_objects(events, object_names)
            skip_reasons = _model_skip_reasons(
                endpoint_ready_count=endpoint_ready_count,
                pods=service_pods,
                deployment=deployment,
                probe=probe,
                route_reasons=route_reasons,
                events=model_events,
            )
            vllm_metrics = (
                _fetch_vllm_metrics(base_url)
                if vllm_metrics_enabled
                and backend == "vllm"
                and endpoint_ready_count > 0
                and probe.get("status") != "unavailable"
                else {"status": "skipped"}
            )

            models.append(
                {
                    "id": f"{namespace}/{service_name}",
                    "namespace": namespace,
                    "service": service_name,
                    "backend": backend,
                    "model_name": model_name,
                    "base_url": base_url,
                    "exposure": exposure,
                    "routes": routes_by_service.get(service_name, []),
                    "endpoints": endpoints,
                    "deployment": {
                        "name": _name(deployment) if deployment else None,
                        "ready_replicas": int(_status(deployment or {}).get("readyReplicas") or 0),
                        "replicas": int(_status(deployment or {}).get("replicas") or 0),
                    },
                    "pods": [
                        {
                            "name": _name(pod),
                            "phase": _status(pod).get("phase"),
                            "ready": _pod_ready(pod),
                            "container_ready_count": _container_ready_count(pod),
                            "restart_count": _container_restarts(pod),
                            "node": _spec(pod).get("nodeName"),
                            "pod_ip": _status(pod).get("podIP"),
                            "metrics": pod_metrics.get(namespace, {}).get(_name(pod), {}),
                        }
                        for pod in service_pods
                    ],
                    "probe": probe,
                    "vllm_metrics": vllm_metrics,
                    "events": model_events[: int(dify_config.MODEL_NET_K8S_DATA_EVENT_LIMIT)],
                    "route_status": {
                        "routable": not skip_reasons,
                        "skip_reasons": skip_reasons,
                    },
                }
            )
    return sorted(models, key=itemgetter("id"))


def _collect_resources(
    client: KubernetesApiClient,
    namespaces: tuple[str, ...],
    errors: list[dict[str, str]],
) -> dict[str, Any]:
    resources: dict[str, dict[str, list[dict[str, Any]]]] = {}
    pod_metrics: dict[str, dict[str, dict[str, Any]]] = {}
    events: dict[str, list[dict[str, Any]]] = {}
    nodes = _items(_safe_get(client, "/api/v1/nodes", errors))
    node_metrics = _node_metrics_by_name(_safe_get(client, "/apis/metrics.k8s.io/v1beta1/nodes", errors))

    for namespace in namespaces:
        ns = quote(namespace, safe="")
        resources[namespace] = {
            "pods": _items(_safe_get(client, f"/api/v1/namespaces/{ns}/pods", errors)),
            "services": _items(_safe_get(client, f"/api/v1/namespaces/{ns}/services", errors)),
            "deployments": _items(_safe_get(client, f"/apis/apps/v1/namespaces/{ns}/deployments", errors)),
            "ingresses": _items(_safe_get(client, f"/apis/networking.k8s.io/v1/namespaces/{ns}/ingresses", errors)),
            "endpoint_slices": _items(
                _safe_get(client, f"/apis/discovery.k8s.io/v1/namespaces/{ns}/endpointslices", errors)
            ),
        }
        pod_metrics[namespace] = _pod_metrics_by_name(
            _safe_get(client, f"/apis/metrics.k8s.io/v1beta1/namespaces/{ns}/pods", errors)
        )
        raw_events = _items(_safe_get(client, f"/api/v1/namespaces/{ns}/events", errors))
        events[namespace] = raw_events[-int(dify_config.MODEL_NET_K8S_DATA_EVENT_LIMIT) :]

    return {
        "nodes": nodes,
        "node_metrics": node_metrics,
        "resources": resources,
        "pod_metrics": pod_metrics,
        "events": events,
    }


def _load_cached_snapshot() -> dict[str, Any] | None:
    try:
        raw = redis_client.get(_CACHE_KEY)
    except Exception:
        return None
    if not raw:
        return None
    if isinstance(raw, bytes):
        raw = raw.decode("utf-8")
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None


def _save_cached_snapshot(snapshot: dict[str, Any]) -> None:
    try:
        redis_client.setex(
            _CACHE_KEY,
            int(dify_config.MODEL_NET_K8S_DATA_CACHE_TTL_SECONDS),
            json.dumps(snapshot, ensure_ascii=False),
        )
    except Exception:
        return


def build_k8s_cluster_snapshot(*, client: KubernetesApiClient | None = None) -> dict[str, Any]:
    generated_at = _now()
    namespaces = parse_namespaces(dify_config.MODEL_NET_K8S_DATA_NAMESPACES)
    if not namespaces:
        namespaces = parse_namespaces(dify_config.MODEL_NET_K8S_NAMESPACES)
    errors: list[dict[str, str]] = []
    data_sources: list[dict[str, Any]] = []

    if client is None:
        client = KubernetesApiClient(
            kubeconfig_path=_kubeconfig_path_from_config(),
            timeout_seconds=float(dify_config.MODEL_NET_K8S_DATA_K8S_API_TIMEOUT_SECONDS),
        )

    resources = _collect_resources(client, namespaces, errors)
    data_sources.append(_source_status("kubernetes_api", status="available", updated_at=generated_at))
    data_sources.append(_source_status("metrics_server", status="available", updated_at=generated_at))

    prometheus = _collect_prometheus(client, errors) if bool(dify_config.MODEL_NET_K8S_DATA_PROMETHEUS_ENABLED) else {
        "samples": {},
        "statuses": [_source_status("prometheus", status="disabled")],
    }
    data_sources.extend(prometheus["statuses"])
    prometheus_by_node = _node_prometheus_summary(prometheus["samples"])

    nodes = _build_node_snapshots(resources["nodes"], resources["node_metrics"], prometheus_by_node)
    models = _build_model_snapshots(
        namespaces=namespaces,
        resources=resources["resources"],
        pod_metrics=resources["pod_metrics"],
        events_by_namespace=resources["events"],
    )
    pods = [
        pod
        for namespace in namespaces
        for pod in [
            {
                "namespace": namespace,
                "name": _name(item),
                "phase": _status(item).get("phase"),
                "ready": _pod_ready(item),
                "restart_count": _container_restarts(item),
                "node": _spec(item).get("nodeName"),
                "pod_ip": _status(item).get("podIP"),
                "metrics": resources["pod_metrics"].get(namespace, {}).get(_name(item), {}),
                "labels": _labels(item),
            }
            for item in resources["resources"].get(namespace, {}).get("pods", [])
        ]
    ]
    events = [
        {
            "namespace": namespace,
            "type": event.get("type"),
            "reason": event.get("reason"),
            "message": event.get("message"),
            "last_timestamp": event.get("lastTimestamp") or event.get("eventTime"),
            "object": event.get("involvedObject"),
        }
        for namespace, namespace_events in resources["events"].items()
        for event in namespace_events
    ]

    snapshot = {
        "generated_at": generated_at,
        "namespaces": list(namespaces),
        "overview": {
            "node_count": len(nodes),
            "ready_node_count": len([item for item in nodes if item["ready"]]),
            "model_count": len(models),
            "routable_model_count": len([item for item in models if item["route_status"]["routable"]]),
            "pod_count": len(pods),
            "event_count": len(events),
        },
        "data_sources": data_sources,
        "nodes": nodes,
        "models": models,
        "pods": sorted(pods, key=itemgetter("namespace", "name")),
        "events": sorted(events, key=lambda item: str(item.get("last_timestamp") or ""), reverse=True),
        "errors": errors,
    }
    _save_cached_snapshot(snapshot)
    return snapshot


def get_k8s_cluster_snapshot(*, refresh: bool = True) -> dict[str, Any]:
    if not refresh:
        cached = _load_cached_snapshot()
        if cached:
            return cached
    try:
        return build_k8s_cluster_snapshot()
    except Exception as exc:
        cached = _load_cached_snapshot()
        if cached:
            cached = dict(cached)
            cached.setdefault("errors", []).append({"source": "snapshot_refresh", "error": str(exc)})
            cached["cache_status"] = "stale_fallback"
            return cached
        return {
            "generated_at": _now(),
            "overview": {},
            "data_sources": [_source_status("kubernetes_api", status="unavailable", error=str(exc))],
            "nodes": [],
            "models": [],
            "pods": [],
            "events": [],
            "errors": [{"source": "snapshot_refresh", "error": str(exc)}],
        }


def get_k8s_overview() -> dict[str, Any]:
    snapshot = get_k8s_cluster_snapshot()
    return {
        "generated_at": snapshot["generated_at"],
        "namespaces": snapshot.get("namespaces", []),
        "overview": snapshot.get("overview", {}),
        "data_sources": snapshot.get("data_sources", []),
        "errors": snapshot.get("errors", []),
    }


def get_k8s_nodes() -> dict[str, Any]:
    snapshot = get_k8s_cluster_snapshot()
    return {
        "generated_at": snapshot["generated_at"],
        "nodes": snapshot.get("nodes", []),
        "errors": snapshot.get("errors", []),
    }


def get_k8s_models() -> dict[str, Any]:
    snapshot = get_k8s_cluster_snapshot()
    return {
        "generated_at": snapshot["generated_at"],
        "models": snapshot.get("models", []),
        "errors": snapshot.get("errors", []),
    }


def get_k8s_pods() -> dict[str, Any]:
    snapshot = get_k8s_cluster_snapshot()
    return {
        "generated_at": snapshot["generated_at"],
        "pods": snapshot.get("pods", []),
        "errors": snapshot.get("errors", []),
    }


def get_k8s_events() -> dict[str, Any]:
    snapshot = get_k8s_cluster_snapshot()
    return {
        "generated_at": snapshot["generated_at"],
        "events": snapshot.get("events", []),
        "errors": snapshot.get("errors", []),
    }


def get_k8s_data_sources() -> dict[str, Any]:
    snapshot = get_k8s_cluster_snapshot()
    return {
        "generated_at": snapshot["generated_at"],
        "data_sources": snapshot.get("data_sources", []),
        "errors": snapshot.get("errors", []),
    }
