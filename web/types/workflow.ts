import type { RefObject } from 'react'
import type { Viewport } from 'reactflow'
import type { ErrorHandleTypeEnum } from '@/app/components/workflow/nodes/_base/components/error-handle/types'
import type { FormInputItem, UserAction } from '@/app/components/workflow/nodes/human-input/types'
import type {
  BlockEnum,
  CommonNodeType,
  ConversationVariable,
  Edge,
  EnvironmentVariable,
  InputVar,
  Node,
  ValueSelector,
  Variable,
  VarType,
  WorkflowRunningStatus,
} from '@/app/components/workflow/types'
import type { RAGPipelineVariables } from '@/models/pipeline'
import type { TransferMethod } from '@/types/app'

export type AgentLogItem = {
  node_execution_id: string
  message_id: string
  node_id: string
  parent_id?: string
  label: string
  data: object // debug data
  error?: string
  status: string
  metadata?: {
    elapsed_time?: number
    provider?: string
    icon?: string
    // Extension nodes can ride a discriminator key here so the SSE
    // ``agent_log`` channel can carry node-specific structured payloads
    // (e.g. parallel-ensemble per-step trace) without polluting the
    // agent-log UI. The base type stays open-string; consumers narrow
    // by const value.
    kind?: string
  }
}

export type AgentLogItemWithChildren = AgentLogItem & {
  hasCircle?: boolean
  children: AgentLogItemWithChildren[]
}

export type NodeTracing = {
  id: string
  index: number
  predecessor_node_id: string
  node_id: string
  iteration_id?: string
  loop_id?: string
  node_type: BlockEnum
  title: string
  inputs: any
  inputs_truncated: boolean
  process_data: any
  process_data_truncated: boolean
  outputs?: Record<string, any>
  outputs_truncated: boolean
  outputs_full_content?: {
    download_url: string
  }
  status: string
  parallel_run_id?: string
  error?: string
  elapsed_time: number
  execution_metadata?: {
    total_tokens: number
    total_price: number
    currency: string
    iteration_id?: string
    iteration_index?: number
    loop_id?: string
    loop_index?: number
    parallel_id?: string
    parallel_start_node_id?: string
    parent_parallel_id?: string
    parent_parallel_start_node_id?: string
    parallel_mode_run_id?: string
    iteration_duration_map?: IterationDurationMap
    loop_duration_map?: LoopDurationMap
    error_strategy?: ErrorHandleTypeEnum
    agent_log?: AgentLogItem[]
    tool_info?: {
      agent_strategy?: string
      icon?: string
    }
    loop_variable_map?: Record<string, any>
  }
  metadata: {
    iterator_length: number
    iterator_index: number
    loop_length: number
    loop_index: number
  }
  created_at: number
  created_by: {
    id: string
    name: string
    email: string
  }
  iterDurationMap?: IterationDurationMap
  loopDurationMap?: LoopDurationMap
  finished_at: number
  extras?: any
  expand?: boolean // for UI
  details?: NodeTracing[][] // iteration or loop detail
  retryDetail?: NodeTracing[] // retry detail
  retry_index?: number
  parallelDetail?: { // parallel detail. if is in parallel, this field will be set
    isParallelStartNode?: boolean
    parallelTitle?: string
    branchTitle?: string
    children?: NodeTracing[]
  }
  parallel_id?: string
  parallel_start_node_id?: string
  parent_parallel_id?: string
  parent_parallel_start_node_id?: string
  agentLog?: AgentLogItemWithChildren[] // agent log
}

export type FetchWorkflowDraftResponse = {
  id: string
  graph: {
    nodes: Node[]
    edges: Edge[]
    viewport?: Viewport
  }
  features?: any
  created_at: number
  created_by: {
    id: string
    name: string
    email: string
  }
  hash: string
  updated_at: number
  updated_by: {
    id: string
    name: string
    email: string
  }
  tool_published: boolean
  environment_variables?: EnvironmentVariable[]
  conversation_variables?: ConversationVariable[]
  rag_pipeline_variables?: RAGPipelineVariables
  version: string
  marked_name: string
  marked_comment: string
}

export type VersionHistory = FetchWorkflowDraftResponse

export type FetchWorkflowDraftPageParams = {
  url: string
  initialPage: number
  limit: number
  userId?: string
  namedOnly?: boolean
}

export type FetchWorkflowDraftPageResponse = {
  items: VersionHistory[]
  has_more: boolean
  page: number
}

export type NodeTracingListResponse = {
  data: NodeTracing[]
}

export type WorkflowStartedResponse = {
  task_id: string
  workflow_run_id: string
  event: string
  data: {
    id: string
    workflow_id: string
    created_at: number
  }
  conversation_id?: string // only in chatflow
  message_id?: string // only in chatflow
}

export type WorkflowPausedResponse = {
  task_id: string
  workflow_run_id: string
  event: string
  data: {
    outputs: any // todo: remove any
    paused_nodes: string[]
    reasons: any[] // todo: remove any
    workflow_run_id: string
  }
}

export type WorkflowFinishedResponse = {
  task_id: string
  workflow_run_id: string
  event: string
  data: {
    id: string
    workflow_id: string
    status: string
    outputs: any
    error: string
    elapsed_time: number
    total_tokens: number
    total_steps: number
    created_at: number
    created_by: {
      id: string
      name: string
      email: string
    }
    finished_at: number
    files?: FileResponse[]
  }
}

export type NodeStartedResponse = {
  task_id: string
  workflow_run_id: string
  event: string
  data: NodeTracing
}

export type FileResponse = {
  related_id: string
  extension: string
  filename: string
  size: number
  mime_type: string
  transfer_method: TransferMethod
  type: string
  url: string
  upload_file_id: string
  remote_url: string
}

export type NodeFinishedResponse = {
  task_id: string
  workflow_run_id: string
  event: string
  data: NodeTracing
}

export type IterationStartedResponse = {
  task_id: string
  workflow_run_id: string
  event: string
  data: NodeTracing
}

export type IterationNextResponse = {
  task_id: string
  workflow_run_id: string
  event: string
  data: NodeTracing
}

export type IterationFinishedResponse = {
  task_id: string
  workflow_run_id: string
  event: string
  data: NodeTracing
}

export type LoopStartedResponse = {
  task_id: string
  workflow_run_id: string
  event: string
  data: NodeTracing
}

export type LoopNextResponse = {
  task_id: string
  workflow_run_id: string
  event: string
  data: NodeTracing
}

export type LoopFinishedResponse = {
  task_id: string
  workflow_run_id: string
  event: string
  data: NodeTracing
}

export type ParallelBranchStartedResponse = {
  task_id: string
  workflow_run_id: string
  event: string
  data: NodeTracing
}

export type ParallelBranchFinishedResponse = {
  task_id: string
  workflow_run_id: string
  event: string
  data: NodeTracing
}

export type TextChunkResponse = {
  task_id: string
  workflow_run_id: string
  event: string
  data: {
    text: string
  }
}

export type TextReplaceResponse = {
  task_id: string
  workflow_run_id: string
  event: string
  data: {
    text: string
  }
}

export type AgentLogResponse = {
  task_id: string
  event: string
  data: AgentLogItemWithChildren
}

// Real-time per-step trace from the parallel-ensemble node. Rides on
// the ``agent_log`` SSE event (graphon's ``AgentLogEvent`` direct-collect
// path bypasses the response coordinator that buffers
// ``StreamChunkEvent``s) and is discriminated by
// ``data.metadata.kind === PARALLEL_ENSEMBLE_TRACE_STEP_KIND`` so the
// agent-log UI does not pick it up. ``data.data`` carries the same
// filtered ``TokenStepTraceEntry`` the backend's ``TraceCollector``
// recorded — toggling the diagnostics ``include_*`` flags governs both
// the persisted trace and this live stream.
export const PARALLEL_ENSEMBLE_TRACE_STEP_KIND = 'parallel_ensemble_trace_step' as const

export type ParallelEnsembleTraceCandidate = {
  token: string
  prob: number
}

export type ParallelEnsembleTraceStep = {
  // ``message_id`` is the backend-deterministic
  // ``"<execution_id>:trace:<step>"``; the store keys dedup off it so a
  // re-emit cannot insert a duplicate row.
  message_id?: string
  step: number
  selected_token: string
  selected_score: number
  elapsed_ms: number
  per_model?: Record<string, ParallelEnsembleTraceCandidate[]>
  per_model_errors?: Record<string, string>
  aggregator_reasoning?: Record<string, unknown> | null
}

export type ParallelEnsembleTraceStepData = AgentLogItem & {
  data: ParallelEnsembleTraceStep
  metadata: AgentLogItem['metadata'] & {
    kind: typeof PARALLEL_ENSEMBLE_TRACE_STEP_KIND
  }
}

export type ParallelEnsembleTraceStepResponse = {
  task_id: string
  event: string
  data: ParallelEnsembleTraceStepData
}

export type HumanInputFormData = {
  form_id: string
  node_id: string
  node_title: string
  form_content: string
  inputs: FormInputItem[]
  actions: UserAction[]
  form_token: string
  resolved_default_values: Record<string, string>
  display_in_ui: boolean
  expiration_time: number
}

export type HumanInputRequiredResponse = {
  task_id: string
  workflow_run_id: string
  event: string
  data: HumanInputFormData
}

export type HumanInputFilledFormData = {
  node_id: string
  node_title: string
  rendered_content: string
  action_id: string
  action_text: string
}

export type HumanInputFormFilledResponse = {
  task_id: string
  workflow_run_id: string
  event: string
  data: HumanInputFilledFormData
}

export type HumanInputFormTimeoutData = {
  node_id: string
  node_title: string
  expiration_time: number
}

export type HumanInputFormTimeoutResponse = {
  task_id: string
  workflow_run_id: string
  event: string
  data: HumanInputFormTimeoutData
}

export type WorkflowRunHistory = {
  id: string
  version: string
  conversation_id?: string
  message_id?: string
  graph: {
    nodes: Node[]
    edges: Edge[]
    viewport?: Viewport
  }
  inputs: Record<string, string>
  status: WorkflowRunningStatus
  outputs: Record<string, any>
  error?: string
  elapsed_time: number
  total_tokens: number
  total_steps: number
  created_at: number
  finished_at: number
  created_by_account: {
    id: string
    name: string
    email: string
  }
}
export type WorkflowRunHistoryResponse = {
  data: WorkflowRunHistory[]
}

export type NodesDefaultConfigsResponse = {
  type: string
  config: any
}[]

export type ConversationVariableResponse = {
  data: (ConversationVariable & { updated_at: number, created_at: number })[]
  has_more: boolean
  limit: number
  total: number
  page: number
}

export type IterationDurationMap = Record<string, number>
export type LoopDurationMap = Record<string, number>
export type LoopVariableMap = Record<string, any>

export type WorkflowConfigResponse = {
  parallel_depth_limit: number
}

export type PublishWorkflowParams = {
  url: string
  title: string
  releaseNotes: string
}

export type UpdateWorkflowParams = {
  url: string
  title: string
  releaseNotes: string
}

export type PanelProps = {
  getInputVars: (textList: string[]) => InputVar[]
  toVarInputs: (variables: Variable[]) => InputVar[]
  runInputData: Record<string, any>
  runInputDataRef: RefObject<Record<string, any>>
  setRunInputData: (data: Record<string, any>) => void
  runResult: any
}

export type NodeRunResult = NodeTracing

// Var Inspect
export const VarInInspectType = {
  conversation: 'conversation',
  environment: 'env',
  node: 'node',
  system: 'sys',
} as const
export type VarInInspectType = typeof VarInInspectType[keyof typeof VarInInspectType]

type FullContent = {
  size_bytes: number
  download_url: string
}

export type VarInInspect = {
  id: string
  type: VarInInspectType
  name: string
  description: string
  selector: ValueSelector // can get node id from selector[0]
  value_type: VarType
  value: any
  edited: boolean
  visible: boolean
  is_truncated: boolean
  full_content: FullContent
  schemaType?: string
}

export type NodeWithVar = {
  nodeId: string
  nodePayload: CommonNodeType
  nodeType: BlockEnum
  title: string
  vars: VarInInspect[]
  isSingRunRunning?: boolean
  isValueFetched?: boolean
}
