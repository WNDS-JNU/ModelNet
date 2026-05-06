import type { ParallelEnsembleTraceStep } from '@/types/workflow'
import { render, screen } from '@testing-library/react'
import ParallelEnsembleTraceStepRow from '../parallel-ensemble-trace-step'

const baseStep: ParallelEnsembleTraceStep = {
  step: 17,
  selected_token: 'hello',
  selected_score: 0.84,
  elapsed_ms: 12,
}

describe('ParallelEnsembleTraceStepRow', () => {
  it('renders the always-on header (step #, token, score, elapsed)', () => {
    render(<ParallelEnsembleTraceStepRow step={baseStep} />)
    expect(screen.getByText('#17')).toBeInTheDocument()
    // ``selected_token`` is JSON-quoted so whitespace tokens stay
    // visible — this assertion pins that contract.
    expect(screen.getByText('"hello"')).toBeInTheDocument()
    expect(screen.getByText('p=0.84 · 12ms')).toBeInTheDocument()
  })

  it('hides per_model / errors / reasoning when the diagnostics flag was off', () => {
    // The runner only includes those fields when the corresponding
    // ``include_*`` flag is on — the row component must not synthesize
    // empty placeholders for absent fields.
    const { container } = render(<ParallelEnsembleTraceStepRow step={baseStep} />)
    expect(container.querySelectorAll('details').length).toBe(0)
  })

  it('highlights the selected token among the per_model candidates', () => {
    const step: ParallelEnsembleTraceStep = {
      ...baseStep,
      per_model: {
        m1: [
          { token: 'hello', prob: 0.9 },
          { token: 'hi', prob: 0.05 },
        ],
        m2: [
          { token: 'hello', prob: 0.7 },
          { token: 'hey', prob: 0.2 },
        ],
      },
    }
    render(<ParallelEnsembleTraceStepRow step={step} />)
    // Two ``"hello"`` chips (one per backend) plus the header instance.
    const hellos = screen.getAllByText('"hello"')
    expect(hellos.length).toBeGreaterThanOrEqual(3)
    // Source ids surface so the user can tell which backend voted what.
    expect(screen.getByText('m1')).toBeInTheDocument()
    expect(screen.getByText('m2')).toBeInTheDocument()
  })

  it('renders per-source error rows when the runner attached them', () => {
    const step: ParallelEnsembleTraceStep = {
      ...baseStep,
      per_model_errors: { m_broken: 'TimeoutError: deadline' },
    }
    render(<ParallelEnsembleTraceStepRow step={step} />)
    expect(screen.getByText('m_broken')).toBeInTheDocument()
    expect(screen.getByText('TimeoutError: deadline')).toBeInTheDocument()
  })

  it('renders aggregator reasoning behind a collapsible details element', () => {
    const step: ParallelEnsembleTraceStep = {
      ...baseStep,
      aggregator_reasoning: { per_token_score: { hello: 1.6 } },
    }
    const { container } = render(<ParallelEnsembleTraceStepRow step={step} />)
    expect(container.querySelector('details')).not.toBeNull()
    // Body content rendered (default open state may vary by browser, so
    // we don't assert visibility — just presence of the JSON dump).
    expect(container.textContent).toContain('per_token_score')
    expect(container.textContent).toContain('1.6')
  })
})
