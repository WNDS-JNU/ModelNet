import type { CommonNodeType, ValueSelector } from '@/app/components/workflow/types'

export const DATA_LOADER_NODE_TYPE = 'data-loader' as const

export const DataLoaderSourceMode = {
  configured: 'configured',
  uploadedCode: 'uploaded_code',
} as const

export type DataLoaderSourceMode = typeof DataLoaderSourceMode[keyof typeof DataLoaderSourceMode]

export const DataLoaderCodeLanguage = {
  python3: 'python3',
} as const

export type DataLoaderCodeLanguage = typeof DataLoaderCodeLanguage[keyof typeof DataLoaderCodeLanguage]

export type DataLoaderNodeType = CommonNodeType & {
  source_mode?: DataLoaderSourceMode
  loader_name: string
  loader_config: Record<string, unknown>
  data_file_selector?: ValueSelector
  code_file_selector?: ValueSelector
  code_language?: DataLoaderCodeLanguage
  limit: number
  offset: number
  shuffle: boolean
  seed: number | null
}

export const DEFAULT_LOADER_CONFIG: Record<string, unknown> = {
  dataset_name: 'inline_json',
  split: 'custom',
  items: [],
}
