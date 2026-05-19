# TokenLevel vLLM Compatibility Hotfix Plan

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
