"""vLLM backend hotfix coverage.

The vLLM adapter deliberately stays in raw-completion mode: no
``CHAT_TEMPLATE`` capability, no ``/apply-template`` call, and
``top_logprobs`` parsed as log-softmax probabilities rather than raw
logits.
"""

from __future__ import annotations

import json
import math
from typing import Any

import pytest
from pydantic import ValidationError

from core.workflow.nodes.parallel_ensemble.backends.vllm import (
    VllmBackend,
    VllmResponseError,
    VllmSpec,
    parse_vllm_top_logprobs,
)
from core.workflow.nodes.parallel_ensemble.registry import BackendRegistry
from core.workflow.nodes.parallel_ensemble.spi.backend import TokenStepParams
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


def _spec(**overrides: Any) -> VllmSpec:
    base = {
        "id": "v1",
        "backend": "vllm",
        "model_name": "test-vllm",
        "model_url": "http://vllm.test:8000",
        "EOS": "<|eos|>",
        "type": "normal",
    }
    base.update(overrides)
    return VllmSpec(**base)


def test_backend_registry_resolves_vllm() -> None:
    assert BackendRegistry.get("vllm") is VllmBackend
    assert BackendRegistry.get_spec_class("vllm") is VllmSpec


def test_capabilities_exclude_chat_template_and_streaming() -> None:
    caps = VllmBackend.capabilities(_spec())
    assert caps == frozenset(
        {
            Capability.TOKEN_STEP,
            Capability.TOP_PROBS,
            Capability.POST_SAMPLING_PROBS,
        }
    )
    assert Capability.CHAT_TEMPLATE not in caps
    assert Capability.STREAMING not in caps


def test_spec_requires_model_name() -> None:
    with pytest.raises(ValidationError):
        VllmSpec(
            id="v1",
            backend="vllm",
            model_url="http://vllm.test:8000",
            EOS="<|eos|>",
        )
    with pytest.raises(ValidationError):
        _spec(model_name="")


def test_spec_rejects_empty_eos() -> None:
    with pytest.raises(ValidationError):
        _spec(EOS="")


def test_validate_requirements_rejects_chat_template() -> None:
    issues = VllmBackend.validate_requirements(
        _spec(),
        [{"kind": "needs_chat_template", "value": True, "rationale": "messages_template"}],
    )
    assert len(issues) == 1
    assert issues[0]["severity"] == "error"
    assert "CHAT_TEMPLATE" in issues[0]["message"]


def test_step_token_posts_to_completion_with_expected_body() -> None:
    payload = {
        "completion_probabilities": [
            {
                "top_logprobs": [
                    {"token": "yes", "logprob": math.log(0.75)},
                    {"token": "no", "logprob": math.log(0.25)},
                ]
            }
        ]
    }
    http = _FakeHttp(_FakeResponse(payload=payload))
    backend = VllmBackend(_spec(), http=http)

    candidates = backend.step_token(
        "the answer is",
        TokenStepParams(
            top_k=10,
            max_tokens=4,
            temperature=0.7,
            top_p=0.9,
            stop=("<stop>",),
            seed=42,
            extra={"repetition_penalty": 1.1, "max_tokens": 99},
        ),
    )

    assert [c["token"] for c in candidates] == ["yes", "no"]
    assert [c["prob"] for c in candidates] == pytest.approx([0.75, 0.25])
    call = http.calls[0]
    assert call["url"] == "http://vllm.test:8000/v1/completions"
    assert call["json"] == {
        "model": "test-vllm",
        "prompt": "the answer is",
        "max_tokens": 1,
        "logprobs": 10,
        "temperature": 0.7,
        "top_p": 0.9,
        "stop": ["<stop>"],
        "seed": 42,
        "repetition_penalty": 1.1,
    }
    assert call["headers"] == {"Content-Type": "application/json"}
    assert call["timeout"] == pytest.approx(30.0)


def test_step_token_omits_optional_knobs_when_unset() -> None:
    payload = {"completion_probabilities": [{"top_logprobs": [{"token": "x", "logprob": 0.0}]}]}
    http = _FakeHttp(_FakeResponse(payload=payload))
    backend = VllmBackend(_spec(), http=http)

    backend.step_token("p", TokenStepParams(top_k=3))

    body = http.calls[0]["json"]
    assert body == {
        "model": "test-vllm",
        "prompt": "p",
        "max_tokens": 1,
        "logprobs": 3,
    }


def test_parse_openai_completion_top_logprobs_map() -> None:
    out = parse_vllm_top_logprobs(
        {
            "choices": [
                {
                    "text": "yes",
                    "logprobs": {
                        "top_logprobs": [
                            {
                                "yes": math.log(0.8),
                                "no": math.log(0.2),
                            }
                        ]
                    },
                }
            ]
        },
        eos="<|eos|>",
    )

    assert [c["token"] for c in out] == ["yes", "no"]
    assert [c["prob"] for c in out] == pytest.approx([0.8, 0.2])
    assert [c["logit"] for c in out] == [None, None]


def test_parse_candidate_list_remaps_eos_and_renormalizes() -> None:
    out = parse_vllm_top_logprobs(
        {
            "completion_probabilities": [
                {
                    "top_logprobs": [
                        {"token": "keep", "logprob": math.log(0.1)},
                        {"token": "<|eos|>", "logprob": math.log(0.3)},
                    ]
                }
            ]
        },
        eos="<|eos|>",
    )

    assert [c["token"] for c in out] == ["keep", "<end>"]
    assert [c["prob"] for c in out] == pytest.approx([0.25, 0.75])


def test_unknown_response_shape_raises() -> None:
    with pytest.raises(VllmResponseError, match="missing top_logprobs"):
        parse_vllm_top_logprobs({"content": "x"}, eos="<|eos|>")


def test_generate_uses_completion_endpoint() -> None:
    http = _FakeHttp(
        _FakeResponse(
            payload={
                "choices": [{"text": "hello", "finish_reason": "length"}],
                "usage": {"completion_tokens": 3},
            }
        )
    )
    backend = VllmBackend(_spec(model_url="http://vllm.test:8000/"), http=http)

    result = backend.generate("hi", {"max_tokens": 3, "temperature": 0.2})

    assert result == {
        "text": "hello",
        "finish_reason": "length",
        "metadata": {"usage": {"completion_tokens": 3}},
    }
    assert http.calls[0]["url"] == "http://vllm.test:8000/v1/completions"
    assert http.calls[0]["json"] == {
        "model": "test-vllm",
        "prompt": "hi",
        "max_tokens": 3,
        "temperature": 0.2,
        "stream": False,
    }
