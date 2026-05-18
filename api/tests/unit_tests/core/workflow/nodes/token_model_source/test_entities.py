"""Schema-level tests for the ``token-model-source`` node entities (P3.B.1).

Coverage:
* :class:`SamplingParams` defaults match DEVELOPMENT_PLAN_v3 §4.3.
* :class:`SamplingParams` ``extra="forbid"`` rejects yaml typos.
* Range guards on ``top_k`` / ``temperature`` / ``max_tokens`` /
  ``top_p`` reject out-of-range values pydantic would otherwise accept.
* :class:`TokenModelSourceNodeData` accepts the documented happy-path
  payload and normalises ``model_alias`` whitespace.
* The node-data ``type`` field is pinned to ``"token-model-source"``.
"""

import pytest
from pydantic import ValidationError

from core.workflow.nodes.token_model_source import TOKEN_MODEL_SOURCE_NODE_TYPE
from core.workflow.nodes.token_model_source.entities import (
    ChatMessageTemplate,
    SamplingParams,
    TokenModelSourceNodeData,
)


class TestSamplingParamsDefaults:
    def test_default_values_match_v3_plan(self):
        sp = SamplingParams()
        assert sp.top_k == 10
        assert sp.temperature == 0.7
        assert sp.max_tokens == 1024
        assert sp.top_p is None
        assert sp.seed is None
        assert sp.stop == []

    def test_overrides_apply(self):
        sp = SamplingParams(
            top_k=5,
            temperature=0.0,
            max_tokens=128,
            top_p=0.95,
            seed=42,
            stop=["\n\n", "</s>"],
        )
        assert sp.top_k == 5
        assert sp.temperature == 0.0
        assert sp.max_tokens == 128
        assert sp.top_p == 0.95
        assert sp.seed == 42
        assert sp.stop == ["\n\n", "</s>"]


class TestSamplingParamsExtraForbid:
    """``extra="forbid"`` is the SPI's seat-belt against yaml typos —
    ``temprature: 0.7`` must hard-fail at schema validation, not silently
    no-op at runtime."""

    def test_unknown_field_rejected(self):
        with pytest.raises(ValidationError):
            SamplingParams.model_validate(
                {"top_k": 10, "temprature": 0.7}  # typo
            )

    def test_repetition_penalty_rejected_at_this_layer(self):
        # vLLM-specific knobs ride on ``TokenModelSourceNodeData.extra``
        # (the parent), not inside SamplingParams. Closing this surface
        # here is what keeps the cross-backend intersection clean.
        with pytest.raises(ValidationError):
            SamplingParams.model_validate(
                {"top_k": 10, "repetition_penalty": 1.1}
            )


class TestSamplingParamsRangeGuards:
    """Pydantic ``Field(gt=...)`` / ``ge=...`` / ``le=...`` already
    encode these bounds; tests pin them so a future "loosen
    temperature" change can't silently drop the negative-value reject."""

    def test_top_k_zero_rejected(self):
        with pytest.raises(ValidationError):
            SamplingParams(top_k=0)

    def test_top_k_negative_rejected(self):
        with pytest.raises(ValidationError):
            SamplingParams(top_k=-1)

    def test_temperature_zero_accepted_for_greedy(self):
        # Greedy decoding (``temperature=0``) is a legal mode for
        # research code that wants deterministic argmax sampling —
        # ``ge=0`` (not ``gt``) is intentional, pin it.
        sp = SamplingParams(temperature=0.0)
        assert sp.temperature == 0.0

    def test_temperature_negative_rejected(self):
        with pytest.raises(ValidationError):
            SamplingParams(temperature=-0.1)

    def test_max_tokens_zero_rejected(self):
        with pytest.raises(ValidationError):
            SamplingParams(max_tokens=0)

    def test_top_p_zero_rejected(self):
        # ``gt=0`` (not ``ge``) — ``top_p=0`` is meaningless (would
        # mask every candidate). pydantic must reject it.
        with pytest.raises(ValidationError):
            SamplingParams(top_p=0.0)

    def test_top_p_above_one_rejected(self):
        with pytest.raises(ValidationError):
            SamplingParams(top_p=1.01)

    def test_top_p_at_one_accepted(self):
        sp = SamplingParams(top_p=1.0)
        assert sp.top_p == 1.0


class TestTokenModelSourceNodeData:
    def test_minimal_happy_path(self):
        nd = TokenModelSourceNodeData(
            title="src",
            model_alias="qwen3-4b",
            prompt_template="Answer: {{#start.q#}}",
        )
        assert nd.type == TOKEN_MODEL_SOURCE_NODE_TYPE
        assert nd.model_alias == "qwen3-4b"
        assert nd.prompt_template == "Answer: {{#start.q#}}"
        # Defaults flow through.
        assert nd.sampling_params.top_k == 10
        assert nd.extra == {}
        assert nd.expose_raw_logits is None

    def test_blank_model_alias_rejected(self):
        with pytest.raises(ValidationError):
            TokenModelSourceNodeData(
                title="src", model_alias="   ", prompt_template="hi"
            )

    def test_empty_model_alias_rejected(self):
        with pytest.raises(ValidationError):
            TokenModelSourceNodeData(
                title="src", model_alias="", prompt_template="hi"
            )

    def test_model_alias_whitespace_normalised(self):
        # Same rationale as ``AggregationInputRef.source_id``: the
        # frontend dedup compares trimmed values, so persist the
        # trimmed form to keep DSL rewrites idempotent.
        nd = TokenModelSourceNodeData(
            title="src",
            model_alias="  qwen3-4b  ",
            prompt_template="",
        )
        assert nd.model_alias == "qwen3-4b"

    def test_empty_prompt_template_allowed(self):
        # Constant prompts are a valid use case — the user wires the
        # full prompt without referencing any upstream variable.
        nd = TokenModelSourceNodeData(
            title="src",
            model_alias="qwen3-4b",
            prompt_template="",
        )
        assert nd.prompt_template == ""

    def test_extra_is_passthrough(self):
        nd = TokenModelSourceNodeData(
            title="src",
            model_alias="qwen3-4b",
            prompt_template="hi",
            extra={"repetition_penalty": 1.1, "research_tag": "exp_42"},
        )
        assert nd.extra == {"repetition_penalty": 1.1, "research_tag": "exp_42"}

    def test_expose_raw_logits_override_accepted(self):
        nd = TokenModelSourceNodeData(
            title="src",
            model_alias="qwen3-4b",
            prompt_template="hi",
            expose_raw_logits=True,
        )
        assert nd.expose_raw_logits is True

    def test_sampling_params_typo_propagates(self):
        # ``SamplingParams.extra="forbid"`` must surface through the
        # parent node-data validation as a ``ValidationError``,
        # otherwise the seat-belt is unreachable from the DSL layer.
        with pytest.raises(ValidationError):
            TokenModelSourceNodeData.model_validate(
                {
                    "title": "src",
                    "type": TOKEN_MODEL_SOURCE_NODE_TYPE,
                    "model_alias": "qwen3-4b",
                    "prompt_template": "hi",
                    "sampling_params": {"top_k": 10, "temprature": 0.7},
                }
            )


class TestInlineSpecField:
    """``inline_spec`` is the optional escape hatch that lets the panel
    bypass ``model_net.yaml``. The DSL layer keeps the per-backend
    schema unconstrained — the parallel-ensemble consumer validates
    the payload against ``BackendRegistry.get_spec_class(...)`` — but
    enforces three invariants here: ``backend`` and ``model_name``
    must be non-blank strings, and the user cannot smuggle an ``id``
    (the consumer derives it from ``model_alias``).
    """

    def test_default_is_none(self):
        nd = TokenModelSourceNodeData(
            title="src", model_alias="ad-hoc", prompt_template="hi"
        )
        assert nd.inline_spec is None

    def test_minimal_inline_spec_accepted(self):
        nd = TokenModelSourceNodeData(
            title="src",
            model_alias="ad-hoc",
            prompt_template="hi",
            inline_spec={
                "backend": "llama_cpp",
                "model_name": "llama-3.1-8b-instruct",
                "model_url": "http://127.0.0.1:8080",
                "EOS": "<|eot_id|>",
            },
        )
        assert nd.inline_spec is not None
        assert nd.inline_spec["backend"] == "llama_cpp"
        assert nd.inline_spec["model_name"] == "llama-3.1-8b-instruct"

    def test_missing_backend_rejected(self):
        with pytest.raises(ValidationError):
            TokenModelSourceNodeData(
                title="src",
                model_alias="ad-hoc",
                prompt_template="hi",
                inline_spec={"model_name": "x"},
            )

    def test_blank_backend_rejected(self):
        with pytest.raises(ValidationError):
            TokenModelSourceNodeData(
                title="src",
                model_alias="ad-hoc",
                prompt_template="hi",
                inline_spec={"backend": "  ", "model_name": "x"},
            )

    def test_missing_model_name_rejected(self):
        with pytest.raises(ValidationError):
            TokenModelSourceNodeData(
                title="src",
                model_alias="ad-hoc",
                prompt_template="hi",
                inline_spec={"backend": "llama_cpp"},
            )

    def test_id_smuggling_rejected(self):
        with pytest.raises(ValidationError):
            TokenModelSourceNodeData(
                title="src",
                model_alias="ad-hoc",
                prompt_template="hi",
                inline_spec={
                    "backend": "llama_cpp",
                    "model_name": "x",
                    "id": "smuggled-id",
                },
            )


class TestChatMessageTemplate:
    """``ChatMessageTemplate`` is the per-row pydantic shape behind
    ``messages_template`` (chat mode). The DSL surface must reject
    yaml typos via ``extra="forbid"`` and require non-blank roles —
    same seat-belts as ``SamplingParams``."""

    def test_minimal_happy_path(self):
        msg = ChatMessageTemplate(role="user", content="Hello")
        assert msg.role == "user"
        assert msg.content == "Hello"

    def test_empty_content_allowed(self):
        # Empty content is a legitimate use case (system slot the user
        # leaves blank intentionally; placeholder-only content that
        # resolves to empty string at run time). Reject only at the
        # role surface, not content.
        msg = ChatMessageTemplate(role="system", content="")
        assert msg.content == ""

    def test_blank_role_rejected(self):
        with pytest.raises(ValidationError):
            ChatMessageTemplate(role="", content="hi")

    def test_unknown_field_rejected(self):
        # ``extra="forbid"`` — yaml typos like ``role: user, contentx: hi``
        # must hard-fail here, not at the rendered-prompt layer.
        with pytest.raises(ValidationError):
            ChatMessageTemplate.model_validate({"role": "user", "contentx": "hi"})


class TestMessagesTemplateField:
    """``messages_template`` carries chat mode through the DSL.

    Two surfaces this test pins down:
    * the field accepts a list of ``{role, content}`` rows and renders
      them through the same pydantic shape as the bare model;
    * the model validator rejects ambiguous configurations
      (``prompt_template`` and ``messages_template`` simultaneously, or
      an empty ``messages_template`` set at all).
    """

    def test_messages_template_accepted(self):
        nd = TokenModelSourceNodeData(
            title="src",
            model_alias="qwen3-4b",
            messages_template=[
                ChatMessageTemplate(role="system", content="You are a helpful assistant."),
                ChatMessageTemplate(role="user", content="Answer: {{#start.q#}}"),
            ],
        )
        assert nd.messages_template is not None
        assert len(nd.messages_template) == 2
        assert nd.messages_template[0].role == "system"
        assert nd.messages_template[1].content == "Answer: {{#start.q#}}"
        # Default ``prompt_template=""`` must remain in chat mode — the
        # mutex only fires on a *non-empty* prompt_template.
        assert nd.prompt_template == ""

    def test_messages_template_dict_form_validates_through(self):
        # Persisted DSL deserialises into raw dicts; pydantic must
        # construct the inner ``ChatMessageTemplate`` model from them so
        # the frontend save path round-trips.
        nd = TokenModelSourceNodeData.model_validate(
            {
                "title": "src",
                "type": TOKEN_MODEL_SOURCE_NODE_TYPE,
                "model_alias": "qwen3-4b",
                "messages_template": [
                    {"role": "user", "content": "hi"},
                ],
            }
        )
        assert nd.messages_template is not None
        assert nd.messages_template[0].role == "user"

    def test_default_messages_template_is_none(self):
        # Raw-completion mode is the default — ``messages_template=None``
        # means "feature not used", distinct from ``[]`` (which the
        # validator rejects below).
        nd = TokenModelSourceNodeData(
            title="src",
            model_alias="qwen3-4b",
            prompt_template="hi",
        )
        assert nd.messages_template is None

    def test_both_set_rejected(self):
        # The schema validator rules out the ambiguous "both set"
        # combination at boot time; the run loop never has to choose
        # which one wins (ADR-v3-16 wire-shape unambiguity).
        with pytest.raises(ValidationError) as exc:
            TokenModelSourceNodeData(
                title="src",
                model_alias="qwen3-4b",
                prompt_template="raw text",
                messages_template=[ChatMessageTemplate(role="user", content="hi")],
            )
        assert "mutually exclusive" in str(exc.value)

    def test_empty_messages_template_rejected(self):
        # ``messages_template=[]`` is "chat mode set but useless" —
        # reject so the user cannot save a config that would render an
        # empty messages list to the chat-template endpoint.
        with pytest.raises(ValidationError) as exc:
            TokenModelSourceNodeData(
                title="src",
                model_alias="qwen3-4b",
                messages_template=[],
            )
        assert "must not be empty" in str(exc.value)

    def test_empty_prompt_template_with_messages_template_allowed(self):
        # The mutex fires on a *non-empty* ``prompt_template``; the
        # default empty string is fine alongside ``messages_template``.
        nd = TokenModelSourceNodeData(
            title="src",
            model_alias="qwen3-4b",
            prompt_template="",
            messages_template=[ChatMessageTemplate(role="user", content="hi")],
        )
        assert nd.messages_template is not None
        assert nd.prompt_template == ""

    def test_inner_validation_propagates(self):
        # ``ChatMessageTemplate.role`` min_length=1 must surface through
        # the parent so a typo'd messages list (empty role) is caught at
        # boot, not at render time.
        with pytest.raises(ValidationError):
            TokenModelSourceNodeData.model_validate(
                {
                    "title": "src",
                    "type": TOKEN_MODEL_SOURCE_NODE_TYPE,
                    "model_alias": "qwen3-4b",
                    "messages_template": [{"role": "", "content": "hi"}],
                }
            )


class TestRawCompletionFlag:
    """``raw_completion=True`` is the research escape hatch: opts out of
    chat-template auto-wrap so chat-template-capable backends still
    receive the rendered ``prompt_template`` verbatim (PN.py-style).
    Default is ``False`` so existing graphs that only set
    ``prompt_template`` get the bug-fix behaviour without a DSL change.
    """

    def test_default_is_false(self):
        # Default flag exists on the schema and defaults to False so the
        # auto-wrap default fires without explicit user opt-in.
        nd = TokenModelSourceNodeData(
            title="src",
            model_alias="qwen3-4b",
            prompt_template="hi",
        )
        assert nd.raw_completion is False

    def test_explicit_true_round_trips(self):
        nd = TokenModelSourceNodeData(
            title="src",
            model_alias="qwen3-4b",
            prompt_template="research mode raw text",
            raw_completion=True,
        )
        assert nd.raw_completion is True

    def test_raw_completion_with_messages_template_rejected(self):
        # ``raw_completion=True`` says "send prompt verbatim" — combining
        # it with ``messages_template`` is a contradiction (the latter
        # has no ``prompt`` slot to send). Schema validator must reject
        # so the contradiction surfaces at boot, not silently at run
        # time.
        with pytest.raises(ValidationError) as exc:
            TokenModelSourceNodeData(
                title="src",
                model_alias="qwen3-4b",
                messages_template=[ChatMessageTemplate(role="user", content="hi")],
                raw_completion=True,
            )
        assert "incompatible" in str(exc.value)

    def test_raw_completion_with_prompt_template_allowed(self):
        # The intended combo: raw_completion=True is *only* meaningful
        # alongside prompt_template. Pin the happy path so a future
        # validator tightening cannot accidentally lock out the
        # research escape hatch.
        nd = TokenModelSourceNodeData(
            title="src",
            model_alias="qwen3-4b",
            prompt_template="raw priming text",
            raw_completion=True,
        )
        assert nd.raw_completion is True
        assert nd.prompt_template == "raw priming text"
