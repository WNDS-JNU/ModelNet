"""Behavioural tests for the ``TokenModelSourceNode`` (P3.B.1).

Coverage:
* ``_run`` happy path — yields a single ``StreamCompletedEvent`` with the
  rendered prompt and the documented spec shape (ADR-v3-10).
* Prompt rendering normalises segment.text for non-string upstreams
  (mirrors ``response_aggregator`` segment-text contract).
* Missing upstream variable → ``PromptRenderError`` → FAILED event
  with structured ``error_type`` for the panel.
* Constant prompt (no placeholders) skips the variable pool entirely.
* ``extra_variable_selector_to_variable_mapping`` exposes every
  ``{{#node.field#}}`` reference with the framework's ``{node_id}.{var}``
  key shape (Rv3-3 / draft-variable preload contract).
* ``node_data.extra`` round-trips into ``spec.extra`` (vLLM-style
  research knobs survive without forking the schema).
"""

from core.workflow.nodes.token_model_source import (
    TOKEN_MODEL_SOURCE_NODE_TYPE,
    TokenModelSourceNode,
)
from graphon.enums import WorkflowNodeExecutionStatus
from graphon.node_events.node import StreamCompletedEvent
from graphon.runtime.variable_pool import VariablePool


def _make_node(pool: VariablePool, payload: dict) -> TokenModelSourceNode:
    """Build a node bypassing ``Node.__init__`` (which needs full
    ``graph_init_params``). Tests only exercise ``_run`` /
    ``_render_prompt``, which read ``_node_data``, ``_node_id``, and
    ``graph_runtime_state.variable_pool``.
    """
    node = TokenModelSourceNode.__new__(TokenModelSourceNode)
    node._node_id = "src_1"

    class _RS:
        pass

    rs = _RS()
    rs.variable_pool = pool
    node.graph_runtime_state = rs
    node._node_data = TokenModelSourceNode._node_data_type.model_validate(payload)
    return node


def _payload(
    *,
    model_alias: str = "qwen3-4b",
    prompt_template: str = "Answer: {{#start.q#}}",
    sampling_params: dict | None = None,
    extra: dict | None = None,
    messages_template: list[dict] | None = None,
    inline_spec: dict | None = None,
) -> dict:
    payload: dict = {
        "title": "src",
        "model_alias": model_alias,
    }
    # Only include ``prompt_template`` when chat-mode is not requested,
    # so the mutex validator on the entity model does not fire.
    if messages_template is not None:
        payload["messages_template"] = messages_template
    else:
        payload["prompt_template"] = prompt_template
    if sampling_params is not None:
        payload["sampling_params"] = sampling_params
    if extra is not None:
        payload["extra"] = extra
    if inline_spec is not None:
        payload["inline_spec"] = inline_spec
    return payload


class TestRunHappyPath:
    def test_single_completed_event_with_spec_shape(self):
        pool = VariablePool()
        pool.add(["start", "q"], "what is 2+2")
        node = _make_node(pool, _payload())

        events = list(node._run())

        assert len(events) == 1
        assert isinstance(events[0], StreamCompletedEvent)
        nrr = events[0].node_run_result
        assert nrr.status == WorkflowNodeExecutionStatus.SUCCEEDED
        assert nrr.error == ""
        assert nrr.inputs == {"model_alias": "qwen3-4b"}

        # Spec shape mirrors ADR-v3-10 / DEVELOPMENT_PLAN_v3 §4.3.
        spec = nrr.outputs["spec"]
        assert spec["model_alias"] == "qwen3-4b"
        assert spec["prompt"] == "Answer: what is 2+2"
        assert spec["sampling_params"] == {
            "top_k": 10,
            "temperature": 0.7,
            "max_tokens": 1024,
            "top_p": None,
            "seed": None,
            "stop": [],
        }
        assert spec["extra"] == {}
        # Raw-completion mode emits ``messages: None`` so the
        # parallel-ensemble consumer can branch on it cheaply.
        assert spec["messages"] is None
        # ``raw_completion`` defaults to False — chat-template auto-wrap
        # path is the active default; pin so a regression to ``True``
        # default would surface as a behaviour change here.
        assert spec["raw_completion"] is False
        # ``model_alias`` surfaced top-level too for panels that only
        # want the alias without unpacking the spec dict.
        assert nrr.outputs["model_alias"] == "qwen3-4b"

    def test_constant_prompt_no_pool_lookup(self):
        # No placeholder → ``_render_prompt`` short-circuits without
        # touching the pool, so an empty pool is fine.
        pool = VariablePool()
        node = _make_node(
            pool,
            _payload(prompt_template="Plain instruction with no vars."),
        )

        events = list(node._run())
        nrr = events[0].node_run_result
        assert nrr.status == WorkflowNodeExecutionStatus.SUCCEEDED
        assert nrr.outputs["spec"]["prompt"] == "Plain instruction with no vars."

    def test_overridden_sampling_params_round_trip_into_spec(self):
        pool = VariablePool()
        pool.add(["start", "q"], "x")
        node = _make_node(
            pool,
            _payload(
                sampling_params={
                    "top_k": 5,
                    "temperature": 0.0,
                    "max_tokens": 64,
                    "top_p": 0.9,
                    "seed": 42,
                    "stop": ["\n\n"],
                }
            ),
        )

        spec = list(node._run())[0].node_run_result.outputs["spec"]
        assert spec["sampling_params"] == {
            "top_k": 5,
            "temperature": 0.0,
            "max_tokens": 64,
            "top_p": 0.9,
            "seed": 42,
            "stop": ["\n\n"],
        }

    def test_extra_dict_round_trips(self):
        # ``extra`` is the documented extension point for backend-private
        # knobs (vLLM ``repetition_penalty``, research_tag, ...). It must
        # arrive in ``spec.extra`` byte-for-byte.
        pool = VariablePool()
        pool.add(["start", "q"], "x")
        node = _make_node(
            pool,
            _payload(extra={"repetition_penalty": 1.1, "research_tag": "exp_42"}),
        )

        spec = list(node._run())[0].node_run_result.outputs["spec"]
        assert spec["extra"] == {"repetition_penalty": 1.1, "research_tag": "exp_42"}

    def test_spec_extra_decoupled_from_node_data(self):
        # ``node_data.extra`` must not be aliased into ``spec.extra``;
        # downstream mutation of one must not bleed into the other
        # (matters for the parallel-ensemble executor which may inject
        # per-call backend keys).
        pool = VariablePool()
        pool.add(["start", "q"], "x")
        node = _make_node(pool, _payload(extra={"k": "v"}))

        spec = list(node._run())[0].node_run_result.outputs["spec"]
        spec["extra"]["mutated"] = True
        assert "mutated" not in node._node_data.extra


class TestChatModeRendering:
    """``messages_template`` (chat mode) renders each ``content``
    against the variable pool with the same semantics as
    ``prompt_template`` (raw mode), and surfaces the result on
    ``spec.messages`` so the parallel-ensemble node can route through
    each backend's ``apply_template`` instead of sending raw completion
    text.
    """

    def test_chat_mode_renders_each_content(self):
        pool = VariablePool()
        pool.add(["start", "q"], "what is 2+2")
        pool.add(["ctx", "lang"], "english")
        node = _make_node(
            pool,
            _payload(
                messages_template=[
                    {"role": "system", "content": "Reply in {{#ctx.lang#}}."},
                    {"role": "user", "content": "Answer: {{#start.q#}}"},
                ],
            ),
        )

        events = list(node._run())
        assert len(events) == 1
        nrr = events[0].node_run_result
        assert nrr.status == WorkflowNodeExecutionStatus.SUCCEEDED

        spec = nrr.outputs["spec"]
        # Chat mode emits the messages list and zeroes the prompt slot.
        assert spec["messages"] == [
            {"role": "system", "content": "Reply in english."},
            {"role": "user", "content": "Answer: what is 2+2"},
        ]
        assert spec["prompt"] == ""
        # Surfacing model_alias still works in chat mode.
        assert nrr.outputs["model_alias"] == "qwen3-4b"

    def test_chat_mode_constant_content_no_pool_lookup(self):
        # No placeholders → renderer short-circuits without touching the
        # pool (matches raw-mode behaviour).
        pool = VariablePool()
        node = _make_node(
            pool,
            _payload(
                messages_template=[
                    {"role": "user", "content": "What's the capital of France?"},
                ],
            ),
        )

        spec = list(node._run())[0].node_run_result.outputs["spec"]
        assert spec["messages"] == [
            {"role": "user", "content": "What's the capital of France?"},
        ]
        assert spec["prompt"] == ""

    def test_chat_mode_missing_variable_fails_with_prompt_render_error(self):
        # A missing upstream variable in any ``content`` must FAIL the
        # node with the same ``PromptRenderError`` shape raw mode uses,
        # so the panel error UX stays consistent across the two modes.
        pool = VariablePool()
        # ``start.q`` deliberately not added.
        node = _make_node(
            pool,
            _payload(
                messages_template=[
                    {"role": "user", "content": "Answer: {{#start.q#}}"},
                ],
            ),
        )

        events = list(node._run())
        nrr = events[0].node_run_result
        assert nrr.status == WorkflowNodeExecutionStatus.FAILED
        assert nrr.error_type == "PromptRenderError"
        assert "#start.q#" in nrr.error

    def test_chat_mode_role_passes_through_unchanged(self):
        # The backend's ``apply_template`` is the canonical authority on
        # role validity; the source node must not gate on role names so
        # research configs with custom roles (e.g. ``"function"``,
        # ``"tool"``, ``"developer"``) round-trip without surgery.
        pool = VariablePool()
        node = _make_node(
            pool,
            _payload(
                messages_template=[
                    {"role": "developer", "content": "Custom role test."},
                ],
            ),
        )
        spec = list(node._run())[0].node_run_result.outputs["spec"]
        assert spec["messages"] == [{"role": "developer", "content": "Custom role test."}]


class TestRenderPromptSegmentText:
    """The renderer must use ``Segment.text`` (graphon canonical),
    matching ``response_aggregator/node.py`` so non-string upstreams
    render the same way across every workflow node."""

    def test_object_segment_renders_as_json(self):
        pool = VariablePool()
        pool.add(["upstream", "answer"], {"city": "Paris", "score": 0.9})
        node = _make_node(
            pool,
            _payload(prompt_template="Look at: {{#upstream.answer#}}"),
        )

        spec = list(node._run())[0].node_run_result.outputs["spec"]
        # JSON form uses double quotes; Python repr uses single quotes.
        assert '"city": "Paris"' in spec["prompt"]
        assert "'city': 'Paris'" not in spec["prompt"]

    def test_array_string_segment_renders_as_json(self):
        pool = VariablePool()
        pool.add(["upstream", "tags"], ["alpha", "beta"])
        node = _make_node(
            pool,
            _payload(prompt_template="Tags: {{#upstream.tags#}}"),
        )
        spec = list(node._run())[0].node_run_result.outputs["spec"]
        assert '["alpha", "beta"]' in spec["prompt"]

    def test_none_segment_renders_as_empty_string(self):
        pool = VariablePool()
        pool.add(["upstream", "maybe"], None)
        node = _make_node(
            pool,
            _payload(prompt_template="Value: <{{#upstream.maybe#}}>"),
        )
        spec = list(node._run())[0].node_run_result.outputs["spec"]
        assert spec["prompt"] == "Value: <>"


class TestInlineSpecPassthrough:
    """``inline_spec`` rides through ``_run`` to ``outputs.spec.inline_spec``
    so the parallel-ensemble consumer can validate it against the
    backend's pydantic class instead of resolving an alias against
    ``model_net.yaml``. The node never validates per-backend fields
    here — that's the consumer's job — but the wire shape must round
    trip byte-for-byte and stay decoupled from the node-data dict.
    """

    def test_inline_spec_round_trips_into_outputs(self):
        pool = VariablePool()
        pool.add(["start", "q"], "x")
        node = _make_node(
            pool,
            _payload(
                inline_spec={
                    "backend": "llama_cpp",
                    "model_name": "llama-3.1-8b-instruct",
                    "model_url": "http://127.0.0.1:8080",
                    "EOS": "<|eot_id|>",
                    "type": "normal",
                    "expose_raw_logits": False,
                },
            ),
        )

        spec = list(node._run())[0].node_run_result.outputs["spec"]
        assert spec["inline_spec"] == {
            "backend": "llama_cpp",
            "model_name": "llama-3.1-8b-instruct",
            "model_url": "http://127.0.0.1:8080",
            "EOS": "<|eot_id|>",
            "type": "normal",
            "expose_raw_logits": False,
        }

    def test_inline_spec_default_none(self):
        # Registered-alias mode (no inline_spec) emits ``inline_spec: None``
        # so the wire shape stays stable; the consumer treats absent
        # and None identically.
        pool = VariablePool()
        pool.add(["start", "q"], "x")
        node = _make_node(pool, _payload())

        spec = list(node._run())[0].node_run_result.outputs["spec"]
        assert spec["inline_spec"] is None

    def test_inline_spec_decoupled_from_node_data(self):
        # Same defensive-copy contract as ``extra``: downstream mutation
        # of ``spec.inline_spec`` must not bleed back into the parsed
        # node_data.
        pool = VariablePool()
        pool.add(["start", "q"], "x")
        node = _make_node(
            pool,
            _payload(
                inline_spec={
                    "backend": "llama_cpp",
                    "model_name": "m",
                    "model_url": "http://127.0.0.1:8080",
                    "EOS": "<|eot_id|>",
                },
            ),
        )

        spec = list(node._run())[0].node_run_result.outputs["spec"]
        spec["inline_spec"]["mutated"] = True
        assert "mutated" not in (node._node_data.inline_spec or {})


class TestRunFailurePaths:
    def test_missing_upstream_variable_becomes_failed_event(self):
        pool = VariablePool()
        # ``start.q`` deliberately not added.
        node = _make_node(pool, _payload())

        events = list(node._run())

        assert len(events) == 1
        nrr = events[0].node_run_result
        assert nrr.status == WorkflowNodeExecutionStatus.FAILED
        assert nrr.error_type == "PromptRenderError"
        # Surface the offending variable in the message so the panel
        # tells the user *which* upstream is unwired.
        assert "#start.q#" in nrr.error
        # ``inputs`` keeps the alias for observability of the failed run.
        assert nrr.inputs == {"model_alias": "qwen3-4b"}
        # Outputs stay empty on failure.
        assert nrr.outputs == {}


class TestExtractVariableSelectorMapping:
    """Mapping must expose every ``{{#upstream.field#}}`` reference so
    the draft-variable preload pipeline materialises the upstream
    value ahead of ``_run``. Key shape follows the framework
    convention: ``{node_id}.{variable_key}``."""

    def _config(self, node_id: str, prompt_template: str) -> dict:
        return {
            "id": node_id,
            "data": {
                "title": "src",
                "type": TOKEN_MODEL_SOURCE_NODE_TYPE,
                "model_alias": "qwen3-4b",
                "prompt_template": prompt_template,
            },
        }

    def test_single_placeholder_exposed(self):
        config = self._config("src_1", "Answer: {{#start.q#}}")
        mapping = TokenModelSourceNode.extract_variable_selector_to_variable_mapping(
            graph_config={}, config=config
        )
        assert dict(mapping) == {"src_1.#start.q#": ["start", "q"]}

    def test_multiple_placeholders_each_exposed(self):
        config = self._config(
            "src_1",
            "{{#start.q#}} for {{#ctx.user#}} in {{#ctx.lang#}}",
        )
        mapping = TokenModelSourceNode.extract_variable_selector_to_variable_mapping(
            graph_config={}, config=config
        )
        assert dict(mapping) == {
            "src_1.#start.q#": ["start", "q"],
            "src_1.#ctx.user#": ["ctx", "user"],
            "src_1.#ctx.lang#": ["ctx", "lang"],
        }

    def test_empty_template_returns_empty_mapping(self):
        config = self._config("src_1", "Plain text, no placeholders.")
        mapping = TokenModelSourceNode.extract_variable_selector_to_variable_mapping(
            graph_config={}, config=config
        )
        assert dict(mapping) == {}

    def test_deep_path_selector_preserved(self):
        # Nested object paths like ``upstream.structured_output.city``
        # must survive verbatim — ``VariableTemplateParser`` already
        # supports up to 11 segments; the mapping must not truncate.
        config = self._config(
            "src_1",
            "City: {{#upstream.structured_output.city#}}",
        )
        mapping = TokenModelSourceNode.extract_variable_selector_to_variable_mapping(
            graph_config={}, config=config
        )
        assert dict(mapping) == {
            "src_1.#upstream.structured_output.city#": [
                "upstream",
                "structured_output",
                "city",
            ],
        }

    def test_messages_template_placeholders_exposed(self):
        # Chat-mode placeholders must reach the preload pipeline too —
        # otherwise ``_render_messages`` would race the variable pool
        # at run time and fail with PromptRenderError on values the
        # framework had time to materialise but didn't, because the
        # mapping omitted them.
        config = {
            "id": "src_1",
            "data": {
                "title": "src",
                "type": TOKEN_MODEL_SOURCE_NODE_TYPE,
                "model_alias": "qwen3-4b",
                "messages_template": [
                    {"role": "system", "content": "Speak {{#ctx.lang#}}."},
                    {"role": "user", "content": "Q: {{#start.q#}}"},
                ],
            },
        }
        mapping = TokenModelSourceNode.extract_variable_selector_to_variable_mapping(
            graph_config={}, config=config
        )
        assert dict(mapping) == {
            "src_1.#ctx.lang#": ["ctx", "lang"],
            "src_1.#start.q#": ["start", "q"],
        }


class TestNodeRegistration:
    """Smoke test the node registers itself under the canonical type
    string so ``DifyNodeFactory.create_node`` can resolve it via
    ``Node._registry``."""

    def test_node_type_attribute_matches_constant(self):
        assert TokenModelSourceNode.node_type == TOKEN_MODEL_SOURCE_NODE_TYPE
        assert TokenModelSourceNode.node_type == "token-model-source"

    def test_version_returns_one(self):
        # P3.B.1 introduces v1 of the node; pin it so a future
        # accidental version bump in the wrong PR is loud.
        assert TokenModelSourceNode.version() == "1"
