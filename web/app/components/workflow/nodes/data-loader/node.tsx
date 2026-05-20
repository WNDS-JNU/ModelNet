import type { FC } from 'react'
import type { DataLoaderNodeType } from './types'
import type { NodeProps } from '@/app/components/workflow/types'
import * as React from 'react'
import { useTranslation } from 'react-i18next'
import { DataLoaderSourceMode } from './types'

const i18nPrefix = 'nodes.dataLoader'

const Node: FC<NodeProps<DataLoaderNodeType>> = ({ data }) => {
  const { t } = useTranslation()
  const sourceMode = data.source_mode ?? DataLoaderSourceMode.configured
  const loaderName = sourceMode === DataLoaderSourceMode.uploadedCode
    ? t(`${i18nPrefix}.sourceModeUploadedCode`, { ns: 'workflow' })
    : data.loader_name

  if (!loaderName)
    return null

  return (
    <div className="mb-1 px-3 py-1">
      <div className="flex items-center justify-between rounded-md bg-workflow-block-parma-bg px-2 py-1">
        <span className="truncate system-xs-medium text-text-secondary">
          {loaderName}
        </span>
        <span className="ml-2 shrink-0 system-xs-regular text-text-tertiary">
          {t(`${i18nPrefix}.limitChip`, { ns: 'workflow', count: data.limit ?? 0 })}
        </span>
      </div>
    </div>
  )
}

export default React.memo(Node)
