import type { FC } from 'react'
import type { ResponseAggregatorNodeType } from './types'
import type { NodePanelProps } from '@/app/components/workflow/types'
import { toast } from '@langgenius/dify-ui/toast'
import * as React from 'react'
import {
  memo,
  useCallback,
} from 'react'
import { useTranslation } from 'react-i18next'
import Textarea from '@/app/components/base/textarea'
import ModelParameterModal from '@/app/components/header/account-setting/model-provider-page/model-parameter-modal'
import Field from '@/app/components/workflow/nodes/_base/components/field'
import OutputVars, { VarItem } from '@/app/components/workflow/nodes/_base/components/output-vars'
import Split from '@/app/components/workflow/nodes/_base/components/split'
import { fetchAndMergeValidCompletionParams } from '@/utils/completion-params'
import InputList from './components/input-list'
import useConfig from './use-config'

const i18nPrefix = 'nodes.responseAggregator'

const Panel: FC<NodePanelProps<ResponseAggregatorNodeType>> = ({
  id,
  data,
}) => {
  const { t } = useTranslation()

  const {
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
  } = useConfig(id, data)

  const model = inputs.model ?? {
    provider: '',
    name: '',
    mode: 'chat',
    completion_params: { temperature: 0.2 },
  }
  const handleModelChange = useCallback((model: {
    provider: string
    modelId: string
    mode?: string
  }) => {
    (async () => {
      let nextParams: Record<string, unknown> = {}
      try {
        const { params: filtered, removedDetails } = await fetchAndMergeValidCompletionParams(
          model.provider,
          model.modelId,
          inputs.model?.completion_params ?? {},
          true,
        )
        const keys = Object.keys(removedDetails)
        if (keys.length)
          toast.warning(`${t('modelProvider.parametersInvalidRemoved', { ns: 'common' })}: ${keys.map(k => `${k} (${removedDetails[k]})`).join(', ')}`)
        nextParams = filtered
      }
      catch {
        toast.error(t('error', { ns: 'common' }))
      }
      // Single mutation — atomic provider/name/mode/completion_params
      // swap. Splitting into two ``setInputs`` calls would race because
      // each ``produce`` reads the same stale ``inputs`` closure.
      handleModelAndCompletionParamsChange(model, nextParams)
    })()
  }, [handleModelAndCompletionParamsChange, inputs.model?.completion_params, t])

  const handleInstructionInput = useCallback(
    (e: React.ChangeEvent<HTMLTextAreaElement>) => {
      handleInstructionChange(e.target.value)
    },
    [handleInstructionChange],
  )

  return (
    <div className="pt-2">
      <div className="space-y-4 px-4 pb-2">
        <Field
          title={t(`${i18nPrefix}.inputs`, { ns: 'workflow' })}
          tooltip={t(`${i18nPrefix}.inputsTooltip`, { ns: 'workflow' })}
          required
        >
          <InputList
            nodeId={id}
            readonly={readOnly}
            list={inputs.inputs}
            onAdd={handleAddInput}
            onRemove={handleRemoveInput}
            onSourceIdChange={handleSourceIdChange}
            onVariableSelectorChange={handleVariableSelectorChange}
            onWeightChange={handleWeightChange}
            onFallbackWeightChange={handleFallbackWeightChange}
            filterVar={filterStringVar}
            filterNumericVar={filterNumericVar}
          />
        </Field>

        <Field
          title={t(`${i18nPrefix}.model`, { ns: 'workflow' })}
          tooltip={t(`${i18nPrefix}.modelTooltip`, { ns: 'workflow' })}
          required
        >
          <ModelParameterModal
            popupClassName="w-[387px]!"
            isInWorkflow
            isAdvancedMode={true}
            provider={model.provider}
            completionParams={model.completion_params}
            modelId={model.name}
            setModel={handleModelChange}
            onCompletionParamsChange={handleCompletionParamsChange}
            hideDebugWithMultipleModel
            debugWithMultipleModel={false}
            readonly={readOnly}
          />
        </Field>

        <Field
          title={t(`${i18nPrefix}.instruction`, { ns: 'workflow' })}
          tooltip={t(`${i18nPrefix}.instructionTooltip`, { ns: 'workflow' })}
        >
          <Textarea
            value={inputs.instruction ?? ''}
            onChange={handleInstructionInput}
            placeholder={t(`${i18nPrefix}.instructionPlaceholder`, { ns: 'workflow' })!}
            disabled={readOnly}
            rows={4}
          />
        </Field>
      </div>

      <Split />

      <div>
        <OutputVars>
          <>
            <VarItem
              name="text"
              type="string"
              description={t(`${i18nPrefix}.outputVars.text`, { ns: 'workflow' })}
            />
            <VarItem
              name="metadata"
              type="object"
              description={t(`${i18nPrefix}.outputVars.metadata`, { ns: 'workflow' })}
            />
          </>
        </OutputVars>
      </div>
    </div>
  )
}

export default memo(Panel)
