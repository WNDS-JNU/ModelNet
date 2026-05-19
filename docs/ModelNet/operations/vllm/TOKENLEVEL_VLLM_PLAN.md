# TokenLevel vLLM Plan

This document merges the original raw vLLM compatibility hotfix plan and the follow-up chat-token plan.

## Reading Order

1. Read "Current Direction" for the active implementation path.
2. Read "Raw Compatibility Hotfix" for the no-404 fallback path.
3. Read "Chat-Token Follow-up" for the semantically correct chat/instruct-model path.

## Current Direction

- Keep raw `vllm` as a compatibility/debugging backend using `/v1/completions`.
- Use `vllm_chat` only after `/v1/chat/completions` token logprobs are verified.
- Use `vllm_template` if chat logprobs are unavailable but completion logprobs work.
- In the current `token_step` runner, backend `step_token()` calls must request exactly one generated token per call; multi-token aggregation needs a separate runner/aggregator contract.

---

## Raw Compatibility Hotfix

## Background

The `test TokenLevel_vllm` workflow fails in the `token级并联集成` node.

After fixing the earlier empty `EOS` validation issue, the latest failure is:

```text
HTTP request failed with status code 404 for https://inference.cluster.aimodelnetwork.cn/tencent/Hunyuan-7B-Instruct-AWQ-Int4/apply-template
```

The two token model sources are vLLM-style endpoints, but their workflow `inline_spec` still uses the `llama_cpp` backend. `LlamaCppBackend` advertises `Capability.CHAT_TEMPLATE`, so `parallel_ensemble` auto-wraps raw prompts and calls `/apply-template`. These vLLM endpoints support token completion, but do not provide `/apply-template`, so the request returns 404.

## Scope

This plan is for a hotfix-quality backend compatibility path, not full productized UI support.

In scope:

- Add a dedicated backend named `vllm`.
- Keep existing `llama_cpp` behavior unchanged.
- Support the current two Token Model Source nodes through `prompt_template` / raw prompt mode.
- Avoid `/apply-template` for vLLM.
- Parse vLLM token probabilities with correct logprob semantics.
- Add focused backend and node tests.

Out of scope for this hotfix:

- Full frontend backend selector support.
- User-facing i18n for a new backend option.
- Support for `messages_template` unless `CHAT_TEMPLATE` support is explicitly implemented later.

If the workflow is migrated manually in DB/DSL, document that this is a controlled workflow migration rather than full UI product support.

## Current Source Configuration

The workflow has two token model sources:

1. `tencent/Hunyuan-7B-Instruct-AWQ-Int4`

```json
{
  "backend": "llama_cpp",
  "model_name": "tencent/Hunyuan-7B-Instruct-AWQ-Int4",
  "model_url": "https://inference.cluster.aimodelnetwork.cn/tencent/Hunyuan-7B-Instruct-AWQ-Int4",
  "EOS": "<|eos|>",
  "type": "normal",
  "stop_think": null,
  "expose_raw_logits": false
}
```

2. `Intel/Qwen3.5-4B-int4-AutoRound`

```json
{
  "backend": "llama_cpp",
  "model_name": "Intel/Qwen3.5-4B-int4-AutoRound",
  "model_url": "https://inference.cluster.aimodelnetwork.cn/Intel/Qwen3.5-4B-int4-AutoRound",
  "EOS": "<non-empty EOS value>",
  "type": "normal",
  "stop_think": null,
  "expose_raw_logits": false
}
```

The hotfix migration should change only:

```json
"backend": "vllm"
```

and keep `model_name`, `model_url`, non-empty `EOS`, `type`, `stop_think`, and `expose_raw_logits`.

## Backend Design

### 1. Add a vLLM backend module

Create:

```text
api/core/workflow/nodes/parallel_ensemble/backends/vllm.py
```

Define:

- `VllmSpec`
- `VllmBackend`

`VllmSpec` must preserve the base spec contract. Do not weaken `model_name` to optional.

Recommended hotfix schema:

```python
class VllmSpec(BaseSpec):
    backend: Literal["vllm"]
    model_url: AnyUrl
    EOS: str = Field(min_length=1)
    type: Literal["normal"] = "normal"
    stop_think: str | None = None
    expose_raw_logits: bool = False
```

Notes:

- Keep `model_name` inherited from `BaseSpec`, or redeclare it as a required non-empty `str` if needed by local typing.
- Restrict `type` to `"normal"` for the hotfix unless `generate()` is fully implemented for think-mode semantics.

### 2. Register backend

Register the new backend:

```python
@register_backend("vllm")
class VllmBackend(ModelBackend):
    spec_class = VllmSpec
```

Ensure the module is imported during backend initialization. If registrations are triggered through `backends/__init__.py`, import `vllm.py` there.

### 3. Capabilities

The vLLM backend must not advertise:

```python
Capability.CHAT_TEMPLATE
```

Recommended capabilities for the hotfix:

```python
frozenset(
    {
        Capability.TOKEN_STEP,
        Capability.TOP_PROBS,
        Capability.POST_SAMPLING_PROBS,
    }
)
```

Do not add `Capability.STREAMING` until the endpoint contract and `generate_stream()` behavior are verified.

Why this matters:

- With no `CHAT_TEMPLATE`, `parallel_ensemble._resolve_effective_prompt()` will not auto-call `apply_template(...)` for raw prompt sources.
- This only works for current sources that use `prompt_template` / raw prompt mode.
- If a source uses `messages_template`, current startup validation should reject it for a backend without `CHAT_TEMPLATE`; that is expected for this hotfix.

### 4. Implement required abstract methods

`ModelBackend` requires more than `step_token()`.

The hotfix implementation should include:

- `validate_requirements()`
- `generate()`
- `step_token()`

Recommended behavior:

- `validate_requirements()` should reject unsupported requirements clearly.
- `generate()` can call the same completion endpoint for normal generation if the SPI requires it, but it should not claim think-mode support.
- `step_token()` is the primary path used by token ensemble.

If full `generate()` support is not intended, keep `VllmSpec.type` limited to `"normal"` and fail explicitly for unsupported generation modes.

## Token-Step Request Contract

The current endpoints accept completion-style calls. Initial request body should be aligned with the existing token-step contract:

```json
{
  "prompt": "...",
  "max_tokens": 1,
  "n_probs": 10,
  "post_sampling_probs": true,
  "temperature": 0.7,
  "top_p": null,
  "stop": []
}
```

Include optional fields only when present:

- `temperature`
- `top_p`
- `stop`
- `seed`
- backend-specific `extra`

Do not send `/apply-template`.

## Probability Parsing Contract

Do not blindly reuse `parse_top_probs(...)` unless the response shape and probability semantics are proven identical.

For vLLM-style responses, common top-prob data is returned as `top_logprobs`: token to log-softmax probability. The parser must:

1. Extract the top-logprob map/list for the generated token step.
2. Convert each logprob with `math.exp(logprob)`.
3. Re-normalize over the returned top-k candidates.
4. Map empty token or configured `EOS` to the ensemble end sentinel.
5. Preserve raw logprob if the SPI candidate supports `logit` / `raw_logit`, but do not treat logprob as a raw logit.
6. Fail explicitly on unknown response shape instead of silently falling back to malformed probabilities.

Expected parser behavior:

```python
prob = math.exp(logprob)
normalized_prob = prob / sum(exp_values)
```

Response mismatch should raise a backend response error with a concise payload excerpt. It should not return a fake fallback candidate unless the endpoint response is valid but empty in a documented way.

## Workflow Migration

For the current workflow, migrate both Token Model Source inline specs:

```json
"backend": "llama_cpp"
```

to:

```json
"backend": "vllm"
```

Also verify:

- `model_name` is present and non-empty.
- `EOS` is present and non-empty.
- The source uses `prompt_template`, not `messages_template`.
- `type` is `"normal"` for this hotfix.

If editing through UI is required, frontend support must be added separately:

- token model source inline spec form backend options
- `KNOWN_BACKENDS`
- field schema defaults
- i18n labels
- frontend tests

Without those UI changes, this is a DB/DSL migration path only.

## Test Plan

Add focused tests before merging.

Required tests:

- Backend registry resolves `"vllm"` to `VllmBackend`.
- `VllmBackend.capabilities` does not include `Capability.CHAT_TEMPLATE`.
- `VllmSpec` rejects missing or empty `model_name` through the base spec contract.
- `VllmSpec` rejects empty `EOS`.
- Prompt resolution for a raw `prompt_template` source does not call `/apply-template`.
- A `messages_template` source with vLLM is rejected clearly unless chat-template support is implemented.
- `step_token()` sends `/completion` with the expected request body.
- vLLM `top_logprobs` are converted with `exp()` and re-normalized.
- EOS token is mapped to the ensemble end sentinel.
- Unknown or incompatible response shape fails explicitly.

Regression tests:

- Existing `llama_cpp` tests still pass.
- `llama_cpp` still advertises `CHAT_TEMPLATE`.
- Existing llama.cpp prompt wrapping behavior is unchanged.

## Validation Plan

Before running the full workflow, temporarily reduce:

```json
"runner_config": {
  "max_len": 5
}
```

or another small value.

Validation checklist:

- No request to `/apply-template`.
- Both sources call `/completion`.
- `token级并联集成` enters token-step generation.
- The first generated token has a sane candidate distribution whose probabilities sum to approximately 1 after top-k normalization.
- If the run fails, classify it as request contract, response parsing, endpoint availability, or workflow graph configuration.

## Risk Notes

The main implementation risk is not the 404 routing issue; it is probability semantics.

A backend that runs but treats vLLM logprobs as probabilities or logits will produce incorrect token ensemble behavior without an obvious crash. The vLLM parser and tests must be part of the initial hotfix, not a follow-up after runtime failure.

Do not remove `CHAT_TEMPLATE` from `LlamaCppBackend`; that would fix this workflow by breaking the backend contract for real llama.cpp deployments.

---

## Chat-Token Follow-up

## Background

The first vLLM compatibility hotfix avoids the original failure:

```text
HTTP request failed with status code 404 for .../apply-template
```

However, live endpoint testing showed that simply disabling
`CHAT_TEMPLATE` and sending a raw prompt to the vLLM completion endpoint
is not semantically reliable for the current instruct/chat models.

Observed on 2026-05-19:

- Both target endpoints return `404` for `/completion`.
- Both target endpoints support OpenAI-compatible `/v1/completions`.
- Raw prompt token stepping does not produce encoding garbage, but output
  is bad:
  - `tencent/Hunyuan-7B-Instruct-AWQ-Int4` repeatedly emits `？`.
  - `Intel/Qwen3.5-4B-int4-AutoRound` emits `<think>` / `Thinking Process`
    scaffold text instead of a direct answer.
- `/v1/chat/completions` is available, but it must be checked for
  token-level logprob support before it can replace raw completion.

Conclusion: the raw `vllm` backend is useful as a no-404 compatibility
path, but it should not be treated as the final TokenLevel solution for
chat/instruct models.

## Goals

- Preserve the current no-404 vLLM compatibility path.
- Add a semantically correct token-level path for vLLM chat/instruct
  models.
- Avoid server-side `/apply-template` calls for vLLM endpoints.
- Keep llama.cpp behavior unchanged.
- Make workflow migration explicit and reversible.

## Non-goals

- Full frontend productization of a new backend selector.
- Broad support for every OpenAI-compatible deployment variant.
- Full streaming support.
- Raw-logit support for vLLM.

## Current Endpoint Findings

### Completion Endpoint

The real endpoints accept:

```text
POST {model_url}/v1/completions
```

with a body like:

```json
{
  "model": "tencent/Hunyuan-7B-Instruct-AWQ-Int4",
  "prompt": "请直接回答：1+1等于几？",
  "max_tokens": 1,
  "temperature": 0,
  "logprobs": 5
}
```

The real endpoints do not accept:

```text
POST {model_url}/completion
```

### Raw Prompt Behavior

Raw prompt token stepping is technically valid but semantically poor.

Hunyuan sample:

```text
？？？？？？？？？？？？？？？？？？？？
```

Qwen sample:

```text
<think>
Thinking Process:

1. **Analyze the Request:** ...
```

This means the model likely needs a model-specific chat template or the
chat-completions API path.

## Proposed Backend Shape

Keep two paths conceptually separate.

### 1. `vllm`

Raw OpenAI-compatible completion fallback.

Contract:

- Endpoint: `/v1/completions`
- Token-step request includes `model`, `prompt`, `max_tokens: 1`, and
  `logprobs`
- Does not advertise `Capability.CHAT_TEMPLATE`
- Does not call `/apply-template`
- Parses completion `top_logprobs`
- Intended for compatibility and debugging, not final chat-model quality

### 2. `vllm_chat`

Chat-token backend for instruct/chat models.

Contract, if supported by the real endpoint:

- Endpoint: `/v1/chat/completions`
- Token-step request includes `model`, `messages`, `max_tokens: 1`,
  and token logprob options
- Maintains assistant prefix across token steps
- Parses chat `top_logprobs`
- Does not call `/apply-template`

Candidate request shape:

```json
{
  "model": "Intel/Qwen3.5-4B-int4-AutoRound",
  "messages": [
    {
      "role": "user",
      "content": "请直接回答：1+1等于几？"
    },
    {
      "role": "assistant",
      "content": "<already selected prefix>"
    }
  ],
  "max_tokens": 1,
  "temperature": 0,
  "logprobs": true,
  "top_logprobs": 5
}
```

If the endpoint does not support chat logprobs, do not fake token
probabilities. Fall back to the client-template plan below.

## Fallback: Client-side Chat Templates

If `/v1/chat/completions` cannot return top logprobs, implement local
template rendering instead of server-side `/apply-template`.

Possible spec extension:

```json
{
  "backend": "vllm_template",
  "model_name": "Intel/Qwen3.5-4B-int4-AutoRound",
  "model_url": "https://...",
  "EOS": "<|im_end|>",
  "chat_template": "qwen",
  "type": "normal"
}
```

The backend would:

1. Render `messages_template` locally into a prompt.
2. Append the selected assistant prefix each token step.
3. Call `/v1/completions`.
4. Parse completion `top_logprobs`.

This does not necessarily need a capability separate from
`Capability.CHAT_TEMPLATE`. The current node contract treats
`CHAT_TEMPLATE` as a backend ability to turn messages into the model
prompt format; llama.cpp implements that through `/apply-template`, but
a vLLM template backend can implement the same `apply_template()` method
locally without any server-side template endpoint. Reusing
`CHAT_TEMPLATE` for the local-template path is the lower-risk route
because it keeps the existing `messages_template` validation and
prompt-resolution branches intact.

A separate capability is only needed if the node and runner grow a direct
structured-message channel. The lower-risk `vllm_chat` implementation used
here keeps the current `SourceInput.prompt` contract: `apply_template()`
does local envelope encoding, declares `CHAT_TEMPLATE`, and `step_token()`
decodes the envelope back into `/v1/chat/completions` messages plus the
assistant prefix.

## Token-Step `max_tokens` Semantics

In the current `token_step` runner, backend `step_token()` requests must
force `max_tokens: 1`, even when source-side
`sampling_params.max_tokens` is greater than `1`.

Why this is required:

- `TokenStepRunner` is a consensus loop over exactly one next position.
  Each round asks every source for candidates for the same next token,
  the aggregator selects one candidate, the runner appends that accepted
  token, then the next round starts from the shared accepted prefix.
- `TokenCandidate` has scalar next-token semantics: one text delta, one
  probability/logprob, one EOS flag, and one trace record for that
  position. It does not represent a generated sequence, per-position
  probability tables, partial acceptance, or EOS inside a block.
- In OpenAI-compatible vLLM responses, later generated positions are
  conditional on the backend's own sampled earlier token, not on the
  ensemble-selected token. Feeding those later positions into the current
  aggregator would compare candidates from different histories.
- Treating a multi-token completion as one `TokenCandidate` would make
  probability normalization, trace, stop/EOS handling, and cross-model
  alignment incorrect.

The frontend and source node may still allow `sampling_params.max_tokens`
values greater than `1`. That value is valid for response-level generation
and for a future multi-token mode, but it is not the effective request
budget for the current `token_step` contract. The backend should clamp the
wire request to `max_tokens: 1` and, if diagnostics are available, record
both `requested_max_tokens` and `effective_max_tokens` so the behavior is
visible rather than silent.

Do not add backend-only multi-token exceptions, including whitespace-loop
lookahead. If a chat-template backend repeats leading whitespace because
of assistant-prefill trimming, fix the template/prefix preservation path
or move the workflow to an explicit block-level aggregation mode. The
current token runner must not append later positions behind the
aggregator's back.

Multi-token aggregation needs a separate runner / aggregator contract. A
future `sequence_step` or `block_step` mode would need a sequence
candidate shape, for example:

```python
SequenceCandidate(
    text=...,
    tokens=[...],
    token_logprobs=[...],
    position_top_logprobs=[...],
    finish_reason=...,
)
```

That future contract must define how to align different candidate lengths,
whether to append an entire block or only an accepted prefix, what happens
when EOS appears inside a block, and whether trace is token-level or
block-level.

## Review-driven Corrections

The plan must account for these implementation constraints before coding:

1. Current startup validation rejects `messages_template` when the backend
   does not declare `Capability.CHAT_TEMPLATE`. A `vllm_chat` backend that
   consumes `messages` directly cannot work by only adding a new backend;
   the node validation and source payload contract must change first, or
   the backend must use local `apply_template()` and declare
   `CHAT_TEMPLATE`.
2. Current `SourceInput` contains only `prompt`, `params`, and `weight`.
   `/v1/chat/completions` needs structured `messages` plus the assistant
   prefix at each token step, so the data path must be designed before
   `vllm_chat` is implemented.
3. The `model_url` contract must be explicit. For OpenAI-compatible vLLM
   endpoints, `model_url` should be the API server or model endpoint root
   that receives `/v1/completions` or `/v1/chat/completions`; it must not
   already include the final route segment.
4. The raw `vllm` parser should include a regression test where a real
   token string is literally `token`; token-logprob maps and
   candidate-object lists must not be confused.

## Implementation Plan

### P0. Stabilize Existing Hotfix

- Keep the raw `vllm` backend registered.
- Use `/v1/completions`, not `/completion`.
- Send `logprobs: top_k`, not only `n_probs`.
- Force `max_tokens: 1` in `step_token()`, regardless of source-side
  `sampling_params.max_tokens`.
- Keep `CHAT_TEMPLATE` absent.
- Keep `messages_template` rejected for raw `vllm`.
- Fix and test the `top_logprobs` parser so token-logprob maps with a
  token named `token` are not mistaken for candidate-object lists.

Acceptance:

- `vllm` no longer 404s on the current endpoints.
- Raw prompt path remains explicitly documented as quality-limited.
- `step_token()` sends `max_tokens: 1` on the wire.
- If the source requested more than one token, diagnostics expose the
  requested value and the effective clamped value.

### P1. Probe Chat Logprob Capability

For each target model, test:

- `/v1/chat/completions` with `logprobs: true`
- `/v1/chat/completions` with `top_logprobs: k`
- direct endpoint `max_tokens` values, including values greater than `1`,
  to evaluate future block-level aggregation; `token_step` still clamps
  to `1`
- assistant prefix continuation
- EOS / stop reason handling

Record:

- HTTP status
- response shape
- location of generated token
- location of top candidates
- whether logprobs are real logprobs or missing/null

Decision:

- If chat top logprobs are present, implement `vllm_chat`.
- If chat top logprobs are absent, implement client-side template
  rendering.

### P2. Preserve Messages Without Changing Runner SPI

The current `SourceInput` only carries `prompt`, `params`, and `weight`.
Changing that contract would broaden the migration, so `vllm_chat` uses a
backend-private prompt envelope instead:

1. Node calls `backend.apply_template(messages)` because `vllm_chat`
   declares `Capability.CHAT_TEMPLATE`.
2. `vllm_chat.apply_template()` encodes the structured messages into the
   prompt string locally; it does not call `/apply-template`.
3. The token runner appends the selected token to the same prompt string.
4. `vllm_chat.step_token()` decodes the original messages plus appended
   assistant prefix and calls `/v1/chat/completions`.

Acceptance:

- `messages_template` with raw `vllm` is still rejected.
- `messages_template` with `vllm_chat` succeeds through local envelope
  encoding and `CHAT_TEMPLATE`.
- The token runner remains backend-agnostic and unchanged.

### P3. Implement `vllm_chat` If Chat Logprobs Work

Add:

```text
api/core/workflow/nodes/parallel_ensemble/backends/vllm_chat.py
```

Schema:

```python
class VllmChatSpec(BaseSpec):
    backend: Literal["vllm_chat"]
    model_url: AnyUrl
    EOS: str = Field(min_length=1)
    type: Literal["normal"] = "normal"
    stop_think: str | None = None
```

Capabilities:

```python
frozenset({
    Capability.TOKEN_STEP,
    Capability.TOP_PROBS,
    Capability.POST_SAMPLING_PROBS,
    Capability.CHAT_TEMPLATE,
})
```

`Capability.CHAT_TEMPLATE` means local message-to-envelope rendering for
this backend. It does not mean the backend calls a server-side
`/apply-template` endpoint.

If P1 shows that `/v1/chat/completions` does not provide usable token
logprobs, skip this backend and implement `vllm_template` instead.

### P3b. Implement `vllm_template` If Chat Logprobs Do Not Work

This path should implement local `apply_template()` and declare
`Capability.CHAT_TEMPLATE`, because it renders messages to a completion
prompt before token stepping. It should still call `/v1/completions` and
parse completion `top_logprobs`.

### P4. Add Explicit Multi-token Aggregation Mode

This is separate from the raw vLLM no-404 hotfix. The token-level node can
expose multi-token behavior as an explicit aggregation choice, not as a
backend side effect.

Candidate shape:

- Keep `TokenCandidate` for `single_token_consensus`.
- Add `SequenceCandidate` for block-level candidates with token text,
  token ids if available, per-token logprobs, per-position top-logprobs,
  finish reason, and EOS location.

Node / runner configuration:

- `step_granularity: "token" | "block"`
- `max_tokens_per_step` used only when `step_granularity == "block"`
- `aggregation_strategy` chosen from explicit strategy ids.

Initial strategy ids:

- `single_token_consensus`: current behavior; always requests
  `max_tokens: 1`.
- `sequence_vote`: compare complete candidate blocks and append the
  selected block.
- `accepted_prefix`: find the weighted agreed prefix across generated
  blocks and append only that prefix.
- `positionwise_consensus`: aggregate one position at a time inside a
  block, stopping when candidates diverge or EOS appears.

Acceptance:

- A frontend source may request `max_tokens > 1`, but the token-level node
  uses that value only when a block strategy is selected.
- Token-mode and block-mode traces are distinguishable.
- EOS inside a block has explicit behavior per strategy.
- Existing `single_token_consensus` behavior and tests remain unchanged.

### P5. Workflow Migration

Short term:

```json
"backend": "vllm"
```

Only use this to verify no-404 execution.

Final target, if chat logprobs work:

```json
"backend": "vllm_chat"
```

Final target, if local templates are required:

```json
{
  "backend": "vllm_template",
  "chat_template": "qwen"
}
```

Migration checklist:

- `model_name` is non-empty.
- `model_url` points to the base model endpoint.
- `EOS` is non-empty and model-specific.
- `type` is `normal`.
- `messages_template` is only enabled once the backend path supports it.
- Raw `prompt_template` is not used as the final quality path for these
  chat/instruct models.

## Test Plan

### Unit Tests

- `vllm` registry resolves to `VllmBackend`.
- `vllm` does not include `Capability.CHAT_TEMPLATE`.
- `vllm` posts to `/v1/completions`.
- `vllm` request includes `model` and `logprobs`.
- `vllm` `step_token()` clamps the backend request to `max_tokens: 1`
  and records requested/effective values when diagnostics are available.
- `vllm` parses completion `top_logprobs` via `exp()` and re-normalizes.
- `vllm` parses a token-logprob map that contains a literal `token`
  token.
- Unknown vLLM response shapes raise a backend response error.
- `messages_template` with raw `vllm` is rejected clearly.

For `vllm_chat`:

- Posts to `/v1/chat/completions`.
- Sends `messages` plus assistant prefix.
- Requests `max_tokens: 1` in token-step mode.
- Requests `top_logprobs`.
- Parses chat token candidates.
- Remaps EOS to `<end>`.
- Fails explicitly if chat logprobs are absent.

### Live Smoke Tests

Run against both target endpoints:

- 20-token raw `vllm` smoke, expected to be no-404 but quality-limited.
- 20-token `vllm_chat` or template smoke.
- Verify output does not repeat `？`.
- Verify output does not start with unintended template scaffold unless
  the model is explicitly configured to expose reasoning.
- Verify no replacement character `�` or invalid control characters.

## Open Questions

- Which block-level aggregation strategies should be exposed first in
  the token-level node UI?
- Which exact chat templates are required for Hunyuan and Qwen?
- Should `<think>` be stripped, stopped, or allowed for Qwen-style models?
- Should raw `vllm` remain available in the UI, or only as a DB/DSL
  migration escape hatch?

## Recommended Next Step

Use `vllm_chat` for the next workflow migration smoke. Keep raw `vllm` as
the no-404 fallback, but do not treat it as the final quality path for the
current chat/instruct models.
