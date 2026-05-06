import type { AgentLogResponse } from '@/types/workflow'
import { produce } from 'immer'
import { useCallback } from 'react'
import { useWorkflowStore } from '@/app/components/workflow/store'

// Node-extension structured payloads (e.g. parallel-ensemble per-step
// trace) ride the same ``agent_log`` SSE channel but are split off at
// the SSE boundary in ``web/service/base.ts`` based on
// ``data.metadata.kind``. By the time this hook is called, the
// payload is guaranteed to be a real agent log — the trace stream
// goes to ``useWorkflowParallelEnsembleTrace`` instead.
export const useWorkflowAgentLog = () => {
  const workflowStore = useWorkflowStore()

  const handleWorkflowAgentLog = useCallback((params: AgentLogResponse) => {
    const { data } = params
    const {
      workflowRunningData,
      setWorkflowRunningData,
    } = workflowStore.getState()

    setWorkflowRunningData(produce(workflowRunningData!, (draft) => {
      const currentIndex = draft.tracing!.findIndex(item => item.node_id === data.node_id)
      if (currentIndex > -1) {
        const current = draft.tracing![currentIndex]

        if (current!.execution_metadata) {
          if (current!.execution_metadata.agent_log) {
            const currentLogIndex = current!.execution_metadata.agent_log.findIndex(log => log.message_id === data.message_id)
            if (currentLogIndex > -1) {
              current!.execution_metadata.agent_log[currentLogIndex] = {
                ...current!.execution_metadata.agent_log[currentLogIndex],
                ...data,
              }
            }
            else {
              current!.execution_metadata.agent_log.push(data)
            }
          }
          else {
            current!.execution_metadata.agent_log = [data]
          }
        }
        else {
          current!.execution_metadata = {
            agent_log: [data],
          } as any
        }
      }
    }))
  }, [workflowStore])

  return {
    handleWorkflowAgentLog,
  }
}
