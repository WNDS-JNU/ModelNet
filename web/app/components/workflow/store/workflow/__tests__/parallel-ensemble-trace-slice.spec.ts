import type { ParallelEnsembleTraceStepResponse } from '@/types/workflow'
import { createStore } from 'zustand/vanilla'
import { PARALLEL_ENSEMBLE_TRACE_STEP_KIND } from '@/types/workflow'
import { createParallelEnsembleTraceSlice } from '../parallel-ensemble-trace-slice'

const buildStep = (overrides?: Partial<{ messageId: string, step: number, token: string, nodeId: string }>): ParallelEnsembleTraceStepResponse => {
  const messageId = overrides?.messageId ?? `exec_1:trace:${overrides?.step ?? 0}`
  const step = overrides?.step ?? 0
  const token = overrides?.token ?? 't0'
  const nodeId = overrides?.nodeId ?? 'pe_1'
  return {
    task_id: 'task_1',
    event: 'agent_log',
    data: {
      node_execution_id: 'exec_1',
      message_id: messageId,
      node_id: nodeId,
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

describe('createParallelEnsembleTraceSlice', () => {
  it('appends steps in arrival order keyed by node_id', () => {
    const store = createStore(createParallelEnsembleTraceSlice)

    store.getState().appendParallelEnsembleTraceStep(buildStep({ step: 0, token: 'a' }))
    store.getState().appendParallelEnsembleTraceStep(buildStep({ step: 1, token: 'b' }))
    store.getState().appendParallelEnsembleTraceStep(buildStep({ step: 2, token: 'c' }))

    const steps = store.getState().parallelEnsembleTraceByNodeId.pe_1!
    expect(steps.map(s => s.selected_token)).toEqual(['a', 'b', 'c'])
  })

  it('dedupes by message_id (re-emit replaces in place, no order shift)', () => {
    // Pins the dedup contract: the backend uses a deterministic
    // "<exec>:trace:<step>" message_id, so a re-emit of the same step
    // (e.g. browser reconnect mid-run) must not duplicate or re-order.
    const store = createStore(createParallelEnsembleTraceSlice)
    store.getState().appendParallelEnsembleTraceStep(buildStep({ step: 0, token: 'a' }))
    store.getState().appendParallelEnsembleTraceStep(buildStep({ step: 1, token: 'b' }))
    // Re-emit step 0 with mutated token — same message_id, replaces.
    store.getState().appendParallelEnsembleTraceStep(buildStep({ step: 0, token: 'a-fixed' }))

    const steps = store.getState().parallelEnsembleTraceByNodeId.pe_1!
    expect(steps).toHaveLength(2)
    expect(steps[0]!.selected_token).toBe('a-fixed')
    expect(steps[1]!.selected_token).toBe('b')
  })

  it('partitions steps per node_id (multiple parallel-ensemble nodes do not bleed)', () => {
    const store = createStore(createParallelEnsembleTraceSlice)
    store.getState().appendParallelEnsembleTraceStep(buildStep({ nodeId: 'pe_a', step: 0, token: 'a0' }))
    store.getState().appendParallelEnsembleTraceStep(buildStep({ nodeId: 'pe_b', step: 0, token: 'b0' }))
    store.getState().appendParallelEnsembleTraceStep(buildStep({ nodeId: 'pe_a', step: 1, token: 'a1' }))

    expect(store.getState().parallelEnsembleTraceByNodeId.pe_a!.map(s => s.selected_token)).toEqual(['a0', 'a1'])
    expect(store.getState().parallelEnsembleTraceByNodeId.pe_b!.map(s => s.selected_token)).toEqual(['b0'])
  })

  it('resetParallelEnsembleTrace clears every node bucket', () => {
    const store = createStore(createParallelEnsembleTraceSlice)
    store.getState().appendParallelEnsembleTraceStep(buildStep({ step: 0 }))
    store.getState().resetParallelEnsembleTrace()
    expect(store.getState().parallelEnsembleTraceByNodeId).toEqual({})
  })
})
