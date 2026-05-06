# PAPER_REPRODUCTION_PLAN

**Paper**: Multi-model serial and parallel collaborative inference in AI-ModelNet
**Source**: `docs/ModelNet/Multi-model serial and parallel collaborative inference in AI-ModelNet.pdf`
**Drafted**: 2026-05-05
**Status**: Plan v0.1 — pending implementation

---

## 1. Context

论文提出 4 种多模型协同推理范式（**SI** 串 / **PI** 并 / **S2P** 串→并 / **P2S** 并→串），在 GSM8K / CEVAL / Mathematics（HendrycksMATH）三个数据集、Qwen-2.5-7B / DeepSeek-R1-Distill-Qwen-7B / Yi-1.5-9B 三个 7-9B 模型上测试。

每个数据集**随机抽 100 题**（论文原文）。表 4-5 是各范式代表路径，**表 6-7 是路径维度展开**：例如 Table 7 出现 `Qwen-[Ds-Yi]` 这种 1 串 + 2 并 = 3 调用 的分配式拓扑。

本仓库已沉淀大量基础设施（`response_aggregator` + `parallel_ensemble` + `token_model_source` + 9 个 PI DSL 模板 + 完整 eval harness `dev/modelnet/duet_net_eval.py`）。本计划目标：**最大复用、最小新代码**，分两阶段产出论文表 4 / 表 6-7 的全部 metrics。

---

## 2. 已确认决策

| 决策点 | 选择 | 备注 |
|---|---|---|
| S2P Stage 2（response-level vote） | 加 `majority_vote` 策略（~80 LOC） | 与论文 Fig 5a response-level vote 一致 |
| Yi-1.5-9B 替代（model_net.yaml 未注册） | `glm-4-9b-chat-q4k` (id 6) | 9B 中文友好 normal 模式 |
| Mathematics 数据集解读 | HendrycksMATH (`hendrycks/competition_math`) | LaTeX `\boxed{...}` 抽答 |
| 样本量 | n = 100 / 数据集 | 与论文严格一致 |
| 实施顺序 | Stage A（MVP，表 4） → Stage B（路径矩阵，表 6-7） | 用户建议的两段切分 |

---

## 3. 已核实的实施事实（消除踩坑点）

| # | 事实 | 来源 |
|---|------|---|
| 1 | `entities.py:134` 锁了 `strategy_name: Literal["concat"]`，必须扩到 `Literal["concat", "majority_vote"]`，否则 DSL 写 `majority_vote` 会被 Pydantic 拒掉 | `api/core/workflow/nodes/response_aggregator/entities.py:134` |
| 2 | 前端三处静态白名单需同步：`ResponseStrategyName` 类型、`RESPONSE_STRATEGY_NAMES` / `RESPONSE_STRATEGY_META`、`ALLOWED_KEYS_BY_STRATEGY` | `web/.../response-aggregator/types.ts:6,8,45`；`default.ts:22` |
| 3 | `default.ts:155-184` 还有针对 `concat` 的字段类型校验块；新策略最好补一个对称的 `majority_vote` 校验块 | `web/.../response-aggregator/default.ts:155` |
| 4 | i18n 文件是 **`workflow.json`** 不是 `.ts` | `web/i18n/en-US/workflow.json`、`web/i18n/zh-Hans/workflow.json` |
| 5 | 标准 `llm` 节点不读 `model_net.yaml`（只服务 `token-model-source` + `parallel-ensemble`）；SI/P2S/S2P 用普通 LLM 节点必须把 3 个 llama.cpp 端点先配成 Dify model provider | model_net.yaml schema |
| 6 | `model_net.yaml` 当前 alias 是 `"5"`、`"27"`、`"6"`（旧 q2/g4 已弃用），新 PI DSL 的 `model_alias` 字段必须按当前 alias 写 | `api/configs/model_net.yaml:11,228,57` |
| 7 | eval 配置字段：`request_timeout_s` / `checkpoint_path` / `report_path`（不是 `timeout` / `checkpoint` / `report`） | `dev/modelnet/duet_net_eval.py:299-307` |
| 8 | `_items_for_dataset()` 当前只给 `simple_math` 传 `seed`；`_c_eval` 硬编码 `computer_network` 单学科，不支持 subjects/seed 参数 | `duet_net_eval.py:367-374, 111-115` |
| 9 | 论文样本量是 **n=100**（不是 500） | 论文原文 |
| 10 | Table 6-7 路径维度：S2P/P2S 是"3 模型分配式" 1串+2并 / 2并+1串 = **3 次调用**，不是"2串+3并"或"3并+1串" | 论文表 7 + 用户确认 |

---

## 4. Stage A — MVP（复现论文表 4）

目标：4 范式 × 3 数据集 × 100 样本 = 1200 次 workflow 调用，产出 12 组 (paradigm, dataset) accuracy / latency / token cost。

### 4.1 后端：新增 `majority_vote` response 策略

**新文件** `api/core/workflow/nodes/response_aggregator/strategies/majority_vote.py`（仿 `concat.py`，约 80 行）：

- `_MajorityVoteConfig`（pydantic, `extra="forbid"`）：
  - `answer_extract_regex: str = ""` — 可选，从每个 verifier 文本抽答案做 vote key；空则用全文做 key
  - `case_sensitive: bool = False`
  - `weighted: bool = True` — 用 `context.weights` 加权计票
  - `tie_break: Literal["first", "longest"] = "first"`
- `MajorityVoteStrategy.aggregate()`:
  1. 对每个 signal 提取 vote_key（regex 抽 / 全文 normalize）
  2. `vote_counts[key] += weights[source_id]`（或 1.0）
  3. argmax + tie_break 解决并列
  4. `text` 取首次 vote_key 命中的原始文本（保 LaTeX/格式）
  5. `metadata`: `strategy="majority_vote"`, `vote_counts`, `winner_key`, `contributions`
- `ui_schema`：4 字段（text_input / switch / switch / select）
- `i18n_key_prefix = "nodes.responseAggregator.majorityVote"`
- `@register("majority_vote")` 装饰

**修改** `api/core/workflow/nodes/response_aggregator/strategies/__init__.py`：+1 import / +1 export

**修改** `api/core/workflow/nodes/response_aggregator/entities.py:134`：
```python
strategy_name: Literal["concat", "majority_vote"] = "concat"
```

**新增测试** `api/tests/unit_tests/core/workflow/nodes/response_aggregator/test_majority_vote.py`（仿 `test_strategies.py`）：
- 全文 vote 多数胜
- regex 抽取 + 大小写归一化
- 加权 tie 处理
- `tie_break = "first" / "longest"` 行为

### 4.2 前端：majority_vote 接线

**修改** `web/app/components/workflow/nodes/response-aggregator/types.ts`：
```ts
export type ResponseStrategyName = 'concat' | 'majority_vote'
export const RESPONSE_STRATEGY_NAMES = ['concat', 'majority_vote']
// + RESPONSE_STRATEGY_META.majority_vote 一项（i18n_key_prefix + ui_schema）
// + 可选 export type MajorityVoteConfig
```

**修改** `web/app/components/workflow/nodes/response-aggregator/default.ts`：
- `ALLOWED_KEYS_BY_STRATEGY.majority_vote = ['answer_extract_regex', 'case_sensitive', 'weighted', 'tie_break']`
- 在 `if (strategy_name === 'concat')` 校验块下面补对称的 `if (strategy_name === 'majority_vote')` 块（4 字段类型校验，错误消息走 i18n）

**修改** `web/i18n/en-US/workflow.json` + `web/i18n/zh-Hans/workflow.json`：
- 在 `nodes.responseAggregator` 下加 `majorityVote` 子树（label / description / 4 字段名 + tooltip）
- 加 4 条 `errorMsg.*` 翻译（regex / case / weighted / tieBreak 各自的 invalid 消息）

> ⚠️ 不需要改 `formatItem` / `getNodeOutputVars`（那两个 switch 是 response-aggregator 节点自己的输出变量，不是策略下拉）

### 4.3 Eval harness 扩展

**修改** `dev/modelnet/duet_net_eval.py`：

1. **加 GSM8K loader** `_gsm8k(n, seed)`：load `gsm8k`/`main`/test split，gold 用 `r"####\s*(-?\d+)"` 抽，extractor 名 `gsm8k_last_int`
2. **加 MATH loader** `_math(n, seed)`：load `hendrycks/competition_math`/test split，gold 用 `r"\\boxed\{([^}]+)\}"` 抽，extractor 名 `math_boxed`
3. **改 `_c_eval`** 接受 `subjects: list[str]`（默认论文 5 学科 if 已知，否则保留 `computer_network`）和 `seed`
4. **改 `_items_for_dataset`**：所有 dataset 都传 `seed`（GSM8K / MATH / c_eval / mmlu / bool_q）；保持 `simple_math` 兼容
5. **加抽取器**：
   - `_extract_gsm8k(text)` — 找 "answer is X" / 最后一个数字
   - `_extract_math_boxed(text)` — 优先 `\boxed{...}`，回退最后 LaTeX 表达式
6. **加 `_matches` 分支**：
   - `gsm8k_last_int`：数值精确匹配
   - `math_boxed`：sympy 符号化等价（`sympy.simplify(parse_latex(p) - parse_latex(e)) == 0`），失败回退字符串归一化
7. **注册**：`DATASET_LOADERS["gsm8k"] = _gsm8k`、`["math"] = _math`；`EXTRACTORS["gsm8k_last_int"]` / `["math_boxed"]`

**新增 dev 依赖**：`sympy` + `antlr4-python3-runtime`（latex parse 用）。eval 是 dev 工具，不进 runtime requirements。

### 4.4 一次性 Dify 平台准备（**非新代码**，但 SI/P2S/S2P 跑通的前提）

> 标准 `llm` 节点不读 `model_net.yaml`，必须先在 Dify Web 控制台把 3 个 llama.cpp 端点配成 model provider。

1. 装 OpenAI-Compatible API plugin（Dify Marketplace 已有官方插件）
2. 在 **Settings → Model Provider → OpenAI-Compatible-API** 添加 3 条：
   - `qwen25-7b-instruct-q5km` / `http://219.222.20.79:32246/v1` / type=LLM
   - `deepseek-r1-distill-qwen-7b-q4` / `http://219.222.20.79:32310/v1` / type=LLM
   - `glm-4-9b-chat-q4k` / `http://219.222.20.79:31021/v1` / type=LLM
3. 验证：Web UI 创建空 chatflow，添加 LLM 节点，确认 3 个新模型出现在下拉

PI 范式不需要这一步（用 `token-model-source` + `model_alias` 直接读 model_net.yaml）。

### 4.5 4 条代表路径 DSL（每个范式 1 条）

| 范式 | 路径 | 节点拓扑 | 调用次数 |
|---|---|---|---|
| **SI** | Qwen → Ds → Yi | `start → llm(Qwen) → llm(Ds) → llm(Yi) → end` | 3 |
| **PI** | [Qwen, Ds, Yi] | `start → 3×token-model-source(alias=5,27,6) → parallel-ensemble(sum_score, runner=token_step) → end` | 3（并行） |
| **S2P** | Qwen → [Ds, Yi] | `start → llm(Qwen) → 2×llm(Ds, Yi) parallel → response_aggregator(majority_vote) → end` | 3 |
| **P2S** | [Qwen, Ds] → Yi | `start → 2×llm(Qwen, Ds) parallel → response_aggregator(concat, label=on) → llm(Yi) → end` | 3 |

**新增文件**（暴露同一输入 `question`、同一输出 `answer`）：
- `docs/ModelNet/examples/workflow_mode/paper_si.yml`
- `docs/ModelNet/examples/workflow_mode/paper_pi.yml`
- `docs/ModelNet/examples/workflow_mode/paper_s2p.yml`
- `docs/ModelNet/examples/workflow_mode/paper_p2s.yml`

Prompt 用论文 Table 2 模板（`{question}` 占位）。PI 模板的 `model_alias` 用字符串 `"5"`、`"27"`、`"6"`，参考 `duet_net_q1_q2_g4.yml` 的 token-model-source 节点写法（注意现有示例可能是 q2/g4 旧别名，按当前 model_net.yaml 实际 alias `"5"/"27"/"6"` 写）。

### 4.6 实验配置 + 跑批

**新增** `dev/modelnet/eval_paper.yaml`：

```yaml
base_url: http://localhost:5001/v1
user: paper-reproduction
response_mode: blocking
request_timeout_s: 600              # 注意是 _s 后缀

workflow_keys:
  paper_si:   "<api_key_si>"
  paper_pi:   "<api_key_pi>"
  paper_s2p:  "<api_key_s2p>"
  paper_p2s:  "<api_key_p2s>"

datasets:
  gsm8k:  {n: 100, seed: 42}        # 论文 n=100
  c_eval: {n: 100, seed: 42, subjects: [...]}    # 论文 5 学科 if 已知
  math:   {n: 100, seed: 42}

checkpoint_path: dev/modelnet/checkpoints/paper.json    # _path 后缀
report_path:     dev/modelnet/reports/paper.json        # _path 后缀
```

**跑**：

```bash
cd /home/xianghe/temp/dify
uv run --project api python dev/modelnet/duet_net_eval.py --config dev/modelnet/eval_paper.yaml
# 4 workflow × 3 dataset × 100 sample = 1200 调用
# --resume 增量恢复
```

### 4.7 Stage A 验证清单

- [ ] **后端单测**：`uv run --project api pytest api/tests/unit_tests/core/workflow/nodes/response_aggregator/test_majority_vote.py -v`
- [ ] **strategy 列表 smoke**：`uv run --project api python -c "from core.workflow.nodes.response_aggregator.strategies import list_strategies; print([s['name'] for s in list_strategies()])"` 输出含 `concat` + `majority_vote`
- [ ] **DSL 校验 smoke**：`uv run --project api python -c "from core.workflow.nodes.response_aggregator.entities import ResponseAggregatorNodeData; ResponseAggregatorNodeData(inputs=[{'source_id':'a','variable_selector':['x','y']},{'source_id':'b','variable_selector':['p','q']}], strategy_name='majority_vote')"` 不抛
- [ ] **前端类型/lint**：`cd web && pnpm type-check && pnpm lint:fix`
- [ ] **DSL 导入 + 手工烟测**：4 个 `paper_*.yml` 通过 Web 控制台导入；S2P 节点面板下拉里能选到 `majority_vote`；每个 workflow 手工跑一道 GSM8K，确认 `answer` 非空且 extractor 命中
- [ ] **小批量端到端**：`eval_paper.yaml` 临时 `n=5`，跑全 4 范式 = 60 调用全 200 OK，报告生成
- [ ] **完整跑批 n=100**：12 组结果对照论文表 4。Qwen2.5-7B 单模 baseline GSM8K=67% 是论文里的，本地量化可能 ±3-5% 偏差；4 范式相对 baseline 提升 24.3% / 16.7% / 26.7% / 25.3%，允许 ±5%

---

## 5. Stage B — 路径矩阵（复现论文表 6-7）

### 5.1 路径枚举

3 模型 = {**Q** = Qwen2.5-7B, **D** = DeepSeek-R1-7B, **Y** = glm-4-9b}

| 范式 | 拓扑约束 | 路径数 | 路径示例 |
|---|---|---|---|
| **SI** | 3 模型全排列 | 3! = 6 | Q→D→Y, Q→Y→D, D→Q→Y, D→Y→Q, Y→Q→D, Y→D→Q |
| **PI** | 3 模型并联（顺序无关） | 1 | [Q, D, Y] |
| **S2P** | 1 串 + 2 并 = `M_serial → [M_a, M_b]` | C(3,1)×C(2,2) = 3 | Q→[D,Y], D→[Q,Y], Y→[Q,D] |
| **P2S** | 2 并 + 1 串 = `[M_a, M_b] → M_serial` | C(3,2)×1 = 3 | [Q,D]→Y, [Q,Y]→D, [D,Y]→Q |

合计 13 个 workflow（6+1+3+3），跑 13 × 3 数据集 × 100 样本 = **3900 次调用**。

### 5.2 DSL 生成器

**新增** `dev/modelnet/generate_paper_dsls.py`（仿 `dev/modelnet/generate_duet_net_dsls.py`）：
- 输入：模板（4 个范式骨架）+ 模型分配（Q/D/Y）
- 输出：13 个 `paper_{si,pi,s2p,p2s}_<path>.yml`

避免手写 13 个文件 + 拷贝偏差。

### 5.3 实验配置 + 跑批

`eval_paper.yaml` 把 `workflow_keys` 扩到 13 条，重跑。可以 `--resume` 复用 Stage A 已跑过的 4 条结果（路径名相同的话）。

### 5.4 Stage B 验证清单

- [ ] 报告 JSON 含 13 × 3 = 39 组 metric
- [ ] 论文表 6-7 给出 path-level accuracy 排名；本地复现允许 path 排名整体一致 + 各组 ±5% 偏差

---

## 6. 关键文件清单

### 只读参考
- 论文：`docs/ModelNet/Multi-model serial and parallel collaborative inference in AI-ModelNet.pdf`
- PI 算法：`docs/ModelNet/PN.py`
- 已有 eval：`dev/modelnet/duet_net_eval.py`
- 配置模板：`dev/modelnet/eval.example.yaml`
- DSL 写法（PI 参考）：`docs/ModelNet/examples/workflow_mode/duet_net_q1_q2_g4.yml`（注意 alias 旧）
- Strategy 写法：`api/core/workflow/nodes/response_aggregator/strategies/concat.py`
- Strategy 测试惯例：`api/tests/unit_tests/core/workflow/nodes/response_aggregator/`
- Frontend 节点惯例：`web/app/components/workflow/nodes/response-aggregator/`
- Frontend 测试规范：`web/docs/test.md` + `frontend-testing` skill（CLAUDE.md 强制）

### Stage A 新增
- `api/core/workflow/nodes/response_aggregator/strategies/majority_vote.py`
- `api/tests/unit_tests/core/workflow/nodes/response_aggregator/test_majority_vote.py`
- `docs/ModelNet/examples/workflow_mode/paper_{si,pi,s2p,p2s}.yml`
- `dev/modelnet/eval_paper.yaml`

### Stage A 修改
- `api/core/workflow/nodes/response_aggregator/strategies/__init__.py`（+1 import / +1 export）
- `api/core/workflow/nodes/response_aggregator/entities.py:134`（`Literal["concat"]` → `Literal["concat", "majority_vote"]`）
- `web/app/components/workflow/nodes/response-aggregator/types.ts`（3 处：type / NAMES / META）
- `web/app/components/workflow/nodes/response-aggregator/default.ts`（2 处：ALLOWED_KEYS + 校验块）
- `web/i18n/en-US/workflow.json`（+ majorityVote 翻译子树）
- `web/i18n/zh-Hans/workflow.json`（+ majorityVote 翻译子树）
- `dev/modelnet/duet_net_eval.py`（+2 loader / +2 extractor / 改 `_items_for_dataset` / 改 `_c_eval` 支持 subjects+seed / 改 `_matches` 增 sympy 路径）

### Stage B 新增
- `dev/modelnet/generate_paper_dsls.py`
- 13 个 `docs/ModelNet/examples/workflow_mode/paper_*_*.yml`（生成）

### 一次性平台准备（非代码）
- Dify Web → Settings → Model Provider，配 OpenAI-Compatible API plugin × 3（Qwen / Ds / glm）

---

## 7. 范围之外（明确不做）

- 不重写 `parallel_ensemble` / `token-model-source`（已就绪）
- 不动 `duet_net` / `sum_score` / `max_score` token aggregator
- 不加新的 token-level 策略
- 不改 model_net.yaml schema
- 不补响应聚合器节点的 `formatItem` / `getNodeOutputVars`（已就绪）
- Stage B 是复现完整论文表 6-7 才需要；Stage A 单独可交付

---

## 8. 变更日志

| 日期 | 版本 | 作者 | 内容 |
|---|---|---|---|
| 2026-05-05 | v0.1 | xianghe | 初稿，含 Stage A / Stage B 双阶段拆分 |
