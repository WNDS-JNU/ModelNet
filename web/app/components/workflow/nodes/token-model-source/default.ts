import type { NodeDefault } from '../../types'
import type { TokenModelSourceNodeType } from './types'
import { BlockClassificationEnum } from '@/app/components/workflow/block-selector/types'
import { BlockEnum } from '@/app/components/workflow/types'
import { genNodeMetaData } from '@/app/components/workflow/utils'
import { DEFAULT_SAMPLING_PARAMS } from './types'

const i18nPrefix = 'nodes.tokenModelSource'

// Pydantic ``AnyUrl`` accepts any URL with a non-empty scheme + host.
// Mirror the bare minimum here: the browser's URL constructor accepts
// strings the backend will also accept (http/https/etc with scheme).
// Bare hostnames ("127.0.0.1:8080") and relative paths are rejected,
// matching ``LlamaCppSpec.model_url: AnyUrl``.
const isWellFormedUrl = (raw: string): boolean => {
  try {
    const parsed = new URL(raw)
    // ``new URL("foo:")`` succeeds with an empty host; reject so the
    // user cannot save a half-typed URL pydantic would refuse.
    return parsed.protocol.length > 1 && parsed.host.length > 0
  }
  catch {
    return false
  }
}

const metaData = genNodeMetaData({
  author: 'xianghe',
  // ``Transform`` keeps the node grouped with parallel-ensemble — they
  // are typically dropped in pairs (multiple sources → one ensemble),
  // and the picker reads top-to-bottom in the same Transform section.
  classification: BlockClassificationEnum.Transform,
  // Sort 6 places it directly after parallel-ensemble (sort 5). The
  // canvas picker reads top-to-bottom, so the order matches the typical
  // build flow: drop a parallel-ensemble first, then add 2+ token
  // sources to feed it.
  sort: 6,
  type: BlockEnum.TokenModelSource,
})

const nodeDefault: NodeDefault<TokenModelSourceNodeType> = {
  metaData,
  defaultValue: {
    model_alias: '',
    prompt_template: '',
    sampling_params: { ...DEFAULT_SAMPLING_PARAMS },
    extra: {},
    // ``null`` is the canonical "registered alias mode" — keeps the
    // saved DSL shape stable across the two modes and lets pydantic
    // round-trip it without distinguishing ``undefined`` from
    // ``None``.
    inline_spec: null,
  },
  checkValid(payload, t) {
    let errorMessage = ''

    // ── model_alias: required, non-blank string ──────────────────
    // Mirrors backend ``TokenModelSourceNodeData.model_alias``
    // (entities.py): ``Field(..., min_length=1)`` + a ``strip``
    // validator. Catching this here means the DSL save flow never
    // produces a payload pydantic will reject — same defence-in-depth
    // pattern parallel-ensemble's checkValid uses.
    const alias = payload?.model_alias
    if (typeof alias !== 'string' || alias.trim().length === 0) {
      errorMessage = t('errorMsg.fieldRequired', {
        ns: 'workflow',
        field: t(`${i18nPrefix}.modelAlias`, { ns: 'workflow' }),
      })
    }

    // ── sampling_params: shape + bounds ──────────────────────────
    // The backend pydantic layer guards every bound (``top_k > 0``,
    // ``temperature >= 0``, ``max_tokens > 0``, ``top_p in (0, 1]``).
    // Replay the same checks here so the panel red-lines before save
    // — a saved-then-rejected payload corrupts the workflow's draft
    // state and forces a refresh.
    const sp = payload?.sampling_params
    if (!errorMessage) {
      if (!sp || typeof sp !== 'object' || Array.isArray(sp)) {
        errorMessage = t(`${i18nPrefix}.errorMsg.samplingParamsMissing`, {
          ns: 'workflow',
        })
      }
      else {
        if (
          typeof sp.top_k !== 'number'
          || !Number.isInteger(sp.top_k)
          || sp.top_k <= 0
        ) {
          // ``Number.isInteger`` rather than ``Number.isFinite``:
          // backend ``SamplingParams.top_k`` is ``int`` (entities.py),
          // so 1.5 round-trips to a Pydantic ValidationError. Catch
          // it here so the panel red-lines pre-save instead of
          // surfacing as a runtime "422" the user can't trace.
          errorMessage = t(`${i18nPrefix}.errorMsg.topKPositive`, { ns: 'workflow' })
        }
        else if (
          typeof sp.temperature !== 'number'
          || !Number.isFinite(sp.temperature)
          || sp.temperature < 0
        ) {
          errorMessage = t(`${i18nPrefix}.errorMsg.temperatureNonNegative`, {
            ns: 'workflow',
          })
        }
        else if (
          typeof sp.max_tokens !== 'number'
          || !Number.isInteger(sp.max_tokens)
          || sp.max_tokens <= 0
        ) {
          // Same int-only contract as top_k — backend
          // ``SamplingParams.max_tokens`` is an integer.
          errorMessage = t(`${i18nPrefix}.errorMsg.maxTokensPositive`, {
            ns: 'workflow',
          })
        }
        else if (
          sp.top_p !== null
          && sp.top_p !== undefined
          && (
            typeof sp.top_p !== 'number'
            || !Number.isFinite(sp.top_p)
            || sp.top_p <= 0
            || sp.top_p > 1
          )
        ) {
          errorMessage = t(`${i18nPrefix}.errorMsg.topPRange`, { ns: 'workflow' })
        }
        else if (
          sp.seed !== null
          && sp.seed !== undefined
          && (typeof sp.seed !== 'number' || !Number.isInteger(sp.seed))
        ) {
          errorMessage = t(`${i18nPrefix}.errorMsg.seedInteger`, { ns: 'workflow' })
        }
        else if (!Array.isArray(sp.stop) || sp.stop.some(s => typeof s !== 'string')) {
          errorMessage = t(`${i18nPrefix}.errorMsg.stopList`, { ns: 'workflow' })
        }
      }
    }

    // ── extra: plain object only ─────────────────────────────────
    // ``extra`` is the documented escape hatch for backend-private
    // sampling knobs (vLLM ``repetition_penalty``, research_tag, ...).
    // The backend's ``Field(default_factory=dict)`` will reject a list
    // / scalar at validate time; pre-empt it here so the panel doesn't
    // need to ship round-trip recovery.
    const extra = payload?.extra
    if (!errorMessage && extra !== undefined && extra !== null) {
      if (typeof extra !== 'object' || Array.isArray(extra)) {
        errorMessage = t(`${i18nPrefix}.errorMsg.extraMustBeObject`, {
          ns: 'workflow',
        })
      }
    }

    // ── inline_spec: shape + required keys ───────────────────────
    // ``null`` = registered mode (skip). When set, replay the
    // server-side ``_inline_spec_shape`` + per-backend invariants so
    // the panel red-lines pre-save: the backend's pydantic class
    // would otherwise surface a 422 the user cannot trace. Today
    // ``llama_cpp`` is the only registered backend, so checks below
    // mirror ``LlamaCppSpec`` (entities at api/core/workflow/nodes/
    // parallel_ensemble/backends/llama_cpp.py).
    const inlineSpec = payload?.inline_spec
    if (!errorMessage && inlineSpec !== undefined && inlineSpec !== null) {
      if (typeof inlineSpec !== 'object' || Array.isArray(inlineSpec)) {
        errorMessage = t(`${i18nPrefix}.errorMsg.inlineSpecMustBeObject`, {
          ns: 'workflow',
          defaultValue: 'Inline model spec must be a JSON object.',
        })
      }
      else if (
        typeof inlineSpec.backend !== 'string'
        || inlineSpec.backend.trim().length === 0
      ) {
        errorMessage = t(`${i18nPrefix}.errorMsg.inlineSpecBackendRequired`, {
          ns: 'workflow',
          defaultValue: 'Backend is required for a custom model.',
        })
      }
      else if (
        typeof inlineSpec.model_name !== 'string'
        || inlineSpec.model_name.trim().length === 0
      ) {
        errorMessage = t(`${i18nPrefix}.errorMsg.inlineSpecModelNameRequired`, {
          ns: 'workflow',
          defaultValue: 'Model name is required for a custom model.',
        })
      }
      else if (inlineSpec.backend === 'llama_cpp') {
        if (typeof inlineSpec.model_url !== 'string' || inlineSpec.model_url.trim().length === 0) {
          errorMessage = t(`${i18nPrefix}.errorMsg.inlineSpecModelUrlRequired`, {
            ns: 'workflow',
            defaultValue: 'Model URL is required for llama.cpp.',
          })
        }
        else if (!isWellFormedUrl(inlineSpec.model_url)) {
          // ``LlamaCppSpec.model_url`` is typed as pydantic
          // ``AnyUrl`` server-side — it must parse as a URL with a
          // scheme. Catch the obvious "looks like a path / hostname
          // with no scheme" mistake here so the panel red-lines
          // pre-save instead of surfacing as a 422.
          errorMessage = t(`${i18nPrefix}.errorMsg.inlineSpecModelUrlInvalid`, {
            ns: 'workflow',
            defaultValue: 'Model URL must be a valid URL with scheme (e.g. http://host:port).',
          })
        }
        else if (typeof inlineSpec.EOS !== 'string' || inlineSpec.EOS.length === 0) {
          // ``EOS`` is ``min_length=1`` server-side; matches the
          // ``LlamaCppSpec.EOS`` invariant.
          errorMessage = t(`${i18nPrefix}.errorMsg.inlineSpecEosRequired`, {
            ns: 'workflow',
            defaultValue: 'EOS token is required for llama.cpp.',
          })
        }
        else if (
          inlineSpec.type !== undefined
          && inlineSpec.type !== 'normal'
          && inlineSpec.type !== 'think'
        ) {
          errorMessage = t(`${i18nPrefix}.errorMsg.inlineSpecTypeInvalid`, {
            ns: 'workflow',
            defaultValue: 'Model type must be "normal" or "think".',
          })
        }
      }

      // ``request_timeout_ms`` is backend-agnostic — ``BaseSpec`` requires
      // ``> 0`` and integer-typed server-side. Validate here so the panel
      // red-lines instead of surfacing as a pydantic 422 the user can't
      // trace back to the field.
      if (
        !errorMessage
        && inlineSpec.request_timeout_ms !== undefined
        && inlineSpec.request_timeout_ms !== null
      ) {
        const rt = inlineSpec.request_timeout_ms
        if (
          typeof rt !== 'number'
          || !Number.isFinite(rt)
          || !Number.isInteger(rt)
          || rt <= 0
        ) {
          errorMessage = t(`${i18nPrefix}.errorMsg.inlineSpecRequestTimeoutPositive`, {
            ns: 'workflow',
            defaultValue: 'Request timeout must be a positive integer (ms).',
          })
        }
      }

      if (!errorMessage && 'id' in (inlineSpec as Record<string, unknown>)) {
        // Server-side ``_inline_spec_shape`` rejects a smuggled ``id``;
        // mirror the rule so a panel that somehow accumulates one
        // (manual DSL edit, future bug) surfaces the same red-line
        // pre-save.
        errorMessage = t(`${i18nPrefix}.errorMsg.inlineSpecIdForbidden`, {
          ns: 'workflow',
          defaultValue: 'Inline spec cannot carry an "id" field; model_alias is used instead.',
        })
      }
    }

    return {
      isValid: !errorMessage,
      errorMessage,
    }
  },
}

export default nodeDefault
