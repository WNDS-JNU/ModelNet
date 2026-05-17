import type { DataLoaderNodeType } from './types'
import { produce } from 'immer'
import { useCallback, useMemo, useState } from 'react'
import { useNodesReadOnly } from '@/app/components/workflow/hooks'
import useNodeCrud from '@/app/components/workflow/nodes/_base/hooks/use-node-crud'

const formatConfig = (config: Record<string, unknown>) => JSON.stringify(config ?? {}, null, 2)

const useConfig = (id: string, payload: DataLoaderNodeType) => {
  const { nodesReadOnly: readOnly } = useNodesReadOnly()
  const { inputs, setInputs } = useNodeCrud<DataLoaderNodeType>(id, payload)
  const [configText, setConfigText] = useState(() => formatConfig(inputs.loader_config))
  const [configError, setConfigError] = useState<string | null>(null)

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
    handleLoaderNameChange,
    handleConfigTextChange,
    handleNumberChange,
    handleShuffleChange,
  }), [
    readOnly,
    inputs,
    configText,
    configError,
    handleLoaderNameChange,
    handleConfigTextChange,
    handleNumberChange,
    handleShuffleChange,
  ])
}

export default useConfig
