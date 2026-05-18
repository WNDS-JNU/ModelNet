import type { FC } from 'react'
import type { TokenModelSourceNodeType } from './types'
import type { NodePanelProps, Var } from '@/app/components/workflow/types'
import { Switch } from '@langgenius/dify-ui/switch'
import * as React from 'react'
import { memo } from 'react'
import { useTranslation } from 'react-i18next'
import Input from '@/app/components/base/input'
import Field from '@/app/components/workflow/nodes/_base/components/field'
import OutputVars, { VarItem } from '@/app/components/workflow/nodes/_base/components/output-vars'
import PromptEditor from '@/app/components/workflow/nodes/_base/components/prompt/editor'
import Split from '@/app/components/workflow/nodes/_base/components/split'
import useAvailableVarList from '@/app/components/workflow/nodes/_base/hooks/use-available-var-list'
import { VarType } from '@/app/components/workflow/types'
import InlineSpecForm from './components/inline-spec-form'
import ModelAliasSelect from './components/model-alias-select'
import SamplingParamsForm from './components/sampling-params-form'
import SourceModeTabs from './components/source-mode-tabs'
import { DEFAULT_INLINE_SPEC } from './types'
import useConfig from './use-config'

const i18nPrefix = 'nodes.tokenModelSource'

const LOGITS_RAW_CAPABILITY = 'logits_raw'

// All ``VarType`` entries the backend ``VariableTemplateParser`` can
// safely stringify into a prompt. ``file`` / ``arrayFile`` are
// deliberately excluded — those are downloaded by the runtime as file
// handles, not interpolated as text. ``any`` / ``arrayAny`` are
// included because schema-loose vars (e.g. tool / plugin output of
// unknown type) can still be ``str()``-ed at render time.
const PROMPT_VAR_TYPES: ReadonlySet<VarType> = new Set([
  VarType.string,
  VarType.number,
  VarType.integer,
  VarType.secret,
  VarType.boolean,
  VarType.object,
  VarType.array,
  VarType.arrayString,
  VarType.arrayNumber,
  VarType.arrayBoolean,
  VarType.arrayObject,
  VarType.any,
  VarType.arrayAny,
])

// ``filterPromptVar`` and ``EMPTY_BLOCK_STATUS`` live at module scope
// so the props ``PromptEditor`` receives have stable identity across
// renders — avoiding the Lexical editor's relatively heavy re-mount
// path on every parent render.
const filterPromptVar = (payload: Var) => PROMPT_VAR_TYPES.has(payload.type)
const EMPTY_BLOCK_STATUS = { context: false, history: false, query: false } as const

const Panel: FC<NodePanelProps<TokenModelSourceNodeType>> = ({
  id,
  data,
}) => {
  const { t } = useTranslation()
  const {
    readOnly,
    inputs,
    models,
    isLoadingModels,
    sourceMode,
    handleModelAliasChange,
    handleSourceModeChange,
    handleInlineSpecChange,
    handlePromptTemplateChange,
    handleRawCompletionChange,
    handleExposeRawLogitsChange,
    handleSamplingParamsChange,
  } = useConfig(id, data)

  const { availableVars, availableNodesWithParent } = useAvailableVarList(id, {
    onlyLeafNodeVar: false,
    filterVar: filterPromptVar,
  })

  const selectedModel = models.find(model => model.id === inputs.model_alias)
  const registeredAliasExposesRawLogits
    = selectedModel?.capabilities.includes(LOGITS_RAW_CAPABILITY) ?? false
  const exposeRawLogitsChecked
    = inputs.expose_raw_logits ?? registeredAliasExposesRawLogits

  return (
    <div className="pt-2">
      <div className="space-y-4 px-4 pb-2">
        {/*
         * Section 1 — Source mode + model identity.
         *
         * The tabs flip between two backend paths described in
         * ``api/core/workflow/nodes/parallel_ensemble/node.py``'s
         * ``_resolve_base_specs``: "registered" picks an alias the
         * deployment already registered in ``model_net.yaml``;
         * "inline" lets the user type the backend fields directly
         * (model_url / EOS / type / …) so the source bypasses the
         * yaml registry. ``model_alias`` stays required in both
         * modes — for registered it's the registry key, for inline
         * it's the synthetic ``id`` the server constructs from the
         * spec block.
         */}
        <SourceModeTabs
          readonly={readOnly}
          value={sourceMode}
          onChange={handleSourceModeChange}
        />

        <Field
          title={t(`${i18nPrefix}.modelAlias`, { ns: 'workflow' })}
          tooltip={
            sourceMode === 'registered'
              ? t(`${i18nPrefix}.modelAliasTooltip`, { ns: 'workflow' })
              : t(`${i18nPrefix}.modelAliasInlineTooltip`, {
                  ns: 'workflow',
                  defaultValue:
                    'A logical name for this source. Used as the synthetic id of the custom spec on the server side; must be non-empty.',
                })
          }
          required
        >
          {sourceMode === 'registered'
            ? (
                <ModelAliasSelect
                  readonly={readOnly}
                  isLoading={isLoadingModels}
                  models={models}
                  selected={inputs.model_alias}
                  onChange={handleModelAliasChange}
                />
              )
            : (
                <Input
                  value={inputs.model_alias}
                  onChange={e => handleModelAliasChange(e.target.value)}
                  disabled={readOnly}
                  placeholder={t(`${i18nPrefix}.modelAliasInlinePlaceholder`, {
                    ns: 'workflow',
                    defaultValue: 'e.g. my-llama-8b',
                  })}
                />
              )}
        </Field>

        {sourceMode === 'registered' && (
          <Field
            title={t(`${i18nPrefix}.exposeRawLogits.label`, { ns: 'workflow' })}
            tooltip={t(`${i18nPrefix}.exposeRawLogits.tooltip`, { ns: 'workflow' })}
            inline
            operations={(
              <Switch
                checked={exposeRawLogitsChecked}
                onCheckedChange={handleExposeRawLogitsChange}
                size="md"
                disabled={readOnly}
                aria-label={t(`${i18nPrefix}.exposeRawLogits.label`, { ns: 'workflow' })}
              />
            )}
          />
        )}

        {sourceMode === 'inline' && (
          <InlineSpecForm
            readonly={readOnly}
            value={inputs.inline_spec ?? DEFAULT_INLINE_SPEC}
            onChange={handleInlineSpecChange}
          />
        )}

        {/* Section 2 — Prompt template.
         *
         * Backend ``TokenModelSourceNode._render_prompt`` resolves
         * ``{{#node.field#}}`` placeholders via ``VariableTemplateParser``;
         * the Lexical-based ``PromptEditor`` writes the same wire format,
         * so the slash trigger / variable picker is purely a UX upgrade
         * over the prior plain ``<textarea>`` — no backend change.
         *
         * LLM-only knobs are intentionally off: token-mode prompts don't
         * speak the chat ``context`` block, jinja2 mode, or the AI
         * prompt-generator (which is wired to ``modelConfig`` from a
         * model picker that this node doesn't have).
         */}
        <PromptEditor
          instanceId={`${id}-token-model-source-prompt-editor`}
          nodeId={id}
          title={t(`${i18nPrefix}.promptTemplate`, { ns: 'workflow' })}
          titleTooltip={t(`${i18nPrefix}.promptTemplateTooltip`, { ns: 'workflow' })}
          value={inputs.prompt_template ?? ''}
          onChange={handlePromptTemplateChange}
          readOnly={readOnly}
          isShowContext={false}
          hasSetBlockStatus={EMPTY_BLOCK_STATUS}
          nodesOutputVars={availableVars}
          availableNodes={availableNodesWithParent}
          placeholder={t(`${i18nPrefix}.promptTemplatePlaceholder`, {
            ns: 'workflow',
            defaultValue: 'Answer: {{#start.q#}}',
          })}
        />

        <Field
          title={t(`${i18nPrefix}.rawCompletion`, { ns: 'workflow' })}
          tooltip={t(`${i18nPrefix}.rawCompletionTooltip`, { ns: 'workflow' })}
          inline
          operations={(
            <Switch
              checked={Boolean(inputs.raw_completion)}
              onCheckedChange={handleRawCompletionChange}
              size="md"
              disabled={readOnly}
              aria-label={t(`${i18nPrefix}.rawCompletion`, { ns: 'workflow' })}
            />
          )}
        />
      </div>

      <Split />

      {/* Section 3 — Sampling params */}
      <div className="space-y-4 px-4 pt-2 pb-2">
        <Field
          title={t(`${i18nPrefix}.sampling.title`, { ns: 'workflow' })}
          tooltip={t(`${i18nPrefix}.sampling.tooltip`, { ns: 'workflow' })}
        >
          <SamplingParamsForm
            readonly={readOnly}
            value={inputs.sampling_params}
            onChange={handleSamplingParamsChange}
          />
        </Field>
      </div>

      <Split />

      <div>
        <OutputVars>
          <>
            {/*
             * Mirrors backend ``TokenModelSourceNode._run`` outputs
             * (api/core/workflow/nodes/token_model_source/node.py):
             * ``spec`` is the ``ModelInvocationSpec`` payload the
             * downstream parallel-ensemble consumes by selector;
             * ``raw_completion`` rides inside that spec to choose raw
             * completion vs chat-template auto-wrap;
             * ``model_alias`` is duplicated at the top level so panels
             * / debug views can show "which model" without unpacking
             * the spec dict.
             */}
            <VarItem
              name="spec"
              type="object"
              description={t(`${i18nPrefix}.outputVars.spec`, { ns: 'workflow' })}
            />
            <VarItem
              name="model_alias"
              type="string"
              description={t(`${i18nPrefix}.outputVars.modelAlias`, { ns: 'workflow' })}
            />
          </>
        </OutputVars>
      </div>
    </div>
  )
}

export default memo(Panel)
