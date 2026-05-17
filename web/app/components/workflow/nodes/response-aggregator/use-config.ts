import type { ValueSelector, Var } from '../../types'
import type {
  AggregationInputRef,
  ResponseAggregatorNodeType,
} from './types'
import type { FormValue } from '@/app/components/header/account-setting/model-provider-page/declarations'
import { produce } from 'immer'
import {
  useCallback,
  useEffect,
} from 'react'
import {
  ModelTypeEnum,
} from '@/app/components/header/account-setting/model-provider-page/declarations'
import { useModelListAndDefaultModelAndCurrentProviderAndModel } from '@/app/components/header/account-setting/model-provider-page/hooks'
import { useNodesReadOnly } from '@/app/components/workflow/hooks'
import useNodeCrud from '@/app/components/workflow/nodes/_base/hooks/use-node-crud'
import { AppModeEnum } from '@/types/app'
import { VarType } from '../../types'

// Upstream text comes through graphon's `segment.text`, which renders
// strings, numbers, objects, and arrays into text. Files are excluded —
// aggregating binary references has no defined semantics for this node.
const TEXT_COMPATIBLE_VAR_TYPES: VarType[] = [
  VarType.string,
  VarType.number,
  VarType.boolean,
  VarType.object,
  VarType.array,
  VarType.arrayString,
  VarType.arrayNumber,
  VarType.arrayBoolean,
  VarType.arrayObject,
  VarType.any,
]

// Weight var-reference picker accepts the numeric-shaped types only —
// string / object / array would either need coercion (silent drift) or
// break the backend's finite-number guard. Match backend
// ``_resolve_weight`` which expects ``int | float`` from the var pool.
const NUMERIC_VAR_TYPES: VarType[] = [
  VarType.number,
  VarType.any,
]

const defaultAggregationModel = () => ({
  provider: '',
  name: '',
  mode: AppModeEnum.CHAT,
  completion_params: {
    temperature: 0.2,
  },
})

const useConfig = (id: string, payload: ResponseAggregatorNodeType) => {
  const { nodesReadOnly: readOnly } = useNodesReadOnly()
  const { inputs, setInputs } = useNodeCrud<ResponseAggregatorNodeType>(id, payload)
  const {
    currentProvider,
    currentModel,
  } = useModelListAndDefaultModelAndCurrentProviderAndModel(ModelTypeEnum.textGeneration)

  useEffect(() => {
    if (
      !inputs.model?.provider
      && currentProvider?.provider
      && currentModel?.model
    ) {
      const next = produce(inputs, (draft) => {
        draft.model = {
          provider: currentProvider.provider,
          name: currentModel.model,
          mode: (currentModel.model_properties?.mode as string | undefined) || AppModeEnum.CHAT,
          completion_params: draft.model?.completion_params ?? { temperature: 0.2 },
        }
      })
      setInputs(next)
    }
  }, [currentModel, currentProvider, inputs, setInputs])

  const filterStringVar = useCallback((varPayload: Var) => {
    return TEXT_COMPATIBLE_VAR_TYPES.includes(varPayload.type)
  }, [])

  const filterNumericVar = useCallback((varPayload: Var) => {
    return NUMERIC_VAR_TYPES.includes(varPayload.type)
  }, [])

  const nextDefaultSourceId = useCallback((refs: AggregationInputRef[]) => {
    // Stable alias naming: `model_1`, `model_2`, … — user is expected to
    // rename, but the default must never collide with an existing entry
    // because the backend rejects duplicate source_id values.
    const existing = new Set(refs.map(r => r.source_id))
    let i = refs.length + 1
    while (existing.has(`model_${i}`))
      i += 1
    return `model_${i}`
  }, [])

  const handleAddInput = useCallback(() => {
    const next = produce(inputs, (draft) => {
      draft.inputs.push({
        source_id: nextDefaultSourceId(draft.inputs),
        variable_selector: [],
        weight: 1,
        fallback_weight: null,
        extra: {},
      })
    })
    setInputs(next)
  }, [inputs, setInputs, nextDefaultSourceId])

  const handleRemoveInput = useCallback((index: number) => {
    const next = produce(inputs, (draft) => {
      draft.inputs.splice(index, 1)
    })
    setInputs(next)
  }, [inputs, setInputs])

  const handleSourceIdChange = useCallback((index: number, value: string) => {
    const next = produce(inputs, (draft) => {
      if (draft.inputs[index])
        draft.inputs[index].source_id = value
    })
    setInputs(next)
  }, [inputs, setInputs])

  const handleVariableSelectorChange = useCallback(
    (index: number, selector: ValueSelector) => {
      const next = produce(inputs, (draft) => {
        if (draft.inputs[index])
          draft.inputs[index].variable_selector = selector
      })
      setInputs(next)
    },
    [inputs, setInputs],
  )

  const handleWeightChange = useCallback(
    (index: number, value: number | ValueSelector) => {
      const next = produce(inputs, (draft) => {
        if (draft.inputs[index])
          draft.inputs[index].weight = value
      })
      setInputs(next)
    },
    [inputs, setInputs],
  )

  const handleFallbackWeightChange = useCallback(
    (index: number, value: number | null) => {
      const next = produce(inputs, (draft) => {
        if (draft.inputs[index])
          draft.inputs[index].fallback_weight = value
      })
      setInputs(next)
    },
    [inputs, setInputs],
  )

  const handleInstructionChange = useCallback((value: string) => {
    const next = produce(inputs, (draft) => {
      draft.instruction = value
    })
    setInputs(next)
  }, [inputs, setInputs])

  const handleCompletionParamsChange = useCallback((newParams: FormValue) => {
    const next = produce(inputs, (draft) => {
      const current = draft.model ?? defaultAggregationModel()
      draft.model = {
        ...current,
        completion_params: newParams,
      }
    })
    setInputs(next)
  }, [inputs, setInputs])

  const handleModelAndCompletionParamsChange = useCallback(
    (
      model: { provider: string, modelId: string, mode?: string },
      completionParams: FormValue,
    ) => {
      // Single ``produce`` over the latest ``inputs`` closure — avoids the
      // sequenced ``setInputs(params)`` then ``setInputs(model)`` pattern,
      // where both updaters reuse the same stale snapshot and the second
      // write clobbers the first.
      const next = produce(inputs, (draft) => {
        const current = draft.model ?? defaultAggregationModel()
        draft.model = {
          ...current,
          provider: model.provider,
          name: model.modelId,
          mode: model.mode || AppModeEnum.CHAT,
          completion_params: completionParams,
        }
      })
      setInputs(next)
    },
    [inputs, setInputs],
  )

  return {
    readOnly,
    inputs,
    filterStringVar,
    filterNumericVar,
    handleAddInput,
    handleRemoveInput,
    handleSourceIdChange,
    handleVariableSelectorChange,
    handleWeightChange,
    handleFallbackWeightChange,
    handleInstructionChange,
    handleCompletionParamsChange,
    handleModelAndCompletionParamsChange,
  }
}

export default useConfig
