import type { StateCreator } from 'zustand'
import type {
  NodeTracing,
  ParallelEnsembleTraceStep,
  ParallelEnsembleTraceStepResponse,
} from '@/types/workflow'
import { BlockEnum } from '@/app/components/workflow/types'

type FinalParallelEnsembleTrace = {
  token_trace?: ParallelEnsembleTraceStep[]
}

export type ParallelEnsembleTraceSliceShape = {
  parallelEnsembleTraceByNodeId: Record<string, ParallelEnsembleTraceStep[]>
  appendParallelEnsembleTraceStep: (response: ParallelEnsembleTraceStepResponse) => void
  hydrateParallelEnsembleTraceFromNodeFinished: (data: NodeTracing) => void
  resetParallelEnsembleTrace: () => void
}

export const createParallelEnsembleTraceSlice: StateCreator<ParallelEnsembleTraceSliceShape> = set => ({
  parallelEnsembleTraceByNodeId: {},
  appendParallelEnsembleTraceStep: (response) => {
    // Idempotent append keyed by ``message_id`` (the backend produces a
    // deterministic ``"<execution_id>:trace:<step>"`` so a re-emit
    // doesn't double-render). The dedup is per-node-id because a single
    // workflow run can have multiple parallel-ensemble nodes — they
    // each carry their own step list.
    const nodeId = response.data.node_id
    const incomingStep = response.data.data
    const incomingMessageId = response.data.message_id
    set((state) => {
      const previous = state.parallelEnsembleTraceByNodeId[nodeId] ?? []
      const existingIndex = previous.findIndex(s => s.message_id === incomingMessageId)
      let next: ParallelEnsembleTraceStep[]
      if (existingIndex === -1) {
        next = [...previous, { ...incomingStep, message_id: incomingMessageId }]
      }
      else {
        // Update in place — preserves insertion order so the panel
        // does not re-flow when the backend re-emits a step.
        next = previous.slice()
        next[existingIndex] = { ...incomingStep, message_id: incomingMessageId }
      }
      return {
        parallelEnsembleTraceByNodeId: {
          ...state.parallelEnsembleTraceByNodeId,
          [nodeId]: next,
        },
      }
    })
  },
  hydrateParallelEnsembleTraceFromNodeFinished: (data) => {
    if (data.node_type !== BlockEnum.ParallelEnsemble)
      return

    const trace = (
      data.process_data?.ensemble_trace ?? data.outputs?.trace
    ) as FinalParallelEnsembleTrace | undefined
    const tokenTrace = trace?.token_trace
    if (!Array.isArray(tokenTrace))
      return

    set(state => ({
      parallelEnsembleTraceByNodeId: {
        ...state.parallelEnsembleTraceByNodeId,
        [data.node_id]: tokenTrace.map(step => ({
          ...step,
          message_id: `${data.id}:trace:${step.step}`,
        })),
      },
    }))
  },
  resetParallelEnsembleTrace: () => set(() => ({ parallelEnsembleTraceByNodeId: {} })),
})
