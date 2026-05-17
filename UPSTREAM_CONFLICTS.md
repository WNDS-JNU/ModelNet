# Upstream Conflict Report

Last sync point: `fe2f7a8920` (2026-04-30, "refactor(web): migrate short tooltips to dify-ui")
Local HEAD: `ee87f2b741` — 75 commits ahead
Upstream HEAD: `cd4d6f8a22` (`langgenius/dify@main`) — 201 commits ahead of sync

Probe method: real `git merge upstream/main` in a throw-away worktree. Numbers below are exact, not estimated.

**Status.** This is a forward-looking merge checklist, not a current-breakage list. Current `main` still builds and passes tests on its own — verified `2026-05-17` by running:

```bash
uv run --project api pytest \
  api/tests/unit_tests/core/workflow/graph_engine/layers/test_llm_quota.py \
  api/tests/unit_tests/core/workflow/nodes/response_aggregator \
  api/tests/unit_tests/core/workflow/test_node_factory.py
# 104 passed
```

The conflicts below only matter when you next sync `upstream/main` into this branch.

## TL;DR — does following this checklist preserve ModelNet features?

**Yes for runtime; the test file needs a real rewrite (not just stacking).** Verified `2026-05-17` by reading upstream `llm_quota.py`, `node_factory.py`, `workflow_entry.py`, `store/workflow/index.ts`, and `history-slice.ts`:

- ResponseAggregator quota path is preserved — `ResponseAggregatorNodeData.model: ModelConfig` carries the `provider`/`name` fields upstream's new helper reads; the node already writes them into `NodeRunResult.inputs` at `node.py:197`. Add the node type to `_QUOTA_NODE_TYPES` and the quota chain works end-to-end.
- node_factory builders for parallel-ensemble (line 464) and response-aggregator (line 542) survive — every attribute they touch still exists upstream with the same name; concatenation is safe.
- Workflow store undo buffer (zundo `temporal`) only snapshots `workflowHistory`, so dropping the parallel-ensemble trace slice into the inner factory does not bloat the undo stack.
- Docker `build:` blocks must be kept (do not accept the upstream `langgenius/dify-api:1.14.1` image) or the container will not contain any ModelNet code.

**Two things the original checklist understated, now fixed below:**
- `LLMQuotaLayer()` constructor in tests needs `tenant_id="..."` at all 9 call sites — see §1.3.
- The frontend `Shape` union must add `ParallelEnsembleTraceSliceShape` or `pnpm type-check` fails — see §1.7.

---

## 1. Hard conflicts — `git merge` aborted on these

`git merge` cannot auto-resolve. Manual three-way merge required.

### 1.1 `api/core/app/workflow/layers/llm_quota.py` — 3 conflict blocks

**Local change.** ResponseAggregator routed through the quota layer:

- Imports `ModelInstance` and `RESPONSE_AGGREGATOR_NODE_TYPE`.
- `_extract_model_instance` (`api/core/app/workflow/layers/llm_quota.py:113`) adds a `case _ if node.node_type == RESPONSE_AGGREGATOR_NODE_TYPE:` branch that casts the node to `ResponseAggregatorNode` and reads `.model_instance`.

**Upstream change.** Quota layer rewritten end-to-end. Model identity is now read from `node_run_result.inputs["model_provider"]` / `["model_name"]` via two new helpers:

- `_extract_model_identity_from_result_event(result_event) -> tuple[str, str] | None`
- `_extract_model_identity_from_node(node) -> tuple[str, str] | None`

The `_extract_model_instance` function and the `ModelInstance` import are gone. `ensure_llm_quota_available` / `deduct_llm_quota` are replaced by `ensure_llm_quota_available_for_model(tenant_id, provider, model_name)` / `deduct_llm_quota_for_model(...)`.

**Resolution.** Do **not** keep `_extract_model_instance`. The node already emits the right fields — `ResponseAggregatorNode` writes `model_provider` / `model_name` into the success `NodeRunResult.inputs` at `api/core/workflow/nodes/response_aggregator/node.py:197`. So the merge action is:

1. Drop the `_extract_model_instance` branch and its `ModelInstance` import.
2. Add `RESPONSE_AGGREGATOR_NODE_TYPE` to upstream's `_QUOTA_NODE_TYPES` frozenset (or whatever guard the new layer uses).
3. `_extract_model_identity_from_result_event` then covers it without any local-side changes.

**Pre-check coverage verified.** `ResponseAggregatorNodeData.model: ModelConfig` (`api/core/workflow/nodes/response_aggregator/entities.py:142`) and upstream `ModelConfig` exposes `provider: str` + `name: str` — exactly what upstream's `_extract_model_identity_from_node` reads. Both required, no default. So once you add the node type to the guard frozenset, the pre-check path also works.

**Behavior change (informational, won't fire in practice).** Upstream's pre-check is strict — missing model identity aborts the node run, whereas your current layer silently skips quota. For `ResponseAggregatorNodeData` the `model` field is a required pydantic field with no default, so a node config without a model never reaches the quota layer (pydantic rejects it at construction). Worth knowing, no action needed.

**No call-site fix needed.** `workflow_entry.py` is not in your local-changed set; upstream's new `LLMQuotaLayer(tenant_id=...)` constructor calls land via auto-merge.

### 1.2 `api/core/workflow/node_factory.py` — 2 conflict blocks

**Block A — line 3 (imports).** Mechanical: local added `ThreadPoolExecutor` (for parallel-ensemble executor), upstream added `Sequence` (for retriever loader signature). Keep both.

**Block B — line 551.** Local added `_build_response_aggregator_node_init_kwargs` at `api/core/workflow/node_factory.py:542` (injects `model_instance`, `prompt_message_serializer`, `llm_file_saver`). Upstream added `_build_retriever_attachment_loader` + `_build_retriever_segment_access_checker` (LLM-node retriever DI). Parallel-ensemble injection lives just above at `api/core/workflow/node_factory.py:464` — both local helpers must survive the merge.

**Resolution.** Two non-overlapping helpers — concatenate them. **Do not** add `retriever_attachment_loader=...` to the response-aggregator kwargs dict during this merge — `ResponseAggregatorNode.__init__` does not accept that parameter and the aggregator has no retriever context, so passing it would crash node construction. The kwarg becomes relevant only if a future feature adds retrieval-attachment support to the response aggregator; track that as a separate change, not part of the upstream merge.

**Dependencies still valid upstream.** Every attribute the local `_build_response_aggregator_node_init_kwargs` reads — `self._llm_credentials_provider`, `self._llm_model_factory`, `self._prompt_message_serializer`, `self._llm_file_saver`, plus the imported `DifyPreparedLLM` and `fetch_model_config` — still exists under the same name in upstream `api/core/workflow/node_factory.py` (verified by grep). The builder runs untouched after the merge.

### 1.3 `api/tests/unit_tests/core/workflow/graph_engine/layers/test_llm_quota.py` — 2 conflict blocks

Companion to 1.1. Upstream rewrote every test in this file around the new `_for_model` API and removed the `ModelInstance` import. Your `test_response_aggregator_synthesis_quota_precheck_passes_without_abort` still patches `ensure_llm_quota_available` and constructs `model_instance` mocks — both names no longer exist.

**Resolution. Real rewrite, not stacking.** Three concrete edits:

1. **All 9 `LLMQuotaLayer()` calls** in this file need `tenant_id="test-tenant"` (upstream constructor now requires it; verified at upstream `workflow_entry.py:115` / `:216` which call `LLMQuotaLayer(tenant_id=...)`).
2. **Drop the `ModelInstance` import** — the symbol still exists in `core.model_manager`, but the new quota path doesn't use it, and your tests built on top of it become dead code.
3. **Rewrite `test_response_aggregator_synthesis_quota_precheck_passes_without_abort`** to use `_build_node_data(model=_build_public_model_identity(provider=..., model_name=...))` (or whatever helper upstream introduces) and patch `ensure_llm_quota_available_for_model` instead of `ensure_llm_quota_available`. Use any upstream LLM-node quota test as a template.

### 1.4 `api/tests/unit_tests/core/workflow/test_node_factory.py` — 2 conflict blocks

**Block A — line 468 (factory fixture).** You added `factory._parallel_ensemble_executor = None`; upstream added `factory._build_retriever_attachment_loader = MagicMock(return_value=sentinel.retriever_attachment_loader)`. Keep both lines.

**Block B — line 813.** You appended `test_creates_parallel_ensemble_node`; upstream appended different new tests. Just stack both.

### 1.5 `api/uv.lock` — 2 conflict blocks

Don't hand-merge. After resolving `api/pyproject.toml`:

```bash
git checkout --theirs api/uv.lock
uv lock --project api
```

### 1.6 `docker/docker-compose.yaml` — 3 conflict blocks (worker, worker_beat, web)

Upstream extracted `&shared-worker-config` / `&shared-worker-beat-config` YAML anchors and bumped image to `langgenius/dify-api:1.14.1` / `langgenius/dify-web:1.14.1`. You kept `build: ../api` + `image: ...:1.14.0-local` because you want to build from local source.

**Resolution. This one is load-bearing — do not accept upstream sides blindly.** ModelNet code (parallel-ensemble, data-loader, response-aggregator, token-model-source, etc.) lives only in your local `api/` tree. If the compose file switches to `langgenius/dify-api:1.14.1` you will end up running a container that does not contain any of your custom nodes. Concrete plan:

- **Keep `build: ../api` + `build: ..` (web)** blocks as-is.
- Bump local image tag `1.14.0-local` → `1.14.1-local` to track upstream version.
- Optionally pull in upstream's `*-shared-config` anchors from elsewhere in the file so future bumps are a one-line change.

### 1.7 `web/app/components/workflow/store/workflow/index.ts` — 1 conflict block

You added `createParallelEnsembleTraceSlice` to the slice list at `web/app/components/workflow/store/workflow/index.ts:90`. Upstream wrapped the entire store with `temporal<Shape, [], [], WorkflowHistoryTemporalState>(...)` middleware (undo/redo via zundo) and changed the return cast to `as WorkflowStoreApi`.

**Resolution.** Two edits, both required:

1. **Slot the slice line** into upstream's `temporal(...)` inner factory:
   ```ts
   return createStore<Shape>()(
     temporal<Shape, [], [], WorkflowHistoryTemporalState>(
       (...args) => ({
         ...createChatVariableSlice(...args),
         // ... existing upstream slices ...
         ...createLayoutSlice(...args),
         ...createParallelEnsembleTraceSlice(...args),  // <-- your line here
         ...(injectWorkflowStoreSliceFn?.(...args) || {} as SliceFromInjection),
       }),
       { partialize: getWorkflowHistoryTemporalState, equality: isWorkflowHistoryTemporalStateEqual },
     ),
   ) as WorkflowStoreApi
   ```
2. **Extend the `Shape` type union** to include `ParallelEnsembleTraceSliceShape` — upstream's `Shape` lists 14 slice shapes but does not know about yours, so `pnpm type-check` will fail until you add `& ParallelEnsembleTraceSliceShape` to the union.

**Undo buffer is safe.** Upstream defines `WorkflowHistoryTemporalState = Pick<HistorySliceShape, 'workflowHistory'>`, so zundo only snapshots `workflowHistory`. Your trace state is never copied into the undo buffer — no memory bloat from long token-level traces.

---

## 2. Silent conflicts — `Auto-merging` succeeded, but both sides touched the file

These files merged cleanly at the text level. The risk is **semantic**: your additions assume the surrounding code shape that existed before the upstream changes. Skim each for nearby upstream edits.

| File | Why to look |
|---|---|
| `.gitignore` | Low risk. Just confirm both sets of ignores landed. |
| `api/Dockerfile` | Check if upstream changed base image / python version / system deps you depend on. |
| `api/configs/feature/__init__.py` | You added modelnet config block; upstream added new feature flags. Verify both registered. |
| `api/controllers/console/__init__.py` | You registered `workflow_probe_model`, `aggregators`, `local_models`, `runners` blueprints; upstream likely added more route registrations. Check no name collision. |
| `api/pyproject.toml` | Dependency changes from both sides. Regenerate `uv.lock` after merge (see 1.5). |
| `web/app/components/workflow-app/hooks/use-workflow-run.ts` | |
| `web/app/components/workflow-app/hooks/use-workflow-run-callbacks.ts` | |
| `web/app/components/workflow-app/hooks/__tests__/use-workflow-run.spec.ts` | |
| `web/app/components/workflow-app/hooks/__tests__/use-workflow-run-callbacks.spec.ts` | |
| `web/app/components/workflow/constants.ts` | Your node-type enums (`PARALLEL_ENSEMBLE`, `RESPONSE_AGGREGATOR`, `DATA_LOADER`, `TOKEN_MODEL_SOURCE`, …) live here. Upstream may have reshuffled the export structure. |
| `web/app/components/workflow/run/node.tsx` | Node-trace rendering. Check whether upstream changed the trace component contract. |
| `web/app/components/workflow/types.ts` | Same as constants — node-type union. |
| `web/contract/router.ts` | TanStack-Query contract surface. Verify your contract entries (`workflowProbeModel`, etc.) still match the upstream router shape. |
| `web/i18n/en-US/workflow.json` | Just a JSON merge. Check no duplicate keys. |
| `web/i18n/zh-Hans/workflow.json` | Same. |

---

## 3. Recommended merge order

1. **Lock files first.** `git checkout --theirs api/uv.lock && uv lock --project api`.
2. **Quota path (1.1 + 1.3).** Hardest semantically — touch ResponseAggregator to write `model_provider/model_name` into `node_run_result.inputs`, drop the `_extract_model_instance` branch, rewrite the test.
3. **node_factory (1.2 + 1.4).** Mostly stacking, but verify retriever-loader injection requirement for response-aggregator's LLM path.
4. **Store + compose (1.6 + 1.7).** Pure structural merges, no semantic redesign.
5. **i18n + types + constants (silent conflicts).** Skim and stack.
6. **Validate.**
   ```bash
   uv run --project api pytest api/tests/unit_tests/core/workflow/
   cd web && pnpm type-check && pnpm lint
   ```

---

## 4. Out of scope

- Upstream changed ~2538 files since the sync point; only the 23 above intersect with your 268 locally-changed files. Anything in upstream's other ~2515 files merges with zero attention.
- Plugin / marketplace / dataset / RAG paths are untouched on your side, so upstream's churn there lands cleanly.
