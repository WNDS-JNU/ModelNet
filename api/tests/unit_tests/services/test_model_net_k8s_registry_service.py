from pathlib import Path

from core.workflow.nodes.parallel_ensemble.registry.model_registry import ModelRegistry
from services import model_net_k8s_registry_service as service


class _FakeRedis:
    def __init__(self):
        self.store = {}

    def set(self, key, value, nx=False, ex=None):
        del ex
        if nx and key in self.store:
            return False
        self.store[key] = value
        return True

    def get(self, key):
        return self.store.get(key)

    def delete(self, key):
        self.store.pop(key, None)


def _patch_config(monkeypatch, tmp_path: Path, *, enabled: bool = True):
    monkeypatch.setattr(service.dify_config, "MODEL_NET_K8S_DISCOVERY_ENABLED", enabled)
    monkeypatch.setattr(service.dify_config, "MODEL_NET_K8S_NAMESPACES", "vllm-test")
    monkeypatch.setattr(service.dify_config, "MODEL_NET_K8S_KUBECONFIG_PATH", "")
    monkeypatch.setattr(service.dify_config, "MODEL_NET_K8S_PROBE_TIMEOUT_SECONDS", 10)
    monkeypatch.setattr(service.dify_config, "MODEL_NET_K8S_ROUTE_DEFAULT_SCHEME", "https")
    monkeypatch.setattr(service.dify_config, "MODEL_NET_K8S_DEFAULT_BACKEND", "vllm_chat")
    monkeypatch.setattr(service.dify_config, "MODEL_NET_K8S_REQUEST_TIMEOUT_MS", 180000)
    monkeypatch.setattr(service.dify_config, "MODEL_NET_REGISTRY_PATH", str(tmp_path / "model_net.yaml"))


def test_refresh_writes_valid_registry_and_reloads_model_registry(monkeypatch, tmp_path):
    _patch_config(monkeypatch, tmp_path)
    monkeypatch.setattr(service, "redis_client", _FakeRedis())
    monkeypatch.setattr(
        service,
        "discover_model_registry",
        lambda settings: {
            "generated_at": "2026-05-20T00:00:00+00:00",
            "models": [
                {
                    "id": "vllm-test-qwen-qwen3-4b-awq",
                    "backend": "vllm_chat",
                    "model_name": "Qwen/Qwen3-4B-AWQ",
                    "model_url": "https://inference.cluster.aimodelnetwork.cn/Qwen/Qwen3-4B-AWQ",
                    "EOS": "<|im_end|>",
                    "type": "think",
                    "stop_think": "</think>",
                    "request_timeout_ms": 180000,
                }
            ],
            "candidates": [],
            "skipped": [],
        },
    )
    ModelRegistry.reset_for_testing()

    status = service.refresh_model_net_registry_from_k8s(triggered_by="test")

    assert status["status"] == "success"
    assert status["applied"] is True
    assert status["model_count"] == 1
    assert "Qwen/Qwen3-4B-AWQ" in Path(service.dify_config.MODEL_NET_REGISTRY_PATH).read_text()
    aliases = ModelRegistry.instance().list_aliases()
    assert aliases[0]["id"] == "vllm-test-qwen-qwen3-4b-awq"
    assert aliases[0]["metadata"]["type"] == "think"
    ModelRegistry.reset_for_testing()


def test_refresh_with_no_healthy_models_leaves_existing_registry(monkeypatch, tmp_path):
    _patch_config(monkeypatch, tmp_path)
    registry_path = Path(service.dify_config.MODEL_NET_REGISTRY_PATH)
    registry_path.write_text(
        """
models:
  - id: old
    backend: vllm_chat
    model_name: old-model
    model_url: https://example.com/old
    EOS: "<|end_of_text|>"
    type: normal
""".strip(),
        encoding="utf-8",
    )
    original = registry_path.read_text(encoding="utf-8")
    monkeypatch.setattr(service, "redis_client", _FakeRedis())
    monkeypatch.setattr(
        service,
        "discover_model_registry",
        lambda settings: {
            "generated_at": "2026-05-20T00:00:00+00:00",
            "models": [],
            "candidates": [{"base_url": "https://example.com/down"}],
            "skipped": [{"base_url": "https://example.com/down", "reason": "probe_failed"}],
        },
    )

    status = service.refresh_model_net_registry_from_k8s(triggered_by="test")

    assert status["status"] == "no_healthy_models"
    assert status["applied"] is False
    assert registry_path.read_text(encoding="utf-8") == original


def test_refresh_returns_disabled_status(monkeypatch, tmp_path):
    _patch_config(monkeypatch, tmp_path, enabled=False)
    fake_redis = _FakeRedis()
    monkeypatch.setattr(service, "redis_client", fake_redis)

    status = service.refresh_model_net_registry_from_k8s(triggered_by="test")

    assert status["status"] == "disabled"
    assert status["applied"] is False
    assert service.get_model_net_k8s_refresh_status()["status"] == "disabled"
