import type { ParallelEnsembleTraceStepResponse } from '@/types/workflow'
import { PARALLEL_ENSEMBLE_TRACE_STEP_KIND } from '@/types/workflow'
import { renderWorkflowHook } from '../../../__tests__/workflow-test-env'
import { useWorkflowParallelEnsembleTrace } from '../use-workflow-parallel-ensemble-trace'

const buildResponse = (overrides?: Partial<{ step: number, token: string }>): ParallelEnsembleTraceStepResponse => {
  const step = overrides?.step ?? 0
  const token = overrides?.token ?? 'a'
  return {
    task_id: 'task_1',
    event: 'agent_log',
    data: {
      node_execution_id: 'exec_1',
      message_id: `exec_1:trace:${step}`,
      node_id: 'pe_1',
      label: `Step ${step}: '${token}'`,
      status: 'success',
      data: {
        step,
        selected_token: token,
        selected_score: 0.5,
        elapsed_ms: 1,
      },
      metadata: { kind: PARALLEL_ENSEMBLE_TRACE_STEP_KIND },
    },
  }
}

describe('useWorkflowParallelEnsembleTrace', () => {
  it('forwards SSE responses to the trace store reducer', () => {
    const { result, store } = renderWorkflowHook(() => useWorkflowParallelEnsembleTrace())
    result.current.handleWorkflowParallelEnsembleTrace(buildResponse({ step: 0, token: 'a' }))
    result.current.handleWorkflowParallelEnsembleTrace(buildResponse({ step: 1, token: 'b' }))
    const steps = store.getState().parallelEnsembleTraceByNodeId.pe_1!
    expect(steps.map(s => s.selected_token)).toEqual(['a', 'b'])
  })

  it('hooks the same dedup contract as the slice (re-emit replaces in place)', () => {
    // Pins the end-to-end contract: SSE → hook → reducer dedup. If the
    // hook ever started buffering or routing through a different
    // reducer, this would catch the drift.
    const { result, store } = renderWorkflowHook(() => useWorkflowParallelEnsembleTrace())
    result.current.handleWorkflowParallelEnsembleTrace(buildResponse({ step: 0, token: 'a' }))
    result.current.handleWorkflowParallelEnsembleTrace(buildResponse({ step: 0, token: 'a-fixed' }))
    const steps = store.getState().parallelEnsembleTraceByNodeId.pe_1!
    expect(steps).toHaveLength(1)
    expect(steps[0]!.selected_token).toBe('a-fixed')
  })
})
