"""vLLM chat-completions backend coverage."""

from __future__ import annotations

import json
import math
from typing import Any

import pytest
from pydantic import ValidationError

from core.workflow.nodes.parallel_ensemble.backends.vllm import VllmResponseError
from core.workflow.nodes.parallel_ensemble.backends.vllm_chat import (
    VllmChatBackend,
    VllmChatSpec,
    decode_vllm_chat_prompt,
    encode_vllm_chat_prompt,
)
from core.workflow.nodes.parallel_ensemble.registry import BackendRegistry
from core.workflow.nodes.parallel_ensemble.spi.backend import ChatMessage, TokenStepParams
from core.workflow.nodes.parallel_ensemble.spi.capability import Capability


class _FakeResponse:
    def __init__(self, payload: Any = None, text: str | None = None, status: int = 200) -> None:
        self.text = json.dumps(payload) if text is None else text
        self.status = status

    def raise_for_status(self) -> None:
        if self.status >= 400:
            raise AssertionError(f"unexpected status {self.status}")


class _FakeHttp:
    def __init__(self, response: _FakeResponse) -> None:
        self.response = response
        self.calls: list[dict[str, Any]] = []

    def post(self, url: str, **kwargs: Any):  # type: ignore[no-untyped-def]
        self.calls.append({"url": url, **kwargs})
        return self.response


def _spec(**overrides: Any) -> VllmChatSpec:
    base = {
        "id": "vc1",
        "backend": "vllm_chat",
        "model_name": "test-chat-model",
        "model_url": "http://vllm.test:8000",
        "EOS": "<|eos|>",
        "type": "normal",
    }
    base.update(overrides)
    return VllmChatSpec(**base)


def _chat_logprobs_payload() -> dict[str, Any]:
    return {
        "choices": [
            {
                "message": {"role": "assistant", "content": "2"},
                "finish_reason": "length",
                "logprobs": {
                    "content": [
                        {
                            "token": "2",
                            "top_logprobs": [
                                {"token": "2", "logprob": math.log(0.8)},
                                {"token": "3", "logprob": math.log(0.2)},
                            ],
                        }
                    ]
                },
            }
        ]
    }


def _chat_leading_whitespace_payload() -> dict[str, Any]:
    return {
        "choices": [
            {
                "message": {"role": "assistant", "content": "\n\nIt"},
                "finish_reason": "length",
                "logprobs": {
                    "content": [
                        {
                            "token": "\n\n",
                            "top_logprobs": [
                                {"token": "\n\n", "logprob": math.log(0.7)},
                                {"token": " This", "logprob": math.log(0.2)},
                                {"token": " It", "logprob": math.log(0.1)},
                            ],
                        },
                        {
                            "token": "It",
                            "top_logprobs": [
                                {"token": "It", "logprob": math.log(0.9)},
                                {"token": "This", "logprob": math.log(0.1)},
                            ],
                        },
                    ]
                },
            }
        ]
    }


def test_backend_registry_resolves_vllm_chat() -> None:
    assert BackendRegistry.get("vllm_chat") is VllmChatBackend
    assert BackendRegistry.get_spec_class("vllm_chat") is VllmChatSpec


def test_capabilities_include_chat_template_but_not_streaming() -> None:
    caps = VllmChatBackend.capabilities(_spec())
    assert caps == frozenset(
        {
            Capability.TOKEN_STEP,
            Capability.TOP_PROBS,
            Capability.POST_SAMPLING_PROBS,
            Capability.CHAT_TEMPLATE,
        }
    )
    assert Capability.STREAMING not in caps


def test_spec_requires_model_name_and_eos() -> None:
    with pytest.raises(ValidationError):
        VllmChatSpec(
            id="vc1",
            backend="vllm_chat",
            model_url="http://vllm.test:8000",
            EOS="<|eos|>",
        )
    with pytest.raises(ValidationError):
        _spec(EOS="")


def test_validate_requirements_rejects_function_calling_only() -> None:
    chat_issues = VllmChatBackend.validate_requirements(
        _spec(),
        [{"kind": "needs_chat_template", "value": True, "rationale": "messages_template"}],
    )
    assert chat_issues == []

    function_issues = VllmChatBackend.validate_requirements(
        _spec(),
        [{"kind": "needs_function_calling", "value": True, "rationale": "tools"}],
    )
    assert len(function_issues) == 1
    assert function_issues[0]["severity"] == "error"


def test_prompt_envelope_round_trips_messages_and_prefix() -> None:
    messages: list[ChatMessage] = [
        {"role": "system", "content": "Be terse."},
        {"role": "user", "content": "1+1=?"},
    ]

    prompt = encode_vllm_chat_prompt(messages, assistant_prefix="答案是")

    decoded_messages, decoded_prefix = decode_vllm_chat_prompt(prompt)
    assert decoded_messages == messages
    assert decoded_prefix == "答案是"


def test_invalid_prompt_envelope_raises() -> None:
    with pytest.raises(VllmResponseError, match="expected a chat prompt envelope"):
        decode_vllm_chat_prompt("raw prompt")


def test_step_token_without_prefix_posts_chat_logprob_request() -> None:
    http = _FakeHttp(_FakeResponse(payload=_chat_logprobs_payload()))
    backend = VllmChatBackend(_spec(), http=http)
    prompt = backend.apply_template([{"role": "user", "content": "1+1=?"}])

    candidates = backend.step_token(
        prompt,
        TokenStepParams(
            top_k=5,
            max_tokens=4,
            temperature=0.0,
            top_p=0.9,
            stop=("<stop>",),
            seed=7,
            extra={"repetition_penalty": 1.1, "max_tokens": 99},
        ),
    )

    assert [c["token"] for c in candidates] == ["2", "3"]
    assert [c["prob"] for c in candidates] == pytest.approx([0.8, 0.2])
    call = http.calls[0]
    assert call["url"] == "http://vllm.test:8000/v1/chat/completions"
    assert call["json"] == {
        "model": "test-chat-model",
        "messages": [{"role": "user", "content": "1+1=?"}],
        "max_tokens": 1,
        "logprobs": True,
        "top_logprobs": 5,
        "add_generation_prompt": True,
        "temperature": 0.0,
        "top_p": 0.9,
        "stop": ["<stop>"],
        "seed": 7,
        "repetition_penalty": 1.1,
    }
    assert call["headers"] == {"Content-Type": "application/json"}
    assert call["timeout"] == pytest.approx(30.0)


def test_step_token_with_prefix_continues_final_assistant_message() -> None:
    http = _FakeHttp(_FakeResponse(payload=_chat_logprobs_payload()))
    backend = VllmChatBackend(_spec(model_url="http://vllm.test:8000/"), http=http)
    prompt = encode_vllm_chat_prompt([{"role": "user", "content": "1+1=?"}], assistant_prefix="答案是")

    backend.step_token(prompt, TokenStepParams(top_k=3, max_tokens=4))

    call = http.calls[0]
    assert call["url"] == "http://vllm.test:8000/v1/chat/completions"
    assert call["json"] == {
        "model": "test-chat-model",
        "messages": [
            {"role": "user", "content": "1+1=?"},
            {"role": "assistant", "content": "答案是"},
        ],
        "max_tokens": 1,
        "logprobs": True,
        "top_logprobs": 3,
        "continue_final_message": True,
        "add_generation_prompt": False,
    }


def test_step_token_keeps_leading_whitespace_without_backend_lookahead() -> None:
    http = _FakeHttp(_FakeResponse(payload=_chat_leading_whitespace_payload()))
    backend = VllmChatBackend(_spec(), http=http)
    prompt = encode_vllm_chat_prompt(
        [{"role": "user", "content": "compare"}],
        assistant_prefix='They are hard to compare."',
    )

    candidates = backend.step_token(prompt, TokenStepParams(top_k=3, max_tokens=4))

    assert [c["token"] for c in candidates] == ["\n\n", " This", " It"]
    assert [c["prob"] for c in candidates] == pytest.approx([0.7, 0.2, 0.1])


def test_step_token_keeps_single_whitespace_token_without_lookahead() -> None:
    payload = _chat_leading_whitespace_payload()
    payload["choices"][0]["message"]["content"] = "\n\n"
    payload["choices"][0]["logprobs"]["content"] = payload["choices"][0]["logprobs"]["content"][:1]
    http = _FakeHttp(_FakeResponse(payload=payload))
    backend = VllmChatBackend(_spec(), http=http)
    prompt = encode_vllm_chat_prompt(
        [{"role": "user", "content": "compare"}],
        assistant_prefix='They are hard to compare."',
    )

    candidates = backend.step_token(prompt, TokenStepParams(top_k=3, max_tokens=1))

    assert [c["token"] for c in candidates] == ["\n\n", " This", " It"]


def test_generate_uses_chat_completions_endpoint() -> None:
    http = _FakeHttp(
        _FakeResponse(
            payload={
                "choices": [
                    {
                        "message": {"role": "assistant", "content": "hello"},
                        "finish_reason": "stop",
                    }
                ],
                "usage": {"completion_tokens": 1},
            }
        )
    )
    backend = VllmChatBackend(_spec(), http=http)

    result = backend.generate("hi", {"max_tokens": 3, "temperature": 0.2})

    assert result == {
        "text": "hello",
        "finish_reason": "stop",
        "metadata": {"usage": {"completion_tokens": 1}},
    }
    assert http.calls[0]["url"] == "http://vllm.test:8000/v1/chat/completions"
    assert http.calls[0]["json"] == {
        "model": "test-chat-model",
        "messages": [{"role": "user", "content": "hi"}],
        "max_tokens": 3,
        "temperature": 0.2,
        "stream": False,
    }
