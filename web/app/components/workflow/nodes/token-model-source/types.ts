import type { CommonNodeType } from '@/app/components/workflow/types'

export const TOKEN_MODEL_SOURCE_NODE_TYPE = 'token-model-source' as const

// Mirrors backend ``SamplingParams`` (api/core/workflow/nodes/
// token_model_source/entities.py). ``extra="forbid"`` is enforced at
// the backend Pydantic layer; on this side we keep the shape narrow so
// a typo (``temprature``) in the saved DSL becomes a TS error rather
// than a silent no-op at run time.
export type SamplingParams = {
  top_k: number
  temperature: number
  max_tokens: number
  top_p: number | null
  seed: number | null
  stop: string[]
}

// ``ModelInvocationSpec`` is the wire shape this node emits into the
// variable pool — downstream ``parallel-ensemble`` (P3.B.3) consumes it
// by selector. Frontend never instantiates one; the type lives here
// purely so panels that *consume* the spec selector (P3.B.4) can pin
// the expected shape statically.
export type ModelInvocationSpec = {
  model_alias: string
  prompt: string
  sampling_params: SamplingParams
  extra: Record<string, unknown>
  raw_completion?: boolean
  inline_spec?: InlineModelSpec | null
}

// Wire shape for the optional inline backend spec the panel produces
// when the user picks "Custom model" instead of a registered alias.
// Mirrors the per-backend yaml entry in ``api/configs/model_net.yaml``
// minus the ``id`` field — that role is played by ``model_alias`` on
// the parent ``TokenModelSourceNodeType``. The shape is intentionally
// open (``[key: string]: unknown``) so a third-party backend adding
// a new ``BaseSpec`` subclass server-side does not force a frontend
// type extension — the per-backend pydantic class on the parallel-
// ensemble side is the authoritative schema. Today only ``llama_cpp``
// is registered, so the rendered fields are tuned for it; future
// backends will surface their fields through a backend-aware form
// switch.
export type InlineModelSpec = {
  backend: string
  model_name: string
  // llama_cpp-specific fields. Optional at this layer because a
  // future backend may not carry them — the server-side spec class
  // rejects the wire if its required fields are missing.
  model_url?: string
  EOS?: string
  type?: 'normal' | 'think'
  stop_think?: string | null
  expose_raw_logits?: boolean
  model_arch?: string
  request_timeout_ms?: number
  // ``BaseSpec.weight`` is deliberately omitted: the runtime weight
  // for the parallel-ensemble vote comes from
  // ``ParallelEnsembleConfig.token_sources[].weight`` on the consumer
  // node, not from the spec. Surfacing it here would create two
  // overlapping knobs with no defined precedence.
  [key: string]: unknown
}

export type TokenModelSourceNodeType = CommonNodeType & {
  model_alias: string
  prompt_template: string
  // ``false`` is the backend default: chat-capable backends auto-wrap
  // ``prompt_template`` as a single user message before token stepping.
  // ``true`` preserves PN.py-style raw completion for research prompts
  // that already include exact model-specific scaffolding.
  raw_completion?: boolean
  sampling_params: SamplingParams
  extra: Record<string, unknown>
  // ``null`` (the canonical "use registered alias" state) is the
  // saved default; ``undefined`` is treated identically by both the
  // panel and the backend (it strips through to ``inline_spec=None``).
  inline_spec?: InlineModelSpec | null
}

// Defaults track ``SamplingParams`` Field defaults (entities.py): the
// backend-level form is the canonical source. Diverging defaults here
// would let a panel-saved DSL look one way pre-load and another
// post-validate — the round-trip mismatch CLAUDE.md flags.
export const DEFAULT_SAMPLING_PARAMS: SamplingParams = {
  top_k: 10,
  temperature: 0.7,
  max_tokens: 1024,
  top_p: null,
  seed: null,
  stop: [],
}

// Default shape for a fresh "Custom model" tab. ``backend`` defaults to
// ``llama_cpp`` because that is the only built-in backend today; the
// dropdown still lets the user pick a different one if more backends
// register. ``EOS`` is required by ``LlamaCppSpec`` server-side and
// has no canonical default — leaving it empty surfaces the panel
// red-line before save. ``model_url`` is pre-seeded with the lab's
// in-house llama.cpp host so a fresh node renders something usable
// and the user only needs to type the port.
export const DEFAULT_INLINE_SPEC: InlineModelSpec = {
  backend: 'llama_cpp',
  model_name: '',
  model_url: 'http://219.222.20.79',
  EOS: '',
  type: 'normal',
  stop_think: null,
  expose_raw_logits: false,
}
