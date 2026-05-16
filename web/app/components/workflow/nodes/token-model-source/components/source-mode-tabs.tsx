'use client'
import type { FC } from 'react'
import type { SourceMode } from '../use-config'
import { cn } from '@langgenius/dify-ui/cn'
import * as React from 'react'
import { useTranslation } from 'react-i18next'

const i18nPrefix = 'nodes.tokenModelSource.sourceMode'

type Props = {
  readonly: boolean
  value: SourceMode
  onChange: (mode: SourceMode) => void
}

// Two-tab switcher between "Registered alias" and "Custom inline".
// Implemented inline rather than via the shared ``Tabs`` primitive
// because the panel only needs a binary toggle with i18n strings —
// pulling in ``Tabs`` would bring an entire content-host abstraction
// the panel does not consume.
const SourceModeTabs: FC<Props> = ({ readonly, value, onChange }) => {
  const { t } = useTranslation()
  const tabs: { id: SourceMode, labelKey: string }[] = [
    { id: 'registered', labelKey: `${i18nPrefix}.registered` },
    { id: 'inline', labelKey: `${i18nPrefix}.inline` },
  ]
  return (
    <div className="flex gap-1 rounded-lg bg-components-segmented-control-bg-normal p-0.5">
      {tabs.map((tab) => {
        const active = tab.id === value
        return (
          <button
            key={tab.id}
            type="button"
            disabled={readonly}
            className={cn(
              'flex-1 rounded-md px-3 py-1 system-sm-medium transition-colors',
              active
                ? 'bg-components-segmented-control-item-active-bg text-text-accent shadow-xs'
                : 'text-text-tertiary',
              readonly ? 'cursor-not-allowed opacity-60' : 'cursor-pointer hover:text-text-secondary',
            )}
            onClick={() => {
              if (tab.id !== value)
                onChange(tab.id)
            }}
          >
            {t(tab.labelKey, {
              ns: 'workflow',
              defaultValue: tab.id === 'registered' ? 'Registered alias' : 'Custom model',
            })}
          </button>
        )
      })}
    </div>
  )
}

export default React.memo(SourceModeTabs)
