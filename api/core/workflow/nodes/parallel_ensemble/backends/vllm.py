"""vLLM-compatible completion backend for token-level ensemble hotfixes.

This adapter is intentionally narrow: it supports raw completion prompts
and token-step probabilities through the OpenAI-compatible
``/v1/completions`` endpoint that vLLM exposes, but it does not expose a
server-side chat-template capability. That absence is important because
the parallel-ensemble node uses ``Capability.CHAT_TEMPLATE`` as the gate
for calling ``apply_template``.
"""

from __future__ import annotations

import json
import logging
import math
from typing import TYPE_CHECKING, Any, ClassVar, Literal

from pydantic import AnyUrl, Field

from ..exceptions import ParallelEnsembleError
from ..registry.backend_registry import register_backend
from ..spi.backend import (
    BaseSpec,
    GenerationParams,
    GenerationResult,
    ModelBackend,
    TokenCandidate,
    TokenStepParams,
)
from ..spi.capability import Capability

if TYPE_CHECKING:
    from ..spi.requirements import Requirement, ValidationIssue

logger = logging.getLogger(__name__)

_VLLM_CAPABILITIES: frozenset[Capability] = frozenset(
    {
        Capability.TOKEN_STEP,
        Capability.TOP_PROBS,
        Capability.POST_SAMPLING_PROBS,
    }
)

_END_TOKEN_SENTINEL = "<end>"
_DEFAULT_HEADERS = {"Content-Type": "application/json"}


class VllmResponseError(ParallelEnsembleError):
    """Raised when a vLLM completion response lacks usable logprobs."""

    def __init__(self, reason: str, payload: object | None = None):
        self.reason = reason
        self.payload = payload
        excerpt = _payload_excerpt(payload)
        suffix = f"; payload={excerpt}" if excerpt else ""
        super().__init__(f"vLLM backend response error: {reason}{suffix}")


class VllmSpec(BaseSpec):
    """Schema for a vLLM-style token completion endpoint."""

    backend: Literal["vllm"]  # pyright: ignore[reportIncompatibleVariableOverride]
    model_url: AnyUrl
    EOS: str = Field(min_length=1)
    type: Literal["normal", "think"] = "normal"
    stop_think: str | None = None
    expose_raw_logits: bool = False


def _payload_excerpt(payload: object | None, *, limit: int = 500) -> str:
    if payload is None:
        return ""
    try:
        text = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    except TypeError:
        text = repr(payload)
    if len(text) <= limit:
        return text
    return f"{text[:limit]}..."


def _filtered_params(params: GenerationParams) -> dict[str, Any]:
    return {k: v for k, v in params.items() if v is not None}


def _candidate_token(token: object, eos: str) -> str:
    value = "" if token is None else str(token)
    if value in ("", eos):
        return _END_TOKEN_SENTINEL
    return value


def _coerce_logprob(value: object) -> float | None:
    if isinstance(value, dict):
        value = value.get("logprob")
    try:
        logprob = float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None
    if not math.isfinite(logprob):
        return None
    return logprob


def _parse_logprob_map(raw: dict[str, Any], eos: str) -> list[tuple[str, float]]:
    out: list[tuple[str, float]] = []
    for token, value in raw.items():
        logprob = _coerce_logprob(value)
        if logprob is None:
            continue
        out.append((_candidate_token(token, eos), logprob))
    return out


def _parse_logprob_items(raw: list[Any], eos: str) -> list[tuple[str, float]]:
    if not raw:
        return []

    # Legacy OpenAI completion shape nests the first generated token as
    # ``top_logprobs: [{token: logprob, ...}]``.
    if len(raw) == 1 and isinstance(raw[0], dict) and "token" not in raw[0]:
        return _parse_logprob_map(raw[0], eos)

    out: list[tuple[str, float]] = []
    for item in raw:
        if isinstance(item, dict) and "token" in item:
            logprob = _coerce_logprob(item.get("logprob"))
            if logprob is None:
                continue
            out.append((_candidate_token(item.get("token"), eos), logprob))
            continue
        if isinstance(item, dict):
            out.extend(_parse_logprob_map(item, eos))
    return out


def _first_top_logprobs(payload: dict[str, Any]) -> object | None:
    completion_probabilities = payload.get("completion_probabilities")
    if isinstance(completion_probabilities, list) and completion_probabilities:
        head = completion_probabilities[0]
        if isinstance(head, dict) and "top_logprobs" in head:
            return head["top_logprobs"]

    choices = payload.get("choices")
    if isinstance(choices, list) and choices:
        choice = choices[0]
        if isinstance(choice, dict):
            logprobs = choice.get("logprobs")
            if isinstance(logprobs, dict):
                top_logprobs = logprobs.get("top_logprobs")
                if isinstance(top_logprobs, list) and top_logprobs:
                    return top_logprobs[0]
                if top_logprobs is not None:
                    return top_logprobs
                content = logprobs.get("content")
                if isinstance(content, list) and content:
                    first = content[0]
                    if isinstance(first, dict) and "top_logprobs" in first:
                        return first["top_logprobs"]

    if "top_logprobs" in payload:
        return payload["top_logprobs"]
    return None


def parse_vllm_top_logprobs(payload: dict[str, Any], eos: str) -> list[TokenCandidate]:
    """Convert returned vLLM log-softmax candidates into top-k probs.

    vLLM/OpenAI-compatible ``top_logprobs`` are log probabilities, not
    raw logits. The ensemble SPI expects normalized probabilities in
    ``TokenCandidate.prob`` and reserves ``TokenCandidate.logit`` for
    actual raw logits, so this function exponentiates and re-normalizes
    over the returned candidate set while leaving ``logit`` as ``None``.
    """
    raw = _first_top_logprobs(payload)
    if raw is None:
        raise VllmResponseError("missing top_logprobs for generated token", payload)

    if isinstance(raw, dict):
        parsed = _parse_logprob_map(raw, eos)
    elif isinstance(raw, list):
        parsed = _parse_logprob_items(raw, eos)
    else:
        raise VllmResponseError("top_logprobs has unsupported shape", payload)

    if not parsed:
        raise VllmResponseError("top_logprobs did not contain numeric logprobs", payload)

    pivot = max(logprob for _, logprob in parsed)
    exp_values = [math.exp(logprob - pivot) for _, logprob in parsed]
    total = sum(exp_values)
    if total <= 0.0 or not math.isfinite(total):
        raise VllmResponseError("top_logprobs normalization failed", payload)

    return [
        TokenCandidate(token=token, prob=exp_value / total, logit=None)
        for (token, _), exp_value in zip(parsed, exp_values)
    ]


@register_backend("vllm")
class VllmBackend(ModelBackend):
    """Raw completion adapter for vLLM-style token ensemble endpoints."""

    spec_class: ClassVar[type[BaseSpec]] = VllmSpec

    @classmethod
    def capabilities(cls, spec: BaseSpec) -> frozenset[Capability]:
        del spec
        return _VLLM_CAPABILITIES

    @classmethod
    def validate_requirements(
        cls,
        spec: BaseSpec,
        requirements: list[Requirement],
    ) -> list[ValidationIssue]:
        del spec
        issues: list[ValidationIssue] = []
        for req in requirements:
            kind = req.get("kind")
            value = req.get("value")
            if kind == "needs_chat_template" and bool(value):
                issues.append(
                    {
                        "severity": "error",
                        "requirement": req,
                        "message": (
                            "vLLM backend does not advertise CHAT_TEMPLATE; "
                            "use prompt_template/raw completion or a backend "
                            "with explicit chat-template support."
                        ),
                        "i18n_key": "parallelEnsemble.errors.vllmNoChatTemplate",
                    }
                )
            elif kind == "needs_function_calling" and bool(value):
                issues.append(
                    {
                        "severity": "error",
                        "requirement": req,
                        "message": "vLLM backend does not advertise FUNCTION_CALLING.",
                        "i18n_key": "parallelEnsemble.errors.vllmNoFunctionCalling",
                    }
                )
        return issues

    def _spec_as_vllm(self) -> VllmSpec:
        assert isinstance(self._spec, VllmSpec)
        return self._spec

    def _base_url(self) -> str:
        return str(self._spec_as_vllm().model_url).rstrip("/")

    def _timeout_seconds(self) -> float:
        return self._spec_as_vllm().request_timeout_ms / 1000.0

    def _post_json(self, path: str, body: dict[str, Any]) -> Any:
        url = f"{self._base_url()}{path}"
        response = self._http.post(  # type: ignore[attr-defined]
            url,
            json=body,
            headers=_DEFAULT_HEADERS,
            timeout=self._timeout_seconds(),
        )
        response.raise_for_status()
        try:
            return json.loads(response.text)
        except json.JSONDecodeError as exc:
            raise VllmResponseError("response body is not valid JSON", response.text) from exc

    def generate(self, prompt: str, params: GenerationParams) -> GenerationResult:
        body: dict[str, Any] = {
            "model": self.model_name,
            "prompt": prompt,
            **_filtered_params(params),
        }
        body["stream"] = False
        payload = self._post_json("/v1/completions", body)
        text = ""
        finish_reason = "stop"
        metadata: dict[str, Any] = {}
        if isinstance(payload, dict):
            if isinstance(payload.get("content"), str):
                text = payload["content"]
            choices = payload.get("choices")
            if isinstance(choices, list) and choices and isinstance(choices[0], dict):
                choice = choices[0]
                if isinstance(choice.get("text"), str):
                    text = choice["text"]
                if isinstance(choice.get("finish_reason"), str) and choice["finish_reason"]:
                    finish_reason = choice["finish_reason"]
            for key in ("generation_settings", "usage"):
                value = payload.get(key)
                if isinstance(value, dict):
                    metadata[key] = value
        return GenerationResult(text=text, finish_reason=finish_reason, metadata=metadata)

    def step_token(self, prompt: str, params: TokenStepParams) -> list[TokenCandidate]:
        body: dict[str, Any] = {
            "model": self.model_name,
            "prompt": prompt,
            "max_tokens": 1,
            "logprobs": params.top_k,
        }
        if params.temperature is not None:
            body["temperature"] = params.temperature
        if params.top_p is not None:
            body["top_p"] = params.top_p
        if params.stop:
            body["stop"] = list(params.stop)
        if params.seed is not None:
            body["seed"] = params.seed
        if params.extra:
            body.update(params.extra)
        body["max_tokens"] = 1

        payload = self._post_json("/v1/completions", body)
        if not isinstance(payload, dict):
            raise VllmResponseError("completion response is not a JSON object", payload)
        return parse_vllm_top_logprobs(payload, eos=self._spec_as_vllm().EOS)
