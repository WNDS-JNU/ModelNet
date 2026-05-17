"""Unit tests for ``controllers.console.workflow_probe_model``.

The endpoint moves the token-model-source ``Fetch model info`` button
server-side so vLLM / TGI / SGLang / hosted routers (which don't enable
CORS by default) work the same as llama.cpp. These tests pin:
  - URL-building parity with the frontend ``buildModelsProbeUrl`` for
    every path-shape the form may hand over (bare host, hosted-router
    path prefix, trailing ``/v1``, full ``/v1/models``).
  - First-model-id extraction across both OpenAI-compat response shapes
    (``data[].id`` and llama.cpp's native ``models[].name``).
  - The handler's mapping of upstream failure modes to BaseHTTPException
    subclasses (malformed URL → 400, fetch failure / non-2xx / non-JSON
    / no model → 502).
"""

from unittest.mock import Mock, patch

import httpx
import pytest

from controllers.console.workflow_probe_model import (
    ProbeModelMalformedURLError,
    ProbeModelUpstreamError,
    _build_probe_url,
    _extract_first_model_id,
    probe_model_info,
)


class TestBuildProbeUrl:
    """Mirror the frontend ``buildModelsProbeUrl`` contract — same input
    classes the inline-spec-form is documented to handle.
    """

    def test_bare_host_appends_v1_models(self) -> None:
        assert _build_probe_url("http://219.222.20.79:30834") == "http://219.222.20.79:30834/v1/models"

    def test_https_bare_host_no_port(self) -> None:
        assert _build_probe_url("https://example.com") == "https://example.com/v1/models"

    def test_hosted_router_path_prefix_is_preserved(self) -> None:
        # The motivating case: a hosted OpenAI-compatible router scopes
        # one model per path. Stripping the prefix turns a valid endpoint
        # into a 404 on the upstream.
        raw = "https://inference.cluster.aimodelnetwork.cn/tencent/Hunyuan-7B-Instruct-AWQ-Int4"
        expected = "https://inference.cluster.aimodelnetwork.cn/tencent/Hunyuan-7B-Instruct-AWQ-Int4/v1/models"
        assert _build_probe_url(raw) == expected

    def test_v1_suffix_gets_models_appended(self) -> None:
        raw = "https://example.com/scope/v1"
        assert _build_probe_url(raw) == "https://example.com/scope/v1/models"

    def test_full_v1_models_endpoint_is_not_duplicated(self) -> None:
        raw = "https://example.com/scope/v1/models"
        assert _build_probe_url(raw) == "https://example.com/scope/v1/models"

    def test_trailing_slash_is_normalised(self) -> None:
        # A user-pasted ``http://h/`` should not double-up to ``//v1/models``.
        assert _build_probe_url("http://h/") == "http://h/v1/models"

    @pytest.mark.parametrize(
        "raw",
        [
            "",
            "not-a-url",
            "ftp://example.com",
            "file:///etc/passwd",
            "http://",
        ],
    )
    def test_rejects_malformed_or_non_http(self, raw: str) -> None:
        assert _build_probe_url(raw) is None


class TestExtractFirstModelId:
    """Pin both OpenAI-compat shapes the inline-spec-form needs to
    survive — ``data[].id`` (vLLM / llama.cpp / TGI / SGLang) and
    ``models[].name`` (llama.cpp native).
    """

    def test_prefers_data_id_when_present(self) -> None:
        # When both shapes are present (llama.cpp returns both), ``id``
        # wins because it matches what the runtime backend will identify
        # the model as.
        payload = {
            "data": [{"id": "from-data", "object": "model"}],
            "models": [{"name": "from-models"}],
        }
        assert _extract_first_model_id(payload) == "from-data"

    def test_falls_back_to_models_name(self) -> None:
        assert _extract_first_model_id({"models": [{"name": "fallback"}]}) == "fallback"

    def test_user_motivating_vllm_response(self) -> None:
        # The exact upstream payload from the bug report (truncated).
        payload = {
            "object": "list",
            "data": [
                {
                    "id": "tencent/Hunyuan-7B-Instruct-AWQ-Int4",
                    "object": "model",
                    "owned_by": "vllm",
                }
            ],
        }
        assert _extract_first_model_id(payload) == "tencent/Hunyuan-7B-Instruct-AWQ-Int4"

    @pytest.mark.parametrize(
        "payload",
        [
            None,
            "string",
            {},
            {"data": []},
            {"data": [{}]},
            {"data": [{"id": ""}]},
            {"data": [{"id": 123}]},
            {"models": []},
            {"models": [{}]},
            {"models": [{"name": ""}]},
        ],
    )
    def test_returns_none_on_empty_or_malformed(self, payload) -> None:
        assert _extract_first_model_id(payload) is None


class TestProbeModelInfo:
    """End-to-end behaviour of ``probe_model_info``.

    The function holds every step the Resource method runs (URL build,
    ssrf_proxy fetch, JSON decode, model-id extraction, error mapping)
    so testing it directly covers the handler's behaviour without
    needing a Flask request context or bypassing auth decorators —
    those are integration-test territory.

    Mocks ``ssrf_proxy.get`` at the seam where the process makes a
    network call; that's the right level to inject fixture responses.
    """

    @staticmethod
    def _mock_response(status_code: int, body: object | None = None, *, raise_on_json: bool = False) -> Mock:
        resp = Mock(spec=httpx.Response)
        resp.status_code = status_code
        if raise_on_json:
            resp.json = Mock(side_effect=ValueError("not json"))
        else:
            resp.json = Mock(return_value=body)
        return resp

    def test_happy_path_returns_first_model_id(self) -> None:
        upstream = self._mock_response(
            200,
            {"data": [{"id": "tencent/Hunyuan-7B-Instruct-AWQ-Int4", "object": "model"}]},
        )
        with patch(
            "controllers.console.workflow_probe_model.ssrf_proxy.get",
            return_value=upstream,
        ) as mocked_get:
            result = probe_model_info(
                "https://inference.cluster.aimodelnetwork.cn/tencent/Hunyuan-7B-Instruct-AWQ-Int4",
            )

        assert result == {"model_name": "tencent/Hunyuan-7B-Instruct-AWQ-Int4"}
        # The handler must hand the upstream-shaped probe URL to
        # ssrf_proxy — not the raw user URL — so the path-prefix +
        # ``/v1/models`` join is exercised end-to-end.
        called_url = mocked_get.call_args.args[0]
        assert called_url == (
            "https://inference.cluster.aimodelnetwork.cn/tencent/Hunyuan-7B-Instruct-AWQ-Int4/v1/models"
        )

    @pytest.mark.parametrize(
        "raw_url",
        [
            None,
            "",
            "   ",
            "not-a-url",
            "ftp://example.com",
        ],
    )
    def test_malformed_url_raises_400(self, raw_url: str | None) -> None:
        with pytest.raises(ProbeModelMalformedURLError):
            probe_model_info(raw_url)

    def test_upstream_non_2xx_raises_502(self) -> None:
        upstream = self._mock_response(503)
        with patch(
            "controllers.console.workflow_probe_model.ssrf_proxy.get",
            return_value=upstream,
        ):
            with pytest.raises(ProbeModelUpstreamError) as exc_info:
                probe_model_info("http://h:1")
        # The status code is surfaced in the message so the inline-form
        # banner can distinguish a 503 from a 504 / 404.
        assert "HTTP 503" in (exc_info.value.description or "")

    def test_upstream_fetch_failure_raises_502(self) -> None:
        # Connection refused, DNS failure, SSRF block — any RequestError
        # bubbles up from ssrf_proxy and the handler converts it to 502
        # rather than letting the 500 default mask the diagnostic.
        with patch(
            "controllers.console.workflow_probe_model.ssrf_proxy.get",
            side_effect=httpx.ConnectError("connection refused"),
        ):
            with pytest.raises(ProbeModelUpstreamError):
                probe_model_info("http://h:1")

    def test_upstream_non_json_raises_502(self) -> None:
        upstream = self._mock_response(200, raise_on_json=True)
        with patch(
            "controllers.console.workflow_probe_model.ssrf_proxy.get",
            return_value=upstream,
        ):
            with pytest.raises(ProbeModelUpstreamError):
                probe_model_info("http://h:1")

    def test_upstream_empty_model_list_raises_502(self) -> None:
        upstream = self._mock_response(200, {"data": [], "models": []})
        with patch(
            "controllers.console.workflow_probe_model.ssrf_proxy.get",
            return_value=upstream,
        ):
            with pytest.raises(ProbeModelUpstreamError) as exc_info:
                probe_model_info("http://h:1")
        assert "no model" in (exc_info.value.description or "")
