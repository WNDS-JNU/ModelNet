# dev/modelnet — multi-model collaborative inference reproduction tooling

Working bench for two paper reproductions on top of the workflow nodes
this fork ships (`parallel-ensemble`, `token-model-source`,
`response-aggregator`):

* **DuetNet** (Wang et al., 2025) — token-level parallel ensemble.
  6 dual-model + 1 triple + 1 quad combo, datasets SimpleMath / C-Eval
  (computer_network) / BoolQ / MMLU. Tables 4–5 / Fig. 7 / Fig. 11.
* **AI-ModelNet** (Li et al., 2025) — 4 paradigms (SI / PI / S2P / P2S)
  × 13 paths × 3 paper datasets (GSM8K, C-Eval multi-subject,
  HendrycksMATH). Tables 4 / 6-7. Framing in
  [`docs/ModelNet/research/UNDERGRAD_RESEARCH_PLAYBOOK.md`](../../docs/ModelNet/research/UNDERGRAD_RESEARCH_PLAYBOOK.md)
  §6 (direction D) and the staged execution plan in
  [`docs/ModelNet/research/PAPER_REPRODUCTION_PLAN.md`](../../docs/ModelNet/research/PAPER_REPRODUCTION_PLAN.md).

This directory is **not** part of the long-term docs surface — it is
research scratch space.

## Files

| File | What it does |
|---|---|
| `generate_duet_net_dsls.py` | Emits 8 DuetNet workflow-mode DSLs (6 dual + 1 triple + 1 quad) under `docs/ModelNet/examples/workflow_mode/duet_net_*.yml` from a single template. Idempotent. |
| `generate_paper_dsls.py` | Emits 13 AI-ModelNet paper DSLs (`paper_*.yml`) covering 4 paradigms × 3 model roles {Q=5, D=22, Y=6}. Idempotent. SI uses standard `llm` chains; PI/S2P/P2S use `parallel-ensemble` (`sum_score`) for every paper parallel stage. |
| `duet_net_eval.py` | Calls Dify's `/v1/workflows/run` API for each (workflow × dataset × item) and records accuracy / token count / latency. Drives both reproductions; the script does not care what is inside each workflow — it only sees the API contract. |
| `eval.example.yaml` | Sample config for the DuetNet 8-DSL reproduction. |
| `eval.paper.example.yaml` | Sample config for the AI-ModelNet paper reproduction (13 paths × paper datasets). |

## DuetNet end-to-end recipe

1. **Pre-flight**:
   - Run a llama.cpp fork that exposes raw logits when `/completion` receives `post_sampling_probs=false`
   - Keep `expose_raw_logits: true` on the matching `model_net.yaml` aliases; `LlamaCppBackend` then declares `Capability.LOGITS_RAW`
   - The fork's `top_probs` items must carry `logit` or `raw_logit`; the adapter fills `TokenCandidate.logit` and synthesises `prob` via softmax
2. **Bring up 4 llama.cpp endpoints** for the DuetNet models:
   - q1 → alias `29`: Qwen2.5-3B (q8)
   - q2 → alias `5`: Qwen2.5-7B-Instruct
   - g4 → alias `6`: GLM-4-9B-Chat
   - L3 → alias `2`: Meta-Llama-3.1-8B-Instruct

   Each numeric alias in `api/configs/model_net.yaml` must set `expose_raw_logits: true`.
3. **Generate the DSLs**:
   ```sh
   uv run --project api python dev/modelnet/generate_duet_net_dsls.py
   ```
4. **Import each DSL into Dify** (Studio → Import DSL) → grab the workflow's API key for each app.
5. **Configure & run the eval**:
   ```sh
   cp dev/modelnet/eval.example.yaml dev/modelnet/eval.yaml
   # edit eval.yaml to paste workflow API keys
   uv run --project api python dev/modelnet/duet_net_eval.py --config dev/modelnet/eval.yaml
   ```
   Resume on interruption with `--resume` (re-uses `eval_checkpoint.json`).
6. **Inspect the report**:
   - Console: paper-Tables-4-5-style accuracy matrix
   - JSON: `eval_report.json` (per-record + per-(workflow, dataset) summary)
   - Compare against paper figures:
     - Tables 4–5: average accuracy across datasets — DuetNet should beat the
       single-model best by ~1.88–38.50 pp depending on combo
     - Fig. 7: avg per-question token count — DuetNet should be ≥50% lower than
       GaC (paper: 80%; we allow noise)
     - Fig. 11: per-token latency — DuetNet vs slowest single model should be
       within ≤10 ms (paper: 2 ms)

## AI-ModelNet paper reproduction recipe

> Read [`UNDERGRAD_RESEARCH_PLAYBOOK.md`](../../docs/ModelNet/research/UNDERGRAD_RESEARCH_PLAYBOOK.md)
> §6 (direction D) and [`PAPER_REPRODUCTION_PLAN.md`](../../docs/ModelNet/research/PAPER_REPRODUCTION_PLAN.md)
> first — together they motivate the model picks, dataset picks, and
> the Stage A → Stage B execution order this section assumes.

1. **Bring up 3 llama.cpp endpoints** for the paper models:
   - **Q** → alias `5`: Qwen2.5-7B-Instruct (`qwen25-7b-instruct-q5km`)
   - **D** → alias `22`: Qwen3-8B-BF16 (`qwen3-8b-bf16`, reachable thinking-model stand-in for the unavailable DeepSeek endpoint)
   - **Y** → alias `6`: GLM-4-9B-Chat (`glm-4-9b-chat-q4k`, replacing the unavailable Yi-1.5-9B per `PAPER_REPRODUCTION_PLAN.md` §2)

   The PI paradigm reads aliases directly from `model_net.yaml`. SI / S2P / P2S use Dify's standard `llm` node, which does **not** read `model_net.yaml`. Pre-configure those 3 endpoints once: Dify Web → Settings → Model Provider → install OpenAI-Compatible API plugin → add 3 entries pointing at the same llama.cpp URLs.
2. **Generate the paper DSLs**:
   ```sh
   uv run --project api python dev/modelnet/generate_paper_dsls.py
   ```
   Outputs the 13 paths under `docs/ModelNet/examples/workflow_mode/paper_*.yml` (SI×6, PI×1, S2P×3, P2S×3). Idempotent.

   * **PI** — token-level parallel ensemble (`parallel-ensemble` + `sum_score`).
   * **SI** — serial chain of standard `llm` nodes; each step refines the previous reply.
   * **S2P** — `llm` → 2× `llm` parallel → `response-aggregator` (`majority_vote` with a permissive default regex covering MCQ letters, booleans, integers, and `\boxed{...}`). Edit the DSL via Studio if your prompt template forces a different answer format.
   * **P2S** — 2× `llm` parallel → `response-aggregator` (`concat`) → `llm` synthesizer.
3. **Import each DSL into Dify** and grab API keys.
4. **Configure & smoke-test before the full run**:
   ```sh
   cp dev/modelnet/eval.paper.example.yaml dev/modelnet/eval.paper.yaml
   # paste API keys
   # Smoke 5 GSM8K items end-to-end before committing to 3900 calls:
   uv run --project api python dev/modelnet/duet_net_eval.py \
       --config dev/modelnet/eval.paper.yaml \
       --datasets gsm8k --n 5
   ```
5. **Run the full reproduction**:
   ```sh
   uv run --project api python dev/modelnet/duet_net_eval.py \
       --config dev/modelnet/eval.paper.yaml
   ```
   13 workflows × 3 datasets × 100 samples = **3900 calls**. `--resume` re-uses `dev/modelnet/checkpoints/paper.json`.
6. **Inspect the report** at `dev/modelnet/reports/paper.json`. Compare against paper Tables 4 / 6-7.

## Datasets

| Name | Source | Used by | Prompt template | Extractor |
|---|---|---|---|---|
| `simple_math` | synthesised in-process (`a+b*c+d-e*f`, 0–30 ints) | DuetNet | "What is the answer to {expr}? Please make sure to repeat the answer at the very end of your reply." | `last_integer` |
| `c_eval` | HF `ceval/ceval-exam`, multi-subject | DuetNet (`computer_network`) / AI-ModelNet (broader pool) | Chinese MCQ; trailing instruction asks to repeat the letter | `last_abcd` |
| `bool_q` | HF `google/boolq` | DuetNet | "Read the following background … please answer the True-false question … reiterate your answer at the end" | `last_bool` |
| `mmlu` | HF `cais/mmlu` (config=all) | DuetNet | "Can you answer … putting the answer in the form (X) at the end" | `paren_abcd` |
| `gsm8k` | HF `gsm8k` (config=main, split=test) | AI-ModelNet | "{question}\nReason step by step, and put the final integer answer at the end of your reply." | `gsm8k_last_int` |
| `math` | HF `hendrycks/competition_math` (split=test) | AI-ModelNet | "{problem}\nReason step by step. Put the final answer in `\boxed{}`." | `math_boxed` (sympy fallback if installed) |

The extractors are intentionally permissive — wrong format counts as a miss, mirroring the paper's evaluation protocol.

## CLI flags

```sh
duet_net_eval.py
    --config CONFIG          path to eval.yaml (required)
    --resume                 skip items already in the checkpoint
    --checkpoint-every N     flush checkpoint every N items (default: 10)
    --datasets a,b,c         restrict to a comma-separated subset of dataset names from the config
    --n N                    override every dataset's `n` (sample count)
    --quiet                  WARNING-level logging only
```

`--datasets` and `--n` are designed for smoke runs without rewriting the config — handy when first wiring a new workflow into Dify.

## Optional Python deps

The eval script defers `requests`, `yaml`, and `datasets` imports so `--help` works without them. To run end-to-end:

```sh
pip install requests pyyaml datasets
# Optional — symbolic-equivalence answer matching for HendrycksMATH:
pip install sympy antlr4-python3-runtime
```

Without `sympy`, `math_boxed` answer matching falls back to normalised string comparison, which still catches most clean-formatted gold answers but undercounts equivalence cases like `1/2 == 0.5`.

`datasets` lives in HuggingFace; the first run downloads ~1 GB across the four DuetNet corpora plus ~250 MB for GSM8K + HendrycksMATH into `$HF_HOME` (default `~/.cache/huggingface`).

## What this directory is not

- **Not** a long-term docs example. The 8 generated DuetNet DSLs and (eventually) the 13 paper DSLs are; this directory is scratch space.
- **Not** a unit-test surface. Algorithm correctness is covered in
  `api/tests/unit_tests/core/workflow/nodes/parallel_ensemble/aggregators/test_token_duet_net.py`.
- **Not** automatically invoked by CI. Run by hand when you want numbers; rerun with `--resume` to fill in gaps.
