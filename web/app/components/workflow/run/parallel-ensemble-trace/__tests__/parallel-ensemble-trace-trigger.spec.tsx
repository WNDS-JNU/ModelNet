import type { NodeTracing, ParallelEnsembleTraceStep } from '@/types/workflow'
import { fireEvent, render, screen } from '@testing-library/react'
import { useStore } from '@/app/components/workflow/store'
import { NodeRunningStatus } from '@/app/components/workflow/types'
import ParallelEnsembleTraceTrigger from '../parallel-ensemble-trace-trigger'

vi.mock('@/app/components/workflow/store', () => ({
  useStore: vi.fn(),
}))

vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string, opts?: Record<string, unknown>) => {
      if (opts && 'count' in opts)
        return `${key}:${opts.count as number}`
      return key
    },
  }),
}))

const useStoreMock = useStore as unknown as ReturnType<typeof vi.fn>

const buildNodeInfo = (overrides: Partial<NodeTracing> = {}): NodeTracing => ({
  id: 'pe_1',
  index: 0,
  predecessor_node_id: '',
  node_id: 'pe_1',
  node_type: 'parallel-ensemble' as NodeTracing['node_type'],
  title: 'Parallel ensemble',
  inputs: {},
  inputs_truncated: false,
  process_data: {},
  process_data_truncated: false,
  outputs_truncated: false,
  status: NodeRunningStatus.Succeeded,
  elapsed_time: 0,
  metadata: { iterator_length: 0, iterator_index: 0, loop_length: 0, loop_index: 0 },
  created_at: 0,
  created_by: { id: '', name: '', email: '' },
  finished_at: 0,
  ...overrides,
})

const buildStep = (step: number): ParallelEnsembleTraceStep => ({
  step,
  selected_token: `t${step}`,
  selected_score: 0.5,
  elapsed_ms: 1,
  message_id: `exec_1:trace:${step}`,
})

describe('ParallelEnsembleTraceTrigger', () => {
  it('hides entirely when the node finished with zero steps (trace_stream was off)', () => {
    // Pins the noise-suppression contract: a finished node without any
    // streamed steps means the user disabled ``enable_trace_stream`` for
    // this run, so the trigger should not occupy DOM space.
    useStoreMock.mockReturnValue([])
    const { container } = render(
      <ParallelEnsembleTraceTrigger nodeInfo={buildNodeInfo({ status: NodeRunningStatus.Succeeded })} />,
    )
    expect(container.firstChild).toBeNull()
  })

  it('stays mounted while the node is running with zero steps so early expand does not flash empty', () => {
    // Without this branch, expanding the node panel before step 1 lands
    // would render nothing — looked indistinguishable from a broken wire.
    useStoreMock.mockReturnValue([])
    render(
      <ParallelEnsembleTraceTrigger nodeInfo={buildNodeInfo({ status: NodeRunningStatus.Running })} />,
    )
    expect(screen.getByText('parallelEnsemble.trace.title')).toBeInTheDocument()
    // 0-count badge is visible in the header so the user can see the
    // panel is wired up but waiting.
    expect(screen.getByText('parallelEnsemble.trace.stepCount:0')).toBeInTheDocument()
  })

  it('shows the waiting placeholder when expanded with zero steps during a run', () => {
    useStoreMock.mockReturnValue([])
    render(
      <ParallelEnsembleTraceTrigger nodeInfo={buildNodeInfo({ status: NodeRunningStatus.Running })} />,
    )
    fireEvent.click(screen.getByText('parallelEnsemble.trace.title'))
    expect(screen.getByText('parallelEnsemble.trace.waiting')).toBeInTheDocument()
  })

  it('renders step rows once steps arrive, regardless of running state', () => {
    useStoreMock.mockReturnValue([buildStep(0), buildStep(1)])
    render(
      <ParallelEnsembleTraceTrigger nodeInfo={buildNodeInfo({ status: NodeRunningStatus.Succeeded })} />,
    )
    expect(screen.getByText('parallelEnsemble.trace.stepCount:2')).toBeInTheDocument()
    fireEvent.click(screen.getByText('parallelEnsemble.trace.title'))
    expect(screen.queryByText('parallelEnsemble.trace.waiting')).not.toBeInTheDocument()
    expect(screen.getByText('#0')).toBeInTheDocument()
    expect(screen.getByText('#1')).toBeInTheDocument()
  })
})
