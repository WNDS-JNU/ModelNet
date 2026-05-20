"""Kubernetes Ingress discovery for the ModelNet registry.

The discovery contract is intentionally narrow:

1. scan configured namespaces for ``networking.k8s.io/v1`` Ingresses;
2. convert ``host + path`` into a public model base URL;
3. probe ``<base>/v1/models`` through the SSRF proxy;
4. emit fully validated-looking ``model_net.yaml`` entries.

Routes that exist but do not answer ``/v1/models`` are reported as
``skipped`` and never enter the runtime registry.
"""

from __future__ import annotations

import base64
import json
import os
import re
import ssl
from dataclasses import dataclass
from datetime import UTC, datetime
from operator import itemgetter
from pathlib import Path
from typing import Any, TypedDict
from urllib.parse import quote, urlparse, urlunparse

import httpx
import yaml

from core.helper import ssrf_proxy


class RouteCandidate(TypedDict, total=False):
    namespace: str
    ingress: str
    host: str
    path: str
    base_url: str
    service_name: str
    service_port: str


class SkippedRoute(RouteCandidate, total=False):
    reason: str
    status_code: int
    error: str


class DiscoveryResult(TypedDict):
    generated_at: str
    models: list[dict[str, Any]]
    candidates: list[RouteCandidate]
    skipped: list[SkippedRoute]


@dataclass(frozen=True)
class K8sDiscoverySettings:
    namespaces: tuple[str, ...]
    kubeconfig_path: str | None = None
    probe_timeout_seconds: float = 10.0
    route_default_scheme: str = "https"
    default_backend: str = "vllm_chat"
    request_timeout_ms: int = 180000


@dataclass(frozen=True)
class KubernetesAuth:
    server: str
    token: str | None
    verify: bool | str | ssl.SSLContext


def parse_namespaces(raw: str | list[str] | tuple[str, ...] | None) -> tuple[str, ...]:
    if raw is None:
        return ()
    if isinstance(raw, str):
        values = raw.split(",")
    else:
        values = list(raw)
    out: list[str] = []
    seen: set[str] = set()
    for value in values:
        namespace = str(value).strip()
        if not namespace or namespace in seen:
            continue
        seen.add(namespace)
        out.append(namespace)
    return tuple(out)


def _ssl_context_from_ca_data(value: str) -> ssl.SSLContext:
    decoded = base64.b64decode(value).decode("utf-8")
    return ssl.create_default_context(cadata=decoded)


def _load_kubeconfig(path: str) -> KubernetesAuth:
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    current_context_name = raw.get("current-context")
    contexts = {
        item.get("name"): item.get("context", {})
        for item in raw.get("contexts", [])
        if isinstance(item, dict)
    }
    context = contexts.get(current_context_name)
    if not isinstance(context, dict):
        raise RuntimeError("kubeconfig current-context not found")

    cluster_name = context.get("cluster")
    user_name = context.get("user")
    clusters = {
        item.get("name"): item.get("cluster", {})
        for item in raw.get("clusters", [])
        if isinstance(item, dict)
    }
    users = {
        item.get("name"): item.get("user", {})
        for item in raw.get("users", [])
        if isinstance(item, dict)
    }
    cluster = clusters.get(cluster_name)
    user = users.get(user_name, {})
    if not isinstance(cluster, dict) or not cluster.get("server"):
        raise RuntimeError("kubeconfig cluster server not found")
    if not isinstance(user, dict):
        user = {}

    verify: bool | str | ssl.SSLContext = True
    if cluster.get("insecure-skip-tls-verify") is True:
        verify = False
    elif isinstance(cluster.get("certificate-authority"), str):
        verify = cluster["certificate-authority"]
    elif isinstance(cluster.get("certificate-authority-data"), str):
        verify = _ssl_context_from_ca_data(cluster["certificate-authority-data"])

    token: str | None = None
    if isinstance(user.get("token"), str):
        token = user["token"]
    elif isinstance(user.get("tokenFile"), str):
        token = Path(user["tokenFile"]).read_text(encoding="utf-8").strip()

    return KubernetesAuth(server=str(cluster["server"]).rstrip("/"), token=token, verify=verify)


def _load_in_cluster_auth() -> KubernetesAuth:
    host = os.getenv("KUBERNETES_SERVICE_HOST")
    port = os.getenv("KUBERNETES_SERVICE_PORT", "443")
    if not host:
        raise RuntimeError("KUBERNETES_SERVICE_HOST is not set")

    token_path = Path("/var/run/secrets/kubernetes.io/serviceaccount/token")
    ca_path = Path("/var/run/secrets/kubernetes.io/serviceaccount/ca.crt")
    token = token_path.read_text(encoding="utf-8").strip() if token_path.exists() else None
    verify: bool | str = str(ca_path) if ca_path.exists() else True
    return KubernetesAuth(server=f"https://{host}:{port}", token=token, verify=verify)


class KubernetesIngressClient:
    def __init__(self, settings: K8sDiscoverySettings):
        self._settings = settings
        if settings.kubeconfig_path:
            self._auth = _load_kubeconfig(settings.kubeconfig_path)
        else:
            self._auth = _load_in_cluster_auth()

    def list_ingresses(self, namespace: str) -> list[dict[str, Any]]:
        ns = quote(namespace, safe="")
        url = f"{self._auth.server}/apis/networking.k8s.io/v1/namespaces/{ns}/ingresses"
        headers = {"Accept": "application/json"}
        if self._auth.token:
            headers["Authorization"] = f"Bearer {self._auth.token}"

        with httpx.Client(timeout=self._settings.probe_timeout_seconds, verify=self._auth.verify) as client:
            response = client.get(url, headers=headers)
        response.raise_for_status()
        payload = response.json()
        items = payload.get("items", [])
        if not isinstance(items, list):
            return []
        return [item for item in items if isinstance(item, dict)]


def _route_scheme(host: str, tls_hosts: set[str], default_scheme: str) -> str:
    if host in tls_hosts or "*" in tls_hosts:
        return "https"
    scheme = default_scheme.strip().lower()
    return scheme if scheme in {"http", "https"} else "https"


def _build_base_url(scheme: str, host: str, path: str) -> str:
    clean_path = path if path.startswith("/") else f"/{path}"
    if clean_path != "/":
        clean_path = clean_path.rstrip("/")
    return urlunparse((scheme, host, "" if clean_path == "/" else clean_path, "", "", ""))


def _service_ref(path_item: dict[str, Any]) -> tuple[str, str]:
    backend = path_item.get("backend")
    if not isinstance(backend, dict):
        return "", ""
    service = backend.get("service")
    if not isinstance(service, dict):
        return "", ""
    name = service.get("name")
    port = service.get("port")
    port_value = ""
    if isinstance(port, dict):
        if port.get("number") is not None:
            port_value = str(port["number"])
        elif port.get("name") is not None:
            port_value = str(port["name"])
    return str(name or ""), port_value


def iter_ingress_routes(
    namespace: str,
    ingress: dict[str, Any],
    *,
    default_scheme: str,
) -> list[RouteCandidate]:
    metadata = ingress.get("metadata") if isinstance(ingress.get("metadata"), dict) else {}
    spec = ingress.get("spec") if isinstance(ingress.get("spec"), dict) else {}
    ingress_name = str(metadata.get("name") or "")

    tls_hosts: set[str] = set()
    tls_items = spec.get("tls")
    if isinstance(tls_items, list):
        for item in tls_items:
            if not isinstance(item, dict):
                continue
            hosts = item.get("hosts")
            if isinstance(hosts, list):
                tls_hosts.update(str(host) for host in hosts if host)

    routes: list[RouteCandidate] = []
    rules = spec.get("rules")
    if not isinstance(rules, list):
        return routes

    for rule in rules:
        if not isinstance(rule, dict):
            continue
        host = str(rule.get("host") or "").strip()
        http = rule.get("http")
        paths = http.get("paths") if isinstance(http, dict) else None
        if not host or not isinstance(paths, list):
            continue
        scheme = _route_scheme(host, tls_hosts, default_scheme)
        for path_item in paths:
            if not isinstance(path_item, dict):
                continue
            path = str(path_item.get("path") or "/")
            service_name, service_port = _service_ref(path_item)
            routes.append(
                RouteCandidate(
                    namespace=namespace,
                    ingress=ingress_name,
                    host=host,
                    path=path,
                    base_url=_build_base_url(scheme, host, path),
                    service_name=service_name,
                    service_port=service_port,
                )
            )
    return routes


def _build_probe_url(raw: str) -> str | None:
    try:
        parsed = urlparse(raw)
    except ValueError:
        return None
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        return None
    path = parsed.path.rstrip("/")
    if not path:
        probe_path = "/v1/models"
    elif path.endswith("/v1/models"):
        probe_path = path
    elif path.endswith("/v1"):
        probe_path = f"{path}/models"
    else:
        probe_path = f"{path}/v1/models"
    return urlunparse((parsed.scheme, parsed.netloc, probe_path, "", "", ""))


def _extract_first_model_id(payload: Any) -> str | None:
    if not isinstance(payload, dict):
        return None
    data = payload.get("data")
    if isinstance(data, list) and data:
        first = data[0]
        if isinstance(first, dict) and isinstance(first.get("id"), str) and first["id"]:
            return first["id"]
    models = payload.get("models")
    if isinstance(models, list) and models:
        first = models[0]
        if isinstance(first, dict) and isinstance(first.get("name"), str) and first["name"]:
            return first["name"]
    return None


def probe_model_name(base_url: str, timeout_seconds: float) -> str:
    probe_url = _build_probe_url(base_url)
    if probe_url is None:
        raise RuntimeError("base_url is not an http(s) URL")

    response = ssrf_proxy.get(probe_url, max_retries=0, timeout=timeout_seconds)
    status_code = getattr(response, "status_code", 0)
    if int(status_code) // 100 != 2:
        raise RuntimeError(f"HTTP {status_code} from {probe_url}")

    try:
        payload = response.json()
    except Exception:
        payload = json.loads(response.text)

    model_name = _extract_first_model_id(payload)
    if not model_name:
        raise RuntimeError("no model id in /v1/models response")
    return model_name


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "model"


def alias_for_route(route: RouteCandidate) -> str:
    path = route.get("path") or route.get("host") or "model"
    return _slug(f"{route.get('namespace', '')}-{path}")


def infer_model_metadata(model_name: str, route_path: str = "") -> dict[str, Any]:
    key = f"{model_name} {route_path}".lower()
    eos = "<|end_of_text|>"
    model_type = "normal"
    stop_think: str | None = None

    if "qwen" in key or "kimi" in key:
        eos = "<|im_end|>"
    if "glm" in key:
        eos = "<|endoftext|>"
    if "hunyuan" in key:
        eos = "<|eos|>"
    if "phi" in key or "gpt-oss" in key:
        eos = "<|end|>"
    if "mistral" in key or "ministral" in key:
        eos = "</s>"

    if "gpt-oss" in key:
        model_type = "think"
        stop_think = "final<|message|>"
    elif "deepseek-r1" in key or "deepseek_r1" in key or ("qwen3" in key and "instruct" not in key):
        model_type = "think"
        stop_think = "</think>"

    return {
        "EOS": eos,
        "type": model_type,
        "stop_think": stop_think,
    }


def build_model_entry(route: RouteCandidate, model_name: str, settings: K8sDiscoverySettings) -> dict[str, Any]:
    metadata = infer_model_metadata(model_name, route.get("path", ""))
    entry: dict[str, Any] = {
        "id": alias_for_route(route),
        "backend": settings.default_backend,
        "model_name": model_name,
        "model_url": route["base_url"],
        "EOS": metadata["EOS"],
        "type": metadata["type"],
        "request_timeout_ms": settings.request_timeout_ms,
    }
    if metadata["stop_think"]:
        entry["stop_think"] = metadata["stop_think"]
    return entry


def discover_model_registry(
    settings: K8sDiscoverySettings,
    *,
    client: KubernetesIngressClient | None = None,
    probe_func: Any | None = None,
) -> DiscoveryResult:
    generated_at = datetime.now(UTC).isoformat()
    candidates: list[RouteCandidate] = []
    skipped: list[SkippedRoute] = []
    models: list[dict[str, Any]] = []
    seen_urls: set[str] = set()
    seen_ids: set[str] = set()

    if not settings.namespaces:
        return DiscoveryResult(generated_at=generated_at, models=[], candidates=[], skipped=[])

    k8s = client or KubernetesIngressClient(settings)
    probe = probe_func or probe_model_name

    for namespace in settings.namespaces:
        try:
            ingresses = k8s.list_ingresses(namespace)
        except Exception as exc:
            skipped.append(SkippedRoute(namespace=namespace, reason="list_ingresses_failed", error=str(exc)))
            continue

        for ingress in ingresses:
            for route in iter_ingress_routes(
                namespace,
                ingress,
                default_scheme=settings.route_default_scheme,
            ):
                base_url = route["base_url"]
                if base_url in seen_urls:
                    continue
                seen_urls.add(base_url)
                candidates.append(route)
                try:
                    model_name = probe(base_url, settings.probe_timeout_seconds)
                    entry = build_model_entry(route, model_name, settings)
                except Exception as exc:
                    skipped.append(SkippedRoute(**route, reason="probe_failed", error=str(exc)))
                    continue

                alias = entry["id"]
                if alias in seen_ids:
                    suffix = _slug(route.get("host", "route"))
                    entry["id"] = f"{alias}-{suffix}"
                seen_ids.add(entry["id"])
                models.append(entry)

    models.sort(key=itemgetter("id"))
    return DiscoveryResult(generated_at=generated_at, models=models, candidates=candidates, skipped=skipped)
