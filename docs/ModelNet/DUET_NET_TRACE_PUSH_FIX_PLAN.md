# duet_net_main Aggregated Trace Frontend Delivery Fix Plan

Recorded on: 2026-05-18

## Current Investigation State

Remote repository state:

- Repository path: `/home/duxianghe/dify`
- Branch: `main`
- HEAD at investigation time: `0cbc397f0 docs(modelnet): update repository URL in branding plan`
- `main` matched `origin/main` and the worktree was clean before this document was added.

Latest successful workflow run found in PostgreSQL:

- `workflow_run_id`: `64c81b9d-7639-42e1-bb07-c68cff610cab`
- `app_id`: `32db99d6-6c42-45ae-8258-426b7183ef5f`
- `status`: `succeeded`
- `created_at`: `2026-05-18 04:57:22.459282`

`ensemble` node in that run:

- `node_id`: `ensemble`
- `node_type`: `parallel-ensemble`
- `status`: `succeeded`
- `created_at`: `2026-05-18 04:57:22.587011`
- The database row's `process_data` already contains `ensemble_trace`.
- `ensemble_trace.aggregator_name` is `duet_net`.

Conclusion: the backend generated and persisted the DuetNet aggregated trace. The trace was not lost during aggregation or node finalization.

Relevant `docs/ModelNet/examples/workflow_mode/duet_net_main.yml` settings:

```yaml
aggregator_name: duet_net
diagnostics:
  enable_trace_stream: false
  include_aggregator_reasoning: true
  include_logits: true
  include_model_outputs: false
  include_per_backend_errors: true
  include_response_timings: true
  include_think_trace: false
  include_token_candidates: true
  max_trace_tokens: 2000
  storage: metadata
```

This means:

- Aggregator reasoning, token candidates, and logits are included in the final trace.
- The trace is stored at `process_data.ensemble_trace`.
- Real-time per-step trace streaming is disabled, so the run will not emit `parallel_ensemble_trace_step` over the `agent_log` SSE channel while it is running.

## Current Code Behavior

Backend behavior:

- `api/core/workflow/nodes/parallel_ensemble/node.py::_finalize_outputs()` calls `trace.finalize(...)` and builds the complete `trace_data` object.
- When `diagnostics.storage == "metadata"`, the backend writes the trace to `NodeRunResult.process_data["ensemble_trace"]`.
- When `diagnostics.storage == "inline"`, the backend writes the trace to `outputs["trace"]`.

Real-time streaming behavior:

- `api/core/workflow/nodes/parallel_ensemble/runners/token_step.py` only yields `TraceStepEvent` when `trace.config.enable_trace_stream` is `true`.
- `api/core/workflow/nodes/parallel_ensemble/node.py` translates `TraceStepEvent` to `AgentLogEvent`.
- That event uses `metadata.kind = "parallel_ensemble_trace_step"` so the frontend can distinguish parallel-ensemble trace steps from normal agent logs.

Frontend behavior:

- `web/service/base.ts` only calls `onParallelEnsembleTraceStep` when it receives an `agent_log` event whose `data.metadata.kind` equals `PARALLEL_ENSEMBLE_TRACE_STEP_KIND`.
- `web/app/components/workflow/hooks/use-workflow-run-event/use-workflow-parallel-ensemble-trace.ts` appends those real-time steps to the workflow store.
- `web/app/components/workflow/store/workflow/parallel-ensemble-trace-slice.ts` currently supports appending real-time step events only.
- `web/app/components/workflow/hooks/use-workflow-run-event/use-workflow-node-finished.ts` merges node-finished tracing data, but it does not hydrate the dedicated trace store from `node_finished.data.process_data.ensemble_trace`.

## Root Cause

`duet_net_main` explicitly sets `enable_trace_stream: false`, so the absence of real-time trace step SSE events during execution is expected.

The missing behavior is final-trace hydration. After a successful node finish, the aggregated trace is available under `node_finished.data.process_data.ensemble_trace`, but the frontend does not copy `ensemble_trace.token_trace` into `parallelEnsembleTraceByNodeId`. Therefore the dedicated trace panel depends only on live step events. When live streaming is disabled, the panel remains empty after success even though the final trace exists.

## Fix Plan

### 1. Extend the frontend trace store

Target file:

- `web/app/components/workflow/store/workflow/parallel-ensemble-trace-slice.ts`

Add a method such as:

```ts
hydrateParallelEnsembleTraceFromNodeFinished: (data: NodeTracing) => void
```

Recommended logic:

- Only handle `data.node_type === BlockEnum.ParallelEnsemble`.
- Prefer `data.process_data?.ensemble_trace`.
- Fall back to `data.outputs?.trace` for `diagnostics.storage == "inline"`.
- Return early if no trace exists or `token_trace` is not an array.
- Convert each `token_trace` entry to the existing `ParallelEnsembleTraceStep` shape.
- Synthesize a stable `message_id` using `${data.id}:trace:${step.step}`.
- Write the list into `parallelEnsembleTraceByNodeId[data.node_id]`.
- Preserve `per_model`, `per_model_errors`, and `aggregator_reasoning`, including DuetNet fields such as `per_token_logit`, `winner_per_model`, and `topT_candidates`.

### 2. Hydrate on node finish

Target file:

- `web/app/components/workflow/hooks/use-workflow-run-event/use-workflow-node-finished.ts`

Inside `handleWorkflowNodeFinished(params)`, after extracting `data`, call:

```ts
workflowStore.getState().hydrateParallelEnsembleTraceFromNodeFinished(data)
```

This can run before or after the tracing merge. It only updates the trace slice and does not depend on React Flow node state.

### 3. Reuse the existing UI

Do not add a second trace UI path. Continue using:

- `web/app/components/workflow/run/parallel-ensemble-trace/parallel-ensemble-trace-trigger.tsx`
- `web/app/components/workflow/run/parallel-ensemble-trace/parallel-ensemble-trace-step.tsx`

Both real-time trace steps and final-trace hydration should populate the same `parallelEnsembleTraceByNodeId` store.

### 4. Add focused tests

Recommended tests:

- `web/app/components/workflow/store/workflow/__tests__/parallel-ensemble-trace-slice.spec.ts`
  - Build a `NodeTracing` object with `process_data.ensemble_trace.token_trace`.
  - Assert that `parallelEnsembleTraceByNodeId["ensemble"]` is hydrated.
  - Assert that DuetNet `aggregator_reasoning.per_token_logit` and related fields are preserved.
  - Cover the `outputs.trace` fallback path.

- `web/app/components/workflow/hooks/use-workflow-run-event/__tests__/use-workflow-node-finished.spec.ts`
  - Build a `node_finished` response for a `parallel-ensemble` node.
  - Assert that `handleWorkflowNodeFinished` hydrates the final trace store.

### 5. Optional real-time streaming change

If live display during execution is required, update the workflow DSL:

```yaml
diagnostics:
  enable_trace_stream: true
```

This should be optional. With the current `duet_net_main` settings, `include_token_candidates`, `include_logits`, and `include_aggregator_reasoning` can make the SSE payload large on long generations. The safer default fix is final-trace hydration after node finish.

## Acceptance Criteria

- With `duet_net_main` keeping `enable_trace_stream: false`, a successful run shows token trace in the dedicated trace panel after the `parallel-ensemble` node finishes.
- The hydrated rows include DuetNet aggregation reasoning such as `per_token_logit`, `winner_per_model`, and `topT_candidates`.
- With `enable_trace_stream: true`, the existing real-time step stream still works.
- Multiple `parallel-ensemble` nodes in one run remain isolated by `node_id`.
- Re-processing the same node-finished payload does not create duplicate steps.

## Risks And Notes

- `process_data` is passed through the backend response truncation path. A large `token_trace` can be truncated before it reaches the frontend.
- The current example uses `max_trace_tokens: 2000` while including logits and token candidates. Consider lowering it to `200` or `500` if payload size becomes a practical issue.
- If the product requires reliable full-trace retrieval for long runs, add a dedicated final trace SSE event or trace detail API instead of relying on ordinary `process_data`.
