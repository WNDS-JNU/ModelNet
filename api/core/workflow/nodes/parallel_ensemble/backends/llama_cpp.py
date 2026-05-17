"""``LlamaCppBackend`` — production SPI implementation for self-hosted llama.cpp.

P2.2 lands the runtime: ``capabilities`` / ``validate_requirements`` /
``generate`` / ``generate_stream`` / ``step_token`` / ``apply_template``.
HTTP traffic is routed through whatever ``HttpClientProtocol`` instance
the framework injects — production wiring hands in
``core.helper.ssrf_proxy.graphon_ssrf_proxy`` (the graphon-typed adapter)
so the URLs from ``api/configs/model_net.yaml`` cannot be reached except
through the deployment's SSRF proxy (ADR-8 / EXTENSIBILITY_SPEC §4.4 T4).
Bodies are decoded via ``json.loads(response.text)`` because the graphon
``HttpResponse`` deliberately exposes only ``text`` / ``content`` /
``raise_for_status`` — there is no ``.json()`` on that contract.

Wire shape mirrors PN.py (``docs/ModelNet/PN.py``) so the existing
research workload upgrades by swapping the orchestration layer rather
than the request bodies. The two functions split out at module scope
(``parse_top_probs`` / ``parse_sse_chunks``) are the ones a Phase 4
fork is most likely to want to reuse / re-mock without taking on the
full backend class — promoting them avoids a "private utility from
inside a class" import that ages badly.
"""

from __future__ import annotations

import json
import logging
import math
from collections.abc import Iterable, Iterator
from typing import TYPE_CHECKING, Any, ClassVar, Literal

from pydantic import AnyUrl, Field

from ..registry.backend_registry import register_backend
from ..spi.backend import (
    BaseSpec,
    ChatMessage,
    GenerationParams,
    GenerationResult,
    ModelBackend,
    StreamChunk,
    TokenCandidate,
    TokenStepParams,
)
from ..spi.capability import Capability

if TYPE_CHECKING:  # avoid runtime cycle through spi.requirements
    from ..spi.requirements import Requirement, ValidationIssue

logger = logging.getLogger(__name__)

_LLAMA_CPP_CAPABILITIES: frozenset[Capability] = frozenset(
    {
        Capability.STREAMING,
        Capability.TOKEN_STEP,
        Capability.TOP_PROBS,
        Capability.POST_SAMPLING_PROBS,
        Capability.CHAT_TEMPLATE,
    }
)
"""Capability set stock llama.cpp ships out of the box.

`LOGITS_RAW` is intentionally absent — `post_sampling_probs=true` is
top-k re-normalised, not raw logits (see EXTENSIBILITY_SPEC §3.2 trap 1).
Specs that opt into the raw-logit fork contract via
``expose_raw_logits=true`` add ``LOGITS_RAW`` at runtime and make
``step_token`` request raw mode."""

_END_TOKEN_SENTINEL = "<end>"
"""PN.py's canonical end-of-stream marker; preserved as the public
contract for downstream aggregators rather than passing the raw EOS
through, since the EOS varies per model."""

_DEFAULT_HEADERS = {"Content-Type": "application/json"}


class LlamaCppSpec(BaseSpec):
    """yaml schema for a single self-hosted llama.cpp endpoint.

    ``backend`` is locked to ``"llama_cpp"`` via ``Literal`` so loading
    a yaml entry that mistakenly points at this spec class with a
    different backend string fails at pydantic validation rather than
    silently mis-routing. The pyright ``reportIncompatibleVariableOverride``
    suppression is the documented pydantic pattern for narrowing a tag
    field on a discriminator-bearing subclass — pydantic resolves the
    Literal at validate time even though pyright treats variable
    overrides as invariant.
    """

    backend: Literal["llama_cpp"]  # pyright: ignore[reportIncompatibleVariableOverride]
    model_arch: str = "llama"
    model_url: AnyUrl
    EOS: str = Field(min_length=1)
    type: Literal["normal", "think"] = "normal"
    stop_think: str | None = None
    expose_raw_logits: bool = False


# ── Pure parsing helpers (module-scope so tests / forks can re-use) ────


def _fallback_end_candidate() -> list[TokenCandidate]:
    return [TokenCandidate(token=_END_TOKEN_SENTINEL, prob=0.01, logit=None)]


def _candidate_token(item: dict[str, Any], eos: str) -> str:
    token = item.get("token", "")
    if token in ("", eos):
        token = _END_TOKEN_SENTINEL
    return str(token)


def _candidate_logit(item: dict[str, Any]) -> float | None:
    for key in ("logit", "raw_logit"):
        value = item.get(key)
        if value is None:
            continue
        try:
            return float(value)
        except (TypeError, ValueError):
            return None
    return None


def _softmax(values: list[float]) -> list[float]:
    """Numerically stable softmax over the returned top-k raw logits."""
    if not values:
        return []
    pivot = max(values)
    exps = [math.exp(v - pivot) for v in values]
    total = sum(exps)
    if total <= 0.0 or not math.isfinite(total):
        return [1.0 / len(values) for _ in values]
    return [v / total for v in exps]


def parse_top_probs(payload: dict[str, Any], eos: str, *, raw_logits: bool = False) -> list[TokenCandidate]:
    """Extract the top-k candidates llama.cpp returns for a single token step.

    R7 (TASKS.md): freeze the ``top_probs`` schema in one place.

    Contract on input ``payload``: the ``json.loads(response.text)``
    of a ``POST /completion`` call with
    ``max_tokens=1, n_probs=k, post_sampling_probs=true``.
    Expected shape::

        {
          "completion_probabilities": [
            {"top_probs": [{"token": str, "prob": float, "bytes": [...]}, ...],
             ...}
          ],
          "content": "...",
          ...
        }

    In raw-logit mode llama.cpp returns ``top_logprobs`` when
    ``post_sampling_probs=false``. Some patched deployments kept the older
    ``top_probs`` spelling while adding ``logit`` / ``raw_logit`` fields, so
    the parser accepts both shapes.

    PN.py rewrites the EOS / empty-string token to ``"<end>"`` so a
    downstream aggregator can compare across models with different EOS
    markers. We preserve that contract here — the runner / aggregator
    do not need to know which model produced which candidate.

    ``raw_logits=True`` is the patched llama.cpp contract used by the
    DuetNet reproduction path: each item must expose ``logit`` (or the
    compatibility spelling ``raw_logit``). The adapter then fills
    ``TokenCandidate.logit`` and synthesises a top-k probability
    distribution with softmax so existing ``TOP_PROBS`` aggregators
    still see a usable ``prob`` value.
    """
    completion_probabilities = payload.get("completion_probabilities") or []
    if not isinstance(completion_probabilities, list) or not completion_probabilities:
        return _fallback_end_candidate()
    head = completion_probabilities[0]
    if not isinstance(head, dict):
        return _fallback_end_candidate()
    if raw_logits:
        raw_top = head.get("top_logprobs")
        if raw_top is None:
            raw_top = head.get("top_probs")
    else:
        raw_top = head.get("top_probs")
    raw_top = raw_top or []
    if not isinstance(raw_top, list):
        return _fallback_end_candidate()

    if raw_logits:
        raw_candidates: list[tuple[str, float]] = []
        for item in raw_top:
            if not isinstance(item, dict):
                continue
            logit = _candidate_logit(item)
            if logit is None:
                continue
            raw_candidates.append((_candidate_token(item, eos), logit))
        if not raw_candidates:
            return _fallback_end_candidate()
        probs = _softmax([logit for _, logit in raw_candidates])
        return [
            TokenCandidate(token=token, prob=prob, logit=logit)
            for (token, logit), prob in zip(raw_candidates, probs)
        ]

    out: list[TokenCandidate] = []
    for item in raw_top:
        if not isinstance(item, dict):
            continue
        prob = item.get("prob", 0.0)
        out.append(TokenCandidate(token=_candidate_token(item, eos), prob=float(prob), logit=None))
    if not out:
        # /completion without top_probs (e.g. content-only response) means
        # the model did not advance the generation — surface as <end> so
        # the aggregator terminates cleanly.
        out.extend(_fallback_end_candidate())
    return out


def parse_sse_chunks(body: str) -> Iterator[StreamChunk]:
    """Iterate ``data: {...}`` SSE lines from a llama.cpp ``stream=true`` body.

    The current ``ssrf_proxy`` helper buffers the response, so the
    ``Iterator`` here delivers chunks once the server has finished —
    semantically correct (yields each ``content`` delta in order) but
    not real-time. P2.13 verifies the dev-server end-to-end behaviour;
    a future ssrf-streaming primitive would let this become true
    incremental delivery.

    Lines that fail JSON parse are skipped with a debug log so a
    half-streamed response (network blip mid-line) doesn't crash the
    runner mid-generation.
    """
    saw_final = False
    for raw_line in body.splitlines():
        line = raw_line.strip()
        if not line or not line.startswith("data:"):
            continue
        data = line[len("data:") :].strip()
        if not data:
            continue
        try:
            payload = json.loads(data)
        except json.JSONDecodeError:
            logger.debug("dropping unparseable SSE line: %r", line)
            continue
        delta = payload.get("content", "")
        is_final = bool(payload.get("stop"))
        if is_final:
            saw_final = True
        yield StreamChunk(delta=str(delta), is_final=is_final)
    if not saw_final:
        # Defensive: server didn't close cleanly; emit a final empty
        # chunk so downstream consumers can finalise their bookkeeping
        # without special-casing this path.
        yield StreamChunk(delta="", is_final=True)


def _filtered_params(params: GenerationParams) -> dict[str, Any]:
    """Drop ``None`` values so the body matches llama.cpp's expected shape."""
    return {k: v for k, v in params.items() if v is not None}


@register_backend("llama_cpp")
class LlamaCppBackend(ModelBackend):
    """Self-hosted llama.cpp adapter (PN.py wire-compatible).

    Subclasses Phase 4 might want to override:
      - ``capabilities`` — for a fork that adds e.g. ``LOGITS_RAW``;
      - ``validate_requirements`` — to surface fork-specific limits;
      - ``apply_template`` — to swap to a client-side template engine.

    The class is created per ``(alias × workflow run)``; ``self._http``
    is the ``HttpClientProtocol`` the framework injects (always
    ``graphon_ssrf_proxy`` in production — see ``node_factory.py``;
    its responses follow the graphon ``HttpResponse`` shape, so
    ``_post_json`` decodes via ``response.text``).
    """

    spec_class: ClassVar[type[BaseSpec]] = LlamaCppSpec

    @classmethod
    def capabilities(cls, spec: BaseSpec) -> frozenset[Capability]:
        """Return capabilities for this llama.cpp spec.

        Stock endpoints expose post-sampling top-k probabilities only.
        The ModelNet DuetNet path uses a patched llama.cpp endpoint and
        opts in with ``expose_raw_logits=true``; only that spec advertises
        ``LOGITS_RAW`` so strict logit aggregators fail fast on ordinary
        endpoints.
        """
        if isinstance(spec, LlamaCppSpec) and spec.expose_raw_logits:
            return _LLAMA_CPP_CAPABILITIES | {Capability.LOGITS_RAW}
        return _LLAMA_CPP_CAPABILITIES

    @classmethod
    def validate_requirements(
        cls,
        spec: BaseSpec,
        requirements: list[Requirement],
    ) -> list[ValidationIssue]:
        """Return validation issues for any requirement llama.cpp can't meet.

        llama.cpp has no hard ``top_k`` cap (unlike OpenAI 20 / vLLM
        per-deploy) and exposes logprobs / chat templates natively, so
        the only requirements the framework can statically reject here
        are ones tied to capabilities llama.cpp does not declare —
        primarily ``needs_function_calling``, which the stock build
        does not surface.
        """
        del spec  # llama.cpp validation does not differ across specs today.
        issues: list[ValidationIssue] = []
        for req in requirements:
            kind = req.get("kind")
            value = req.get("value")
            if kind == "needs_function_calling" and bool(value):
                issues.append(
                    {
                        "severity": "error",
                        "requirement": req,
                        "message": (
                            "llama.cpp backend does not advertise "
                            "FUNCTION_CALLING; switch to an openai_compat "
                            "backend or a fork that exposes tool_choice."
                        ),
                        "i18n_key": "parallelEnsemble.errors.llamaCppNoFunctionCalling",
                    }
                )
        return issues

    # ── HTTP helpers ──────────────────────────────────────────────────

    def _base_url(self) -> str:
        # ``AnyUrl`` always renders trailing slashes when the path is
        # empty (``http://h:1/``). llama.cpp endpoints want the path
        # appended bare, so trim once at the boundary.
        return str(self._spec_as_llama().model_url).rstrip("/")

    def _spec_as_llama(self) -> LlamaCppSpec:
        # The framework guarantees by construction that ``self._spec``
        # is a ``LlamaCppSpec`` (via ``BackendRegistry.get_spec_class``),
        # but we narrow explicitly so methods below get IDE-level field
        # access on ``EOS`` / ``model_url`` without ``# type: ignore``.
        assert isinstance(self._spec, LlamaCppSpec)
        return self._spec

    def _timeout_seconds(self) -> float:
        return self._spec_as_llama().request_timeout_ms / 1000.0

    def _post_json(self, path: str, body: dict[str, Any]) -> Any:
        url = f"{self._base_url()}{path}"
        # ``self._http`` follows ``HttpClientProtocol`` (see
        # ``graphon.nodes.protocols``); production wiring injects
        # ``graphon_ssrf_proxy`` so the URL is reachable only via the
        # SSRF proxy. Decode via ``response.text`` rather than
        # ``response.json()`` because graphon's ``HttpResponse`` only
        # exposes the transport-agnostic surface (text/content/
        # raise_for_status); calling ``.json()`` would AttributeError
        # against the production client even though httpx-style fakes
        # define it.
        response = self._http.post(  # type: ignore[attr-defined]
            url,
            json=body,
            headers=_DEFAULT_HEADERS,
            timeout=self._timeout_seconds(),
        )
        response.raise_for_status()
        try:
            return json.loads(response.text)
        except json.JSONDecodeError:
            return None

    # ── SPI methods ───────────────────────────────────────────────────

    def generate(self, prompt: str, params: GenerationParams) -> GenerationResult:
        body: dict[str, Any] = {"prompt": prompt, **_filtered_params(params)}
        body["stream"] = False
        payload = self._post_json("/completion", body)
        text = payload.get("content", "") if isinstance(payload, dict) else ""
        finish_reason = "stop"
        if isinstance(payload, dict):
            # llama.cpp surfaces stop reason in ``stop_type`` (truncate /
            # eos / limit / abort). Map ``limit`` to the openai-style
            # ``length`` so cross-backend metadata stays portable.
            stop_type = payload.get("stop_type")
            if stop_type == "limit":
                finish_reason = "length"
            elif isinstance(stop_type, str) and stop_type:
                finish_reason = stop_type
        metadata: dict[str, Any] = {}
        if isinstance(payload, dict):
            settings = payload.get("generation_settings")
            if isinstance(settings, dict):
                metadata["generation_settings"] = settings
        return GenerationResult(text=str(text), finish_reason=finish_reason, metadata=metadata)

    def generate_stream(self, prompt: str, params: GenerationParams) -> Iterator[StreamChunk]:
        body: dict[str, Any] = {"prompt": prompt, **_filtered_params(params)}
        body["stream"] = True
        url = f"{self._base_url()}/completion"
        response = self._http.post(  # type: ignore[attr-defined]
            url,
            json=body,
            headers=_DEFAULT_HEADERS,
            timeout=self._timeout_seconds(),
        )
        response.raise_for_status()
        # ``response.text`` is the buffered SSE body; see
        # ``parse_sse_chunks`` for why this is buffered rather than
        # truly incremental.
        return parse_sse_chunks(response.text)

    def step_token(self, prompt: str, params: TokenStepParams) -> list[TokenCandidate]:
        # Apply every per-call sampling knob to the llama.cpp request body
        # so the runner can vary temperature / top_p / seed / stop / max_tokens
        # across the same backend instance (ADR-v3-14: lets self-consistency
        # research use one backend with different temperatures per step).
        body: dict[str, Any] = {
            "prompt": prompt,
            "max_tokens": params.max_tokens,
            "n_probs": params.top_k,
            "post_sampling_probs": not self._spec_as_llama().expose_raw_logits,
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
            # Backend-specific knobs ride on ``extra``; the runner-side
            # contract is pass-through, so a fork that adds e.g. mirostat
            # picks it up here without changing the SPI surface.
            body.update(params.extra)
        payload = self._post_json("/completion", body)
        if not isinstance(payload, dict):
            return _fallback_end_candidate()
        spec = self._spec_as_llama()
        return parse_top_probs(payload, eos=spec.EOS, raw_logits=spec.expose_raw_logits)

    def apply_template(self, messages: list[ChatMessage]) -> str:
        # Cast to ``Iterable`` so the json body is a plain list of
        # dicts; the TypedDict shape carries through directly.
        msgs: Iterable[ChatMessage] = messages
        body = {"messages": list(msgs)}
        payload = self._post_json("/apply-template", body)
        if isinstance(payload, dict):
            prompt = payload.get("prompt", "")
            if isinstance(prompt, str):
                return prompt
        # Empty string mirrors PN.py's behaviour on a malformed
        # response — a runner that gets "" can either re-raise or fall
        # back to ``ModelBackend.apply_template``'s naive join.
        logger.warning(
            "apply_template returned malformed payload from %s; falling back to empty",
            self.id,
        )
        return ""
