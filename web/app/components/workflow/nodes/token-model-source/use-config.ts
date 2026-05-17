import type { InlineModelSpec, SamplingParams, TokenModelSourceNodeType } from './types'
import { produce } from 'immer'
import { useCallback, useMemo } from 'react'
import { useNodesReadOnly } from '@/app/components/workflow/hooks'
import useNodeCrud from '@/app/components/workflow/nodes/_base/hooks/use-node-crud'
// ``useLocalModels`` already lives under ``parallel-ensemble`` (P2.11) —
// importing it here keeps the wire contract single-sourced. Both nodes
// hit ``GET /workspaces/current/local-models`` and de-dupe via the
// react-query staleTime; pulling it out into a shared hooks module
// would be a premature abstraction with only two consumers.
import { useLocalModels } from '../parallel-ensemble/use-registries'
import { DEFAULT_INLINE_SPEC, DEFAULT_SAMPLING_PARAMS } from './types'

// Two source modes the panel surfaces. ``registered`` matches the
// original P3.B.1 behaviour (alias resolved against
// ``model_net.yaml``); ``inline`` lets the user type the backend
// fields directly so the source bypasses the yaml registry — useful
// for ad-hoc endpoints that should not live in a shared config file.
export type SourceMode = 'registered' | 'inline'

const useConfig = (id: string, payload: TokenModelSourceNodeType) => {
  const { nodesReadOnly: readOnly } = useNodesReadOnly()
  const { inputs, setInputs } = useNodeCrud<TokenModelSourceNodeType>(id, payload)

  const localModelsQuery = useLocalModels()
  const models = useMemo(
    () => localModelsQuery.data?.models ?? [],
    [localModelsQuery.data],
  )

  // ``inline_spec`` being non-null is the authoritative discriminator
  // for "panel is in inline mode". A previously-saved DSL with
  // ``inline_spec: null`` lands in registered mode automatically,
  // matching the pre-change behaviour.
  const sourceMode: SourceMode = inputs.inline_spec ? 'inline' : 'registered'

  // ── Mutation handlers ───────────────────────────────────────────

  const handleModelAliasChange = useCallback(
    (alias: string) => {
      const next = produce(inputs, (draft) => {
        draft.model_alias = alias
      })
      setInputs(next)
    },
    [inputs, setInputs],
  )

  const handleSourceModeChange = useCallback(
    (mode: SourceMode) => {
      const next = produce(inputs, (draft) => {
        if (mode === 'inline') {
          // Seed with a fresh inline-spec block; preserve the user's
          // ``model_alias`` so they don't have to retype it when
          // switching modes (it doubles as the inline spec's ``id``
          // on the backend side).
          draft.inline_spec = { ...DEFAULT_INLINE_SPEC }
        }
        else {
          // ``null`` is the canonical "registered mode" sentinel —
          // matches the saved-DSL shape pydantic round-trips to.
          draft.inline_spec = null
        }
      })
      setInputs(next)
    },
    [inputs, setInputs],
  )

  const handleInlineSpecChange = useCallback(
    (patch: Partial<InlineModelSpec>) => {
      const next = produce(inputs, (draft) => {
        const current: InlineModelSpec
          = (draft.inline_spec ?? DEFAULT_INLINE_SPEC) as InlineModelSpec
        if (typeof patch.model_name === 'string') {
          const nextModelName = patch.model_name.trim()
          const currentModelName = current.model_name.trim()
          const currentAlias = draft.model_alias.trim()
          if (nextModelName && (currentAlias.length === 0 || currentAlias === currentModelName))
            draft.model_alias = nextModelName
        }
        draft.inline_spec = {
          ...current,
          ...patch,
        } as InlineModelSpec
      })
      setInputs(next)
    },
    [inputs, setInputs],
  )

  const handlePromptTemplateChange = useCallback(
    (template: string) => {
      const next = produce(inputs, (draft) => {
        draft.prompt_template = template
      })
      setInputs(next)
    },
    [inputs, setInputs],
  )

  const handleSamplingParamsChange = useCallback(
    (patch: Partial<SamplingParams>) => {
      const next = produce(inputs, (draft) => {
        draft.sampling_params = {
          // ``DEFAULT_SAMPLING_PARAMS`` first so a DSL that landed
          // without a ``sampling_params`` block (legacy / hand-edited)
          // still gets the canonical floor; ``draft.sampling_params``
          // second so user-set fields override; ``patch`` last for the
          // current edit.
          ...DEFAULT_SAMPLING_PARAMS,
          ...draft.sampling_params,
          ...patch,
        }
      })
      setInputs(next)
    },
    [inputs, setInputs],
  )

  const handleExtraChange = useCallback(
    (extra: Record<string, unknown>) => {
      const next = produce(inputs, (draft) => {
        draft.extra = extra
      })
      setInputs(next)
    },
    [inputs, setInputs],
  )

  return {
    readOnly,
    inputs,
    models,
    isLoadingModels: localModelsQuery.isLoading,
    sourceMode,
    handleModelAliasChange,
    handleSourceModeChange,
    handleInlineSpecChange,
    handlePromptTemplateChange,
    handleSamplingParamsChange,
    handleExtraChange,
  }
}

export default useConfig
