# ModelNet Roadmap

## Current Source Of Truth

- Implementation checklist: `TASKS.md`
- SPI and extension contract: `../architecture/EXTENSIBILITY_SPEC.md`
- Capability semantics: `../architecture/BACKEND_CAPABILITIES.md`
- vLLM token-level work: `../operations/vllm/TOKENLEVEL_VLLM_PLAN.md`
- Historical landing log: `../history/LANDING.md`

## Current Focus

1. Stabilize the raw vLLM `/v1/completions` compatibility path.
2. Probe `/v1/chat/completions` logprob support for chat/instruct models.
3. Choose between `vllm_chat` and `vllm_template` based on that probe.
4. Keep the existing llama.cpp path and SPI contracts unchanged unless a reviewed migration requires it.

## Reading Guide

- New contributor: read this file, then `../architecture/EXTENSION_GUIDE.md`.
- Backend implementer: read `../architecture/EXTENSIBILITY_SPEC.md` and `../architecture/BACKEND_CAPABILITIES.md`.
- Experiment/research user: read `../research/UNDERGRAD_RESEARCH_PLAYBOOK.md` and `../research/PAPER_REPRODUCTION_PLAN.md`.
- Debugging current vLLM workflow: read `../operations/vllm/TOKENLEVEL_VLLM_PLAN.md`.
