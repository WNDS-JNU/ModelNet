import type { NodeDefault } from '../../types'
import type { ResponseAggregatorNodeType } from './types'
import { BlockClassificationEnum } from '@/app/components/workflow/block-selector/types'
import { BlockEnum } from '@/app/components/workflow/types'
import { genNodeMetaData } from '@/app/components/workflow/utils'
import { AppModeEnum } from '@/types/app'

const i18nPrefix = 'nodes.responseAggregator'

const metaData = genNodeMetaData({
  author: 'xianghe',
  classification: BlockClassificationEnum.ModelCollaboration,
  sort: 1,
  type: BlockEnum.ResponseAggregator,
})

const isFiniteNumber = (v: unknown): v is number =>
  typeof v === 'number' && Number.isFinite(v) && typeof v !== 'boolean'

const isVariableSelectorShape = (v: unknown): v is string[] => {
  if (!Array.isArray(v))
    return false
  if (v.length < 2)
    return false
  return v.every(seg => typeof seg === 'string' && seg.trim().length > 0)
}

const nodeDefault: NodeDefault<ResponseAggregatorNodeType> = {
  metaData,
  defaultValue: {
    inputs: [],
    instruction: '',
    model: {
      provider: '',
      name: '',
      mode: AppModeEnum.CHAT,
      completion_params: {
        temperature: 0.2,
      },
    },
  },
  checkValid(payload: ResponseAggregatorNodeType, t: (key: string, options?: Record<string, unknown>) => string) {
    const { inputs, model, instruction } = payload
    let errorMessages = ''

    if (!inputs || inputs.length < 2) {
      errorMessages = t('errorMsg.fieldRequired', {
        ns: 'workflow',
        field: t(`${i18nPrefix}.inputs`, { ns: 'workflow' }),
      })
    }

    if (!errorMessages && inputs) {
      const seenSourceIds = new Set<string>()
      for (const ref of inputs) {
        const sid = (ref.source_id || '').trim()
        if (!sid) {
          errorMessages = t('errorMsg.fieldRequired', {
            ns: 'workflow',
            field: t(`${i18nPrefix}.sourceId`, { ns: 'workflow' }),
          })
          break
        }
        if (seenSourceIds.has(sid)) {
          errorMessages = t(`${i18nPrefix}.errorMsg.duplicateSourceId`, {
            ns: 'workflow',
            sourceId: sid,
          })
          break
        }
        seenSourceIds.add(sid)
        if (!ref.variable_selector || ref.variable_selector.length < 2) {
          errorMessages = t('errorMsg.fieldRequired', {
            ns: 'workflow',
            field: t(`${i18nPrefix}.variableSelector`, { ns: 'workflow' }),
          })
          break
        }

        // Weight: static finite number OR ``VariableSelector``-shaped
        // ``list[str]`` (≥2 segments, all non-blank). ``undefined`` is the
        // legacy-DSL path; backend pydantic fills the default ``1.0``.
        const w: unknown = ref.weight
        const weightOk
          = w === undefined || isFiniteNumber(w) || isVariableSelectorShape(w)
        if (!weightOk) {
          errorMessages = t(`${i18nPrefix}.errorMsg.weightInvalid`, {
            ns: 'workflow',
            sourceId: sid,
          })
          break
        }

        const fb = ref.fallback_weight
        if (fb !== null && fb !== undefined && !isFiniteNumber(fb)) {
          errorMessages = t(`${i18nPrefix}.errorMsg.fallbackWeightInvalid`, {
            ns: 'workflow',
            sourceId: sid,
          })
          break
        }

        if (ref.extra !== undefined && (typeof ref.extra !== 'object' || ref.extra === null || Array.isArray(ref.extra))) {
          errorMessages = t(`${i18nPrefix}.errorMsg.extraMustBeObject`, {
            ns: 'workflow',
            sourceId: sid,
          })
          break
        }
      }
    }

    if (!errorMessages && (!model?.provider || !model?.name)) {
      errorMessages = t('errorMsg.fieldRequired', {
        ns: 'workflow',
        field: t(`${i18nPrefix}.model`, { ns: 'workflow' }),
      })
    }

    if (!errorMessages && instruction !== undefined && typeof instruction !== 'string') {
      errorMessages = t(`${i18nPrefix}.errorMsg.instructionMustBeString`, {
        ns: 'workflow',
      })
    }

    return {
      isValid: !errorMessages,
      errorMessage: errorMessages,
    }
  },
}

export default nodeDefault
