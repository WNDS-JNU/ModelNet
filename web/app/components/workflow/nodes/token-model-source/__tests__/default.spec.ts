import type { TokenModelSourceNodeType } from '../types'
import { describe, expect, it } from 'vitest'
import { BlockEnum } from '@/app/components/workflow/types'
import nodeDefault from '../default'
import { DEFAULT_SAMPLING_PARAMS } from '../types'

// ── Stub `t`: passes through the resolved key + interp args so the
// test can assert *which* error fired without coupling to copy. The
// real i18n file is asserted separately by the i18n key-coverage
// suite.
const t = (key: string, opts?: Record<string, unknown>) => {
  if (!opts)
    return key
  if (typeof opts.field === 'string')
    return `${key}:${opts.field}`
  return key
}

const buildPayload = (
  overrides: Partial<TokenModelSourceNodeType> = {},
): TokenModelSourceNodeType => ({
  title: 'src',
  desc: '',
  type: BlockEnum.TokenModelSource,
  model_alias: 'qwen3-4b',
  prompt_template: 'Answer: {{#start.q#}}',
  sampling_params: { ...DEFAULT_SAMPLING_PARAMS },
  extra: {},
  ...overrides,
})

describe('token-model-source/default.checkValid', () => {
  describe('happy path', () => {
    it('accepts a fully populated payload', () => {
      const result = nodeDefault.checkValid(buildPayload(), t)
      expect(result.isValid).toBe(true)
      expect(result.errorMessage).toBe('')
    })

    it('accepts an empty prompt_template (constant prompt is legal)', () => {
      // Mirrors backend ``TokenModelSourceNodeData.prompt_template = ""``
      // — constant prompts skip the variable pool entirely.
      const result = nodeDefault.checkValid(
        buildPayload({ prompt_template: '' }),
        t,
      )
      expect(result.isValid).toBe(true)
    })

    it('accepts temperature = 0 (greedy decoding)', () => {
      const result = nodeDefault.checkValid(
        buildPayload({
          sampling_params: { ...DEFAULT_SAMPLING_PARAMS, temperature: 0 },
        }),
        t,
      )
      expect(result.isValid).toBe(true)
    })

    it('accepts top_p = 1 (boundary)', () => {
      const result = nodeDefault.checkValid(
        buildPayload({
          sampling_params: { ...DEFAULT_SAMPLING_PARAMS, top_p: 1 },
        }),
        t,
      )
      expect(result.isValid).toBe(true)
    })
  })

  describe('model_alias guards', () => {
    it.each([
      ['empty string', ''],
      ['blank whitespace', '   '],
    ])('rejects %s model_alias', (_, alias) => {
      const result = nodeDefault.checkValid(
        buildPayload({ model_alias: alias }),
        t,
      )
      expect(result.isValid).toBe(false)
      expect(result.errorMessage).toContain('errorMsg.fieldRequired')
    })
  })

  describe('sampling_params bound guards', () => {
    it('rejects top_k = 0', () => {
      const result = nodeDefault.checkValid(
        buildPayload({
          sampling_params: { ...DEFAULT_SAMPLING_PARAMS, top_k: 0 },
        }),
        t,
      )
      expect(result.errorMessage).toContain('topKPositive')
    })

    it('rejects negative top_k', () => {
      const result = nodeDefault.checkValid(
        buildPayload({
          sampling_params: { ...DEFAULT_SAMPLING_PARAMS, top_k: -1 },
        }),
        t,
      )
      expect(result.errorMessage).toContain('topKPositive')
    })

    it('rejects fractional top_k (backend SamplingParams.top_k is int)', () => {
      // Pin the int-only contract — backend Pydantic 422s on a float
      // and the panel must red-line pre-save instead of surfacing as
      // a runtime error.
      const result = nodeDefault.checkValid(
        buildPayload({
          sampling_params: { ...DEFAULT_SAMPLING_PARAMS, top_k: 1.5 },
        }),
        t,
      )
      expect(result.errorMessage).toContain('topKPositive')
    })

    it('rejects negative temperature', () => {
      const result = nodeDefault.checkValid(
        buildPayload({
          sampling_params: { ...DEFAULT_SAMPLING_PARAMS, temperature: -0.1 },
        }),
        t,
      )
      expect(result.errorMessage).toContain('temperatureNonNegative')
    })

    it('rejects max_tokens = 0', () => {
      const result = nodeDefault.checkValid(
        buildPayload({
          sampling_params: { ...DEFAULT_SAMPLING_PARAMS, max_tokens: 0 },
        }),
        t,
      )
      expect(result.errorMessage).toContain('maxTokensPositive')
    })

    it('rejects fractional max_tokens (backend int-only)', () => {
      const result = nodeDefault.checkValid(
        buildPayload({
          sampling_params: { ...DEFAULT_SAMPLING_PARAMS, max_tokens: 64.5 },
        }),
        t,
      )
      expect(result.errorMessage).toContain('maxTokensPositive')
    })

    it('rejects top_p = 0 (gt=0 backend rule, pin it)', () => {
      const result = nodeDefault.checkValid(
        buildPayload({
          sampling_params: { ...DEFAULT_SAMPLING_PARAMS, top_p: 0 },
        }),
        t,
      )
      expect(result.errorMessage).toContain('topPRange')
    })

    it('rejects top_p > 1', () => {
      const result = nodeDefault.checkValid(
        buildPayload({
          sampling_params: { ...DEFAULT_SAMPLING_PARAMS, top_p: 1.01 },
        }),
        t,
      )
      expect(result.errorMessage).toContain('topPRange')
    })

    it('accepts null top_p (sampling cutoff disabled)', () => {
      const result = nodeDefault.checkValid(
        buildPayload({
          sampling_params: { ...DEFAULT_SAMPLING_PARAMS, top_p: null },
        }),
        t,
      )
      expect(result.isValid).toBe(true)
    })

    it('rejects fractional seed', () => {
      const result = nodeDefault.checkValid(
        buildPayload({
          sampling_params: { ...DEFAULT_SAMPLING_PARAMS, seed: 1.5 },
        }),
        t,
      )
      expect(result.errorMessage).toContain('seedInteger')
    })

    it('rejects non-string entry inside stop list', () => {
      const result = nodeDefault.checkValid(
        buildPayload({
          sampling_params: {
            ...DEFAULT_SAMPLING_PARAMS,
            stop: ['ok', 42 as unknown as string],
          },
        }),
        t,
      )
      expect(result.errorMessage).toContain('stopList')
    })

    it('rejects sampling_params replaced by an array (DSL smuggle)', () => {
      const result = nodeDefault.checkValid(
        buildPayload({
          sampling_params: [] as unknown as typeof DEFAULT_SAMPLING_PARAMS,
        }),
        t,
      )
      expect(result.errorMessage).toContain('samplingParamsMissing')
    })
  })

  describe('extra bag guards', () => {
    it('accepts arbitrary extra dict (vLLM repetition_penalty case)', () => {
      const result = nodeDefault.checkValid(
        buildPayload({
          extra: { repetition_penalty: 1.1, research_tag: 'exp_42' },
        }),
        t,
      )
      expect(result.isValid).toBe(true)
    })

    it('rejects extra replaced by an array', () => {
      const result = nodeDefault.checkValid(
        buildPayload({
          extra: ['a', 'b'] as unknown as Record<string, unknown>,
        }),
        t,
      )
      expect(result.errorMessage).toContain('extraMustBeObject')
    })
  })

  describe('inline_spec guards', () => {
    // Mirrors backend ``_inline_spec_shape`` (entities.py) — the panel
    // red-lines every error pydantic would 422 on after save.
    const goodLlamaInline = {
      backend: 'llama_cpp',
      model_name: 'llama-3.1-8b-instruct',
      model_url: 'http://127.0.0.1:8080',
      EOS: '<|eot_id|>',
      type: 'normal' as const,
    }

    it('accepts a fully populated llama_cpp inline spec', () => {
      const result = nodeDefault.checkValid(
        buildPayload({ inline_spec: goodLlamaInline }),
        t,
      )
      expect(result.isValid).toBe(true)
    })

    it('treats null inline_spec as registered-alias mode (no inline check)', () => {
      const result = nodeDefault.checkValid(
        buildPayload({ inline_spec: null }),
        t,
      )
      expect(result.isValid).toBe(true)
    })

    it('rejects inline_spec replaced by an array (DSL smuggle)', () => {
      const result = nodeDefault.checkValid(
        buildPayload({
          inline_spec: ['x'] as unknown as typeof goodLlamaInline,
        }),
        t,
      )
      expect(result.errorMessage).toContain('inlineSpecMustBeObject')
    })

    it.each([
      ['missing', undefined],
      ['empty', ''],
      ['blank', '   '],
    ])('rejects %s backend', (_, backend) => {
      const result = nodeDefault.checkValid(
        buildPayload({
          inline_spec: {
            ...goodLlamaInline,
            backend: backend as unknown as string,
          },
        }),
        t,
      )
      expect(result.errorMessage).toContain('inlineSpecBackendRequired')
    })

    it.each([
      ['missing', undefined],
      ['empty', ''],
      ['blank', '   '],
    ])('rejects %s model_name', (_, model_name) => {
      const result = nodeDefault.checkValid(
        buildPayload({
          inline_spec: {
            ...goodLlamaInline,
            model_name: model_name as unknown as string,
          },
        }),
        t,
      )
      expect(result.errorMessage).toContain('inlineSpecModelNameRequired')
    })

    it('rejects llama_cpp inline spec missing model_url', () => {
      const result = nodeDefault.checkValid(
        buildPayload({
          inline_spec: { ...goodLlamaInline, model_url: '' },
        }),
        t,
      )
      expect(result.errorMessage).toContain('inlineSpecModelUrlRequired')
    })

    it('rejects llama_cpp inline spec missing EOS', () => {
      const result = nodeDefault.checkValid(
        buildPayload({
          inline_spec: { ...goodLlamaInline, EOS: '' },
        }),
        t,
      )
      expect(result.errorMessage).toContain('inlineSpecEosRequired')
    })

    it('rejects invalid type value on llama_cpp inline spec', () => {
      const result = nodeDefault.checkValid(
        buildPayload({
          inline_spec: {
            ...goodLlamaInline,
            type: 'reasoning' as unknown as 'normal' | 'think',
          },
        }),
        t,
      )
      expect(result.errorMessage).toContain('inlineSpecTypeInvalid')
    })

    it('rejects an "id" field smuggled into the inline spec', () => {
      const result = nodeDefault.checkValid(
        buildPayload({
          inline_spec: {
            ...goodLlamaInline,
            id: 'smuggled-id',
          } as typeof goodLlamaInline,
        }),
        t,
      )
      expect(result.errorMessage).toContain('inlineSpecIdForbidden')
    })

    describe('model_url URL shape (llama_cpp)', () => {
      // Mirrors ``LlamaCppSpec.model_url: AnyUrl`` — must be parseable
      // by ``new URL`` with a scheme + host. Bare hostnames and
      // relative paths are rejected.
      it.each([
        ['bare hostname', '127.0.0.1:8080'],
        ['relative path', '/api/completion'],
        ['no scheme', 'host.example.com'],
        ['scheme only', 'http:'],
      ])('rejects %s', (_, model_url) => {
        const result = nodeDefault.checkValid(
          buildPayload({
            inline_spec: { ...goodLlamaInline, model_url },
          }),
          t,
        )
        expect(result.errorMessage).toContain('inlineSpecModelUrlInvalid')
      })

      it.each([
        ['http://127.0.0.1:8080'],
        ['https://llama.example.com'],
        ['http://localhost:8080/'],
      ])('accepts %s', (model_url) => {
        const result = nodeDefault.checkValid(
          buildPayload({
            inline_spec: { ...goodLlamaInline, model_url },
          }),
          t,
        )
        expect(result.isValid).toBe(true)
      })
    })

    describe('request_timeout_ms guard', () => {
      // ``BaseSpec.request_timeout_ms`` is ``int`` with ``gt=0``;
      // mirror server-side invariants so pydantic never sees a
      // payload it would 422 on.
      it('accepts undefined (backend default applies)', () => {
        const result = nodeDefault.checkValid(
          buildPayload({
            inline_spec: { ...goodLlamaInline, request_timeout_ms: undefined },
          }),
          t,
        )
        expect(result.isValid).toBe(true)
      })

      it.each([
        ['zero', 0],
        ['negative', -1],
        ['fractional', 1500.5],
        ['NaN', Number.NaN],
        ['Infinity', Number.POSITIVE_INFINITY],
      ])('rejects %s request_timeout_ms', (_, request_timeout_ms) => {
        const result = nodeDefault.checkValid(
          buildPayload({
            inline_spec: {
              ...goodLlamaInline,
              request_timeout_ms: request_timeout_ms as unknown as number,
            },
          }),
          t,
        )
        expect(result.errorMessage).toContain('inlineSpecRequestTimeoutPositive')
      })

      it('rejects non-numeric request_timeout_ms (DSL smuggle)', () => {
        const result = nodeDefault.checkValid(
          buildPayload({
            inline_spec: {
              ...goodLlamaInline,
              request_timeout_ms: '30000' as unknown as number,
            },
          }),
          t,
        )
        expect(result.errorMessage).toContain('inlineSpecRequestTimeoutPositive')
      })

      it('accepts a positive integer', () => {
        const result = nodeDefault.checkValid(
          buildPayload({
            inline_spec: { ...goodLlamaInline, request_timeout_ms: 60000 },
          }),
          t,
        )
        expect(result.isValid).toBe(true)
      })
    })
  })
})
