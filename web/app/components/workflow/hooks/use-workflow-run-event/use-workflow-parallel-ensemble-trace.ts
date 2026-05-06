import type { ParallelEnsembleTraceStepResponse } from '@/types/workflow'
import { useCallback } from 'react'
import { useWorkflowStore } from '@/app/components/workflow/store'

// Listens for parallel-ensemble per-step trace events. The SSE wiring
// in ``web/service/base.ts`` routes ``agent_log`` events with
// ``metadata.kind === PARALLEL_ENSEMBLE_TRACE_STEP_KIND`` here instead
// of to the agent-log handler — single source of truth for the
// discriminator lives in ``parallel_ensemble/node.py`` (server) and
// ``types/workflow.ts`` (client). The hook only forwards the wire
// payload to the trace store; insertion / dedup logic lives in
// ``parallel-ensemble-trace-slice.ts`` so multiple consumers (workflow
// app callbacks, debug-and-preview, future RAG) can call the same
// reducer.
export const useWorkflowParallelEnsembleTrace = () => {
  const workflowStore = useWorkflowStore()

  const handleWorkflowParallelEnsembleTrace = useCallback((response: ParallelEnsembleTraceStepResponse) => {
    workflowStore.getState().appendParallelEnsembleTraceStep(response)
  }, [workflowStore])

  return {
    handleWorkflowParallelEnsembleTrace,
  }
}
