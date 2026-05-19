# ModelNet Docs

This directory contains the ModelNet design notes, implementation task list, landing records, and runtime/debugging plans for the Dify ModelNet workflow work.

## Start Here

- `TASKS.md`: execution checklist and current project status.
- `LANDING.md`: consolidated landing record for all old `P*_LANDING.md` phase shards.
- `TOKENLEVEL_VLLM_COMPAT_PLAN.md`: current hotfix plan for TokenLevel vLLM backend compatibility.
- `EXTENSIBILITY_SPEC.md`: backend / runner / aggregator SPI contract.
- `BACKEND_CAPABILITIES.md`: backend capability and probability semantics contract.

## Planning Docs

- `DEVELOPMENT_PLAN.md`: original v2 development plan.
- `DEVELOPMENT_PLAN_v3.md`: v3 plan for response weighting, token source relocation, and token-model-source node work.
- `EXTENSION_GUIDE.md`: implementation guide for extending ModelNet.
- `PAPER_REPRODUCTION_PLAN.md`: paper reproduction plan.
- `UNDERGRAD_RESEARCH_PLAYBOOK.md`: research playbook.

## Operational Notes

- `DUET_NET_TRACE_PUSH_FIX_PLAN.md`: DuetNet trace push fix plan.
- `MODELNET_LOCAL_CHAT_TEMPLATES.md`: local chat template notes.
- `BRANDING_REBRAND_PLAN.md`: naming and branding cleanup plan.

## Data And Examples

- `examples/`: workflow-mode YAML examples.
- `model_info.json` / `model_info.xlsx`: model metadata.
- `PN.py`: original PN.py reference script.
- PDFs: source papers and reference material.

## Cleanup Policy

The old phase landing shards `P1.*_LANDING.md`, `P2.*_LANDING.md`, `P3.A.*_LANDING.md`, and `P3.B.*_LANDING.md` have been merged into `LANDING.md` and removed as standalone files.

`SPIKE_GRAPHON.md` was merged into the Phase 0 section of `TASKS.md` and removed as a standalone file. `DEPLOYMENT_PORTS.md` was removed because it described an old local Docker deployment under `/home/xianghe/temp/dify`, not the current `/home/duxianghe/dify` runtime.

When adding new landing notes:

- Prefer appending or regenerating `LANDING.md` instead of creating another phase shard.
- Keep historical source filenames inside `LANDING.md` as provenance markers.
- Update this README if a new top-level document becomes an entry point.
