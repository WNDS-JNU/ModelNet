# ModelNet 平台研究入门攻略

**面向**：计算机本科生（会写 Python，git/pip 用过几次，没碰过 LLM 工程系统）
**目标**：1 学期内基于本仓库做出可复现、可投会的多模型协作推理研究
**贯穿示例**：《Multi-model serial and parallel collaborative inference in AI-ModelNet》（以下简称 **AI-ModelNet 论文**），收录在 `docs/ModelNet/` 同目录

---

## 0. 你为什么要读这份攻略

LLM 多模型协作（Multi-LLM ensemble）正在出会议论文，但门槛在工程而非算法：你要起若干个本地模型服务、拉通 prompt 流、做并联融合、跑评测、画图。从零搭一遍要 3–4 周。

本仓库（Dify fork + ModelNet 二次开发）已经把以下事情**全做完了**：

| 基础设施 | 在哪 | 你拿来直接用 |
|---|---|---|
| 多模型工作流画布（拖拽式） | `web/app/components/workflow/` | UI 拼接 SI/PI/S2P/P2S 拓扑，零代码 |
| 模型清单 + 别名 | `api/configs/model_net.yaml` | 27 个 llama.cpp 端点（含 `expose_raw_logits`） |
| Token 级并联融合节点 | `api/core/workflow/nodes/parallel_ensemble/` | 已实现 sum_score / max_score / **duet_net** 三聚合器 |
| Response 级聚合节点 | `api/core/workflow/nodes/response_aggregator/` | 已实现 concat 策略 + 加权投票框架 |
| Token 模板节点 | `api/core/workflow/nodes/token_model_source/` | 渲染 prompt → 输出 ModelInvocationSpec |
| 实时 trace 面板 | `parallel_ensemble/spi/trace.py` + `AgentLogEvent` | 每 token 步逐步可视化（已自带前端） |
| Eval harness | `dev/modelnet/duet_net_eval.py` | 调 Dify workflow API → 跑 MMLU/CEVAL/SimpleMath/BoolQ → 出 acc/latency/token 表 |
| DSL 模板生成器 | `dev/modelnet/generate_duet_net_dsls.py` | 一行命令批量铺满路径矩阵的 8 个 yml |

**结论**：你的研究只需要**改 1 个扩展点**就能写论文。这份攻略告诉你扩展点在哪、每个方向门槛多高、第一个项目可以是什么。

---

## 1. 一张图认识平台架构

```
┌──────────── workflow DSL（yml）────────────┐
│  start → token-model-source(q1, q2, g4)    │   ← 你能拖拽
│        → parallel-ensemble(duet_net)        │     生成的拓扑
│        → end                                 │
└──────────────────────────────────────────────┘
                     ↓ 解析 / 执行
┌──────── parallel_ensemble 节点 ─────────────┐
│  Runner（解码循环）                          │   ← SPI 1：解码策略
│    ├─ token_step ← 每步取所有 backend 候选  │
│    └─ think_phase ← 处理 think 模型          │
│        ↓                                     │
│  Aggregator（每步选 token）                  │   ← SPI 2：聚合策略
│    ├─ sum_score（加权求 prob）              │
│    ├─ max_score（取 max prob）              │
│    └─ duet_net（论文 PN.py 算法）           │
│        ↓                                     │
│  Backend（模型客户端）                       │   ← SPI 3：后端 / 协议
│    └─ llama_cpp（HTTP /completion）         │
└──────────────────────────────────────────────┘
                     ↓ Capability 声明
        LOGITS_RAW / TOP_PROBS / TOKEN_STEP / CHAT_TEMPLATE …
```

**核心 idea**：每个 SPI 都用 `@register_*` 装饰器注册到全局表。**你新写一个 .py 文件、加一个装饰器，平台就自动识别**。不用改 core、不用改前端、不用改测试 runner。

---

## 2. 研究方向地图

| 方向 | 难度 | 平台扩展点 | 1 学期可做成什么 | AI-ModelNet 对应 |
|---|---|---|---|---|
| **A. 聚合策略** | ★★ | 加 Aggregator 子类 | 新算法 + 论文一篇 short | §3.2 公式 7 / §3.3 公式 9-10 |
| **B. 路由 / 调度** | ★★★ | 新增节点 OR 用现有 if-else | 自适应路由器 + 实验对比 | 论文未涉及（=机会点） |
| **C. 模型选择 / 后端** | ★★ | 加 Backend 子类 + Capability | 接入 vLLM / Ollama，做服务化对比 | §4 (1) 模型选择 |
| **D. 协作拓扑** | ★ | 写 DSL（无代码） | 复现 SI/PI/S2P/P2S + 新拓扑 | 论文 §3 全文 |
| **E. 解码 / Runner** | ★★★★ | 加 EnsembleRunner 子类 | speculative decoding / tree of thoughts ensemble | 论文未涉及 |
| **F. 评测 / 诊断** | ★ | 改 eval harness + trace | Pareto 前沿图 + 错例聚类 | §5 全章 |

**强烈建议本科生先做 A 或 D 方向起步**。

---

## 3. 方向 A：聚合策略研究 ★★

> "现在有 N 个模型对同一个 token 给出 top-k 候选，怎么融合成 1 个 token？"

### 3.1 平台已实现的 3 种聚合器

| 名字 | 算法 | 文件 | 用 Capability |
|---|---|---|---|
| `sum_score` | 加权 ∑ prob，最大者胜 | `aggregators/token/sum_score.py` | TOP_PROBS |
| `max_score` | 取 max(prob)，最大者胜 | `aggregators/token/max_score.py` | TOP_PROBS |
| `duet_net` | τ_K + τ_P 截断 → 候选并集 → raw-logit 求和 → Top-T 采样 | `aggregators/token/duet_net.py` | **LOGITS_RAW** |

### 3.2 你写一个新聚合器需要的全部代码

新建文件 `aggregators/token/your_method.py`：

```python
from parallel_ensemble.registry import register_aggregator
from parallel_ensemble.spi.aggregator import (
    TokenAggregator, BackendAggregationContext, TokenSignals, TokenPick,
)
from parallel_ensemble.spi.capability import Capability
from pydantic import BaseModel

class YourMethodConfig(BaseModel):
    your_hyperparam: float = 0.5

@register_aggregator("your_method", scope="token")
class YourMethodAggregator(TokenAggregator[YourMethodConfig]):
    REQUIRED_CAPABILITIES = (Capability.TOP_PROBS,)  # or LOGITS_RAW

    def aggregate(
        self,
        signals: list[TokenSignals],   # 每个 backend 的 top-k 候选
        context: BackendAggregationContext,
    ) -> TokenPick:
        # 你的算法在这里
        # signals[i].candidates = [{token, prob, logit}, ...]
        # context.weights[i] = backend i 的权重
        winner_token = ...
        return {"token": winner_token, "metadata": {...}}
```

然后在 `aggregators/token/__init__.py` 加一行 `from .your_method import *`。

**完事**。前端 i18n 加 12 个 key（参考 duet_net commit），DSL 里写 `aggregator: your_method` 就能用。

### 3.3 第一个本科生项目（4-6 周）

**题目**：复现并对比 7 种聚合策略

按论文 [42] [43] 列出的 EMNLP/COLING 投票方法，逐个实现成 aggregator：
- 等权多数投票（已有：sum_score 退化版）
- 困惑度加权投票（参考 [42]）
- Span-level 集成（参考 [43]）
- 你自己的方法（比如 token entropy weighting）

跑 AI-ModelNet 论文的 GSM8K/CEVAL/Mathematics 三个数据集，画准确率 + 延迟散点图。**这就是一篇 short paper 的实验部分**。

---

## 4. 方向 B：路由 / 调度研究 ★★★

> "input 来了，应该路由到哪个模型 / 子图？"

### 4.1 平台目前的状态

平台**没有**专门的"router"节点抽象，但有 3 条可走的路：

| 选项 | 怎么实现 | 难度 |
|---|---|---|
| (1) 用现有 if-else 节点 | DSL 里 `if "math" in question → 走 SI；else → 走 PI` | ★ |
| (2) 用 LLM 节点做 zero-shot 分类 | 一个轻量 LLM 当 router，输出走哪条分支 | ★★ |
| (3) 新增 `router` 节点 | 仿 `parallel_ensemble` 写一个 Node 子类 | ★★★★ |

### 4.2 选项 (3) 的扩展点

新增节点参考 `parallel_ensemble/node.py` 结构：
- `node.py` 实现 `Node[YourRouterData]._run()` 协议
- `entities.py` 写 pydantic 配置 schema
- 前端 9 处硬编码注册（见 `docs/ModelNet/ref_dify_workflow_arch.md` 第 6 条）

**注意**：plugin 系统**不能加新节点类型**（见 `node_factory.py:104-108`，注册器只扫 graphon + core.workflow.nodes 两个包）。所以 router 必须以 fork 方式落到 `api/core/workflow/nodes/router/`。

### 4.3 第一个本科生项目（6-8 周）

**题目**：基于 query difficulty 的自适应模型选择

idea：用一个轻量分类器（甚至一个小 LLM 的 perplexity）评估 query 难度，简单 query 走 1 个 7B 模型，难 query 走 PI（3 个 9B 并联）。

先用选项 (1) 写一个 if-else 版本跑 baseline，再用选项 (3) 自己加 router 节点跑 ablation。**对比"猜难度的准确率 vs 总 latency 节省"画 Pareto 曲线**。

这个方向 AI-ModelNet 论文未覆盖，是 **gap = 机会**。

---

## 5. 方向 C：模型 / 后端研究 ★★

> "我的论文要用 vLLM / Ollama / 闭源 API，怎么接？"

### 5.1 现有后端

只有一个：`backends/llama_cpp.py`。它声明的 capabilities：
- `STREAMING`、`TOKEN_STEP`、`TOP_PROBS`、`POST_SAMPLING_PROBS`、`CHAT_TEMPLATE`
- 当 `expose_raw_logits=true` 时还声明 `LOGITS_RAW`

### 5.2 加新后端的 SPI

```python
from parallel_ensemble.registry import register_backend
from parallel_ensemble.spi.backend import ModelBackend, GenerationResult, TokenStepParams
from parallel_ensemble.spi.capability import Capability

@register_backend("vllm")
class VllmBackend(ModelBackend):
    CAPABILITIES = (Capability.STREAMING, Capability.TOP_PROBS, Capability.TOKEN_STEP)

    def generate(self, prompt, params) -> GenerationResult: ...
    def step_token(self, prompt, params: TokenStepParams) -> list[TokenCandidate]: ...
    def apply_template(self, messages) -> str: ...   # 可选，CHAT_TEMPLATE
```

**重点提示**：vLLM 的 `logprobs` 是 log-softmax，不是 raw logits。如果你要做"raw logit 求和"型聚合（如 duet_net），必须 `exp() + 重新归一化`，并**只声明 `TOP_PROBS`，不声明 `LOGITS_RAW`**。这条 trap 写在 `spi/capability.py:13-14`。

### 5.3 第一个本科生项目（4-5 周）

**题目**：对比同模型在 3 种后端上的 PI 表现

挑 1 个开源模型（比如 Qwen2.5-7B）跑：
- 后端 X：llama.cpp（已有）
- 后端 Y：vLLM（你写）
- 后端 Z：HuggingFace TGI（你写）

输出表格：吞吐 / 首 token 延迟 / 每步 logits 数值差异（同 prompt 同 sampler 下）。**这能验证 AI-ModelNet 论文 §5.2 的"路径敏感性"是不是其实是后端实现差异引起的**。

---

## 6. 方向 D：协作拓扑研究 ★

> "把 N 个模型按什么形状串起来，效果最好？"

**这是最低门槛方向**：**你不用写 Python，只用写 yml DSL**。

### 6.1 已落地的 8 份 PI DSL

`docs/ModelNet/examples/workflow_mode/duet_net_*.yml`：
- `duet_net_q1_q2.yml` / `_q1_g4.yml` / `_q2_g4.yml` / `_q1_L3.yml` / `_q2_L3.yml` / `_g4_L3.yml`：6 种 2 模型并联
- `duet_net_q1_q2_g4.yml`：3 模型并联
- `duet_net_q1_q2_g4_L3.yml`：4 模型并联

### 6.2 论文 4 范式 → DSL 映射

| 范式 | 拓扑 | 在 DSL 里长什么样 |
|---|---|---|
| **SI**（串） | M1 → M2 → M3 | 3 个 LLM 节点串行 |
| **PI**（并） | [M1, M2, M3] | 已有 8 份示例 |
| **S2P**（先串后并） | M1 → [M2, M3] | LLM 节点 → 多个 token-model-source → parallel-ensemble |
| **P2S**（先并后串） | [M1, M2] → M3 | 同上反过来：parallel-ensemble → LLM |

**关键事实**：GraphEngine **天然支持并联**——一个节点拉 N 条边到 N 个下游就并发执行（线程池见 `node_factory.py`）。你只需画对边。

### 6.3 第一个本科生项目（2-3 周）

**题目**：复现 AI-ModelNet 论文表 6-7 的路径矩阵

3 模型 = {Q, D, Y}，论文枚举 13 种路径（SI 6 + PI 1 + S2P 3 + P2S 3）。

用 `dev/modelnet/generate_duet_net_dsls.py` 改改模板就能批量铺出 13 个 yml。然后：

```bash
uv run --project api python dev/modelnet/duet_net_eval.py \
    --config dev/modelnet/eval_paper.yaml
```

**两周就能拿到 13 × 3 = 39 组 (acc, latency)，对照论文表 6-7 验证**。这一项就够给毕设/课程项目交付。

---

## 7. 方向 E：解码 / Runner 研究 ★★★★

> "我想做 speculative decoding / tree-of-thoughts / consensus decoding 的多模型版本"

### 7.1 已实现的 Runner

| 名字 | 干什么 | 文件 |
|---|---|---|
| `token_step` | 每步从所有 backend 取 top-k → 喂 aggregator → 选 1 token | `runners/token_step.py` |
| `think_phase` | 处理 `<think>...</think>` 推理段（针对 R1-distill 类模型） | `runners/think_phase.py` |

### 7.2 加新 runner

```python
from parallel_ensemble.registry import register_runner
from parallel_ensemble.spi.runner import EnsembleRunner, SourceInput, TokenEvent

@register_runner("speculative")
class SpeculativeRunner(EnsembleRunner[YourConfig]):
    REQUIRED_CAPABILITIES = (Capability.TOKEN_STEP, Capability.LOGITS_RAW)

    def run(self, sources: list[SourceInput], aggregator, ctx):
        # 你的 draft + verify 解码循环
        yield TokenEvent(...)
```

### 7.3 第一个本科生项目（一学期）

**题目**：多模型 speculative decoding

draft = 3B 小模型快速生成 N 个 token，verify = 3 个 7B 模型并联打分（reuse parallel_ensemble 的 backend pool）。

实现复杂度高（涉及 KV-cache、回滚），但**没有人在 Dify 平台上做过**——是直接出 paper 的方向。参考论文 [12] [45]。

---

## 8. 方向 F：评测 / 诊断研究 ★

> "我不写算法，专门做评测平台 / 错例聚类 / 可视化"

### 8.1 现有 eval harness

`dev/modelnet/duet_net_eval.py`（549 行）：
- 调用 Dify workflow REST API
- 支持 SimpleMath / CEVAL / BoolQ / MMLU
- 输出 acc + token cost + latency
- `--resume` 断点续跑

`dev/modelnet/eval.example.yaml`：配置模板。

### 8.2 你能加的事

| 增量 | 改哪 | 难度 |
|---|---|---|
| 加 GSM8K / MATH 数据集 | `_items_for_dataset()` + `_extract_*()` | ★ |
| 加 token-step 级 trace | 开 `DiagnosticsConfig.enable_trace_stream` 抓日志 | ★ |
| 错例聚类 | trace JSON → 自己写后处理脚本 | ★★ |
| 实时 dashboard | Streamlit / Gradio 读 report.json | ★★ |
| Pareto 前沿图 | matplotlib + report.json | ★ |

### 8.3 第一个本科生项目（4 周）

**题目**：构建多模型协作的 Pareto Dashboard

跑 13 路径 × 3 数据集 = 39 实验，把 (accuracy, latency, $/1k tokens) 三维点画成 Pareto 前沿，让用户能交互式选"我能接受 30s 延迟，最高 acc 是哪条路径"。**这是个工程项目，但能直接当工业界 internship 作品集**。

---

## 9. 你的第一周：从 zero 到跑通一份 DSL

```bash
# Day 1: 起服务
cd /home/xianghe/temp/dify
./dev/start-docker-compose      # 起 Dify 容器（postgres + redis + sandbox）
./dev/start-api                  # 起 API（uv run）
./dev/start-web                  # 起前端（pnpm dev）

# Day 2: 起 1 个 llama.cpp 端点
# 按 dev/modelnet/README.md 的 §1.1 配 q2 alias（Qwen2.5-7B）
# 验证：curl http://<host>:<port>/completion -d '{"prompt":"hi"}'

# Day 3: 把 model_net.yaml 里的 alias "5"（q2）的 model_url 改成你起的端点
# 重启 api，访问 http://localhost:3000，登录

# Day 4: Web 控制台导入 docs/ModelNet/examples/workflow_mode/duet_net_q1_q2.yml
# （把 q1 和 q2 都指向你那个唯一的端点，跑 self-ensemble 也能验证管线）

# Day 5: Web 控制台点 Publish → 拿 API key
# 跑 eval harness：
cp dev/modelnet/eval.example.yaml dev/modelnet/eval_my.yaml
# 编辑 eval_my.yaml 填 API key
uv run --project api python dev/modelnet/duet_net_eval.py \
    --config dev/modelnet/eval_my.yaml --datasets simple_math --n 10
```

**第 1 周末你应该能拿到一份 10 题的 acc/latency 报告**。从这里往任何研究方向走都成本极低。

---

## 10. 常见坑（前人替你踩过）

| 坑 | 现象 | 修法 |
|---|---|---|
| 标准 LLM 节点不读 model_net.yaml | SI/P2S 串联段配不上模型 | Web → Settings → Model Provider 装 OpenAI-Compatible API plugin，再配 3 条端点 |
| llama.cpp `post_sampling_probs=true` ≠ raw logits | duet_net 跑出乱码 | 模型必须 `expose_raw_logits: true` 并跑你 fork 的 llama.cpp |
| 插件不能加新节点 | 写完插件加载不出来 | 必须 fork 进 `api/core/workflow/nodes/`，参考方向 B (3) |
| token_step 拿不到中间 chunk | 下游节点想"逐 token 实时融合"读不到上游 | token 级真协作必须由 parallel_ensemble 节点本身做（"聚合器即执行器"） |
| think 模型 `<think>...</think>` 污染 vote | 准确率反常下降 | runner 用 `think_phase` 而不是 `token_step` |
| chat 模型直接走 raw completion | 模型复读 system prompt | `raw_completion: false`（默认），让 backend 自动套 chat template |
| 13 vs 24 路径数 | 论文声称 24，自己枚举出 13 | 论文按"顺序敏感"展开 S2P/P2S 的并联段；按需选边 |

---

## 11. 写论文之前的 checklist

复现 AI-ModelNet 论文这种工作要投会，至少需要：

- [ ] 实验：方向 D 路径矩阵 + 方向 F 评测产出至少 3 数据集 × 4 范式 × n=100 的 acc/latency 表
- [ ] 算法增量：方向 A 或 E 至少加 1 个 novel 聚合器或 runner（duet_net 已有，所以你不能拿它当 contribution）
- [ ] 诊断：方向 F 的 trace + Pareto 图，证明你的方法在某个 trade-off 维度更好
- [ ] 消融：每个超参 / 每个组件单独 toggle 一遍，画 Fig 12-13 那种敏感性热图
- [ ] 复现包：`dev/modelnet/eval_<your_paper>.yaml` + `paper_*.yml` DSL + 结果 json，全提交

完成上述，你具备投 short paper（NLP/ML 工业 track 类）的硬实力。

---

## 12. 下一步去哪读

| 想了解 | 读这个 |
|---|---|
| 平台架构总图 | `docs/ModelNet/EXTENSIBILITY_SPEC.md` |
| Phase 历史决策 | `docs/ModelNet/DEVELOPMENT_PLAN_v3.md` |
| Capability 语义陷阱 | `api/core/workflow/nodes/parallel_ensemble/spi/capability.py` 的 docstring |
| 怎么写新节点 | `docs/ModelNet/EXTENSION_GUIDE.md` |
| AI-ModelNet 论文复现具体步骤 | `docs/ModelNet/PAPER_REPRODUCTION_PLAN.md` |
| token 级算法原型（PN.py） | `docs/ModelNet/PN.py` |

---

**最后**：本攻略不是 spec，是入场指南。落到代码细节时以 SPI 文件本身（`parallel_ensemble/spi/*.py`）的 docstring 为准——那是被持续维护的合同，本攻略可能过时。

> 如果你卡住了，最快的求救路径：贴出你正在改的 .py 文件 + 报错堆栈，问 Claude Code "我加 X aggregator 报 Y"。
