# dev/modelnet — DuetNet reproduction tooling

Research scripts that drive the paper "Token-Level Collaborative Reasoning
for Parallel Multi-Models" (Wang et al., 2025) on top of the
`parallel-ensemble` workflow node. **Not** part of the long-term docs
surface — this directory is the working bench for the reproduction
experiments.

## Files

| File | What it does |
|---|---|
| `generate_duet_net_dsls.py` | Emits 8 workflow-mode DSLs (6 dual-model + 1 triple + 1 quad) under `docs/ModelNet/examples/workflow_mode/` from a single template. Idempotent. |
| `duet_net_eval.py` | Calls Dify's `/v1/workflows/run` API for each (workflow × dataset × item), records accuracy / token count / latency, prints a paper-Tables-4-5-style comparison table. |
| `eval.example.yaml` | Sample config for `duet_net_eval.py`. Copy to `eval.yaml` (gitignored) and fill in workflow API keys. |

## End-to-end reproduction recipe

1. **Pre-flight (already done on the user's other server)**:
   - llama.cpp fork exposes raw logits at `POST /completion?post_sampling_probs=false`
   - `LlamaCppBackend` declares `Capability.LOGITS_RAW` when the spec sets `expose_raw_logits: true`
   - `parse_top_probs()` populates `TokenCandidate.logit` and synthesises `prob` via softmax when the wire payload only carries logits
2. **Bring up 4 llama.cpp endpoints** for the reproduction models:
   - q1 → alias `29`: Qwen2.5-3B (q8)
   - q2 → alias `5`: Qwen2.5-7B-Instruct
   - g4 → alias `6`: GLM-4-9B-Chat
   - L3 → alias `2`: Meta-Llama-3.1-8B-Instruct
   Each numeric alias in `api/configs/model_net.yaml` must set `expose_raw_logits: true`.
3. **Generate the DSLs**:
   ```sh
   python dev/modelnet/generate_duet_net_dsls.py
   ```
4. **Import each DSL into Dify** (Studio → Import DSL) → grab the
   workflow's API key for each app.
5. **Configure & run the eval**:
   ```sh
   cp dev/modelnet/eval.example.yaml dev/modelnet/eval.yaml
   # edit eval.yaml to paste workflow API keys
   python dev/modelnet/duet_net_eval.py --config dev/modelnet/eval.yaml
   ```
   Resume on interruption with `--resume` (re-uses `eval_checkpoint.json`).
6. **Inspect the report**:
   - Console: paper-Tables-4-5-style accuracy matrix
   - JSON: `eval_report.json` (per-record + per-(workflow,dataset) summary)
   - Compare against paper figures:
     - Tables 4–5: average accuracy across datasets — DuetNet should beat the
       single-model best by ~1.88–38.50 pp depending on combo
     - Fig. 7: avg per-question token count — DuetNet should be ≥50% lower than
       GaC (paper: 80%; we allow noise)
     - Fig. 11: per-token latency — DuetNet vs slowest single model should be
       within ≤10 ms (paper: 2 ms)

## Datasets

| Name | Source | Prompt template (paper Table 2) | Extractor |
|---|---|---|---|
| `simple_math` | synthesised in-process (`a+b*c+d-e*f`, 0–30 ints) | "What is the answer to {expr}? Please make sure to repeat the answer at the very end of your reply." | `last_integer` |
| `c_eval` | HF `ceval/ceval-exam` (subject=computer_network) | Chinese MCQ; trailing instruction asks to repeat the letter | `last_abcd` |
| `bool_q` | HF `google/boolq` | "Read the following background … please answer the True-false question … reiterate your answer at the end" | `last_bool` |
| `mmlu` | HF `cais/mmlu` (config=all) | "Can you answer … putting the answer in the form (X) at the end" | `paren_abcd` |

The extractors are intentionally permissive — wrong format counts as a
miss, mirroring the paper's evaluation protocol.

## Optional Python deps

The eval script defers `requests`, `yaml`, and `datasets` imports so
`--help` works without them. To run end-to-end:

```sh
pip install requests pyyaml datasets
```

`datasets` lives in HuggingFace; the first run downloads ~1 GB across
the four corpora into `$HF_HOME` (default `~/.cache/huggingface`).

## What this directory is not

- **Not** a long-term docs example. The 8 generated DSLs are; this
  directory is scratch space.
- **Not** a unit-test surface. Algorithm correctness is covered in
  `api/tests/unit_tests/core/workflow/nodes/parallel_ensemble/aggregators/test_token_duet_net.py`.
- **Not** automatically invoked by CI. Run by hand when you want
  numbers; rerun with `--resume` to fill in gaps.
