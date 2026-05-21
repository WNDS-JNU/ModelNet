from pathlib import Path

from core.workflow.nodes.parallel_ensemble.registry.model_registry import ModelRegistry
from services import model_net_load_service as service


def _patch_config(monkeypatch, tmp_path: Path):
    monkeypatch.setattr(service.dify_config, "MODEL_NET_REGISTRY_PATH", str(tmp_path / "model_net.yaml"))
    monkeypatch.setattr(service.dify_config, "MODEL_NET_PROMETHEUS_URL", "")
    monkeypatch.setattr(service.dify_config, "MODEL_NET_PROMETHEUS_TIMEOUT_SECONDS", 5)
    monkeypatch.setattr(service.dify_config, "MODEL_NET_PROMETHEUS_HEALTH_QUERY", "")
    monkeypatch.setattr(service.dify_config, "MODEL_NET_PROMETHEUS_QPS_QUERY", "")
    monkeypatch.setattr(service.dify_config, "MODEL_NET_PROMETHEUS_P95_LATENCY_QUERY", "")
    monkeypatch.setattr(service.dify_config, "MODEL_NET_PROMETHEUS_QUEUE_DEPTH_QUERY", "")
    monkeypatch.setattr(service.dify_config, "MODEL_NET_PROMETHEUS_GPU_UTILIZATION_QUERY", "")
    monkeypatch.setattr(service.dify_config, "MODEL_NET_PROMETHEUS_GPU_MEMORY_USED_RATIO_QUERY", "")
    monkeypatch.setattr(service.dify_config, "MODEL_NET_PROMETHEUS_ERROR_RATE_QUERY", "")
    monkeypatch.setattr(service.dify_config, "MODEL_NET_LOAD_METRIC_STALE_SECONDS", 180)
    monkeypatch.setattr(service.dify_config, "MODEL_NET_ROUTE_TOP_K", 1)


def _write_registry(tmp_path: Path):
    Path(service.dify_config.MODEL_NET_REGISTRY_PATH).write_text(
        """
models:
  - id: fast
    backend: vllm_chat
    model_name: fast-model
    model_url: https://example.com/fast
    EOS: "<|end_of_text|>"
    type: normal
    weight: 1.0
  - id: slow
    backend: vllm_chat
    model_name: slow-model
    model_url: https://example.com/slow
    EOS: "<|end_of_text|>"
    type: normal
    weight: 1.0
""".strip(),
        encoding="utf-8",
    )
    ModelRegistry.reset_for_testing()


def test_load_status_falls_back_to_static_registry_when_prometheus_is_not_configured(monkeypatch, tmp_path):
    _patch_config(monkeypatch, tmp_path)
    _write_registry(tmp_path)

    status = service.get_model_net_load_status()

    assert status["source"]["status"] == "static_fallback"
    assert status["source"]["prometheus_configured"] is False
    assert [item["id"] for item in status["models"]] == ["fast", "slow"]
    assert all(item["load"]["healthy"] is True for item in status["models"])
    assert all(item["score"] == 1.0 for item in status["models"])
    assert all("prometheus_not_configured" in item["reasons"] for item in status["models"])
    ModelRegistry.reset_for_testing()


def test_route_uses_prometheus_metrics_to_pick_lower_load_model(monkeypatch, tmp_path):
    _patch_config(monkeypatch, tmp_path)
    _write_registry(tmp_path)
    monkeypatch.setattr(service.dify_config, "MODEL_NET_PROMETHEUS_URL", "http://prometheus")
    monkeypatch.setattr(service.dify_config, "MODEL_NET_PROMETHEUS_HEALTH_QUERY", "health_{alias}")
    monkeypatch.setattr(service.dify_config, "MODEL_NET_PROMETHEUS_P95_LATENCY_QUERY", "latency_{alias}")
    monkeypatch.setattr(service.dify_config, "MODEL_NET_PROMETHEUS_QUEUE_DEPTH_QUERY", "queue_{alias}")
    monkeypatch.setattr(service.dify_config, "MODEL_NET_PROMETHEUS_GPU_UTILIZATION_QUERY", "gpu_{alias}")
    monkeypatch.setattr(service.dify_config, "MODEL_NET_PROMETHEUS_GPU_MEMORY_USED_RATIO_QUERY", "mem_{alias}")
    monkeypatch.setattr(service.dify_config, "MODEL_NET_PROMETHEUS_ERROR_RATE_QUERY", "error_{alias}")

    values = {
        "health_fast": 1,
        "latency_fast": 1000,
        "queue_fast": 1,
        "gpu_fast": 20,
        "mem_fast": 30,
        "error_fast": 0.01,
        "health_slow": 1,
        "latency_slow": 25000,
        "queue_slow": 32,
        "gpu_slow": 95,
        "mem_slow": 90,
        "error_slow": 20,
    }

    def query(query_text):
        return {"value": float(values[query_text]), "observed_at": None}

    monkeypatch.setattr(service, "_query_prometheus", query)

    result = service.route_model_from_load()

    assert result["source"]["status"] == "prometheus"
    assert result["selected_alias"] == "fast"
    assert [item["id"] for item in result["ranked_candidates"]] == ["fast", "slow"]
    assert result["ranked_candidates"][0]["score"] > result["ranked_candidates"][1]["score"]
    ModelRegistry.reset_for_testing()


def test_route_filters_unknown_and_missing_capability_candidates(monkeypatch, tmp_path):
    _patch_config(monkeypatch, tmp_path)
    _write_registry(tmp_path)

    result = service.route_model_from_load(
        candidate_aliases=["fast", "missing"],
        required_capabilities=["function_calling"],
    )

    assert result["selected_alias"] is None
    assert result["fallback_reason"] == "no_eligible_models"
    assert result["errors"] == [{"alias": "missing", "error": "unknown_model_alias"}]
    assert result["ranked_candidates"][0]["id"] == "fast"
    assert result["ranked_candidates"][0]["eligible"] is False
    assert result["ranked_candidates"][0]["missing_capabilities"] == ["function_calling"]
    ModelRegistry.reset_for_testing()


def test_route_skips_unhealthy_models_unless_policy_allows_them(monkeypatch, tmp_path):
    _patch_config(monkeypatch, tmp_path)
    _write_registry(tmp_path)
    monkeypatch.setattr(service.dify_config, "MODEL_NET_PROMETHEUS_URL", "http://prometheus")
    monkeypatch.setattr(service.dify_config, "MODEL_NET_PROMETHEUS_HEALTH_QUERY", "health_{alias}")

    def query(query_text):
        del query_text
        return {"value": 0.0, "observed_at": None}

    monkeypatch.setattr(service, "_query_prometheus", query)

    skipped = service.route_model_from_load()
    included = service.route_model_from_load(policy={"include_unhealthy": True})

    assert skipped["selected_alias"] is None
    assert skipped["fallback_reason"] == "no_healthy_eligible_models"
    assert included["selected_alias"] == "fast"
    ModelRegistry.reset_for_testing()
