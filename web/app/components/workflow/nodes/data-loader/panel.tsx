import type { FC } from 'react'
import type { DataLoaderNodeType } from './types'
import type { NodePanelProps } from '@/app/components/workflow/types'
import { Switch } from '@langgenius/dify-ui/switch'
import * as React from 'react'
import { memo } from 'react'
import { useTranslation } from 'react-i18next'
import Input from '@/app/components/base/input'
import Textarea from '@/app/components/base/textarea'
import Field from '@/app/components/workflow/nodes/_base/components/field'
import OutputVars, { VarItem } from '@/app/components/workflow/nodes/_base/components/output-vars'
import TypeSelector from '@/app/components/workflow/nodes/_base/components/selector'
import Split from '@/app/components/workflow/nodes/_base/components/split'
import VarReferencePicker from '@/app/components/workflow/nodes/_base/components/variable/var-reference-picker'
import { DataLoaderSourceMode } from './types'
import useConfig from './use-config'

const i18nPrefix = 'nodes.dataLoader'

const Panel: FC<NodePanelProps<DataLoaderNodeType>> = ({
  id,
  data,
}) => {
  const { t } = useTranslation()
  const {
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
  } = useConfig(id, data)
  const sourceMode = inputs.source_mode ?? DataLoaderSourceMode.configured
  const sourceModeOptions = [
    {
      label: t(`${i18nPrefix}.sourceModeConfigured`, { ns: 'workflow' }),
      value: DataLoaderSourceMode.configured,
    },
    {
      label: t(`${i18nPrefix}.sourceModeUploadedCode`, { ns: 'workflow' }),
      value: DataLoaderSourceMode.uploadedCode,
    },
  ]

  const configErrorText = configError === 'json'
    ? t(`${i18nPrefix}.errorMsg.loaderConfigJson`, { ns: 'workflow' })
    : configError === 'object'
      ? t(`${i18nPrefix}.errorMsg.loaderConfigObject`, { ns: 'workflow' })
      : ''

  return (
    <div className="pt-2">
      <div className="space-y-4 px-4 pb-2">
        <Field
          title={t(`${i18nPrefix}.sourceModeTitle`, { ns: 'workflow' })}
          tooltip={t(`${i18nPrefix}.sourceModeTooltip`, { ns: 'workflow' })}
          required
        >
          <TypeSelector
            options={sourceModeOptions}
            value={sourceMode}
            onChange={value => handleSourceModeChange(value as DataLoaderSourceMode)}
          />
        </Field>

        {sourceMode === DataLoaderSourceMode.configured && (
          <>
            <Field
              title={t(`${i18nPrefix}.loaderName`, { ns: 'workflow' })}
              tooltip={t(`${i18nPrefix}.loaderNameTooltip`, { ns: 'workflow' })}
              required
            >
              <Input
                value={inputs.loader_name}
                onChange={e => handleLoaderNameChange(e.target.value)}
                disabled={readOnly}
                placeholder={t(`${i18nPrefix}.loaderNamePlaceholder`, { ns: 'workflow' })}
              />
            </Field>

            <Field
              title={t(`${i18nPrefix}.loaderConfig`, { ns: 'workflow' })}
              tooltip={t(`${i18nPrefix}.loaderConfigTooltip`, { ns: 'workflow' })}
              required
            >
              <div>
                <Textarea
                  value={configText}
                  onChange={e => handleConfigTextChange(e.target.value)}
                  disabled={readOnly}
                  rows={10}
                  destructive={!!configError}
                  className="font-mono text-xs"
                />
                {!!configErrorText && (
                  <div className="mt-1 system-xs-regular text-text-destructive">
                    {configErrorText}
                  </div>
                )}
              </div>
            </Field>
          </>
        )}

        {sourceMode === DataLoaderSourceMode.uploadedCode && (
          <>
            <Field
              title={t(`${i18nPrefix}.dataFile`, { ns: 'workflow' })}
              tooltip={t(`${i18nPrefix}.dataFileTooltip`, { ns: 'workflow' })}
              required
            >
              <VarReferencePicker
                readonly={readOnly}
                nodeId={id}
                isShowNodeName
                value={inputs.data_file_selector || []}
                onChange={value => handleFileSelectorChange('data_file_selector', value)}
                filterVar={filterFileVar}
                typePlaceHolder="File | Array[File]"
              />
            </Field>

            <Field
              title={t(`${i18nPrefix}.codeFile`, { ns: 'workflow' })}
              tooltip={t(`${i18nPrefix}.codeFileTooltip`, { ns: 'workflow' })}
              required
            >
              <VarReferencePicker
                readonly={readOnly}
                nodeId={id}
                isShowNodeName
                value={inputs.code_file_selector || []}
                onChange={value => handleFileSelectorChange('code_file_selector', value)}
                filterVar={filterFileVar}
                typePlaceHolder="File | Array[File]"
              />
            </Field>
          </>
        )}

        <div className="grid grid-cols-2 gap-3">
          <Field
            title={t(`${i18nPrefix}.limit`, { ns: 'workflow' })}
            tooltip={t(`${i18nPrefix}.limitTooltip`, { ns: 'workflow' })}
            required
          >
            <Input
              type="number"
              min={1}
              max={10000}
              value={inputs.limit}
              onChange={e => handleNumberChange('limit', e.target.value)}
              disabled={readOnly}
            />
          </Field>
          <Field
            title={t(`${i18nPrefix}.offset`, { ns: 'workflow' })}
            tooltip={t(`${i18nPrefix}.offsetTooltip`, { ns: 'workflow' })}
            required
          >
            <Input
              type="number"
              min={0}
              value={inputs.offset}
              onChange={e => handleNumberChange('offset', e.target.value)}
              disabled={readOnly}
            />
          </Field>
        </div>

        <div className="grid grid-cols-2 gap-3">
          <Field
            title={t(`${i18nPrefix}.shuffle`, { ns: 'workflow' })}
            tooltip={t(`${i18nPrefix}.shuffleTooltip`, { ns: 'workflow' })}
            inline
            operations={(
              <Switch
                checked={inputs.shuffle}
                onCheckedChange={handleShuffleChange}
                size="md"
                disabled={readOnly}
              />
            )}
          />
          <Field
            title={t(`${i18nPrefix}.seed`, { ns: 'workflow' })}
            tooltip={t(`${i18nPrefix}.seedTooltip`, { ns: 'workflow' })}
          >
            <Input
              type="number"
              value={inputs.seed ?? ''}
              onChange={e => handleNumberChange('seed', e.target.value)}
              disabled={readOnly}
              placeholder={t(`${i18nPrefix}.seedPlaceholder`, { ns: 'workflow' })}
            />
          </Field>
        </div>
      </div>

      <Split />

      <div>
        <OutputVars>
          <>
            <VarItem name="dataset" type="string" description={t(`${i18nPrefix}.outputVars.dataset`, { ns: 'workflow' })} />
            <VarItem name="split" type="string" description={t(`${i18nPrefix}.outputVars.split`, { ns: 'workflow' })} />
            <VarItem name="items" type="array[object]" description={t(`${i18nPrefix}.outputVars.items`, { ns: 'workflow' })} />
            <VarItem name="count" type="number" description={t(`${i18nPrefix}.outputVars.count`, { ns: 'workflow' })} />
            <VarItem name="total" type="number" description={t(`${i18nPrefix}.outputVars.total`, { ns: 'workflow' })} />
            <VarItem name="has_more" type="boolean" description={t(`${i18nPrefix}.outputVars.hasMore`, { ns: 'workflow' })} />
            <VarItem name="next_offset" type="number" description={t(`${i18nPrefix}.outputVars.nextOffset`, { ns: 'workflow' })} />
            <VarItem name="questions" type="array[string]" description={t(`${i18nPrefix}.outputVars.questions`, { ns: 'workflow' })} />
            <VarItem name="answers" type="array[string]" description={t(`${i18nPrefix}.outputVars.answers`, { ns: 'workflow' })} />
            <VarItem name="metadata" type="object" description={t(`${i18nPrefix}.outputVars.metadata`, { ns: 'workflow' })} />
          </>
        </OutputVars>
      </div>
    </div>
  )
}

export default memo(Panel)
