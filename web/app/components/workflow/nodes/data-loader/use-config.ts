import type { ValueSelector, Var } from '../../types'
import type { DataLoaderNodeType, DataLoaderSourceMode } from './types'
import { produce } from 'immer'
import { useCallback, useMemo, useState } from 'react'
import { useNodesReadOnly } from '@/app/components/workflow/hooks'
import useNodeCrud from '@/app/components/workflow/nodes/_base/hooks/use-node-crud'
import { VarType } from '../../types'

const formatConfig = (config: Record<string, unknown>) => JSON.stringify(config ?? {}, null, 2)

const useConfig = (id: string, payload: DataLoaderNodeType) => {
  const { nodesReadOnly: readOnly } = useNodesReadOnly()
  const { inputs, setInputs } = useNodeCrud<DataLoaderNodeType>(id, payload)
  const [configText, setConfigText] = useState(() => formatConfig(inputs.loader_config))
  const [configError, setConfigError] = useState<string | null>(null)

  const filterFileVar = useCallback((varPayload: Var) => {
    return varPayload.type === VarType.file || varPayload.type === VarType.arrayFile
  }, [])

  const handleSourceModeChange = useCallback((sourceMode: DataLoaderSourceMode) => {
    const next = produce(inputs, (draft) => {
      draft.source_mode = sourceMode
    })
    setInputs(next)
  }, [inputs, setInputs])

  const handleLoaderNameChange = useCallback((loaderName: string) => {
    const next = produce(inputs, (draft) => {
      draft.loader_name = loaderName
    })
    setInputs(next)
  }, [inputs, setInputs])

  const handleConfigTextChange = useCallback((text: string) => {
    setConfigText(text)
    try {
      const parsed = JSON.parse(text) as unknown
      if (typeof parsed !== 'object' || parsed === null || Array.isArray(parsed)) {
        setConfigError('object')
        return
      }
      setConfigError(null)
      const next = produce(inputs, (draft) => {
        draft.loader_config = parsed as Record<string, unknown>
      })
      setInputs(next)
    }
    catch {
      setConfigError('json')
    }
  }, [inputs, setInputs])

  const handleNumberChange = useCallback((field: 'limit' | 'offset' | 'seed', raw: string) => {
    const next = produce(inputs, (draft) => {
      if (field === 'seed') {
        draft.seed = raw === '' ? null : Number(raw)
      }
      else {
        draft[field] = raw === '' ? 0 : Number(raw)
      }
    })
    setInputs(next)
  }, [inputs, setInputs])

  const handleFileSelectorChange = useCallback((field: 'data_file_selector' | 'code_file_selector', variable: ValueSelector | string) => {
    const next = produce(inputs, (draft) => {
      draft[field] = variable as ValueSelector
    })
    setInputs(next)
  }, [inputs, setInputs])

  const handleShuffleChange = useCallback((checked: boolean) => {
    const next = produce(inputs, (draft) => {
      draft.shuffle = checked
    })
    setInputs(next)
  }, [inputs, setInputs])

  return useMemo(() => ({
    readOnly,
    inputs,
    configText,
    configError,
    filterFileVar,
    handleSourceModeChange,
    handleLoaderNameChange,
    handleConfigTextChange,
    handleNumberChange,
    handleFileSelectorChange,
    handleShuffleChange,
  }), [
    readOnly,
    inputs,
    configText,
    configError,
    filterFileVar,
    handleSourceModeChange,
    handleLoaderNameChange,
    handleConfigTextChange,
    handleNumberChange,
    handleFileSelectorChange,
    handleShuffleChange,
  ])
}

export default useConfig
