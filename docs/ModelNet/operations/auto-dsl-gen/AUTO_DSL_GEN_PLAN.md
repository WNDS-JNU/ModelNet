# Auto DSL Generation Plan (v2)

> 输入：**任意领域**的自由文本任务描述
> 输出：可直接 import 进 Dify 的 workflow DSL（YAML）
> 关键约束：必须覆盖 long tail（不是 5 个模板能枚举的），同时仍能用到 ModelNet
> 三个自定义节点（`token-model-source` / `parallel-ensemble` / `response-aggregator`）

---

## 0. v1 与 v2 的区别（自我检讨）

v1 计划本质是"5 个模板 + slot 填充"。这个方案对 ModelNet 系任务够用，对
**真实长尾完全不够**——用户随便丢一句"先 RAG 再用三个模型集成，最后让 GPT-4
当评委"就出模板了。

v2 改用学界已经验证的 **三阶段流水线**：NL Plan → RAG-grounded compile →
deterministic validate + 有界 repair。模板降级为"语料库里的一类范例"，
不再是 dispatch 的根。

---

## 1. 现状调研（载明出处）

### 1.1 Dify 仓库内

| 维度 | 现状 | 来源 |
|---|---|---|
| AI workflow 生成器 | **无** | 全仓搜索 |
| App 模板推荐 | 仅基于市场拉取，无生成 | `api/services/recommended_app_service.py` |
| Prompt/代码 AI 助手（节点内） | PR #23633 | github.com/langgenius/dify/pull/23633 |
| 整图生成的需求 | 已被多次讨论但未实现 | discussions #10249, #3733；模板 "Workflow Planning Assistant" 报 broken（#21693） |

**结论**：绿地。我们填的是社区已经在等的功能。

### 1.2 学术 SOTA（2023-2026）

| 论文 | 贡献 | 我们能借的 |
|---|---|---|
| **AFlow** (ICLR'25 Oral, [arxiv:2410.10762](https://arxiv.org/abs/2410.10762)) | 把 workflow 生成建模为对 code-graph 的搜索问题；MCTS + 6 个可复用算子 + 执行反馈 | "算子作为一等公民"——把 ModelNet 三节点直接编码成算子；MCTS 适合**离线**挖范例，不适合在线生成 |
| **WorkflowLLM** (NeurIPS'24, [arxiv:2411.05451](https://arxiv.org/abs/2411.05451)) | 106K 样本 SFT 一个 Llama-3.1-8B → WorkflowLlama；in-dist 76.9% vs GPT-4o ICL 67.5%；**OOD API 降到 70.4%** | 给出实际可达天花板；语料构造方法（爬真实流 + GPT 扩 query + 分层思维链注释）可复用 |
| **AutoFlow** (Salesforce 2024, [arxiv:2407.12821](https://arxiv.org/abs/2407.12821)) | NL-as-DSL 中间表示；执行轨迹迭代优化 | **两阶段 NL 计划 → DSL 编译**比一步出 YAML 错误率显著低 |
| **XGrammar / JSONSchemaBench** ([arxiv:2411.15100](https://arxiv.org/pdf/2411.15100), [arxiv:2501.10868](https://arxiv.org/html/2501.10868v3)) | 生产级 CFG/JSON-schema 受约束解码 | 在 token 层就排除"未知节点类型 / 边引用乱写"；OpenAI 兼容 API 没有这个能力时退化为 `response_format=json_schema` |
| **Self-Refine** + 2026 self-repair 研究 ([arxiv:2303.17651](https://arxiv.org/abs/2303.17651)) | 单 LLM 同时做 generator + critic + refiner | **修复主要收益在 round 1-2**，逻辑错只能修 ~45%；语法/命名错好修。**预算 2 轮，再不过就升级让用户澄清**，别死循环 |

### 1.3 开源对照表

| 项目 | NL→workflow? | 怎么做 | 失败模式 | 我们能借 |
|---|---|---|---|---|
| **n8n AI Builder** (2025 GA) | ✅ | 闭源 LLM 服务一次性出 JSON，多轮对话精修 | 长链质量差；按 credit 收费导致 retry 预算低 | "用户在画布里事后编辑"作为 UX 闭环 |
| **WorkflowLLM** | ✅（研究） | SFT 8B 模型 + 分层 CoT | OOD API 衰减、Apple Shortcuts 偏置 | 语料构造方法 |
| **AFlow** | 间接 | 对**给定 benchmark** 搜最优工作流，不是从用户描述 | 慢、需评估信号 | 算子抽象 + 离线挖范例 |
| **Microsoft PromptFlow** | ❌ 整图 | 仅自动检测 flow 类型；变体实验 | 手写图 | 变体实验骨架 |
| **Flowise AgentFlow V2** | 部分 | 有 LLM Router 节点做**运行期**路由 | 不解决冷启动 | 把它作为生成出来的 DSL 内部的一个节点 |
| **LangGraph `create_supervisor`** | ❌ | 运行期抽象 | 多 agent 维护贵 | **Planner→Compiler→Validator 模式**正是我们生成器侧应当采用的 |
| **CrewAI `planning=True`** | 部分 | 任务级计划 | 无类型校验 | "先粗计划后展开成节点"的 bootstrap |
| **Latitude (Latte)** | ✅ | 单 agent + tools | 不输出 DSL/DAG | 验证"描述即生成"的 UX 在生产环境可行 |
| **Dify** | ❌ | n/a | n/a | 我们要填的洞 |

---

## 2. 设计原则（从调研提炼，**有 why**）

1. **不要让 LLM 一步生成 YAML**——AutoFlow 论文 + n8n 经验都指向"先 NL/JSON 计划，再编译到 DSL"。直接 YAML 生成的错误率不可承受。
2. **模板不是 dispatch 根，是检索语料**——WorkflowLLM 的 OOD 数字（76.9% → 70.4%）说明：哪怕训练过的模型遇到没见过的节点都会衰减；模板穷举注定不够，必须配 RAG over examples。
3. **能用约束解码就用**——XGrammar 在 token 层就排除一整类失败模式；OpenAI 兼容 API 用 `response_format` 退化。把"节点类型必须在白名单内"这种事**不要靠 LLM 自觉**。
4. **校验器必须 deterministic**——self-repair 2026 论文：LLM-as-judge 在内层循环不收敛。我们的 validator 是规则 + pydantic + 反向可达性，不调 LLM。
5. **修复 2 轮就够，第 3 轮升级**——同一篇论文：round 1-2 拿走绝大多数增益；继续重试边际为零。round 2 不过 → 把当前 best-effort DSL + 失败原因抛回给用户决定。
6. **生成期的 multi-agent ≠ 运行期的 multi-agent**——生成器内部可以是 Planner / Compiler / Validator 三角色（LangGraph 风格），但**生成出来的 Dify workflow 应该尽可能扁平**。别把翻译任务编译成多 agent 系统。
7. **AFlow 风格 MCTS 是离线工具**——用来挖新范例进语料库，**不在线跑**，太慢。

---

## 3. 三阶段架构

```
┌────────────────────────────────────────────────────────────┐
│ Stage 1 · PLAN                                              │
│   LLM (1 call) ─ NL 任务 ──► 结构化 JSON 计划：              │
│   {                                                          │
│     "intent": "...",                                         │
│     "required_capabilities": ["rag","ensemble",...],         │
│     "nodes_sketch": [                                        │
│       {"role":"input","type":"start","purpose":"..."},       │
│       {"role":"retriever","type":"knowledge-retrieval",...}, │
│       {"role":"answerer","type":"parallel-ensemble",...},    │
│       ...                                                    │
│     ],                                                       │
│     "data_flow": [["start.q","retriever.query"], ...],       │
│     "confidence": 0.0~1.0                                    │
│   }                                                          │
└──────────────────────────┬─────────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────────┐
│ Stage 2 · COMPILE (RAG-grounded, schema-constrained)         │
│                                                              │
│   plan ──► embed plan.intent + node_types ──► 检索 Top-K     │
│         exemplars from corpus (50-150 hand-curated YAMLs)    │
│                                                              │
│   ┌──────────────────────────────────────────────────┐      │
│   │ LLM 第二次调用：                                   │      │
│   │  - system: 节点目录 + 全部 schema + 约束            │      │
│   │  - user:   plan + Top-K exemplars + "compile to YAML"│   │
│   │  - response_format: json_schema（OpenAI 兼容）       │   │
│   └──────────────────────────────────────────────────┘      │
│                            │                                 │
│                            ▼                                 │
│                     DSL dict (JSON)                          │
└──────────────────────────┬─────────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────────┐
│ Stage 3 · VALIDATE + REPAIR                                  │
│                                                              │
│   deterministic validator（5 层，下文 §5.5）                  │
│                            │                                 │
│             ok ◄──── 失败 ────► 把错误列表喂回 Compile        │
│             │                   重试（max 2 次）              │
│             ▼                                                │
│         write out.yml      ──► 仍失败 ──► 升级到澄清模式：    │
│                                  返回 best-effort DSL +     │
│                                  必须用户回答的具体问题       │
└────────────────────────────────────────────────────────────┘
```

---

## 4. 关键交付物

| 名称 | 形态 | 说明 |
|---|---|---|
| **节点能力清单** | `node_catalog.yaml` | 所有支持的节点（内置 + ModelNet 三个自定义）的：type 字符串、用途一句话、关键字段、输入字段、输出字段、典型用例。LLM 在 Plan 阶段读这个；Compile 阶段也读 |
| **范例语料库** | `exemplars/*.yml` + `exemplars/index.json` | 50-150 份手工挑选 / 半自动生成的 DSL 样本，每份带 `{title, description, tags, embedding}` 索引。包括 ModelNet 系（DuetNet / response-aggregator）、RAG 各变体、agent、iteration、判别-路由、HTTP 集成等 |
| **JSON Schema** | `schemas/dsl_schema.json` | 给 OpenAI 兼容 `response_format=json_schema` 用的整图 schema；约束节点 type 只能取自白名单 |
| **Validator** | Python | §5.5 |
| **Pipeline** | Python | Plan → Compile → Validate → Repair |
| **CLI + 服务** | Python | 短期 CLI，后续可改成 Dify 内部一个新 controller（在 `api/controllers/console/app/` 加 endpoint） |

---

## 5. 各组件设计

### 5.1 NL Plan IR（中间表示）

为什么不直接生成 YAML：YAML 里有 React Flow `position` / `width` / `data.type` 嵌套 / `sourceHandle` / mustache 变量引用——LLM 直接生成出错概率高。

Plan IR 用扁平 JSON：

```json
{
  "intent": "用 q1/q2/g4/L3 四个本地模型做 token 级 DuetNet 集成，回答数学题",
  "language": "zh",
  "required_capabilities": ["token-level-ensemble", "math-reasoning"],
  "input_schema": {
    "fields": [
      {"name": "question", "type": "paragraph", "required": true,
       "description": "用户提出的数学题"}
    ]
  },
  "output_schema": {
    "fields": [
      {"name": "answer", "type": "string", "from": "ensemble.text"},
      {"name": "metadata", "type": "object", "from": "ensemble.metadata"}
    ]
  },
  "nodes": [
    {"role": "start_input",       "type": "start", "purpose": "..."},
    {"role": "model_source_q1",   "type": "token-model-source",
     "params": {"model_alias": "38", ...}, "purpose": "..."},
    {"role": "model_source_q2",   "type": "token-model-source", ...},
    {"role": "model_source_g4",   "type": "token-model-source", ...},
    {"role": "model_source_L3",   "type": "token-model-source", ...},
    {"role": "ensemble",          "type": "parallel-ensemble",
     "params": {"runner_name":"token_step","aggregator_name":"duet_net",
                "tau_k":10,"tau_p":0.75,"top_t":1,"max_len":512},
     "purpose": "..."},
    {"role": "final_output",      "type": "end", ...}
  ],
  "edges": [
    {"from": "start_input",     "to": "model_source_q1"},
    {"from": "start_input",     "to": "model_source_q2"},
    {"from": "start_input",     "to": "model_source_g4"},
    {"from": "start_input",     "to": "model_source_L3"},
    {"from": "model_source_q1", "to": "ensemble"},
    {"from": "model_source_q2", "to": "ensemble"},
    {"from": "model_source_g4", "to": "ensemble"},
    {"from": "model_source_L3", "to": "ensemble"},
    {"from": "ensemble",        "to": "final_output"}
  ],
  "variable_refs": [
    {"from": "start_input.question", "to_node": "model_source_q1",
     "to_field": "prompt_template", "insert_as": "mustache"},
    ...
  ],
  "confidence": 0.86
}
```

`confidence` 是 LLM 自评，<0.5 直接进澄清模式。

### 5.2 节点能力清单 `node_catalog.yaml`

LLM 在 Plan 阶段读这个——它就是 Plan IR 里 `node.type` 的取值域。每条：

```yaml
- type: token-model-source
  category: modelnet-ensemble
  one_liner: |
    渲染共享 prompt，给后续 parallel-ensemble 节点输出一个 ModelInvocationSpec。
    每个 token-model-source 代表 ensemble 里的一个 voter。
  required_capability: LOGITS_RAW  # 候选模型必须在 model_net.yaml 注册并暴露 raw logits
  required_fields:
    - model_alias        # registry key
    - prompt_template    # 含 {{#node.field#}} 占位
  optional_fields:
    - sampling_params    # max_tokens/top_k/temperature/top_p/stop/seed
    - inline_spec        # 跳过 registry 直接传 backend spec
    - raw_completion     # 关闭 chat-template auto-wrap
    - expose_raw_logits  # 覆盖 registry alias 的 raw-logit 开关
  outputs:
    - spec               # 类型 ModelInvocationSpec，被 parallel-ensemble 消费
  use_when: |
    任务明确提到 token 级 / logit 级 / 联合解码 / DuetNet，或要求 2+
    模型在 per-token 层面而不是 per-response 层面集成。

- type: parallel-ensemble
  ...

- type: response-aggregator
  ...

- type: llm
  ...

- type: knowledge-retrieval
  ...

# ...剩余所有内置节点
```

这一份就是单一真相源。LLM 不能凭空发明 type 字符串。

### 5.3 范例语料库

**初始规模 50-150 份**，覆盖以下类别（每类 3-10 份变体）：

| 类别 | 范例 |
|---|---|
| simple-llm | 单 LLM、有/无 system prompt、不同 model 家族 |
| rag-qa | 单数据集 / 多数据集 / single vs multiple retrieval |
| classification-routing | question-classifier 分支 / variable-aggregator 合并 |
| agent-tool-use | agent 节点 + 工具调用 |
| iteration-map | 列表迭代 + 每项 LLM 处理 |
| http-integration | http-request + template-transform |
| document-extract | document-extractor + LLM 抽结构化字段 |
| **modelnet-token-ensemble** | DuetNet（已存在 `docs/ModelNet/examples/workflow_mode/duet_net_main.yml`），变体（不同 model alias 数 / 不同 tau） |
| **modelnet-response-ensemble** | N 个 LLM 并联 + response-aggregator |
| **cascade** | RAG → token-ensemble、retrieval → response-ensemble 等组合 |
| 长链 multi-step | start → http → llm → if-else → llm → end |

每份带 `meta.json`：

```json
{
  "id": "rag-multi-multilingual-001",
  "title": "Multilingual RAG over multiple datasets with reranking",
  "tags": ["rag", "multilingual", "reranking", "multiple-retrieval"],
  "description_for_embedding": "Retrieve from N knowledge bases, rerank, then answer in user's language",
  "nodes": ["start", "knowledge-retrieval", "code", "llm", "end"],
  "complexity": "medium"
}
```

**冷启动来源**：
1. `api/tests/fixtures/workflow/*.yml`（23 份内置）
2. `docs/ModelNet/examples/workflow_mode/*.yml`（ModelNet 系）
3. Dify 官方模板市场拉一些，删脱敏
4. 手工补 ~30 份长尾覆盖（agent、iteration、classification 等内置 fixture 没有的）

**长期增长**：用户每次成功的生成 + 人工审一遍 → 自动入库（去重 + tags 自动标注）。AFlow 风格的离线 MCTS 可以在 benchmark 上跑出新的"高质量"组合作为种子。

### 5.4 RAG retriever（语料检索）

最朴素够用：

```python
# 索引阶段（一次性 / 入库时）
for exemplar in corpus:
    vec = embedding_model(exemplar.description_for_embedding +
                           " | nodes: " + ",".join(exemplar.nodes))
    save(vec, exemplar.id)

# 检索阶段（每次生成）
query_vec = embedding_model(plan.intent + " | required_nodes: " +
                             ",".join(n.type for n in plan.nodes))
top_k = vector_search(query_vec, k=5)
```

向量后端：复用 Dify 已有的向量能力（在 `api/core/rag/datasource/vdb/`），无需新依赖。embedding 也用 Dify 已配置的（默认 `text-embedding-3-small`）。

为什么 description+node_types 拼着 embed：纯文本 embedding 会被表面相似带偏（"翻译"和"summarization"在 embedding 空间很近），把节点类型作为弱信号一起编码能显著拉开。

### 5.5 Compile：约束生成 DSL

prompt 构造：

```
SYSTEM：
你是 Dify workflow 编译器。把给定的结构化 Plan 翻译成可 import 的 Dify YAML。
严格遵守：
- 节点 type 只能从下方目录里选（不允许编造）
- 变量引用统一用 {{#node_id.field#}}
- 边的 data.{sourceType,targetType} 必须和节点 data.type 一致
- 顶层用 {app, dependencies:[], kind:"app", version:"0.6.0", workflow:{...}}
- React Flow 字段：每个节点外层 type:"custom"，内层 data.type 才是 Dify 节点类型

节点目录（从 node_catalog.yaml 复制完整 schema 进来）：
<...>

参考范例（Top-K from RAG）：
--- Example 1 (id=rag-multi-multilingual-001) ---
<完整 YAML>
--- Example 2 (id=...) ---
<...>

USER：
Plan JSON：
<plan>

任务：把上面 Plan 编译成完整的 Dify DSL YAML。

输出：仅 YAML 内容，不要任何解释。
```

**结构约束**：
- 优先：`response_format={"type":"json_schema", "json_schema":{...}}`，schema 用一个最小化的 DSL JSON Schema（约束 `kind=app`, `workflow.graph.nodes[].data.type ∈ 白名单`, `edges[].source/target` 必须存在等）
- 次选：当 endpoint 不支持 json_schema 时用 `json_object` + 后端校验
- 如果接的是支持 XGrammar 的 vLLM，可以直接传一个 EBNF/CFG，更强约束

**重要**：YAML 本身没 JSON Schema 友好，所以我们让 LLM 输出 JSON 形式的 DSL（Dify import 路径 `AppDslService.import_app` 内部就是 dict），然后 Python 一侧 `yaml.safe_dump` 落盘。

### 5.6 Validator（5 层 deterministic）

| 层 | 检查 | 实现 |
|---|---|---|
| **L1 结构** | 顶层 keys、`workflow.graph.nodes/edges` 是 list | 手写 |
| **L2 节点 pydantic** | 每节点 `data` 走 `Node.validate_node_data` | `core.workflow.node_factory.register_nodes()` + `Node.get_node_type_classes_mapping()`；注意 `NodeType` 是 `type NodeType = str` 别名，key 是普通字符串 |
| **L3 自定义节点深层** | 对 `parallel-ensemble`：`runner_config` 过 `RunnerRegistry.get(name).config_class.model_validate`；`aggregator_config` 同理过 `AggregatorRegistry`；对自定义节点的子配置同样 | Dify import 路径**不做**这一步，runtime 才炸 |
| **L4 变量可达性** | 反向走 DAG，所有 `value_selector/variable_selector/spec_selector` + prompt 字符串里的 `{{#node.field#}}` 必须指向真实存在的祖先 + 该节点确实有这个输出字段 | 自己实现；输出字段表见下 |
| **L5 节点输入完整性** | 每个节点根据 catalog 声明的 `required_fields`，确认在 plan 里都有数据来源（外部输入 / 上游变量 / 静态值之一） | 自己实现，这层是 catalog 驱动的，新增节点只改 catalog |

L4 反向可达性算法（关键，因为 Dify 自己不做）：

```
for each node N:
    anc(N) = 反向 BFS 沿 edges 收集祖先集
    for each selector [first, second, ...] mined from N.data:
        if len == 0:                continue   # 未设置（可选字段）
        if len < 2:                 error      # malformed
        if first in {"sys","env","conversation"}: continue
        if first not in graph:      error
        if first != N and first not in anc(N): error
        if second not in outputs_of(first):    error
```

各节点 outputs（reachability 表）来自 catalog；自定义三节点的输出已知：

```python
"token-model-source":  {"spec"}
"parallel-ensemble":   {"text", "metadata"}
"response-aggregator": {"text"}
```

### 5.7 Repair loop（有界 + 升级）

```python
def generate(task, *, max_repair=2):
    plan = stage1_plan(task)
    if plan.confidence < CLARIFY_THRESHOLD:
        return escalate_to_clarification(plan)

    prior_errors = None
    for round in range(max_repair + 1):
        dsl = stage2_compile(plan, prior_errors=prior_errors)
        result = validate(dsl)
        if result.ok:
            return Success(dsl, plan, attempts=round + 1)
        prior_errors = format_errors_for_llm(result.errors)

    # round 2 仍失败 → 升级
    return ClarificationNeeded(
        best_effort_dsl=dsl,
        plan=plan,
        residual_errors=result.errors,
        questions=derive_questions_from_errors(result.errors, plan),
    )

def derive_questions_from_errors(errs, plan):
    # 把验证错误转成对用户的具体问题：
    # "ensemble 节点引用了 q1_source.spec 但 q1_source 没在图里——
    #  你想用 token-model-source 还是 LLM 节点作为第一个 voter？"
    ...
```

**为什么 2 轮**：self-repair 2026 研究的实测——绝大部分增益在前 2 轮。第 3 轮起边际收益接近 0，但 LLM token 成本线性涨。

**升级的产物**：不是"失败"而是一个 *半成品 DSL + 具体问题列表*。用户回答后可以从 plan 阶段重入，或者直接修 plan 然后跳到 compile 阶段。

---

## 6. 关键代码 anchor（沿用 v1 调研结果）

| 用途 | 路径:行 |
|---|---|
| 自定义节点 schema | `api/core/workflow/nodes/{token_model_source,parallel_ensemble,response_aggregator}/entities.py` |
| 节点工厂 + 注册 | `api/core/workflow/node_factory.py:115-130`（`register_nodes()`） |
| DSL 版本常量 | `api/constants/dsl_version.py:1` (`CURRENT_APP_DSL_VERSION = "0.6.0"`) |
| DSL import 入口 | `api/services/app_dsl_service.py:111` (`AppDslService.import_app`) |
| graphon `NodeType` 是 `type NodeType = str` 别名 | `graphon/enums.py:13` — **mapping key 是字符串，不要 `NodeType("llm")` 调用** |
| `RunnerRegistry` / `AggregatorRegistry` | `api/core/workflow/nodes/parallel_ensemble/registry/` |
| SPI `config_class` | `parallel_ensemble/spi/{runner,aggregator}.py`（runner:162, aggregator:120） |
| 参考 DSL（DuetNet 标准样本） | `docs/ModelNet/examples/workflow_mode/duet_net_main.yml` |
| 内置节点 fixture | `api/tests/fixtures/workflow/*.yml`（23 份） |
| Embedding / vector DB（复用，不要新增依赖） | `api/core/rag/datasource/vdb/`、`api/core/model_runtime/.../text_embedding/` |

---

## 7. 文件布局

```
api/dsl_gen/
├── __init__.py
├── __main__.py
├── cli.py                       # CLI 入口
├── controllers/                 # （Phase 2）Dify console API endpoint
│   └── app_workflow_generate.py
├── pipeline.py                  # 编排 Stage 1-3 + repair loop + 澄清升级
├── planner.py                   # Stage 1：NL → Plan IR
├── compiler.py                  # Stage 2：Plan + RAG → DSL（schema-constrained）
├── validator.py                 # Stage 3：5 层 deterministic 校验
├── catalog/
│   ├── node_catalog.yaml        # 单一真相源
│   └── loader.py                # 加载、校验 catalog 自身
├── corpus/
│   ├── exemplars/               # 50-150 份 .yml + .meta.json
│   ├── builder.py               # 从 tests/fixtures + docs/ModelNet/examples 引种
│   ├── indexer.py               # 建 embedding 索引
│   └── retriever.py             # 检索 Top-K
├── schemas/
│   └── dsl_json_schema.py       # 给 response_format=json_schema 用
├── llm/
│   ├── client.py                # httpx OpenAI 兼容
│   ├── plan_prompts.py          # Stage 1 prompts
│   └── compile_prompts.py       # Stage 2 prompts
├── clarification.py             # 失败升级：把错误转成给用户的问题
└── tests/
    ├── test_validator.py
    ├── test_planner_fixtures.py # 离线模式：用预录的 LLM 响应跑 planner
    ├── test_compiler_fixtures.py
    └── golden/                  # 一批 "任务描述 → 期望 DSL" 的 golden 测试
```

---

## 8. 实施路线（Phase）

每个 phase 都能独立交付价值；不强求一口气做完。

| Phase | 内容 | 验收 |
|---|---|---|
| **P1** | `node_catalog.yaml` + L1/L2/L4 validator + 复用 v1 已有 fixture 跑通 | 23 份 fixture 全过 validator；自定义三节点的 catalog 完整 |
| **P2** | corpus builder + indexer + retriever；冷启动 50 份范例 | 给定 plan 能返回 Top-5 相关范例 |
| **P3** | planner（Stage 1）+ Plan IR 校验（自校验：node.type 在 catalog 内、selector 自洽） | 10 个 golden 任务描述能产出合法 Plan |
| **P4** | compiler（Stage 2）+ L3/L5 validator + 一轮 repair | 10 个 golden 任务能编译出 DSL 并过 validator，>= 70% 一次过 |
| **P5** | CLI + 升级澄清模式 | `python -m dsl_gen "..."` 端到端可用；失败时输出有意义的问题 |
| **P6** | Dify console API endpoint + 前端调用 | 在 Dify UI 里点"AI 生成"能用 |
| **P7（持续）** | 语料库扩张：用户成功生成自动审 + 入库；离线 AFlow 风格挖新范例 | 长尾覆盖逐月提升 |

---

## 9. 评估

借鉴 WorkflowLLM 的方法。

### 9.1 指标

| 指标 | 目标 | 备注 |
|---|---|---|
| `compile_pass_rate` | ≥ 70% 不 repair；≥ 85% 含 ≤2 轮 repair | 用 golden + 100 条合成任务 |
| `validator_layer_failure` | L1 < 1%、L2 < 5%、L3 < 5%、L4 < 15%、L5 < 5% | L4（变量可达）会最高，符合直觉 |
| `OOD_pass_rate` | ≥ 60% | "OOD" = 任务用到不常见组合（cascade、罕用节点） |
| `clarification_quality` | 升级时的问题人工评分 ≥ 4/5 | 一组人测 20 个升级样本 |
| `time_per_generation` | p50 < 8s，p95 < 25s | 包含 2 次 LLM 调用 + 检索 + 校验 |

### 9.2 测试集来源

1. **Golden（~30 条）**：手写 20 条覆盖各类别 + 5 条专为 ModelNet 自定义节点（含 DuetNet 主算法、response-level 集成、二者级联）+ 5 条边界（无效任务 / 缺信息 / 跨多类）
2. **合成（~100 条）**：用 GPT-4o 基于 catalog 生成（"假设你是 Dify 用户，写一句话描述你想要的 workflow"），人工筛
3. **真实（持续）**：用户实际使用积累

---

## 10. 已知风险 & 缓解

| 风险 | 缓解 |
|---|---|
| **长尾任务衰减**（WorkflowLLM OOD 数据点） | RAG corpus 持续扩张；升级到澄清模式而非死循环 |
| **LLM 路由幻觉节点 type** | catalog 白名单 + `response_format=json_schema` + L2 pydantic 三重防 |
| **变量引用错位**（最高频失败） | L4 反向可达性是硬约束；repair 时把"哪个 selector 不可达"喂回 LLM |
| **`register_nodes()` 是全局副作用** | 进程级 lazy + cache；CLI 单次调用 ok，长驻服务首次启动会慢 ~5s |
| **OpenAI 兼容端点不支持 json_schema** | 退化到 `json_object` + 强后端校验；对接 vLLM 可启用 XGrammar 拿到 token 级约束 |
| **范例语料污染**（错例进库） | 入库前必过 validator；用户成功样本入库前需要人审 |
| **生成的 DSL 能 import 但运行炸** | L3 深度校验已最大限度抓 schema 错；语义错（业务逻辑不对）由用户自己跑一次确认，这层我们不假装能保证 |
| **多语言任务描述** | planner 不强制英文；catalog 也支持双语 description |
| **Dataset UUID 不存在** | RAG 类任务允许 `dataset_ids=["REPLACE_ME"]`，clarification 阶段问用户 |

---

## 11. 何时考虑 SFT（fine-tuning）

不是 v1 范围，但需要心里有数：

WorkflowLLM 的数据点：8B SFT 模型在 in-distribution 比 GPT-4o ICL 高 9.4pp
（76.9% vs 67.5%），代价是建 100K 样本语料库 + SFT 算力。

**触发条件**（同时满足才上 SFT）：
1. RAG + repair 之后 pass rate 长期卡在 < 70%
2. 累计真实用例 > 5000 条
3. 有明确不能用 closed-source LLM 的合规要求

否则继续走 closed-source LLM + RAG + 约束解码这条更便宜的路径。

---

## 12. 与 v1 计划的对照

| 维度 | v1 | v2 |
|---|---|---|
| 核心机制 | 5 个固定模板 + slot 填充 | NL Plan → RAG-grounded compile → validate+repair |
| 模板地位 | dispatch 根 | 语料库一类范例（非排他） |
| 长尾覆盖 | 模板未命中即失败 | 通过 RAG + 节点目录 + 受约束生成 cover 任意组合 |
| 路由 | 单次 LLM call 选模板 + 填 slot | 两次 LLM call：先 plan 后 compile |
| 校验 | 4 层 | 5 层（多 L5 输入完整性） |
| 失败处理 | 重试 ≤2 次 → 报错 | 重试 ≤2 次 → **升级到澄清** |
| 工程量 | ~2K 行 | ~4-5K 行 + 50-150 份 corpus |
| 学界对照 | 无 | AFlow / WorkflowLLM / AutoFlow / Self-Refine / XGrammar |
| 现实预期 | 模板内 100%，模板外 0% | in-dist ~75-85%、OOD ~60-70% |

v1 不是错的——它就是 v2 corpus 的一个子集 + 一个最简单的 dispatch 路径。
真正动手时可以先按 v1 跑通骨架，再逐 phase 升级到 v2。

---

## 13. 参考资料（含 URL）

### 论文
- AFlow: <https://arxiv.org/abs/2410.10762> · <https://github.com/FoundationAgents/AFlow>
- WorkflowLLM: <https://arxiv.org/abs/2411.05451> · <https://github.com/OpenBMB/WorkflowLLM>
- AutoFlow: <https://arxiv.org/abs/2407.12821>
- XGrammar: <https://arxiv.org/pdf/2411.15100>
- JSONSchemaBench: <https://arxiv.org/html/2501.10868v3>
- Self-Refine: <https://arxiv.org/abs/2303.17651> · <https://selfrefine.info/>
- Prompt2DAG: <https://arxiv.org/html/2509.13487v1>
- FlowBench: <https://arxiv.org/abs/2406.14884>
- FlowMind: <https://arxiv.org/abs/2404.13050>
- CodeRAG-Bench: <https://arxiv.org/html/2406.14497v2>
- LLM+P: <https://arxiv.org/abs/2304.11477>

### 开源项目
- n8n AI Workflow Builder: <https://docs.n8n.io/advanced-ai/ai-workflow-builder/>
- Microsoft PromptFlow: <https://github.com/microsoft/promptflow>
- Flowise AgentFlow V2: <https://docs.flowiseai.com/using-flowise/agentflowv2>
- LangGraph supervisor: <https://reference.langchain.com/python/langgraph/supervisor/>
- AutoGen task decomposition: <https://microsoft.github.io/autogen/0.2/docs/topics/task_decomposition/>
- CrewAI planning: <https://docs.crewai.com/en/concepts/agents>
- Latitude (Latte): <https://github.com/latitude-dev/latitude-llm>

### Dify 相关讨论
- discussions #10249: <https://github.com/langgenius/dify/discussions/10249>
- discussions #3733: <https://github.com/langgenius/dify/discussions/3733>
- 节点内 AI 助手 PR #23633: <https://github.com/langgenius/dify/pull/23633>

---

## 14. 一句话总结

**别把模板当 dispatch 根**——做"NL 计划 → RAG 取范例 → 受约束编译 → deterministic 校验 → 有界 repair → 澄清升级"这条产业 + 学界已验证的链。模板降级为语料库一员，长尾通过 RAG + 节点目录 + 约束解码 cover，对 OOD 的现实预期是 ~70% 而不是 100%——剩下的 30% 用澄清模式而不是无限重试解决。
