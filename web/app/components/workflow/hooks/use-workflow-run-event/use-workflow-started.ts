import type { WorkflowStartedResponse } from '@/types/workflow'
import { produce } from 'immer'
import { useCallback } from 'react'
import { useStoreApi } from 'reactflow'
import { useWorkflowStore } from '@/app/components/workflow/store'
import { WorkflowRunningStatus } from '@/app/components/workflow/types'

export const useWorkflowStarted = () => {
  const store = useStoreApi()
  const workflowStore = useWorkflowStore()

  const handleWorkflowStarted = useCallback((params: WorkflowStartedResponse) => {
    const { task_id, data } = params
    const {
      workflowRunningData,
      setWorkflowRunningData,
      setIterParallelLogMap,
      resetParallelEnsembleTrace,
    } = workflowStore.getState()
    const {
      getNodes,
      setNodes,
      edges,
      setEdges,
    } = store.getState()
    if (workflowRunningData?.result?.status === WorkflowRunningStatus.Paused) {
      setWorkflowRunningData(produce(workflowRunningData!, (draft) => {
        draft.result = {
          ...draft.result,
          status: WorkflowRunningStatus.Running,
        }
      }))
      return
    }
    setIterParallelLogMap(new Map())
    // Drop any parallel-ensemble trace steps left behind by a previous
    // run on the same canvas; without this the run panel would
    // pre-render the prior session's steps and append the new
    // execution's steps after them, making it look like the joint loop
    // ran twice as long. ``message_id`` dedup does NOT save us — the
    // ``<execution_id>:trace:<step>`` key changes every run, so the
    // store would just keep accumulating.
    resetParallelEnsembleTrace()
    setWorkflowRunningData(produce(workflowRunningData!, (draft) => {
      draft.task_id = task_id
      draft.result = {
        ...draft?.result,
        ...data,
        status: WorkflowRunningStatus.Running,
      }
      draft.resultText = ''
    }))
    const nodes = getNodes()
    const newNodes = produce(nodes, (draft) => {
      draft.forEach((node) => {
        node.data._waitingRun = true
        node.data._runningBranchId = undefined
      })
    })
    setNodes(newNodes)
    const newEdges = produce(edges, (draft) => {
      draft.forEach((edge) => {
        edge.data = {
          ...edge.data,
          _sourceRunningStatus: undefined,
          _targetRunningStatus: undefined,
          _waitingRun: true,
        }
      })
    })
    setEdges(newEdges)
  }, [workflowStore, store])

  return {
    handleWorkflowStarted,
  }
}
