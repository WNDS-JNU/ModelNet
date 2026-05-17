"""Server-side proxy for the token-model-source ``Fetch model info`` button.

The inline-spec-form panel used to ``fetch('${model_url}/v1/models')``
straight from the browser. That works for llama.cpp (CORS on by default)
but fails on vLLM / TGI / SGLang / hosted routers (no CORS), so the
button errors out for every OpenAI-compatible server except llama.cpp.
Moving the probe server-side bypasses CORS entirely; the request still
travels through ``ssrf_proxy`` so the same egress / SSRF guards apply
as any other workflow-node-issued HTTP call.

Returns only the first model id the upstream reports — the inline form
uses that one value to fill ``model_name`` and discards the rest.
"""

from __future__ import annotations

import json
import logging
from typing import Any
from urllib.parse import urlparse, urlunparse

from flask import request
from flask_restx import Resource

from controllers.console import console_ns
from controllers.console.wraps import account_initialization_required, setup_required
from core.helper import ssrf_proxy
from libs.exception import BaseHTTPException
from libs.login import login_required

logger = logging.getLogger(__name__)

# Cap the probe at a single attempt — the user clicked a button and is
# watching the spinner; retrying three times with backoff (the ssrf
# default) would push the worst-case wait past 20s for a misconfigured
# URL. The button is cheap to click again.
_PROBE_MAX_RETRIES = 0

# Total wall-clock budget for the upstream call. Generous enough for a
# cold vLLM ``/v1/models`` (which lists every loaded model) but short
# enough that a hung server doesn't leave the UI spinning forever.
_PROBE_TIMEOUT_SECONDS = 10.0


class ProbeModelMalformedURLError(BaseHTTPException):
    error_code = "probe_model_malformed_url"
    description = "model_url must be an http(s) URL with a host."
    code = 400


class ProbeModelUpstreamError(BaseHTTPException):
    error_code = "probe_model_upstream_error"
    description = "Upstream /v1/models probe failed."
    code = 502


def _build_probe_url(raw: str) -> str | None:
    """Mirror ``buildModelsProbeUrl`` in inline-spec-form.tsx.

    Returns ``None`` when ``raw`` is missing scheme / host or is not
    http(s); callers map ``None`` to a 400. Preserves any user-typed
    path prefix so hosted routers that scope one model per path
    (e.g. ``…/tencent/Hunyuan…``) still resolve to a real endpoint
    after the ``/v1/models`` suffix is appended.
    """
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
    """Pull a model id from the two OpenAI-compatible response shapes.

    ``data[].id`` is what vLLM / llama.cpp / TGI / SGLang all emit
    (the canonical OpenAI shape). ``models[].name`` is llama.cpp's
    native field — kept as a fallback so a server with only the
    native endpoint enabled still works.
    """
    if not isinstance(payload, dict):
        return None
    data = payload.get("data")
    if isinstance(data, list) and data:
        first = data[0]
        if isinstance(first, dict):
            mid = first.get("id")
            if isinstance(mid, str) and mid:
                return mid
    models = payload.get("models")
    if isinstance(models, list) and models:
        first = models[0]
        if isinstance(first, dict):
            name = first.get("name")
            if isinstance(name, str) and name:
                return name
    return None


def probe_model_info(raw_url: str | None) -> dict[str, str]:
    """Run the full probe pipeline against ``raw_url``.

    Extracted from the Resource method so the unit-test suite can hit
    the entire URL-build → ssrf_proxy.get → parse path without standing
    up a Flask request context or bypassing auth decorators. Raises
    ``ProbeModelMalformedURLError`` (400) or ``ProbeModelUpstreamError``
    (502) on any failure; the Flask error handler renders the right
    status code + ``{code, message, status}`` body from there.
    """
    if not isinstance(raw_url, str) or not raw_url.strip():
        raise ProbeModelMalformedURLError(description="url is required")

    probe_url = _build_probe_url(raw_url.strip())
    if probe_url is None:
        raise ProbeModelMalformedURLError()

    try:
        response = ssrf_proxy.get(
            probe_url,
            max_retries=_PROBE_MAX_RETRIES,
            timeout=_PROBE_TIMEOUT_SECONDS,
        )
    except Exception as exc:
        # Network-level failure (DNS, refused, timeout, SSRF block).
        # Log at info — this is user-driven, not a system fault.
        logger.info("probe-model fetch failed for %s: %s", probe_url, exc)
        raise ProbeModelUpstreamError(description=f"fetch failed: {exc}")

    if response.status_code // 100 != 2:
        raise ProbeModelUpstreamError(
            description=f"HTTP {response.status_code} from upstream",
        )

    try:
        payload = response.json()
    except (json.JSONDecodeError, ValueError) as exc:
        raise ProbeModelUpstreamError(description=f"non-JSON response: {exc}")

    model_name = _extract_first_model_id(payload)
    if not model_name:
        raise ProbeModelUpstreamError(description="no model in response")

    return {"model_name": model_name}


@console_ns.route("/workflow/probe-model-info")
class ProbeModelInfoApi(Resource):
    """``POST /console/api/workflow/probe-model-info``.

    Body: ``{"url": "<model_url>"}``. Response: ``{"model_name": "..."}``.
    """

    @setup_required
    @login_required
    @account_initialization_required
    def post(self):
        body = request.get_json(silent=True) or {}
        return probe_model_info(body.get("url")), 200
