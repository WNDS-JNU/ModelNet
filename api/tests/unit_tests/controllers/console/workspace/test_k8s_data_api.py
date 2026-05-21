from __future__ import annotations

from unittest.mock import patch

from controllers.console.workspace.k8s_data import K8sModelsApi, K8sOverviewApi


def _unwrap(func):
    while hasattr(func, "__wrapped__"):
        func = func.__wrapped__
    return func


def test_k8s_overview_api_returns_service_payload(app):
    api = K8sOverviewApi()
    method = _unwrap(api.get)

    with (
        app.test_request_context("/"),
        patch(
            "controllers.console.workspace.k8s_data.get_k8s_overview",
            return_value={"overview": {"model_count": 2}, "data_sources": []},
        ),
    ):
        result, status = method(api)

    assert status == 200
    assert result["overview"]["model_count"] == 2


def test_k8s_models_api_returns_service_payload(app):
    api = K8sModelsApi()
    method = _unwrap(api.get)

    with (
        app.test_request_context("/"),
        patch(
            "controllers.console.workspace.k8s_data.get_k8s_models",
            return_value={"models": [{"id": "inference/qwen"}]},
        ),
    ):
        result, status = method(api)

    assert status == 200
    assert result["models"] == [{"id": "inference/qwen"}]
