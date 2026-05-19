# ModelNet Docs

ModelNet documentation is grouped by lifecycle. Start with the active docs, then use architecture, operations, research, or history depending on the task.

## Start Here

- `active/TASKS.md`: current execution checklist and project status.
- `active/ROADMAP.md`: short current-state roadmap and reading guide.
- `architecture/EXTENSIBILITY_SPEC.md`: backend / runner / aggregator SPI contract.
- `architecture/BACKEND_CAPABILITIES.md`: capability and probability-semantics quick reference.
- `operations/vllm/TOKENLEVEL_VLLM_PLAN.md`: active vLLM compatibility and chat-token plan.

## Directory Map

- `active/`: current project status and next-step planning.
- `architecture/`: stable design contracts and extension guidance.
- `operations/`: runtime inventories, hotfix plans, branding work, and operational notes.
- `research/`: paper reproduction plans, student research guide, source papers, model metadata, and PN.py reference code.
- `history/`: superseded development plans and consolidated landing records.
- `examples/`: workflow-mode DSL examples.

## Cleanup Policy

Top-level files should stay limited to this README and durable entry points. New implementation plans should usually live under `operations/<topic>/`; historical landing notes should be appended to `history/LANDING.md` rather than added as new top-level shards.
