import type { CommonNodeType } from '@/app/components/workflow/types'

export const DATA_LOADER_NODE_TYPE = 'data-loader' as const

export type DataLoaderNodeType = CommonNodeType & {
  loader_name: string
  loader_config: Record<string, unknown>
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
