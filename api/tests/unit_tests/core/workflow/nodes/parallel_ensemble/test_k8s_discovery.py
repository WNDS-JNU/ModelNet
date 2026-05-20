from core.workflow.nodes.parallel_ensemble.registry.k8s_discovery import (
    K8sDiscoverySettings,
    alias_for_route,
    discover_model_registry,
    infer_model_metadata,
    iter_ingress_routes,
    parse_namespaces,
)


def _ingress():
    return {
        "metadata": {"name": "qwen3-4b-awq"},
        "spec": {
            "tls": [{"hosts": ["inference.cluster.aimodelnetwork.cn"]}],
            "rules": [
                {
                    "host": "inference.cluster.aimodelnetwork.cn",
                    "http": {
                        "paths": [
                            {
                                "path": "/Qwen/Qwen3-4B-AWQ",
                                "pathType": "Prefix",
                                "backend": {
                                    "service": {
                                        "name": "qwen3-4b-awq",
                                        "port": {"number": 8000},
                                    }
                                },
                            }
                        ]
                    },
                }
            ],
        },
    }


class _FakeIngressClient:
    def __init__(self, ingresses):
        self.ingresses = ingresses

    def list_ingresses(self, namespace):
        assert namespace == "vllm-test"
        return self.ingresses


def test_parse_namespaces_dedupes_and_trims():
    assert parse_namespaces(" inference, llama-cpp, inference ,, light ") == (
        "inference",
        "llama-cpp",
        "light",
    )


def test_iter_ingress_routes_builds_kuboard_base_url():
    routes = iter_ingress_routes("vllm-test", _ingress(), default_scheme="http")

    assert routes == [
        {
            "namespace": "vllm-test",
            "ingress": "qwen3-4b-awq",
            "host": "inference.cluster.aimodelnetwork.cn",
            "path": "/Qwen/Qwen3-4B-AWQ",
            "base_url": "https://inference.cluster.aimodelnetwork.cn/Qwen/Qwen3-4B-AWQ",
            "service_name": "qwen3-4b-awq",
            "service_port": "8000",
        }
    ]


def test_alias_for_route_uses_namespace_and_path_slug():
    [route] = iter_ingress_routes("vllm-test", _ingress(), default_scheme="https")

    assert alias_for_route(route) == "vllm-test-qwen-qwen3-4b-awq"


def test_infer_model_metadata_marks_qwen3_base_as_think_model():
    metadata = infer_model_metadata("Qwen/Qwen3-4B-AWQ", "/Qwen/Qwen3-4B-AWQ")

    assert metadata == {
        "EOS": "<|im_end|>",
        "type": "think",
        "stop_think": "</think>",
    }


def test_discover_model_registry_keeps_healthy_routes_and_skips_failed_routes():
    ingress = _ingress()
    ingress["spec"]["rules"].append(
        {
            "host": "inference.cluster.aimodelnetwork.cn",
            "http": {
                "paths": [
                    {
                        "path": "/broken/model",
                        "backend": {"service": {"name": "broken", "port": {"number": 8000}}},
                    }
                ]
            },
        }
    )
    settings = K8sDiscoverySettings(
        namespaces=("vllm-test",),
        default_backend="vllm_chat",
        route_default_scheme="https",
    )

    def probe(base_url, timeout):
        del timeout
        if base_url.endswith("/broken/model"):
            raise RuntimeError("HTTP 503 from upstream")
        return "Qwen/Qwen3-4B-AWQ"

    result = discover_model_registry(settings, client=_FakeIngressClient([ingress]), probe_func=probe)

    assert [model["id"] for model in result["models"]] == ["vllm-test-qwen-qwen3-4b-awq"]
    assert result["models"][0]["model_url"] == "https://inference.cluster.aimodelnetwork.cn/Qwen/Qwen3-4B-AWQ"
    assert result["models"][0]["backend"] == "vllm_chat"
    assert result["models"][0]["type"] == "think"
    assert len(result["skipped"]) == 1
    assert result["skipped"][0]["reason"] == "probe_failed"
