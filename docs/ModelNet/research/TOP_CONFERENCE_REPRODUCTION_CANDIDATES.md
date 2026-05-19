# 顶会相似工作复现候选

**检索日期**：2026-05-19  
**目标平台**：ModelNet / Dify 分支  
**筛选目标**：优先选择可以用现有工作流画布、RAG、模型管理、`response-aggregator`、`token-model-source`、`parallel-ensemble`、`data-loader` 和 eval harness 复现的顶会工作。

## 1. 结论摘要

当前平台最适合复现的方向不是纯训练型大模型论文，而是以下四类：

1. **多模型响应级协作**：多个模型并行回答，再由聚合器融合。
2. **多智能体辩论与评审**：多个 agent 多轮互评，最后由 judge 汇总。
3. **模型路由与自适应 RAG**：根据问题复杂度、成本或置信度选择模型/检索策略。
4. **token 级协作解码**：多个模型在逐 token 解码阶段协作。

优先级建议：

```text
MoA / multi-agent debate
  -> RouteLLM / Adaptive-RAG
  -> Co-LLM token-level collaboration
  -> Self-RAG / DRAGIN / FLARE
  -> ARES / RAGAS-style evaluation
```

其中，**MoA、Multiagent Debate、RouteLLM / Adaptive-RAG** 最适合作为第一批平台复现实验；**Co-LLM** 最贴近 ModelNet 的 token-level 设计，但实现风险更高。

## 2. 平台能力匹配

本仓库已有能力与这些论文的对应关系：

| 平台能力 | 可复现方向 | 说明 |
|---|---|---|
| `response-aggregator` | MoA、debate、LLM judge | 适合多路完整回答后的响应级综合。当前实现是 synthesis-only，不应依赖旧版 `strategy_name` / `strategy_config`。 |
| `token-model-source` | Co-LLM、DuetNet、token ensemble | 每个模型来源独立配置 prompt、采样参数和模型别名。 |
| `parallel-ensemble` | token-level multi-model decoding | 当前最适合复现 `sum_score`、`max_score`、`duet_net` 等无训练或轻训练协作解码。 |
| Dify RAG / Knowledge Base | Self-RAG、DRAGIN、FLARE、Adaptive-RAG | 可做 query complexity routing、retrieve/read loop、document grading、answer verification。 |
| `data-loader` + eval harness | benchmark reproduction | 可用 GSM8K、C-Eval、BoolQ、MATH、HotpotQA/NQ 类数据跑准确率、延迟和成本。 |

## 3. 推荐复现候选

### 3.1 Mixture-of-Agents, ICLR 2025 Spotlight

- **论文**：[Mixture-of-Agents Enhances Large Language Model Capabilities](https://openreview.net/forum?id=h0ZfDIrj7T)
- **作者**：Junlin Wang, Jue Wang, Ben Athiwaratkun, Ce Zhang, James Zou
- **会议**：ICLR 2025 Spotlight
- **核心思想**：构造多层 LLM agents；每一层的 agent 读取上一层所有输出作为辅助信息，再生成新回答。
- **为什么适合本平台**：这几乎就是 Dify workflow 的天然形态：多路 LLM 并行，下一层读取前一层变量，最后由聚合模型输出。
- **复现难度**：低到中。
- **平台实现路径**：
  - `start -> N 个 LLM 节点 -> response-aggregator -> end`
  - 多层版本：`layer1 N agents -> layer2 N agents -> final aggregator`
  - 每个 agent 可使用不同模型、不同 prompt 或不同角色。
- **建议 benchmark**：
  - AlpacaEval-style instruction following
  - Arena-Hard-style pairwise judge
  - GSM8K / MATH / C-Eval 小样本
- **可做的增量贡献**：
  - 比较同构模型 MoA、异构模型 MoA、随机模型组合、基于历史表现的模型选择。
  - 将 MoA 输出接入 `response-aggregator` 的诊断元数据，记录每层贡献。
  - 对比 response-level MoA 与 token-level `parallel-ensemble`。

### 3.2 Multiagent Debate, ICML 2024

- **论文**：[Improving Factuality and Reasoning in Language Models through Multiagent Debate](https://icml.cc/virtual/2024/poster/32620)
- **作者**：Yilun Du, Shuang Li, Antonio Torralba, Joshua Tenenbaum, Igor Mordatch
- **会议**：ICML 2024
- **核心思想**：多个 LLM instances 先独立回答，再通过多轮辩论互相指出问题，最终形成共同答案。
- **为什么适合本平台**：Dify workflow 可以显式表达多 agent、多轮、judge、memory 和最终汇总。
- **复现难度**：低。
- **平台实现路径**：
  - Round 1：`agent_a`、`agent_b`、`agent_c` 并行回答。
  - Round 2：每个 agent 读取其他 agent 的回答并修正。
  - Final：judge 节点综合全部轮次输出。
- **建议 benchmark**：
  - GSM8K / StrategyQA / TruthfulQA / C-Eval
  - 同时记录 accuracy、token cost、latency。
- **可做的增量贡献**：
  - 角色多样性：reasoner / critic / verifier / domain expert。
  - 辩论轮数自适应：若 judge 置信度高则提前停止。
  - 和 MoA 对比：层式汇总 vs 交互式辩论。

### 3.3 ChatEval, ICLR 2024

- **论文**：[ChatEval: Towards Better LLM-based Evaluators through Multi-Agent Debate](https://openreview.net/pdf?id=FQepisCUWu)
- **会议**：ICLR 2024
- **核心思想**：把多 agent debate 用于自动评测，让多个 evaluator 讨论后给出评分。
- **为什么适合本平台**：可以作为平台内置 eval workflow，而不是只作为回答生成 workflow。
- **复现难度**：低。
- **平台实现路径**：
  - `candidate answer + reference/context -> 多个 evaluator -> debate -> final score`
  - evaluator 维度可拆成 correctness、faithfulness、helpfulness、format。
- **建议 benchmark**：
  - RAG QA
  - Summarization / instruction following
  - ModelNet 多模型协作输出的自动评分
- **可做的增量贡献**：
  - 给每个 workflow run 生成结构化 judge trace。
  - 对比 single judge、multi judge vote、multi judge debate。

### 3.4 RouteLLM, ICLR 2025

- **论文**：[RouteLLM: Learning to Route LLMs from Preference Data](https://openreview.net/forum?id=8sSqNntaMr)
- **会议**：ICLR 2025
- **核心思想**：训练或学习一个 router，在强模型和弱模型之间动态选择，以降低成本并保持质量。
- **为什么适合本平台**：Dify/ModelNet 本身管理多个模型，平台价值之一就是把不同模型按任务动态编排。
- **复现难度**：中。
- **平台实现路径**：
  - MVP：用 LLM classifier 或 embedding classifier 判断 query 难度。
  - 路由：简单问题走便宜模型，复杂问题走强模型或多模型协作。
  - eval：记录质量、成本、延迟，画 Pareto curve。
- **建议 benchmark**：
  - GSM8K / MMLU / C-Eval / BoolQ
  - 企业 RAG QA 数据集
- **可做的增量贡献**：
  - 将 router 作为可视化节点配置。
  - 支持 shadow routing：实际只调用一路，同时抽样调用另一路收集偏好数据。
  - 用平台日志持续更新 router。

### 3.5 Adaptive-RAG, NAACL 2024

- **论文**：[Adaptive-RAG: Learning to Adapt Retrieval-Augmented Large Language Models through Question Complexity](https://aclanthology.org/2024.naacl-long.389/)
- **会议**：NAACL 2024
- **核心思想**：先判断问题复杂度，再选择 no retrieval、single-step retrieval 或 iterative retrieval。
- **为什么适合本平台**：Dify 的知识库、条件分支和工作流节点可以直接表达不同 RAG 策略。
- **复现难度**：低到中。
- **平台实现路径**：
  - `question -> complexity classifier`
  - easy：直接 LLM
  - medium：单次 RAG
  - hard：多跳 retrieve-read loop
- **建议 benchmark**：
  - HotpotQA / 2WikiMultiHopQA / Natural Questions
  - 企业内部知识库 QA
- **可做的增量贡献**：
  - 用平台执行日志学习 complexity classifier。
  - 将 cost/latency 纳入 routing objective。
  - 与 RouteLLM 结合：同时路由模型和检索策略。

### 3.6 Co-LLM Token-Level Collaboration, ACL 2024

- **论文**：[Learning to Decode Collaboratively with Multiple Language Models](https://aclanthology.org/2024.acl-long.701/)
- **作者**：Zejiang Shen, Hunter Lang, Bailin Wang, Yoon Kim, David Sontag
- **会议**：ACL 2024 Long Paper
- **核心思想**：在逐 token 解码时决定由哪个模型生成下一个 token，从而融合 generalist 和 expert 模型能力。
- **为什么适合本平台**：这是与 `token-model-source` 和 `parallel-ensemble` 最贴近的顶会工作。
- **复现难度**：高。
- **平台实现路径**：
  - MVP：不训练 router，先实现启发式 token routing。
  - 可选策略：`sum_score`、`max_score`、entropy routing、domain routing。
  - 进阶：训练轻量 router 或用历史 eval 数据学习 token/model 选择。
- **建议 benchmark**：
  - domain-specific QA
  - reasoning
  - instruction following
- **可做的增量贡献**：
  - 在同一个平台上对比 response-level MoA 与 token-level collaboration。
  - 记录 token-level trace，分析每个模型在不同任务中的贡献。
  - 加入 cost-aware token routing。

### 3.7 Self-RAG, ICLR 2024 Oral

- **论文**：[Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection](https://openreview.net/forum?id=hSyW5go0v8)
- **会议**：ICLR 2024 Oral
- **核心思想**：模型通过自反思决定何时检索、如何生成、如何批判自己的回答。
- **为什么适合本平台**：Dify 可以把 retrieve、generate、critique、revise 拆成显式 workflow。
- **复现难度**：中到高。
- **平台实现路径**：
  - MVP：不用训练特殊 reflection token，用 LLM 节点模拟 reflection decision。
  - `question -> retrieve? -> retrieve -> generate -> critique -> revise`
  - 每一步输出结构化 JSON，方便 eval。
- **建议 benchmark**：
  - Open-domain QA
  - Fact verification
  - Long-form factual generation
- **可做的增量贡献**：
  - 将 reflection trace 可视化。
  - 与 DRAGIN/FLARE 的 uncertainty-based retrieval 对比。

### 3.8 DRAGIN, ACL 2024

- **论文**：[DRAGIN: Dynamic Retrieval Augmented Generation based on the Real-time Information Needs of Large Language Models](https://aclanthology.org/2024.acl-long.702/)
- **会议**：ACL 2024 Long Paper
- **核心思想**：根据生成过程中的实时信息需求动态触发检索，并生成更适合检索的 query。
- **为什么适合本平台**：适合做成“动态 RAG workflow”模板，展示 retrieval trigger、query rewriting、answer revision。
- **复现难度**：中到高。
- **平台实现路径**：
  - MVP：按句子或段落循环，而不是严格逐 token。
  - 每轮：生成草稿段落 -> 判断信息缺口 -> 改写 query -> 检索 -> 修订。
- **建议 benchmark**：
  - Long-form QA
  - Multi-hop QA
  - Knowledge-intensive generation
- **可做的增量贡献**：
  - 将 dynamic retrieval 与模型路由结合。
  - 记录每次检索触发原因和 query evolution。

### 3.9 FLARE, EMNLP 2023

- **论文**：[Active Retrieval Augmented Generation](https://aclanthology.org/2023.emnlp-main.495/)
- **会议**：EMNLP 2023
- **核心思想**：先预测下一句，用预测内容作为检索 query；若下一句低置信，则检索并重新生成。
- **为什么适合本平台**：比 Self-RAG 更容易复现，且不要求训练特殊模型。
- **复现难度**：中。
- **平台实现路径**：
  - `draft next sentence -> confidence check -> retrieve -> regenerate`
  - 若当前后端拿不到 token logprob，可先用 LLM judge 近似置信度。
- **建议 benchmark**：
  - Long-form generation
  - Open-domain QA
- **可做的增量贡献**：
  - 和 DRAGIN 比较不同 retrieval trigger。
  - 结合 Dify knowledge base 做平台级 active RAG template。

### 3.10 ARES, NAACL 2024

- **论文**：[ARES: An Automated Evaluation Framework for Retrieval-Augmented Generation Systems](https://aclanthology.org/2024.naacl-long.20/)
- **会议**：NAACL 2024 Long Paper
- **核心思想**：自动评估 RAG 系统的 context relevance、answer faithfulness、answer relevance。
- **为什么适合本平台**：这是构建 ModelNet/Dify 实验闭环的关键：不只生成，还要系统评估每个 workflow。
- **复现难度**：中。
- **平台实现路径**：
  - MVP：用 LLM judge 直接打三类分数。
  - 进阶：生成 synthetic training data，训练轻量 judge。
  - 输出统一 eval report。
- **建议 benchmark**：
  - KILT / SuperGLUE / AIS 类任务
  - 平台自建企业 RAG 数据集
- **可做的增量贡献**：
  - 作为所有 RAG/Agent workflow 的自动评价层。
  - 和 ChatEval 结合：single judge vs multi-agent judge debate。

### 3.11 DSPy, ICLR 2024 Spotlight

- **论文**：[DSPy: Compiling Declarative Language Model Calls into Self-Improving Pipelines](https://openreview.net/forum?id=sY5N0zY5Od)
- **会议**：ICLR 2024 Spotlight
- **核心思想**：把 LM pipeline 抽象成模块图，并基于 metric 自动优化 prompt/demonstrations。
- **为什么适合本平台**：Dify workflow 与 DSPy 的 pipeline graph 很接近；可以把平台 workflow 当成可优化对象。
- **复现难度**：中到高。
- **平台实现路径**：
  - MVP：固定 workflow 拓扑，只优化每个节点 prompt。
  - 用 eval harness 作为 objective。
  - 从少量 labeled examples 中自动挑 demonstrations。
- **建议 benchmark**：
  - RAG QA
  - Math reasoning
  - Classification / extraction workflow
- **可做的增量贡献**：
  - “Workflow auto-tuning”：自动搜索 prompt、模型、routing threshold。
  - 形成平台差异化功能，而不是单篇论文复现。

## 4. 第一阶段落地建议

建议第一阶段不要同时追求所有方向。优先做三条可快速出结果的线：

### 4.1 MoA 工作流模板

**目标**：复现 response-level multi-model collaboration。

**节点拓扑**：

```text
start
  -> llm_agent_1
  -> llm_agent_2
  -> llm_agent_3
  -> response_aggregator
  -> end
```

**可扩展为两层 MoA**：

```text
start
  -> layer1_agent_1 / layer1_agent_2 / layer1_agent_3
  -> layer2_agent_1 / layer2_agent_2 / layer2_agent_3
  -> final_aggregator
  -> end
```

**需要产出**：

- `docs/ModelNet/examples/workflow_mode/moa/` 下的 DSL。
- `dev/modelnet/eval_moa.yaml`。
- accuracy / latency / token cost 表。

### 4.2 Multiagent Debate 工作流模板

**目标**：复现 debate 对 factuality / reasoning 的提升。

**节点拓扑**：

```text
start
  -> proposer_a / proposer_b / proposer_c
  -> critic_round_1_a / critic_round_1_b / critic_round_1_c
  -> revise_round_2_a / revise_round_2_b / revise_round_2_c
  -> judge
  -> end
```

**需要产出**：

- `debate_rounds = 1, 2, 3` 的 ablation。
- `agents = 1, 2, 3` 的 ablation。
- single answer / self-consistency / debate 对比。

### 4.3 Adaptive Routing + RAG

**目标**：复现 RouteLLM / Adaptive-RAG 的成本-效果折中。

**节点拓扑**：

```text
start
  -> query_complexity_classifier
  -> if easy: cheap_llm
  -> if medium: single_rag
  -> if hard: iterative_rag_or_moa
  -> end
```

**需要产出**：

- routing decision trace。
- accuracy-cost Pareto curve。
- routing threshold ablation。

## 5. 第二阶段落地建议

第一阶段跑通后，再做更有 ModelNet 特色的 token-level 方向：

### 5.1 Co-LLM 启发式复现

**目标**：先不训练 router，复现 token-level collaboration 的基本现象。

**节点拓扑**：

```text
start / data-loader
  -> token-model-source(model_a)
  -> token-model-source(model_b)
  -> token-model-source(model_c)
  -> parallel-ensemble(strategy=sum_score|max_score|entropy_router)
  -> end
```

**关键指标**：

- accuracy
- latency
- per-model token contribution
- token-level routing trace

**主要风险**：

- 不同 backend 的 logprob/probability 语义需要对齐。
- OpenAI-compatible backend 的 `top_logprobs` 通常有上限。
- 若要严格复现 learned router，需要训练数据和新增训练流程。

### 5.2 Dynamic RAG

**目标**：复现 Self-RAG / DRAGIN / FLARE 的 inference-time dynamic retrieval。

**推荐先做 FLARE-style MVP**：

```text
question
  -> draft next sentence
  -> confidence / information-need check
  -> retrieve if needed
  -> regenerate sentence
  -> repeat until final answer
```

**原因**：FLARE 不强依赖训练特殊 reflection token，比 Self-RAG 更适合作为平台模板起点。

## 6. 暂不建议优先做的论文类型

| 方向 | 原因 |
|---|---|
| Speculative Decoding | 需要 draft/verify 解码、KV cache 和服务端高效批处理；当前平台短期展示成本较高。 |
| DoLa / layer-contrast decoding | 需要访问模型内部层 logits；外部 API / llama.cpp 普通服务不一定支持。 |
| 大规模 MoE 训练论文 | 训练成本过高，和 Dify workflow 平台能力不直接匹配。 |
| 纯 prompt engineering benchmark | 工程展示弱，平台差异化不足。 |

## 7. 推荐执行顺序

1. **MoA 单层 / 双层复现**  
   最快展示多模型协作，和现有 `response-aggregator` 最匹配。

2. **Multiagent Debate 复现**  
   展示多轮 agent 协作和可解释 trace。

3. **Adaptive-RAG / RouteLLM 复现**  
   展示平台的成本、延迟、质量三目标调度能力。

4. **Co-LLM 启发式 token routing**  
   作为 ModelNet 的 token-level 核心特色。

5. **ARES / ChatEval 自动评测层**  
   把复现实验变成可重复 benchmark，而不是手工演示。

## 8. 参考链接

- [Mixture-of-Agents Enhances Large Language Model Capabilities, ICLR 2025](https://openreview.net/forum?id=h0ZfDIrj7T)
- [Improving Factuality and Reasoning in Language Models through Multiagent Debate, ICML 2024](https://icml.cc/virtual/2024/poster/32620)
- [ChatEval: Towards Better LLM-based Evaluators through Multi-Agent Debate, ICLR 2024](https://openreview.net/pdf?id=FQepisCUWu)
- [RouteLLM: Learning to Route LLMs from Preference Data, ICLR 2025](https://openreview.net/forum?id=8sSqNntaMr)
- [Adaptive-RAG, NAACL 2024](https://aclanthology.org/2024.naacl-long.389/)
- [Learning to Decode Collaboratively with Multiple Language Models, ACL 2024](https://aclanthology.org/2024.acl-long.701/)
- [Self-RAG, ICLR 2024](https://openreview.net/forum?id=hSyW5go0v8)
- [DRAGIN, ACL 2024](https://aclanthology.org/2024.acl-long.702/)
- [Active Retrieval Augmented Generation / FLARE, EMNLP 2023](https://aclanthology.org/2023.emnlp-main.495/)
- [ARES, NAACL 2024](https://aclanthology.org/2024.naacl-long.20/)
- [DSPy, ICLR 2024](https://openreview.net/forum?id=sY5N0zY5Od)
