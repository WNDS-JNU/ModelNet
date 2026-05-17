import type { NodeDefault, Var } from '../../types'
import type { DataLoaderNodeType } from './types'
import { BlockClassificationEnum } from '@/app/components/workflow/block-selector/types'
import { BlockEnum, VarType } from '@/app/components/workflow/types'
import { genNodeMetaData } from '@/app/components/workflow/utils'
import { DEFAULT_LOADER_CONFIG } from './types'

const i18nPrefix = 'nodes.dataLoader'

const isPlainObject = (value: unknown): value is Record<string, unknown> =>
  typeof value === 'object' && value !== null && !Array.isArray(value)

const isPositiveInt = (value: unknown, max?: number): value is number =>
  typeof value === 'number'
  && Number.isInteger(value)
  && value > 0
  && (max === undefined || value <= max)

const isNonNegativeInt = (value: unknown): value is number =>
  typeof value === 'number' && Number.isInteger(value) && value >= 0

const metaData = genNodeMetaData({
  author: 'xianghe',
  classification: BlockClassificationEnum.Transform,
  sort: 7,
  type: BlockEnum.DataLoader,
})

const outputVars: Var[] = [
  { variable: 'dataset', type: VarType.string },
  { variable: 'split', type: VarType.string },
  { variable: 'items', type: VarType.arrayObject },
  { variable: 'count', type: VarType.number },
  { variable: 'total', type: VarType.number },
  { variable: 'has_more', type: VarType.boolean },
  { variable: 'next_offset', type: VarType.number },
  { variable: 'questions', type: VarType.arrayString },
  { variable: 'answers', type: VarType.arrayString },
  { variable: 'metadata', type: VarType.object },
]

const nodeDefault: NodeDefault<DataLoaderNodeType> = {
  metaData,
  defaultValue: {
    loader_name: 'inline_json',
    loader_config: { ...DEFAULT_LOADER_CONFIG },
    limit: 100,
    offset: 0,
    shuffle: false,
    seed: null,
  },
  checkValid(payload, t) {
    let errorMessage = ''

    if (typeof payload.loader_name !== 'string' || payload.loader_name.trim().length === 0) {
      errorMessage = t('errorMsg.fieldRequired', {
        ns: 'workflow',
        field: t(`${i18nPrefix}.loaderName`, { ns: 'workflow' }),
      })
    }

    if (!errorMessage && !isPlainObject(payload.loader_config)) {
      errorMessage = t(`${i18nPrefix}.errorMsg.loaderConfigObject`, {
        ns: 'workflow',
      })
    }

    if (!errorMessage && !isPositiveInt(payload.limit, 10000)) {
      errorMessage = t(`${i18nPrefix}.errorMsg.limitPositive`, {
        ns: 'workflow',
      })
    }

    if (!errorMessage && !isNonNegativeInt(payload.offset)) {
      errorMessage = t(`${i18nPrefix}.errorMsg.offsetNonNegative`, {
        ns: 'workflow',
      })
    }

    if (!errorMessage && typeof payload.shuffle !== 'boolean') {
      errorMessage = t(`${i18nPrefix}.errorMsg.shuffleBoolean`, {
        ns: 'workflow',
      })
    }

    if (
      !errorMessage
      && payload.seed !== null
      && payload.seed !== undefined
      && !Number.isInteger(payload.seed)
    ) {
      errorMessage = t(`${i18nPrefix}.errorMsg.seedInteger`, {
        ns: 'workflow',
      })
    }

    return {
      isValid: !errorMessage,
      errorMessage,
    }
  },
  getOutputVars() {
    return outputVars
  },
}

export default nodeDefault
