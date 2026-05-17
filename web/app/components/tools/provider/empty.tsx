'use client'
import { cn } from '@langgenius/dify-ui/cn'
import { useTranslation } from 'react-i18next'
import useTheme from '@/hooks/use-theme'
import Link from '@/next/link'
import { NoToolPlaceholder } from '../../base/icons/src/vender/other'
import { ToolTypeEnum } from '../../workflow/block-selector/types'

type Props = {
  type?: ToolTypeEnum
  isAgent?: boolean
}

const getLink = (type?: ToolTypeEnum) => {
  switch (type) {
    case ToolTypeEnum.Custom:
      return '/tools?category=api'
    case ToolTypeEnum.MCP:
      return '/tools?category=mcp'
    default:
      return '/tools?category=api'
  }
}
const Empty = ({
  type,
  isAgent,
}: Props) => {
  const { t } = useTranslation()
  const { theme } = useTheme()

  const hasLink = type === ToolTypeEnum.Custom || type === ToolTypeEnum.MCP
  const renderType = isAgent ? 'agent' as const : type
  const hasTitle = renderType && t(`addToolModal.${renderType}.title`, { ns: 'tools' }) !== `addToolModal.${renderType}.title`
  const tipClassName = cn('flex items-center text-[13px] leading-[18px] text-text-tertiary', hasLink && 'cursor-pointer hover:text-text-accent')

  return (
    <div className="flex flex-col items-center justify-center">
      <NoToolPlaceholder className={theme === 'dark' ? 'invert' : ''} />
      <div className="mt-2 mb-1 text-[13px] leading-[18px] font-medium text-text-primary">
        {(hasTitle && renderType) ? t(`addToolModal.${renderType}.title`, { ns: 'tools' }) : 'No tools available'}
      </div>
      {!!(!isAgent && hasTitle && renderType) && (
        hasLink
          ? (
              <Link className={tipClassName} href={getLink(type)} target="_blank">
                {t(`addToolModal.${renderType}.tip`, { ns: 'tools' })}
                {' '}
                <span className="ml-0.5 i-ri-arrow-right-up-line h-3 w-3" />
              </Link>
            )
          : (
              <div className={tipClassName}>
                {t(`addToolModal.${renderType}.tip`, { ns: 'tools' })}
              </div>
            )
      )}
    </div>
  )
}

export default Empty
