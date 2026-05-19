"""vLLM chat-completions backend for token-level ensemble voting.

Unlike the raw ``vllm`` backend, this adapter preserves chat/instruct
semantics by sending structured messages to vLLM's OpenAI-compatible
``/v1/chat/completions`` endpoint. The runner SPI still carries a string
prompt, so ``apply_template`` encodes the original messages into a
private prompt envelope. The token runner appends selected tokens to the
envelope suffix; ``step_token`` decodes that suffix as the assistant
prefix and asks vLLM to continue the final assistant message.
"""

from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING, Any, ClassVar, Literal

from pydantic import AnyUrl, Field

from ..registry.backend_registry import register_backend
from ..spi.backend import (
    BaseSpec,
    ChatMessage,
    GenerationParams,
    GenerationResult,
    ModelBackend,
    TokenCandidate,
    TokenStepParams,
)
from ..spi.capability import Capability
from .vllm import VllmResponseError, parse_vllm_top_logprobs

if TYPE_CHECKING:
    from ..spi.requirements import Requirement, ValidationIssue

logger = logging.getLogger(__name__)

_VLLM_CHAT_CAPABILITIES: frozenset[Capability] = frozenset(
    {
        Capability.TOKEN_STEP,
        Capability.TOP_PROBS,
        Capability.POST_SAMPLING_PROBS,
        Capability.CHAT_TEMPLATE,
    }
)

_DEFAULT_HEADERS = {"Content-Type": "application/json"}
_END_TOKEN_SENTINEL = "<end>"
_ENVELOPE_PREFIX = "__dify_vllm_chat_prompt_v1__\n"
_ASSISTANT_PREFIX_MARKER = "\n__dify_vllm_chat_assistant_prefix__\n"


class VllmChatSpec(BaseSpec):
    """Schema for a vLLM chat-completions token endpoint."""

    backend: Literal["vllm_chat"]  # pyright: ignore[reportIncompatibleVariableOverride]
    model_url: AnyUrl
    EOS: str = Field(min_length=1)
    type: Literal["normal"] = "normal"
    stop_think: str | None = None
    expose_raw_logits: bool = False


def _filtered_params(params: GenerationParams) -> dict[str, Any]:
    return {k: v for k, v in params.items() if v is not None}


def _validated_messages(raw: object) -> list[ChatMessage]:
    if not isinstance(raw, list) or not raw:
        raise VllmResponseError("chat prompt envelope messages must be a non-empty list", raw)

    messages: list[ChatMessage] = []
    for idx, item in enumerate(raw):
        if not isinstance(item, dict):
            raise VllmResponseError(f"chat prompt envelope messages[{idx}] is not an object", raw)
        role = item.get("role")
        content = item.get("content")
        if not isinstance(role, str) or not role:
            raise VllmResponseError(f"chat prompt envelope messages[{idx}].role is invalid", raw)
        if not isinstance(content, str):
            raise VllmResponseError(f"chat prompt envelope messages[{idx}].content is invalid", raw)
        messages.append({"role": role, "content": content})
    return messages


def encode_vllm_chat_prompt(messages: list[ChatMessage], assistant_prefix: str = "") -> str:
    """Encode chat messages into the runner's string prompt channel."""

    payload = {"messages": _validated_messages(messages)}
    return (
        _ENVELOPE_PREFIX
        + json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
        + _ASSISTANT_PREFIX_MARKER
        + assistant_prefix
    )


def decode_vllm_chat_prompt(prompt: str) -> tuple[list[ChatMessage], str]:
    """Decode the private vLLM chat prompt envelope."""

    if not prompt.startswith(_ENVELOPE_PREFIX):
        raise VllmResponseError(
            "vLLM chat backend expected a chat prompt envelope; "
            "use prompt_template/messages_template without raw_completion",
            prompt,
        )
    body = prompt[len(_ENVELOPE_PREFIX) :]
    try:
        payload_text, assistant_prefix = body.split(_ASSISTANT_PREFIX_MARKER, 1)
    except ValueError as exc:
        raise VllmResponseError("vLLM chat prompt envelope is missing assistant prefix marker", prompt) from exc
    try:
        payload = json.loads(payload_text)
    except json.JSONDecodeError as exc:
        raise VllmResponseError("vLLM chat prompt envelope JSON is invalid", prompt) from exc
    if not isinstance(payload, dict):
        raise VllmResponseError("vLLM chat prompt envelope JSON must be an object", payload)
    return _validated_messages(payload.get("messages")), assistant_prefix


@register_backend("vllm_chat")
class VllmChatBackend(ModelBackend):
    """Chat-completions adapter for vLLM token ensemble endpoints."""

    spec_class: ClassVar[type[BaseSpec]] = VllmChatSpec

    @classmethod
    def capabilities(cls, spec: BaseSpec) -> frozenset[Capability]:
        del spec
        return _VLLM_CHAT_CAPABILITIES

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
            if kind == "needs_function_calling" and bool(value):
                issues.append(
                    {
                        "severity": "error",
                        "requirement": req,
                        "message": "vLLM chat backend does not advertise FUNCTION_CALLING.",
                        "i18n_key": "parallelEnsemble.errors.vllmChatNoFunctionCalling",
                    }
                )
        return issues

    def _spec_as_vllm_chat(self) -> VllmChatSpec:
        assert isinstance(self._spec, VllmChatSpec)
        return self._spec

    def _base_url(self) -> str:
        return str(self._spec_as_vllm_chat().model_url).rstrip("/")

    def _timeout_seconds(self) -> float:
        return self._spec_as_vllm_chat().request_timeout_ms / 1000.0

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

    def apply_template(self, messages: list[ChatMessage]) -> str:
        return encode_vllm_chat_prompt(messages)

    def generate(self, prompt: str, params: GenerationParams) -> GenerationResult:
        body: dict[str, Any] = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}],
            **_filtered_params(params),
        }
        body["stream"] = False
        payload = self._post_json("/v1/chat/completions", body)

        text = ""
        finish_reason = "stop"
        metadata: dict[str, Any] = {}
        if isinstance(payload, dict):
            choices = payload.get("choices")
            if isinstance(choices, list) and choices and isinstance(choices[0], dict):
                choice = choices[0]
                message = choice.get("message")
                if isinstance(message, dict) and isinstance(message.get("content"), str):
                    text = message["content"]
                if isinstance(choice.get("finish_reason"), str) and choice["finish_reason"]:
                    finish_reason = choice["finish_reason"]
            usage = payload.get("usage")
            if isinstance(usage, dict):
                metadata["usage"] = usage
        return GenerationResult(text=text, finish_reason=finish_reason, metadata=metadata)

    def step_token(self, prompt: str, params: TokenStepParams) -> list[TokenCandidate]:
        messages, assistant_prefix = decode_vllm_chat_prompt(prompt)
        body: dict[str, Any] = {
            "model": self.model_name,
            "messages": messages,
            "max_tokens": 1,
            "logprobs": True,
            "top_logprobs": params.top_k,
        }

        if assistant_prefix:
            body["messages"] = [
                *messages,
                {"role": "assistant", "content": assistant_prefix},
            ]
            body["continue_final_message"] = True
            body["add_generation_prompt"] = False
        else:
            body["add_generation_prompt"] = True

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

        payload = self._post_json("/v1/chat/completions", body)
        if not isinstance(payload, dict):
            raise VllmResponseError("chat completion response is not a JSON object", payload)
        candidates = parse_vllm_top_logprobs(payload, eos=self._spec_as_vllm_chat().EOS)
        if not candidates:
            return [TokenCandidate(token=_END_TOKEN_SENTINEL, prob=0.01, logit=None)]
        return candidates
