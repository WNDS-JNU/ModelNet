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

## 4. 方向 B：路由 / 调度研究 ★ → ★★★★

> "input 来了，应该路由到哪个模型 / 子图？"

### 4.1 三条路径速览

| 路径 | 怎么实现 | 难度 | 时间 | Paper 强度 |
|---|---|---|---|---|
| **(1) 纯 DSL 路由** | if-else 节点 + LLM 当 zero-shot 分类器 | ★ | 1 周 | 弱（demo） |
| **(2) fork router 节点** | 写新节点 + 自训练分类器 | ★★★ | 3–4 周 | 中（short paper） |
| **(3) 在线学习 router** | Bandit/RL + Redis 持久状态 + Celery 反馈 | ★★★★ | 2–3 月 | 强（full paper） |

**强烈建议**：先用路径 1 跑通 baseline 验证 idea 有没有 acc/latency 增益；有再投入路径 2/3。AI-ModelNet 论文完全没做路由，**对你是机会点**。

---

### 4.2 路径 1：纯 DSL 路由（最低成本，1 周可交付）

**思路**：用一个轻量 LLM 当 zero-shot 分类器输出 JSON `{"route": "math_path"}`，下接 if-else 节点分流。

**完整 DSL 骨架**：
```
start → llm(router, prompt="判断这题是 math/commonsense/code，返回 JSON")
      → if-else (variable: router.text contains "math")
          ├─ then → llm_chain(SI: Q→D→Y) → end
          └─ else → parallel-ensemble(PI: [Q,D,Y]) → end
```

**关键技巧**：
- router LLM 用最小可用模型（Qwen2.5-3B 即可，alias `29`）
- prompt 里给 3-5 shot 示范，准确率能到 85%+
- 失败 fallback：`if router.text.length < 3 → 默认走 PI`

**第一个本科生项目（1 周）**：复现 if-else 版本，跑 GSM8K + CEVAL，画 (router-on, router-off) 的 acc/latency 散点图。这一周的产出是路径 2/3 的 baseline 比较基线。

---

### 4.3 路径 2：fork router 节点（详解）

**目标**：用专门训练的 ML 分类器替代 zero-shot LLM router，更快、更准、更可控。

#### 4.3.1 架构定位

```
start → model-router(node) → if-else(switch on router.output.route)
                              ├─ branch_A (SI:  Q→D→Y)
                              ├─ branch_B (PI:  [Q,D,Y])
                              └─ branch_C (单模 Q)
                                       ↓
                                     end
```

#### 4.3.2 文件清单（仿 `parallel_ensemble/`）

| 文件 | 作用 |
|---|---|
| `api/core/workflow/nodes/model_router/node.py` | `Node[ModelRouterNodeData]._run()` 协议 |
| `entities.py` | pydantic NodeData schema |
| `exceptions.py` | 自定义异常（如 `ClassifierNotFoundError`） |
| `classifiers/__init__.py` | 分类器注册表 + `@register_classifier` |
| `classifiers/bert.py` | BERT-base 分类器实现 |
| `classifiers/regex.py` | 规则引擎 fallback |
| `classifiers/llm_distilled.py` | 蒸馏的小 LLM 分类器 |

#### 4.3.3 NodeData schema

```python
from typing import Literal
from pydantic import BaseModel
from graphon.nodes.base.entities import NodeData
from graphon.enums import NodeType

class RouteSpec(BaseModel):
    id: str                # 路由 ID（下游 if-else 用这个 switch）
    description: str       # 给训练数据标注用的语义描述
    fallback_priority: int = 0  # confidence 都低时按这个排序选

class ModelRouterNodeData(NodeData):
    type: NodeType = "model-router"
    classifier_type: Literal["bert", "regex", "llm_distilled"] = "bert"
    classifier_path: str = ""        # 权重 / 规则文件路径
    routes: list[RouteSpec]
    confidence_threshold: float = 0.5  # 低于此值走 fallback
    feature_template: str = "{{#start.question#}}"  # 特征提取模板
```

#### 4.3.4 Node._run() 协议

```python
def _run(self) -> Generator[NodeEventBase, None, None]:
    query = self.graph_runtime_state.variable_pool.get(
        self.node_data.feature_template
    )
    classifier = ClassifierRegistry.get(self.node_data.classifier_type)(
        path=self.node_data.classifier_path
    )
    scores = classifier.predict(query)  # {route_id: confidence}
    
    best = max(scores, key=scores.get)
    if scores[best] < self.node_data.confidence_threshold:
        best = min(self.node_data.routes, key=lambda r: r.fallback_priority).id

    yield StreamCompletedEvent(
        node_run_result=NodeRunResult(
            outputs={
                "route": best,            # 下游 if-else switch on this
                "confidence": scores[best],
                "all_scores": scores,
            },
            process_data={"classifier_type": self.node_data.classifier_type},
        )
    )
```

#### 4.3.5 前端 9 处硬编码注册

参考 `docs/ModelNet/ref_dify_workflow_arch.md` 第 6 条 + 之前 `parallel_ensemble` 落地经验。**不会前端没关系**：贴个 `parallel_ensemble` 等价结构给 Claude，30 分钟代写。9 处归类：

| 类别 | 文件 | 改什么 |
|---|---|---|
| Block 注册（3 处必填） | `web/app/components/workflow/types.ts` / `block-selector/constants.tsx` / `nodes/components.ts` | 加 `BlockEnum.ModelRouter` + 挂组件 |
| 节点目录（5 文件必填） | `web/app/components/workflow/nodes/model-router/{default.ts,node.tsx,panel.tsx,types.ts,use-config.ts}` | 仿 parallel-ensemble 写 |
| 输出变量 picker（2 处必填） | `web/app/components/workflow/nodes/_base/components/variable/utils.ts` 的 `formatItem` + `getNodeOutputVars` | 让下游 if-else 节点能看到 router.route 变量 |
| i18n（2 处必填） | `web/i18n/{en-US,zh-Hans}/workflow.json` | 12-15 个 key（label/desc/error msg） |

#### 4.3.6 训练数据从哪来（关键瓶颈）

| 来源 | 怎么用 | 标注成本 |
|---|---|---|
| **论文实验日志反向构造** | 每个 (query, path) → label = "acc 最高且 latency 最低的 path" | 0（自动） |
| **LLM-as-judge 合成** | 让 GPT-4 标注 1000 道题"应该走 SI 还是 PI" | $20-50 |
| **主动学习** | 先用路径 1 baseline 跑，置信度低的拿来人工标注 | 几小时人工 |
| **Reasoning trace 距离** | query 与 paper 题库的 BERT-similarity 投票 | 0（自动） |

数据集 size：500-1000 (query, best_route) 就够 fine-tune BERT-base。AI-ModelNet 论文表 6-7 的实验日志（13 路径 × 3 数据集 × 100 题 = 3900 (query, path, acc, latency) 记录）就是天然训练集。

#### 4.3.7 分类器选择

| 分类器 | 特征 | 准确率 | 推理速度 | 适合 |
|---|---|---|---|---|
| **正则 + 关键词** | 字符串匹配 | 60-70% | μs 级 | 快速 baseline |
| **TF-IDF + LR** | 词袋 | 70-80% | ms 级 | 简单可解释 |
| **BERT-base + LoRA** | 上下文 | 85-92% | 10-30ms | **本科生首选** |
| **LLM-as-router-distill** | full transformer | 90-95% | 100-300ms | 准确率优先 |

#### 4.3.8 评测方法

```python
# baseline_full_pi: 全部走 PI 范式
# router_oracle: 假设 router 100% 正确（acc/latency 上界）
# router_yours:  你训练出的 router

metrics = {
    "acc":            正确率（同 baseline 对比，要 ≥ baseline）,
    "latency_p50":    中位延迟（应 < baseline 全 PI）,
    "latency_p95":    长尾延迟,
    "router_overhead": router 自身耗时（应 < 总延迟 5%）,
    "route_distribution": 各路由实际命中比例（看 router 有没有偏置）,
}
```

**论文必备的 ablation**：
- classifier_type ∈ {regex, BERT, distill}
- confidence_threshold ∈ {0.3, 0.5, 0.7, 0.9}
- 路由数量 ∈ {2, 3, 4, 6, 13}
- training_data_size ∈ {100, 500, 1000, 5000}

#### 4.3.9 第一个本科生项目（4-5 周）

**题目**：Difficulty-Aware Routing for Multi-LLM Collaborative Inference

| 周 | 工作 |
|---|---|
| W1 | 落实路径 1 baseline（DSL + if-else） |
| W2 | 写 model-router 节点（后端 + Claude 代写前端） |
| W3 | 训 BERT 分类器（数据从 PAPER_REPRODUCTION_PLAN 反向构造） |
| W4 | 跑 ablation + 出图 |
| W5 | 写 paper（NLP 工业 track / SLT / 国内顶会） |

**预期 contribution**：在 acc 不降的前提下，平均 latency 比"全部走 PI"降 30-50%，比 zero-shot LLM router 准确 5-15%。

---

### 4.4 路径 3：在线学习 router（详解）

**目标**：router 部署后从用户/任务的 reward 信号持续学习，越用越准。

**为什么更难**（vs 路径 2）：
1. 需要 **reward signal**：query 走完后必须能回流"对不对"
2. 需要 **持久状态**：bandit 的 Q-table / regret 历史要存活过单次 workflow
3. 需要 **exploration**：不能贪心走"目前最好"的 path，否则学不到新东西
4. 需要 **异步反馈管线**：reward 不能阻塞 workflow 主线程

#### 4.4.1 架构

```
请求 ─┬─→ router(选 arm) ─→ 执行 ensemble ─→ 用户/judge 反馈
      │         ↑                                    │
      │    Redis Q-table ←── Celery worker ←─────────┘
      │   (router:bandit:state)     reward signal
      │
      └─ request_id 写入 Redis（router:reward:{rid} TTL 1h）
```

**好消息**：Dify stack 里 **Redis + Celery 已就绪**，不用自己起服务。
- Redis：`api/core/helper/redis_helper.py`
- Celery：`api/tasks/` 下挂任务

#### 4.4.2 Redis 状态 schema

```
KEY                                       VALUE
router:bandit:state                       JSON {arm_id: {count, total_reward, sq_reward}}
router:context:{query_hash}               JSON {features: [...], TTL 30 天}
router:reward:{request_id}                JSON {arm_id, ts, query_hash, TTL 1h}
router:regret:history                     LIST 最近 10000 个 (best_acc - actual_acc)
```

#### 4.4.3 算法选择阶梯

| 算法 | 复杂度 | sample 效率 | 是否用 query 特征 | 适合 |
|---|---|---|---|---|
| **Random** | ★ | 极差 | 否 | sanity check |
| **Epsilon-greedy** | ★ | 差 | 否 | 调通管线第一版 |
| **UCB1** | ★★ | 中 | 否 | 第二版 baseline |
| **Thompson sampling** | ★★ | 好 | 否 | 第三版 |
| **LinUCB（contextual）** | ★★★ | 好 | **是** | **paper 主算法** |
| **Neural bandit** | ★★★★ | 最好 | 是 | 资源充裕时 |
| **PPO / DQN** | ★★★★ | 决策序列长 | 是 | router 决定多步策略时 |

⚠️ **本科生务必从 epsilon-greedy 起步**，跑通管线（reward 能回流、Q-table 真在更新、regret 曲线在下降）再升级。直接上 PPO 99% 会卡 debug。

#### 4.4.4 Reward 信号的 3 种来源

| 来源 | 延迟 | 噪声 | 适合阶段 |
|---|---|---|---|
| **数据集 ground truth** | 离线即时 | 极低 | **本科生先用** |
| **LLM-as-judge** | 一次额外推理（300ms） | 中 | 中期 |
| **用户 thumbs up/down** | 高（人来反馈） | 高（用户偏好≠正确） | 生产环境 |

**关键**：reward 必须 **normalize 到 [0, 1]**，混合来源时加权平均：
```python
reward = 0.6 * acc_signal + 0.3 * latency_signal + 0.1 * cost_signal
```

#### 4.4.5 Celery worker 设计

```python
# api/tasks/router_tasks.py
from celery import shared_task
from core.helper import redis_helper
import json

@shared_task(name="router.process_reward")
def process_router_reward(request_id: str, reward: float):
    redis = redis_helper.get_redis_client()
    record = json.loads(redis.get(f"router:reward:{request_id}") or "{}")
    if not record:
        return  # TTL 过期或没有该 request
    arm = record["arm_id"]
    state = json.loads(redis.get("router:bandit:state") or "{}")
    s = state.setdefault(arm, {"count": 0, "total_reward": 0.0})
    s["count"] += 1
    s["total_reward"] += reward
    redis.set("router:bandit:state", json.dumps(state))
    redis.delete(f"router:reward:{request_id}")  # consumed
```

异步保证 reward 处理不阻塞主 workflow。failure mode：reward 丢失（TTL 过期）→ 默默忽略，不影响下次决策（自然有探索）。

#### 4.4.6 冷启动 3 种策略

| 策略 | 怎么做 | pros / cons |
|---|---|---|
| **强制探索 N 步** | 前 100 次请求 epsilon=1.0，之后 decay 到 0.1 | 简单；前 100 次用户体验差 |
| **离线 prior** | 用路径 2 训好的 BERT 当先验，bandit 微调 | 起步快；需先做完路径 2 |
| **专家规则 prior** | 手写规则给每个 arm 一个初始 count/reward | 中庸；规则可能有偏 |

#### 4.4.7 评测：Regret curve

经典 bandit 评估指标。每次请求记录：
```
regret_t = acc(oracle_arm) - acc(chosen_arm)
cumulative_regret_T = ∑ regret_t for t in [1, T]
```

**期望曲线**：cumulative_regret 关于 T 是 sublinear（典型 √T 或 log(T)）。如果是 linear，说明 bandit 没在学。

跑 10000 个请求，对比：
- **Random** 上界（最差）
- **Oracle** 下界（最好，已知最优 arm）
- **Epsilon-greedy / UCB1 / LinUCB / 你的方法** —— 应在这两条之间

#### 4.4.8 第一个本科生项目（一学期 = 12-16 周）

**题目**：Online Contextual Bandit Routing for Adaptive Multi-LLM Inference

| 阶段 | 周 | 工作 |
|---|---|---|
| Phase 1 | W1-2 | 实现路径 1 baseline + 路径 2 离线 BERT router |
| Phase 2 | W3-5 | 加 model-router 节点 + Redis Q-table + 写 epsilon-greedy |
| Phase 3 | W6-8 | 实现 LinUCB（特征：query embedding + 历史 reward 向量） |
| Phase 4 | W9-11 | 跑 stream 实验：GSM8K 5000 题 / 4 arms / 3 算法对比 |
| Phase 5 | W12-14 | 出 regret curve + ablation（特征维度 / exploration 系数 / cold-start 策略） |
| Phase 6 | W15-16 | 写 paper（投 NeurIPS workshop / EMNLP industry track / ACL ARR） |

**预期 contribution**：
1. 第一个把 contextual bandit 用在 multi-LLM 路由的工作（AI-ModelNet 没做）
2. 在 GSM8K stream 上 cumulative regret 比 epsilon-greedy 低 40-60%
3. 开源 Dify 节点 + bandit 实现（reproducibility）

#### 4.4.9 论文 contribution 选哪个？

| 你的 contribution 落在 | 路径 | Paper venue |
|---|---|---|
| 分类器算法本身（特征工程 / 蒸馏） | 2 | ACL / EMNLP |
| router + ensemble 联合训练 | 2 → 3 | ICLR / NeurIPS |
| 在线学习的 regret 下界 / 算法 | 3 | NeurIPS / ICML |
| 实证 study："query 什么特征决定路由" | 1 + 数据分析 | ACL / EMNLP findings |
| 系统工程（router as a service） | 2/3 | OSDI / SOSP / EuroSys |

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
| 平台架构总图 | `docs/ModelNet/architecture/EXTENSIBILITY_SPEC.md` |
| Phase 历史决策 | `docs/ModelNet/history/DEVELOPMENT_PLAN_v3.md` |
| Capability 语义陷阱 | `api/core/workflow/nodes/parallel_ensemble/spi/capability.py` 的 docstring |
| 怎么写新节点 | `docs/ModelNet/architecture/EXTENSION_GUIDE.md` |
| AI-ModelNet 论文复现具体步骤 | `docs/ModelNet/research/research/PAPER_REPRODUCTION_PLAN.md` |
| token 级算法原型（PN.py） | `docs/ModelNet/research/references/PN.py` |

---

**最后**：本攻略不是 spec，是入场指南。落到代码细节时以 SPI 文件本身（`parallel_ensemble/spi/*.py`）的 docstring 为准——那是被持续维护的合同，本攻略可能过时。

> 如果你卡住了，最快的求救路径：贴出你正在改的 .py 文件 + 报错堆栈，问 Claude Code "我加 X aggregator 报 Y"。
