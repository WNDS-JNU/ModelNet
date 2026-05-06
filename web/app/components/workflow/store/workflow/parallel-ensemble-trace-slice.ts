import type { StateCreator } from 'zustand'
import type {
  ParallelEnsembleTraceStep,
  ParallelEnsembleTraceStepResponse,
} from '@/types/workflow'

export type ParallelEnsembleTraceSliceShape = {
  parallelEnsembleTraceByNodeId: Record<string, ParallelEnsembleTraceStep[]>
  appendParallelEnsembleTraceStep: (response: ParallelEnsembleTraceStepResponse) => void
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
  resetParallelEnsembleTrace: () => set(() => ({ parallelEnsembleTraceByNodeId: {} })),
})
