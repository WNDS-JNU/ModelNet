'use client'
import type { FC } from 'react'
import type {
  ParallelEnsembleTraceCandidate,
  ParallelEnsembleTraceStep,
} from '@/types/workflow'
import { cn } from '@langgenius/dify-ui/cn'
import { useTranslation } from 'react-i18next'

type Props = {
  step: ParallelEnsembleTraceStep
}

// Format helper: probability → "0.84" (two decimals). The backend
// already trimmed the candidate list to the configured top-k, so there
// is no need to re-cap here.
const formatProb = (p: number) => p.toFixed(2)

const Candidates: FC<{
  selected: string
  candidates: ParallelEnsembleTraceCandidate[]
}> = ({ selected, candidates }) => (
  <div className="flex flex-wrap gap-1">
    {candidates.map((c, idx) => {
      const isSelected = c.token === selected
      return (
        <span
          key={`${idx}-${c.token}`}
          className={cn(
            'rounded border px-1.5 py-0.5 system-2xs-medium',
            isSelected
              ? 'border-components-badge-status-light-success-border bg-components-badge-status-light-success-bg text-text-success'
              : 'border-divider-subtle bg-components-input-bg-normal text-text-tertiary',
          )}
        >
          <span className="font-mono">{JSON.stringify(c.token)}</span>
          <span className="ml-1 opacity-70">{formatProb(c.prob)}</span>
        </span>
      )
    })}
  </div>
)

const ParallelEnsembleTraceStepRow: FC<Props> = ({ step }) => {
  const { t } = useTranslation()

  // Render the per-step header (step #, selected token, score, time)
  // unconditionally; the body sections (per_model / errors / reasoning)
  // are gated by the diagnostics flags the runner used at emit time —
  // missing keys here mean the user opted out of that field, not that
  // the step had no data.
  return (
    <div className="rounded-md border border-divider-subtle bg-background-section-burn p-2">
      <div className="flex items-center gap-2">
        <span className="rounded bg-components-input-bg-normal px-1.5 py-0.5 system-2xs-medium text-text-tertiary">
          {`#${step.step}`}
        </span>
        <span className="grow truncate font-mono system-xs-medium text-text-primary">
          {JSON.stringify(step.selected_token)}
        </span>
        <span className="shrink-0 system-2xs-regular text-text-tertiary">
          {`p=${formatProb(step.selected_score)} · ${step.elapsed_ms}ms`}
        </span>
      </div>
      {step.per_model && Object.keys(step.per_model).length > 0 && (
        <div className="mt-2 space-y-1">
          {Object.entries(step.per_model).map(([sourceId, candidates]) => (
            <div key={sourceId} className="flex items-start gap-2">
              <span className="mt-0.5 shrink-0 system-2xs-regular text-text-tertiary">
                {sourceId}
              </span>
              <div className="grow">
                <Candidates selected={step.selected_token} candidates={candidates} />
              </div>
            </div>
          ))}
        </div>
      )}
      {step.per_model_errors && Object.keys(step.per_model_errors).length > 0 && (
        <div className="mt-2 space-y-0.5">
          {Object.entries(step.per_model_errors).map(([sourceId, errMsg]) => (
            <div
              key={sourceId}
              className="flex items-start gap-2 system-2xs-regular text-text-destructive"
            >
              <span className="shrink-0">{sourceId}</span>
              <span className="break-words">{errMsg}</span>
            </div>
          ))}
        </div>
      )}
      {step.aggregator_reasoning && (
        <details className="mt-2">
          <summary className="cursor-pointer system-2xs-regular text-text-tertiary">
            {t('parallelEnsemble.trace.reasoning', { ns: 'workflow' })}
          </summary>
          <pre className="mt-1 max-h-32 overflow-auto rounded bg-components-input-bg-normal p-1.5 font-mono system-2xs-regular break-all whitespace-pre-wrap text-text-secondary">
            {JSON.stringify(step.aggregator_reasoning, null, 2)}
          </pre>
        </details>
      )}
    </div>
  )
}

export default ParallelEnsembleTraceStepRow
