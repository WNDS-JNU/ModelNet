from __future__ import annotations

from services import model_net_k8s_data_service as service


class FakeK8sClient:
    def get_json(self, path: str):
        if path == "/api/v1/nodes":
            return {
                "items": [
                    {
                        "metadata": {
                            "name": "pc-4090",
                            "labels": {"device-type": "pc-gpu"},
                        },
                        "spec": {},
                        "status": {
                            "conditions": [{"type": "Ready", "status": "True"}],
                            "addresses": [{"type": "InternalIP", "address": "192.168.8.174"}],
                        },
                    },
                    {
                        "metadata": {
                            "name": "jetson-16g-1",
                            "labels": {"device-type": "jetson", "jetson-memory": "16g"},
                        },
                        "spec": {},
                        "status": {
                            "conditions": [{"type": "Ready", "status": "True"}],
                            "addresses": [{"type": "InternalIP", "address": "192.168.8.199"}],
                        },
                    },
                ]
            }
        if path == "/apis/metrics.k8s.io/v1beta1/nodes":
            return {
                "items": [
                    {
                        "metadata": {"name": "pc-4090"},
                        "timestamp": "2026-05-21T00:00:00Z",
                        "window": "20s",
                        "usage": {"cpu": "100m", "memory": "2Gi"},
                    }
                ]
            }
        if "prometheus-k8s" in path:
            return self._prometheus(path)
        if "/namespaces/inference/" in path:
            return self._inference(path)
        if "/namespaces/llama-cpp/" in path:
            return self._llama_cpp(path)
        return {"items": []}

    def _prometheus(self, path: str):
        result = []
        if "DCGM_FI_DEV_GPU_UTIL" in path:
            result = [
                {
                    "metric": {
                        "instance": "pc-4090",
                        "device": "nvidia0",
                        "gpu": "0",
                        "modelName": "NVIDIA GeForce RTX 4090",
                        "UUID": "GPU-test",
                    },
                    "value": [1779346000, "12"],
                }
            ]
        elif "DCGM_FI_DEV_FB_USED" in path:
            result = [{"metric": {"instance": "pc-4090", "device": "nvidia0"}, "value": [1779346000, "1024"]}]
        elif "temperature_C" in path:
            result = [
                {
                    "metric": {"instance": "jetson-16g-1", "statistic": "gpu"},
                    "value": [1779346000, "74.5"],
                }
            ]
        elif "ram_kB" in path:
            result = [
                {
                    "metric": {"instance": "jetson-16g-1", "statistic": "used"},
                    "value": [1779346000, "14597376"],
                }
            ]
        return {"status": "success", "data": {"resultType": "vector", "result": result}}

    def _inference(self, path: str):
        if path.endswith("/pods"):
            return {
                "items": [
                    {
                        "metadata": {"name": "qwen-pod", "labels": {"app": "qwen"}},
                        "spec": {"nodeName": "pc-4090", "containers": [{"name": "vllm", "image": "vllm-openai"}]},
                        "status": {
                            "phase": "Running",
                            "podIP": "10.42.1.2",
                            "conditions": [{"type": "Ready", "status": "True"}],
                            "containerStatuses": [{"name": "vllm", "ready": True, "restartCount": 0}],
                        },
                    }
                ]
            }
        if path.endswith("/services"):
            return {
                "items": [
                    {
                        "metadata": {"name": "qwen", "labels": {"k8s.kuboard.cn/name": "qwen"}},
                        "spec": {"type": "ClusterIP", "selector": {"app": "qwen"}, "ports": [{"port": 8000}]},
                    },
                    {
                        "metadata": {"name": "empty", "labels": {"k8s.kuboard.cn/name": "empty"}},
                        "spec": {"type": "ClusterIP", "selector": {"app": "empty"}, "ports": [{"port": 8000}]},
                    },
                ]
            }
        if path.endswith("/deployments"):
            return {
                "items": [
                    {
                        "metadata": {"name": "qwen"},
                        "spec": {"selector": {"matchLabels": {"app": "qwen"}}},
                        "status": {"readyReplicas": 1, "replicas": 1},
                    },
                    {"metadata": {"name": "empty"}, "spec": {}, "status": {"readyReplicas": 0, "replicas": 1}},
                ]
            }
        if path.endswith("/ingresses"):
            return {
                "items": [
                    {
                        "metadata": {"name": "qwen", "namespace": "inference"},
                        "spec": {
                            "rules": [
                                {
                                    "host": "inference.example.test",
                                    "http": {
                                        "paths": [
                                            {
                                                "path": "/Qwen/Qwen",
                                                "backend": {"service": {"name": "qwen", "port": {"number": 8000}}},
                                            },
                                            {
                                                "path": "/empty",
                                                "backend": {"service": {"name": "empty", "port": {"number": 8000}}},
                                            },
                                        ]
                                    },
                                }
                            ]
                        },
                    }
                ]
            }
        if path.endswith("/endpointslices"):
            return {
                "items": [
                    {
                        "metadata": {"labels": {"kubernetes.io/service-name": "qwen"}},
                        "endpoints": [{"addresses": ["10.42.1.2"], "conditions": {"ready": True}}],
                    },
                    {"metadata": {"labels": {"kubernetes.io/service-name": "empty"}}, "endpoints": []},
                ]
            }
        if path.endswith("/events"):
            return {
                "items": [
                    {
                        "type": "Warning",
                        "reason": "BackOff",
                        "message": "Back-off restarting failed container",
                        "lastTimestamp": "2026-05-21T00:00:00Z",
                        "involvedObject": {"kind": "Pod", "name": "empty-pod"},
                    }
                ]
            }
        if path.endswith("/pods") is False and "metrics.k8s.io" in path:
            return {"items": []}
        return {"items": []}

    def _llama_cpp(self, path: str):
        if path.endswith("/pods"):
            return {
                "items": [
                    {
                        "metadata": {"name": "llama-pod", "labels": {"app": "llama"}},
                        "spec": {
                            "nodeName": "jetson-16g-1",
                            "containers": [{"name": "llama", "image": "llama-cpp-runner"}],
                        },
                        "status": {
                            "phase": "Running",
                            "podIP": "10.42.2.2",
                            "conditions": [{"type": "Ready", "status": "True"}],
                            "containerStatuses": [{"name": "llama", "ready": True, "restartCount": 0}],
                        },
                    }
                ]
            }
        if path.endswith("/services"):
            return {
                "items": [
                    {
                        "metadata": {"name": "llama", "labels": {"k8s.kuboard.cn/name": "llama"}},
                        "spec": {
                            "type": "NodePort",
                            "selector": {"app": "llama"},
                            "ports": [{"port": 8000, "nodePort": 30582}],
                        },
                    }
                ]
            }
        if path.endswith("/deployments"):
            return {
                "items": [
                    {
                        "metadata": {"name": "llama"},
                        "spec": {"selector": {"matchLabels": {"app": "llama"}}},
                        "status": {"readyReplicas": 1, "replicas": 1},
                    }
                ]
            }
        if path.endswith("/endpointslices"):
            return {
                "items": [
                    {
                        "metadata": {"labels": {"kubernetes.io/service-name": "llama"}},
                        "endpoints": [{"addresses": ["10.42.2.2"], "conditions": {"ready": True}}],
                    }
                ]
            }
        return {"items": []}


def _set_config(monkeypatch):
    monkeypatch.setattr(service.dify_config, "MODEL_NET_K8S_DATA_NAMESPACES", "inference,llama-cpp")
    monkeypatch.setattr(service.dify_config, "MODEL_NET_K8S_DATA_MONITORING_NAMESPACE", "kuboard")
    monkeypatch.setattr(service.dify_config, "MODEL_NET_K8S_DATA_PROMETHEUS_SERVICE_PROXY", "http:prometheus-k8s:9090")
    monkeypatch.setattr(service.dify_config, "MODEL_NET_K8S_DATA_PROMETHEUS_ENABLED", True)
    monkeypatch.setattr(service.dify_config, "MODEL_NET_K8S_DATA_NODEPORT_HOST", "219.222.20.79")
    monkeypatch.setattr(service.dify_config, "MODEL_NET_K8S_DATA_PROBE_ENABLED", True)
    monkeypatch.setattr(service.dify_config, "MODEL_NET_K8S_DATA_VLLM_METRICS_ENABLED", True)
    monkeypatch.setattr(service.dify_config, "MODEL_NET_K8S_DATA_EVENT_LIMIT", 100)
    monkeypatch.setattr(service.dify_config, "MODEL_NET_K8S_ROUTE_DEFAULT_SCHEME", "http")


def test_parse_vllm_metrics_extracts_queue_and_histogram():
    parsed = service.parse_vllm_metrics(
        "\n".join(
            [
                'vllm:num_requests_running{model_name="qwen"} 2',
                'vllm:num_requests_waiting{model_name="qwen"} 3',
                'vllm:kv_cache_usage_perc{model_name="qwen"} 0.25',
                'vllm:request_success_total{finished_reason="stop",model_name="qwen"} 10',
                'vllm:request_success_total{finished_reason="length",model_name="qwen"} 2',
                'vllm:e2e_request_latency_seconds_bucket{le="1.0",model_name="qwen"} 1',
                'vllm:e2e_request_latency_seconds_bucket{le="2.0",model_name="qwen"} 10',
                'vllm:e2e_request_latency_seconds_bucket{le="+Inf",model_name="qwen"} 10',
            ]
        )
    )

    assert parsed["num_requests_running"] == 2
    assert parsed["num_requests_waiting"] == 3
    assert parsed["kv_cache_usage_perc"] == 0.25
    assert parsed["request_success_total"] == 12
    assert parsed["e2e_request_latency_p95_seconds"] is not None


def test_snapshot_normalizes_k8s_prometheus_probe_and_vllm(monkeypatch):
    _set_config(monkeypatch)
    monkeypatch.setattr(service, "_save_cached_snapshot", lambda snapshot: None)
    monkeypatch.setattr(
        service,
        "_probe_openai",
        lambda base_url: {"status": "available", "status_code": 200, "model_name": "Qwen/Qwen"}
        if base_url
        else {"status": "skipped"},
    )
    monkeypatch.setattr(
        service,
        "_fetch_vllm_metrics",
        lambda base_url: {"status": "available", "metrics": {"num_requests_waiting": 0}},
    )

    snapshot = service.build_k8s_cluster_snapshot(client=FakeK8sClient())

    assert snapshot["overview"]["node_count"] == 2
    by_node = {item["name"]: item for item in snapshot["nodes"]}
    assert by_node["pc-4090"]["prometheus"]["gpu"]["devices"][0]["utilization_percent"] == 12
    assert by_node["jetson-16g-1"]["prometheus"]["jetson"]["temperatures_c"]["gpu"] == 74.5

    by_model = {item["id"]: item for item in snapshot["models"]}
    assert by_model["inference/qwen"]["route_status"]["routable"] is True
    assert by_model["inference/qwen"]["base_url"] == "http://inference.example.test/Qwen/Qwen"
    assert by_model["inference/qwen"]["vllm_metrics"]["metrics"]["num_requests_waiting"] == 0
    assert by_model["inference/empty"]["route_status"]["routable"] is False
    assert "no_ready_endpoint" in by_model["inference/empty"]["route_status"]["skip_reasons"]
    assert by_model["llama-cpp/llama"]["base_url"] == "http://219.222.20.79:30582"
    assert by_model["llama-cpp/llama"]["backend"] == "llama_cpp"
