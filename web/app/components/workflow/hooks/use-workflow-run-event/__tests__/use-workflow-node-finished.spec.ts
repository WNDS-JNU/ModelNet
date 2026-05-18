import { act, waitFor } from '@testing-library/react'
import { createNode } from '../../../__tests__/fixtures'
import { baseRunningData } from '../../../__tests__/workflow-test-env'
import { BlockEnum, NodeRunningStatus } from '../../../types'
import { useWorkflowNodeFinished } from '../use-workflow-node-finished'
import {
  createNodeFinishedResponse,
  getEdgeRuntimeState,
  getNodeRuntimeState,
  renderRunEventHook,
} from './test-helpers'

describe('useWorkflowNodeFinished', () => {
  it('updates tracing and node running status', async () => {
    const { result, store } = renderRunEventHook(() => useWorkflowNodeFinished(), {
      nodes: [
        createNode({
          id: 'n1',
          data: { _runningStatus: NodeRunningStatus.Running },
        }),
      ],
      initialStoreState: {
        workflowRunningData: baseRunningData({
          tracing: [{ id: 'trace-1', node_id: 'n1', status: NodeRunningStatus.Running }],
        }),
      },
    })

    act(() => {
      result.current.handleWorkflowNodeFinished(createNodeFinishedResponse())
    })

    const trace = store.getState().workflowRunningData!.tracing![0]
    expect(trace!.status).toBe(NodeRunningStatus.Succeeded)

    await waitFor(() => {
      expect(getNodeRuntimeState(result.current.nodes[0])._runningStatus).toBe(NodeRunningStatus.Succeeded)
      expect(getEdgeRuntimeState(result.current.edges[0])._targetRunningStatus).toBe(NodeRunningStatus.Succeeded)
    })
  })

  it('sets _runningBranchId for IfElse nodes', async () => {
    const { result } = renderRunEventHook(() => useWorkflowNodeFinished(), {
      nodes: [
        createNode({
          id: 'n1',
          data: { _runningStatus: NodeRunningStatus.Running },
        }),
      ],
      initialStoreState: {
        workflowRunningData: baseRunningData({
          tracing: [{ id: 'trace-1', node_id: 'n1', status: NodeRunningStatus.Running }],
        }),
      },
    })

    act(() => {
      result.current.handleWorkflowNodeFinished(createNodeFinishedResponse({
        data: {
          id: 'trace-1',
          node_id: 'n1',
          node_type: BlockEnum.IfElse,
          status: NodeRunningStatus.Succeeded,
          outputs: { selected_case_id: 'branch-a' },
        } as never,
      }))
    })

    await waitFor(() => {
      expect(getNodeRuntimeState(result.current.nodes[0])._runningBranchId).toBe('branch-a')
    })
  })

  it('hydrates parallel ensemble final trace from node finished data', () => {
    const { result, store } = renderRunEventHook(() => useWorkflowNodeFinished(), {
      nodes: [
        createNode({
          id: 'n1',
          data: { _runningStatus: NodeRunningStatus.Running },
        }),
      ],
      initialStoreState: {
        workflowRunningData: baseRunningData({
          tracing: [{ id: 'trace-1', node_id: 'n1', status: NodeRunningStatus.Running }],
        }),
      },
    })

    act(() => {
      result.current.handleWorkflowNodeFinished(createNodeFinishedResponse({
        data: {
          id: 'trace-1',
          node_id: 'n1',
          node_type: BlockEnum.ParallelEnsemble,
          status: NodeRunningStatus.Succeeded,
          process_data: {
            ensemble_trace: {
              token_trace: [
                {
                  step: 0,
                  selected_token: 'duet',
                  selected_score: 0.8,
                  elapsed_ms: 10,
                  aggregator_reasoning: {
                    per_token_logit: { duet: 2.1 },
                    winner_per_model: { model_a: 2.1 },
                    topT_candidates: ['duet'],
                  },
                },
              ],
            },
          },
        } as never,
      }))
    })

    const steps = store.getState().parallelEnsembleTraceByNodeId.n1!
    expect(steps).toHaveLength(1)
    expect(steps[0]!.message_id).toBe('trace-1:trace:0')
    expect(steps[0]!.aggregator_reasoning).toEqual({
      per_token_logit: { duet: 2.1 },
      winner_per_model: { model_a: 2.1 },
      topT_candidates: ['duet'],
    })
  })
})
