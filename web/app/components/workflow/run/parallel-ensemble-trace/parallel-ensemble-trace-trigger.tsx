'use client'
import type { FC } from 'react'
import type { NodeTracing } from '@/types/workflow'
import { cn } from '@langgenius/dify-ui/cn'
import { RiArrowRightSLine } from '@remixicon/react'
import { useEffect, useMemo, useRef, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { useStore } from '@/app/components/workflow/store'
import ParallelEnsembleTraceStepRow from './parallel-ensemble-trace-step'

type Props = {
  nodeInfo: NodeTracing
}

// How many of the most-recent steps to render. The backend caps the
// trace store at ``max_trace_tokens`` (default 1000) but the streamed
// list can contain every step the runner emitted; for v1 we cap render
// to the trailing 200 entries to keep the panel responsive on long
// runs. The user can still scroll within that window. A future
// virtualisation pass can lift this cap.
const RENDER_TAIL_LIMIT = 200

const ParallelEnsembleTraceTrigger: FC<Props> = ({ nodeInfo }) => {
  const { t } = useTranslation()
  const [expanded, setExpanded] = useState(false)
  const steps = useStore(s => s.parallelEnsembleTraceByNodeId[nodeInfo.node_id]) ?? []
  const stepsRef = useRef<HTMLDivElement>(null)

  const visibleSteps = useMemo(() => {
    if (steps.length <= RENDER_TAIL_LIMIT)
      return steps
    return steps.slice(steps.length - RENDER_TAIL_LIMIT)
  }, [steps])

  // Auto-scroll the panel to the latest step as new ones stream in.
  // Only scrolls when expanded, so a collapsed panel does not fight
  // user reads on other parts of the run-detail UI.
  useEffect(() => {
    if (!expanded)
      return
    const el = stepsRef.current
    if (el)
      el.scrollTop = el.scrollHeight
  }, [steps.length, expanded])

  // Hide entirely when no steps have arrived. The user enables the
  // trace stream via ``DiagnosticsConfig.enable_trace_stream`` on the
  // node panel; if it stayed off this whole run, there is nothing to
  // show — keeping the trigger out of the DOM is less noisy than a
  // disabled card.
  if (steps.length === 0)
    return null

  return (
    <div className="rounded-[10px] bg-components-button-tertiary-bg">
      <div
        className="flex cursor-pointer items-center px-3 py-2"
        onClick={() => setExpanded(prev => !prev)}
      >
        <RiArrowRightSLine
          className={cn(
            'mr-1 h-4 w-4 shrink-0 text-text-quaternary transition-transform',
            expanded && 'rotate-90',
          )}
        />
        <div className="grow system-xs-medium-uppercase text-text-tertiary">
          {t('parallelEnsemble.trace.title', { ns: 'workflow' })}
        </div>
        <div className="shrink-0 system-xs-regular text-text-tertiary">
          {t('parallelEnsemble.trace.stepCount', { ns: 'workflow', count: steps.length })}
          {steps.length > RENDER_TAIL_LIMIT && (
            <span className="ml-1 system-2xs-regular">
              {t('parallelEnsemble.trace.tailNotice', { ns: 'workflow', shown: RENDER_TAIL_LIMIT })}
            </span>
          )}
        </div>
      </div>
      {expanded && (
        <div
          ref={stepsRef}
          className="max-h-80 space-y-1 overflow-auto px-2 pb-2"
        >
          {visibleSteps.map(step => (
            <ParallelEnsembleTraceStepRow
              key={step.message_id ?? `${step.step}`}
              step={step}
            />
          ))}
        </div>
      )}
    </div>
  )
}

export default ParallelEnsembleTraceTrigger
