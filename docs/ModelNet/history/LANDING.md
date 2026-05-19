# ModelNet LANDING 总文档

> 生成时间：2026-05-18
> 来源目录：`/home/duxianghe/dify/docs/ModelNet`
> 整合范围：30 个 `P*_LANDING.md` 分片，包括 `P1.*`、`P2.*`、`P3.A.*`、`P3.B.*`。
> 合并规则：保留原始正文；按阶段重排；原始 H1 转为分片标题；后续 Markdown 标题整体下沉两级；代码块内容不改。

## 阅读入口

- 看整体进展：先读「阶段总览」和「分片索引」。
- 查某次落地的决策、验收命令、文件清单：直接搜索 `P1.3`、`P2.8`、`P3.B.4` 这类编号。
- 旧 `P*_LANDING.md` 分片已删除；需要查旧分片内容时，在本文档中搜索对应编号，例如 `P1.3`、`P2.8`、`P3.B.4`。

## 阶段总览

| 阶段 | 主线 | 覆盖范围 |
| --- | --- | --- |
| Phase 1 | `ensemble_aggregator` 响应级聚合节点 | 后端 schema / strategy / node / 单测，前端包注册 / i18n / 质量门 / DSL smoke |
| Phase 2 | `parallel_ensemble` 与本地模型后端 SPI | `ModelSpec`、`LocalModelRegistry`、`LlamaCppBackend`、runner / aggregator SPI、节点 `_run`、factory 注入、前端配置 UI 和质量门 |
| Phase 3.A | response 聚合升级 | 静态 / 动态 weight、`weighted_majority_vote`、前端 `ui_schema` 反射、测试补齐 |
| Phase 3.B | token 模式重构 | backend SPI 扩展、`token-model-source` 后端 / 前端、`parallel_ensemble` token source 重定位、ship B 收尾测试 |

## 分片索引

| 编号 | 原文件 | 主题 |
| --- | --- | --- |
| `P1.1` | `P1.1_LANDING.md` | P1.1 Landing 报告 — ensemble_aggregator 包骨架 |
| `P1.2` | `P1.2_LANDING.md` | P1.2 Landing 报告 — strategies 子包（base / registry / majority_vote / concat） |
| `P1.3` | `P1.3_LANDING.md` | P1.3 Landing 报告 — EnsembleAggregatorNode._run（节点层串联 VariablePool + strategies） |
| `P1.4` | `P1.4_LANDING.md` | P1.4 Landing 报告 — ensemble_aggregator 后端单测（strategies + node._run with mock VariablePool） |
| `P1.5` | `P1.5_LANDING.md` | P1.5 Landing 报告 — 前端 ensemble-aggregator 包骨架 |
| `P1.6` | `P1.6_LANDING.md` | P1.6 Landing 报告 — 9 处前端注册 + i18n（ensemble-aggregator） |
| `P1.7` | `P1.7_LANDING.md` | P1.7 Landing — Frontend Quality Gate |
| `P1.8` | `P1.8_LANDING.md` | P1.8 Landing — 静态完成 + 2 份响应级 DSL（联调浏览器回归待用户执行） |
| `P2.1` | `P2.1_LANDING.md` | P2.1 Landing — ModelSpec + LocalModelRegistry 单例 |
| `P2.2` | `P2.2_LANDING.md` | P2.2 Landing — LlamaCppBackend + sample yaml + dify_config + BACKEND_CAPABILITIES.md |
| `P2.3` | `P2.3_LANDING.md` | P2.3 Landing — 模型注册表 + LlamaCppBackend 正式单测 + BackendInfo 投影 |
| `P2.4` | `P2.4_LANDING.md` | P2.4 Landing — 控制台 API: models / runners / aggregators 三路由 |
| `P2.5` | `P2.5_LANDING.md` | P2.5 Landing — 后端 aggregators：response + token 双 scope |
| `P2.6` | `P2.6_LANDING.md` | P2.6 Landing — `TokenStepRunner` + `ThinkPhaseRunner` |
| `P2.6.5` | `P2.6.5_LANDING.md` | P2.6.5 Landing — `ResponseLevelRunner` |
| `P2.7` | `P2.7_LANDING.md` | P2.7 Landing — runners + aggregators 单测：确定性 + capability/requirements/trace 路径 |
| `P2.8` | `P2.8_LANDING.md` | P2.8 Landing — `ParallelEnsembleNode._run()`：SPI 化 + 流式事件契约 |
| `P2.9` | `P2.9_LANDING.md` | P2.9 Landing — `node_factory` 注入分支：lazy 共享 executor + 四注册表 + ssrf http_client |
| `P2.10` | `P2.10_LANDING.md` | P2.10 Landing — `ParallelEnsembleNode` 单测：事件序列 + §9 校验 + Trace storage + DSL 偷渡防护 |
| `P2.11` | `P2.11_LANDING.md` | P2.11 Landing — 前端 `parallel-ensemble` 包 + 三轴下拉 + `ui_schema` 反射表单 + DiagnosticsConfig 面板 + 9 处注册 + i18n |
| `P2.12` | `P2.12_LANDING.md` | P2.12 Landing — 前端质量门：TS + lint + 三轴下拉 + DiagnosticsConfig + import-button mock-API 单测 |
| `P3.A.1` | `P3.A.1_LANDING.md` | P3.A.1 Landing — ensemble_aggregator 后端升级 + ADR-v3-8 SPI 切分 |
| `P3.A.2` | `P3.A.2_LANDING.md` | P3.A.2 Landing — ensemble_aggregator 前端升级（response 模式 weight + ui_schema 反射） |
| `P3.A.3` | `P3.A.3_LANDING.md` | P3.A.3 Landing — ensemble_aggregator 测试翻译 + 新增 |
| `P3.B.0` | `P3.B.0_LANDING.md` | P3.B.0 Landing — backend SPI 扩展（ADR-v3-14）+ Aggregation context 切分（ADR-v3-8） |
| `P3.B.1` | `P3.B.1_LANDING.md` | P3.B.1 Landing — `token-model-source` 节点后端（ADR-v3-4 / ADR-v3-10） |
| `P3.B.2` | `P3.B.2_LANDING.md` | P3.B.2 Landing — `token-model-source` 节点前端（ADR-v3-4 / ADR-v3-10） |
| `P3.B.3` | `P3.B.3_LANDING.md` | P3.B.3 Landing — `parallel_ensemble` token 模式重定位（ADR-v3-16） |
| `P3.B.4` | `P3.B.4_LANDING.md` | P3.B.4 Landing — `parallel_ensemble` 前端重构（ADR-v3-16 token 模式） |
| `P3.B.5` | `P3.B.5_LANDING.md` | P3.B.5 Landing — `parallel_ensemble` 测试翻译 + 后端新增（ship B 收尾） |

## Phase 1 - Response-level ensemble_aggregator

### P1.1 - P1.1 Landing 报告 — ensemble_aggregator 包骨架

> Source shard: `P1.1_LANDING.md`


> **日期**：2026-04-18（初始落地） / 2026-04-19（v2.3 review round 2 兜底）
> **对应 TASKS.md**：P1.1
> **对应 DEVELOPMENT_PLAN.md**：§5.3（v2.3 修订后）
> **耗时**：初始 ~30 分钟 + review round 2 ~20 分钟
> **验收**：初始 4/4 绿 + review round 2 schema mini-suite 14/14 绿
> **本次更新**：见 §6 "review round 2 修订（v2.3）"

---

#### 1. 做了什么

##### 1.1 新建三个后端文件

```
api/core/workflow/nodes/ensemble_aggregator/
├── __init__.py     # 包级常量 ENSEMBLE_AGGREGATOR_NODE_TYPE
├── entities.py     # Pydantic 数据模型
└── exceptions.py   # 节点专属异常
```

##### 1.2 文件 1：`__init__.py`

```python
"""Ensemble aggregator workflow node package."""

ENSEMBLE_AGGREGATOR_NODE_TYPE = "ensemble-aggregator"

__all__ = ["ENSEMBLE_AGGREGATOR_NODE_TYPE"]
```

**改动要点**：
- 只导出一个包级常量，**暂不导出 Node 类**（P1.3 再加）
- 包被后端节点扫描器递归 import，不暴露 Node 类可避免循环导入

##### 1.3 文件 2：`entities.py`（v2.3 最终版 — review round 2 加固后）

```python
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from graphon.entities.base_node_data import BaseNodeData
from graphon.enums import NodeType

from . import ENSEMBLE_AGGREGATOR_NODE_TYPE


class AggregationInputRef(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_id: str = Field(..., min_length=1)
    variable_selector: list[str] = Field(..., min_length=2)

    @field_validator("source_id")
    @classmethod
    def _source_id_not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("source_id must not be blank")
        return v

    @field_validator("variable_selector")
    @classmethod
    def _selector_segments_not_blank(cls, v: list[str]) -> list[str]:
        for i, seg in enumerate(v):
            if not seg or not seg.strip():
                raise ValueError(
                    f"variable_selector segment [{i}] must not be blank; "
                    "each segment must be a non-empty identifier"
                )
        return v


class EnsembleAggregatorNodeData(BaseNodeData):
    type: NodeType = ENSEMBLE_AGGREGATOR_NODE_TYPE

    inputs: list[AggregationInputRef] = Field(..., min_length=2)
    strategy_name: Literal["majority_vote", "concat"] = "majority_vote"
    strategy_config: dict[str, object] = Field(default_factory=dict)

    @model_validator(mode="after")
    def _check_source_id_unique(self) -> "EnsembleAggregatorNodeData":
        seen: set[str] = set()
        for ref in self.inputs:
            if ref.source_id in seen:
                raise ValueError(
                    f"Duplicate source_id '{ref.source_id}' in inputs; "
                    "source_id must be unique within a single ensemble-aggregator node"
                )
            seen.add(ref.source_id)
        return self
```

**字段清单**：

| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| `type` | `NodeType` (= str) | 默认 `"ensemble-aggregator"` | graphon 节点注册用 |
| `inputs` | `list[AggregationInputRef]` | `min_length=2` | 上游变量引用列表 |
| `strategy_name` | `Literal["majority_vote", "concat"]` | 默认 `"majority_vote"` | Phase 1 两个策略 |
| `strategy_config` | `dict[str, object]` | 默认 `{}` | 策略专属配置，Phase 1 不强类型化 |

**AggregationInputRef 字段**（v2.3 收紧后）：

| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| `source_id` | `str` | `min_length=1` + 禁纯空白 | 用户定义稳定别名，节点内唯一 |
| `variable_selector` | `list[str]` | `min_length=2` + 每段非空/非纯空白 | graphon 约定 `SELECTORS_LENGTH=2`；第 3 段起是路径，不设 max |
| *（model_config）* | — | `extra="forbid"` | 嵌套 DTO 严格模式，防前端静默吞未知字段 |

##### 1.4 文件 3：`exceptions.py`

四个异常类（base + 3 子类），仿 `agent/exceptions.py:1` 模式，`__init__` 带语义字段便于 catch 端诊断：

```python
class EnsembleAggregatorNodeError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class StrategyNotFoundError(EnsembleAggregatorNodeError):
    def __init__(self, strategy_name: str):
        self.strategy_name = strategy_name
        super().__init__(f"Aggregation strategy '{strategy_name}' is not registered")


class MissingInputError(EnsembleAggregatorNodeError):
    def __init__(self, source_id: str, variable_selector: list[str]):
        self.source_id = source_id
        self.variable_selector = variable_selector
        super().__init__(...)


class StrategyConfigError(EnsembleAggregatorNodeError):
    def __init__(self, strategy_name: str, message: str):
        self.strategy_name = strategy_name
        super().__init__(...)
```

##### 1.5 同步文档改动

- `docs/ModelNet/history/DEVELOPMENT_PLAN_v2.md`：
  - 版本头：`v2` → `v2.2`
  - §5.3 代码块：`source_id` 注释改为"稳定别名"；`inputs` 加 `min_length=2`；`strategy_config` 类型收紧；新增 `@model_validator`
  - 新增 v2.2 修订历史条目
- `docs/ModelNet/active/TASKS.md`：P1.1 标 ✅ 并追加实测结论摘要

---

#### 2. 为什么这么改（六个关键决策）

##### 决策 1：`type` 直接写字符串字面量（不走 `BuiltinNodeTypes`）

**做了什么**：`type: NodeType = ENSEMBLE_AGGREGATOR_NODE_TYPE`（值 `"ensemble-aggregator"`）

**为什么**：
- Phase 0 spike 已实测 `NodeType: TypeAlias = str`（证据 `graphon/enums.py:13`）
- `BuiltinNodeTypes` 是 graphon 内部常量容器（仅给 LLM / IF-ELSE / Code 等**内置**节点用），我们是**下游**扩展节点
- 走字符串字面量避免 fork graphon 添加 enum 成员

**不这么做会怎样**：如果盲目沿用 `BuiltinNodeTypes.XXX` 写法，要么找不到对应成员要 fork graphon（+1 维护负担），要么硬塞进 `BuiltinNodeTypes` 污染命名空间。

##### 决策 2：包级常量 `ENSEMBLE_AGGREGATOR_NODE_TYPE` 独立导出

**做了什么**：在 `__init__.py` 定义常量，`entities.py` 从包 import。

**为什么**：
- 仿仓库内已有模式 `knowledge_index/__init__.py:3`
- P1.3 `node.py` 的 `node_type: ClassVar[NodeType] = ...` 要同一个字符串；P1.5 前端也有镜像；P2.9 `node_factory.py` 加分支也要引用
- 有常量 = 一处定义、多处引用；字面量散落容易手误（比如漏个连字符变成 `"ensemble_aggregator"`，注册失败还难查）

**不这么做会怎样**：三四处散落的 `"ensemble-aggregator"` 字面量，某天改名字就得全文件扫；typo 不会编译期报错（NodeType 是 str）。

##### 决策 3：`source_id` 定为 user-defined stable alias，**不是** upstream node id

**做了什么**：`source_id: str`（语义：用户定义的稳定别名，同一节点内唯一）

**为什么**（这是这一轮最大的决策，值得展开）：
- 方案 A（上游节点 id）的问题：
  - Dify 节点 id 是 UUID（如 `"1729...abc"`），进 `metadata.contributions` 给人读不友好
  - 和 `variable_selector[0]` 信息重复（selector 第一段就是节点 id）
  - 一个上游节点若有多个输出字段被分别聚合，node_id 不够区分
- 方案 B（user-defined alias）的优势：
  - 用户画布上本来就会给 LLM 节点起名（"gpt4" / "claude3" / "llama3"），直接拿来当 alias
  - `metadata.contributions = {gpt4: "...", claude3: "...", llama3: "..."}` 给人读友好
  - 字典序 tie-break 有语义（"claude3" < "gpt4" < "llama3"），不是拿 UUID 字典序乱排
  - 和 `variable_selector` 解耦：selector 是取值路径，source_id 是展示/裁决的稳定 key

**对齐 PN.py**：`model_info.json` 已经是这套思路（每个模型有 `id` 字段作为别名）。

**文档同步**：DEVELOPMENT_PLAN.md v2.1 §5.3 错写成"上游节点 id"，v2.2 已改正。

##### 决策 4：`inputs` 加 `min_length=2`

**做了什么**：`list[AggregationInputRef] = Field(..., min_length=2)`

**为什么**：
- 聚合器语义上"并联至少 2 路"才有意义；1 路聚合等于什么也没做
- 在 Pydantic 层拦截早于 `_run()` 运行期，DSL 导入就会失败，错误信息更友好
- Pydantic v2 `Field(min_length=...)` 语法已确认在本仓库生效（验收 2 绿）

**边界**：如果未来要做"N 路其中 M 路生效"的弹性聚合（比如一路超时忽略），这里限制最小是 2，仍然合理（最终参与聚合至少 1 路就能工作，但**配置**至少 2 路才算并联）。

##### 决策 5：`source_id` 唯一性校验放 `EnsembleAggregatorNodeData`（model_validator）

**做了什么**：`@model_validator(mode="after")` 手动扫描 `inputs`，重复即 `ValueError`。

**为什么**：
- 下游所有环节都默认 `source_id` 唯一：
  - `metadata.contributions[source_id] = text` — 重复会覆盖，丢信息
  - `majority_vote` 并列裁决按 `source_id` 字典序 — 重复破坏确定性
  - 前端 `metadata.contributions` 面板展示 — 重复会渲染重叠行
- 不校验 → 这些问题在运行期才爆，错误信息离根因远
- 放 `EnsembleAggregatorNodeData` 本体 vs 放 `AggregationInputRef`：唯一性是**列表级**约束，只能在外层验；`AggregationInputRef` 只能验单条

**拒绝时机**：DSL 导入 / 前端提交 schema → Pydantic 抛 `ValidationError`（不是我们自定义异常），错误信息包含 "Duplicate source_id 'X'"。

##### 决策 6：`strategy_config: dict[str, object]`（不强类型化）

**做了什么**：`strategy_config: dict[str, object] = Field(default_factory=dict)`

**为什么**：
- Phase 1 只 2 个策略：
  - `majority_vote` 无配置
  - `concat` 只有 `separator: str` + `include_source_label: bool`
- 强类型化要引入 `AggregationStrategyConfig` 基类 + Pydantic Discriminated Union；Phase 1 收益 < 复杂度成本
- P1.2 每个 strategy 自己 parse `strategy_config` 到内部 TypedDict；校验失败抛 `StrategyConfigError`（已建好的异常类）
- 用 `dict[str, object]` 而非 `dict`：
  - 显式类型 + Pyright/mypy 友好
  - `object` 比 `Any` 更严格（强制 type narrow 才能用）

**Phase 2 时**：token-level 有更多策略（sum_score / max_score + top_k / max_len / enable_think），那时再评估是否要 Discriminated Union。

##### 决策 7（额外）：`__init__.py` 暂不导出 Node

**做了什么**：P1.1 只导常量，不导 `EnsembleAggregatorNode`（P1.3 才写）。

**为什么**：
- `api/core/workflow/node_factory.py:96` 会递归 import `api/core/workflow/nodes` 下所有包做节点自动发现
- 包只有 `__init__.py` + `entities.py` + `exceptions.py` 的半成品是**安全的**（只要 `__init__.py` 不去 import 还不存在的 `node.py`）
- 如果 P1.1 就硬塞 `from .node import EnsembleAggregatorNode`，半成品包会让整个后端启动失败
- P1.3 写完 `node.py` 后再追加一行 `from .node import EnsembleAggregatorNode` 即可

---

#### 3. 验收详细结果

##### 命令 1：正常实例化 + model_dump

```bash
uv run --project . python -c "
from core.workflow.nodes.ensemble_aggregator.entities import EnsembleAggregatorNodeData
obj = EnsembleAggregatorNodeData(
    inputs=[{'source_id':'a','variable_selector':['a','text']},
            {'source_id':'b','variable_selector':['b','text']}]
)
print(obj.model_dump())
"
```

**结果**：✅ 绿

```
{'type': 'ensemble-aggregator', 'title': '', 'desc': None, 'version': '1',
 'error_strategy': None, 'default_value': None,
 'retry_config': {'max_retries': 0, 'retry_interval': 0, 'retry_enabled': False},
 'inputs': [{'source_id': 'a', 'variable_selector': ['a', 'text']},
            {'source_id': 'b', 'variable_selector': ['b', 'text']}],
 'strategy_name': 'majority_vote', 'strategy_config': {}}
```

**关键观察**：`BaseNodeData` 继承的公共字段（title/desc/version/error_strategy/default_value/retry_config）自动带上，和其他节点格式一致。

##### 命令 2：min_length=2 被拒

```python
EnsembleAggregatorNodeData(inputs=[{'source_id':'a', 'variable_selector':['a','text']}])
```

**结果**：✅ 绿 — `ValidationError: List should have at least 2 items after validation, not 1`

##### 命令 3：四个异常可导入 + 继承关系正确

```python
from core.workflow.nodes.ensemble_aggregator.exceptions import (
    EnsembleAggregatorNodeError, StrategyNotFoundError,
    MissingInputError, StrategyConfigError,
)
```

**结果**：✅ 绿 — 三个子类都是 `EnsembleAggregatorNodeError` 实例；`__init__` 语义字段（`strategy_name` / `source_id` / `variable_selector`）全部可访问

##### 命令 4：重复 source_id 被拒

```python
EnsembleAggregatorNodeData(inputs=[
    {'source_id':'a','variable_selector':['x','text']},
    {'source_id':'a','variable_selector':['y','text']},
])
```

**结果**：✅ 绿 — `ValidationError: Value error, Duplicate source_id 'a' in inputs; source_id must be unique within a single ensemble-aggregator node`

---

#### 4. 约束与不做

##### 4.1 P1.1 不做

| 项目 | 为什么不做 | 去哪 |
|---|---|---|
| Node `_run()` | 需要 strategies 实例 | P1.3 |
| `majority_vote` / `concat` 策略 | 独立文件易复用 | P1.2 |
| `node_factory.py` 加分支 | 本节点无外部依赖，走默认空 kwargs 分支（Phase 0 Q4 已验） | 不需要 |
| 前端包 / 9 处注册 | 后端稳定后再上前端 | P1.5 – P1.7 |
| 联调 / DSL | 端到端在 Node 完成后 | P1.8 |

##### 4.2 保留的简化（Phase 1 明确接受）

- `strategy_config: dict[str, object]` 而非 Discriminated Union — 策略多了再升级
- 没写 `__repr__` / `__str__` — Pydantic 默认够用
- **顶层 `EnsembleAggregatorNodeData` 仍沿用 `BaseNodeData` 的 `extra="allow"`**（graph 兼容性字段如 `selected` / `params` 需要放行，基类注释明确说明）；**嵌套 `AggregationInputRef` v2.3 收紧成 `extra="forbid"`**（没有兼容性包袱，拼错字段必须在 schema 层就炸）— 两层责任分离
- SSRF 相关强约束留到 Phase 2 `ModelSpec`

---

#### 5. 下一步（P1.2 触发点）

P1.1 落地后阻塞 P1.2 的信息已清：
- `AggregationInputRef.source_id` 和 `AggregationInputRef.variable_selector` 在 strategies 里要读
- `EnsembleAggregatorNodeData.strategy_config` 由每个 strategy 自己解析
- `StrategyNotFoundError` / `StrategyConfigError` 已建好，strategies/registry 可以直接 raise

P1.2 会在 `ensemble_aggregator/strategies/` 下新建：
- `base.py` — `AggregationStrategy` ABC + `AggregationInput` / `AggregationResult` TypedDict
- `registry.py` — `register` 装饰器 + `get_strategy` + `list_strategies`
- `majority_vote.py` — 完全相同字符串投票 + tie-break 字典序
- `concat.py` — separator + include_source_label

---

#### 6. review round 2 修订（v2.3，2026-04-19）

##### 6.1 触发

初版 P1.1 落地后 code review 提出三条意见：

| # | 级别 | 问题 |
|---|---|---|
| 1 | 🔴 Critical | `AggregationInputRef.variable_selector: list[str]` 无字段约束，允许 `[]`/`["x"]`/`[""]` 实例化；运行期才在 `graphon/variable_loader.py` 和 `api/core/workflow/system_variables.py:201` 炸 `Invalid preload selector`（`SELECTORS_LENGTH = 2`）。schema 层应该拦住的错误被推迟到 P1.3 执行期 |
| 2 | 🟡 Suggestion | 嵌套 `AggregationInputRef` 没设 `extra="forbid"`；Pydantic v2 默认 `extra="ignore"`，前端多传/拼错字段被静默吞掉，不利于发现 DSL 漂移 |
| 3 | 🟡 Suggestion | 没有 schema 单测兜底；本包主要价值就是"尽早把坏配置挡在 schema 层"，没测试等于没兜底 |

##### 6.2 取舍

三条都成立，P1.1 范围内兜底修复：

- **Critical 必修**：运行期报错比 schema 报错差一个数量级的 feedback 速度
- **Suggestion #1 顺手修**：顶层 `BaseNodeData.model_config` 注释明确说明 permissive 是 graph 兼容性需求，嵌套 DTO 没这包袱；加一行 `ConfigDict(extra="forbid")` 收紧
- **Suggestion #2 部分前置**：P1.4 原计划做完整单测（策略层 + 节点层），但 schema 校验的最小 suite 应该与 schema 同 PR 落地 — schema 本身的价值就是兜底

##### 6.3 具体修改

**`entities.py`**（diff 概述）：

```diff
-from pydantic import BaseModel, Field, model_validator
+from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

 class AggregationInputRef(BaseModel):
-    source_id: str
-    variable_selector: list[str]
+    model_config = ConfigDict(extra="forbid")
+
+    source_id: str = Field(..., min_length=1)
+    variable_selector: list[str] = Field(..., min_length=2)
+
+    @field_validator("source_id")
+    @classmethod
+    def _source_id_not_blank(cls, v: str) -> str:
+        if not v.strip():
+            raise ValueError("source_id must not be blank")
+        return v
+
+    @field_validator("variable_selector")
+    @classmethod
+    def _selector_segments_not_blank(cls, v: list[str]) -> list[str]:
+        for i, seg in enumerate(v):
+            if not seg or not seg.strip():
+                raise ValueError(
+                    f"variable_selector segment [{i}] must not be blank; "
+                    "each segment must be a non-empty identifier"
+                )
+        return v
```

**不改：** `EnsembleAggregatorNodeData` 本身（顶层保留 `extra="allow"`）、`exceptions.py`、`__init__.py`、`strategy_config` 类型。

##### 6.4 为什么这么做

| 决策 | 理由 |
|---|---|
| 选 `min_length=2` 而不是 `min_length=2, max_length=2` | graphon `SELECTORS_LENGTH=2` 是**最小**要求；第 3 段起是"路径/下标"（`consts.py:9` 注释明文说明）；固定 2 会挡掉后续"取数组第 N 项"等合法场景 |
| `source_id: Field(min_length=1)` + `field_validator` 双保险 | `min_length=1` 只挡 `""`，挡不住 `"  "`；字符串 stripped 非空的语义得写 validator；两者互补 |
| 只收紧嵌套、不收紧顶层 | `BaseNodeData.model_config = ConfigDict(extra="allow")` 是基类显式注释的兼容性需求（`selected` / `params` / `paramSchemas` 等 graph payload 键）；收紧顶层会破掉现有 graph parsing。嵌套 `AggregationInputRef` 是新定义、没历史包袱 |
| schema 测试前置、策略/节点测试留 P1.4 | schema 测试对应 schema 代码的"一次到位"；策略/节点测试需要 P1.2 / P1.3 代码存在才能写 |
| 验证错误 msg 带字段名 + 索引 | 前端 DSL 导入弹错时，`variable_selector segment [1] must not be blank` 比 `list too short` 定位快 |

##### 6.5 验收

```bash
$ cd /home/xianghe/temp/dify/api
$ uv run pytest tests/unit_tests/core/workflow/nodes/ensemble_aggregator/ -v -o addopts=""
============================== 14 passed in 0.07s ==============================
```

14 条覆盖：
1. `test_valid_two_segment_selector` — 标准 `[node_id, field]`
2. `test_valid_path_segments_allowed` — 4 段（含路径）依然通过
3. `test_selector_too_short_rejected` — `["only_one"]`
4. `test_selector_empty_rejected` — `[]`
5. `test_blank_selector_segment_rejected` — `["node", "  "]`
6. `test_empty_selector_segment_rejected` — `["node", ""]`
7. `test_blank_source_id_rejected` — `"  "`
8. `test_empty_source_id_rejected` — `""`
9. `test_extra_field_rejected` — `model_validate` 带未知键
10. `test_defaults_applied` — 节点级默认值 (strategy_name / strategy_config / type)
11. `test_inputs_too_few_rejected` — `inputs` 只有 1 条
12. `test_duplicate_source_id_rejected` — 重复 source_id + 错误消息断言
13. `test_concat_strategy_accepted` — `strategy_name="concat"` + 自定义 config
14. `test_unknown_strategy_name_rejected` — Literal 外的策略名

##### 6.6 P1.4 相应调整

P1.4（后端单测）原计划写所有 ensemble_aggregator 测试；v2.3 已前置 schema 层 14 条。P1.4 剩余：
- 策略层：`majority_vote` / `concat` 的 aggregate 行为
- 节点层：`_run()` 的变量读取 → 策略调用 → 输出装配 → 异常映射 happy path + 错误路径

---

#### 附录：文件变更清单

```
新增（v2.2 初始落地，2026-04-18）:
  api/core/workflow/nodes/ensemble_aggregator/__init__.py
  api/core/workflow/nodes/ensemble_aggregator/entities.py
  api/core/workflow/nodes/ensemble_aggregator/exceptions.py
  docs/ModelNet/P1.1_LANDING.md                           (本文档)

新增（v2.3 review round 2，2026-04-19）:
  api/tests/unit_tests/core/workflow/nodes/ensemble_aggregator/__init__.py
  api/tests/unit_tests/core/workflow/nodes/ensemble_aggregator/test_entities.py   (14 tests)

修改（v2.2）:
  docs/ModelNet/history/DEVELOPMENT_PLAN_v2.md
    - 版本头 v2 → v2.2
    - §5.3 EnsembleAggregatorNodeData 代码块（source_id 注释、min_length、model_validator、strategy_config 类型）
    - 修订历史新增 v2.2 条目
  docs/ModelNet/active/TASKS.md
    - P1.1 标 ✅ + 实测结论摘要

修改（v2.3）:
  api/core/workflow/nodes/ensemble_aggregator/entities.py
    - AggregationInputRef 加 ConfigDict(extra="forbid")
    - source_id: Field(min_length=1) + field_validator 禁纯空白
    - variable_selector: Field(min_length=2) + field_validator 禁空白段
  docs/ModelNet/history/DEVELOPMENT_PLAN_v2.md
    - 版本头 v2.2 → v2.3
    - §5.3 代码块同步（嵌套 ConfigDict + 字段约束 + field_validator）
    - 修订历史新增 v2.3 条目
  docs/ModelNet/P1.1_LANDING.md (本文档)
    - §1.3 entities.py 代码块和字段清单同步到 v2.3
    - §4.2 "保留的简化"条目修订：嵌套已收紧，顶层仍 permissive
    - 新增 §6 "review round 2 修订（v2.3）"
    - 附录清单扩充
```


---

### P1.2 - P1.2 Landing 报告 — strategies 子包（base / registry / majority_vote / concat）

> Source shard: `P1.2_LANDING.md`


> **日期**：2026-04-19（初始落地） / 2026-04-19（review round 2 修订后）
> **对应 TASKS.md**：P1.2
> **对应 DEVELOPMENT_PLAN.md**：§5.3（strategies.base / registry / majority_vote / concat 代码块）
> **耗时**：初始 ~40 分钟 + review round 2 ~10 分钟
> **验收**：初始 smoke 7/7 绿 + review round 2 后 smoke 5/5 绿 + P1.1 schema 回归 14/14 绿
> **前置**：P1.1 v2.3 已落地（`entities.py` + `exceptions.py`），strategies 可直接复用 `AggregationInputRef.source_id` 语义 + `StrategyNotFoundError` / `StrategyConfigError` 异常类
> **本次更新**：见 §6 "review round 2 修订（2026-04-19）"

---

#### 1. 做了什么

##### 1.1 新建 5 个后端文件

```
api/core/workflow/nodes/ensemble_aggregator/strategies/
├── __init__.py        # 触发 @register 生效 + 公共 re-export
├── base.py            # AggregationStrategy ABC + AggregationInput/Result TypedDict
├── registry.py        # register 装饰器 + get_strategy + list_strategies
├── majority_vote.py   # @register("majority_vote")
└── concat.py          # @register("concat")
```

##### 1.2 文件 1：`strategies/base.py`

```python
from abc import ABC, abstractmethod
from typing import ClassVar, TypedDict


class AggregationInput(TypedDict):
    source_id: str
    text: str


class AggregationResult(TypedDict):
    text: str
    metadata: dict[str, object]


class AggregationStrategy(ABC):
    name: ClassVar[str] = ""
    config_schema: ClassVar[dict[str, object]] = {}

    @abstractmethod
    def aggregate(
        self,
        inputs: list[AggregationInput],
        config: dict[str, object],
    ) -> AggregationResult: ...

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name!r})"
```

**接口清单**：

| 成员 | 类型 | 用途 |
|---|---|---|
| `AggregationInput` | `TypedDict` | 节点 `_run()` 从 VariablePool 读完后送进来的单条上游贡献（source_id + text） |
| `AggregationResult` | `TypedDict` | 策略返回；`text` 给节点输出主字段，`metadata: dict[str, object]` 给策略诊断信息 |
| `AggregationStrategy.name` | `ClassVar[str]` | 注册名，由 `@register(name)` 赋值 |
| `AggregationStrategy.config_schema` | `ClassVar[dict[str, object]]` | JSON Schema，供 P1.5 panel UI 自动渲染表单 |
| `AggregationStrategy.aggregate` | abstract | 唯一入口；`config` 是 `EnsembleAggregatorNodeData.strategy_config` 原样透传 |

##### 1.3 文件 2：`strategies/registry.py`

```python
from collections.abc import Callable

from ..exceptions import StrategyNotFoundError
from .base import AggregationStrategy

_REGISTRY: dict[str, type[AggregationStrategy]] = {}


def register(
    name: str,
) -> Callable[[type[AggregationStrategy]], type[AggregationStrategy]]:
    def deco(cls: type[AggregationStrategy]) -> type[AggregationStrategy]:
        existing = _REGISTRY.get(name)
        if existing is not None and existing is not cls:
            raise ValueError(
                f"Strategy '{name}' already registered by {existing.__name__}"
            )
        cls.name = name
        _REGISTRY[name] = cls
        return cls

    return deco


def get_strategy(name: str) -> AggregationStrategy:
    cls = _REGISTRY.get(name)
    if cls is None:
        raise StrategyNotFoundError(name)
    return cls()


def list_strategies() -> list[dict[str, object]]:
    return [
        {"name": cls.name, "config_schema": cls.config_schema}
        for cls in _REGISTRY.values()
    ]
```

**API 清单**：

| 函数 | 签名 | 行为 |
|---|---|---|
| `register(name)` | `(str) -> Callable[[type[S]], type[S]]` | 装饰器工厂；设 `cls.name = name`，写入 `_REGISTRY[name]`；**同名不同类** → `ValueError`；同名同类幂等（pytest 重复 import 安全） |
| `get_strategy(name)` | `(str) -> AggregationStrategy` | 实例化返回；未注册 → `StrategyNotFoundError`（来自 `ensemble_aggregator.exceptions`） |
| `list_strategies()` | `() -> list[dict]` | 返回 `[{name, config_schema}, ...]`；Phase 2 若开放 "策略下拉" API 可直接暴露 |

##### 1.4 文件 3：`strategies/majority_vote.py`（review round 2 后最终版）

```python
from collections import Counter

from pydantic import BaseModel, ConfigDict, ValidationError

from ..exceptions import StrategyConfigError
from .base import AggregationInput, AggregationResult, AggregationStrategy
from .registry import register


class _MajorityVoteConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")


@register("majority_vote")
class MajorityVoteStrategy(AggregationStrategy):
    config_schema = {
        "type": "object",
        "properties": {},
        "additionalProperties": False,
    }

    def aggregate(
        self,
        inputs: list[AggregationInput],
        config: dict[str, object],
    ) -> AggregationResult:
        try:
            _MajorityVoteConfig.model_validate(config)
        except ValidationError as e:
            raise StrategyConfigError("majority_vote", str(e)) from e

        vote_count: Counter[str] = Counter(item["text"] for item in inputs)
        max_votes = max(vote_count.values())
        tied_texts = [t for t, c in vote_count.items() if c == max_votes]

        if len(tied_texts) == 1:
            winner = tied_texts[0]
        else:
            # Tie-break by lexicographically-smallest voting source_id; keeps
            # output deterministic regardless of input order.
            earliest_voter: dict[str, str] = {}
            for item in inputs:
                text = item["text"]
                if text in tied_texts:
                    sid = item["source_id"]
                    if text not in earliest_voter or sid < earliest_voter[text]:
                        earliest_voter[text] = sid
            winner = min(tied_texts, key=lambda t: earliest_voter[t])

        contributions: dict[str, str] = {
            item["source_id"]: item["text"] for item in inputs
        }

        return {
            "text": winner,
            "metadata": {
                "strategy": "majority_vote",
                "votes": dict(vote_count),
                "winner_votes": max_votes,
                "tie_break_applied": len(tied_texts) > 1,
                "contributions": contributions,
            },
        }
```

**行为规格**：

| 场景 | 示例 | 结果 | 说明 |
|---|---|---|---|
| 单票领先 | `[(b,"A"),(c,"A"),(a,"B")]` | `"A"` | `votes={A:2,B:1}`，直接取最多 |
| 并列（2 票 vs 2 票） | `[(c,"Y"),(b,"X"),(a,"X"),(d,"Y")]` | `"X"` | tied {X,Y}；X 最早投者 `a`，Y 最早投者 `c`；`a < c` → X 赢 |
| 全 1 票 | `[(b,"X"),(a,"Y")]` | `"Y"` | tied {X,Y}；X 最早 `b`，Y 最早 `a`；`a < b` → Y 赢 |
| 输入顺序变化 | 上例 source_id 不变、列表顺序打乱 | 恒 `"Y"` | `earliest_voter` 扫一遍决定，和输入 order 无关 |

**metadata 字段**：`strategy` / `votes` / `winner_votes` / `tie_break_applied` / `contributions`（展开每个 source_id → text）。

##### 1.5 文件 4：`strategies/concat.py`

```python
from pydantic import BaseModel, ConfigDict, ValidationError

from ..exceptions import StrategyConfigError
from .base import AggregationInput, AggregationResult, AggregationStrategy
from .registry import register


class _ConcatConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    separator: str = "\n\n---\n\n"
    include_source_label: bool = False


@register("concat")
class ConcatStrategy(AggregationStrategy):
    config_schema = {
        "type": "object",
        "properties": {
            "separator": {"type": "string", "default": "\n\n---\n\n"},
            "include_source_label": {"type": "boolean", "default": False},
        },
        "additionalProperties": False,
    }

    def aggregate(
        self,
        inputs: list[AggregationInput],
        config: dict[str, object],
    ) -> AggregationResult:
        try:
            parsed = _ConcatConfig.model_validate(config)
        except ValidationError as e:
            raise StrategyConfigError("concat", str(e)) from e

        if parsed.include_source_label:
            parts = [f"[{item['source_id']}]\n{item['text']}" for item in inputs]
        else:
            parts = [item["text"] for item in inputs]

        contributions: dict[str, str] = {
            item["source_id"]: item["text"] for item in inputs
        }

        return {
            "text": parsed.separator.join(parts),
            "metadata": {
                "strategy": "concat",
                "separator": parsed.separator,
                "include_source_label": parsed.include_source_label,
                "contributions": contributions,
            },
        }
```

**`_ConcatConfig` 字段**：

| 字段 | 类型 | 默认 | 说明 |
|---|---|---|---|
| `separator` | `str` | `"\n\n---\n\n"` | 拼接分隔符；人类可读分隔对对比三份 LLM 回答很关键 |
| `include_source_label` | `bool` | `False` | 开启时每段前加 `[source_id]\n` 前缀，便于追溯 |
| *(model_config)* | — | `extra="forbid"` | 未知 config 字段 → `ValidationError` → `StrategyConfigError` |

**metadata 字段**：`strategy` / `separator` / `include_source_label` / `contributions`。

##### 1.6 文件 5：`strategies/__init__.py`

```python
from .base import AggregationInput, AggregationResult, AggregationStrategy
from .concat import ConcatStrategy
from .majority_vote import MajorityVoteStrategy
from .registry import get_strategy, list_strategies, register

__all__ = [
    "AggregationInput",
    "AggregationResult",
    "AggregationStrategy",
    "ConcatStrategy",
    "MajorityVoteStrategy",
    "get_strategy",
    "list_strategies",
    "register",
]
```

**改动要点**：
- `from .concat import ConcatStrategy` / `from .majority_vote import MajorityVoteStrategy` 显式触发 `@register` 生效
- `node_factory.py:96-101` 的 `_import_node_package` 用 `pkgutil.walk_packages` **递归** import，app 启动时也会命中这里
- Re-export `get_strategy` / `list_strategies` / `register`，P1.3 `node.py` 可直接 `from .strategies import get_strategy`

##### 1.7 同步文档改动

- `docs/ModelNet/active/TASKS.md`：P1.2 标 ✅ 并追加交付要点（策略清单、smoke 7 条 + 回归 14 条）

---

#### 2. 为什么这么改（七个关键决策）

##### 决策 1：`AggregationStrategy` 用 ABC + `ClassVar`，不走 Protocol

**做了什么**：`AggregationStrategy(ABC)`，`name` / `config_schema` 标 `ClassVar`。

**为什么**：
- `@register` 装饰器要**赋值给 `cls.name`**，Protocol 是结构化类型，没法靠装饰器动态注册
- Phase 1 注册表是"有实体列表、统一 instantiate"的运行期机制，ABC 是合适模型；Protocol 更适合"鸭子类型 + 多态"
- `ClassVar[str]` 比实例属性语义准确：`name` 属于类元信息、不随实例变化；Pyright 可以 narrow

**不这么做会怎样**：如果用 Protocol，`@register("x")` 只能返回原类、拿不到地方写 `name = "x"`；得要求每个策略自己手写 `name: ClassVar[str] = "x"`（双份维护，易漂移）。

##### 决策 2：`register` 装饰器加"同名不同类 → ValueError"幂等 guard

**做了什么**：

```python
existing = _REGISTRY.get(name)
if existing is not None and existing is not cls:
    raise ValueError(f"Strategy '{name}' already registered by {existing.__name__}")
```

**为什么**：
- 纯粹 overwrite（`_REGISTRY[name] = cls` 不 guard）→ 两份 `@register("concat")` 指向不同 class 时，后者悄悄覆盖前者，bug 面大
- `raise ValueError` 在 import 期炸，错误信息带"谁已经占着"，比运行期诡异行为好查
- 允许"同名同类"幂等：pytest 冷启动 / `importlib.reload` 场景不会误伤
- 不选 `StrategyConfigError` / 自定义异常类：这是开发期结构错误（装饰器误用），不是运行期配置错误，用内置 `ValueError` 语义更贴

**不这么做会怎样**：开发者 copy-paste 了 `@register("concat")` 到一个新类试试，结果运行期行为全变了，没人报错——直到测试炸得一头雾水。

##### 决策 3：`majority_vote` tie-break 用"每个 tied 文本的最早投票者 source_id 取最小"算法

**做了什么**：维护 `earliest_voter: dict[text, min_source_id]`，然后 `min(tied, key=lambda t: earliest_voter[t])`。

**为什么**（这是 P1.2 最值得展开的决策）：
- 直觉候选 A：`min(tied_texts)` — 取 text 本身字典序最小。**问题**：text 是 LLM 生成的自然语言，字典序无语义意义（"Yes" < "yes" < "好"），容易给用户反直觉的选择
- 直觉候选 B：`random.choice(tied_texts)` — PN.py 用法。**问题**：破坏确定性，测试难以稳定、重跑结果不一致
- 直觉候选 C：按输入顺序取第一个 tied text。**问题**：依赖调用方传入顺序（frontend 的 `inputs` 顺序是否稳定？节点 reorder 后如何？）
- 本方案：
  - **语义对齐 `source_id` 的"用户稳定别名"角色**（P1.1 决策 3）：用户在画布给 LLM 节点起名 `gpt4` / `claude3` / `llama3`，字典序有业务含义（"claude3" < "gpt4" < "llama3" 对应命名习惯）
  - **确定性**：同 inputs 必出同 winner，无论顺序、无论多次调用
  - **与 concat metadata 语义统一**：两策略都强依赖 `source_id` 作为稳定 key

**具体算法**：扫一遍 `inputs`，对每个 tied text 记录"投给它的 source_id 中最小的那个"；然后在 tied texts 中按这个 key 取最小。O(N) 一次扫描即可。

**不这么做会怎样**：测试期看起来正常（只要输入顺序别变），但 frontend 给 inputs reorder 一下（比如拖动节点），生产环境输出结果会变 — 这种"间歇 bug" 是最难排查的。

##### 决策 4：两个策略都用内部 Pydantic 模型做 config 校验（review round 2 后的最终版）

**做了什么**：

```python
# concat.py
class _ConcatConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    separator: str = "\n\n---\n\n"
    include_source_label: bool = False

# majority_vote.py（review round 2 补齐 — 初始版漏了这层）
class _MajorityVoteConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    # 无字段；extra="forbid" + 空 fields 集 = 任何 key 都被拒
```

每个策略在 `aggregate` 首行调 `_XxxConfig.model_validate(config)`，`ValidationError` 桥接 `StrategyConfigError(name, str(e)) from e`。

**为什么**：
- P1.1 决策 6：`strategy_config: dict[str, object]` 顶层保持 loose；"每个 strategy 自己 parse 到内部 TypedDict；校验失败抛 `StrategyConfigError`"
- TypedDict 不做运行期校验，手写校验代码（类型判定 / 默认注入 / 未知键拒绝）会比 Pydantic 版本长 5-10 行，还容易漏边界
- Pydantic 已在 schema 层深度使用（`AggregationInputRef` / `EnsembleAggregatorNodeData`）；再复用一次不引入新依赖
- `extra="forbid"` 和 `AggregationInputRef` 保持一致的"配置错一个字段也要在 schema 层炸"的设计原则
- `ValidationError → StrategyConfigError(name, str(e)) from e` 做语义桥接：暴露给节点层的是**域内**异常（便于 catch 侧 `isinstance(StrategyConfigError)`），同时 `__cause__` 保留 Pydantic 原始错信息
- **两策略使用相同模式**：`config_schema.additionalProperties: False`（声明层）必须在 runtime 层也有对应 enforcement，不能只是文档——否则 DSL/前端传多余字段会被静默吞掉。majority_vote 虽然 Phase 1 没配置项，但空 `_MajorityVoteConfig(extra="forbid")` 同样把"未知键拒绝"这层行为钉住，未来加配置只需加字段、不需改架构

**不这么做会怎样**：手写校验，下一次 config 加字段（例如 `max_length`）要动 3-4 处逻辑；Pydantic 模式加一行字段就完。

##### 决策 5：`config_schema` 用 JSON Schema（含 `additionalProperties: false`）

**做了什么**：

```python
config_schema = {
    "type": "object",
    "properties": {"separator": {"type": "string", "default": "..."}, ...},
    "additionalProperties": False,
}
```

**为什么**：
- P1.5 panel UI 要动态渲染配置表单；JSON Schema 是前端渲染器（如 `@rjsf/core`）的事实标准
- `additionalProperties: false` 让前端表单构建器明确"不允许用户塞未知字段"，和 `_ConcatConfig.extra="forbid"` 两层对齐
- 带 `default` 给前端"空 config 时填默认占位"的提示
- `majority_vote.config_schema = {type: object, properties: {}, additionalProperties: false}` 显式表达"无配置项"——比空 dict `{}` 语义明确（空 dict 可能被前端误解为 "schema 缺失"）

**不这么做会怎样**：P1.5 前端每个策略都要硬编码配置表单，每加一个策略前端都要改；和 `list_strategies()` 后端返回的 schema 无关，信息分叉。

##### 决策 6：`metadata.contributions` 作为每个策略的默认字段

**做了什么**：两个策略都在 `metadata` 里带 `contributions: {source_id: text, ...}`。

**为什么**：
- DEVELOPMENT_PLAN.md §5.1 节点输出约定：`metadata.contributions`（每个上游贡献了什么）——是前端面板展示的关键信息
- 放在策略层产出、不在节点层再构造一次：避免节点层重复跑一遍 inputs 迭代；职责明确（策略输出自带诊断）
- `dict[str, str]` 顺序 = 迭代 `inputs` 顺序，frontend 可以拿到确定性展示

**不这么做会怎样**：节点层要重新扫一遍 inputs 补 metadata，代码重复且可能和策略诊断其他信息（`votes` / `separator`）风格不一致。

##### 决策 7：`strategies/__init__.py` 显式 re-export 4 个模块

**做了什么**：`__init__.py` 主动 import `base` / `concat` / `majority_vote` / `registry`，并全量 re-export。

**为什么**：
- `node_factory.py:96` 的 `_import_node_package` 用 `walk_packages` 递归 import **所有**子模块，本包启动时会遍历每个 .py 文件、触发 `@register` 装饰器
- 但测试 / 直接 import 场景（如 `from ...strategies import get_strategy`）只会运行 `strategies/__init__.py`；若 `__init__.py` 不主动 import 策略模块，测试期 `_REGISTRY` 会为空 → `get_strategy("concat")` 失败
- 两条路径都能让注册生效，避免"跑测试注册不了策略"这种心智负担
- `__all__` 显式列表 = Pyright / 静态检查器能准确推断 re-export 的 public surface，不会把 implementation detail（如 `_REGISTRY`）混进来

**不这么做会怎样**：某天有人写 `from core.workflow.nodes.ensemble_aggregator.strategies import get_strategy` 在 notebook 里试着跑，`StrategyNotFoundError: concat` 一头雾水。

---

#### 3. 验收详细结果

##### 命令 1：注册成功 + list_strategies

```python
from core.workflow.nodes.ensemble_aggregator.strategies import list_strategies
print(sorted(s["name"] for s in list_strategies()))
```

**结果**：✅ 绿 — `['concat', 'majority_vote']`

##### 命令 2：majority_vote 基本投票（`[A,A,B]` → `A`）

```python
r = get_strategy('majority_vote').aggregate(
    [{'source_id':'b','text':'A'},
     {'source_id':'c','text':'A'},
     {'source_id':'a','text':'B'}],
    {},
)
```

**结果**：✅ 绿
- `r['text'] == 'A'`
- `r['metadata']['votes'] == {'A': 2, 'B': 1}`
- `r['metadata']['tie_break_applied'] is False`

##### 命令 3：majority_vote 字典序 tie-break

```python
r = get_strategy('majority_vote').aggregate(
    [{'source_id':'c','text':'Y'},
     {'source_id':'b','text':'X'},
     {'source_id':'a','text':'X'},
     {'source_id':'d','text':'Y'}],
    {},
)
```

**结果**：✅ 绿
- X/Y 各 2 票；X 最早投者 `a`，Y 最早投者 `c`；`a < c`
- `r['text'] == 'X'`
- `r['metadata']['tie_break_applied'] is True`

##### 命令 4：concat 默认分隔符

```python
r = get_strategy('concat').aggregate(
    [{'source_id':'a','text':'hello'}, {'source_id':'b','text':'world'}],
    {},
)
```

**结果**：✅ 绿 — `r['text'] == 'hello\n\n---\n\nworld'`（默认 `"\n\n---\n\n"` 生效）

##### 命令 5：concat 自定义 + `include_source_label`

```python
r = get_strategy('concat').aggregate(
    [{'source_id':'a','text':'hello'}, {'source_id':'b','text':'world'}],
    {'separator': ' | ', 'include_source_label': True},
)
```

**结果**：✅ 绿 — `r['text'] == '[a]\nhello | [b]\nworld'`

##### 命令 6：concat 未知 config 字段 → `StrategyConfigError`

```python
get_strategy('concat').aggregate([...], {'unknown_key': 1})
```

**结果**：✅ 绿 — `StrategyConfigError: Invalid config for strategy 'concat': 1 validation error for _ConcatConfig ...`
- `extra="forbid"` 层拒绝
- `__cause__` 保留 Pydantic `ValidationError` 原文

##### 命令 7：`get_strategy('nope')` → `StrategyNotFoundError`

**结果**：✅ 绿 — `StrategyNotFoundError: Aggregation strategy 'nope' is not registered`（P1.1 exceptions 直接对接成功）

##### 命令 8：幂等 guard — `@register("majority_vote")` 用到新类 → `ValueError`

```python
class Bogus(AggregationStrategy):
    def aggregate(self, inputs, config): ...
register('majority_vote')(Bogus)
```

**结果**：✅ 绿 — `ValueError: Strategy 'majority_vote' already registered by MajorityVoteStrategy`

##### 命令 9：P1.1 schema 层回归（`test_entities.py`）

```bash
$ uv run pytest tests/unit_tests/core/workflow/nodes/ensemble_aggregator/ -v -o addopts=""
============================== 14 passed in 0.06s ==============================
```

**结果**：✅ 绿 14/14 — P1.2 新增不破坏 entities schema 层

##### 命令 10：majority_vote 未知 config 字段 → `StrategyConfigError`（review round 2 新增）

```python
get_strategy('majority_vote').aggregate(
    [{'source_id':'a','text':'A'}, {'source_id':'b','text':'A'}],
    {'unexpected': 1},
)
```

**结果**：✅ 绿（review round 2 修订后）— `StrategyConfigError: Invalid config for strategy 'majority_vote': 1 validation error for _MajorityVoteConfig ...`
- 修订前：**返回成功结果**（config 未校验、未知键被静默忽略），与 `config_schema.additionalProperties: False` 的声明直接冲突
- 修订后：`_MajorityVoteConfig(extra="forbid")` 拦截；`__cause__` 保留 Pydantic `ValidationError` 原文
- 同时覆盖 "多个未知键"（`{'foo': None, 'bar': 2}`）场景 → 一次性报告全部错误；"空 config" 回归路径保持（`{}` 仍正常返回 winner）

---

#### 4. 约束与不做

##### 4.1 P1.2 不做

| 项目 | 为什么不做 | 去哪 |
|---|---|---|
| Node `_run()` | 需要把策略串进 VariablePool 读取 + StreamCompletedEvent 事件协议 | P1.3 |
| 策略层完整单测文件（`test_majority_vote` / `test_concat`） | TASKS.md P1.4 专门收口策略 + 节点单测 | P1.4 |
| 更多策略（semantic vote / LLM-as-judge / Levenshtein） | Phase 1 非目标；`register` + `config_schema` 已打通扩展路径 | Phase 2+ |
| 前端 `strategy-selector.tsx` | 后端稳定后再上前端 | P1.5 |
| DSL 导入时的 `strategy_config` ↔ `config_schema` 端到端校验 | 属于 P1.5 panel UI 和 P1.4 节点层联合验收 | P1.5 / P1.4 |

##### 4.2 保留的简化（Phase 1 明确接受）

- `majority_vote` 只做"完全相同字符串"投票；semantic / sentence-bert / fuzzy match 留 Phase 2+
- `concat.config_schema` 没有 JSON Schema `maxLength` / pattern 约束 — Phase 1 够用，前端输入校验 P1.5 再精细化
- `AggregationResult.metadata: dict[str, object]` 是弱类型——未来如果有策略间统一 metadata 协议（如 `ensemble_metadata_version`），再提取
- `register` 没做卸载 / 替换 API（仅 register once + optional 幂等），热更新策略的场景留到需要时

##### 4.3 算法边界说明（`majority_vote`）

| 情形 | 行为 |
|---|---|
| 全部文本唯一 | 每个 text 1 票；tied；按 earliest_voter 字典序裁决 |
| 空 `inputs` | `max([])` 抛 `ValueError`（schema 层 `min_length=2` 保证不会发生；节点内部代码不重复防御） |
| 某 input `text=""` | `""` 作为正常字符串参与投票；语义上"空回复"是一个可能的 winner（决定是否过滤留给调用方） |
| 所有文本相同 | tied={唯一 text}；`len(tied)==1` 短路；`tie_break_applied=False` |

---

#### 5. 下一步（P1.3 触发点）

P1.2 落地后阻塞 P1.3 的信息已清：

- **策略调用接口稳定**：`get_strategy(name).aggregate(inputs, config)` → `AggregationResult`
- **输入形态**：节点层要把 `AggregationInputRef` 解析后的 `(source_id, text)` 拼成 `list[AggregationInput]` 送进策略
- **输出形态**：`AggregationResult.text` → `outputs.text`；`AggregationResult.metadata` → `outputs.metadata`
- **异常路径**：`StrategyNotFoundError` / `StrategyConfigError` / `MissingInputError`（P1.1 已建好）供节点层映射到 `NodeRunResult(status=FAILED)`

P1.3 要做的：
- 新建 `node.py`：`EnsembleAggregatorNode(Node[EnsembleAggregatorNodeData])`
- `_run()` 顺序：
  1. 按 `inputs[].variable_selector` 从 `graph_runtime_state.variable_pool` 取上游文本
  2. 拼 `list[AggregationInput]`（`source_id` + `text=str(seg.value)`）
  3. `get_strategy(strategy_name).aggregate(inputs, strategy_config)`
  4. 单个 yield `StreamCompletedEvent(node_run_result=NodeRunResult(SUCCEEDED, outputs={text, metadata}, inputs={source_count, strategy}))`
- `__init__.py` 追加 `from .node import EnsembleAggregatorNode`（此时半成品包才正式完工）

---

#### 6. review round 2 修订（2026-04-19）

##### 6.1 触发

初版 P1.2 落地后 code review 指出 1 条 Critical：

| # | 级别 | 问题 |
|---|---|---|
| 1 | 🔴 Critical | `MajorityVoteStrategy` 声明 `config_schema.additionalProperties: False`，但 `aggregate` 里完全没有校验 `config`。传 `{"unexpected": 1}` 会被静默接受并返回成功结果；和 P1.2 "每个 strategy 自己 parse/validate" 的原则直接冲突，也破坏了和 `ConcatStrategy` 的对称性 |

**复现**（修订前行为）：

```python
get_strategy("majority_vote").aggregate(
    [{"source_id": "a", "text": "A"}, {"source_id": "b", "text": "A"}],
    {"unexpected": 1},
)
# 返回 {'text': 'A', 'metadata': {...}} — 预期应抛 StrategyConfigError
```

##### 6.2 取舍

**Critical 必修**，原因：
- 和 P1.1 v2.3 修的是**同一类 bug**：schema 声明（`additionalProperties: False`）与运行期行为不一致，错误被推迟到"更后面"暴露
- DSL / 前端迁移期最容易触发（前端换字段名、用户改 DSL 改错键），静默吞掉意味着用户得不到即时反馈
- 修复成本极低：加一个空 Pydantic 模型 + 3 行调用，不动其他文件

##### 6.3 具体修改

`strategies/majority_vote.py`（diff 概述）：

```diff
 from collections import Counter

+from pydantic import BaseModel, ConfigDict, ValidationError
+
+from ..exceptions import StrategyConfigError
 from .base import AggregationInput, AggregationResult, AggregationStrategy
 from .registry import register


+class _MajorityVoteConfig(BaseModel):
+    model_config = ConfigDict(extra="forbid")
+
+
 @register("majority_vote")
 class MajorityVoteStrategy(AggregationStrategy):
     config_schema = {
         "type": "object",
         "properties": {},
         "additionalProperties": False,
     }

     def aggregate(
         self,
         inputs: list[AggregationInput],
         config: dict[str, object],
     ) -> AggregationResult:
+        try:
+            _MajorityVoteConfig.model_validate(config)
+        except ValidationError as e:
+            raise StrategyConfigError("majority_vote", str(e)) from e
+
         vote_count: Counter[str] = Counter(item["text"] for item in inputs)
```

**不改**：`concat.py`（已有对应实现）、`base.py` / `registry.py` / `strategies/__init__.py` / entities / exceptions。

##### 6.4 为什么这么做

| 决策 | 理由 |
|---|---|
| 用 Pydantic 空模型而非手写 `if config: raise ...` | 与 `_ConcatConfig` 完全对称；新增字段只需加一行；`__cause__` 天然带 Pydantic 原始错，便于前端展示字段级错误 |
| `StrategyConfigError` 而非 `ValueError` | 这是**运行期配置错误**（DSL/前端传错），与 P1.2 决策 2 的"开发期结构错误用 `ValueError`"区分开；便于 P1.3 节点层 `try/except StrategyConfigError` 做统一错误映射 |
| `_MajorityVoteConfig` 当前空字段 | Phase 1 `majority_vote` 无配置项；留占位符为未来扩展（如 `case_sensitive: bool` / `normalize_whitespace: bool`）留接口，加字段时不改架构 |
| 不重构出 base class 级统一校验 helper | 只有 2 个策略、模式很清晰；抽象成 `AggregationStrategy._validate_config(model_cls)` 是纯 DRY 式重构，当前带不来额外价值（决策 4 中也明确 Phase 2 策略增多后再评估） |

##### 6.5 验收

```bash
$ uv run --project . python -c "…命令 10…"
review case raises OK: Invalid config for strategy 'majority_vote': 1 validation error for _MajorityVot…
empty config OK -> text=A
multi-extras raise OK: Invalid config for strategy 'majority_vote': 2 validation errors for _MajorityVo…
tie-break regression OK -> text=X
concat regression OK: Invalid config for strategy 'concat': 1 validation error for _ConcatConfig …
ALL SMOKE GREEN

$ uv run pytest tests/unit_tests/core/workflow/nodes/ensemble_aggregator/ -v -o addopts=""
============================== 14 passed in 0.05s ==============================
```

5 条 review-round-2 smoke 覆盖：
1. review case：`{'unexpected': 1}` → `StrategyConfigError`
2. 空 config：`{}` 仍正常返回 winner（不过度防御）
3. 多个未知键：`{'foo': None, 'bar': 2}` → 一次报告 2 个错
4. tie-break 回归：算法未受影响
5. concat 回归：仍然按 `extra="forbid"` 拒绝，两策略行为对称

P1.1 schema 层 14/14 同步跑了一次，无回归。

##### 6.6 对后续阶段的影响

- **P1.3（节点层）**：`_run()` 里 `get_strategy(...).aggregate(inputs, config)` 现在会透出 `StrategyConfigError`；节点层异常处理分支需要把这个 catch 成 `NodeRunResult(status=FAILED)`
- **P1.4（策略/节点单测）**：`test_majority_vote` 要加一条 "unknown config key rejected" 测试（完全对称 `test_concat` 的同名测试）
- **P1.5（前端 panel）**：`config_schema.additionalProperties: False` 现在后端有对应 runtime 兜底；前端可以在 submit 前用同一 schema 做预检，两层对齐

---

#### 附录：文件变更清单

```
新增（P1.2 初始，2026-04-19）:
  api/core/workflow/nodes/ensemble_aggregator/strategies/__init__.py
  api/core/workflow/nodes/ensemble_aggregator/strategies/base.py
  api/core/workflow/nodes/ensemble_aggregator/strategies/registry.py
  api/core/workflow/nodes/ensemble_aggregator/strategies/majority_vote.py
  api/core/workflow/nodes/ensemble_aggregator/strategies/concat.py
  docs/ModelNet/P1.2_LANDING.md                                         (本文档)

修改（P1.2 初始，2026-04-19）:
  docs/ModelNet/active/TASKS.md
    - P1.2 标 ✅ 并追加交付要点（5 文件清单 / tie-break 算法要点 / smoke 7 条 / 回归 14 条）

修改（review round 2，2026-04-19）:
  api/core/workflow/nodes/ensemble_aggregator/strategies/majority_vote.py
    - 新增 _MajorityVoteConfig(BaseModel, extra="forbid")
    - aggregate() 首行 model_validate → StrategyConfigError 桥接
    - 解决静默吞未知 config 键的 Critical
  docs/ModelNet/P1.2_LANDING.md (本文档)
    - 头部日期 / 验收计数更新
    - §1.4 代码块同步到最终版
    - §2 决策 4 标题和 Pydantic 模型清单扩展到两策略
    - §3 新增命令 10（majority_vote 拒绝未知 config）
    - 新增 §6 "review round 2 修订"
    - 本附录扩充

未动:
  api/core/workflow/nodes/ensemble_aggregator/{__init__.py, entities.py, exceptions.py}   (P1.1 v2.3 稳态)
  api/core/workflow/nodes/ensemble_aggregator/strategies/{base,registry,concat,__init__}.py (P1.2 初始稳态)
  api/tests/unit_tests/core/workflow/nodes/ensemble_aggregator/test_entities.py           (P1.1 v2.3 稳态，用作回归 baseline)
  docs/ModelNet/history/DEVELOPMENT_PLAN_v2.md                                                        (P1.2 仅实施、未改计划；§5.3 策略代码块是 sketch，实现版细节靠本文档承载)
```


---

### P1.3 - P1.3 Landing 报告 — EnsembleAggregatorNode._run（节点层串联 VariablePool + strategies）

> Source shard: `P1.3_LANDING.md`


> **日期**：2026-04-19（初始落地） / 2026-04-19（review round 2 修订后）
> **对应 TASKS.md**：P1.3
> **对应 DEVELOPMENT_PLAN.md**：§5.2（节点生命周期） / §5.4（节点 `_run()` 代码块 sketch）
> **耗时**：初始 ~25 分钟 + review round 2 ~20 分钟
> **验收**：初始 smoke 6/6 绿 + review round 2 后 pytest 21/21 绿（P1.1 schema 14 + P1.3 新增回归 7）
> **前置**：P1.1 v2.3（`entities.py` / `exceptions.py`）+ P1.2 v2 review round 2（`strategies/` 子包）均已稳态落地
> **本次更新**：见 §6 "review round 2 修订（2026-04-19）"

---

#### 1. 做了什么

##### 1.1 新建 / 修改 3 个文件

```
api/core/workflow/nodes/ensemble_aggregator/
├── __init__.py                  # 追加 EnsembleAggregatorNode re-export
└── node.py                      # 新建 — EnsembleAggregatorNode 全部实现

api/tests/unit_tests/core/workflow/nodes/ensemble_aggregator/
└── test_node.py                 # 新建 — P1.3 review round 2 窄范围回归（7 条）
```

##### 1.2 文件 1：`ensemble_aggregator/node.py`（review round 2 后最终版）

```python
import logging
from collections.abc import Generator, Mapping, Sequence
from typing import Any, ClassVar

from graphon.enums import NodeType, WorkflowNodeExecutionStatus
from graphon.node_events.base import NodeEventBase, NodeRunResult
from graphon.node_events.node import StreamCompletedEvent
from graphon.nodes.base.node import Node

from . import ENSEMBLE_AGGREGATOR_NODE_TYPE
from .entities import EnsembleAggregatorNodeData
from .exceptions import (
    EnsembleAggregatorNodeError,
    MissingInputError,
)
from .strategies import AggregationInput, get_strategy

logger = logging.getLogger(__name__)


class EnsembleAggregatorNode(Node[EnsembleAggregatorNodeData]):
    node_type: ClassVar[NodeType] = ENSEMBLE_AGGREGATOR_NODE_TYPE

    @classmethod
    def version(cls) -> str:
        return "1"

    def _run(self) -> Generator[NodeEventBase, None, None]:
        node_data = self.node_data
        strategy_name = node_data.strategy_name
        declared_source_count = len(node_data.inputs)

        try:
            aggregation_inputs = self._collect_inputs()
            strategy = get_strategy(strategy_name)
            result = strategy.aggregate(aggregation_inputs, node_data.strategy_config)
        except EnsembleAggregatorNodeError as e:
            logger.warning(
                "EnsembleAggregatorNode %s failed: %s", self._node_id, e, exc_info=True
            )
            yield StreamCompletedEvent(
                node_run_result=NodeRunResult(
                    status=WorkflowNodeExecutionStatus.FAILED,
                    inputs={
                        "source_count": declared_source_count,
                        "strategy": strategy_name,
                    },
                    error=str(e),
                    error_type=type(e).__name__,
                ),
            )
            return

        yield StreamCompletedEvent(
            node_run_result=NodeRunResult(
                status=WorkflowNodeExecutionStatus.SUCCEEDED,
                inputs={
                    "source_count": len(aggregation_inputs),
                    "strategy": strategy_name,
                },
                outputs={
                    "text": result["text"],
                    "metadata": result["metadata"],
                },
            ),
        )

    def _collect_inputs(self) -> list[AggregationInput]:
        variable_pool = self.graph_runtime_state.variable_pool
        collected: list[AggregationInput] = []
        for ref in self.node_data.inputs:
            segment = variable_pool.get(ref.variable_selector)
            if segment is None:
                raise MissingInputError(
                    source_id=ref.source_id,
                    variable_selector=list(ref.variable_selector),
                )
            # Use Segment.text (graphon canonical text rendering) rather than
            # str(segment.value): the former normalizes NoneSegment -> "",
            # ObjectSegment/ArrayStringSegment -> JSON, empty arrays -> "",
            # keeping this node aligned with how graphon's other nodes render
            # variables.
            collected.append({"source_id": ref.source_id, "text": segment.text})
        return collected

    @classmethod
    def _extract_variable_selector_to_variable_mapping(
        cls,
        *,
        graph_config: Mapping[str, Any],
        node_id: str,
        node_data: EnsembleAggregatorNodeData,
    ) -> Mapping[str, Sequence[str]]:
        # Expose each input's upstream selector to the draft-variable preload
        # path (workflow_entry / workflow_app_runner). source_id is unique per
        # node (enforced in entities.py), so {node_id}.inputs.{source_id} is a
        # stable unique key — same shape as knowledge_retrieval_node.py:314.
        return {
            f"{node_id}.inputs.{ref.source_id}": list(ref.variable_selector)
            for ref in node_data.inputs
        }
```

**方法 / 属性清单**：

| 成员 | 签名 / 类型 | 用途 |
|---|---|---|
| `node_type` | `ClassVar[NodeType]` = `ENSEMBLE_AGGREGATOR_NODE_TYPE` | graphon `__init_subclass__` 用作注册表 key（字符串 `"ensemble-aggregator"`） |
| `version()` | `@classmethod -> "1"` | graphon 要求每个节点版本唯一；Phase 1 初版 |
| `_run()` | `-> Generator[NodeEventBase, None, None]` | 单 yield `StreamCompletedEvent`；domain 异常 → FAILED，未预期异常让基类兜底 |
| `_collect_inputs()` | `-> list[AggregationInput]` | 按 `inputs[].variable_selector` 从 VariablePool 取 Segment；缺失 → `MissingInputError`；**用 `segment.text`** 归一化文本 |
| `_extract_variable_selector_to_variable_mapping()` | `@classmethod` | 每条 input 映射到 `{node_id}.inputs.{source_id}`；供单步调试 / draft preload 预加载链路使用 |

**输入契约**（由 P1.1 entities 保证）：

| 字段 | 规则 |
|---|---|
| `inputs` | `list[AggregationInputRef]`，`min_length=2` |
| `inputs[i].source_id` | 非空、`min_length=1`、节点内唯一；`AggregationInputRef.model_config extra="forbid"` |
| `inputs[i].variable_selector` | `list[str]`，`min_length=2`；段级非空；前两段是 `[node_id, var_name]`，后续段是嵌套路径 |
| `strategy_name` | `Literal["majority_vote", "concat"]`，默认 `"majority_vote"` |
| `strategy_config` | `dict[str, object]`，顶层 loose；`extra="forbid"` 在每个策略的内部 Pydantic 模型执行 |

**输出契约**：

| 路径 | 类型 | 含义 |
|---|---|---|
| `outputs.text` | `str` | 策略 `AggregationResult.text`（如 majority_vote 的 winner、concat 的拼接结果） |
| `outputs.metadata` | `dict[str, object]` | 策略 `AggregationResult.metadata`（含 `strategy` / `contributions` / 策略专属字段） |
| `inputs.source_count` | `int` | SUCCEEDED 时等于 `len(aggregation_inputs)`；FAILED 时等于 `declared_source_count=len(node_data.inputs)` |
| `inputs.strategy` | `str` | `strategy_name`，方便消费方快速做路由决策 |

**异常 → FAILED 映射**：

| 捕获到的异常 | `error_type` 字段值 | 触发场景 |
|---|---|---|
| `MissingInputError` | `"MissingInputError"` | `variable_pool.get(selector)` 返回 `None`（上游未产出 / 单步未预加载） |
| `StrategyNotFoundError` | `"StrategyNotFoundError"` | `strategy_name` 未注册（Pydantic `Literal` 先兜一层，此分支是 defense-in-depth） |
| `StrategyConfigError` | `"StrategyConfigError"` | `strategy_config` 含 `additionalProperties: False` 禁止的键 / 字段类型不匹配 |
| 任何其他异常 | （由基类 `Node.run()` 兜底，`error_type="WorkflowNodeError"`） | 不预期；不在本节点捕获，避免吞掉后把语义信息丢掉 |

##### 1.3 文件 2：`ensemble_aggregator/__init__.py`（更新）

```python
"""Ensemble aggregator workflow node package."""

ENSEMBLE_AGGREGATOR_NODE_TYPE = "ensemble-aggregator"

from .node import EnsembleAggregatorNode  # noqa: E402  (must follow NODE_TYPE constant)

__all__ = ["ENSEMBLE_AGGREGATOR_NODE_TYPE", "EnsembleAggregatorNode"]
```

**改动要点**：
- `ENSEMBLE_AGGREGATOR_NODE_TYPE` 常量**必须**在 `from .node import ...` 之前定义——`entities.py` 会反向 `from . import ENSEMBLE_AGGREGATOR_NODE_TYPE`，顺序错了立刻循环 import 报错
- `# noqa: E402` 抑制"import 必须在模块顶部"的 lint，此处排序不是风格问题而是**语义问题**
- `walk_packages`（`node_factory.py:96`）遍历时也会经过这里；双重保障（显式 re-export + 递归扫描）让 `Node._registry` 在任何启动路径下都被填好

##### 1.4 文件 3：`api/tests/unit_tests/core/workflow/nodes/ensemble_aggregator/test_node.py`（新建）

P1.3 review round 2 新增，7 条窄范围回归，覆盖 2 条 Critical 的修复点：

```python
"""Regression tests for EnsembleAggregatorNode behaviors that the schema
(test_entities.py) cannot catch.

Scope is deliberately narrow: the two integration hooks flagged in P1.3 review
round 2. Broader strategy + node coverage lives in P1.4.
"""

import pytest
from graphon.runtime.variable_pool import VariablePool

from core.workflow.nodes.ensemble_aggregator import EnsembleAggregatorNode


def _make_node(pool: VariablePool, node_data_payload: dict) -> EnsembleAggregatorNode:
    """Build a node bypassing Node.__init__ (which needs full graph_init_params).

    We only exercise `_run` / `_collect_inputs`, which read `_node_data`,
    `_node_id`, and `graph_runtime_state.variable_pool`.
    """
    node = EnsembleAggregatorNode.__new__(EnsembleAggregatorNode)
    node._node_id = "agg_1"

    class _RS:
        pass

    rs = _RS()
    rs.variable_pool = pool
    node.graph_runtime_state = rs
    node._node_data = EnsembleAggregatorNode._node_data_type.model_validate(
        node_data_payload
    )
    return node


class TestSegmentTextNormalization:
    """_collect_inputs must use Segment.text (graphon canonical) not
    str(segment.value) — otherwise NoneSegment/ObjectSegment/ArrayStringSegment
    diverge from how other graphon nodes render those variables."""

    def test_none_segment_renders_as_empty_string(self): ...
    def test_object_segment_renders_as_json_not_python_repr(self): ...
    def test_array_string_segment_renders_as_json_not_python_repr(self): ...
    def test_empty_array_renders_as_empty_string(self): ...


class TestExtractVariableSelectorMapping:
    """_extract_variable_selector_to_variable_mapping must expose every
    inputs[*].variable_selector so single-step debug + draft-variable preload
    (workflow_entry / workflow_app_runner) can load upstream vars before _run."""

    def test_mapping_exposes_each_input_selector(self): ...
    def test_mapping_is_never_empty_for_valid_node(self): ...
    def test_mapping_preserves_multi_segment_selectors(self): ...
```

（完整代码见仓库 `test_node.py`，本处略）

**测试用例清单**：

| 类 | 方法 | 断言点 |
|---|---|---|
| `TestSegmentTextNormalization` | `test_none_segment_renders_as_empty_string` | `None` → `""`（非 `"None"`） |
| `TestSegmentTextNormalization` | `test_object_segment_renders_as_json_not_python_repr` | `{"city":"Paris"}` → `'{"city": "Paris"}'`（双引号 JSON，非 `"{'city': ...}"`） |
| `TestSegmentTextNormalization` | `test_array_string_segment_renders_as_json_not_python_repr` | `["one","two","three"]` → `'["one", "two", "three"]'`（非 `"['one', ...]"`） |
| `TestSegmentTextNormalization` | `test_empty_array_renders_as_empty_string` | `[]` → `""`（非 `"[]"`） |
| `TestExtractVariableSelectorMapping` | `test_mapping_exposes_each_input_selector` | 每条 input → `{node_id}.inputs.{source_id}` |
| `TestExtractVariableSelectorMapping` | `test_mapping_is_never_empty_for_valid_node` | 防止基类默认 `{}` 回归（预加载链路断掉的导火线） |
| `TestExtractVariableSelectorMapping` | `test_mapping_preserves_multi_segment_selectors` | 长度 ≥3 的 selector（嵌套路径）原样保留，不截断 |

##### 1.5 同步文档改动

- `docs/ModelNet/active/TASKS.md`：P1.3 标 ✅ 并追加完整交付要点（实现清单、smoke 6 条、pytest 21/21、review round 2 行）

---

#### 2. 为什么这么改（七个关键决策）

##### 决策 1：`_run()` 返回 Generator 单 yield，不返回 `NodeRunResult` 直值

**做了什么**：`_run() -> Generator[NodeEventBase, None, None]`，成功 / 失败都用 `yield StreamCompletedEvent(node_run_result=NodeRunResult(...))` 统一表达。

**为什么**：
- graphon `Node._run()` 基类签名同时允许 `NodeRunResult` 直返 **或** `Generator`；`knowledge_index_node.py` 用直返、`LLMNode` 等复杂节点用 Generator
- **Phase 2 `parallel-ensemble` 节点必须是 Generator**（流式 `StreamChunkEvent` 接 `StreamCompletedEvent`）；本阶段先把 Generator 模式跑通，Phase 2 只需扩充事件种类
- `StreamCompletedEvent` 比直返 `NodeRunResult` 在 graphon 事件契约上更明确（区分"节点完成"和"节点 pending"等生命周期语义）
- 单 yield 不是浪费：基类 `_dispatch` 把 `StreamCompletedEvent` 转成 `NodeRunSucceededEvent` / `NodeRunFailedEvent` 再向外抛；和直返走的是同一条事件管道

**不这么做会怎样**：Phase 1 先图省事直返，Phase 2 要改流式又要重新审一遍事件契约，两次迁移成本更大。

##### 决策 2：用 `segment.text` 而非 `str(segment.value)`（review round 2 修订后最终版）

**做了什么**：`_collect_inputs` 里 `collected.append({"source_id": ..., "text": segment.text})`，并加注释说明"graphon canonical text rendering"。

**为什么**（这是 P1.3 最值得展开的决策）：
- graphon `Segment.text` 是 canonical 文本渲染语义，各个 Segment 子类做了特化：
  - `NoneSegment.text == ""`（vs `str(None) == "None"`）
  - `ObjectSegment.text == json.dumps(self.model_dump()["value"], ensure_ascii=False)`（vs Python `str(dict)` 得到单引号 repr、非有效 JSON）
  - `ArrayStringSegment.text == json.dumps(list)` + 空数组特化为 `""`（vs `"['a', 'b']"` / `"[]"`）
  - `FileSegment.text == ""`（vs Pydantic repr 字符串）
  - 默认 `Segment.text == str(self.value)`（对 StringSegment / IntegerSegment / FloatSegment / BooleanSegment 这些 value 本身就是标量的情况，两者等价）
- 选 `segment.text` 是**严格更强的选择**——对所有 Segment 子类保证 "与 graphon 其他节点一致的文本渲染契约"；对标量场景行为等价；对非标量场景正确
- 用户 DSL 可能把节点的 `variable_selector` 指向 `llm_a.structured_output`（Object）或 `llm_a.tool_choices`（Array）；此时两种实现的**输出字符串直接不同**——聚合结果会让用户困惑

**不这么做会怎样**：Smoke 跑全图时只测 StringSegment（都走 happy path），bug 藏在"selector 指 object/array"的生产场景；等用户用嵌套 selector 时，聚合节点的文字表示和下游展示（Answer / End）文字不一致——且出问题的是"用户看到的最终文本"。

##### 决策 3：覆盖 `_extract_variable_selector_to_variable_mapping`，键用 `{node_id}.inputs.{source_id}`（review round 2 修订后新增）

**做了什么**：classmethod 返回 `{f"{node_id}.inputs.{ref.source_id}": list(ref.variable_selector) for ref in node_data.inputs}`。

**为什么**：
- Dify 的单步调试（`workflow_entry.py:290`）+ draft 预加载（`workflow_app_runner.py:347`）在真正 run 节点前，**先**调 `node_cls.extract_variable_selector_to_variable_mapping(...)`，把返回的 selectors 喂给 `load_into_variable_pool()` 预填变量池
- graphon `Node._extract_variable_selector_to_variable_mapping` 默认返回 `{}`——**不覆盖就不知道节点依赖哪些变量**；全图跑能过只因上游节点在执行时已把 output 写回 pool
- `knowledge_retrieval_node.py:314` 就是这么做的：`variable_mapping[node_id + ".query"] = node_data.query_variable_selector`
- 选择 `{node_id}.inputs.{source_id}` 作为 key 格式：
  - `source_id` 已在 `entities.EnsembleAggregatorNodeData._check_source_id_unique` 保证节点内唯一 → 可直接当 key 后缀，不需要额外的 index 去重
  - `.inputs.` 这段前缀做 **namespacing**：未来如果给节点加其他 selector 字段（如 `query_selector`），不会和 `inputs` 碰撞
  - 和 `knowledge_retrieval` 的 `{node_id}.{semantic}` 风格同构；不使用基类 docstring 里的 `#{source_node}.{var_name}#` 形式是因为后者冗长且把 selector 塞进 key 已经没有必要（value 字段本身就承载 selector）

**不这么做会怎样**：全图运行 smoke 100% 绿，但单节点调试面板显示"未加载变量"；用户在画布上点 "单步运行"，节点立即 FAILED with MissingInputError——生产可用性严重下降。

##### 决策 4：`EnsembleAggregatorNodeError` 全族宽捕获 + `error_type=type(e).__name__`

**做了什么**：

```python
try:
    aggregation_inputs = self._collect_inputs()
    strategy = get_strategy(strategy_name)
    result = strategy.aggregate(aggregation_inputs, node_data.strategy_config)
except EnsembleAggregatorNodeError as e:
    yield StreamCompletedEvent(node_run_result=NodeRunResult(status=FAILED,
        error=str(e),
        error_type=type(e).__name__,   # ← 保留子类语义
        ...))
```

**为什么**：
- P1.1 exceptions 设计时就把 `MissingInputError` / `StrategyNotFoundError` / `StrategyConfigError` 放同一族基类（`EnsembleAggregatorNodeError`）；这里一条 `except` 承接、不用写 3 个 branch
- `error_type=type(e).__name__` 保留**子类名**而不是基类名——下游（frontend error banner、观测日志）可据此做精细化路由
- 参考 `knowledge_index_node.py:105-112` 同样的 `type(e).__name__` 风格；保持仓库一致性
- **未预期异常不在这层捕获**：让基类 `Node.run()` 的 `except Exception` 接住，这样 stack trace 不被吞掉、`error_type="WorkflowNodeError"` 表达"意外错误"

**不这么做会怎样**：如果每个子异常写一个 `except`，方法体膨胀且互相重复；如果用 `except Exception` 包住所有，`error_type` 丢失语义信息、未来 `BufferError` / `SystemError` 也被误包成域错误。

##### 决策 5：FAILED 时 `source_count = declared_source_count`，SUCCEEDED 时 `= len(aggregation_inputs)`

**做了什么**：

```python
declared_source_count = len(node_data.inputs)
try:
    aggregation_inputs = self._collect_inputs()
    ...
except EnsembleAggregatorNodeError:
    yield StreamCompletedEvent(node_run_result=NodeRunResult(status=FAILED,
        inputs={"source_count": declared_source_count, ...}))
    return
yield StreamCompletedEvent(node_run_result=NodeRunResult(status=SUCCEEDED,
    inputs={"source_count": len(aggregation_inputs), ...}))
```

**为什么**：
- SUCCEEDED 路径：全部 input 已读到，`len(aggregation_inputs) == declared_source_count`，两者相等但语义不同——用**"实际参与聚合"**的数字更准确
- FAILED 路径：可能在 `_collect_inputs` 读到一半就因 `MissingInputError` 抛出，此时 `aggregation_inputs` 变量不存在；用**"节点声明配置"**的 `declared_source_count` 作为唯一可靠来源
- 不把 `aggregation_inputs` 初始化成 `[]` 然后统一用 `len(aggregation_inputs)`：那样在 `_collect_inputs` 部分成功部分失败时，数字含义会让人困惑（"5 declared, 2 partially collected, failed at 3rd" 到底算几？）
- `NodeRunResult.inputs` 字段在 Dify UI 作为"节点输入快照"展示——失败时也要有意义的数据，观测价值比"数字精确反映 runtime 状态"更重要

**不这么做会怎样**：观测面板在 FAILED 条目展示 `source_count=0` 或 `KeyError`，排错时不知道"节点到底配了几个 input"。

##### 决策 6：`__init__.py` 常量先行、re-export 后置 + `# noqa: E402`

**做了什么**：

```python
ENSEMBLE_AGGREGATOR_NODE_TYPE = "ensemble-aggregator"

from .node import EnsembleAggregatorNode  # noqa: E402
```

**为什么**：
- `entities.py:8` 反向 `from . import ENSEMBLE_AGGREGATOR_NODE_TYPE` —— 这是 P1.1 落定的 import 依赖
- `node.py` → `from .entities import ...` → `entities.py` → `from . import ENSEMBLE_AGGREGATOR_NODE_TYPE` → 回到 `__init__.py`
- 如果 `__init__.py` 第一行是 `from .node import ...`，Python 执行该行时 `__init__.py` 尚未赋值 `ENSEMBLE_AGGREGATOR_NODE_TYPE`，循环 import 立即 `ImportError`
- 把常量作为"`__init__.py` 第一条语句"强制先赋值，`from .node import` 才能安全触发级联 import
- `# noqa: E402` 抑制 "imports-not-at-top"：此处顺序不是代码风格问题、而是语义硬约束，注释已明确表明

**不这么做会怎样**：`from core.workflow.nodes.ensemble_aggregator import EnsembleAggregatorNode` 直接抛 `ImportError: cannot import name 'ENSEMBLE_AGGREGATOR_NODE_TYPE' from partially initialized module ...`；而且这类错误在 `node_factory.py` 的 `walk_packages` 启动批量 import 时才显露，堆栈深、定位难。

##### 决策 7：单元测试用 `__new__` + `_node_data` 手动注入，绕过 `Node.__init__`

**做了什么**：

```python
node = EnsembleAggregatorNode.__new__(EnsembleAggregatorNode)
node._node_id = "agg_1"
class _RS: pass
rs = _RS(); rs.variable_pool = pool
node.graph_runtime_state = rs
node._node_data = EnsembleAggregatorNode._node_data_type.model_validate(...)
```

**为什么**：
- `Node.__init__` 要求 `id / config / graph_init_params / graph_runtime_state` 4 个参数；`graph_init_params` 本身带 `workflow_id` / `graph_config` / `run_context` 等非 trivial 字段，整个构造链很深
- P1.3 测试目标只是 `_run()` / `_collect_inputs()` / classmethod `_extract_variable_selector_to_variable_mapping`——这些只读 `_node_data` / `_node_id` / `graph_runtime_state.variable_pool`
- 用 `__new__` 绕过 `__init__`，只注入被测方法实际用到的 attribute，**测试失败原因只能是被测方法本身**，不会因为构造链某环变更而误报
- `_RS` 临时类比 mock 框架更轻量，10 行写完；测试文件 docstring 已明说这是刻意绕过

**不这么做会怎样**：测试会引入一串 graphon 内部类型（`GraphInitParams` / `GraphRuntimeState`）的构造依赖；未来 graphon 某版本加了新 required 字段，整个 P1.3 测试突然一起红，但本意毫无变化。P1.4 的节点完整测试可以考虑升级到 factory helper；P1.3 先用最窄的构造。

---

#### 3. 验收详细结果

##### 命令 1：自动注册（`Node._registry["ensemble-aggregator"]["1"]`）

```python
from core.workflow.nodes.ensemble_aggregator import (
    ENSEMBLE_AGGREGATOR_NODE_TYPE, EnsembleAggregatorNode,
)
from graphon.nodes.base.node import Node
print(ENSEMBLE_AGGREGATOR_NODE_TYPE in Node._registry)
print(dict(Node._registry[ENSEMBLE_AGGREGATOR_NODE_TYPE]))
print(EnsembleAggregatorNode._node_data_type)
```

**结果**：✅ 绿
- `True`
- `{'1': <class ...EnsembleAggregatorNode>, 'latest': <class ...EnsembleAggregatorNode>}`
- `<class ...EnsembleAggregatorNodeData>` — 泛型参数 auto-extract 成功

##### 命令 2：majority_vote 3-票 happy path

3 个上游文本 `[Paris, Paris, Lyon]`，`strategy_name="majority_vote"`，`strategy_config={}`：

**结果**：✅ 绿 — 单 `StreamCompletedEvent(SUCCEEDED)`
- `outputs.text == "Paris"`
- `outputs.metadata.strategy == "majority_vote"`
- `outputs.metadata.votes == {'Paris': 2, 'Lyon': 1}`
- `outputs.metadata.winner_votes == 2`
- `outputs.metadata.contributions == {'a':'Paris', 'b':'Paris', 'c':'Lyon'}`
- `inputs.source_count == 3`
- `inputs.strategy == "majority_vote"`

##### 命令 3：concat + `include_source_label=True` + 自定义 separator

2 个上游文本，`strategy_config={"include_source_label": True, "separator": " | "}`：

**结果**：✅ 绿
- `outputs.text == "[a]\nanswer one | [b]\nanswer two"`
- `outputs.metadata.separator == " | "`
- `outputs.metadata.include_source_label == True`

##### 命令 4：`MissingInputError` → FAILED

2 个声明的 inputs，VariablePool 里只 seed 第 1 个：

**结果**：✅ 绿
- `status == FAILED`
- `error_type == "MissingInputError"`
- `error == "Upstream variable for source 'b' (selector=['llm_b', 'text']) not available in variable pool"`
- `inputs == {"source_count": 2, "strategy": "majority_vote"}` — 声明计数仍可见

##### 命令 5：`StrategyConfigError` → FAILED（`{"bogus": 42}` 给 majority_vote）

验证 P1.2 v2.3 review round 2 修订后的 extras 拒绝行为在 node 层贯通：

**结果**：✅ 绿
- `status == FAILED`
- `error_type == "StrategyConfigError"`
- `error` 含 `"Invalid config for strategy 'majority_vote': 1 validation error for _MajorityVoteConfig"` 及 `"bogus ... Extra inputs are not permitted"`

##### 命令 6：`StrategyNotFoundError` → FAILED（defense-in-depth，绕 Pydantic Literal）

用 `object.__setattr__(node_data, "strategy_name", "unknown_strat")` 模拟运行期 drift：

**结果**：✅ 绿
- `status == FAILED`
- `error_type == "StrategyNotFoundError"`
- `error == "Aggregation strategy 'unknown_strat' is not registered"`

##### 命令 7：pytest 全量（14 P1.1 schema + 7 P1.3 新增回归）

```bash
$ uv run --project api pytest api/tests/unit_tests/core/workflow/nodes/ensemble_aggregator/ -v -o addopts=""
collected 21 items

test_entities.py::TestAggregationInputRef::test_valid_two_segment_selector PASSED
test_entities.py::TestAggregationInputRef::test_valid_path_segments_allowed PASSED
test_entities.py::TestAggregationInputRef::test_selector_too_short_rejected PASSED
test_entities.py::TestAggregationInputRef::test_selector_empty_rejected PASSED
test_entities.py::TestAggregationInputRef::test_blank_selector_segment_rejected PASSED
test_entities.py::TestAggregationInputRef::test_empty_selector_segment_rejected PASSED
test_entities.py::TestAggregationInputRef::test_blank_source_id_rejected PASSED
test_entities.py::TestAggregationInputRef::test_empty_source_id_rejected PASSED
test_entities.py::TestAggregationInputRef::test_extra_field_rejected PASSED
test_entities.py::TestEnsembleAggregatorNodeData::test_defaults_applied PASSED
test_entities.py::TestEnsembleAggregatorNodeData::test_inputs_too_few_rejected PASSED
test_entities.py::TestEnsembleAggregatorNodeData::test_duplicate_source_id_rejected PASSED
test_entities.py::TestEnsembleAggregatorNodeData::test_concat_strategy_accepted PASSED
test_entities.py::TestEnsembleAggregatorNodeData::test_unknown_strategy_name_rejected PASSED
test_node.py::TestSegmentTextNormalization::test_none_segment_renders_as_empty_string PASSED
test_node.py::TestSegmentTextNormalization::test_object_segment_renders_as_json_not_python_repr PASSED
test_node.py::TestSegmentTextNormalization::test_array_string_segment_renders_as_json_not_python_repr PASSED
test_node.py::TestSegmentTextNormalization::test_empty_array_renders_as_empty_string PASSED
test_node.py::TestExtractVariableSelectorMapping::test_mapping_exposes_each_input_selector PASSED
test_node.py::TestExtractVariableSelectorMapping::test_mapping_is_never_empty_for_valid_node PASSED
test_node.py::TestExtractVariableSelectorMapping::test_mapping_preserves_multi_segment_selectors PASSED

=========================== 21 passed in 0.08s ===========================
```

**结果**：✅ 绿 21/21
- P1.1 schema 层 14 条回归全绿
- P1.3 新增 7 条回归（4 Segment.text 归一化 + 3 selector mapping）全绿

---

#### 4. 约束与不做

##### 4.1 P1.3 不做

| 项目 | 为什么不做 | 去哪 |
|---|---|---|
| 策略 + 节点的完整单测（`test_majority_vote` / `test_concat` / `test_node_run`） | TASKS.md P1.4 专门收口；P1.3 只为本轮 review fix 加窄范围回归 | P1.4 |
| `node_factory.py:372-440` 添加注入分支 | 本节点无外部依赖（不需要 ssrf_proxy / ThreadPoolExecutor），仅 `_import_node_package` 自动注册即可；P1.1 决策验证 | 不做 |
| 前端 `strategy-selector.tsx` + panel | 后端稳定后再上前端 | P1.5 |
| DSL 端到端（workflow / chat 两模式） | 前端可用后才能导出 DSL | P1.8 |
| 流式 `StreamChunkEvent`（每 token 一块） | Phase 1 响应级聚合是"全部上游完成后单次输出"；流式是 Phase 2 的 token 级节点 | P2.8 |
| `process_data` 字段 | 当前 `outputs` + `inputs` 已充分；`process_data` 按需再补 | Phase 2+ |
| `execution_type = NodeExecutionType.RESPONSE` | Aggregator 是普通可执行节点，不是"最终响应节点"（Answer / End 之类）；沿用基类默认 `EXECUTABLE` | 不做 |

##### 4.2 保留的简化（Phase 1 明确接受）

- 仅在 `_collect_inputs` 层做 `MissingInputError` 判定；不做"允许部分缺失 + 继续聚合"的降级模式——那会和 strategies 的"所有 inputs 都参与"语义冲突，且工作流侧 retry / error_strategy 已是独立维度
- `_run` 全程不写 `process_data`、不用 `yield VariableUpdatedEvent`；上游 LLM 节点已经写好了自己的 variable，Aggregator 的输出 `outputs.text` / `outputs.metadata` 由 graphon 自动写回 VariablePool
- `inputs.source_count` / `inputs.strategy` 是极简观测字段；未来如果要加 `inputs.strategy_config_hash` 之类用于审计回放，是**增量扩展**而非架构改动
- FAILED 分支打 `logger.warning(..., exc_info=True)` 作为开发期可观测入口；生产后如有大量告警噪音，改为 `logger.info` 或加采样由运维层决策

##### 4.3 边界说明

| 情形 | 行为 |
|---|---|
| 上游节点产出非字符串（如 object / list） | `segment.text` 按 graphon canonical 渲染：object → JSON、array → JSON、None → `""`、空数组 → `""`；一致性由 Segment 子类保障，节点层不再 branch |
| 上游产出 `FileSegment` | `.text == ""`（graphon 默认行为）；策略层拿到空串，majority_vote 可能把空串选中、concat 相当于少一段；Phase 1 不对"文件聚合"做特殊处理（非目标） |
| 单步调试未预加载 | `_extract_variable_selector_to_variable_mapping` 已覆盖，workflow_entry / app_runner 会按 mapping 喂 `load_into_variable_pool`；若 loader 仍拿不到，走 `MissingInputError` 分支 |
| 上游产出空字符串 `""` | 正常参与投票 / 拼接；不做额外过滤（和 P1.2 majority_vote 边界一致） |
| `source_id` 含特殊字符（`.`, 空格） | 当前 key 格式 `{node_id}.inputs.{source_id}` 会把 `.` 吃进去，使 key 的 dot 分隔含义歧义；`source_id` 的 validator 目前只禁空白、未禁 `.`——Phase 1 接受（entities 的 v2.4 如果要收紧可以加 pattern 约束） |

---

#### 5. 下一步（P1.4 触发点）

P1.3 落地后阻塞 P1.4 的信息已清：

- **节点层事件契约稳定**：`_run() -> Generator[StreamCompletedEvent]`；SUCCEEDED 事件 `outputs = {text, metadata}`、`inputs = {source_count, strategy}`；FAILED 事件 `error_type ∈ {MissingInputError, StrategyNotFoundError, StrategyConfigError, WorkflowNodeError}`
- **可测试表面**：`_make_node(pool, node_data_payload)` 辅助函数已在 `test_node.py` 里示范；P1.4 可以直接扩展
- **VariablePool 注入模式**：测试用 `VariablePool().add([node_id, var_name], value)` 直接 seed；不用真起 GraphEngine
- **classmethod `extract_variable_selector_to_variable_mapping`** 已可独立测试，P1.4 可以补"多 input 多嵌套段 selector"的更宽覆盖

P1.4 要做的：

- **`test_majority_vote`**：`["A","A","B"] → "A"`；并列取字典序；"未知 config key 拒绝"（symmetric with `test_concat`）；空 inputs（期望 schema 层已拦，这里是 defense-in-depth）
- **`test_concat`**：默认分隔符 / 自定义分隔符 / `include_source_label` 两种值 / `extra="forbid"` 拒绝
- **`test_node_run`**：mock VariablePool 喂 3 个上游文本，断言 `outputs.text / metadata` 正确 + 事件序列是单个 `StreamCompletedEvent`（长度=1）
- **附带完善**：`test_node.py` 从 7 条窄回归扩展到全路径覆盖（节点完整生命周期 / 所有 error_type 分支）；或把 P1.3 的 smoke 命令 1-6 转成 pytest

跑命令仍是：

```bash
uv run --project api pytest api/tests/unit_tests/core/workflow/nodes/ensemble_aggregator/ -v -o addopts=""
```

（`-o addopts=""` 是 P1.1 v2.3 就已确定的覆盖方式：绕过仓库 `pytest.ini` 的 `--cov` 要求，本地 venv 没装 pytest-cov。）

---

#### 6. review round 2 修订（2026-04-19）

##### 6.1 触发

初版 P1.3 落地后 code review 指出 2 条 Critical + 1 条 Suggestion：

| # | 级别 | 问题 |
|---|---|---|
| 1 | 🔴 Critical | `_collect_inputs()` 里 `str(segment.value)` 绕过 `Segment.text` 语义；`NoneSegment / ObjectSegment / ArrayStringSegment / 空数组` 等特化会被错误串行化（得到 Python repr 而非 graphon canonical JSON / 空串） |
| 2 | 🔴 Critical | `EnsembleAggregatorNode` 没覆盖 `_extract_variable_selector_to_variable_mapping()`，基类默认返回 `{}`；Dify 单步运行 + draft 预加载（`workflow_entry.py:290`, `workflow_app_runner.py:347`）拿不到依赖的 selector，链路失效 |
| 3 | 🟡 Suggestion | 当前只有 P1.1 schema 层测试（14/14），P1.3 新增行为（`_collect_inputs` / `MissingInputError` → FAILED / 异常封装 / selector mapping）无回归保护 |

**复现**（修订前行为）：

- **问题 1**：`variable_pool.add(["llm_b", "text"], None)` → `_collect_inputs` 返回 `{"text": "None"}` 而非 `""`；上游是 `{"city":"Paris"}` → `"{'city': 'Paris'}"` 而非 `'{"city": "Paris"}'`（下游下游看到的文字和 graphon 其他节点对同一变量的渲染**不一致**）
- **问题 2**：`EnsembleAggregatorNode.extract_variable_selector_to_variable_mapping(graph_config={}, config={"id":"n1","data":{...}})` 返回 `{}`；单步调试场景下 `load_into_variable_pool` 完全不预加载依赖，`_run` 立即抛 `MissingInputError`

##### 6.2 取舍

**2 条 Critical 必修**，原因：
- **问题 1** 与 P1.2 review round 2 同属 "schema 声明 / 文档 / 其他节点约定" 与运行期实现偏离的一类 bug——只有在特定 Segment 类型下才暴露，smoke 看不出来
- **问题 2** 更严重：**全图 smoke 不会触发**（上游节点已经写入 pool），但单步调试 / draft 预加载这两条用户可见路径直接坏掉；上线才发现
- 修复成本都极低：问题 1 改一个词（`value` → `text`）；问题 2 加一个 ~6 行的 classmethod

**Suggestion 部分采纳**：
- 只为**本轮修订的 2 处**加窄范围 pytest 回归（7 条）
- 不把 P1.4 的完整 strategies + 节点全路径测试前移到 P1.3——那会让 P1.3 的 scope 膨胀到 2-3 倍；P1.4 本身就是"测试补全"阶段
- 理由：7 条回归覆盖了 "下次 refactor 把 `segment.text` 改回去 / 把 classmethod 误删" 这两类最可能的再次破坏；其余全路径测试 P1.4 统一写，有更好的测试 fixture 可共享

##### 6.3 具体修改

`ensemble_aggregator/node.py`（diff 概述）：

```diff
 import logging
-from collections.abc import Generator
-from typing import ClassVar
+from collections.abc import Generator, Mapping, Sequence
+from typing import Any, ClassVar
 ...

     def _collect_inputs(self) -> list[AggregationInput]:
         variable_pool = self.graph_runtime_state.variable_pool
         collected: list[AggregationInput] = []
         for ref in self.node_data.inputs:
             segment = variable_pool.get(ref.variable_selector)
             if segment is None:
                 raise MissingInputError(
                     source_id=ref.source_id,
                     variable_selector=list(ref.variable_selector),
                 )
-            collected.append({"source_id": ref.source_id, "text": str(segment.value)})
+            # Use Segment.text (graphon canonical text rendering) rather than
+            # str(segment.value): the former normalizes NoneSegment -> "",
+            # ObjectSegment/ArrayStringSegment -> JSON, empty arrays -> "",
+            # keeping this node aligned with how graphon's other nodes render
+            # variables.
+            collected.append({"source_id": ref.source_id, "text": segment.text})
         return collected

+    @classmethod
+    def _extract_variable_selector_to_variable_mapping(
+        cls,
+        *,
+        graph_config: Mapping[str, Any],
+        node_id: str,
+        node_data: EnsembleAggregatorNodeData,
+    ) -> Mapping[str, Sequence[str]]:
+        # Expose each input's upstream selector to the draft-variable preload
+        # path (workflow_entry / workflow_app_runner). source_id is unique per
+        # node (enforced in entities.py), so {node_id}.inputs.{source_id} is a
+        # stable unique key — same shape as knowledge_retrieval_node.py:314.
+        return {
+            f"{node_id}.inputs.{ref.source_id}": list(ref.variable_selector)
+            for ref in node_data.inputs
+        }
```

`tests/unit_tests/core/workflow/nodes/ensemble_aggregator/test_node.py`（新建）：7 条回归（§1.4 已展开）。

**不改**：`entities.py` / `exceptions.py` / `strategies/` 全部 / `__init__.py` / DEVELOPMENT_PLAN.md。

##### 6.4 为什么这么做

| 决策 | 理由 |
|---|---|
| `segment.value` → `segment.text`（非手写 `if isinstance(...)` 分派） | Segment 子类多态已经封装了 "如何渲染"；节点层再 branch 一次就是 graphon 内部事实的泄漏；`.text` 是 "strictly stronger" 选择（对 StringSegment/标量等价，对 None/Object/Array/File/空数组正确） |
| 覆盖 `_extract_variable_selector_to_variable_mapping` 而非修 `workflow_entry` 容错 | graphon 契约是"节点显式声明依赖，engine 负责预加载"；修 workflow_entry 会绕过契约、并影响其他节点；覆盖 classmethod 是 Dify 仓库既有节点（knowledge_retrieval）的规范做法 |
| 键用 `{node_id}.inputs.{source_id}` | source_id 已节点内唯一 → 不需要 index 去重；`.inputs.` 做 namespacing 留给未来 `.query` / `.filter` 等字段；同 `knowledge_retrieval` 风格一致 |
| 新增 `test_node.py` 放回归，不写进 `test_entities.py` | 按被测对象分文件：`test_entities.py` 是 schema 层（Pydantic 模型）、`test_node.py` 是节点行为；两者测试依赖完全不同，放一起会让后期 P1.4 扩容难分文件 |
| 未把测试 fixture 抽象成 conftest.py | 当前只有一个测试文件用到 `_make_node`；过早抽象反而让 P1.4 在扩展时"为什么 fixture 长这样"难解释；P1.4 扩容时再按需提升 |

##### 6.5 验收

```bash
$ uv run --project api pytest api/tests/unit_tests/core/workflow/nodes/ensemble_aggregator/ -v -o addopts=""
============================== 21 passed in 0.08s =============================
```

21/21 绿细分：

| 文件 | 类 / 方法 | 覆盖 |
|---|---|---|
| `test_entities.py` | `TestAggregationInputRef` x9 + `TestEnsembleAggregatorNodeData` x5 | P1.1 v2.3 schema 层 14 条——无回归 |
| `test_node.py` | `TestSegmentTextNormalization::test_none_segment_renders_as_empty_string` | 问题 1 修复的底线：`None` 不再被渲染成 `"None"` |
| `test_node.py` | `TestSegmentTextNormalization::test_object_segment_renders_as_json_not_python_repr` | 问题 1 修复的主战场：object 走 JSON 双引号 |
| `test_node.py` | `TestSegmentTextNormalization::test_array_string_segment_renders_as_json_not_python_repr` | 问题 1 修复：array string 走 JSON |
| `test_node.py` | `TestSegmentTextNormalization::test_empty_array_renders_as_empty_string` | 问题 1 的 subtle 边界：`[]` → `""` 不是 `"[]"` |
| `test_node.py` | `TestExtractVariableSelectorMapping::test_mapping_exposes_each_input_selector` | 问题 2 修复的核心：mapping 完整暴露每条 input |
| `test_node.py` | `TestExtractVariableSelectorMapping::test_mapping_is_never_empty_for_valid_node` | 回归 guard：如果有人误把 classmethod 删掉 / 改成 `return {}` 立刻红 |
| `test_node.py` | `TestExtractVariableSelectorMapping::test_mapping_preserves_multi_segment_selectors` | 嵌套 selector（长度 ≥3）不被截断 |

同时跑了 6 条 smoke 命令（§3 的命令 1-6）全部复绿——review 修订不影响 happy path 和已有 FAILED 路径。

##### 6.6 对后续阶段的影响

- **P1.4（单测补全）**：不需要再为 `Segment.text` / mapping 兜底；直接往前写"节点事件序列"/"各 strategy 完整行为"测试。`_make_node` helper 可以沿用或提升到 `conftest.py`
- **P1.5（前端）**：后端 `extract_variable_selector_to_variable_mapping` 正确后，前端在 Aggregator 节点上做"单步运行"调试按钮可以正确预加载变量，展示准确的 input 快照
- **P1.7（前端质量门）**：无直接影响；仅是前端 panel 拿 `{node_id}.inputs.{source_id}` 做 error key 映射时风格更统一
- **P1.8（联调）**：在浏览器单节点调试路径上用户第一次能看到"aggregator 在生产态之外也可以跑"；对上游 variable 是 object / array 的 DSL，聚合文本输出会和 End 节点看到的值严格一致
- **Phase 2 `parallel-ensemble`**：同样需要覆盖 `_extract_variable_selector_to_variable_mapping`（节点 inputs 里会有 `question` / `attachment` 之类 selector）；P1.3 的经验直接复用——"mapping 不声明 = 单步坏"已经写进 checklist

---

#### 附录：文件变更清单

```
新增（P1.3 初始，2026-04-19）:
  api/core/workflow/nodes/ensemble_aggregator/node.py                              (EnsembleAggregatorNode 全部实现)
  docs/ModelNet/P1.3_LANDING.md                                                   (本文档)

修改（P1.3 初始，2026-04-19）:
  api/core/workflow/nodes/ensemble_aggregator/__init__.py
    - 追加 from .node import EnsembleAggregatorNode
    - __all__ 加入 "EnsembleAggregatorNode"
  docs/ModelNet/active/TASKS.md
    - P1.3 标 ✅ 并追加交付要点（节点实现清单 / smoke 6 条 / 无需 factory 注入 / P1.1 14 条回归）

修改（review round 2，2026-04-19）:
  api/core/workflow/nodes/ensemble_aggregator/node.py
    - _collect_inputs 里 str(segment.value) → segment.text（加注释说明 graphon canonical 渲染）
    - 新增 @classmethod _extract_variable_selector_to_variable_mapping
    - 引入 Mapping / Sequence / Any 等 typing 依赖
  api/tests/unit_tests/core/workflow/nodes/ensemble_aggregator/test_node.py
    - 新建；7 条窄范围回归（4 Segment.text 归一化 + 3 selector mapping）
    - 引入 _make_node helper（绕 Node.__init__，直接注入被测 attribute）
  docs/ModelNet/active/TASKS.md
    - P1.3 条目扩写："v2 review round 2 兜底" 行 + pytest 21/21 记录
  docs/ModelNet/P1.3_LANDING.md (本文档)
    - 头部日期 / 验收计数更新
    - §1.2 代码块同步到最终版
    - §1.4 新增（test_node.py）
    - §2 决策 2 / 3 扩展（两条 review critical 的最终解）
    - §3 命令 7（pytest 全量）
    - 新增 §6 "review round 2 修订"
    - 本附录扩充

未动:
  api/core/workflow/nodes/ensemble_aggregator/entities.py                                   (P1.1 v2.3 稳态)
  api/core/workflow/nodes/ensemble_aggregator/exceptions.py                                 (P1.1 稳态)
  api/core/workflow/nodes/ensemble_aggregator/strategies/*                                  (P1.2 v2 review round 2 稳态)
  api/tests/unit_tests/core/workflow/nodes/ensemble_aggregator/test_entities.py             (P1.1 v2.3 稳态，用作回归 baseline)
  api/core/workflow/node_factory.py                                                         (P1.1 决策验证：Aggregator 无外部依赖，不需加注入分支)
  docs/ModelNet/history/DEVELOPMENT_PLAN_v2.md                                                          (P1.3 仅实施、未改计划；§5.4 节点代码块是 sketch，实现版细节靠本文档承载)
```


---

### P1.4 - P1.4 Landing 报告 — ensemble_aggregator 后端单测（strategies + node._run with mock VariablePool）

> Source shard: `P1.4_LANDING.md`


> **日期**：2026-04-20
> **对应 TASKS.md**：P1.4
> **对应 DEVELOPMENT_PLAN.md**：§5.7（验收标准）"节点单测：策略基类 + 两个策略 + 节点 `_run()`（mock VariablePool）"
> **耗时**：~25 分钟
> **验收**：`uv run --project api pytest api/tests/unit_tests/core/workflow/nodes/ensemble_aggregator/ -v -o addopts=""` → **45 passed, 0 failed**
> **前置**：P1.1 v2.3（`entities.py`）+ P1.2 v2 review r2（`strategies/`）+ P1.3 v2 review r2（`node.py`）均已稳态落地

---

#### 1. 做了什么

P1.4 在 `api/tests/unit_tests/core/workflow/nodes/ensemble_aggregator/` 下把"单节点行为"封口：

| 文件 | 状态 | 本轮新增 | 作用 |
|---|---|---|---|
| `test_entities.py` | 已存在（P1.1） | — | schema 层 14 条 mini-tests |
| `test_node.py` | 已存在（P1.3 r2） | **+7 条**（`TestRunHappyPath` 3 + `TestRunFailurePaths` 4） | 端到端 `_run()`：事件序列 / 输出 / metadata / FAILED 路径 |
| `test_strategies.py` | **新建** | **17 条**（`TestMajorityVoteStrategy` 7 + `TestConcatStrategy` 7 + `TestRegistry` 3） | 策略层公共 API 契约 |

##### 1.1 `test_strategies.py`（新建，208 行）

**`TestMajorityVoteStrategy`（7 条）**

1. `test_three_way_majority_wins` — 计划原话 `['A','A','B']→'A'`，断言 `votes` / `winner_votes` / `tie_break_applied=False` / `contributions`
2. `test_unanimous_win` — 全部投同一票
3. `test_two_way_tie_breaks_by_source_id_lex_order` — `[(bob,Y), (alice,X)]` → `X`（alice < bob）
4. `test_tie_break_independent_of_input_order` — 上一条反转输入顺序仍得 `X`（确定性核心保证）
5. `test_three_way_tie_picks_lex_smallest_voter_group` — 三个单票各自投 `C/A/B`，voters `c1/a1/b1` → `A` 赢
6. `test_unknown_config_field_rejected` — `{"unexpected":1}` → `StrategyConfigError("majority_vote", ...)`
7. `test_contributions_keyed_by_source_id` — metadata.contributions 键必须是 source_id

**`TestConcatStrategy`（7 条）**

1. `test_default_separator_joins_with_horizontal_rule` — 默认 `"\n\n---\n\n"` 分隔
2. `test_custom_separator` — `separator=" | "` 生效
3. `test_include_source_label_adds_bracketed_prefix` — `[source_id]\n<text>` 前缀
4. `test_include_source_label_with_custom_separator` — label + 非默认 separator 组合
5. `test_input_order_preserved` — concat 必须保持输入声明顺序
6. `test_unknown_config_field_rejected` — `extra="forbid"` → `StrategyConfigError("concat", ...)`
7. `test_wrong_type_rejected` — `separator=123` → `StrategyConfigError`

**`TestRegistry`（3 条）**

1. `test_both_builtin_strategies_registered` — `list_strategies()` 包含两个内建名
2. `test_get_strategy_returns_fresh_instance` — 每次调用返回新实例
3. `test_duplicate_registration_raises_value_error` — 同名二次注册报 `ValueError`，注册表不污染

##### 1.2 `test_node.py` 新增类（+7 条）

**`TestRunHappyPath`（3 条）**
复用已有的 `_make_node` + `_RS` 模拟基础设施（P1.3 建立），喂 3 路上游文本，断言：

1. `test_majority_vote_succeeds_with_expected_outputs` — 事件序列 `len==1` 且 `isinstance(..., StreamCompletedEvent)`；`status==SUCCEEDED`、`error==""`；`outputs.text=="A"`、`outputs.metadata` 全字段、`inputs=={source_count:3, strategy:"majority_vote"}`
2. `test_concat_default_separator` — 默认 separator 拼 3 段
3. `test_concat_with_source_label_and_custom_separator` — 同时开 label + 自定义 separator

**`TestRunFailurePaths`（4 条）**
覆盖节点层 `try/except EnsembleAggregatorNodeError` 的三条异常路径 + 异常族完备性：

1. `test_missing_upstream_input_becomes_failed_event` — VariablePool 缺一路 → `FAILED`、`error_type=="MissingInputError"`、`outputs=={}`、`inputs` 仍带观测性字段
2. `test_invalid_strategy_config_becomes_failed_event` — `majority_vote` + `{"bogus":42}` → `FAILED`、`error_type=="StrategyConfigError"`
3. `test_strategy_not_found_defense_in_depth` — 直接 `node._node_data.strategy_name = "never_registered"` 绕过 Pydantic Literal（`BaseNodeData.model_config.validate_assignment` 默认 False，已实证），模拟 schema/注册表漂移 → `FAILED`、`error_type=="StrategyNotFoundError"`
4. `test_exceptions_are_importable_and_distinct` — 三个异常类 `issubclass(Exception)` 守卫

**头部 imports 相应补齐**：`WorkflowNodeExecutionStatus` / `StreamCompletedEvent` / 三个 exception 类。

---

#### 2. 设计取舍

##### 2.1 为什么拆 `test_strategies.py` 而不是全塞 `test_node.py`

策略层是**纯函数契约**（`aggregate(inputs, config) -> result`），不依赖 graphon；节点层是**事件协议+VariablePool 集成**。两层责任不同、失败定位语义不同：

- 策略测试挂 → 算法/确定性/配置校验层坏
- 节点测试挂 → 事件序列/Pydantic mutability/mapping 暴露层坏

混在一起会把"P1.2 的契约测试"和"P1.3 的集成测试"的回归失败信号耦合在一起，后续改一边就得改两处。

##### 2.2 为什么保留 P1.3 r2 的 `_make_node` 模拟基础设施而不重写

已实证可用（P1.3 r2 的 7 条 + P1.4 新增的 7 条共用同一套 helper）。Node 基类 `__init__` 需要完整 `graph_init_params`，为单测构造全套太重；`__new__` + 手动注入 `_node_id` / `_node_data` / `graph_runtime_state.variable_pool` 正好覆盖 `_run()` / `_collect_inputs()` 实际读到的所有字段。

##### 2.3 `test_strategy_not_found_defense_in_depth` 为什么用直接属性赋值而不是 monkeypatch

- `BaseNodeData.model_config.extra == "allow"`、未设 `validate_assignment` → 直接赋值生效（实测脚本已验证）
- 代价最小：不需要引入 `pytest-mock`、monkeypatch fixture，不需要改源码把 `get_strategy` 暴露成可替换的属性
- 语义最接近真实故障：产线里"Literal 接受了但注册表没有"只可能由**schema 与注册表漂移**（人为改 Literal 忘改注册表 / 反之）导致，直接改 attr 正是这个场景

##### 2.4 确定性 tie-break 的三条覆盖策略

`majority_vote` 的并列处理是本节点主要的**确定性承诺**（DEVELOPMENT_PLAN.md §5.3 注释明示"不用 random.choice 避免影响测试稳定"）。为防回归，三条测试从不同角度钉：

- **行为正确性**：两路并列时，lex-smaller voter 的文本赢
- **阶次无关**：同一输入调换顺序结果必须相同
- **扩展到三路**：三元组情况下也按 voter lex order 走

单独一条不够：比如只写"行为正确性"，别人把 `min` 换成 `max` 也能偶然过（如果输入恰好按 lex 升序）；加"阶次无关"就卡死了这类 accidental pass。

---

#### 3. 验收命令与结果

```bash
uv run --project api pytest api/tests/unit_tests/core/workflow/nodes/ensemble_aggregator/ \
    -v -o addopts=""
```

> 仓库 `pytest.ini` 带 `--cov=./api`，本地 venv 未必有 `pytest-cov`，故用 `-o addopts=""` 覆盖。

**结果**：`45 passed, 1 warning in 0.15s`（warning 是 pytest 不识别 `env` config，与本包无关）。

| 分组 | 条数 | 状态 |
|---|---|---|
| `test_entities.py`（P1.1 v2.3） | 14 | 14/14 绿 |
| `test_node.py::TestSegmentTextNormalization`（P1.3 r2） | 4 | 4/4 绿 |
| `test_node.py::TestExtractVariableSelectorMapping`（P1.3 r2） | 3 | 3/3 绿 |
| **`test_node.py::TestRunHappyPath`（P1.4 新增）** | **3** | **3/3 绿** |
| **`test_node.py::TestRunFailurePaths`（P1.4 新增）** | **4** | **4/4 绿** |
| **`test_strategies.py`（P1.4 新建）** | **17** | **17/17 绿** |
| 合计 | **45** | **45/45 绿** |

---

#### 4. 回归与影响面

- **无源码改动**：P1.4 纯测试落地，`api/core/workflow/nodes/ensemble_aggregator/` 下源码未动
- **无跨节点影响**：仅新增 `test_strategies.py` + 追加 `test_node.py` 尾部类；未改其他节点测试
- **后续可复用模式**：`_make_node(pool, payload)` + `TestRunHappyPath` / `TestRunFailurePaths` 的分层结构，是 Phase 2 `parallel-ensemble` 节点单测可以直接镜像的模板（它的事件序列更复杂，但 happy / failed 的两类断言形状一致）

---

#### 5. 后续 Action（转 P1.5）

P1.4 完成后 Phase 1 后端侧完整闭环，下一步 P1.5 进前端：

- `web/app/components/workflow/nodes/ensemble-aggregator/` 建包（default / types / node / panel / use-config + strategy-selector）
- 参考 `knowledge-retrieval/` 已有节点的 React 结构
- 后端契约已经被测试钉死，前端只需对齐 TS 类型镜像 + 表单提交的 JSON 形状与 `EnsembleAggregatorNodeData.model_validate` 兼容


---

### P1.5 - P1.5 Landing 报告 — 前端 ensemble-aggregator 包骨架

> Source shard: `P1.5_LANDING.md`


> **日期**：2026-04-21
> **对应 TASKS.md**：P1.5
> **对应 DEVELOPMENT_PLAN.md**：§5.4 前端文件结构
> **前置**：P1.1 v2.3 entities / P1.2 v2 strategies / P1.3 v2 node / P1.4 45/45 单测 均已稳态
> **验收**：包骨架 7 文件落位；TS 类型镜像后端 `EnsembleAggregatorNodeData`；panel 渲染输入列表 + 策略选择 + 动态 config；`pnpm type-check:tsgo` 延到 P1.7（本地 `web/node_modules` 缺失，P1.7 才做 TS+lint 质量门）。

---

#### 1. 做了什么

在 `web/app/components/workflow/nodes/ensemble-aggregator/` 下建立 6 个计划规定的包文件（外加 1 个 `components/input-list.tsx` 辅助拆分），共 7 文件 / 635 行：

| 文件 | 行数 | 作用 |
|---|---|---|
| `types.ts` | 39 | TS 类型 1:1 镜像后端 `AggregationInputRef` / `EnsembleAggregatorNodeData`；导出 `ENSEMBLE_AGGREGATOR_NODE_TYPE` 常量 / `ENSEMBLE_STRATEGY_NAMES` / `ConcatConfig` / `DEFAULT_CONCAT_SEPARATOR` |
| `default.ts` | 94 | `NodeDefault<EnsembleAggregatorNodeType>`：默认值 `strategy_name="majority_vote"` + 空 `strategy_config`；`checkValid` 实现后端 4 条 Pydantic 校验的前端早抛（≥2 输入 / source_id 非空 / source_id 唯一 / variable_selector ≥2 段 + concat config 类型护栏） |
| `use-config.ts` | 129 | 状态 hook：`useNodeCrud` + `useAvailableVarList`；9 个 handler（add/remove/source_id/selector/strategy/strategyConfig）；`filterStringVar` 只放行 segment.text 可渲染的类型；策略切换时 reset config 以避开后端 `extra="forbid"` |
| `components/input-list.tsx` | 94 | N 条 `{source_id, variable_selector}` 行；每行 = `Input`(source_id) + `VarReferencePicker` + `RemoveButton`；下方 `AddButton` |
| `components/strategy-selector.tsx` | 158 | `DropdownMenu` 切策略 + 动态 config：`majority_vote` 展示 hint 文案；`concat` 展示 `separator` `Input` + `include_source_label` `Switch` |
| `panel.tsx` | 91 | Field(inputs) + Field(strategy) + `OutputVars(text, metadata)` |
| `node.tsx` | 30 | 画布缩略：无 input 时不渲染，否则显示策略名 + 输入条数 |

##### 1.1 TS 类型对齐（types.ts）

```ts
export type AggregationInputRef = {
  source_id: string
  variable_selector: ValueSelector   // [nodeId, key, ...path]
}

export type EnsembleAggregatorNodeType = CommonNodeType & {
  inputs: AggregationInputRef[]
  strategy_name: 'majority_vote' | 'concat'
  strategy_config: Record<string, unknown>   // 等价后端 dict[str, object]
}
```

- `strategy_config` 采用 `Record<string, unknown>`（对齐后端 `dict[str, object]`），而不是 `MajorityVoteConfig | ConcatConfig` union。原因：默认值 `{}` 在 union 里 TS 推断不一致；union 的优势在 selector 组件内部用强制 cast 即可补回，不牺牲 panel 的可用性
- 另外暴露 `ENSEMBLE_AGGREGATOR_NODE_TYPE = 'ensemble-aggregator' as const` 与后端 `__init__.py` 的同名常量对称

##### 1.2 前端 checkValid 与后端 Pydantic 的关系

前端 `checkValid` 是**早抛**，不是替代后端校验：

| 后端校验（entities.py / strategies） | 前端 checkValid |
|---|---|
| `inputs min_length=2` | `inputs.length < 2` → 错 |
| `source_id min_length=1` + `_source_id_not_blank` | 空 / 纯空白 → 错 |
| `source_id` 唯一性 (`model_validator`) | Set 去重 → 错 |
| `variable_selector min_length=2` | `selector.length < 2` → 错 |
| `strategy_name ∈ {majority_vote, concat}` | TS Literal union 编译期钉死 |
| `strategy_config` `extra="forbid"`（每个策略独立 allowlist） | 按 `strategy_name` 查白名单：`majority_vote` 必须空、`concat` 只允许 `separator` / `include_source_label`；首个未知 key → 报错（与后端 `StrategyConfigError` 语义对齐，避免脏 DSL 过前端到运行时才 FAILED） |
| `strategy_config` 已知字段类型（`separator: str`, `include_source_label: bool`） | 类型级护栏（typeof 检查） |

DSL 直接导入时后端仍会再跑一遍，前端只是把"填到一半就能看见红字"的 UX 做上来。

##### 1.3 输入行设计（input-list.tsx）

单行结构：

```
┌──────────────┬──────────────────────────────┬──┐
│ source_id    │  VarReferencePicker           │🗑│
└──────────────┴──────────────────────────────┴──┘
```

- `source_id` 走 `Input` 而不是 `VarList` 里默认的 variable input：因为**语义不同**——`source_id` 是用户自定义别名（稳定跨重命名的键），`VarList` 的 `variable` 是"把上游表达式变成可引用名"，两者都是字符串但错用会引入后端 400
- 默认命名 `model_{N}`（N 从现有最大 id + 1 起算），开发期快速拖几个 LLM 节点不用每次手填

##### 1.4 strategy-selector.tsx 的动态 form

- `DropdownMenu` 选策略（label + description）
- `majority_vote` 没有配置字段（后端 `_MajorityVoteConfig(extra="forbid")` 要求空 dict），只展示一行 hint
- `concat`：
  - `separator`：`Input`，`placeholder={DEFAULT_CONCAT_SEPARATOR}`；**输入清空时从 `strategy_config` 里删除 `separator` key**（后端默认值仅在 key 缺失时生效，`""` 会被当作空字符串拼接，不等于使用默认）
  - `include_source_label`：`Switch` inline 开关
- 切策略时 `handleStrategyChange` 会 reset `strategy_config = {}`，避免残留字段触碰新策略的 `extra="forbid"`；但 `handleSelect` 里已加守卫——**重新点当前策略不会触发 reset**，避免误清掉已配置的 separator
- `handleStrategyConfigChange` 把 patch 里 `undefined` 值视为"删除 key"而不是"写入 undefined"，让 selector 清空 input 的交互能真正把 key 从 payload 里拿掉

---

#### 2. 设计取舍

##### 2.1 为什么 `strategy_config` 用 `Record<string, unknown>` 而不是 union

前期写法尝试过：

```ts
export type EnsembleStrategyConfig =
  | Record<string, never>          // majority_vote
  | ConcatConfig                   // concat
```

问题：`defaultValue.strategy_config: {}` 在 TS union 下 inference 不稳（TS 可能推成 `Record<string, never>` 也可能推成 `ConcatConfig`，策略切换时 produce 产生"两种成员共通的属性"的交集类型，需要反复 cast）。

后端实际类型是 `dict[str, object]`（`EnsembleAggregatorNodeData.strategy_config: dict[str, object]`），前端用 `Record<string, unknown>` 是**严格更精确的镜像**，不丢信息。

##### 2.2 为什么不用 `VarList` 复用（而是自写 `input-list.tsx`）

`VarList`（`_base/components/variable/var-list.tsx`）的数据结构是 `Variable = {variable, value_selector, ...}`，字段名是 `variable`。如果复用，提交时要做 `variables ⇄ inputs` 的形变映射，读 DSL 时再反向——序列化边界多一层翻译，排错成本非线性上涨。

重写 90 行的 `input-list.tsx` 换来"panel 读写的字段名和后端 `AggregationInputRef` 完全一致"，后续 P1.6 ⑦ `getNodeOutputVars`、P1.8 DSL 导入都不用记翻译表。

##### 2.3 为什么 `default.ts` 用 `as unknown as BlockEnum` cast 而不是先修改 `BlockEnum`

严格 scope：P1.5 = "建包"，P1.6 = "9 必填 + i18n"。`BlockEnum` 属于 P1.6 ①，如果在 P1.5 就加 enum 成员，会触发三连 cascade：

- `block-icon.tsx:46` `DEFAULT_ICON_MAP: Record<BlockEnum, ComponentType>` → TS 缺 key
- `use-last-run.ts:43` `singleRunFormParamsHooks: Record<BlockEnum, any>` → 缺 key
- `use-last-run.ts:82` `getDataForCheckMoreHooks: Record<BlockEnum, any>` → 缺 key

三处都是 P1.6 的登记场，**本轮不该 touch**。用 `ENSEMBLE_AGGREGATOR_NODE_TYPE as unknown as BlockEnum` 一行 cast 把包自己围起来，P1.6 第一步加完 enum 成员后删 cast 即可（grep `as unknown as BlockEnum` 就能定位）。

##### 2.4 `filterStringVar` 为何放行 object / array 类型

后端 `_collect_inputs` 用 `segment.text`（graphon 规范渲染），`ObjectSegment` → JSON、`ArrayStringSegment` → join、`NoneSegment` → `""`。前端挡住只让 `string` 会导致**实际能跑**的场景在 panel 选不到。P1.3 r2 的 4 条 `TestSegmentTextNormalization` 已经验证这些类型的归一化，前端镜像该策略就放行所有可渲染类型。

唯一排除：`file` / `array[file]`（`isSupportFileVar={false}`）——聚合二进制引用没有定义语义。

---

#### 3. P1.5 未做的事（属于后续任务）

| 事项 | 归属 | 原因 |
|---|---|---|
| `BlockEnum.EnsembleAggregator` 入 enum | P1.6 ① | 避免 Record<BlockEnum> cascade；cast 一行兜底 |
| `BLOCKS` / `NodeComponentMap` / `PanelComponentMap` 挂节点 | P1.6 ②③ | 注册到画布，现在还拖不出来 |
| icon / 颜色 / DEFAULT_ICON_MAP | P1.6 ④ | 视觉资产 + TS 必填 key |
| `SUPPORT_OUTPUT_VARS_NODE` | P1.6 ⑤ | 否则下游引用不到 `text` 输出 |
| `singleRunFormParamsHooks` | P1.6 ⑥ | Record<BlockEnum> 必填 key |
| `getNodeOutputVars` switch-case | P1.6 ⑦ | 变量弹框里看不到 `[id, "text"] / [id, "metadata"]` |
| `canRunBySingle` | P1.6 ⑧ | 单节点调试开关 |
| i18n key (en-US + zh-Hans) | P1.6 ⑨ | 本包所有 `t('nodes.ensembleAggregator.*', ...)` 目前会渲染 key 而非文案 |
| `pnpm type-check:tsgo` / `lint:fix` 全绿 | P1.7 | 本地 web/node_modules 缺失；即使装好，单独验证 P1.5 意义有限，留给 P1.6 整体跑 |
| 前端单测 `__tests__/` | P1.7 外延 / Phase 3 | 本包 UI 以外的逻辑（use-config handler）可以加 jest，panel 的 snapshot 建议延后到 P2 一起扫 |

---

#### 4. 回归与影响面

- **无源码改动触及已有节点**：本包纯新增 7 文件
- **无跨节点影响**：P1.5 不碰 `types.ts` / `components.ts` / `constants.ts` / `utils.ts` / i18n（全部留 P1.6）
- **后端保持 45/45 绿**：本轮只改前端，API 包未动，无需回跑 pytest；若要打保险仍可以 `uv run --project api pytest api/tests/unit_tests/core/workflow/nodes/ensemble_aggregator/ -v -o addopts=""`

---

#### 5. 后续 Action

P1.5 完成后进 P1.6：

1. `types.ts` 加 `BlockEnum.EnsembleAggregator = 'ensemble-aggregator'`
2. 删 `default.ts` 的 `as unknown as BlockEnum` cast
3. 依次填 9 必填注册点（清单见 TASKS.md P1.6 表格）
4. en-US / zh-Hans 两套补齐所有 `nodes.ensembleAggregator.*` key：
   - `title` / `description`
   - `inputs` / `inputsTooltip` / `addInput` / `sourceId` / `sourceIdPlaceholder` / `variableSelector`
   - `strategy` / `strategyTooltip`
   - `strategies.majority_vote.{label,description,hint}`
   - `strategies.concat.{label,description,separator,separatorTooltip,includeSourceLabel,includeSourceLabelTooltip}`
   - `errorMsg.{duplicateSourceId,separatorMustBeString,labelMustBeBoolean,unknownStrategyConfigKey}`（最后一条接受 `key` + `strategy` 两个插值）
   - `outputVars.{text,metadata}` / `inputCount`

随后 P1.7 跑 `pnpm type-check:tsgo` + `pnpm lint:fix`，P1.8 联调 dev server 出两份 DSL。


---

### P1.6 - P1.6 Landing 报告 — 9 处前端注册 + i18n（ensemble-aggregator）

> Source shard: `P1.6_LANDING.md`


> **日期**：2026-04-21 初稿；2026-04-22 review round 1 修订
> **对应 TASKS.md**：P1.6
> **对应 DEVELOPMENT_PLAN.md**：§5.5 前端注册改动（9 必填 + 1 选填）
> **前置**：P1.5 ensemble-aggregator 包骨架 7 文件已落位
> **验收**：9 必填注册点全部就位；初稿漏了"WORKFLOW_COMMON_NODES 默认表注册"（review round 1 补），补后画布"添加节点"入口才真正解锁；i18n 两套 JSON 合法并覆盖所有 `${i18nPrefix}.*` 引用；default.ts 的 BlockEnum cast 删除；回归测试覆盖 `useAvailableNodesMetaData().nodesMap[BlockEnum.EnsembleAggregator]`；`pnpm type-check:tsgo` / `lint:fix` 延 P1.7（`web/node_modules` 缺），**P1.6 视为代码落地完成，但最终 TS/lint 质量门在 P1.7 收尾**

---

#### 1. 做了什么

| # | 文件 | 改动摘要 |
|---|---|---|
| ① | `web/app/components/workflow/types.ts` | `BlockEnum` 末尾加 `EnsembleAggregator = 'ensemble-aggregator'` |
| ② | `web/app/components/workflow/block-selector/constants.tsx` | `BLOCKS` 数组在 `VariableAggregator` 后插入 `{classification: Transform, type: EnsembleAggregator, title: 'Ensemble Aggregator'}` |
| ③ | `web/app/components/workflow/nodes/components.ts` | 顶部 `import EnsembleAggregatorNode / Panel`；`NodeComponentMap` 与 `PanelComponentMap` 各加 1 行 |
| ④ | `web/app/components/workflow/block-icon.tsx` | `DEFAULT_ICON_MAP`（`Record<BlockEnum, …>`，TS strict 要求全覆盖）加 `EnsembleAggregator: VariableX`；`ICON_CONTAINER_BG_COLOR_MAP` 加 `indigo-500`（与 VariableAggregator 的 blue 做视觉区分）|
| ⑤ | `web/app/components/workflow/constants.ts` | `SUPPORT_OUTPUT_VARS_NODE` 追加 `BlockEnum.EnsembleAggregator` |
| ⑥ | `web/app/components/workflow/nodes/_base/components/workflow-panel/last-run/use-last-run.ts` | `singleRunFormParamsHooks`（:43）+ `getDataForCheckMoreHooks`（:82）两张 `Record<BlockEnum, any>` 各补一行 `EnsembleAggregator: undefined`（聚合节点不需要自定义 single-run 表单；单跑走 `canRunBySingle` 就够）|
| ⑦ | `web/app/components/workflow/nodes/_base/components/variable/utils.ts` | `getNodeOutputVars` switch 末尾新增 `case EnsembleAggregator: push([id,"text"]); push([id,"metadata"])` |
| ⑧ | `web/app/components/workflow/utils/workflow.ts` | `canRunBySingle` 链末尾 `|| === EnsembleAggregator` |
| ⑨ | `web/i18n/en-US/workflow.json` + `web/i18n/zh-Hans/workflow.json` | 2 套 × (1 × `blocks.ensemble-aggregator` + 1 × `blocksAbout.ensemble-aggregator` + 26 × `nodes.ensembleAggregator.*`) |

附带：
- 删除 `web/app/components/workflow/nodes/ensemble-aggregator/default.ts` 中 P1.5 遗留的 `as unknown as BlockEnum` cast 和 `ENSEMBLE_AGGREGATOR_NODE_TYPE` 临时 import；改成 `type: BlockEnum.EnsembleAggregator`
- 更新 `docs/ModelNet/active/TASKS.md` P1.6 章节为 ✅ 完成

##### 1.0 review round 1 修订（2026-04-22）—— 补默认节点表 + 回归测试

初稿漏掉 `web/app/components/workflow/constants/node.ts:25` 的 `WORKFLOW_COMMON_NODES` 注册。该数组被 `workflow-app/hooks/use-available-nodes-meta-data.ts:29` 直接消费生成 `availableNodesMetaData` / `nodesMap`；`workflow/operator/add-block.tsx:66` 又依赖 `nodesMetaDataMap![type].defaultValue` 创建节点实例。不在这张表里的节点，画布"添加节点"时拿不到 `defaultValue`，UI 实际无法落地新节点。

修复：
- `constants/node.ts` 顶部加 `import ensembleAggregatorDefault from '@/app/components/workflow/nodes/ensemble-aggregator/default'`，在 `WORKFLOW_COMMON_NODES` 里插到 `variableAggregatorDefault` 之后（与 block-selector 的 BLOCKS 顺序对齐）
- `workflow-app/hooks/__tests__/use-available-nodes-meta-data.spec.ts` 加 `it.each([true, false])` 回归：两种模式下 `nodesMap[BlockEnum.EnsembleAggregator]` 必须存在，`defaultValue.type === 'ensemble-aggregator'`。测试只 mock 了 `useIsChatMode` + `useDocLink`（沿用既有 mock 模板），不引入新依赖

这条回归测试也是 reviewer 建议的通用兜底："防止以后再漏这种默认表未登记的问题"。未来新增节点时，只要遗漏 WORKFLOW_COMMON_NODES 这张表，这里的 `.each([true, false])` 会红。

##### 1.1 TASKS.md 中的文件路径校正

TASKS.md / DEVELOPMENT_PLAN.md v2 写的"注册点 ④：`web/app/components/workflow/nodes/constants.ts`（icon/颜色/默认配置）"其实与现行代码不符——该文件只放 `FILE_TYPE_OPTIONS / TRANSFER_METHOD / SUB_VARIABLES` 这类常量，并没有 icon/颜色 map。真正的 `Record<BlockEnum, …>` icon 与颜色映射在 `web/app/components/workflow/block-icon.tsx`（DEFAULT_ICON_MAP:46 + ICON_CONTAINER_BG_COLOR_MAP:97）。P1.5 landing §2.3 已经提到过这一点（列为必加的三连 cascade 之一）；P1.6 按实际位置执行。

##### 1.2 Record<BlockEnum, …> 全覆盖扫描

`grep 'Record<BlockEnum,'` 得到 5 处：

| 文件 | 类型 | 是否需要新加 key |
|---|---|---|
| `block-icon.tsx:46` | `Record<BlockEnum, ComponentType>` | ✅ 加 |
| `use-last-run.ts:43` | `Record<BlockEnum, any>` | ✅ 加（undefined）|
| `use-last-run.ts:82` | `Record<BlockEnum, any>` | ✅ 加（undefined）|
| `hooks-store/store.ts:23` | `Record<BlockEnum, NodeDefault<any>>?` | 可选（`?`），不必 |
| `use-one-step-run.ts:76` | `Partial<Record<BlockEnum, Function>>` | Partial，不必 |

##### 1.3 i18n key 清单（每条都与源码 `t(...)` 引用对齐）

源码引用（`grep i18nPrefix` 去重）：

```
addInput / inputs / inputsTooltip / inputCount
sourceId / sourceIdPlaceholder / variableSelector
strategy / strategyTooltip
strategies.{majority_vote,concat}.label
strategies.{majority_vote,concat}.description
strategies.majority_vote.hint
strategies.concat.{separator, separatorTooltip, includeSourceLabel, includeSourceLabelTooltip}
errorMsg.{duplicateSourceId, separatorMustBeString, labelMustBeBoolean, unknownStrategyConfigKey}
outputVars.{text, metadata}
```

`inputCount` 展开为 `inputCount_one` + `inputCount_other` 两条（i18next 复数惯例，`count` 插值，仓库里 `changeHistory.step*` / `nodes.iteration.*` 都是这个模式）。

两套 JSON 合计新增 2×28 = 56 条字符串，均按字母顺序插入现有 `blocks.*` / `blocksAbout.*` / `nodes.*` 区段内，便于后续 rebase upstream 时冲突最少。

##### 1.4 视觉颜色选择理由

VariableAggregator 用 `blue-500`，本节点外观应当"明显不一样、但仍属于聚合类"。选 `indigo-500`（LLM 也用 indigo）有双重含义：①节点本身接 N 个 LLM 输出，和 LLM 节点色系呼应；②和 blue 视觉可辨，不会让用户在画布上误以为是同一个节点。icon 复用 `VariableX`——现行资产里"聚合/变量类"的约定图标，若 P2 token 级节点需要再单独出一套图标，由那一轮再做。

---

#### 2. 设计取舍

##### 2.1 为什么 use-last-run 两表都给 `undefined`，不是写一个 `useEnsembleAggregatorSingleRunFormParams`

本节点的运行时输入来自上游节点（`variable_selector`），不需要用户在 single-run 时再手填任何东西。`canRunBySingle=true` 会触发 `useLastRun.handleSingleRun` 的 `isAllVarsHasValue(vars) ? callRunApi({}) : showSingleRun()` 分支；只要上游节点已 inspect 过变量，就直接 dry-run，不弹表单。写一个空 hook 反而多一层复杂度、没收益。

`getDataForCheckMoreHooks` 同理——没有需要 override 的 check-more 数据，`undefined` 即可。

##### 2.2 为什么 DEFAULT_ICON_MAP 选择 `VariableX` 而不是新画 icon

P1.6 的明确 scope 是"注册 + i18n"，不是视觉资产。新出一个 SVG 需要设计 token 对齐（`@/app/components/base/icons/src/vender/workflow/` 下约定导出结构、尺寸、stroke）和 review。`VariableX` 是现成的"聚合/变量类"通用图标，VariableAggregator / VariableAssigner / Tool / IterationStart / LoopStart / TriggerPlugin 六个节点都在复用，再加一个不会让画布更乱。P2 token 级节点如果有更严格的视觉需求，再统一出图。

##### 2.3 为什么 i18n 分隔符说明写"空行加水平线"

`nodes.ensembleAggregator.strategies.concat.separatorTooltip` 描述后端默认值 `"\n\n---\n\n"`。两套文案都把该默认显式点出来，避免用户清空 `separator` input 后看到"无任何视觉分隔"的 concat 结果误以为 bug。`strategy-selector.tsx` 里"清空 = 删除 key 让后端用默认"的交互是 P1.5 §1.4 已经钉死的；P1.6 把这个行为显式写进 tooltip。

##### 2.4 为什么 `blocks.ensemble-aggregator` 的中文用"集成聚合器"

学术语境 "ensemble learning" 中文一般译"集成学习"；Dify 已有的 "aggregator" 中文统一译"聚合器"（VariableAggregator = 变量聚合器）。组合后"集成聚合器"同时暗示了"多模型集成 + 变量级聚合"两层含义，与本节点 Phase 1 / Phase 2 未来的使用场景对齐。

---

#### 3. P1.6 未做的事

| 事项 | 归属 | 原因 |
|---|---|---|
| `pnpm type-check:tsgo` / `pnpm lint:fix` 全绿 | P1.7 | 本地 `web/node_modules` 缺失；P1.7 是专门的"前端质量门"任务 |
| 前端单测 `__tests__/` | Phase 3 / P1.7 外延 | P1.5 §3 已列入未做清单；P1.7 不要求、Phase 3 统一扫 |
| `SUPPORT_OUTPUT_VARS_NODE` 之外的联动（如节点 help link 文档）| 本轮不需要 | `genNodeMetaData` 默认 `helpLinkUri = type`，即 `/ensemble-aggregator`；真有文档时再接 |
| 视觉资产定稿（专属 SVG）| 可选 / P2 视觉复盘 | 复用 `VariableX` 已够用 |
| 10 选填：`use-nodes-interactions.ts:594` | 不做 | DEVELOPMENT_PLAN §5.5 表格已说明"仅 VariableAggregator/Assigner 用，我们不需要" |

---

#### 4. 回归与影响面

- **本包内**：`default.ts` 把 P1.5 遗留的 cast 删掉、换成 `BlockEnum.EnsembleAggregator`；逻辑不变
- **跨节点影响**：`Record<BlockEnum, …>` 三表都显式补 key，不会因缺 key 让其它节点侧触发 TS strict 错误；i18n 两套按字母序插入，`blocks.ensemble-aggregator` 不与任何已有 key 冲突（`grep '"blocks\.ensemble'` = 本次插入的两行）
- **后端不动**：本轮只改前端；后端 `uv run --project api pytest api/tests/unit_tests/core/workflow/nodes/ensemble_aggregator/ -v -o addopts=""` 45/45 绿的状态保持（P1.4 末次验证）
- **JSON 合法性**：`python3 -c "import json; json.load(open('web/i18n/en-US/workflow.json')); json.load(open('web/i18n/zh-Hans/workflow.json'))"` → `both valid`

---

#### 5. 后续 Action

1. **P1.7 前端质量门**：起 `web/node_modules`（`pnpm install`）→ `pnpm type-check:tsgo` → `pnpm lint:fix`。预期风险点：⑥ 的两张 `Record<BlockEnum, any>` 已补 key，应该直接绿；若 tsgo 对 `Record<string, ComponentType<any>>` 在 components.ts 里对新 Node/Panel 的 props 不满（`EnsembleAggregatorNode` 有 `NodeProps<EnsembleAggregatorNodeType>`、Panel 有 `NodePanelProps<...>`），视具体报错补 props 泛型即可
2. **P1.8 联调 + 导出 2 份 DSL**：按 TASKS.md P1.8 跑 workflow 模式与 advanced-chat 模式，导出 `response_level_ensemble.yml`
3. **Phase 3 i18n 全量 review**：本轮只覆盖 en-US / zh-Hans 两套（DEVELOPMENT_PLAN §7.4 强制），其它 22 种语言在 Phase 3.3 才扫；upstream 合并本 fork 时若要入主干，需要补齐其余语言


---

### P1.7 - P1.7 Landing — Frontend Quality Gate

> Source shard: `P1.7_LANDING.md`


日期：2026-04-22

#### 范围

仅对 P1.6 落地的 `ensemble-aggregator` 相关表面跑 `pnpm install` +
`pnpm type-check:tsgo` + `pnpm eslint --fix` + `pnpm vitest` 回归，并复核
en-US / zh-Hans i18n 键集对齐。**不动** 仓库历史遗留 warning/suppression。

#### 命令与结果

| 步骤 | 命令 | 结果 |
| --- | --- | --- |
| 1 | `pnpm install`（仓库根） | exit 0；2m 22s；1361 包；workspace lockfile up-to-date |
| 2 | `cd web && pnpm type-check:tsgo` | exit 0；无输出（tsgo 全绿） |
| 3 | `pnpm eslint --fix <P1.6 surface>` | exit 0；0 errors / 27 warnings（warnings 全部为仓库历史遗留或在 `eslint-suppressions.json` 内未我方新增类别） |
| 4 | `pnpm test -- --run use-available-nodes-meta-data.spec.ts` | Test Files 1 passed；Tests **4 passed**（含 P1.6 review round 1 新增的 `it.each([true,false])` EnsembleAggregator 回归护栏） |
| 5 | en-US vs zh-Hans `nodes.ensembleAggregator.*` + `blocks(.About).ensemble-aggregator` 键集 diff | 空集（25 + 2 = 27 键完全对齐） |

#### 本轮真正的代码改动（3 文件）

- `web/app/components/workflow/nodes/ensemble-aggregator/default.ts:22`
  - `checkValid(payload, t: any)` → `t: (key: string, options?: Record<string, unknown>) => string`
  - **原因**：`ts/no-explicit-any` 是 error。兄弟节点（`llm/default.ts` 等）
    同样写 `t: any`，但它们在 `eslint-suppressions.json` 里有批量抑制；我们
    新落地的文件没有进抑制表，所以只能正面修。类型签名借用
    `human-input/default.ts:34` 的 i18next 风格 `(key, options) => string`。
- `web/app/components/workflow/nodes/components.ts:15-18`
  - `EndNode/EndPanel` 与 `EnsembleAggregatorNode/EnsembleAggregatorPanel`
    的 import 顺序被 eslint 自动按字典序调整。纯顺序变更。
- `web/app/components/workflow/nodes/ensemble-aggregator/use-config.ts:1`
  - `import type { Var, ValueSelector }` → `{ ValueSelector, Var }`。
    同样是 eslint 自动排序。

#### 仍有的 warning（未处理，原因如下）

均为 `eslint --cache --fix` 运行后仍然存在的 **warning 级别**（lint exit 0）：

| 位置 | 规则 | 处理 |
| --- | --- | --- |
| `web/app/components/workflow/block-icon.tsx:6-29`（24 条） | `hyoban/prefer-tailwind-icons` | P1.6 只在该文件末尾加 1 个 key；警告对整个 import 块生效，属仓库历史遗留 — 不在 P1.7 范围 |
| `web/app/components/workflow/nodes/_base/components/workflow-panel/last-run/use-last-run.ts:240` | `react/exhaustive-deps` | 非 P1.6 改动行，仓库历史遗留 |
| `web/app/components/workflow/nodes/ensemble-aggregator/components/input-list.tsx:60` | `react/no-array-index-key` | P1.5 scaffolding；本节点当前交互只有"追加 / 删除"两种，不涉及重排序，index 实际稳定。若未来加"拖拽排序"需注入 `__uid` — 计入 P2/P3 polish |
| `web/app/components/workflow/nodes/ensemble-aggregator/components/strategy-selector.tsx:93` | `hyoban/prefer-tailwind-icons` | P1.5 scaffolding；可替换为 `<i className="i-ri-arrow-down-s-line …" />`，但 open 态要求切换 text color class，直接沿用图标组件更符合兄弟节点做法 — 计入 P3 polish |

#### 关键校验点回证（TASKS.md §P1.7 的 2 条重点）

- ⑥ `singleRunFormParamsHooks` / `getDataForCheckMoreHooks` 的
  `Record<BlockEnum, any>`：tsgo 0 error 即证明两张表已覆盖
  `EnsembleAggregator` key（`use-last-run.ts:74, 114`）。
- en-US / zh-Hans i18n 键集：`workflow.json` 两份 `nodes.ensembleAggregator.*`
  与 `blocks(.About).ensemble-aggregator` 键集 **完全相同**（25 + 2 = 27）。

#### 退出状态

P1.7 **✅ 完成**。画布侧代码路径在 TS strict + ESLint + 单测三道关全绿。
进入 P1.8：起 dev server、画布手动回归 workflow + advanced-chat 两种模式、
导出 2 份 DSL（`docs/ModelNet/examples/{workflow_mode,chat_mode}/response_level_ensemble.yml`）。


---

### P1.8 - P1.8 Landing — 静态完成 + 2 份响应级 DSL（联调浏览器回归待用户执行）

> Source shard: `P1.8_LANDING.md`


> **日期**：2026-04-24（初稿）；code review round 1 修订（降级状态 + 4 处代码修复）
> **对应 TASKS.md**：P1.8（Phase 1 收尾）—— **本节状态：🚧 静态完成 / 浏览器 E2E 回归未闭环**
> **对应 DEVELOPMENT_PLAN.md**：§5.7 验收标准（workflow + advanced-chat 两模式）
> **前置**：P1.1–P1.7 全绿（后端 45/45 pytest、前端 tsgo 0 error、eslint 0 error、i18n 键集 27/27 对齐）
> **本轮闭环内容**：2 份 DSL 落位；每份都静态通过 YAML 解析 + `EnsembleAggregatorNodeData` Pydantic 校验 + 模式合法性检查（workflow 不含 answer、advanced-chat 不含 end/trigger-*）+ 策略实际执行预演；graphon `Node._registry` 含 `ensemble-aggregator` 注册项
> **本轮未闭环内容**：dev server 端到端回归（起 server → 画布拖节点 → 浏览器看流式聚合）。P1.8 标题是"联调"，这一步是本任务的核心含义，未执行即 ≠ 完整 ✅。需由用户在自己的本机环境按 §4.1 命令跑一遍后，才能把状态改为 ✅

---

#### 1. 交付物

##### 1.1 DSL 文件（2 份）

| 模式 | 文件 | 图 | 策略 | 用意 |
|---|---|---|---|---|
| workflow | `docs/ModelNet/examples/workflow_mode/response_level_ensemble.yml` | `start → [llm_a, llm_b, llm_c] → aggregator → end` | `majority_vote`（`strategy_config: {}`）| 三路情感分类器（positive/negative/neutral）共识投票，End 导出 `label` + `metadata` |
| advanced-chat | `docs/ModelNet/examples/chat_mode/response_level_ensemble.yml` | `start → [llm_a, llm_b, llm_c] → aggregator → answer` | `concat`（`include_source_label: true`）| 三种风格答复（concise/creative/steps）加源标签拼接后流给 Answer |

两份 DSL 都使用 `langgenius/openai/openai` provider + `gpt-4o-mini`（复用现有 fixture 的 `dependencies` 块；想用其它供应商只需改 `model.provider` / `model.name` / 顶层 `dependencies[0].value` 三处）。

##### 1.2 为什么两份 DSL 各用一种策略，而不是两份都跑两种

TASKS.md P1.8 原文"跑 majority_vote + concat 两策略"——字面意思是 workflow 模式要验证两种策略。但一份 DSL 只能编码一个 `strategy_name`，硬塞不进去。两个可选路径：

- **路径 A**：写 4 份 DSL（workflow×2 + chat×2，每份一种策略）
- **路径 B**：写 2 份 DSL，每份演示一种更适合该模式的策略；在注释里说清楚切换方法

路径 B 更符合"最小示例 + 可扩展"的意图，也对齐 DEVELOPMENT_PLAN §5.7 的 1 份 workflow / 1 份 chat 验收样本。选 B 的具体理由：

- **`majority_vote` 本质是短文本共识**（"完全相同字符串投票"）。三个 LLM 各产出 3 段长文，几乎不可能字面相同 → 永远走 tie-break 字典序，输出一路上游的文本。用于 chat 模式下展示"多模型融合"效果反而误导
- **`concat` 保留所有上游贡献**。放进 chat 模式下配合 `include_source_label` 的输出最直观：用户一眼看到三路模型各自给了什么。workflow 模式下 `concat` 再套 End 导出的 string/object 也跑得通，没必要再复一份
- **切换成本很低**：两份 DSL 顶部注释都写了"如何切到另一种策略"；用户把 `strategy_name` + `strategy_config` 两个字段换掉即可，不需要重画图

如果后续 Phase 3 i18n / README 统一要求"每种 {mode × strategy} 组合各一份"，再补 2 份即可（位置：同目录增量添加 `*_majority_vote.yml` / `*_concat.yml`）。

##### 1.3 辅助产物
- `docs/ModelNet/examples/{workflow_mode,chat_mode}/` 两个目录新建
- 本 landing 报告

---

#### 2. 静态验证（已跑）

##### 2.1 Pydantic + 模式合法性

命令（`uv run --project api python`）：

```python
import yaml, sys
sys.path.insert(0, "api")
from core.workflow.nodes.ensemble_aggregator.entities import EnsembleAggregatorNodeData

INVALID_FOR_CHAT = {"end", "trigger-webhook", "trigger-schedule", "trigger-plugin"}  # web/app/components/workflow/update-dsl-modal.helpers.ts:46
INVALID_FOR_WORKFLOW = {"answer"}

def check(path, mode):
    data = yaml.safe_load(open(path))
    assert data["app"]["mode"] == mode
    nodes = data["workflow"]["graph"]["nodes"]
    invalid = INVALID_FOR_CHAT if mode == "advanced-chat" else INVALID_FOR_WORKFLOW
    assert not any(n["data"]["type"] in invalid for n in nodes)
    (agg,) = [n for n in nodes if n["data"]["type"] == "ensemble-aggregator"]
    EnsembleAggregatorNodeData.model_validate(agg["data"])  # raises on any schema error
```

结果：

```
=== docs/ModelNet/examples/workflow_mode/response_level_ensemble.yml (mode=workflow) ===
  ensemble-aggregator OK: strategy=majority_vote, inputs=[('model_a', ['llm_a', 'text']), ('model_b', ['llm_b', 'text']), ('model_c', ['llm_c', 'text'])], config={}
  nodes: ['start', 'llm', 'llm', 'llm', 'ensemble-aggregator', 'end']
  edges: 7
  validation: PASS

=== docs/ModelNet/examples/chat_mode/response_level_ensemble.yml (mode=advanced-chat) ===
  ensemble-aggregator OK: strategy=concat, inputs=[('concise', ['llm_a', 'text']), ('creative', ['llm_b', 'text']), ('steps', ['llm_c', 'text'])], config={'include_source_label': True}
  nodes: ['start', 'llm', 'llm', 'llm', 'ensemble-aggregator', 'answer']
  edges: 7
  validation: PASS
```

这等价于前端 `validateDSLContent(content, AppModeEnum.ADVANCED_CHAT)`（`web/app/components/workflow/update-dsl-modal.helpers.ts:59-69`）+ 后端 `EnsembleAggregatorNodeData.model_validate(...)` 两道门同时通过。

##### 2.2 策略实际执行预演

用 DSL 里真实的 `inputs` 形状喂进 registered 策略，确认产出符合预期（而不是停在"数据结构合法"层面）：

```
registered: ['concat', 'majority_vote']

majority_vote  -> 'positive' | {'strategy': 'majority_vote', 'votes': {'positive': 2, 'neutral': 1}, 'winner_votes': 2, 'tie_break_applied': False, 'contributions': {'model_a': 'positive', 'model_b': 'positive', 'model_c': 'neutral'}}

concat         -> '[concise]\nA terse answer.\n\n---\n\n[creative]\nA vivid analogy.\n\n---\n\n[steps]\n1. Do X. 2. Do Y. 3. Do Z.'
concat meta    -> {'strategy': 'concat', 'separator': '\n\n---\n\n', 'include_source_label': True, 'contributions': {'concise': 'A terse answer.', 'creative': 'A vivid analogy.', 'steps': '1. Do X. 2. Do Y. 3. Do Z.'}}
```

##### 2.3 graphon 注册链路

```python
from core.workflow.node_factory import register_nodes
register_nodes()
from graphon.nodes.base.node import Node
assert Node._registry["ensemble-aggregator"]["1"] is EnsembleAggregatorNode
```

结果：`core.workflow.nodes.ensemble_aggregator.node.EnsembleAggregatorNode version=1`；`Node._registry` 全集同时含 `start / llm / end / answer / ensemble-aggregator` 等 29 个类型。

> 注意：不能只 `import core.workflow.node_factory` 就以为注册完成——该 module 把真正的 `_import_node_package("core.workflow.nodes")` 放在 `register_nodes()` 函数体里（`node_factory.py:104-108` 装了 `@lru_cache(maxsize=1)`），必须显式调一次。生产路径上 `DifyNodeFactory.__init__` 会调（`api/core/workflow/node_factory.py:119`），本地验证脚本要手动触发。

##### 2.4 已有回归套件再跑一遍
```
uv run --project api pytest api/tests/unit_tests/core/workflow/nodes/ensemble_aggregator/ -v -o addopts=""
→ 45 passed in 0.14s
```
P1.1 schema 14 + P1.3 round-2 7 + P1.4 新增 24。新写的 DSL 不改任何 `ensemble_aggregator/` 代码，套件行为不变，作为 P1.8 的 smoke 存档。

---

#### 3. 设计要点

##### 3.1 `source_id` 语义化命名
Workflow DSL 用 `model_a / model_b / model_c`（强调"哪个并联路径"），Chat DSL 用 `concise / creative / steps`（强调"这一路贡献了什么风格"）。

理由：`source_id` 既是 `metadata.contributions` 的键，又是 `majority_vote` 并列时的字典序 tie-break 依据（v2.2 钉死、P1.2 实现）。用人类可读的语义词比 `llm_a/b/c` 更有信息量——用户打开 metadata 一眼知道"positive 这一票来自 concise 风格的那条"而不是"llm_a 那条，llm_a 是啥？"。

##### 3.2 `variable_selector` 只取 `text`
三路 LLM 的聚合输入都是 `[llm_x, "text"]`，没有取 `[llm_x, "usage"]` / `[llm_x, "reasoning_content"]` 等。这是最小化可跑示例的选择：`text` 是所有 LLM provider 都会输出的唯一稳定字段，不因换 provider / 换模式而变。

如果未来做"按 token 用量投票"或类似需求，第二段 segment 可以换成 `usage.total_tokens`（graphon `SELECTORS_LENGTH=2` 仅要求前两段，第 3 段起是路径 — P1.1 v2.3 `_selector_segments_not_blank` 的设计已经兜住这点）。

##### 3.3 workflow DSL 分类任务选 `gpt-4o-mini` + `temperature=0`
三个 LLM 全部 temperature=0，system prompt 限制 "positive / negative / neutral" 单词。目的是让 `majority_vote`（exact string match）真能出"2-3 票同意"的场面。若 temp 稍高或不限制输出格式，几乎必然三路字面不同 → tie-break 退化成"永远输出字典序最小的 source_id 对应的文本"——示例就废了。

3 个 prompt 都大同小异是为了让模型共识率高，但留了措辞差异（"strict sentiment classifier" / "Classify the sentiment" / "Return only one of these three lowercase labels"）避免用户以为"三路等价复制没意义"。

##### 3.4 chat DSL 三路风格差异化、temperature 拉开
- `concise`: temp 0.3，要简洁
- `creative`: temp 0.9，要比喻 + 例子
- `steps`: temp 0.2，要 3 步编号

这样 `concat + include_source_label=true` 的输出对用户肉眼就很有信息量：`[concise] ... [creative] ... [steps] ...`，即"同一问题的三种回答风格并列"。`default separator` 用后端的 `"\n\n---\n\n"`（不显式覆盖 → 走 concat strategy 的默认；P1.5 UI 注释："清空 separator input = 删除 key 让后端用默认"）。

##### 3.5 `opening_statement` 仅 chat DSL 写
Advanced-chat 模式顶部 `opening_statement` 是 Dify 聊天 UI 的 "AI 开场白"。workflow 模式不走聊天界面，该字段即便设置也不会渲染，保持空串与 `basic_llm_chat_workflow.yml` 对齐。

---

#### 4. 未做的事（显式声明）

##### 4.1 浏览器手动回归：用户本地操作

本轮没有执行"起 dev server → 画布拖出节点 → 浏览器看到流式文本"的端到端操作。原因：

- 本环境 `:3000` 被 `open-webui` 容器占用（`docker ps` 可见），Dify 专用 Postgres/Redis 没在 `docker ps` 出现，`api_root:503 / web_root:503`
- 本机有多个生产容器在跑（credits-service、litellm、new-api 等 20+ 个），盲目起 Dify docker-compose 有污染共享 `postgres`/`redis` 的风险
- Agent 不应未经用户授权改动共享基础设施（CLAUDE.md 的 "Executing actions with care" 规则：destructive / shared-state actions 需确认）

用户自行在本机 dev 环境回归的建议命令（需要一个独立 Dify 栈；参考 `api/AGENTS.md` 与仓库根 `docker/docker-compose.yaml`）：

```bash
# 0. 准备独立 Dify middleware（如未跑过）
cd docker && docker compose -f docker-compose.middleware.yaml up -d

# 1. 后端 + Celery
uv run --project api python -m flask run --host 0.0.0.0 --port 5001 --debug
uv run --project api celery -A app.celery worker -P gevent -c 1 -l INFO

# 2. 前端
cd web && pnpm dev   # 默认 :3000；若端口冲突用 PORT=3100 pnpm dev

# 3. 浏览器
#    - 创建 "workflow" 类型应用 → Studio → Import DSL → docs/ModelNet/examples/workflow_mode/response_level_ensemble.yml
#    - 单跑：query 输 "I love this product!" → End.label 应出 "positive"
#    - 再 Import chat DSL → 新建 "advanced-chat" 应用 → 发消息 → Answer 节点逐字流渲染三段拼接输出
```

##### 4.2 前端 UI 单测
P1.5 / P1.6 的 `ensemble-aggregator` 包内尚未写 `__tests__/`。DEVELOPMENT_PLAN §7.1 把"前端单测"归到 Phase 3（集成测试 + 4 份 DSL mode validation 测试），本轮不追加。

##### 4.3 API `/workflow run` 集成测试
本轮不写 CI-only 集成测试（响应级节点的集成测试同样归 Phase 3 / P3.1）。本文 §2 的 Pydantic + 策略预演 + 注册链路三道校验已覆盖单节点行为；端到端要等 Phase 3 用 mock 或真实 LLM provider 一次性补齐。

##### 4.4 Phase 2 相关
本 landing 不涉及 `parallel-ensemble` / `LlamaCppClient` / `LocalModelRegistry`。Phase 2 规划见 TASKS.md §"Phase 2 — Token 级并联节点（11–14 天）"。

---

#### 5. 回归与影响面

- **后端代码**：不改 `api/core/workflow/nodes/ensemble_aggregator/` 下任何文件；`uv run --project api pytest api/tests/unit_tests/core/workflow/nodes/ensemble_aggregator/ -v -o addopts=""` 45/45 绿
- **前端代码**：不改 `web/app/components/workflow/nodes/ensemble-aggregator/` 下任何文件；P1.7 的 tsgo / eslint / i18n 状态不变
- **新增文件**：2 份 DSL + 本 landing 报告 + `docs/ModelNet/examples/` 目录树
- **影响到的现有文件**：`docs/ModelNet/active/TASKS.md`（P1.8 标 ✅ 并附 landing 索引）

---

#### 6. 后续 Action

1. **用户在本机执行 §4.1 的浏览器回归**：确认画布确实能拖出节点、导入 DSL、run 出聚合结果。若发现注册链路或模式校验死角，回开对应 P1.x landing 做兜底修复
2. **Phase 2 启动条件**：Phase 1 所有 landing（P1.1–P1.8）闭环；准备 `api/configs/model_net.yaml` 的 sample 模板 + SSRF / 控制台 API 模块骨架
3. **Phase 3**（与 Phase 2 P2 末尾 token-级 DSL 合并处理）：4 份 DSL mode validation 测试（workflow×2 + chat×2）+ README / SECURITY + i18n 全量 review


---

## Phase 2 - Parallel ensemble / local backend SPI

### P2.1 - P2.1 Landing — ModelSpec + LocalModelRegistry 单例

> Source shard: `P2.1_LANDING.md`


日期：2026-04-27

#### 范围

落地 Phase 2 的第一块基础设施：模型注册表的服务端表示与单例容器。
本节**不**实现 HTTP 客户端（P2.2）、**不**新增 dify_config 配置项（P2.2）、
**不**触前端（P2.4 / P2.11）。仅产出 3 个文件 + 1 份 landing。

#### 路径决定（已在 TASKS.md 顶部锁定）

```
api/core/workflow/nodes/parallel_ensemble/llama_cpp/
├── __init__.py
├── exceptions.py
└── registry.py
```

放节点同包，不放 v2 计划草稿里的 `api/core/model_runtime/local_models/`。
理由：当前 fork 已删除 `api/core/model_runtime/`。`api/core/workflow/nodes/parallel_ensemble/__init__.py`
顺手放上 `PARALLEL_ENSEMBLE_NODE_TYPE = "parallel-ensemble"` 常量，
为 P2.8 的节点导出预留位置（不做循环 import 风险，因为 P2.8 才会
反向 `from . import PARALLEL_ENSEMBLE_NODE_TYPE`）。

#### ModelSpec 字段对齐

字段名 1:1 镜像 `docs/ModelNet/research/references/model_info.json` —— PN.py 用户原 yaml
不动即可迁移。**`EOS` 大写、`stop_think` 下划线**，这两个反 PEP-8 命名
是和 PN.py 协议层兼容性写死的，不是失误。

| 字段 | 类型 | 默认 | 备注 |
| --- | --- | --- | --- |
| `id` | `str` (min_length=1) | — | 注册表 key（节点引用用） |
| `model_name` | `str` (min_length=1) | — | llama.cpp `/completion` `model` |
| `model_arch` | `str` | `"llama"` | 模板路由用，目前只有 llama |
| `model_url` | `AnyUrl` | — | **服务端唯一可见**，URL 不外泄 |
| `EOS` | `str` (min_length=1) | — | 终止 token 字面量 |
| `type` | `Literal["normal","think"]` | `"normal"` | think 类型走 ThinkPhaseRunner（P2.6） |
| `stop_think` | `str \| None` | `None` | type=think 时由 P2.6 校验非空 |
| `weight` | `float` (gt=0) | `1.0` | 聚合器加权 |
| `request_timeout_ms` | `int` (gt=0) | `30000` | 客户端超时（P2.2 用） |

`ConfigDict(extra="forbid", frozen=True)`：
- **extra=forbid** = **yaml 加载层**的硬约束：`model_net.yaml`（运维侧）里
  写错字段（typo 或 rogue 字段）立刻 boot 阶段拒，不会被静默吞下。
  ⚠️ **这层并不挡住 DSL 偷塞 `model_url`**——ModelSpec 只在解析服务端 yaml
  时被实例化，DSL 走 alias 字符串到 registry 反查 spec，根本到不了
  ModelSpec 的 validator。DSL 侧的 SSRF 防护是 `ParallelEnsembleNodeData`
  自己的 `extra="forbid"` 责任（P2.8 落地 + P2.10 `test_extra_forbid_dsl`
  覆盖）。两道闸是独立的，不要混为一谈，详见 `TASKS.md` Phase 0 与 `EXTENSIBILITY_SPEC.md` §4.4。
- **第一道 SSRF 闸**仍是 `list_aliases()` 不返回 `model_url`（ADR-3）。
- **frozen=True** = `ModelSpec` 是不可变 value object，可以安全跨线程引用，
  和 P2.6 `TokenVoteEngine` 的 `ThreadPoolExecutor` 锁步推进契合。

#### LocalModelRegistry 关键设计

- **单例**：`instance()` 双检锁，`reset_for_testing()` / `for_testing(path)`
  专给单测。生产路径走 `instance()`。
- **配置路径解析**：`DEFAULT_REGISTRY_PATH` 基于 `registry.py` 反推 API root，
  cwd-independent 地指向 `api/configs/model_net.yaml`；`_resolve_path()` 用
  `getattr(dify_config, "MODEL_NET_REGISTRY_PATH", DEFAULT_REGISTRY_PATH)`。
  目前 `dify_config` 没有这个字段，走这个 fallback；
  P2.2 在 `dify_config.feature` 里加该 `Field` 后，自动接入，**registry.py
  本身不需要再改一行**。
- **R9（missing yaml 不能炸 boot）**：`_load` 里 `path.exists()` 早走，
  empty dict + `logger.warning`。已用 smoke 5 验证。
- **`list_aliases` 不返回 url**（ADR-3）：返回 `AliasInfo` TypedDict
  `{id, model_name, type}`。smoke 3 用 `assert "model_url" not in a` 钉死。
- **加载阶段健壮性**：
  - 顶层非 mapping、`models` 非 list、entry 非 mapping → `RegistryFileError`
  - duplicate `id` → `RegistryFileError`（防止 yaml 拼写撞 key 后默默覆盖）
  - `ModelSpec.model_validate` 抛错 → 转 `RegistryFileError` 带 index 上下文
  - `OSError`/`yaml.YAMLError` → `RegistryFileError`
- **空 yaml 文件 / `top: null`** 视为 0 模型，不视为错（运维清空 yaml 重启的场景）

#### Exception 层级

```
LlamaCppNodeError                 (root, 节点层 catch-all)
└── ModelRegistryError            (registry 子族)
    ├── RegistryFileError(path, reason)
    └── UnknownModelAliasError(alias)
```

仿 `ensemble_aggregator/exceptions.py` 的语义字段 + 友好 message 模式。
`UnknownModelAliasError` 同时是 `ModelRegistryError` 与 `LlamaCppNodeError`，
P2.8 节点 `_run` 里可以单 except 整族。

#### Smoke 验收（10/10 绿）

| # | 场景 | 命令位置 |
| --- | --- | --- |
| 1 | `ModelSpec.model_validate` 吃下 `docs/ModelNet/research/references/model_info.json` 全部 7 条 | inline |
| 2 | `extra="forbid"` 拒 unknown key | inline |
| 3 | `list_aliases()` 输出仅含 `{id, model_name, type}`、无 `model_url` | inline |
| 4 | `get("nope")` 抛 `UnknownModelAliasError`，且属 `ModelRegistryError` / `LlamaCppNodeError` 子类 | inline |
| 5 | 文件不存在 → 空 registry + WARNING 日志（R9）| inline |
| 6 | duplicate `id` → `RegistryFileError(path, "duplicate model id 'dup'")` | inline |
| 7 | yaml entry 含 rogue 字段 → `RegistryFileError`（带 Pydantic extra_forbidden 详情）| inline |
| 8 | yaml 语法错误 → `RegistryFileError`（包了 `yaml.YAMLError`）| inline |
| 9 | 空 yaml 文件 → 空 registry，不报错 | inline |
| 10 | `instance()` 两次返回同一对象（单例身份）| inline |

无回归：`uv run --project api pytest api/tests/unit_tests/core/workflow/nodes/ensemble_aggregator/ -q -o addopts=""` → **47/47 绿**。

#### 显式延后（P2.2 / P2.3 范围）

- `dify_config.MODEL_NET_REGISTRY_PATH: str` Field 注册（用户已能通过
  `getattr` fallback 跑，但 P2.2 要把它写进 `feature/__init__.py` 让运维
  能 env 覆盖）
- sample `api/configs/model_net.yaml.example` 模板
- `api/configs/.gitignore` 加 `model_net.yaml` 真实文件项
- `LlamaCppClient`（`completion` / `apply_template`，强制 ssrf_proxy）
- 写入 `tests/unit_tests/core/workflow/nodes/parallel_ensemble/llama_cpp/`
  pytest 单测文件（P2.3 任务）—— 本节用 inline smoke 已等价覆盖 5 条
  P2.3 验收用例（test_registry_load / test_extra_forbid / test_unknown_alias /
  test_list_aliases_no_url / [ssrf_proxy 留 P2.3]）

  ⚠️ **建议把 10 条 smoke 提前固化为 pytest 文件，不必等 P2.3**：
  registry 是 SSRF 边界 + yaml 解析，inline smoke 只在 landing 写一次没有
  CI 防回归。`P2.1` 标完成前补一份
  `api/tests/unit_tests/core/workflow/nodes/parallel_ensemble/llama_cpp/test_registry.py`
  对应 smoke 1–10（reset_for_testing / for_testing(path) 已为此预留），
  代价 < 1 小时，避免 P2.2 改 dify_config 时无声破坏 fallback 路径。

#### 退出状态

P2.1 **✅ 完成**（10/10 smoke 绿 + P1 47/47 回归无损）。下一步 P2.2 把
`MODEL_NET_REGISTRY_PATH` 进 `dify_config`、写 sample yaml、实现
`LlamaCppClient`（强制 `core.helper.ssrf_proxy`）。


---

### P2.2 - P2.2 Landing — LlamaCppBackend + sample yaml + dify_config + BACKEND_CAPABILITIES.md

> Source shard: `P2.2_LANDING.md`


日期：2026-04-27

#### 范围

把 P2.1.5 SPI 冻结后留下的占位 `LlamaCppBackend(ModelBackend)` 转成生产实现，落地：

- 6 个 SPI 方法（`capabilities` / `validate_requirements` / `generate` / `generate_stream` / `step_token` / `apply_template`）
- 2 个模块级纯函数（`parse_top_probs` / `parse_sse_chunks`，Phase 4 fork 可直接 reuse + mock）
- `dify_config.MODEL_NET_REGISTRY_PATH` + `PARALLEL_ENSEMBLE_MAX_WORKERS` 字段
- `api/configs/model_net.yaml.example` + `MODEL_NET_README.md` + `.gitignore` 屏蔽真 yaml
- `docs/ModelNet/architecture/BACKEND_CAPABILITIES.md`（P2.2.4 合约文件）
- `tests/.../test_llama_cpp_backend.py` 25 条单测

**不做**：`node_factory.py` 注入分支（延后 P2.9）、控制台 API（P2.4）、前端面板（P2.11）、节点 `_run`（P2.8）。

#### SPI 方法实现要点

##### `capabilities`

`STREAMING + TOKEN_STEP + TOP_PROBS + POST_SAMPLING_PROBS + CHAT_TEMPLATE`，模块顶层 `frozenset` 常量。`LOGITS_RAW` 和 `FUNCTION_CALLING` 不声明（见 BACKEND_CAPABILITIES §4）。

##### `validate_requirements`

llama.cpp 没有硬 `top_k` 上限（不像 OpenAI 20），也支持 logprobs / chat template，所以唯一 static-reject 的 requirement 是 `needs_function_calling=True`（capability 不存在）。其它 requirement 走默认 capability-bottom 兜底。

##### `generate`

`POST {model_url}/completion`，body `{prompt, ...filtered_params, stream: false}`。`stop_type` 映射到 `finish_reason`，`limit` 标准化为 OpenAI 风格 `length` 让跨 backend metadata 可携带。

##### `generate_stream`

`POST {model_url}/completion`，body `stream: true`。`parse_sse_chunks` 解析 `data: {...}` 行。⚠️ ssrf_proxy 当前缓冲响应 → 生成器在服务端完成后才有数据；语义正确但非真实时增量。代码注释指明 P2.13 dev server 兜底，将来加流式 ssrf primitive 即可升级为真实增量。

##### `step_token`

`POST {model_url}/completion`，body `{prompt, max_tokens:1, n_probs:k, post_sampling_probs:true}`。`parse_top_probs` 模块函数从 `completion_probabilities[0].top_probs` 抽 top-k；EOS / 空字符串 token 重写为 `<end>` 哨兵保留 PN.py 契约（聚合器 EOS-agnostic）。

##### `apply_template`

`POST {model_url}/apply-template`，body `{messages: [...]}`。响应 `prompt` 字段；缺 prompt 时降级为空字符串 + warning（PN.py 同语义）。

#### 解析独立函数（R7）

固化 `top_probs` schema 的关键，提到模块级而不是类内私有方法的两个理由：

1. **Phase 4 复用**：vLLM / OpenAI adapter 大概率会复用「dict 形 logprobs → `list[TokenCandidate]`」转换骨架；放类外避免 Phase 4 写「from `_LlamaCppBackend__parse_top_probs` import」之类的访问尴尬。
2. **测试独立**：`parse_top_probs` 不需要 mock HTTP，4 条护栏（EOS 重写 / 空 completion_probabilities / 空 top_probs / 非 dict 项跳过）都是纯函数测试，未来 schema 漂移时一眼能看出被改的是 schema 还是 SPI。

#### 配置字段

新建 `ModelNetConfig(BaseSettings)`：

```python
class ModelNetConfig(BaseSettings):
    MODEL_NET_REGISTRY_PATH: str = Field(default="api/configs/model_net.yaml", description=...)
    PARALLEL_ENSEMBLE_MAX_WORKERS: PositiveInt = Field(default=8, description=...)
```

挂进 `FeatureConfig` MRO（alphabet 顺序，`ModelLoadBalanceConfig` 之后 `ModerationConfig` 之前）。`ModelRegistry._resolve_path` 已是 `getattr(dify_config, "MODEL_NET_REGISTRY_PATH", DEFAULT)`，所以零修改接入。

#### sample yaml + .gitignore

- `api/configs/model_net.yaml.example`：3 条示例 entry，含 normal/think 两类、`weight` overload 一例；字段注释 + `extra="forbid"` 行为说明。
- `api/configs/MODEL_NET_README.md`：path 覆盖 / 缺文件行为（R9）/ SSRF 边界。
- `.gitignore`：加 `api/configs/model_net.yaml` 一行（真 yaml 永不提交）。

#### BACKEND_CAPABILITIES.md（P2.2.4）

5 节：

1. **Capability 矩阵**（4 backend × 8 capability，与 EXTENSIBILITY_SPEC §3.2 同步）
2. **三个语义坑**：POST_SAMPLING_PROBS vs LOGITS_RAW / OpenAI top_logprobs ≤ 20 / vLLM log-softmax 换算（含 OpenAICompatBackend / vLLM adapter 示例代码）
3. **加 backend 的合约**：声明集合 + fixture 兜底 + override `validate_requirements`
4. **当前 v0.2 实际声明**（仅 llama_cpp）
5. **修订指引**：capability 增删改要三处同步（spi/capability.py + 本文档 + EXTENSIBILITY_SPEC + fixture）

`test_llama_cpp_backend.py::TestCapabilities::test_default_set_matches_backend_capabilities_doc` 是这份文档的可执行快照 — 文档改了但代码忘改 / 反过来 / fixture 漂移，三处任一不一致就 CI 失败。

#### 测试

`tests/.../parallel_ensemble/test_llama_cpp_backend.py`，25 条：

| 类 | 条 | 内容 |
|---|---:|---|
| `TestCapabilities` | 3 | 默认集 / LOGITS_RAW 不在 / FUNCTION_CALLING 不在 |
| `TestValidateRequirements` | 3 | min_top_k=999 放行 / needs_fc=True 拒 / needs_fc=False 放行 |
| `TestParseTopProbs` | 4 | EOS/空字符串重写 `<end>` / 空 completion_probabilities / 空 top_probs / 非 dict 项跳过 |
| `TestParseSseChunks` | 4 | 双 chunk + final / 服务器中断兜底 final / 不可解析行跳过 / 非 data 行忽略 |
| `TestGenerate` | 3 | 端点 + body + headers + 30s timeout / `limit` → `length` / 末尾斜杠裁剪 |
| `TestStepToken` | 3 | PN.py contract body / EOS 折叠 / payload 异常兜底 |
| `TestApplyTemplate` | 2 | 端点 + 透传 / 缺 prompt 字段 fallback `""` |
| `TestGenerateStream` | 2 | 顺序 + final 标志 + stream=True / 端点 |
| `TestSsrfProxyInjection` | 1 | `monkeypatch ssrf_proxy.post` 验证 step_token 走代理 |

`_FakeHttp` shim 实现 `HttpClientProtocol.post`，记录每次调用。比 `monkeypatch httpx` 干净的地方：(1) 不依赖真 ssrf_proxy 的内部 `httpx.Client` 池；(2) 验证的是 backend 调 protocol 的契约，不是 protocol 本身的实现。production 路径用 `TestSsrfProxyInjection` 单独兜底。

#### 验收

```
$ uv run --project . pytest tests/unit_tests/core/workflow/nodes/parallel_ensemble/ \
    tests/unit_tests/core/workflow/nodes/ensemble_aggregator/ -q -o addopts=""
106 passed in 0.37s
```

构成：P1 47 + P2.1.5 34 + P2.2 新增 25 = 106。

```
$ uv run --project . ruff check core/workflow/nodes/parallel_ensemble/ \
    tests/unit_tests/core/workflow/nodes/parallel_ensemble/ configs/feature/__init__.py
All checks passed!
$ uv run --project . ruff format ...   # 全文件格式化通过
```

```
$ uv run --project . python -c "from configs import dify_config; print(dify_config.MODEL_NET_REGISTRY_PATH, dify_config.PARALLEL_ENSEMBLE_MAX_WORKERS)"
api/configs/model_net.yaml 8
```

#### 后续依赖

- **P2.3**：把 P2.1 的 inline smoke 移成正式 pytest，加跨 backend ssrf_proxy 注入 e2e（本任务的 `TestSsrfProxyInjection` 已铺路）。
- **P2.4**：控制台 `/local-models` API 复用 `ModelRegistry.list_aliases()`，不需要碰 backend 实现。
- **P2.6** / **P2.6.5**：runner 调 `backend.step_token` / `backend.generate`，把本任务的 SPI 方法当合约用。
- **P2.9**：`node_factory.py` 加分支注入 `(model_registry, runner_registry, aggregator_registry, backend_registry, ssrf_proxy)`；本任务的 `_FakeHttp` 已锁定 `HttpClientProtocol` 契约，注入只剩物理连线。


---

### P2.3 - P2.3 Landing — 模型注册表 + LlamaCppBackend 正式单测 + BackendInfo 投影

> Source shard: `P2.3_LANDING.md`


日期：2026-04-27

#### 范围

P2.1 / P2.2 把核心实现 + inline smoke 落了下来；P2.3 的本职是
**把临时 smoke 转成正式 pytest 文件**，并顺手收口 P2.4 控制台 API 上游
依赖的 `list_aliases` 投影 shape：

- 新建 `api/tests/unit_tests/core/workflow/nodes/parallel_ensemble/llama_cpp/`
  子目录，含 2 个测试文件、共 12 条用例，覆盖 P2.3 spec 列出的 10 项（其中
  `validate_requirements_default` 拆为 3 条子测试以便定位）
- `ModelRegistry.list_aliases()` 返回类型由 `list[AliasInfo]` 升级为
  `list[BackendInfo]`（SPI §4 已存在的 TypedDict），`AliasInfo = BackendInfo`
  保留为 import-name compat
- 同步更新 `tests/.../test_model_registry.py::test_list_aliases_omits_url`
  的 keys 断言

**不做**：node_factory 注入 e2e（P2.9）、控制台 API（P2.4）、第二个 backend 的
 ssrf 测试（Phase 4 引入 vLLM/OpenAI adapter 时再各自落地）。

#### 测试目录结构

```
api/tests/unit_tests/core/workflow/nodes/parallel_ensemble/llama_cpp/
├── __init__.py
├── test_registry_load.py     # 5 用例：注册表 → LlamaCppSpec dispatch
└── test_backend_ssrf.py      # 7 用例：backend × ssrf_proxy adapter 接缝
```

为什么单开子目录而不是合并进现有 `test_llama_cpp_backend.py` /
`test_model_registry.py`：P2.3 spec L330 明确指定路径
`parallel_ensemble/llama_cpp/`，与 v0.3 后多 backend 并列时
 `parallel_ensemble/openai_compat/` / `parallel_ensemble/vllm/` 形成对称
（每个 backend 的 spec / backend 测试都收在自己的子目录），P2.3 先把
目录骨架定下来。

#### test_registry_load.py 5 条

| 用例 | 内容 |
|---|---|
| `test_registry_load` | 写两条 `backend: llama_cpp` yaml entry，验证 `ModelRegistry.for_testing(path)` 通过 BackendRegistry 反查 `LlamaCppSpec` 加载正确（`isinstance(spec, LlamaCppSpec)` + 字段值） |
| `test_extra_forbid` | yaml entry 含未知字段 `rogue` → `RegistryFileError(reason 包含 "rogue")`（包装 Pydantic `ValidationError`） |
| `test_unknown_backend` | yaml `backend: my_zmq` 但未注册 → `RegistryFileError`，reason 含 `"my_zmq"` + `"is not registered"` + 已注册的 `llama_cpp`（错误信息 actionable） |
| `test_unknown_alias` | `registry.get("nope")` 抛 `UnknownModelAliasError(alias="nope")`（不是裸 KeyError） |
| `test_list_aliases_returns_backend_info` | 返回 `BackendInfo{id, backend, model_name, capabilities, metadata}`；T2 断言 `model_url` / `api_key` / `api_key_env` 都不在；capabilities 含 `token_step`/`top_probs`，不含 `logits_raw`；`metadata.type` 区分 normal/think |

`_entry()` / `_write_yaml()` 两个内部 helper 把"写一个 yaml entry"的样板
压扁成一行；之所以不抽成 conftest fixture，是想让每条用例的 yaml 内容
inline 可见（diff review 时不用跨文件追 fixture 状态）。

#### test_backend_ssrf.py 7 条

##### Capability + Validate（4 条）

| 用例 | 内容 |
|---|---|
| `test_capability_declaration` | `LlamaCppBackend.capabilities(spec)` 等于 `{STREAMING, TOKEN_STEP, TOP_PROBS, POST_SAMPLING_PROBS, CHAT_TEMPLATE}`，`LOGITS_RAW` 不在（trap 1） |
| `test_validate_requirements_default_passes_for_unknown_kind` | 框架走 deny-list 风格——未知 kind 默认 pass（runner 演进先于 backend 适配时不立刻硬 break） |
| `test_validate_requirements_default_min_top_k_unbounded` | `min_top_k=999` pass（llama.cpp 无硬上限，区别于 OpenAI 20 / vLLM 部署侧上限） |
| `test_validate_requirements_default_function_calling_blocks` | `needs_function_calling=True` 拒（capability 不存在）；`False` pass（runner 显式声明不需要 function calling 不应被误伤） |

P2.3 spec 写的"`test_validate_requirements_default`：默认 capability-bottom 兜底
通过 / 不通过路径"被拆成上述 3 条；目的是让一条断言失败时立刻定位到具体 kind。

##### SSRF 注入（3 条）

| 用例 | 内容 |
|---|---|
| `test_step_token_uses_ssrf_proxy` | `monkeypatch ssrf_proxy.ssrf_proxy.post`；验证 url + body `{prompt, max_tokens=1, n_probs=k, post_sampling_probs=True}` + headers + `request_timeout_ms=15000` → `timeout=15.0s` |
| `test_generate_uses_ssrf_proxy` | `/completion` 端点 + body 含 `stream=False` + caller sampling params 透传 + 默认 `request_timeout_ms=30000` → `timeout=30.0s` + 返回结构 `{text, finish_reason, metadata}` |
| `test_apply_template_uses_ssrf_proxy` | `/apply-template` 端点 + messages list 透传 |

#### 测试范围说明（不夸大）

`test_backend_ssrf.py` 是 **adapter-level wiring smoke**，不是真 e2e：

- 测试**直接**构造 `LlamaCppBackend(spec, http=ssrf_module.ssrf_proxy)`，
  然后 monkeypatch `ssrf_proxy.post`；这能证明 backend 拿到 `SSRFProxy`
  实例后确实调它（而不是绕路 `httpx.post`）
- **没**覆盖框架运行时一定注入 proxy 这一更强命题——`node_factory →
  backend constructor` 的注入路径属 P2.9 范围

`_FakeResponse` 在 `test_backend_ssrf.py` 内部重新定义而不是从
`test_llama_cpp_backend.py` 复用：P2.3 brief 是"测试自包含在 llama_cpp/"，
跨目录复用 fixture 会让重命名 / 重构时形成隐式耦合。

#### 实现侧改动：list_aliases → BackendInfo

##### 旧 shape vs 新 shape

```python
# P2.1（旧）
class AliasInfo(TypedDict):
    id: str
    backend: str
    model_name: str
    type: Literal["normal", "think"]   # ← llama_cpp-specific

# P2.3（新，等价 SPI §4 BackendInfo）
class BackendInfo(TypedDict):
    id: str
    backend: str
    model_name: str
    capabilities: list[str]            # ← 新增
    metadata: dict                     # ← 新增；旧 type 下沉到这里
```

##### 为什么改

P2.4 控制台 `/workspaces/current/local-models` API 要返回的就是
`BackendInfo`（TASKS.md L347 指明）；如果 P2.4 阶段才改 shape，前端的
mocked dropdown 数据会先用 `AliasInfo` 形式做了，再返工成本反而更高。
SPI §4 已经把 `BackendInfo` TypedDict 写好备用，P2.3 趁 list_aliases 还没
有外部 caller 时先迁移。

##### 实现要点

```python
def list_aliases(self) -> list[BackendInfo]:
    out: list[BackendInfo] = []
    for spec in self._models.values():
        backend_cls = BackendRegistry.get(spec.backend)
        capabilities = sorted(cap.value for cap in backend_cls.capabilities(spec))
        metadata: dict[str, Any] = {}
        spec_type = getattr(spec, "type", None)
        if spec_type is not None:
            metadata["type"] = spec_type
        out.append(BackendInfo(
            id=spec.id, backend=spec.backend, model_name=spec.model_name,
            capabilities=capabilities, metadata=metadata,
        ))
    return out
```

三处考虑：

1. **capabilities 用 `BackendRegistry.get(spec.backend).capabilities(spec)`**：
   不直接读 `spec.backend` 字符串去查表是因为 SPI §4 允许同一 backend
   类对不同 spec 返回不同 capability 集（OpenAI 那种 `gpt-3.5-turbo-0301`
   不支持 logprobs 的 case），所以必须 spec-aware 派发。
2. **capabilities 转字符串 list 再排序**：前端不需要 `import Capability`
   枚举即可渲染；排序让 dropdown 顺序在 commit 间稳定，方便 review 截图
   diff。
3. **metadata 仅放 `type`**：当前 v0.2 只有 llama.cpp 的 `type` 字段
   是非密钥可外露的扩展。`stop_think` 是 think runner 内部用的（前端
   下拉不展示），故不放 metadata；将来 P2.4 / P2.11 如果 UI 真要展示
   再补，且必须同步加测试。

##### AliasInfo = BackendInfo

```python
# ⚠️ Import-name compatibility ONLY. The runtime shape changed:
# P2.1 was {id, backend, model_name, type};
# P2.3 is {id, backend, model_name, capabilities, metadata}.
# Code that read info["type"] must migrate to info["metadata"].get("type").
AliasInfo = BackendInfo
```

字面"兼容别名"容易让 P2.1-era caller 以为 `info["type"]` 还能用。
注释明示 import-name only 是 review 反馈过的关键修正。

#### 同步更新

`tests/.../test_model_registry.py::test_list_aliases_omits_url` 的 keys 断言：

```python
# before
assert set(info.keys()) == {"id", "backend", "model_name", "type"}
# after
assert set(info.keys()) == {"id", "backend", "model_name", "capabilities", "metadata"}
```

T2 SSRF 防护断言（`model_url` / `url` 不在）保留不动。

#### 验收

```
$ uv run --project . pytest \
    tests/unit_tests/core/workflow/nodes/parallel_ensemble/llama_cpp/ -v -o addopts=""
12 passed in 0.14s

$ uv run --project . pytest \
    tests/unit_tests/core/workflow/nodes/parallel_ensemble/ \
    tests/unit_tests/core/workflow/nodes/ensemble_aggregator/ -q -o addopts=""
118 passed in 0.39s
```

构成：P1 47 + P2.1.5 34 + P2.2 25 + **P2.3 新增 12** = 118。

```
$ uv run --project . ruff check core/workflow/nodes/parallel_ensemble/registry/model_registry.py \
    tests/unit_tests/core/workflow/nodes/parallel_ensemble/
All checks passed!

$ uv run --project . ruff format --check ...   # 8 files already formatted

$ uv run --project . basedpyright core/workflow/nodes/parallel_ensemble/registry/model_registry.py \
    tests/unit_tests/core/workflow/nodes/parallel_ensemble/llama_cpp/ \
    tests/unit_tests/core/workflow/nodes/parallel_ensemble/test_model_registry.py
0 errors, 0 warnings, 0 notes
```

#### Code review 反馈与修正

P2.3 落地后做了一轮 code review，其中三条被修复：

1. **`AliasInfo` 兼容措辞**：原注释"backwards-compat alias for one
   release"会让人以为 runtime shape 也兼容；改为明示 import-name only
   并指出 `info["type"]` 需迁移到 `info["metadata"].get("type")`。
2. **`list_aliases` docstring 与实现不符**：原 docstring 写 `stop_think`
   也会进 metadata，但实现只放 `type`，测试也只断言 `type`；改为只描述
   `type`，避免误导 P2.4 接入者。
3. **SSRF 测试措辞偏满**：原模块 docstring 写"production wiring"暗示
   覆盖框架注入路径；改为"adapter-level wiring smoke"，明示
   node_factory 注入留给 P2.9。

#### 后续依赖

- **P2.4 控制台 API**：`/workspaces/current/local-models` 直接返回
  `ModelRegistry.instance().list_aliases()` 的输出，shape 已对齐 BackendInfo
  零改动接入。
- **P2.9 node_factory 注入**：本任务的 `test_step_token_uses_ssrf_proxy`
  只锁定 adapter 端的 `self._http` 调用契约；P2.9 落地后追加 e2e 测试
  证明工厂确实把 `ssrf_proxy` 传进 `LlamaCppBackend(__init__)`。
- **Phase 4 跨 backend ssrf 测试**：P2.3 当前只覆盖 llama_cpp；vLLM /
  OpenAI adapter 各自落地时，应在 `parallel_ensemble/<backend>/` 子目录
  复制相同的 3 条 SSRF smoke（端点 / body / timeout 换算）。


---

### P2.4 - P2.4 Landing — 控制台 API: models / runners / aggregators 三路由

> Source shard: `P2.4_LANDING.md`


日期：2026-04-27

#### 范围

P2.3 把 `ModelRegistry.list_aliases()` 的返回 shape 升级到 `BackendInfo`
并把 SPI 跑过 12 条 pytest，**P2.4 的本职是把这一层 shape 暴露成
HTTP 接口**，给 P2.11 三轴下拉（model / runner / aggregator）提供
真实的后端数据源。

- 新增 3 个 controller：`local_models.py` / `runners.py` /
  `aggregators.py`，挂在 `controllers/console/workspace/` 下
- `controllers/console/__init__.py` 9 处注册（3 个 import 名 + 3 条
  `__all__` 条目；导入与 `__all__` 各加一行 ↔ 共 6 个改动点，但因为
  3 个 module 各占 import 块 + `__all__` 各一行，总计 9 个 hunk）
- 1 个测试文件 9 条用例：3 类 Resource × 投影契约 / ui_schema 白名单 /
  装饰器链 / blueprint 注册 smoke

**不做**：P2.5/P2.6 的 runner / aggregator 实现（本任务无 runner /
 aggregator 注册时，``/runners`` / ``/aggregators`` 合法返回空列表）；
P2.11 的前端面板（依赖这三路由的客户端 fetch）；运行时的 capability
过滤（前端职责，P2.11）。

#### 三个 controller 的形状

每个 controller 都是单 `Resource` 子类 + 单 `GET`，没有路径参数、没
有请求体、没有 query param。三个 endpoint 在 `console_ns` 下挂的全
路径是：

| Controller | URL | 项目数据来源 |
|---|---|---|
| `LocalModelsApi` | `GET /console/api/workspaces/current/local-models` | `ModelRegistry.instance().list_aliases()` |
| `RunnersApi` | `GET /console/api/workspaces/current/runners` | `RunnerRegistry.known_runners()` |
| `AggregatorsApi` | `GET /console/api/workspaces/current/aggregators` | `AggregatorRegistry.known_aggregators()` |

返回值都包在 `{ "<复数名>": [...] }` 顶层，便于以后追加 metadata 字
段（例如 OQ-2 的 `unknown_keys` 计数）而不破坏外层 contract。

##### LocalModelsApi 投影

直接返回 `list_aliases()`：P2.3 已经把 shape 锁定为 `BackendInfo`
（`{id, backend, model_name, capabilities, metadata}`），这里只是把它
JSON 化。**T2 保护点是 P2.3 的实现层而不是这层** —— controller 不再
做字段过滤，否则一处遗漏（例如未来的 `api_key_env` 字段）就会绕过
filter。让 `list_aliases` 在 model_registry.py 里成为唯一过滤点更
安全。

##### RunnersApi / AggregatorsApi 投影

```python
def _project_runner(runner_cls):
    return {
        "name": runner_cls.name,
        "i18n_key_prefix": runner_cls.i18n_key_prefix,
        "ui_schema": runner_cls.ui_schema,
        "config_schema": runner_cls.config_schema_json(),
        "aggregator_scope": runner_cls.aggregator_scope,
        "required_capabilities": sorted(c.value for c in runner_cls.required_capabilities),
        "optional_capabilities": sorted(c.value for c in runner_cls.optional_capabilities),
    }
```

三处选型：

1. **`config_schema_json()` 显式调用**：SPI 已经提供了这个
   classmethod（dump pydantic JSON schema），调用时机选 controller
   层而不是 SPI 类属性，是因为 schema 体积较大（`max_len: int = 64`
   会展开成 ~100 字符 JSON），放进 `ClassVar` 反而不利于热更新。
2. **capabilities 转 `str` 再排序**：与 P2.3 `list_aliases` 同样的
   理由 —— 前端不应该 import `Capability` 枚举即可渲染；排序让
   review screenshot 在 commit 间稳定。
3. **`scope`（aggregator）/ `aggregator_scope`（runner）字段命名不
   对称**：保留 SPI 命名差异，因为 SPI 自己就是这样命名的（aggregator
   有 `scope`，runner 有 `aggregator_scope`）；前端做配对时按字符串
   等值匹配，命名不对称不构成阻碍。

##### 鉴权装饰器栈

三个 controller 都用了同样的装饰器链：

```python
@setup_required
@login_required
@account_initialization_required
def get(self):
    ...
```

参考 `agent_providers.py` 的同目录形状。这一层不做 plugin permission
（这三个 endpoint 的内容不依赖 tenant plugin install / debug 权限），
也不做 enterprise license（基础功能）。

#### 测试目录结构

```
api/tests/unit_tests/controllers/console/workspace/
├── ... (existing)
└── test_local_models_api.py   # 9 用例：3 routes × 投影契约 + smoke
```

为什么三 route 合并到一个测试文件而不是分三个：3 个 endpoint 的
shape 同型（一个 GET、零参数、纯投影），分文件会让 import 块和
fixture 各重复一遍；review 一次看完所有投影契约也更省事。同名子文件
命名策略：`test_local_models_api.py`（沿用 `local_models.py` 主名 +
`_api` 后缀，参考 `test_workspace_account.py` 的 `test_<module>.py`
惯例）。

#### 9 条用例

##### LocalModelsApi (2 条)

| 用例 | 内容 |
|---|---|
| `test_returns_models_without_url_or_api_key` | 注入两条 `LlamaCppSpec`（normal + think），断言 `models` 长度 = 2、ID 集合正确、**每条 entry keys 仅限 5 字段**（`id, backend, model_name, capabilities, metadata`），显式检查 `model_url / url / api_key / api_key_env / endpoint` 都不在 keys 中（T2 SSRF 边界）；llama.cpp 的 `type=think/normal` 落到 `metadata.type`（P2.3 契约） |
| `test_returns_empty_list_when_registry_empty` | 注入空 `ModelRegistry()`，返回 `{"models": []}`；这条护住 yaml 不存在 / 用户没配模型时 controller 不爆 500 |

##### RunnersApi (3 条)

| 用例 | 内容 |
|---|---|
| `test_returns_runner_descriptor` | 注册 `_FakeRunner`，断言 7 字段全在（`name / i18n_key_prefix / ui_schema / config_schema / aggregator_scope / required_capabilities / optional_capabilities`），capability 字段返回字符串 list 而非 enum |
| `test_ui_schema_controls_within_v02_allowlist` | 遍历所有 runner 的 `ui_schema`，断言每个 field 的 `control` 都 ∈ `UI_CONTROL_ALLOWLIST`（v0.2 冻结的 7 控件）—— **P2.4 spec 直接列出的接收门** |
| `test_config_schema_is_pydantic_json_schema` | 断言 `config_schema` 是 pydantic v2 形状（`type=object / properties: {max_len, enable_think}`），证明 `config_schema_json()` 没被错误覆写成空 dict |

##### AggregatorsApi (2 条)

| 用例 | 内容 |
|---|---|
| `test_returns_aggregator_descriptor` | 注册 `_FakeAggregator`（`scope="response"`），断言 5 字段全在（`name / i18n_key_prefix / ui_schema / config_schema / scope`）；scope 是 P2.11 前端用来过滤 dropdown 的关键字段 |
| `test_ui_schema_controls_within_v02_allowlist` | 同 runner 那条，遍历所有 aggregator 的 ui_schema |

##### 元测试 (2 条)

| 用例 | 内容 |
|---|---|
| `test_decorators_chain_intact` | 数 `Resource.get` 的 `__wrapped__` 深度 ≥ 3，护住 setup/login/account 三层装饰器，避免未来一次去掉 `functools.wraps` 把 unwrap-based 测试静默旁路 |
| `test_resources_registered_in_console_blueprint` | `from controllers.console import local_models, runners, aggregators` 必须能成功 —— 加新 controller 而忘了在 `__init__.py` 注册时这条会先于 `pytest collect` 失败 |

#### Fixture 设计

##### `_ensure_llama_cpp_backend_registered`（autouse）

`test_spi_freeze.py` / `test_llama_cpp_backend.py` 之间会调
`BackendRegistry.reset_for_testing()`，pytest 文件间的执行顺序无保
证。当本测试在那两个之后跑，`LlamaCppBackend` 注册被清空，
`list_aliases()` 就在 `BackendRegistry.get(spec.backend)` 处抛
`UnknownBackendError`。

最干净的修是在测试开头 sniff `_backends`，**仅在缺失时补注册并在
teardown 弹回去**：

```python
pre_existing = "llama_cpp" in BackendRegistry._backends
if not pre_existing:
    BackendRegistry.register("llama_cpp", LlamaCppBackend)
try:
    yield
finally:
    if not pre_existing:
        BackendRegistry._backends.pop("llama_cpp", None)
```

不无脑 always-register 是因为：本测试在 P2.9 之后会和真正的 import
时序协同，那时 LlamaCppBackend 已经注册好；always-register 会触发
`DuplicateRegistrationError`。

不直接 `reset + register` 是因为：那会破坏其它注册（vLLM /
OpenAI adapter 在 P4 加进来后），让本测试从隔离改成 invasive。

##### `registered_fake_runner` / `registered_fake_aggregator`

不让真实 P2.6 的 runner（还没落地）来填测试 ── 即使 P2.6 落地了，
直接依赖 P2.6 的 runner 名会让本测试在 P2.6 改名时一起断；测试只
应该锁 controller 投影契约，不应该锁实现存在性。所以注一个
`_FakeRunner`（`required_capabilities = {STREAMING}`，
`ui_schema = {"max_len": number_input, "enable_think": switch}`）专
门给 controller 测试用，teardown 时 `RunnerRegistry._runners.pop`
弹掉。

##### 不用 mock 整个 RunnerRegistry

可以，但每条用例都要写 `with patch.object(RunnerRegistry, ...)`，
而这里我们要测的是 *真实的注册→列表→投影* 链路。注一个真 runner
覆盖范围更大。

#### 实现侧要点

##### 路由注册的 9 处

`controllers/console/__init__.py` 是 console blueprint 的 entry
point；workspace 子模块通过 import 触发 `@console_ns.route(...)`
装饰器副作用。所以新增一个 module 必须：

1. 在 `from .workspace import (...)` 块按字母序加 1 行
2. 在 `__all__` 块按字母序加 1 行

P2.4 加 3 个 module，因此 6 个文本改动点；之所以叫"9 处"是因为
spec 原文 `parallel_ensemble/node_factory:300, 383` 类比模式说的是
"加新节点 9 处注册"，本任务沿用计数口径 ——
`controllers/console/__init__.py` 共 6 处 + 3 个 `route(...)`
装饰器调用 = 9 处可见的注册痕迹。

##### 不内联 `setup_required` 之外的额外鉴权

考虑过加 `plugin_permission_required` —— 不加，因为这三个 endpoint
不涉及 plugin 安装 / debug 权限，加上反而误导。enterprise license
也不加（基础功能，社区版必须可用）。

##### `_project_*` 的位置

放在 controller 模块文件级而不是 SPI / registry 模块。理由：投影
shape 是 *console API contract*，跟运行时 SPI 不同 ——
runtime 的 `runner_cls` 直接被 `RunnerRegistry.get` 拿走，不走
JSON。把投影放进 SPI 会让 SPI 耦合 HTTP 字段命名（比如未来如果
console 想加 `display_name` 字段，SPI 会无辜抖动）。投影留给
controller，SPI 保持纯净。

#### 验收

```
$ uv run --project . pytest \
    tests/unit_tests/controllers/console/workspace/test_local_models_api.py \
    -v -o addopts=""
9 passed in 1.49s

$ uv run --project . pytest \
    tests/unit_tests/core/workflow/nodes/parallel_ensemble/ \
    tests/unit_tests/core/workflow/nodes/ensemble_aggregator/ \
    tests/unit_tests/controllers/console/workspace/test_local_models_api.py \
    -q -o addopts=""
127 passed in 1.25s
```

构成：P1 47 + P2.1.5 34 + P2.2 25 + P2.3 12 + **P2.4 新增 9** = 127。

```
$ uv run --project . ruff check controllers/console/workspace/local_models.py \
    controllers/console/workspace/runners.py \
    controllers/console/workspace/aggregators.py \
    controllers/console/__init__.py \
    tests/unit_tests/controllers/console/workspace/test_local_models_api.py
All checks passed!

$ uv run --project . ruff format --check ...
5 files already formatted

$ uv run --project . basedpyright controllers/console/workspace/local_models.py \
    controllers/console/workspace/runners.py \
    controllers/console/workspace/aggregators.py \
    tests/unit_tests/controllers/console/workspace/test_local_models_api.py
0 errors, 0 warnings, 0 notes
```

#### 后续依赖

- **P2.5 / P2.6 / P2.6.5**：runner + aggregator 实现落地后会自动出现在
  这两个 endpoint 的返回中（无需 controller 改动）。届时本任务的
  `test_returns_runner_descriptor` 可以改为断言真名（`token_step` /
  `response_level` / `majority_vote` / `concat` / `sum_score` /
  `max_score`），把 `_FakeRunner` 退化为兜底；建议保留 fake runner
  以隔离实现层飘动。
- **P2.11 前端**：fetch 这三 endpoint，按 `aggregator.scope ==
  runner.aggregator_scope` 过滤 aggregator dropdown，按
  `runner.required_capabilities ⊆ backend.capabilities` 过滤 model
  dropdown。本任务把这两条过滤所需要的字段都暴露出来了。
- **P2.9 node_factory**：P2.4 不消费 BackendRegistry 的运行时实例，
  仅查类型；P2.9 把工厂注入打通后，本测试的
  `_ensure_llama_cpp_backend_registered` 兜底逻辑可以视
  test ordering 决定保留与否。

#### Code review 自查项

1. **T2 SSRF 边界**：`list_aliases` 是唯一过滤点，controller 不
   重复过滤；test 显式断言 5 个候选敏感字段（`model_url / url /
   api_key / api_key_env / endpoint`）都不在 keys 中
2. **空数据路径**：空 ModelRegistry / 未注册 runner / 未注册
   aggregator 都返回 200 + 空 list（`{"models": []} / {"runners":
   []} / {"aggregators": []}`），不抛 5xx
3. **隔离性**：本测试不污染全局 registry —— 每条 fixture 用
   sniff-then-restore；`autouse` 的 backend 兜底也是
   sniff-then-restore
4. **decorator chain 完整性**：`test_decorators_chain_intact` 防止
   一次 `wraps` 丢失把 unwrap-based 测试变成"测试装饰器外的空函数"
5. **blueprint 注册可见性**：`test_resources_registered_in_console_blueprint`
   防止只加文件不加 import 时的"看起来 PR 完整、生产 404"陷阱


---

### P2.5 - P2.5 Landing — 后端 aggregators：response + token 双 scope

> Source shard: `P2.5_LANDING.md`


日期：2026-04-27

#### 范围

P2.1.5 已经把三轴 SPI（backend / runner / aggregator）冻结，P2.4 把
`AggregatorRegistry.known_aggregators()` 暴露给前端 dropdown；**P2.5
的本职是把 4 个内置 aggregator 落到 SPI 上**，让 P2.4 的 `/aggregators`
endpoint 真正返回内容、让 P2.6 / P2.6.5 的两个 runner 能在测试期就
拿到合法的 `Aggregator` 实例。

- 新增 `parallel_ensemble/aggregators/` 包，`response/` 与 `token/`
  双子包
- `response/`：平滑迁移 P1 `ensemble_aggregator` 的两个 strategy ——
  `majority_vote` / `concat`，行为 + metadata 1:1 对齐 P1 实现
- `token/`：PN.py 主循环的两种 token-level 聚合 —— `sum_score`
  （等价 `calculate_scores`）+ `max_score`（取最大单分）
- `parallel_ensemble/__init__.py` 加 1 行副作用 import，让 4 个
  aggregator 在节点包导入期就进 `AggregatorRegistry`
- 1 个测试目录 4 个测试文件 + `conftest.py`，29 条用例

**不做**：P2.6 / P2.6.5 的 runner（落地后会消费这 4 个 aggregator）；
P2.7 已经在 P2.5 同步落地的 aggregator 子集（runner 部分留 P2.6 /
P2.7）；前端三轴下拉（P2.11，仅消费 controller 投影）。

#### 包结构

```
api/core/workflow/nodes/parallel_ensemble/aggregators/
├── __init__.py                 # 副作用导入 response/ + token/
├── response/
│   ├── __init__.py
│   ├── majority_vote.py        # ResponseAggregator[MajorityVoteConfig]
│   └── concat.py               # ResponseAggregator[ConcatConfig]
└── token/
    ├── __init__.py
    ├── sum_score.py            # TokenAggregator[SumScoreConfig]
    └── max_score.py            # TokenAggregator[MaxScoreConfig]
```

每个 aggregator 单文件 + 单 config 类，和 P1 的"strategy + 同文件 config"
风格一致；不用 `strategies/registry.py` 那种 P1 内部 mini-registry，
因为 SPI 已经提供 `AggregatorRegistry`，再叠一层只会重复职责。

#### 4 个 aggregator 的契约

##### response / majority_vote

| 字段 | 值 |
|---|---|
| `name` | `majority_vote` |
| `scope` | `response` |
| `config_class` | `MajorityVoteConfig`（无字段，`extra="forbid"`） |
| `i18n_key_prefix` | `parallelEnsemble.aggregators.majorityVote` |
| `ui_schema` | `{}` |

行为对 P1 严格对齐：

- 多数票即赢，平票时按 *最早投出该票的 source_id* 字典序最小做 tie-break，
  保证翻转输入顺序得到同一答案。
- `error != None` 的 backend **不参与计票**（P1 在节点层先 filter；
  P2.5 在 aggregator 层 filter，使 aggregator 跑测试不需要先过节点）。
- `metadata` 5 个字段（`strategy / votes / winner_votes /
  tie_break_applied / contributions`）逐字段保 1:1，下游节点引用
  P1 metadata 不需要改 selector。
- 全员 errored 的兜底：返回 `text=""` + `winner_votes=0` 的合法
  `ResponseAggregationResult`，不抛 `ValueError`。

##### response / concat

| 字段 | 值 |
|---|---|
| `name` | `concat` |
| `scope` | `response` |
| `config_class` | `ConcatConfig`（`separator`, `include_source_label`） |
| `ui_schema` | `{separator: text_input, include_source_label: switch}` |

`ui_schema` 控件全部落在 `UI_CONTROL_ALLOWLIST` 内（P2.11 渲染门），
默认 separator `"\n\n---\n\n"` 与 P1 完全一致。

##### token / sum_score（等价 PN.py `calculate_scores`）

| 字段 | 值 |
|---|---|
| `name` | `sum_score` |
| `scope` | `token` |
| `config_class` | `SumScoreConfig`（`skip_empty_voters`, `use_weights`） |
| `ui_schema` | `{skip_empty_voters: switch, use_weights: switch}` |

算法：

```
for alias, candidates in per_model.items():
    w = ctx.weights.get(alias, 1.0) if config.use_weights else 1.0
    for cand in candidates:
        token_score[cand.token] += cand.prob * w
winner = min(t for t, s in token_score.items() if s == max_score)
```

三个**对 PN.py 的故意偏离**：

1. **不用 `random.choice` 做 tie-break**：PN.py 在并列时 `random.choice`，
   导致同一 prompt + 同一 seed 跑两次结果不一致（破坏 reproducibility）。
   P2.5 改为字典序最小，单测 `test_deterministic_tie_break` 跑 5 次断
   言全部相同。
2. **加权可选**：PN.py 等权和；这里把 `BackendInfo.weight`
   通过 `AggregationContext.weights` 喂进来，研究侧需要不等权时
   `use_weights=True` 一开关搞定，默认 True 保持模型 spec 上 weight
   字段的语义有效。
3. **空票路径走结构化 reasoning**：PN.py 没区分"全员超时"和"全员一致投空"；
   这里返回 `{"token": "", "all_voters_empty": True, "empty_voters": [...]}`，
   让 runner 自己决定是 fallback 上一步、还是直接终止。Aggregator 不
   做 cross-step state（aggregator 本来就只看一个 step）。

`skip_empty_voters` 的 *aggregator-side* 语义：

- `True`（默认）—— 错误 backend 的 alias 不进 `reasoning` 字段，
  trace 体积小；
- `False` —— `empty_voters: list[alias]` 进 `reasoning`，runner 可以
  读到这个 key 后决定是否走"用上步 fallback"。**fallback 本身是 runner
  职责**，aggregator 没有 step-level state，硬塞会破坏 SPI 单步纯函数
  契约。

##### token / max_score

| 字段 | 值 |
|---|---|
| `name` | `max_score` |
| `scope` | `token` |
| `config_class` | `MaxScoreConfig`（同 sum_score 两字段） |

算法：每个 token 取**单一 backend 的最大加权 prob**，token 之间再取
最大；token 内部 alias tie-break 同样字典序最小（保证 `winner_alias`
确定性）。

适用场景：研究侧需要"loudest dissenter wins"——只有一个模型非常
确信时它的票压过另一组中等确信票的总和。和 sum_score 是互补关系。

#### 注册路径

```python
# parallel_ensemble/__init__.py
from . import aggregators as aggregators
from . import backends as backends
```

副作用导入序：`backends` 之后导入 `aggregators` 不重要（互相不依赖）。
4 个 `@register_aggregator` 装饰器在
`aggregators/{response,token}/__init__.py` 的子模块 import 链路上跑过，
之后 `AggregatorRegistry.known_aggregators()` 立刻返回
`["concat", "majority_vote", "max_score", "sum_score"]`。

`@register_aggregator(name, scope=...)` 装饰器自带 *scope 一致性断言*：
装饰器声明的 scope 与类 ClassVar `scope` 不一致时直接抛 `ValueError`，
所以 `ResponseAggregator` 子类粘错 `scope="token"` 在 import 期就爆。

#### 测试目录

```
api/tests/unit_tests/core/workflow/nodes/parallel_ensemble/aggregators/
├── __init__.py
├── conftest.py                       # make_ctx + cand fixtures
├── test_response_majority_vote.py    # 6
├── test_response_concat.py           # 6
├── test_token_sum_score.py           # 9
└── test_token_max_score.py           # 8
```

##### `conftest.py` —— `make_ctx` 工厂

`AggregationContext` 字段密集（backends / weights / capabilities /
runner_name / runner_config / trace / elapsed_ms_so_far / step_index），
每条用例直接构 `AggregationContext(...)` 会让真正测的代码淹没在
boilerplate 里。`make_ctx` 工厂只暴露**测试关心的 3 个字段**
（`weights`, `runner_name`, `step_index`），其余兜底为合理默认。

`TraceCollector(DiagnosticsConfig())` 用默认 diagnostics 注入 trace
handle —— 不放空对象，是因为 SPI 显式声明 `trace: TraceCollector`
（`arbitrary_types_allowed=True` 但仍需要真实类型），用 `None` 会让
pydantic 校验失败。

##### `cand` —— TokenCandidate 工厂

P2.5 测试只关心 `(token, prob)` 二元组，但 SPI 层 `TokenCandidate` 是
`{token, prob, logit}`（logit 可选）。`cand("hi", 0.5)` 比每条用例
内联 `{"token": "hi", "prob": 0.5, "logit": None}` 简洁约 60%。

##### 29 条用例

###### test_response_majority_vote.py (6)

| 用例 | 内容 |
|---|---|
| `test_registered_under_response_scope` | 装饰器副作用：`AggregatorRegistry.get("majority_vote")` 拿到本类，`scope == "response"`，`name == "majority_vote"` |
| `test_three_way_majority` | P1 canonical：`['A','A','B'] → 'A'`，metadata 5 字段全对 |
| `test_lex_tie_break_independent_of_input_order` | 翻转输入顺序结果一致（确定性 acceptance） |
| `test_errored_backend_does_not_vote` | `error="timeout"` 的 source_id 不进 `votes` / `contributions` |
| `test_all_errored_returns_empty` | 全员 errored → `text=""` + `winner_votes=0`，不抛 |
| `test_config_rejects_extra_fields` | `extra="forbid"` 拒 yaml typo |

###### test_response_concat.py (6)

| 用例 | 内容 |
|---|---|
| `test_registered_under_response_scope` | scope 注册路径 |
| `test_default_separator` | 默认 `"\n\n---\n\n"` 与 P1 对齐 |
| `test_custom_separator` | 自定义 `" | "` |
| `test_source_label` | `include_source_label=True` 形成 `[id]\ntext` |
| `test_errored_skipped` | errored backend 既不进 `text` 也不进 `contributions` |
| `test_config_rejects_extra_fields` | `extra="forbid"` |

###### test_token_sum_score.py (9)

| 用例 | 内容 |
|---|---|
| `test_registered_under_token_scope` | scope=`"token"` |
| `test_pn_calculate_scores_equivalence` | 对 PN.py：`m1=[hello:0.6, world:0.4] + m2=[hello:0.5, world:0.5]` → `hello (1.1)` |
| `test_deterministic_tie_break` | 完全平局 `(zebra:1.0 vs apple:1.0)` 跑 5 次都得 `apple` |
| `test_weighted_sum` | weight `m2=3.0` 让 `world` 反超 `hello` |
| `test_skip_empty_voters_default_silent` | 默认 `True`：`reasoning` 不含 `empty_voters` 键 |
| `test_skip_empty_voters_false_records_errors` | `False`：`reasoning.empty_voters == ["m2", "m3"]` |
| `test_all_voters_empty` | 全员 errored → `token=""` + `all_voters_empty=True` |
| `test_use_weights_false_ignores_ctx_weights` | 即使 `weights={m1: 1000}`，`use_weights=False` 时不应用 |
| `test_config_rejects_extra_fields` | `extra="forbid"` |

###### test_token_max_score.py (8)

| 用例 | 内容 |
|---|---|
| `test_registered_under_token_scope` | scope=`"token"` |
| `test_max_single_score_wins` | `foo` 求和更大但单分小，`bar` 单分 0.85 一击致命 → `bar` 胜 |
| `test_lex_tie_break_on_token` | `(zebra:0.9, apple:0.9)` → `apple` |
| `test_lex_tie_break_on_alias_within_token` | 同 token 不同 alias 平分 → `winner_alias=alpha` |
| `test_weighted` | weight 让 `bar` 反超 |
| `test_all_voters_empty` | 全员空票兜底 |
| `test_skip_empty_voters_false_surfaces_errors` | reasoning 暴露 `empty_voters` |
| `test_config_rejects_extra_fields` | `extra="forbid"` |

#### 实现侧要点

##### 为什么 `scope` ClassVar 和装饰器都传一遍

`@register_aggregator("majority_vote", scope="response")` 看起来重复
（`ResponseAggregator` 类本身已经把 `scope = "response"` 钉在 ClassVar
上），但装饰器要求显式传 scope 是有意为之 —— P2.1.5 SPI freeze 的
注释里就写了：

> "asserts the class declares the same scope it is registered under so
> the decorator and the class can't drift"

考虑过的反例：作者复制 `MajorityVoteAggregator` 改成
`MyTokenMajorityAggregator`、忘改基类（仍 `ResponseAggregator`）但
装饰器写 `scope="token"` —— SPI 的 scope 一致性断言会在 import 期
直接抛错，避免运行时才发现"声明 token 但拿到的是 response signal"
的 type confusion。

##### errored backend 在 aggregator 层 filter，而不是节点层

P1 ensemble_aggregator 的 strategy 假设 inputs 已经被 node 过滤过
（不接受 `error` 字段）。P2.5 的 `ResponseSignal` 显式带 `error: str | None`，
filter 移到 aggregator 内部，理由：

1. P2.6.5 ResponseLevelRunner 不会重做 P1 节点那种 filter；让 aggregator
   自己 filter 减少 runner 模板代码；
2. 单测能直接喂带 `error` 的 signal，不需要先过 node fixture；
3. 与 P1 行为兼容（节点已经 filter 过的话，aggregator 这层 filter 是
   no-op，无副作用）。

##### `AggregationContext.weights` 来源

token aggregator 用 `ctx.weights` 而不是 `signals.per_model_*` 里
某字段的理由：weights 是 *backend 配置层属性*（`BaseSpec.weight`），
不是单步信号；放进 ctx 让一次 aggregator 实例覆盖整段对话过程。
P2.6 TokenStepRunner 在调 `aggregator.aggregate(...)` 前会把
`{alias: spec.weight}` 投影成 `ctx.weights`。本任务不依赖 P2.6
落地（fixture 直接构 ctx），但接口形状已经按 P2.6 的消费方式定。

##### 不为 `MajorityVoteConfig` / `MaxScoreConfig` 单独建文件

config 类紧贴 aggregator 类（同文件、上下相邻）—— 调研 P1
`majority_vote.py` 也是同模式（`_MajorityVoteConfig` 私有内联）。
P2.5 的 config 类公开（去掉 `_` 前缀），因为 P2.4 controller 投影
要 `config_class.model_json_schema()` 给前端。

#### 验收

```
$ uv run --project . pytest \
    tests/unit_tests/core/workflow/nodes/parallel_ensemble/aggregators/ \
    -q -o addopts=""
29 passed in 0.23s

$ uv run --project . pytest \
    tests/unit_tests/core/workflow/nodes/parallel_ensemble/ \
    tests/unit_tests/core/workflow/nodes/ensemble_aggregator/ \
    -q -o addopts=""
147 passed in 0.75s
```

构成：parallel_ensemble 既有 71 + **P2.5 新增 29** = 100，加 P1
ensemble_aggregator 47 = 147；P1 47 条全程未受影响（迁移到 SPI 的是
副本而非替换）。

```
$ uv run --project . ruff check core/workflow/nodes/parallel_ensemble/aggregators/ \
    tests/unit_tests/core/workflow/nodes/parallel_ensemble/aggregators/
All checks passed!

$ uv run --project . ruff format --check core/workflow/nodes/parallel_ensemble/ \
    tests/unit_tests/core/workflow/nodes/parallel_ensemble/
39 files already formatted

$ uv run --project . basedpyright core/workflow/nodes/parallel_ensemble/aggregators/ \
    tests/unit_tests/core/workflow/nodes/parallel_ensemble/aggregators/
0 errors, 0 warnings, 0 notes
```

#### 后续依赖

- **P2.6 TokenStepRunner**：消费 `sum_score` / `max_score`，
  `aggregator_scope = "token"` 与本任务的两个 token aggregator 配对；
  runner 在循环内构 `AggregationContext(weights={alias: spec.weight}, ...)`
  并传给 `aggregator.aggregate(signals, ctx, config)`。
- **P2.6.5 ResponseLevelRunner**：消费 `majority_vote` / `concat`，
  `aggregator_scope = "response"`；signal 形状即本任务的 `ResponseSignal`。
- **P2.4 `/aggregators` endpoint**：本任务落地后这 endpoint 立即返回 4
  条，前端 P2.11 dropdown 不再为空；P2.4 的 `test_returns_aggregator_descriptor`
  此时可以从 `_FakeAggregator` 改断真名（保留 fake 兜底测注册路径
  即可）。
- **P2.10 ParallelEnsembleNode 单测**：本任务的 aggregator 实例可以
  直接喂进 mock 节点测 yield 序列，不需要再 mock aggregator。

#### Code review 自查项

1. **scope 一致性**：4 个 aggregator 的 ClassVar `scope` 与装饰器
   `scope=` 参数一一对齐，import 期断言生效（`@register_aggregator`
   的 ValueError 路径）。
2. **P1 行为兼容**：majority_vote / concat 的 metadata 5 字段
   名 + 默认 separator + tie-break 规则与 P1 strategy 严格对齐 ——
   P1 47 条回归测试零修改通过。
3. **确定性**：sum_score / max_score 故意偏离 PN.py 的
   `random.choice`，改字典序最小；`test_deterministic_tie_break` 跑
   5 次断言全等。
4. **空票兜底**：4 个 aggregator 全部覆盖"全员错误"路径，返回
   合法 result（text=""/token=""）而不是抛 KeyError。
5. **`extra="forbid"` 全覆盖**：4 个 config 类都有专门用例验证 yaml
   typo / DSL 走私字段被拒。
6. **fixture 隔离**：`make_ctx` / `cand` 工厂在 conftest，aggregator
   测试不动 `AggregatorRegistry._aggregators`（类级注册一次到底，与
   P2.4 fake-runner-pop teardown 模式不冲突）。


---

### P2.6 - P2.6 Landing — `TokenStepRunner` + `ThinkPhaseRunner`

> Source shard: `P2.6_LANDING.md`


日期：2026-04-27

#### 范围

P2.5 已经把 4 个内置 aggregator 落到 SPI 上；**P2.6 的本职是把
PN.py 的主循环以 `EnsembleRunner` SPI 形式落到一个新的 `runners/`
子包里**，让 P2.4 的 `/runners` endpoint 真正返回内容、让 P2.8 的
`ParallelEnsembleNode._run` 可以直接 `runner_registry.get("token_step")`
拿到一个能跑的 runner 类。

- 新增 `parallel_ensemble/runners/` 包（`token_step.py` +
  `think_phase.py`），副作用 import 到 `parallel_ensemble/__init__.py`
- `TokenStepRunner` 等价 PN.py `MultiModelHandler.generate_response`
  主循环：每步 ThreadPoolExecutor 并发 `step_token` →
  `aggregator.aggregate(TokenSignals, ctx, agg_config)` → 同步追加
  pick.token → `yield TokenEvent` → 终止后 `yield DoneEvent`
- `ThinkPhaseRunner` 等价 PN.py `process_think_task`：扫描
  `type=think` 模型，并发跑 `backend.generate(stop=[stop_think],
  max_tokens=8196)`，返回 `dict[alias, suffix]` 让 token loop 把
  CoT 段拼到对应模型的 prompt 上
- 1 个测试目录 2 个测试文件 + `conftest.py`，16 条用例

**不做**：P2.6.5 的 `ResponseLevelRunner`（同样消费 `aggregators/response/`，
留下个 import 槽位但代码先空着）；KV-cache 复用（EXTENSIBILITY_SPEC §1.2
非目标，`KV_CACHE_REUSE` 容量位保留给将来的 fork）；P2.8 的
`ParallelEnsembleNode._run`（这里只把 runner SPI 跑通，节点装配是
P2.8 / P2.9 的事）。

#### 包结构

```
api/core/workflow/nodes/parallel_ensemble/runners/
├── __init__.py             # 副作用导入 token_step（P2.6.5 加 response_level）
├── think_phase.py          # ThinkPhaseRunner — type=think 前置思考段
└── token_step.py           # TokenStepRunner — PN.py 主循环
```

跟 `aggregators/` 不一样，runner 不分子包：runner 数量本来就不多
（v0.2 `token_step` + `response_level`，第三方 runner 走自己的 plugin
包）；强行二级目录（`runners/streaming/` / `runners/judge/`）只会让
4 个文件被分散到 5 个目录，反而降低可发现性。

#### `TokenStepRunner` 契约

| 字段 | 值 |
|---|---|
| `name` | `token_step`（装饰器赋值） |
| `aggregator_scope` | `token`（与 `sum_score` / `max_score` 配对） |
| `required_capabilities` | `{TOKEN_STEP, TOP_PROBS}` |
| `optional_capabilities` | `{CHAT_TEMPLATE}` |
| `config_class` | `TokenStepConfig`（`top_k`, `max_len`, `enable_think`） |
| `i18n_key_prefix` | `parallelEnsemble.runners.tokenStep` |

`ui_schema` 三个控件全部落在 `UI_CONTROL_ALLOWLIST` 内：

```python
{
  "top_k":        {"control": "number_input", "min": 1, "max": 20, "step": 1},
  "max_len":      {"control": "number_input", "min": 1, "step": 1},
  "enable_think": {"control": "switch"},
}
```

`top_k` 上限 20 是为了对齐 OpenAI/OpenAI-compat 的 `top_logprobs` 上限
（llama.cpp 没硬限），P2.4 的 `/local-models` capability 反过来也用
这个上限做 dropdown 灰化。

##### `requirements(config)`

派生两条：

```python
[
  {"kind": "min_top_k",      "value": config.top_k, "rationale": ...},
  {"kind": "needs_logprobs", "value": True,         "rationale": ...},
]
```

`min_top_k` 让 §9 capability filter 拒掉 `top_k` 上限不够的 backend；
`needs_logprobs` 在 capability 过滤已经把没有 `TOP_PROBS` 的 backend
摘掉之后是冗余的，但留着是为了 tooltip：前端可以告诉用户"为什么这
个 backend 灰掉" → "因为它不暴露概率值"。

##### `validate_selection(config, model_aliases, registry)`

两类规则：

- ≥ 2 模型（`severity="error"`）：单模型不构成"集成"，跟 PN.py
  一模一样
- `enable_think` / `type=think` 一致性（两条 `severity="warning"`）：
  - `enable_think=True` 但选中的模型里没 `type=think`：think 阶段会是
    no-op，前端给 warning（不阻塞，因为有研究价值的边界场景）
  - `enable_think=False` 但选中了 `type=think` 模型：模型的 CoT 段
    会被当成普通 token 投票，结果通常没意义；前端给 warning

`registry.get(alias)` 拿到的 spec 可能没 `type` 字段（第三方 backend
不一定有），用 `getattr(..., "type", None)` 防御性读，与 P1 兼容
对齐。

##### `run(question, backends, aggregator, config, trace)` 主循环

PN.py `generate_response` 的 SPI 翻译：

```python
prompts = self._template_prompts(question, backends)   # 调每个 backend.apply_template

if config.enable_think:
    suffixes = ThinkPhaseRunner(self._executor).run(prompts, backends, trace)
    for alias, suffix in suffixes.items():
        if suffix: prompts[alias] += suffix

while step < config.max_len:
    per_model, per_model_errors = self._step_concurrent(backends, prompts, config.top_k)
    pick = aggregator.aggregate(
        TokenSignals(per_model=per_model, per_model_errors=per_model_errors),
        AggregationContext(weights=..., capabilities=..., trace=trace, step_index=step, ...),
        self._aggregator_config,                         # ← 见下文 §"为什么 aggregator_config 在 __init__"
    )
    trace.record_token_step({...})                       # 由 collector 按 cfg gate
    token = pick["token"]
    if token == "<end>": stopped_by = "eos";              break
    if token == "":      stopped_by = "all_voters_empty"; break
    for alias in prompts: prompts[alias] += token
    accumulated += token
    yield TokenEvent(kind="token", delta=token)
    step += 1

trace.record_summary("stopped_by", stopped_by)
trace.record_summary("tokens_count", step)
trace.record_summary("total_elapsed_ms", total_elapsed_ms)
yield DoneEvent(kind="done", text=accumulated, metadata={stopped_by, tokens_count, elapsed_ms})
```

##### 三个对 PN.py 的故意偏离

1. **Aggregator 是可插拔的** —— PN.py 把 `calculate_scores` 内联在
   handler 里；这里 aggregator 是 SPI-pluggable 的 `TokenAggregator`，
   `sum_score` / `max_score` 默认两种，第三方扩展可以注册新的
   token-scope aggregator 而不动 runner 代码。
2. **Concurrency 走 caller-supplied executor** —— PN.py 在 handler
   里自建 `ThreadPoolExecutor(max_workers=10)`；这里由节点共享一个
   `ThreadPoolExecutor` 传进来。一个工作流里多个 parallel-ensemble
   节点共用一个池，避免线程数爆炸；`PARALLEL_ENSEMBLE_MAX_WORKERS`
   config 留给 P2.9 的节点工厂。
3. **Aggregator config 在 `__init__` 绑定** —— SPI 的
   `EnsembleRunner.run(...)` 签名已冻结，没有 `aggregator_config`
   参数；但 `TokenAggregator.aggregate(signals, ctx, config)` 必须
   带 config。**唯一同时拿到 runner 配置和 aggregator 配置的层是
   节点**，所以节点（P2.8）在 `TokenStepRunner(executor=..., aggregator_config=...)`
   时把已 validate 过的 aggregator config 一起传进来。Runner 在
   `run()` 内部用 `self._aggregator_config` 调 `aggregator.aggregate`。
   这样 SPI run() 签名零修改，单元测试也能直接构造。

##### 终止状态机

| token | `stopped_by` | 备注 |
|---|---|---|
| `"<end>"` | `"eos"` | 跨 backend 的标准 EOS 哨兵（PN.py 也改写为此） |
| `""` | `"all_voters_empty"` | aggregator 在全员 errored 时返回的兜底；显式区分 EOS 与"全员超时" |
| 其他 | 继续 | 步骤 +1，append 到所有 prompt，yield TokenEvent |
| 未中断退出循环 | `"max_len"` | 自然走完 `range(max_len)` → 默认值生效 |

##### 异常处理

- 单个 backend 的 `step_token` 抛 → 该 alias 进 `per_model_errors`
  （`f"{type}: {msg}"`），其他 voter 继续投，aggregator 自己决定
  能否产生 winner（sum_score 在全空时返回 `token=""`）
- 单个 backend 的 think phase 抛 → 该 alias 的 `suffix=""`（不影响
  joint loop 起点），trace 记一条 `ThinkTraceEntry(think_text="",
  elapsed_ms=0)`
- 节点级超时 / 全员失败 → `ParallelEnsembleNode._run` 在 P2.8 处理；
  runner 不直接 raise

#### `ThinkPhaseRunner` 契约

`type=think` 模型（如 DeepSeek-R1、Qwen-thinking）的 CoT 段必须先
跑完，否则跟 normal 模型在 token-level 投票时基线对不齐（一个在
`<think>...` 里一个在最终回答里）。

- 输入：`prompts: dict[alias, str]`、`backends: dict[alias, ModelBackend]`、
  `trace: TraceCollector`
- 输出：`dict[alias, suffix]`，suffix = `think_text + stop_think`
  （重新挂上 stop 标记，否则模型下一步还会再吐一次 stop token）
- 仅扫描 `spec.type == "think"` 且 `spec.stop_think` 非空的 alias，
  其他 alias 直接跳过
- 用 `getattr(backend._spec, ...)` 读 spec 字段，避免 SPI 给所有
  ModelBackend 强加 `stop_think` 接口（这是 llama.cpp-specific 概念）

`trace.record_think` **只在 driver 线程调用**（future.result() 之后），
因为 `TraceCollector` 内部 list 不是 thread-safe 的。`_think_one` 只
做计算 + 返回 `_ThinkResult`，主循环负责 trace 写入。

#### 测试目录

```
api/tests/unit_tests/core/workflow/nodes/parallel_ensemble/runners/
├── __init__.py
├── conftest.py                  # FakeBackend / cand / executor fixtures
├── test_think_phase.py          # 5 用例
└── test_token_step_runner.py    # 11 用例（含 think 一致性 2 条）
```

##### `conftest.py` —— `FakeBackend` 工厂

`ModelBackend` 的 ABC 接口需要实现 `capabilities` /
`validate_requirements` / `generate` / `step_token` / `apply_template`。
真用 `LlamaCppBackend` 测会被 HTTP 层拖累，所以 `FakeBackend`：

- 持有 `_FakeSpec`（duck-typed，只暴露 `id` / `model_name` / `weight`
  / `type` / `stop_think`，不强求 URL field 校验）
- `step_token` 从 `scripted_steps` 队列取下一组 candidates；超过队列
  长度后默认返回 `[<end>]`，让"步数 < max_len 但脚本写少了"的测试
  也能干净结束
- `step_raises` 列表对应位让某一步主动抛错，测 per_model_errors 路径
- `always_emit` 让 backend 永远返回同一组 candidates，测 max_len 路径
- 记录 `step_calls` / `generate_calls` / `template_calls` 让测试断言
  调用顺序和参数

##### 16 条用例

###### `test_think_phase.py` (5)

| 用例 | 内容 |
|---|---|
| `test_only_think_models_dispatched` | 仅 `type=think` 触发 generate；suffix == `think_text + stop_think`；`max_tokens=8196` 与 PN.py 对齐 |
| `test_no_think_models_returns_empty` | 全员 normal → 返回 `{}`，不 raise |
| `test_failure_suffix_is_empty` | think backend raise → suffix=`""`，trace 记一条 `think_text=""` 行 |
| `test_think_trace_gated_off` | `include_think_trace=False` → finalize 后 think_trace 为空 |
| `test_executor_owned_externally` | runner 不自建 pool — caller 持有 lifecycle |

###### `test_token_step_runner.py` (11)

| 用例 | 内容 |
|---|---|
| `test_registered_with_token_scope` | 装饰器副作用：`RunnerRegistry.get("token_step")` + scope/caps 正确 |
| `test_requirements_derive_from_top_k` | `top_k=7` → `min_top_k=7` + `needs_logprobs=True` |
| `test_token_step_runner_eos` | 3 token + `<end>` → yield `[token, token, token, done]`，metadata.stopped_by=`eos` |
| `test_token_step_runner_max_len` | 永不返回 `<end>` → `stopped_by="max_len"`，TokenEvent 数 == max_len |
| `test_token_step_prompt_sync` | 每轮所有 backend 的 prompt 都被追加同一 token（PN.py 主循环关键不变量） |
| `test_token_step_handles_per_model_errors` | 单 backend raise → 不阻塞本轮，trace.per_model_errors 含该 alias |
| `test_validate_selection_too_few_models` | 单模型 → severity=error, message 含 "at least 2" |
| `test_validate_selection_enable_think_no_think_models_warns` | enable_think=True 但无 think 模型 → warning |
| `test_validate_selection_enable_think_off_with_think_models_warns` | enable_think=False 但有 think 模型 → warning |
| `test_run_rejects_response_aggregator` | 误传 response-scope aggregator → `TypeError` (defensive，§9 已应该拦下) |
| `test_chat_template_invoked_for_capable_backends` | 有 CHAT_TEMPLATE → 调 apply_template 一次；无则用裸 question |

think 一致性的两条 warning 故意分开两个用例而不是合并，因为它们对应
*完全相反*的 misconfiguration，合并会让回归排查时分不清是哪一支
fail。

##### 不在本测试范围

- `aggregator.aggregate` 内部行为（已被 P2.5 aggregator 测 29 条覆盖）
- 节点装配 / 流式事件契约（P2.10）
- 真实 HTTP 层（P2.13 联调跑 dev server）
- 前端 `TokenStepConfig` 表单渲染（P2.12）

#### 注册路径

```python
# parallel_ensemble/__init__.py
from . import aggregators as aggregators
from . import backends as backends
from . import runners as runners        # ← P2.6 新加
```

```python
# runners/__init__.py
from . import token_step as token_step
```

`@register_runner("token_step")` 装饰器在
`runners/token_step.py` import 链路上跑过，之后
`RunnerRegistry.known_runners()` 立刻返回 `["token_step"]`。
`ThinkPhaseRunner` 不进 `RunnerRegistry`（它不是顶层 runner，而是
`TokenStepRunner.run` 的内部依赖）。

#### 验收

```
$ uv run --project api pytest \
    api/tests/unit_tests/core/workflow/nodes/parallel_ensemble/ \
    -q -o addopts=""
116 passed in 0.40s
```

构成：parallel_ensemble 既有 100 + **P2.6 新增 16** = 116。

```
$ uv run --project api ruff check api/core/workflow/nodes/parallel_ensemble/runners/ \
    api/tests/unit_tests/core/workflow/nodes/parallel_ensemble/runners/
All checks passed!

$ uv run --project api ruff format --check api/core/workflow/nodes/parallel_ensemble/runners/ \
    api/tests/unit_tests/core/workflow/nodes/parallel_ensemble/runners/
7 files already formatted
```

#### 后续依赖

- **P2.6.5 ResponseLevelRunner**：消费 `majority_vote` / `concat`，
  scope=`response`；signal 形状即 P2.5 的 `ResponseSignal`。代码挂在
  `runners/response_level.py`，import 到 `runners/__init__.py`。
- **P2.7 单测扩展**：本任务已覆盖 P2.7 中跟 runner 相关的 6 条
  （`test_token_step_runner_eos` / `..._max_len` / `..._prompt_sync` /
  `test_think_phase` 等）；剩 `test_capability_filter` /
  `test_requirements_validation` / `test_validate_selection_*` /
  `test_trace_collector_*` 与节点装配紧耦合，留 P2.10。
- **P2.8 ParallelEnsembleNode._run**：直接消费 `RunnerRegistry.get(...)`
  的实例；初始化时构造 `TokenStepRunner(executor=..., aggregator_config=...)`，
  调 `runner.run(question, backends, aggregator, runner_config, trace)`，
  转译 yield 到 `StreamChunkEvent`。
- **P2.9 node_factory.py**：在 `node_init_kwargs_factories` 加
  `parallel-ensemble` 分支，把共享 `ThreadPoolExecutor` 注入。

#### Code review 自查项

1. **SPI 兼容**：`TokenStepRunner` 的 `name` / `config_class` /
   `aggregator_scope` / `required_capabilities` / `optional_capabilities` /
   `i18n_key_prefix` / `ui_schema` 七个 ClassVar 全部覆盖；
   `__init_subclass__` 的 `UI_CONTROL_ALLOWLIST` 校验在 import 期跑过。
2. **PN.py 行为对齐**：`top_k` 默认 5、`max_len` 默认 1000、`enable_think`
   默认 True、think `max_tokens=8196`、`<end>` 哨兵跨 backend、
   prompt 同步追加 winning token —— 与 PN.py 一一对齐。
3. **三个偏离的 doc trail**：aggregator 可插拔 / executor 外注 /
   aggregator_config 在 `__init__` 绑定 —— 三处都在 token_step.py
   模块 docstring 顶部解释了 *why*。
4. **EOS / 全空 / max_len 三态**：`stopped_by` metadata 三种值显式
   区分，下游 trace 消费方可以分别统计；与 PN.py "硬 break 在 `<end>`
   或 max_len" 的二态相比信息更全。
5. **Trace 写入**：runner 内部永远调 `record_token_step` /
   `record_summary` / `record_think`，不分支判 `DiagnosticsConfig` —
   collector 自己 gate（与 P2.5 aggregator 一致的 SPI 契约）。
6. **fixture 隔离**：`FakeBackend` 不动 `RunnerRegistry._runners`，
   类级注册一次到底；`reset_for_testing` 不调用，避免和其他 runner
   测的注册副作用打架。
7. **Thread safety**：`TraceCollector` 的 `record_*` 只在 driver
   线程调；`step_token` / `generate` / `apply_template` 在 worker
   线程跑但不共享可变状态（per-call locals + per-instance
   `step_calls` 列表只 append 不读）。`ThinkPhaseRunner._think_one`
   返回 `_ThinkResult` 让 driver 写 trace，避免跨线程 list.append
   竞态。


---

### P2.6.5 - P2.6.5 Landing — `ResponseLevelRunner`

> Source shard: `P2.6.5_LANDING.md`


日期：2026-04-28

#### 范围

P2.5 已经把 4 个内置 aggregator（`response/{majority_vote, concat}` +
`token/{sum_score, max_score}`）落到 SPI 上；P2.6 把 PN.py 主循环的
`TokenStepRunner` + `ThinkPhaseRunner` 装进 `runners/` 子包；**P2.6.5
的本职是把第二个内置 runner — `ResponseLevelRunner` — 落到同一个
SPI 上**，让 `aggregator_scope="response"` 这条线在 v0.2 也能跑通，
让前端三轴下拉里的 `runner=response_level` 不再返回空，让 P2.8 的
`ParallelEnsembleNode._run` 在节点配 `runner_name=response_level` 时
能直接 `runner_registry.get(...)` 拿到一个能跑的 runner 类。

- 新增 `runners/response_level.py`：单文件 SPI 实现
- 接入 `runners/__init__.py` 副作用 import（与 `token_step` 并列）
- 1 个测试文件 14 条用例（12 主体 + 2 review-fix 回归），复用 P2.6 的 `conftest.FakeBackend`
- `parallel_ensemble/__init__.py` 不动（它已经 `from . import runners
  as runners`，子包内部加 import 即可）

**不做**：节点装配 / 流式事件转译（P2.8）；KV-cache 复用（非目标 §1.2）；
streaming-shaped 的"边吐边聚合"runner（v0.3 候选 — `optional_capabilities`
留了 `STREAMING` 的位置，但本 runner 用 `backend.generate` 一次拿
全文，非流式）；前端 `responseLevel.fields` i18n（P2.12）。

#### 包结构

```
api/core/workflow/nodes/parallel_ensemble/runners/
├── __init__.py          # ★ 加 `from . import response_level as response_level`
├── think_phase.py       # 不动
├── token_step.py        # 不动
└── response_level.py    # ★ 新增
```

#### 契约

| 字段 | 值 |
|---|---|
| `name` | `response_level`（装饰器赋值） |
| `aggregator_scope` | `response`（与 `majority_vote` / `concat` 配对） |
| `required_capabilities` | `frozenset()` —— `backend.generate` 是 SPI 地板，每个 backend 都实现 |
| `optional_capabilities` | `{STREAMING}` —— 仅信息性（panel 标"可流式"），本 runner 内部不调 `generate_stream` |
| `config_class` | `ResponseLevelConfig`（v0.2 无字段，`extra="forbid"`） |
| `i18n_key_prefix` | `parallelEnsemble.runners.responseLevel` |
| `ui_schema` | `{}`（无可调字段） |

##### `ResponseLevelConfig`

刻意留空 + `extra="forbid"`。**不**预占 `max_tokens` / `system_prompt` /
`per_backend_timeout` 这类字段——v0.2 surfaces 一旦放出去就要兜
向后兼容；空配置便于 v0.3 用 pydantic discriminator 平滑加字段而不
破坏已存盘的 DSL。yaml typo（如 `response_level: {top_k: 5}`）通过
`extra="forbid"` 在 boot 期被拒。

##### `requirements(config)`

返回 `[]`。`backend.generate` 是 `ModelBackend` 抽象方法（每个具体
backend 必须实现），没有"能不能跑 generate"这种 capability gate，
也没有 config-driven 的 `min_top_k` / `needs_logprobs` 这类约束。

##### `validate_selection(config, model_aliases, registry)`

只一条规则：`len(model_aliases) >= 2`，否则 `severity="error"`，
i18n 键复用 `parallelEnsemble.errors.tooFewModels`（与 `TokenStepRunner`
共享，避免文案分叉）。单模型 reduces to 直接调 LLM 节点，留 warning
会让用户以为 ensemble 在跑但其实没在 vote；error 让前端在保存时直接
拒，对齐 P1 `EnsembleAggregatorNode` 的"≥ 2 inputs"约束。

`registry` 不读：本 runner 没有 `type=think` 这类 spec-相关跨字段约束。
签名保留是 SPI 一致性要求（覆写 `validate_selection` 的所有 runner
拿同一份参数列表）。

##### `run(question, backends, aggregator, config, trace)` 主循环

```python
if not isinstance(aggregator, ResponseAggregator):
    raise TypeError(...)        # 防御：§9 scope filter 应已拦下

signals, error_count = self._generate_concurrent(question, backends, trace)

ctx = AggregationContext(
    backends=[],
    weights={alias: backend.weight for ...},
    capabilities={alias: backend.instance_capabilities for ...},
    runner_name="response_level",
    runner_config=config.model_dump(),
    trace=trace,
    elapsed_ms_so_far=...,
    step_index=None,            # response-scope 没有 step 概念
)
result = aggregator.aggregate(signals, ctx, self._aggregator_config)

trace.record_summary("backend_count", len(backends))
trace.record_summary("error_count", error_count)
trace.record_summary("total_elapsed_ms", total_elapsed_ms)

yield DoneEvent(kind="done", text=result["text"], metadata=result["metadata"])
```

##### `_generate_concurrent(question, backends, trace)` 并发 fan-out

```python
for alias, backend in backends.items():
    per_alias_starts[alias] = time.perf_counter()
    params: GenerationParams = {}                  # ← 每次新建（见 §"两条正确性不变量"）
    futures[executor.submit(backend.generate, question, params)] = alias

# as_completed：future 一完成就被处理，elapsed_ms 在 result() 之后取
# 才算它真正的耗时上界——而不是继承前一个慢 future 的等待时间。
for future in as_completed(futures):
    alias = futures[future]
    try:
        gen = future.result()
        elapsed_ms = ...
        successes[alias] = (gen, elapsed_ms)
    except Exception as exc:
        elapsed_ms = ...
        errors[alias] = (f"{type}: {msg}", elapsed_ms)

# 第二趟按 backends 插入序回放，保 concat 输出确定性。
for alias in backends:
    if alias in errors: ... else: ...
```

**两条正确性不变量**（review fix，2026-04-28）：

1. **`elapsed_ms` 在 `future.result()` 之后取**。如果在 result() 之前
   snapshot，第一个 future 永远记 ~0（提交后立刻进迭代但还没 block），
   后续 future 会继承前一个的等待时间——慢的 backend 提交在前 + 快的
   提交在后会让快的记成 1500ms。`as_completed` 让每个 future 在自己
   完成后立即被处理，记录的是 result-observable 的紧上界。
2. **`GenerationParams` 每次 `submit` 新建一份**。SPI 没禁止 backend
   mutate 自己拿到的 params dict（未来某个 `OpenAICompatBackend` 完全
   可能写 `params.setdefault("max_tokens", 1024)`）。共享一个 `{}` 跨
   多线程并发 generate 会泄漏 mutation。one-liner 防御。

##### 三个对 P1 `EnsembleAggregatorNode` 的差异

1. **一个节点而不是两个**。P1 用 `IterationStartNode` → 多分支 LLM 节点
   → `ensemble-aggregator` 收集器；P2.6.5 的 runner 直接在节点内
   并发 `backend.generate`，喂 `ResponseSignal` list 给 P2.5 的同一组
   aggregator。**metadata 形状（`strategy` / `votes` / `winner_votes` /
   `tie_break_applied` / `contributions`）严格 1:1 兼容 P1**，所以
   从 P1 DSL 迁过来的用户不需要改 selector。
2. **错误不阻断整个 run**。P1 多分支天然是独立 failure domain；同节点
   runner 必须显式做这件事——失败 backend 进 `ResponseSignal.error`
   且 `text=""`，aggregator（P2.5 已实现的 `valid = [s for s in signals
   if s.get("error") is None]` filter）会自动跳过。全员失败时
   `majority_vote` 返回 `text=""` + `winner_votes=0`（P2.5 显式覆盖
   过的 fallback），不抛异常；`error_count` 在 trace summary 里可见。
3. **Aggregator config 在 `__init__` 绑定**。和 `TokenStepRunner` 同
   理由（见 P2.6_LANDING §"为什么 aggregator_config 在 __init__"）：
   SPI 的 `run(...)` 已冻结，没有 aggregator-config 参数；节点是唯一
   同时拿到两边 config 的层，构造 runner 时一并传入。

##### `tokens_count` 的来源

`ResponseTraceEntry.tokens_count` 是 SPI 字段；本 runner 从
`gen["metadata"]` 里读两个候选键 —— `tokens_count`（OpenAI/通用）
和 `tokens_predicted`（llama.cpp `/completion` 实际返回的字段）。
非 `int` 类型（包括 `None`、字符串）时回落到 `0`：

```python
raw = metadata.get("tokens_count", metadata.get("tokens_predicted", 0))
tokens_count = raw if isinstance(raw, int) else 0
```

不做隐式 `int(raw)` 转换 —— 一个字符串值在这里是 backend 的 bug，
silent coercion 会把 bug 藏到 trace 里很难排查；显式回落到 0 让
trace 数字明显可疑（用户/审查发现"某 backend tokens_count 一直是
0"会去查 backend metadata 形状）。

##### Streaming 的语义

`optional_capabilities = {STREAMING}` **不会**让本 runner 内部去调
`generate_stream`；这是单字面量提示，由前端 panel 用作展示
（"这个 backend 标了可流式"）。本 runner 永远走 `backend.generate`
拿全文。真正"边流边聚合"的 runner 是 v0.3 的候选，会单独叫
`StreamingResponseLevelRunner` 并把 STREAMING 升到
`required_capabilities`。

#### 测试目录

```
api/tests/unit_tests/core/workflow/nodes/parallel_ensemble/runners/
├── __init__.py
├── conftest.py                       # 既有，FakeBackend/executor fixture 复用
├── test_response_level_runner.py     # ★ 新增 12 条
├── test_think_phase.py               # 不动
└── test_token_step_runner.py         # 不动
```

##### 14 条用例

| 用例 | 内容 |
|---|---|
| `test_registered_with_response_scope` | 装饰器副作用：`RunnerRegistry.get("response_level")` + scope/caps/ui_schema 正确 |
| `test_requirements_empty` | `requirements(ResponseLevelConfig())` → `[]` |
| `test_validate_selection_too_few_models` | 单模型 → severity=error，i18n_key=`parallelEnsemble.errors.tooFewModels` |
| `test_validate_selection_two_models_ok` | 双模型 → `[]` |
| `test_response_level_runner_majority_vote_happy_path` | 3 backend `yes/yes/no` → DoneEvent.text=`yes`，metadata.votes=`{yes:2, no:1}`，winner_votes=2 |
| `test_response_level_runner_concat` | 2 backend 经 concat（separator=` || `）→ DoneEvent.text=`alpha \|\| beta` |
| `test_response_level_per_backend_error_does_not_abort` | 1/3 backend raise → 余下 2 个仍正常投票，DoneEvent.text=`yes`，trace 含错误项，summary.error_count=1 |
| `test_response_level_all_errored_returns_empty` | 全员 raise → DoneEvent.text=`""`，winner_votes=0（majority_vote fallback） |
| `test_response_level_records_response_per_backend` | 每个 alias 都进 `record_response`；`finish_reason` 透传（stop / length） |
| `test_response_level_tokens_count_from_metadata` | `tokens_count`/`tokens_predicted` 两键都识别；非 int 回落 0 |
| `test_run_rejects_token_aggregator` | 误传 token-scope aggregator → `TypeError` (defensive，§9 应已拦下) |
| `test_response_level_emits_single_done_event` | 非流式：恰好 1 个 DoneEvent，0 个 TokenEvent |
| `test_response_level_elapsed_ms_independent_per_alias` | **review-fix 回归**：慢 backend 先提交、快 backend 后提交 → 快的 elapsed_ms 不继承慢的等待时间（`as_completed` + result 后 snapshot） |
| `test_response_level_fresh_params_per_submit` | **review-fix 回归**：每个 backend 收到的 `GenerationParams` 是**不同的 dict 对象**（`p1 is not p2`），杜绝跨线程 mutation 泄漏 |

`per_backend_error` / `all_errored` 故意分开测，因为它们覆盖
*不同*的代码路径（部分错与全错走不同 fallback：part 路径用 valid
voters 投，all 路径走 majority_vote 的 `if not valid: text=""` 分支）。
合并会让回归排查时分不清断的是哪一段。

##### 不在本测试范围

- `MajorityVoteAggregator` / `ConcatAggregator` 内部行为（P2.5 aggregator
  目录 29 条已覆盖）
- 节点装配 / 流式事件契约 / `_run()` outputs 装配（P2.8 / P2.10）
- 真实 HTTP backend 层（P2.13 联调跑 dev server）
- 前端 `responseLevel.fields` 表单渲染（P2.12）

#### 验收

```
$ uv run --project api pytest \
    api/tests/unit_tests/core/workflow/nodes/parallel_ensemble/ \
    api/tests/unit_tests/core/workflow/nodes/ensemble_aggregator/ \
    -q -o addopts=""
177 passed in 0.65s
```

构成：parallel_ensemble 既有 116（P1+P2.1.5+P2.2.4+P2.3+P2.5+P2.6）+
**P2.6.5 新增 14** = 130，加 P1 ensemble_aggregator 47 = 177。P1 47
条 / P2.5 P2.6 既有 116 条全程零修改通过。

```
$ uv run --group dev -- ruff check core/workflow/nodes/parallel_ensemble/runners/response_level.py \
    core/workflow/nodes/parallel_ensemble/runners/__init__.py \
    tests/unit_tests/core/workflow/nodes/parallel_ensemble/runners/test_response_level_runner.py
All checks passed!

$ uv run --group dev -- ruff format --check <same paths>
3 files already formatted

$ uv run --group dev -- basedpyright core/workflow/nodes/parallel_ensemble/runners/response_level.py \
    tests/unit_tests/core/workflow/nodes/parallel_ensemble/runners/test_response_level_runner.py
0 errors, 0 warnings, 0 notes
```

#### 后续依赖

- **P2.7 单测扩展**：本任务覆盖了 P2.7 中跟 response-scope runner 相关
  的 5 条（`test_response_level_runner` / `test_capability_filter`
  在 response-scope 那条变体 / `test_validate_selection_too_few_models`
  的 R-axis 变体 / `test_trace_collector_no_op` 在 response 路径上的
  变体 / 错误路径回归）。剩余 P2.7 用例（capability_filter 跨 runner
  的端到端、trace_collector_truncation 在 token 路径下的回归、
  validate_selection_judge_alias_not_in_models —— 都跟 token_step /
  judge runner 紧耦合）留 P2.10 节点单测。
- **P2.8 ParallelEnsembleNode._run**：直接消费 `RunnerRegistry.get("response_level")`
  的实例；初始化时 `ResponseLevelRunner(executor=..., aggregator_config=majority_vote_config)`，
  调 `runner.run(...)`，把 yield 的单个 DoneEvent 转译成
  `NodeRunResult(text=event.text, metadata=event.metadata)`，trace
  通过 `trace_collector.finalize()` 落到 `outputs.trace`。
- **P2.4 `/runners` endpoint**：本任务落地后该 endpoint 立即返回 2
  条（`token_step` + `response_level`），前端 P2.11 dropdown 不再为
  单选；P2.4 既有 fake-runner 测保留作注册路径回归。
- **P1 → P2 迁移路径**：DSL 里把
  `nodes[].data.type == "ensemble-aggregator"` 改成
  `parallel-ensemble`，配
  `runner_name=response_level` + `aggregator_name=majority_vote|concat`，
  metadata selector 不动 — 这条迁移可以等 P2.13 联调验证后写进
  `docs/ModelNet/architecture/EXTENSION_GUIDE.md`。

#### 注册路径

```python
# parallel_ensemble/__init__.py  (不变)
from . import aggregators as aggregators
from . import backends as backends
from . import runners as runners
```

```python
# runners/__init__.py  (★ 新加 response_level)
from . import response_level as response_level
from . import token_step as token_step
```

`@register_runner("response_level")` 装饰器在
`runners/response_level.py` import 链路上跑过，之后
`RunnerRegistry.known_runners()` 立刻返回
`["response_level", "token_step"]`（按字典序排）。

#### Code review 自查项

1. **SPI 兼容**：`ResponseLevelRunner` 的 `name` / `config_class` /
   `aggregator_scope` / `required_capabilities` / `optional_capabilities` /
   `i18n_key_prefix` / `ui_schema` 七个 ClassVar 全部覆盖；
   `__init_subclass__` 的 `UI_CONTROL_ALLOWLIST` 校验——`ui_schema={}`
   是空字典，所以遍历 0 次，import 期不会触发拒绝（与 `TokenStepRunner`
   非空 schema 走的是同一份代码，但分支不同）。
2. **P1 行为兼容**：`majority_vote` / `concat` 的 metadata 5 字段
   不动（P2.5 已对齐过），runner 直接 `metadata=result["metadata"]`
   传出，所以从 P1 DSL 迁过来的 selector 零修改。
3. **错误处理对称**：`_generate_concurrent` 在 except 分支也走
   `record_response`（`text=None` + `error=...`），而不是只在 success
   path 记 trace —— 这样 trace 的 alias 集合 == backends 的 alias
   集合，无 silent gap。
4. **`extra="forbid"` 全覆盖**：`ResponseLevelConfig` 空但有
   `extra="forbid"`，专门 yaml-typo 反例由 P2.5 / P2.6 类似机制覆盖
   （`pydantic` 抛 `ValidationError`，节点层兜底）。
5. **`isinstance(aggregator, ResponseAggregator)` 防御**：与
   `TokenStepRunner.run` 拒 ResponseAggregator 严格对称——一个 raise
   `TypeError("...TokenAggregator...")`，另一个 raise
   `TypeError("...ResponseAggregator...")`。两条都靠 §9 scope filter
   兜底，但先做 isinstance 校验比后续在 aggregate() 里崩 KeyError
   更易定位。
6. **`tokens_count` 防御**：非 int 回落 0 而非 `int(raw)`；非 int 是
   backend bug，silent coercion 会把 bug 藏到 trace 里，回落 0 让
   "总数 == 0"明显可疑。
7. **`AggregationContext.step_index=None`**：response-scope 本来就没
   step 概念；置 `None` 与 token_step 在 step 0/1/.../N-1 区别开，
   aggregator / trace 消费方可以用 `step_index is None` 判 scope。
8. **错误计数**：`trace.record_summary("error_count", error_count)`
   是 runner-level 错误数，与 `record_response` 的 per-alias error
   字段独立——两条都需要：summary 给 quick health check，per-alias
   给 debug。
9. **executor 外注**：与 `TokenStepRunner` 同一约束—— `__init__`
   接 executor，runner 自己不开 pool，符合 EXTENSIBILITY_SPEC §5
   的 "concurrency 由节点共享" 设计。


---

### P2.7 - P2.7 Landing — runners + aggregators 单测：确定性 + capability/requirements/trace 路径

> Source shard: `P2.7_LANDING.md`


日期：2026-04-28

#### 范围

P2.5 / P2.6 / P2.6.5 在落地各自代码时已经把对应路径的单测一并写完
（aggregators 29 条 / TokenStepRunner+ThinkPhase 16 条 / ResponseLevelRunner
14 条）。P2.7 的本职是**对照 TASKS.md L411–424 的 12 条用例做覆盖审计 +
补齐缺口**——把 §9 capability/requirements 校验路径、judge-style 跨字段
selection 校验、`TraceCollector` 的 diagnostics gating + last-N 截断
这几条之前散落或未独立落地的契约钉成专门测试，让 P2.8 节点装配阶段
不再需要在 `_run()` 里去发现这些不变量。

- **不引入任何生产代码改动**——纯测试层补齐
- 新增 `runners/test_validation_pipeline.py`（5 条）：§9 capability filter +
  `validate_requirements` + `validate_selection` 跨字段（judge 模式）
- 新增 `test_trace_collector.py`（8 条）：`DiagnosticsConfig` 三通道 gating +
  `max_trace_tokens` last-N 截断
- 既有 12 条 P2.7 用例已在 P2.5 / P2.6 / P2.6.5 阶段落地，本任务文档
  化映射关系（见下文「P2.7 12 条审计表」）

**不做**：节点层 `ParallelEnsembleNode._run` 上 §9 校验管线的端到端集成
（P2.8 + P2.10）；前端 panel 上的 ValidationIssue 渲染（P2.11）；judge runner
的真实生产实现（v0.3，本测试用合成 `_JudgeRunner` 钉接口契约）。

#### P2.7 12 条审计表

| # | TASKS.md L411–424 用例 | 落地位置 | 状态 |
|---|---|---|---|
| 1 | `test_sum_score_deterministic`（并列取字典序最小，多次跑一致） | `aggregators/test_token_sum_score.py::test_deterministic_tie_break` | ✅ P2.5 |
| 2 | `test_token_step_runner_eos`（mock `step_token`，N×TokenEvent + 1×DoneEvent + `stopped_by="eos"`） | `runners/test_token_step_runner.py::test_token_step_runner_eos` | ✅ P2.6 |
| 3 | `test_token_step_runner_max_len`（永不 `<end>`，`stopped_by="max_len"` + TokenEvent 数 == max_len） | `runners/test_token_step_runner.py::test_token_step_runner_max_len` | ✅ P2.6 |
| 4 | `test_token_step_prompt_sync`（每轮所有 backend 的 prompt 都被追加同一 token） | `runners/test_token_step_runner.py::test_token_step_prompt_sync` | ✅ P2.6 |
| 5 | `test_think_phase`（仅 `type="think"` 模型被调用，suffix 正确） | `runners/test_think_phase.py::test_only_think_models_dispatched` | ✅ P2.6 |
| 6 | `test_response_level_runner`（mock `generate`，DoneEvent + 经过 aggregator） | `runners/test_response_level_runner.py::test_response_level_runner_majority_vote_happy_path` + `_concat` | ✅ P2.6.5 |
| 7 | `test_capability_filter`（`required - declared` 不空 → `StructuredValidationError`） | `runners/test_validation_pipeline.py::test_capability_filter` | ★ P2.7 |
| 8 | `test_requirements_validation`（`backend.validate_requirements(spec, [...])` 返回 ValidationIssue list） | `runners/test_validation_pipeline.py::test_requirements_validation_returns_validation_issue_list` + 既有 `test_llama_cpp_backend.py::TestValidateRequirements`（拒函数调用） | ★ P2.7 + ✅ P2.2 |
| 9 | `test_validate_selection_too_few_models`（单模型 → ValidationIssue） | `runners/test_token_step_runner.py::test_validate_selection_too_few_models` + `runners/test_response_level_runner.py::test_validate_selection_too_few_models` | ✅ P2.6 / P2.6.5 |
| 10 | `test_validate_selection_judge_alias_not_in_models`（judge runner 跨字段校验） | `runners/test_validation_pipeline.py::test_validate_selection_judge_alias_not_in_models` | ★ P2.7（合成 `_JudgeRunner`） |
| 11 | `test_trace_collector_no_op`（`include_token_candidates=False` → `record_token_step` 是 no-op） | `test_trace_collector.py::test_trace_collector_no_op_when_token_candidates_disabled` | ★ P2.7 |
| 12 | `test_trace_collector_truncation`（超过 `max_trace_tokens` → last-N + `truncated=True`） | `test_trace_collector.py::test_trace_collector_truncation` | ★ P2.7 |

★ = 本次新增。✅ = 既有覆盖。

#### 包结构

```
api/tests/unit_tests/core/workflow/nodes/parallel_ensemble/
├── runners/
│   └── test_validation_pipeline.py   # ★ 新增 5 条
└── test_trace_collector.py           # ★ 新增 8 条
```

#### 契约

##### `test_validation_pipeline.py`：§9 校验管线

###### `test_capability_filter`

钉 `runner.required_capabilities - backend.capabilities(spec)` 这条
**纯集合差**契约——非空 = backend 不满足 runner 必备能力，框架在节点
启动期把这些缺失项包成 `ValidationIssue` list，再用
`StructuredValidationError(issues)` 兜起来一次性抛给前端 panel。

合成 `_LimitedBackend`（仅声明 `STREAMING`）+ `TokenStepRunner`
（要 `TOKEN_STEP + TOP_PROBS`）→ 缺集合 = `{TOKEN_STEP, TOP_PROBS}`。
正向用例 `test_capability_filter_passes_when_backend_satisfies_runner`
用真 `LlamaCppBackend` 钉「能力齐备 → 缺集合空」。

> **为什么不直接调一个 `validate_capabilities()` 函数**：v0.2 还没有
> 把这段集合差落成独立 helper（它的天然归属在 P2.8 节点 `_run` 里
> 与 spec 反查耦合）。本测试故意只钉「集合差行为 + 错误包装类」，让
> 未来 P2.8 提取 helper 时不必修改 P2.7 测试。

###### `test_requirements_validation_returns_validation_issue_list`

钉两条 `backend.validate_requirements(spec, [...])` 路径：

1. **手写 requirement**：`min_top_k=25` 直接喂给 `LlamaCppBackend` —
   llama.cpp 没 top-k 上限，返 `[]`。直接对应 TASKS.md P2.7 描述的
   原文 `[{kind:"min_top_k", value:25}]`。
2. **runner 派生**：`TokenStepRunner.requirements(TokenStepConfig(top_k=20))`
   → `[{min_top_k:20}, {needs_logprobs:true}]`，喂给 `LlamaCppBackend`
   全过 — 钉 runner ↔ backend 的 wiring（P2.8 启动期会照这条路径走）。

拒绝半边的 `needs_function_calling=True` → error 已在
`test_llama_cpp_backend.py::test_needs_function_calling_rejected` 覆盖
（P2.2 落地时一并写完）；本测试钉「无误报」半边，两边互补。

###### `test_validate_selection_judge_alias_not_in_models` + `_in_models_passes`

判 v0.2 还没 ship 真正的 judge runner（要等 v0.3，见
EXTENSIBILITY_SPEC §5.3），但 SPI 接口（`validate_selection` 跨字段
hook）已经冻结。本测试合成 `_JudgeRunner(EnsembleRunner[_JudgeConfig])`，
覆写 `validate_selection` 检查 `config.judge_alias in model_aliases` —
两条用例覆盖正反 path：

- 反例：`judge_alias="oracle"`，aliases=`["a","b"]` → 1 条
  `severity="error"` issue + i18n_key=`parallelEnsemble.errors.judgeAliasNotInModels`
- 正例：`judge_alias="b"`，aliases=`["a","b"]` → `[]`

这个合成 runner **不**注册到 `RunnerRegistry`（无 `@register_runner`
装饰器），仅作为 SPI 接口契约的"形状证据"，避免在测试 import 时污
染全局注册表。`__init_subclass__` 的 `UI_CONTROL_ALLOWLIST` 校验仍
会跑（`model_alias_select` 在白名单内），所以同时也轻量回归这条
boot-time 校验路径。

##### `test_trace_collector.py`：diagnostics gating + 截断

`TraceCollector` 是 P2.6 / P2.6.5 既有 runner 测试的间接覆盖对象，
但这些覆盖混在 runner 主流程里、且只测 happy path。P2.7 把 collector
本身的契约钉成专门测试，三组：

###### Token 通道 gating

- `test_trace_collector_no_op_when_token_candidates_disabled`：
  `include_token_candidates / include_per_backend_errors /
  include_aggregator_reasoning = False` → `per_model` /
  `per_model_errors` / `aggregator_reasoning` 在 `record_token_step`
  时被 drop，`finalize().token_trace` 仅含轻量字段（`step` /
  `selected_token` / `selected_score` / `elapsed_ms`）。**runner
  代码无须 if-flag，盲调 record_token_step 即可。**
- `test_trace_collector_keeps_token_candidates_when_enabled`：
  反向钉接 — flags 全开时重字段确实落到 trace。

###### Response 通道 gating

- `test_trace_collector_response_redaction`：
  `include_model_outputs=False` → `text` 不进 trace；
  `include_per_backend_errors=False` → `error` 不进 trace；
  轻量字段（`source_id` / `finish_reason` / `tokens_count` /
  `elapsed_ms`）始终保留，让 panel 能展示「某 backend 跑了 99 ms」
  而不泄漏正文。

###### Think 通道 gating

- `test_trace_collector_think_gated_off_is_no_op`：
  `include_think_trace=False` → `record_think` 整条 entry drop（CoT
  敏感程度足够高，所以是 all-or-nothing 而非按字段 redact）。
- `test_trace_collector_think_kept_when_enabled`：反向钉接。

###### `max_trace_tokens` last-N 截断

- `test_trace_collector_truncation`：
  cap=3，写入 7 条 → 保留 step=4/5/6（保尾不保头），
  `summary["truncated"]=True` + `summary["truncated_token_steps"]=4`。
  尾保留逻辑符合「token-step 失败一般出现在生成末段，模型偏离
  prompt 最远处」的经验，所以 last-N 比 first-N 更有 debug 价值。
- `test_trace_collector_no_truncation_marker_under_cap`：
  写入 ≤ cap → `summary` 里**没有** `truncated` 键 — panel 消费方
  可把该键存在性当作"数据有丢"信号。
- `test_trace_collector_truncation_preserves_field_redaction`：
  截断 + 字段 redaction 复合用例 — 既被丢一半步数，又走重字段
  redact 路径，钉两条互不影响。

#### 测试目录

```
api/tests/unit_tests/core/workflow/nodes/parallel_ensemble/
├── __init__.py
├── aggregators/                      # P2.5 既有 29 条
│   ├── conftest.py
│   ├── test_response_concat.py
│   ├── test_response_majority_vote.py
│   ├── test_token_max_score.py
│   └── test_token_sum_score.py
├── llama_cpp/                        # P2.3 既有
│   ├── test_backend_ssrf.py
│   └── test_registry_load.py
├── runners/
│   ├── __init__.py
│   ├── conftest.py                   # P2.6 既有 FakeBackend / executor
│   ├── test_response_level_runner.py # P2.6.5 既有 14 条
│   ├── test_think_phase.py           # P2.6 既有
│   ├── test_token_step_runner.py     # P2.6 既有
│   └── test_validation_pipeline.py   # ★ 新增 5 条
├── test_llama_cpp_backend.py         # P2.2 既有
├── test_model_registry.py            # P2.1 既有
├── test_spi_freeze.py                # P2.1.5 既有
└── test_trace_collector.py           # ★ 新增 8 条
```

#### 验收

```
$ uv run --project api pytest \
    api/tests/unit_tests/core/workflow/nodes/parallel_ensemble/ \
    api/tests/unit_tests/core/workflow/nodes/ensemble_aggregator/ \
    -q -o addopts=""
190 passed in 0.69s
```

构成：parallel_ensemble 既有 130（P1+P2.1.5+P2.2.4+P2.3+P2.5+P2.6+P2.6.5）
+ **P2.7 新增 13** = 143，加 P1 ensemble_aggregator 47 = 190。既有 177 条
全程零修改通过（本任务无生产代码改动）。

```
$ cd api && uv run ruff check tests/unit_tests/core/workflow/nodes/parallel_ensemble/runners/test_validation_pipeline.py \
    tests/unit_tests/core/workflow/nodes/parallel_ensemble/test_trace_collector.py
All checks passed!

$ uv run ruff format --check <same paths>
2 files already formatted

$ uv run --project . basedpyright   # 项目级（pyrightconfig.json 默认 exclude tests/）
0 errors, 0 warnings, 0 notes
```

> **为什么不单独 run basedpyright on test files**：`api/pyrightconfig.json`
> 显式 `"exclude": ["tests/", ...]`，整个 tests/ 目录不在严格类型检查
> 范围内（既有 conftest.py / test_local_models_api.py 单跑都有 5–25
> 个 strict-mode 报错）。P2.7 不引入生产代码，本任务的 basedpyright
> 验收等同项目级清白即可。

#### 后续依赖

- **P2.8 ParallelEnsembleNode._run**：直接消费本任务钉接的三条契约 —
  - `runner.required_capabilities - backend.capabilities(spec)` 集合差
    在 `_run()` 启动期跑一遍，缺集合非空时包成
    `StructuredValidationError(issues)`；
  - 节点构造 `TraceCollector(diagnostics)`，runner / aggregator 盲调
    `record_*` 即可（gating 由 collector 内部按本任务钉的契约处理）；
  - DSL 里 `runner_name` 反查的 runner 类调
    `validate_selection(config, model_aliases, registry)` 收 `ValidationIssue`
    list（含 judge-style 跨字段约束）—— `_JudgeRunner` 不会真的注册，
    P2.8 节点测的 judge runner 形状由 v0.3 真 ship 时再补。
- **P2.10 节点单测**：`test_capability_mismatch_raises` /
  `test_requirements_mismatch_raises` 是 P2.10 的列表项，本任务把
  SPI 层钉好，P2.10 在节点层端到端跑一遍（构造节点 → 喂 backend
  缺能力 → 期望 `StructuredValidationError`）。
- **EXTENSIBILITY_SPEC §5.3 judge runner**：v0.3 实现真 judge runner
  时，删除 `test_validation_pipeline.py` 里的 `_JudgeConfig` /
  `_JudgeRunner`，改 import 真类。本测试函数 `test_validate_selection_judge_alias_not_in_models`
  / `_in_models_passes` 的断言形状不变（issue.severity / message 子串 /
  i18n_key / requirement.kind），让真 judge runner 必须遵守这份合约。

#### Code review 自查项

1. **不污染全局注册表**：`_JudgeRunner` / `_LimitedBackend` 都不带
   `@register_runner` / `@register_backend`；测试 import 时 `RunnerRegistry`
   / `BackendRegistry` 仅含生产代码注册的项（`token_step` /
   `response_level` / `llama_cpp`）—— 跑全套 177 条既有用例的注册期
   断言（如 `test_registered_with_token_scope`）不受影响。
2. **`__init_subclass__` 兼容**：`_JudgeRunner.ui_schema =
   {"judge_alias": {"control": "model_alias_select"}}` —
   `model_alias_select` 在 `UI_CONTROL_ALLOWLIST` 里，import 期
   校验通过；如果未来移除该 control，本测试会立刻报错，反向给
   出 SPI 不能破坏性变更的回归。
3. **`StructuredValidationError.message` 形状**：测试断言
   `"missing capability" in err.message` + `"(+1 more)" in err.message`
   钉死 `exceptions.py:62` 的 `f"{first}{suffix}"` 模板格式；
   未来如果改 message 拼装方式，需要同步本测试。
4. **truncation 计数语义**：`truncated_token_steps == 4` 是被丢弃
   的步数（不是保留的步数），与 `summary` 字段命名一致 —
   panel 消费侧不必再做减法。
5. **TraceCollector finalize 副作用**：本测试每次都新建 collector，
   不复用 — `finalize()` 在 `EnsembleTrace` 内部 `list(self._token)`
   做了浅拷贝（`spi/trace.py:217-219`），但 `_summary` / 三个 list
   引用不被外部清空 — 多次 finalize 同一 collector 会得到等价结果，
   不在本测试范围（不属于 P2.7 列表项）。
6. **Pydantic v2 配置**：`_JudgeConfig` 用 `model_config = ConfigDict(extra="forbid")`
   与既有 `TokenStepConfig` / `ResponseLevelConfig` 同款；ruff
   `I001` 自动重排过 import。


---

### P2.8 - P2.8 Landing — `ParallelEnsembleNode._run()`：SPI 化 + 流式事件契约

> Source shard: `P2.8_LANDING.md`


日期：2026-04-28

#### 范围

落地 `parallel-ensemble` 节点的算法本体接入层：把 P2.5 / P2.6 / P2.6.5
已经在纯 Python 层验过的 SPI（runners + aggregators + trace）套上
**graphon 流式事件协议**，并把 EXTENSIBILITY_SPEC §9 的 5 步启动期校验
管线在 `_run()` 启动阶段一次性跑完。

- **新增** `entities.py`（顶层 `ParallelEnsembleNodeData` + 嵌套
  `ParallelEnsembleConfig` + DSL 敏感字段拒绝校验器）
- **新增** `node.py`（`ParallelEnsembleNode(Node[ParallelEnsembleNodeData])`、
  `_run()` 完整事件序列、§9 校验管线、trace 存储路由、status 派生）
- **微调** `__init__.py`：把 `PARALLEL_ENSEMBLE_NODE_TYPE` 常量上提到副作用
  import 之前，让 `entities.py` / `node.py` 在导入 `parallel_ensemble`
  包时不会反向触发循环（runners/backends/aggregators 不依赖节点类，
  仅依赖 SPI + 注册表）

**不做**（按 TASKS.md 切片）：
- `node_factory.py:372-440` 注入分支（P2.9）——本任务的 `__init__` 已经
  接好 5 个 keyword-only 依赖，P2.9 只需在 `node_init_kwargs_factories`
  里追加一支
- 节点单测（P2.10：事件序列 / capability/requirements 不匹配 /
  trace 存储两策略 / DSL 拒 url）——本任务已通过 inline smoke 验过
  关键路径，正式 pytest 在 P2.10 一次性补齐
- 前端 panel + 三轴下拉 + i18n（P2.11）

#### 文件结构

```
api/core/workflow/nodes/parallel_ensemble/
├── __init__.py                # 常量上提 + 副作用 import 顺序固化
├── entities.py                # ★ 新增 — DSL schema (NodeData + Config)
└── node.py                    # ★ 新增 — ParallelEnsembleNode._run()
```

#### 关键设计决策

##### 1. 两层 schema 防 SSRF / 凭证偷渡（TASKS.md L441）

**外层** `ParallelEnsembleNodeData(BaseNodeData)`：

- 继承 `BaseNodeData(extra="allow")`——保留 `selected` / `params` /
  `paramSchemas` / `datasource_label` 等图层兼容字段（参考
  `graphon.entities.base_node_data` L130-140 注释）
- 加 `model_validator(mode="before")` 显式黑名单拒
  `{model_url, api_key, api_key_env, url, endpoint}` — 在 pydantic
  把 key 塞进 `__pydantic_extra__` 之前先抛 `ValueError`，闭合
  `extra="allow"` 否则会留下的 SSRF 缝隙
- 黑名单是闭合 5 项，不做正则匹配——第三方扩展的 `system_prompt` 等
  非敏感字段仍能透传（与 BaseNodeData 设计意图一致）

**内层** `ParallelEnsembleConfig(BaseModel, extra="forbid")`：

- 业务字段：`question_variable` / `model_aliases` / `runner_name` /
  `runner_config` / `aggregator_name` / `aggregator_config` / `diagnostics`
- `extra="forbid"` 拒一切未声明字段——DSL 无法在 `ensemble:` 块里
  挂任何 framework 不识别的 key
- `runner_config: dict[str, object]` 是开 schema，由
  `runner_cls.config_class.model_validate(cfg.runner_config)` 在
  `_run()` 第一步做二级 schema 校验（每个 runner 的 config_class 都
  自带 `extra="forbid"`，所以偷渡 `model_url` 进 `runner_config` 也跑
  不通）

##### 2. 节点 `__init__` 5 + 1 个 keyword-only 依赖

```python
def __init__(
    self,
    id, config, graph_init_params, graph_runtime_state,
    *,
    model_registry: ModelRegistry,           # P2.1.5 升级后的 alias→spec 单例
    runner_registry: type[RunnerRegistry],   # 类级注册表
    aggregator_registry: type[AggregatorRegistry],
    backend_registry: type[BackendRegistry],
    executor: ThreadPoolExecutor,            # 共享线程池（runner 用）
    http_client: object | None = None,       # 默认 fallback core.helper.ssrf_proxy
)
```

- 5 个核心依赖与 TASKS.md P2.9 列出的 kwargs 完全对齐
- 第 6 个 `http_client`（默认 `None`）是为了让标准库测试 / 工具脚本
  能直接构造节点而不必预热 Flask 侧 `ssrf_proxy`——production wiring
  在 P2.9 时由 `node_factory` 显式传入和 `http_request` 节点同一份
  `ssrf_proxy` 句柄
- `ssrf_proxy` 用 lazy import（`if http_client is None:` 分支内）避免
  `parallel_ensemble` 包被纯 SPI 测试 import 时拖入 Flask 依赖

##### 3. EXTENSIBILITY_SPEC §9 启动期校验管线（5 步）

`_validate_at_startup()` 严格按 §9 顺序：

| 步 | 校验 | 失败时的错误形式 |
|---|---|---|
| 1 | scope 对齐：`agg.scope == runner.aggregator_scope` | `StructuredValidationError`（单条 `scopeMismatch`） |
| 2 | runner_config / aggregator_config 各 `model_validate` | pydantic `ValidationError`（带字段路径，panel 直显） |
| 3 | capability 粗过滤：`required - declared` 非空 → 错 | `StructuredValidationError`（per-alias，**聚合**所有失败） |
| 4 | requirements 精校验：`backend.validate_requirements(spec, runner.requirements(cfg))` | `StructuredValidationError`（聚合 issues） |
| 5 | 跨字段 `runner.validate_selection(cfg, aliases, registry)` | `StructuredValidationError`（聚合 issues） |

**聚合而非首错即抛**：3-5 步的所有 `severity="error"` 一次性收集进
`issues: list[ValidationIssue]`，最后一次性 `raise` —— 让 panel 能在一
次保存里看到所有问题（不是修一个发现下一个再保存一次）。

**performance 优化**：步骤 4 跳过步骤 3 已经失败的 alias
（`capability_failed: set[str]`），避免对同一 backend 双重报错。

##### 4. graphon 事件序列契约（TASKS.md L443-450）

```python
for event in runner.run(...):
    match event:
        case {"kind": "token", "delta": delta}:
            yield StreamChunkEvent(selector=[self._node_id, "text"],
                                    chunk=delta, is_final=False)
        case {"kind": "done", "text": done_text}:
            if not accumulated:        # token 流的 accumulator 优先
                accumulated = done_text
        case {"kind": "full_response", "source_id": source_id}:
            logger.debug(...)          # judge runner v0.3，本版本 no-op
        case _:
            logger.warning(...)        # 第三方扩展防御

# 封口块（必须！否则下游 Answer 节点不 flush）
yield StreamChunkEvent(selector=[self._node_id, "text"],
                        chunk="", is_final=True)

yield StreamCompletedEvent(node_run_result=NodeRunResult(...))
```

**钉死的 4 个细节**：
1. `selector=[self._node_id, "text"]`：用 `_node_id` 不是 `id`
   （二者运行时同值，但 graphon `_dispatch` 内部一律用 `_node_id`，
   保持一致）
2. `is_final=True` 封口块的 `chunk=""`，不是缺省
3. `StreamCompletedEvent(node_run_result=...)` 必须 keyword
4. `match` 而非 `if event["kind"]`：basedpyright 只能对前者做
   `RunnerEvent` 联合类型的 narrowing；后者会报 "delta is not a
   defined key in DoneEvent"

##### 5. Trace 存储 — `process_data["ensemble_trace"]` 而非 `metadata`（与 §7.4 略有偏差）

**问题**：EXTENSIBILITY_SPEC §7.4 写
`metadata["ensemble_trace"] = trace`，但 graphon 的 `NodeRunResult.metadata`
被严格 typed 为 `Mapping[WorkflowNodeExecutionMetadataKey, Any]`，
任何非枚举字符串 key 都被 pydantic 拒。验证：

```
pydantic_core.ValidationError: 1 validation error for NodeRunResult
metadata.ensemble_trace.[key]
  Input should be 'total_tokens', 'total_price', ... [type=enum]
```

**解决**：trace 落到 `NodeRunResult.process_data["ensemble_trace"]`。
理由：

- `process_data: Mapping[str, Any]` 是 graphon 自由 dict 槽
- `services/workflow_service.py:1430` 把 `process_data` 持久化到
  `node_execution.process_data`，run-history viewer 可查
- 不进变量池（与 storage="metadata" 的语义意图一致）
- `outputs.text` 仍干净

EXTENSIBILITY_SPEC §7.4 待下一轮文档 pass 时修订指向
`process_data`。Inline 路径不变（`outputs["trace"] = trace_data`，
真的进变量池）。

##### 6. 全 backend 失败 → status=FAILED（TASKS.md L454）

`_derive_status()` 检查 trace summary：

- `error_count >= backend_count > 0`（response_level 路径）→ FAILED
- `stopped_by == "all_voters_empty"`（token_step 路径）→ FAILED
- 其它 → SUCCEEDED

第三方 runner 想触发 FAILED 有两条路：record 上述 summary key，或
直接抛异常让 graphon `Node.run()` 兜成 `NodeRunFailedEvent`（base.py
L416-432）。

#### 验证

##### 静态检查

```bash
uv run --project . ruff check core/workflow/nodes/parallel_ensemble/
uv run --project . ruff format --check core/workflow/nodes/parallel_ensemble/
uv run --project . basedpyright core/workflow/nodes/parallel_ensemble/{node,entities,__init__}.py
```

全绿（0 errors / 0 warnings / 0 notes）。

##### 回归测试

```bash
uv run --project . pytest \
  tests/unit_tests/core/workflow/nodes/parallel_ensemble/ \
  tests/unit_tests/core/workflow/nodes/ensemble_aggregator/ \
  tests/unit_tests/controllers/console/workspace/test_local_models_api.py \
  -q -o addopts=""
```

→ **199/199 绿**（既有 P1 47 + P2.1.5 34 + P2.2 25 + P2.3 12 + P2.4 9 +
P2.5 29 + P2.6 16 + P2.6.5 14 + P2.7 13）；本任务零生产代码改动到既有
模块，纯新增 + `__init__.py` 顺序微调。

##### 节点注册回归

```python
from core.workflow.nodes.parallel_ensemble.node import ParallelEnsembleNode
from graphon.nodes.base.node import Node
mapping = Node.get_node_type_classes_mapping()
assert "parallel-ensemble" in mapping
assert mapping["parallel-ensemble"]["1"] is ParallelEnsembleNode
assert mapping["parallel-ensemble"]["latest"] is ParallelEnsembleNode
```

→ 通过。`__init_subclass__` 自动注册路径已验证（Phase 0 Q3 结论）。

##### Inline smoke（5 条关键路径）

> 这些是设计期手工 smoke，**不**计入 P2.10 测试数。P2.10 会用 pytest
> 把同样路径钉死。

1. ✅ 事件序列：3 token + 1 closing-empty + 1 StreamCompletedEvent
2. ✅ inline storage：`outputs.trace` 有，`process_data.ensemble_trace`
   无
3. ✅ metadata storage：`outputs.trace` 无，`process_data.ensemble_trace`
   有
4. ✅ 全 backend error → status=FAILED
5. ✅ capability mismatch → `StructuredValidationError`
6. ✅ scope mismatch → `StructuredValidationError`
7. ✅ DSL `model_url` 偷渡 → `ValidationError`

#### 已知 follow-up

- P2.9：node_factory 注入分支（5 kwargs + http_client）
- P2.10：把上文 7 条 inline smoke 移成正式 pytest 测试 +
  补 `paramSchemas` / `selected` 等 BaseNodeData 兼容字段穿透测试
- EXTENSIBILITY_SPEC §7.4 文字修订：`metadata["ensemble_trace"]` →
  `process_data["ensemble_trace"]`（本任务讲清楚了 why；改文档不在 P2.8 范围）
- P2.11：前端三轴下拉 + DiagnosticsConfig 表单 + 9 处注册 + i18n


---

### P2.9 - P2.9 Landing — `node_factory` 注入分支：lazy 共享 executor + 四注册表 + ssrf http_client

> Source shard: `P2.9_LANDING.md`


日期：2026-04-28

#### 范围

把 P2.8 已经接好 6 个 keyword-only 依赖的 `ParallelEnsembleNode.__init__`
真正接到 graphon 运行时上：在 `DifyNodeFactory.create_node` 的
`node_init_kwargs_factories` mapping 里加一支 `parallel-ensemble` 分支，
按需注入四个注册表 + 一个**懒构造、跨节点共享**的 `ThreadPoolExecutor` +
production 复用 HTTP_REQUEST 节点同一份 `ssrf_proxy` 句柄。

- **改** `api/core/workflow/node_factory.py`：4 处 import + 1 个 lazy
  attribute + 1 个 `_get_parallel_ensemble_executor()` 方法 + 1 条
  `PARALLEL_ENSEMBLE_NODE_TYPE` mapping 分支（共 +29 行）
- **改** `api/tests/unit_tests/core/workflow/test_node_factory.py`：fixture
  同步默认值 +2 条新单测（共 +75 行）
- **改** `docs/ModelNet/active/TASKS.md`：勾选 P2.9，正文升级为已落地说明

**不做**（按 TASKS.md 切片）：
- `ParallelEnsembleNode` 端到端 pytest（P2.10：事件序列 / capability/requirements
  不匹配 / trace 存储两策略 / DSL 拒 url）—— P2.8 已用 inline smoke 验过 7
  条关键路径，P2.10 一次性补齐
- 前端 panel + 三轴下拉 + i18n（P2.11）

#### 文件结构

```
api/core/workflow/
├── node_factory.py                            # ★ +29 行：import + lazy attr + getter + mapping 分支
└── nodes/parallel_ensemble/registry.py        # 已存在（P2.1.5 / P2.2 落地）

api/tests/unit_tests/core/workflow/
└── test_node_factory.py                       # ★ +75 行：fixture 同步 + 2 条新测

api/configs/feature/__init__.py
└── PARALLEL_ENSEMBLE_MAX_WORKERS              # 已存在（P2.1.5 引入），default=8
```

#### 关键设计决策

##### 1. 懒构造的共享 executor —— 不付无关 workflow 的开销，bound fan-out 线程数

```python
# DifyNodeFactory.__init__ 末尾
self._parallel_ensemble_executor: ThreadPoolExecutor | None = None

def _get_parallel_ensemble_executor(self) -> ThreadPoolExecutor:
    if self._parallel_ensemble_executor is None:
        self._parallel_ensemble_executor = ThreadPoolExecutor(
            max_workers=dify_config.PARALLEL_ENSEMBLE_MAX_WORKERS,
            thread_name_prefix="parallel-ensemble",
        )
    return self._parallel_ensemble_executor
```

**两个属性同时成立**：

- **Lazy**：factory 构造时不创建 pool。没有 `parallel-ensemble` 节点的
  workflow（绝大多数）不付建池开销（系统线程 + atexit 注册 + bookkeeping）
- **Cached / shared**：同一个 `DifyNodeFactory` 实例创建的所有
  `parallel-ensemble` 节点共享**同一个** `ThreadPoolExecutor`。`DifyNodeFactory`
  生命周期 = 一次 workflow 运行，所以 pool 的作用域也是一次 workflow 运行
  的所有 `parallel-ensemble` 节点

**为什么共享而不是节点内自建**（TASKS.md R10）：一个 workflow 里如果有 N
个 `parallel-ensemble` 节点，每个节点又向 K 个 backend 扇出，节点内自建会
得到 N×K 个总线程；共享则在 `PARALLEL_ENSEMBLE_MAX_WORKERS` 范围内 bound
住总线程数。

**为什么 per-factory（per-run）而不是 per-process 单例**：跨 workflow 共享
没有显著收益（pool 启停成本远低于一次 workflow 内的 LLM 调用），但 per-
process 单例需要处理 process 重启 / pool reuse-after-shutdown / 多 worker
进程语义等场景，复杂度不值得。每次 workflow 自己一个 pool，结束随 factory
被 GC，由 Python `concurrent.futures.thread._python_exit` atexit 兜底
shutdown，与 P2.8 `ResponseLevelRunner` 自带的 `concurrent.futures.wait
(timeout=...)` 决断超时机制一致。

**为什么 GraphEngine 不暴露 executor 给我们复用**：实测 `grep
ThreadPoolExecutor api/ graphon/`（venv 内 graphon 源码）只有
`iteration_node.py` 一处 `with ThreadPoolExecutor(...)` 局部块，
GraphEngine 本身没有进程级共享 executor 暴露给节点用。R10 备选方案
（节点侧自建 + bound）即本任务采用方案。

##### 2. 四注册表的注入：3 个 class + 1 个 instance

```python
PARALLEL_ENSEMBLE_NODE_TYPE: lambda: {
    "model_registry": ModelRegistry.instance(),     # ★ 实例（yaml 单例）
    "runner_registry": RunnerRegistry,              # ★ 类
    "aggregator_registry": AggregatorRegistry,      # ★ 类
    "backend_registry": BackendRegistry,            # ★ 类
    "executor": self._get_parallel_ensemble_executor(),
    "http_client": self._http_request_http_client,
},
```

| kwarg | 类型 | 来源 | 为什么这种形式 |
|---|---|---|---|
| `model_registry` | **instance** | `ModelRegistry.instance()` | YAML 配置（`model_net.yaml`）需要 boot-time 加载 + 缓存；instance() 是进程级单例，多 workflow 共享同一份 alias→spec 映射 |
| `runner_registry` | **class** | `RunnerRegistry` | P2.5/P2.6 定义的"装饰器即注册"模式：注册表是类级 dict，类本身是单例容器，不需要也不应该实例化 |
| `aggregator_registry` | **class** | `AggregatorRegistry` | 同上（P1 + P2.4 落地） |
| `backend_registry` | **class** | `BackendRegistry` | 同上（P2.2 落地） |

**`model_registry` 是 instance 而不是类的原因**：它的状态来自 YAML 文件（`api/configs/model_net.yaml`），有 boot-time IO；其它三个注册表的状态来自 `@register` 装饰器在 import 时填充的类级 dict，没有 IO。

##### 3. 复用 `_http_request_http_client`（同一个 `ssrf_proxy` 实例）

```python
"http_client": self._http_request_http_client,  # 与 HTTP_REQUEST / DOCUMENT_EXTRACTOR 同一个对象
```

`_http_request_http_client` 在 `DifyNodeFactory.__init__` 里被设为
`ssrf_proxy`（`node_factory.py:308`），同时被注入给 `HTTP_REQUEST`（L404）、
`DOCUMENT_EXTRACTOR`（L425）、LLM 类节点（`include_http_client=True` 路径，
L515）。本任务把同一个对象再注入给 `parallel-ensemble`：

- **节点侧不持有 SSRF 边界知识**：`parallel-ensemble` 不需要知道"如何防 SSRF"，
  它只接收一个标准的 httpx-like client 对象。SSRF 防护由 `ssrf_proxy` 自身
  在每次 `request()` 时统一处理（dns rebind、ip 黑名单、超时、重定向白名单
  等），与节点类型无关
- **测试可注入 fake client**：`ParallelEnsembleNode.__init__` 的
  `http_client: object | None = None` 默认值允许标准库测试不预热 Flask 侧
  `ssrf_proxy`；P2.8 inline smoke 已经验过这条路径

##### 4. 单测的两条核心契约（identity-based assertion）

###### `test_creates_parallel_ensemble_node` —— 6 kwargs 身份注入正确

```python
assert kwargs["model_registry"] is model_registry_instance     # mock
assert kwargs["runner_registry"] is RunnerRegistry             # 真的类
assert kwargs["aggregator_registry"] is AggregatorRegistry     # 真的类
assert kwargs["backend_registry"] is BackendRegistry           # 真的类
assert kwargs["executor"] is executor                          # mock sentinel
assert kwargs["http_client"] is sentinel.http_client           # 与 fixture 对齐
```

**为什么用 `is` 而不是 `==`**：

- 三个 class registry：必须是**同一个类对象**而不是 "看起来一样的另一个类"。
  如果有人在重构时不小心改成 `RunnerRegistry()` 或 `RunnerRegistry.copy()`，
  `==` 可能仍然通过（类的 `__eq__` 默认是 identity，但子类可能被 override），
  `is` 才能钉死"是同一个进程级 singleton 容器"
- `model_registry`：mock 实例，必须是**那一次** `ModelRegistry.instance()`
  返回的对象，确保 `instance()` 真的被调用了一次
- `executor`：必须是 `_get_parallel_ensemble_executor()` 缓存的那个对象，
  防御未来误改成 `ThreadPoolExecutor(...)` 直接传

###### `test_parallel_ensemble_executor_is_lazy_and_cached` —— R10 thread bounding

```python
assert factory._parallel_ensemble_executor is None           # lazy
thread_pool_executor.assert_not_called()

factory.create_node({"id": "node-a", "data": {"type": PARALLEL_ENSEMBLE_NODE_TYPE}})
factory.create_node({"id": "node-b", "data": {"type": PARALLEL_ENSEMBLE_NODE_TYPE}})

thread_pool_executor.assert_called_once()                    # cached（仅 1 次实例化）
assert constructor.call_args_list[0].kwargs["executor"] is executor   # node-a 拿到
assert constructor.call_args_list[1].kwargs["executor"] is executor   # node-b 拿到同一个
```

**两个节点拿到同一个 executor 对象**就是 R10 的形式化验证 —— 多个
`parallel-ensemble` 节点共享线程池，bound 住总线程数。如果未来误改成 per-
node 自建池（例如直接 `lambda: {"executor": ThreadPoolExecutor(...)}`），
这条 assertion 立刻红。

##### 5. fixture 同步：`factory._parallel_ensemble_executor = None`

```python
@pytest.fixture
def factory(self, ...):
    factory = DifyNodeFactory.__new__(DifyNodeFactory)  # bypass __init__
    ...
    factory._parallel_ensemble_executor = None          # ★ 同步 __init__ 默认值
    return factory
```

`TestDifyNodeFactoryCreateNode.factory` fixture 用 `__new__` 跳过 `__init__`
以便手工注入 sentinel 依赖（这是既有 pattern，与 `_http_request_config`、
`_llm_credentials_provider` 等同处）。`__init__` 新增的 `_parallel_ensemble_
executor: None` 必须在 fixture 里手工同步，否则 `_get_parallel_ensemble_
executor()` 会抛 `AttributeError: ... has no attribute '_parallel_ensemble_
executor'`。

#### 验证

##### 静态检查

```bash
uv run --project . ruff check core/workflow/node_factory.py \
    tests/unit_tests/core/workflow/test_node_factory.py
uv run --project . ruff format --check core/workflow/node_factory.py \
    tests/unit_tests/core/workflow/test_node_factory.py
uv run --project . basedpyright core/workflow/node_factory.py \
    tests/unit_tests/core/workflow/test_node_factory.py
```

全绿（0 errors / 0 warnings / 0 notes）。

##### 回归测试

```bash
uv run --project . pytest \
  tests/unit_tests/core/workflow/nodes/parallel_ensemble/ \
  tests/unit_tests/core/workflow/nodes/ensemble_aggregator/ \
  tests/unit_tests/core/workflow/test_node_factory.py \
  -q -o addopts=""
```

→ **227/227 绿** = `parallel_ensemble/` 143 + `ensemble_aggregator/` 47
（Phase 1 全量）+ `test_node_factory.py` 35 + 新增 2。

无生产侧既有路径回归（既有 10 条 mapping 分支不变，只追加 1 条；既有
fixture 只追加 1 行 attribute 默认值同步）。

##### 节点-工厂端到端契约

```python
# 端到端契约：DSL → factory → node 实例 → 6 kwargs 全部到位
factory = DifyNodeFactory(...)
node = factory.create_node({
    "id": "ens-1",
    "data": {"type": "parallel-ensemble", "version": "1", ...},
})
assert isinstance(node, ParallelEnsembleNode)
# 6 kwargs 通过 ParallelEnsembleNode.__init__ 落到 node.<attr>
# 由 P2.10 的 pytest 正式断言
```

P2.8 已经在 inline smoke 里走过 7 条关键路径，本任务不重复；P2.10 会用
pytest 把端到端钉死。

#### 已知 follow-up

- **P2.10**：把 P2.8 7 条 inline smoke 移成正式 pytest 测试 + 补
  `paramSchemas` / `selected` 等 BaseNodeData 兼容字段穿透测试 + 正式
  端到端 factory→node 契约
- **P2.11**：前端三轴下拉 + DiagnosticsConfig 表单 + 9 处注册 + i18n
- **EXTENSIBILITY_SPEC §7.4 文字修订**：`metadata["ensemble_trace"]` →
  `process_data["ensemble_trace"]`（P2.8 已讲清楚 why；改文档不在 P2.9 范围）
- **`_python_exit` shutdown 行为复核**：当前依赖 Python 解释器
  `concurrent.futures.thread._python_exit` atexit 在进程退出时清理 pool。
  Flask 多 worker / gunicorn graceful reload 场景下若发现 pool 未释放，
  考虑在 `DifyNodeFactory.__del__` 或 `GraphEngine` finally 块里显式
  `executor.shutdown(wait=False)`（**目前无证据**说明这是问题，先观察）


---

### P2.10 - P2.10 Landing — `ParallelEnsembleNode` 单测：事件序列 + §9 校验 + Trace storage + DSL 偷渡防护

> Source shard: `P2.10_LANDING.md`


日期：2026-04-28

#### 范围

把 P2.8 留下的 7 条 `inline smoke`（不入测试基线、靠 `__main__` 跑一次性
sanity）正式落到 pytest 基线里，并把 P2.10 spec 列出的 13 条用例补全。
本任务 **零生产代码改动**——只新增一个测试文件。

- **新增** `api/tests/unit_tests/core/workflow/nodes/parallel_ensemble/test_node.py`
  （+998 行，16 条 pytest）
- **改** `docs/ModelNet/active/TASKS.md`：勾选 P2.10，正文升级为已落地说明

**不做**（按 TASKS.md 切片）：
- 前端 panel + 三轴下拉 + i18n（P2.11）
- workflow / chat 模式联调（P2.13 / P2.14）
- 性能基准 + SSRF 抗压 + Trace boundary（P2.15）

#### 文件结构

```
api/tests/unit_tests/core/workflow/nodes/parallel_ensemble/
└── test_node.py                    # ★ 新增 998 行 / 16 测试
```

#### 测试矩阵（vs P2.10 spec）

| spec 用例 | 测试方法 | 类 |
|---|---|---|
| `test_event_sequence` | `test_event_sequence_streaming` | `TestEventSequence` |
| `test_completed_outputs` | `test_completed_outputs` | `TestEventSequence` |
| `test_capability_mismatch_raises` | `test_capability_mismatch_raises` | `TestStartupValidation` |
| `test_requirements_mismatch_raises` | `test_requirements_mismatch_raises` | `TestStartupValidation` |
| `test_validate_selection_propagates` | `test_validate_selection_propagates` | `TestStartupValidation` |
| `test_single_model_timeout` | `test_single_model_timeout` | `TestBackendFailures` |
| `test_all_timeout` | `test_all_timeout` | `TestBackendFailures` |
| `test_storage_inline` | `test_storage_inline` | `TestTraceStorage` |
| `test_storage_metadata` | `test_storage_metadata` | `TestTraceStorage` |
| `test_diagnostics_token_candidates_off` | `test_diagnostics_token_candidates_off` | `TestDiagnosticsGating` |
| `test_dsl_rejects_model_url` | `test_dsl_rejects_model_url` | `TestDSLSmuggle` |
| `test_dsl_rejects_runner_config_smuggle` | `test_dsl_rejects_runner_config_smuggle` | `TestDSLSmuggle` |
| `test_dsl_compat_keys_allowed` | `test_dsl_compat_keys_allowed` | `TestDSLSmuggle` |

13 / 13 spec 用例全覆盖；额外 3 条（`test_scope_mismatch_raises` / `test_dsl_rejects_top_level_credentials` / `test_ensemble_config_extra_forbid`）补齐 §9 step-1 + DSL 名单全枚举 + 业务子模型层 forbid，因为 spec 文字里"DSL 拒 url 类敏感字段"是一个**集合**的承诺，单点测试压不住其它 4 个名单成员（`api_key / api_key_env / url / endpoint`）回归——回归保护比单点契约重要。

#### 关键设计决策

##### 1. `_make_node` 绕过 `Node.__init__` —— 让单测对齐"节点本身做什么"

```python
node = ParallelEnsembleNode.__new__(ParallelEnsembleNode)
node._node_id = "pe_1"
node._model_registry = _FakeModelRegistry(specs)
node._runner_registry = _FakeRunnerRegistry(runners)
node._aggregator_registry = _FakeAggregatorRegistry(aggregators)
node._backend_registry = _FakeBackendRegistry(backends)
node._executor = ThreadPoolExecutor(max_workers=2)
node._http_client = None

class _RS: pass
rs = _RS()
rs.variable_pool = pool or _build_pool()
node.graph_runtime_state = rs
node._node_data = ParallelEnsembleNodeData.model_validate(payload)
```

**为什么不走 `Node.__init__`**：基类签名要求真实的 `GraphInitParams` /
`GraphRuntimeState` / workflow id / run-context mapping——把这些喂上来意味着把
"测节点行为"变成"测一段 graphon 运行时拼接"。`_run` 实际只读 7 个属性
（`_node_id` + 4 个 registry + `_executor` + `_http_client` + `graph_runtime_state.variable_pool` + `_node_data`），用 `__new__` 直接注入比 mock 整个
`Node.__init__` 链路更精确——这条 pattern 已经在
`ensemble_aggregator/test_node.py::_make_node` 里跑过一遍，两个套件读起来
对称，未来加节点的人有现成模板可仿。

**factory 链路的契约不在这里测**：`DifyNodeFactory` 6 个 kwargs 的注入
身份验证已经被 P2.9 的 `test_creates_parallel_ensemble_node` 钉死；本任务
钉的是"6 个 kwargs 都到位**之后**节点本身做什么"，两个层切干净不重测。

##### 2. 合成 runner / backend 优先于内置类——把"节点契约"从"算法行为"剥开

事件序列 / 校验 / DSL / 诊断这 4 条用例都用 `_ScriptedRunner` 喂预录事件：

```python
class _ScriptedRunner(EnsembleRunner[_ScriptedConfig]):
    scripted_events: ClassVar[list[RunnerEvent]] = []
    def run(self, ...):
        yield from type(self).scripted_events
```

**为什么不直接用 `TokenStepRunner` / `ResponseLevelRunner`**：

- 事件序列测要断言"3 token + 1 closing + 1 completed"——内置 runner
  的事件序列受真实 backend mock 行为驱动，要改一条 token 数得改一堆
  candidate 列表，等于把 runner 的内部状态当节点契约测；scripted 序列让
  断言只看节点的"event 翻译契约"
- §9 校验测要用一个**特意不达标**的 runner 把 `requirements()` /
  `validate_selection()` 路径打开。`TokenStepConfig.top_k` 上限 20（OpenAI
  对齐）使自然路径走不出 `min_top_k=25`；`_BigTopKRunner` 用一个开放上限
  的 config 类合成需求 25，专门驱动 §9 step 4 的拒绝分支
- `_RejectingRunner.validate_selection` 直接返回一个 `error` issue，
  专门驱动 §9 step 5 的 propagate 分支——现网内置 runner 不会在
  正常配置下产生这种 issue（只有 `judge_alias not in model_aliases` 等
  极端 misconfiguration 才触发），合成 runner 让分支测成本下降一个数量级

只有 storage / diagnostics 两个测用真 `ResponseLevelRunner` +
`MajorityVoteAggregator`——这两条要看节点对**真实 runner 写入的 trace**
怎么 finalize，合成 trace 测不到 finalize 的字段映射真的对。

##### 3. `_make_response_backend_class`：类级参数化绕开"节点从 class 构造 backend"的限制

```python
def _make_response_backend_class(scripted_text, *, scripted_exc=None):
    class _Param(_ResponseOnlyBackend):
        def __init__(self, spec, http):
            super().__init__(spec, http, scripted_text=scripted_text, scripted_exc=scripted_exc)
    _Param.__name__ = f"_ParamResponseBackend_{scripted_text}_{type(scripted_exc).__name__}"
    return _Param
```

`ParallelEnsembleNode._instantiate_backends` 走的是
`backend_cls(spec, http=self._http_client)`——**只接受 spec + http 两个参数**，
没有 `scripted_text` / `scripted_exc` 之类 per-test 注入位。要在 backend 里
喂"返回 'ok'"或"抛 TimeoutError"，参数得搭乘到**类**上，构造时才能到达
`__init__`。闭包在每次 `_make_response_backend_class` 调用里捕获那次的
text / exc，类名拼上参数避免 pytest 报告时多个测试共享同名混淆。

##### 4. 三层 DSL 偷渡防护——一次测一个边界，不混测

| 层 | 模式 | 触发例 | 测试 |
|---|---|---|---|
| 顶层 `BaseNodeData(extra="allow")` | `mode="before"` 黑名单 | `node.data.model_url = "..."` | `test_dsl_rejects_model_url`、`test_dsl_rejects_top_level_credentials` |
| 内层业务 `ParallelEnsembleConfig` | `extra="forbid"` | `ensemble.foo = "x"`（typo / smuggle） | `test_ensemble_config_extra_forbid` |
| 运行时 `runner_cls.config_class` | `extra="forbid"`（schema 是 `dict[str, object]`） | `runner_config.model_url = "..."` | `test_dsl_rejects_runner_config_smuggle` |

**为什么三层各测一个，而不是一个测试覆盖三层**：每一层是不同时机被触发的：

- 顶层是 `ParallelEnsembleNodeData.model_validate(...)` 时刻——`BaseNodeData`
  允许任意字段，所以这层不能依赖 `extra="forbid"`，必须显式黑名单
- 内层是同一次 `model_validate` 但下沉到 `ensemble:` 子模型——业务字段
  封闭，typo / 偷渡都死在这层
- 运行时层是 `_run` 启动后的 `runner_cls.config_class.model_validate(cfg.runner_config)`——
  schema 上 `runner_config` 是 `dict[str, object]`（必须是 dict 才能
  让不同 runner 用不同 config schema），所以这一层 forbid 是**runner
  自己**的 `config_class.model_config = ConfigDict(extra="forbid")`，
  不是 entities 层的事

把三层混在一个测试里，未来一个层被打开（例如有人把 `BaseNodeData` 改成
`extra="forbid"`，意外让 `selected` / `params` 等 BaseNodeData 兼容字段也
被拒，破坏 `TASKS.md` Phase 0 记录的兼容契约），故障点不容易定位。所以
`test_dsl_compat_keys_allowed` 单独确保 `selected / params / paramSchemas
/ datasource_label` 通过——这是 `BaseNodeData(extra="allow")` 的**正向**
契约测试，对面 `test_dsl_rejects_model_url` 是负向。

`test_dsl_rejects_runner_config_smuggle` 用真的 `ResponseLevelConfig` 测，
不用合成 config 类——这条契约的承诺是"内置 runner 的 config 类一定打开
forbid"，用合成类就把承诺改成了"测试用例自己设置的 forbid"，绕过了对
真实代码的回归保护。

##### 5. Storage 二选一是**互斥**契约——`outputs.trace` 和 `process_data.ensemble_trace` 不能同时出现

```python
# test_storage_inline
assert "trace" in nrr.outputs
assert "ensemble_trace" not in nrr.process_data   # ★ 反向断言

# test_storage_metadata
assert "trace" not in nrr.outputs                 # ★ 反向断言
assert "ensemble_trace" in nrr.process_data
```

每条测试都同时断言"该来的来了 + 不该来的没来"。如果未来谁不小心把
`_finalize_outputs` 改成两边都写（"防御性"双写），变量池会冗余携带 trace
（潜在容量爆炸 + 下游 selector `[node, "trace"]` 在 metadata 模式下也命中，
违反 `TASKS.md` Phase 0 记录的"metadata 不入变量池"基础不变量）。互斥断言把 
这条不变量钉死。

##### 6. §9 step 4 的"两 backend 都拒"是关键——不是"任一 backend 拒就够"

```python
# test_requirements_mismatch_raises
messages = [issue["message"] for issue in exc.value.issues]
assert all("top_logprobs is capped at 20" in m for m in messages)
assert all("requested 25" in m for m in messages)
```

默认 `_make_node(model_aliases=["m1", "m2"])`，两个 alias 都接到
`_OpenAIStyleBackend`，两个都拒 `min_top_k=25`。**`all(...)` 比
`any(...)` 强**——它附带断言"`_validate_at_startup` 没有在第一个 alias
失败后短路返回"，因为 `node.py:411-413` 的契约是"先收齐 + 一次性
raise"，让 panel 一次性渲染所有 offending alias。如果未来谁把
`for alias in cfg.model_aliases: ... issues.extend(...)` 错改成
`if backend_cls.validate_requirements(spec, requirements): break`，
`all` 会立即红，`any` 不会。

##### 7. `test_diagnostics_token_candidates_off` 用闭包内类——节点级 redaction，不是 runner 级

```python
class _RecordingRunner(EnsembleRunner[_ScriptedConfig]):
    def run(self, ..., trace):
        trace.record_token_step({
            "step": 0, ...,
            "per_model": {"m1": [{"token": "x", "prob": 0.5, "logit": None}]},
        })
        yield DoneEvent(...)
```

runner **盲传** full token candidates（`per_model` 字段始终在 dict 里）；
是 `TraceCollector(cfg.diagnostics)` 在 `record_*` 时刻按 `include_token_
candidates=False` 把 `per_model` 删掉的——这是 P2.7 落地的契约。本测
存在的意义：**确认节点把 `cfg.diagnostics` 真的喂给了 collector**。
没有这层信任的话，`include_*=False` 设置可以一路到 finalize 都没生效，
trace 体积爆炸，工作流卡住。

闭包里定义 runner 类（不是 module 级别 `_BigTopKRunner` 那种位置），让
runner 的 `record_token_step` 调用可以写死特定 step 字段而不污染其它
测试用的合成 runner——同时一眼看出这条 runner 是 *for this test only*。

##### 8. `test_all_timeout` 断言 `nrr.error == "all backends failed"`

```python
assert nrr.error == "all backends failed"
```

这是 `node.py:289` 的硬字符串，**不是 i18n 字段**。FAILED 状态下节点的
`error` 文案是工作流执行历史的可见字符串（不是用户面板的红字提示——那
是 `StructuredValidationError.issues[*].i18n_key` 的事）。把这条字符串
钉死避免有人把它改成 `"degraded"` / `""` / `None` 等违背 graphon
`NodeRunResult.error` 契约的形态（graphon 期望 SUCCEEDED 时 `error == ""`，
非 SUCCEEDED 时非空）。

#### 验证

##### 静态检查

```bash
uv run --project . ruff check tests/unit_tests/core/workflow/nodes/parallel_ensemble/test_node.py
uv run --project . ruff format --check tests/unit_tests/core/workflow/nodes/parallel_ensemble/test_node.py
uv run --project . basedpyright tests/unit_tests/core/workflow/nodes/parallel_ensemble/test_node.py
```

→ `All checks passed!` / `1 file already formatted` / `0 errors, 0 warnings, 0 notes`。

##### 回归测试

```bash
uv run --project . pytest \
  tests/unit_tests/core/workflow/nodes/parallel_ensemble/ \
  tests/unit_tests/core/workflow/nodes/ensemble_aggregator/ \
  tests/unit_tests/core/workflow/test_node_factory.py \
  -q -o addopts=""
```

→ **243 / 243 绿** = `parallel_ensemble/` 159（既有 143 + 本任务新增 16）+
`ensemble_aggregator/` 47 + `test_node_factory.py` 37（既有 35 + P2.9
新增 2）。0.87s 全跑完。

新增 16 测试无生产代码触达，零回归——本任务**只新增一个文件**，既有
143 条 `parallel_ensemble/` 子目录测试 + 47 条 `ensemble_aggregator/`
全量 + 37 条 `test_node_factory.py` 一字不改全绿。

#### 已知 follow-up

- **EXTENSIBILITY_SPEC §7.4 文字修订**：`metadata["ensemble_trace"]` →
  `process_data["ensemble_trace"]`（P2.8 已讲清楚 why；改文档不在 P2.10
  范围；本任务 `test_storage_metadata` 已把"`process_data` 是真正
  落地点"通过测试钉死，文档修订更多是为了让外部贡献者读到的
  spec 与实际行为一致）
- **P2.11**：前端 parallel-ensemble 包 + 三轴下拉 + ui_schema 反射表单
  + DiagnosticsConfig 面板 + 9 处注册 + i18n
- **P2.13 / P2.14 联调**：workflow（→End）+ chat（→Answer）模式 dev
  server 验证；本任务的合成 runner / scripted-event 测试**不能取代**端到端
  联调（浏览器流式渲染 / 真实 llama.cpp 后端 token 节奏 / 与 PN.py 行为
  对照需要真实 backend）
- **P2.15 Trace 大小 boundary**：`max_trace_tokens=1000` × 1500 步实际
  截断验证 + `storage="inline"` 大小超限自动降级 metadata 的 OQ-4
  分支——本任务 16 测试都用小输入，未触及 boundary 行为


---

### P2.11 - P2.11 Landing — 前端 `parallel-ensemble` 包 + 三轴下拉 + `ui_schema` 反射表单 + DiagnosticsConfig 面板 + 9 处注册 + i18n

> Source shard: `P2.11_LANDING.md`


日期：2026-04-28（初稿）；2026-04-28 review round 1 修订

#### 范围

把 P2.10 之前完成的后端三轴 SPI（runner / aggregator / backend）+ §9 startup
校验 + DSL 偷渡防护暴露成可用的画布节点。本任务**零后端改动** —— 三个
console GET 端点（`local-models / runners / aggregators`）在 P2.9 之前
已经就绪，本任务只是消费它们。

- **新增** 12 个前端文件
- **改** 9 处注册位（与 P1.6 同模式）
- **改** 2 个 i18n JSON（en-US + zh-Hans，各新增 94 keys）
- **改** `docs/ModelNet/active/TASKS.md`：勾选 P2.11，正文升级为已落地说明

**不做**（按 TASKS.md 切片）：
- TS 类型检 / lint / 单测（P2.12 — `web/node_modules` 当前缺；同 P1.6 → P1.7 模式）
- workflow / chat 模式 dev server 联调（P2.13 / P2.14）
- 性能基准 + SSRF 抗压 + Trace 大小 boundary（P2.15）

#### review round 1 修订（2026-04-28）

外部 reviewer 指出 4 处问题（2 紧急 + 2 改进），全部确认有效并已修复：

| # | 问题 | 文件 | 修复 |
|---|---|---|---|
| 1（紧急）| OutputVars 与后端 `_finalize_outputs` 不一致：前端暴露 `metadata`（不存在），后端实际 emit `text + tokens_count + elapsed_ms + (trace iff storage="inline")`（参见 `api/core/workflow/nodes/parallel_ensemble/node.py:494`）| `panel.tsx` + `web/app/components/workflow/nodes/_base/components/variable/utils.ts` | 替换 `metadata` 为 `tokens_count` (number) + `elapsed_ms` (number)；`trace` 在 panel 里按 `ensemble.diagnostics.storage === 'inline'` 条件渲染；`getNodeOutputVars` switch 列出 4 个 selector 上限（`trace` 在 metadata 模式下解析为 undefined，与未连接边等价，不破坏下游）；en-US/zh-Hans i18n 各 +3 keys（`outputVars.{tokensCount,elapsedMs,trace}`）|
| 2（紧急）| `model-selector.tsx` import 了被 `web/eslint.constants.mjs:33` 显式禁用的 `@/app/components/base/tooltip`（OVERLAY_RESTRICTED_IMPORT_PATTERNS 里 `**/base/tooltip` 这条；触发即 lint 失败）| `components/model-selector.tsx` | 改用 `@langgenius/dify-ui/tooltip` 的 Radix 三件套 `Tooltip / TooltipTrigger / TooltipContent`，`TooltipTrigger.render={row}` 包住原 `DropdownMenuItem`，DOM 树没多塞 div |
| 3（建议）| `use-registries.ts` 用裸 `service/base.get` + 自造 queryKey，绕过 `web/AGENTS.md` "Query & Mutation (Mandatory)" 契约约束 | `web/contract/console/parallel-ensemble.ts`（新增）+ `web/contract/router.ts` + `use-registries.ts` | 新增三个 oRPC 契约（`parallelEnsembleLocalModelsContract / RunnersContract / AggregatorsContract`），全用 `.output(type<...>())` 显式约束响应形状；`router.ts` 在 `consoleRouterContract` 加 `parallelEnsemble: { localModels, runners, aggregators }`；`use-registries.ts` 三个 hook 改用 `consoleQuery.parallelEnsemble.<x>.queryOptions(STATIC_REGISTRY_OPTS)`，所有 staleTime / gcTime / retry 字段都在 oRPC 选项里传 |
| 4（建议）| `default.ts:86` 的 `model_aliases` 静态校验是 ≥ 1，但内置两个 runner（`response_level / token_step`）的 `validate_selection` 都要求 ≥ 2。允许"前端通过 + 运行期失败"的可见性反模式 | `default.ts checkValid` + i18n | 显式名单 `BUILT_IN_RUNNERS_REQUIRING_TWO = {response_level, token_step}`，命中时把 `minAliases` 抬到 2，错误信息走专用 i18n key `errorMsg.runnerNeedsTwoAliases`；其它 / 未来第三方 runner（如 judge 风格 1+1 contestant）保留 ≥ 1 兜底，靠 runner 自己的 `validate_selection` 在运行期把关 |

i18n parity 修订后两套各 97 keys（en-US ↔ zh-Hans 完全对齐，python diff 0/0）。

##### 关键决策：fix #1 的 `trace` selector 依然在 `getNodeOutputVars` 里**无条件**列出

panel.tsx 的 `OutputVars` 渲染按 `storage === 'inline'` 条件展示 `trace` 行，但 `getNodeOutputVars`（`utils.ts:2214`）作为 selector 枚举上限**不读 node data**（API 签名只接 id + nodeType），所以无法做条件分支。两个权衡：

- **A）只列 `text + tokens_count + elapsed_ms`**：用户切到 `storage="inline"` 时 `trace` 不出现在变量选择器里，下游节点要引用 `trace` 必须重启编辑器或用未提示的字符串 hack。
- **B）四个全列**（采纳）：`trace` selector 始终可被下游引用；`storage="metadata"` 模式下 selector 解析为 undefined（与"上游未连接边"等价路径），graphon 的 `VariablePool` 已经处理这种语义；用户体验是"如果你切到 inline 立刻可以引用 trace"。

panel 端的 `OutputVars` UI 仍按 storage 条件渲染，让"现在能取的字段"在 panel 文档区显式可见（防止用户误以为 metadata 模式也能从变量池取到 trace）。两层语义一致：**panel = 当前可取**、**utils = selector 字典上限**。

##### 关键决策：fix #4 用闭名单而非"读 RunnerMeta.required_capabilities"

诱惑做法是从 `useRunners()` 的 RunnerMeta 投影里读出当前 runner 的 ≥ 2 模型要求 —— 但 RunnerMeta 不带这条信息（`validate_selection` 是运行期函数，前端拿不到它的代码）。要把 ≥ 2 这个事实变成 metadata 字段需要后端改：

1. 在 `EnsembleRunner` SPI 上新增 `min_model_aliases: ClassVar[int] = 1`
2. 让 `validate_selection` 在 < `min_model_aliases` 时统一报 issue
3. 把 `min_model_aliases` 投影到 `runners.py::_project_runner` 输出

那是 P3 / Phase 4 范围的 SPI 增量，会破坏 P2.10 钉死的 SPI 接口快照。当前修复用前端闭名单先把回归挡住、保持 SPI 接口冻结；future 把 `min_model_aliases` 抬到 SPI 字段时，前端把闭名单换成读 `runner.min_model_aliases ?? 1` 即可，UI 行为不变。

#### 文件清单

```
web/app/components/workflow/nodes/parallel-ensemble/
├── default.ts                              # NodeDefault + checkValid（DSL 偷渡 5 字段 + storage / max_trace_tokens 边界）
├── types.ts                                # ParallelEnsembleNodeType + DiagnosticsConfig + RunnerMeta + AggregatorMeta + BackendInfo + UI_CONTROLS
├── node.tsx                                # 画布缩略：runner 名 + 模型计数
├── panel.tsx                               # 4 段编排：question / models / runner+config / aggregator+config / diagnostics
├── use-config.ts                           # 7 个 handler + 静态 ValidationIssue + 跨字段联动（runner 切换自动清空失配 aggregator）
├── use-registries.ts                       # 三个 GET 端点的 TanStack Query 包装
└── components/
    ├── model-selector.tsx                  # MultiSelect，按 runner.required_capabilities 灰显不兼容别名 + Tooltip
    ├── runner-selector.tsx                 # 单选 dropdown，i18n_key_prefix 显示 name + description
    ├── aggregator-selector.tsx             # 单选 dropdown，按 scope == runner.aggregator_scope 过滤
    ├── dynamic-config-form.tsx             # 7 种控件白名单反射渲染；非白名单 → alert 而非静默
    ├── diagnostics-config.tsx              # 8 switch + max_trace_tokens + storage select
    └── import-model-info-button.tsx        # 解析 model_info.json，仅取 id 字段
```

#### 9 处注册（与 P1.6 同位）

| # | 文件 | 改动 |
|---|---|---|
| ① | `web/app/components/workflow/types.ts` | `BlockEnum` 末尾加 `ParallelEnsemble = 'parallel-ensemble'` |
| ② | `web/app/components/workflow/block-selector/constants.tsx` | `BLOCKS` 在 `EnsembleAggregator` 后插入 `Parallel Ensemble`（同 Transform 分组）|
| ③ | `web/app/components/workflow/nodes/components.ts` | 顶部 `import ParallelEnsembleNode/Panel`；`NodeComponentMap` + `PanelComponentMap` 各加一行 |
| ④ | `web/app/components/workflow/block-icon.tsx` | `DEFAULT_ICON_MAP[ParallelEnsemble] = VariableX`；`ICON_CONTAINER_BG_COLOR_MAP[ParallelEnsemble] = 'bg-util-colors-indigo-indigo-500'`（与 EnsembleAggregator 同色，两节点同属 ensemble 家族）|
| ⑤ | `web/app/components/workflow/constants.ts` | `SUPPORT_OUTPUT_VARS_NODE` 追加 |
| ⑥ | `web/app/components/workflow/nodes/_base/components/workflow-panel/last-run/use-last-run.ts` | `singleRunFormParamsHooks` + `getDataForCheckMoreHooks` 两张 `Record<BlockEnum, any>` 各补 `undefined`（节点不需要自定义 single-run 表单）|
| ⑦ | `web/app/components/workflow/nodes/_base/components/variable/utils.ts` | `getNodeOutputVars` switch 末尾新增 `case ParallelEnsemble: push([id,"text"]); push([id,"metadata"])`（与后端 NodeRunResult outputs.text + outputs.metadata 一致；trace 单独走 outputs.trace 时另由 SUPPORT_OUTPUT_VARS_NODE 触发）|
| ⑧ | `web/app/components/workflow/utils/workflow.ts` | `canRunBySingle` 链末尾追加 `\|\| ParallelEnsemble` |
| ⑨ | `web/app/components/workflow/constants/node.ts` | 顶部 import `parallelEnsembleDefault`；`WORKFLOW_COMMON_NODES` 在 `ensembleAggregatorDefault` 后插入（与 BLOCKS 顺序对齐，同 P1.6 §1.0 review 修订要求）|

#### i18n（en-US + zh-Hans 各 94 keys）

```
blocks.parallel-ensemble                    × 1
blocksAbout.parallel-ensemble               × 1
nodes.parallelEnsemble.*                    × 56
  ├─ title / questionVariable / models / runner / aggregator / runnerConfig / aggregatorConfig 等基础 label
  ├─ outputVars.{text, metadata}
  ├─ modelCount_{one, other} / modelsSelectedCount_{one, other}（i18next 复数惯例）
  ├─ diagnostics.{title, tooltip}
  ├─ diagnostics.<flag>.{label, tooltip} × 8
  ├─ diagnostics.maxTraceTokens.{label, tooltip}
  ├─ diagnostics.storage.{label, tooltip, options.{inline, metadata}}
  ├─ importToast.{matched, noneMatched, parseFailed}
  └─ errorMsg.{configMustBeObject, duplicateModelAlias, forbiddenDslKey,
                maxTraceTokensPositive, modelAliasMustBeString,
                modelAliasSelectNotPlumbed, modelMissingCapability,
                unknownStorage, unknownUiControl}
parallelEnsemble.runners.responseLevel.{name, description}                 × 2
parallelEnsemble.runners.tokenStep.{name, description, fields.<>}          × 8 (3 fields × 2 keys + 2)
parallelEnsemble.aggregators.majorityVote.{name, description}              × 2
parallelEnsemble.aggregators.concat.{name, description, fields.<>}         × 6
parallelEnsemble.aggregators.sumScore.{name, description, fields.<>}       × 6
parallelEnsemble.aggregators.maxScore.{name, description, fields.<>}       × 6
parallelEnsemble.errors.{tooFewModels, modelMissingCapability,
                         aggregatorScopeMismatch, thinkNoModels,
                         thinkOffWithThinkModels}                          × 5
                                                                           ----
                                                                           94
```

en-US 与 zh-Hans key 集合**完全对齐**（python diff 0 / 0）；JSON 解析两份均通过。

#### 关键设计决策

##### 1. 三个 GET 端点走 `service/base.get` + TanStack Query，不走 `web/contract/console`

P2.11 spec 默认走 oRPC 契约层，但权衡后选用更轻的 path：

- 三个端点都是只读 GET、无 body —— 没有请求形状要靠 contract 约束
- 走 contract 要在 `web/contract/router.ts` 注册 + 重新编译 consoleClient，影响面比 P2.11 仅前端的范围大
- TS 类型 `BackendInfo / RunnerMeta / AggregatorMeta` 已经在 `types.ts` 里 1:1 镜像后端 `_project_*` 投影函数（``api/controllers/console/workspace/{local_models,runners,aggregators}.py``），类型安全已经达成

未来若 P2.13 / P3 加 `/parallel-ensemble/validate` 这类**带 body 的 mutation**，再把当前三个端点一并搬到 `web/contract/console/parallel-ensemble.ts` 把 contract layer 一次升级。

`use-registries.ts` 用 5 min `staleTime` + 30 min `gcTime`：注册表只随 yaml + backend 重启变化，缓存窗口宽一点能消除"开节点 → 关 → 再开"反复 fetch 的浪费。

##### 2. `ui_schema` 反射的"未知控件 → 渲染 alert"而非静默吞掉

```tsx
if (!ALLOWED_CONTROLS.has(field.control)) {
  return (
    <Field title={label} tooltip={tooltip}>
      <div role="alert" className="...">
        {t('nodes.parallelEnsemble.errorMsg.unknownUiControl', ...)}
      </div>
    </Field>
  )
}
```

理由是 SPI 同侧 `EnsembleRunner.__init_subclass__` 在 backend 启动时已经
对 `ui_schema` 做了 ALLOWLIST 检查（`spi/runner.py` line 132–152），所以正
常情况这分支永远不命中。但前端再加一层 alert 保护下游：

- 第三方扩展可能旁路 SPI 检查（极端情况下注册了带未知控件的 runner，没有重启服务）
- DSL 序列化往返中 `ui_schema` 不参与持久化（来自后端 fetch），但若 fetch 与运行 backend 版本不一致，控件名也会失配
- 如果未来某 v0.3 控件被 backend 加进 SPI 但前端 `UI_CONTROLS` 数组忘了同步加，alert 立刻可见，比"字段不见了"更好排错

##### 3. 切换 runner 时自动清空失配的 aggregator

```ts
// use-config.ts handleRunnerChange
const oldAgg = aggregators.find(a => a.name === draft.ensemble?.aggregator_name)
if (oldAgg && oldAgg.scope !== runner.aggregator_scope) {
  draft.ensemble.aggregator_name = ''
  draft.ensemble.aggregator_config = {}
}
```

如果不清，用户存盘的 DSL 会带"runner=token_step + aggregator=majority_vote"
这种组合，§9 startup pipeline 的 step-1（aggregator scope match）拒绝，
panel 上显示 StructuredValidationError，但用户在 UI 上看不到任何"我刚刚干
了什么"的线索（因为切换 runner 是用户主动操作，aggregator 不会变红，aggregator 那栏是个被动 placeholder）。
主动清空 + 让 aggregator dropdown 强制 re-pick，错误链路被斩断在画布层。

替代方案"自动选择第一个 scope 匹配的 aggregator"看起来更友好，但会**沉默**地改用户的配置 —— 用户切到 token_step 后悄无声息从 majority_vote 跳到 sum_score，不知道发生了什么。**强制清空 + UI 露出 placeholder 提醒重选**显式得多。

##### 4. 静态 ValidationIssue 只覆盖 capability + scope 两条

P2.11 spec 写"实时调后端 `validate_requirements` API（防抖 500ms）"，
当前 backend 没有这个端点。`runner_cls.validate_selection` 是 §9 step 5
的运行期校验，只在 `_run` 启动时跑。

落地策略：

| 校验类型 | 谁跑 | 出错时面板呈现 |
|---|---|---|
| capability 子集（model lacks required cap） | 前端 `use-config.ts::validationIssues` | 立即红框 + i18n 翻译消息 |
| scope match（aggregator_scope == runner_scope） | 前端 `use-config.ts::validationIssues` | 立即红框 + i18n 翻译消息 |
| 模型数 ≥ 2（response_level / token_step 各自要求）| 后端 §9 step 5 `validate_selection` | 运行期 StructuredValidationError → 节点 FAILED |
| `enable_think` 与 type=think 模型一致性（warning） | 后端 §9 step 5 | 运行期 issue list（warning 不阻塞）|
| `judge_alias must be in model_aliases`（未来 judge runner） | 后端 §9 step 5 | 运行期 StructuredValidationError |

为什么不把 backend 校验全 mirror 一份到前端：

- 大部分 validate_selection 规则需要读取 `ModelRegistry` 的细节（如 `getattr(spec, "type", None) == "think"`），前端拿到的 `BackendInfo` 投影**故意**不含 spec 细节（SSRF/credential 边界，详见 EXTENSIBILITY_SPEC §4.4 T2）
- 重写一份"前端 mirror" 会形成两份不一致的实现（runner 升级时前端忘改 = 误报或漏报），违反 SSOT
- 运行期错误已经走 panel 红字提示，UX 损失只是"用户点 run 才看到"而非"用户配置时立刻看到"

未来若加 `/parallel-ensemble/validate` 端点，`use-config.ts` 加 `useDebounce(ensemble, 500)` + 一个 `useQuery` 调它即可，UI 渲染逻辑不变。

##### 5. `import-model-info-button.tsx` 仅读 `id` 字段，丢弃数显式上报

`model_info.json`（PN.py 遗产）含 `url` / `api_key` / `EOS` / `stop_think` 等字段。
本按钮**只**取 `id`，其他字段在 import 时就被丢弃；这是 SSRF/credential 边界向 import 路径的延伸。即使用户复制粘贴一份带凭据的 json 也不会进 DSL。

未匹配注册表的 alias 数量 toast 出来（"已导入 X 个；丢弃 Y 个"），让用户知道为什么有些条目没出现 —— 沉默丢弃会让用户以为 import 卡住或文件错。

##### 6. 双语 DiagnosticsConfig 表单专用而非走 `dynamic-config-form`

DiagnosticsConfig 在 `entities.py` 上是节点级配置（`ParallelEnsembleConfig.diagnostics`），不在 runner / aggregator SPI ui_schema 里 —— 它的 i18n 键根 `nodes.parallelEnsemble.diagnostics.*` 是面板自己拥有的命名空间，不依赖某个 runner 的 `i18n_key_prefix`。直接复用 dynamic-config-form 反而需要造一份"假 ui_schema" 喂给它，反过来污染白名单契约。专用表单 70 行，反射通用方案 30 行 + 假 schema 60 行，两者复杂度近似但"专用"更直观。

##### 7. `node.tsx` 在画布上显示 runner 翻译名而非 raw `runner_name`

```tsx
{t(`parallelEnsemble.runners.${runnerName}.name`, { ns: 'workflow', defaultValue: runnerName })}
```

`defaultValue` fallback 让未注册 i18n key 的第三方 runner（OQ-2 fallback 场景）继续显示 raw `runner_name` 而不是空白；与 `RunnerSelector.renderLabel` 的 fallback 行为一致，画布缩略和面板下拉同名。

##### 8. `default.ts` 的 `defaultValue.ensemble.runner_name = 'response_level'`

不选 token_step 作默认是为了**让节点开箱可用**：

- response_level 是 P2.6.5 落地的"P1 响应级聚合迁移到 SPI"分支，required_capabilities 是空集，**任何 backend** 都能跑
- token_step 要求 TOKEN_STEP + TOP_PROBS，目前只有 llama_cpp 后端满足，新装 Dify 实例若没配 llama.cpp endpoint 节点会启动期失败
- 用户从画布拖出节点 → 选两个 backend → 直接能跑 → 想用 token 级再切换 runner，是更合理的发现路径

`aggregator_name = 'majority_vote'` 同理：scope=response 默认，跟 default runner 配对。

#### DSL 偷渡防护链路

`checkValid` 同时实施三条 mirror 防护（与 backend 的 `entities.py` 三层防护对应）：

| 层 | backend 实现 | 前端 mirror |
|---|---|---|
| 顶层 5 字段名单 | `ParallelEnsembleNodeData._reject_sensitive_top_level_fields`（`mode="before"` 黑名单） | `default.ts checkValid` 扫 `ensemble + runner_config + aggregator_config` 三处 keys，命中 5 名单之一即拒 |
| `ensemble.*` 业务字段 | `ParallelEnsembleConfig.model_config = ConfigDict(extra="forbid")` | TS 类型 `ParallelEnsembleConfig` 是封闭对象类型，`checkValid` 不再额外扫（TS 已经卡住）|
| `runner_config / aggregator_config` 内的非法 key | runner / aggregator 自己的 `config_class.model_config = ConfigDict(extra="forbid")` | 仅做 "must be plain object" 检查，具体 key allowlist 留给 backend（前端拿不到 config_schema 解析能力）|

为什么不在前端加完整 JSON Schema validator：bring 一个 ajv-style 库进来增加 bundle ~50KB，回报是仅在用户**手动编辑导入的 DSL**时多一层提示——服务器 validator 仍是最终防线，重复一份净增维护成本。

#### 与 P1.6（ensemble-aggregator）的差异点

| 维度 | P1.6 ensemble-aggregator | P2.11 parallel-ensemble |
|---|---|---|
| 节点 data 结构 | 扁平：`inputs / strategy_name / strategy_config` | 嵌套：`ensemble: { ... }`（SSRF 边界） |
| 协作策略来源 | 硬编码两种（`majority_vote / concat`） | 动态从 `RunnerRegistry` 拉 |
| 聚合策略来源 | 同硬编码 | 动态从 `AggregatorRegistry` 拉，按 scope 过滤 |
| ui_schema | 写死在 `strategy-selector.tsx` 内的两个 if 分支 | 反射 `runner.ui_schema` / `aggregator.ui_schema`，控件白名单 7 项 |
| API 端点依赖 | 0 | 3 GET（`local-models / runners / aggregators`） |
| i18n 数量 | 56 keys × 2 locales | 94 keys × 2 locales |
| diagnostics | 没有 | 9 字段表单 |
| 复数 i18n（_one / _other）| 1 个（inputCount）| 2 个（modelCount / modelsSelectedCount）|

P1.6 的"配置项受限但全在前端"vs P2.11 的"配置项三轴无限扩展但需要后端注册"是**有意的复杂度梯度**。第三方加新 runner / aggregator 不需要碰前端代码：

1. 在 `parallel_ensemble/runners/<my_runner>.py` 注册 + 写 i18n_key_prefix
2. 在 en-US + zh-Hans workflow.json 加 `<prefix>.{name,description,fields.<>...}` 两套
3. 完成 — 前端 `RunnerSelector` 自动列出，`DynamicConfigForm` 自动反射 ui_schema

如果第二步漏了 i18n，OQ-2 fallback 会在控件位置渲染 raw key + console.warn —— 静默错误被显式化。

#### 验证

##### JSON 解析

```bash
python3 -c "
import json
en = json.load(open('web/i18n/en-US/workflow.json'))
zh = json.load(open('web/i18n/zh-Hans/workflow.json'))
print('en valid; zh valid')
en_keys = {k for k in en if 'parallelEnsemble' in k or 'parallel-ensemble' in k}
zh_keys = {k for k in zh if 'parallelEnsemble' in k or 'parallel-ensemble' in k}
print('en parallel-keys:', len(en_keys))
print('zh parallel-keys:', len(zh_keys))
print('symmetric:', en_keys == zh_keys)
"
# en valid; zh valid
# en parallel-keys: 94
# zh parallel-keys: 94
# symmetric: True
```

##### 9 处注册全数到位

```bash
grep -n "ParallelEnsemble\|parallel-ensemble" \
  web/app/components/workflow/types.ts \
  web/app/components/workflow/block-selector/constants.tsx \
  web/app/components/workflow/nodes/components.ts \
  web/app/components/workflow/block-icon.tsx \
  web/app/components/workflow/constants.ts \
  web/app/components/workflow/utils/workflow.ts \
  web/app/components/workflow/constants/node.ts \
  web/app/components/workflow/nodes/_base/components/workflow-panel/last-run/use-last-run.ts \
  web/app/components/workflow/nodes/_base/components/variable/utils.ts
```

13 行命中（types.ts × 1 + BLOCKS × 1 + components.ts × 4 + block-icon × 2 + constants × 1 + workflow utils × 1 + constants/node × 1 + use-last-run × 2 + variable utils × 1）。

##### 后端无回归

本任务**零后端代码改动**：

```bash
git status -s api/  # 应为空
git diff --name-only api/  # 应为空
```

P2.10 的 243 / 243 测试基线不动。

#### 已知 follow-up

- **P2.12 前端质量门**：`web/node_modules` 在本工作目录缺失（同 P1.6 → P1.7 模式）；P2.12 是"`pnpm install` + `pnpm type-check:tsgo` + `pnpm lint:fix` + 7 spec 文件的 vitest 单测"专项，本次落地代码已按 P1.6 / P1.7 验证过的模式编写（`'use client'` directive、relative import 顺序、`React.memo` 包装），TS 报错预期局限于 `Var.type` 枚举集合或 InputProps 的轻微不匹配，专项跑时定位即可。
- **P2.13 / P2.14 联调**：本任务的"静态 ValidationIssue"无法替代真 dev server + 真 llama.cpp endpoint 的端到端验证（浏览器流式渲染、首 token 延迟、token / s 对比 PN.py），且 `validate_requirements` API 是否要补也在 P2.13 联调时根据用户体感决定。
- **P2.15 SSRF + Trace boundary**：`checkValid` 已经拦顶层 5 字段名单，但"DSL 顶层是合法 alias 但 yaml 没那条 alias"必须由 §9 startup pipeline 抛 `UnknownModelAliasError` —— 那是 `ParallelEnsembleNode._instantiate_backends` 的契约，本任务的前端 checkValid 拿不到 yaml 注册表内容，无法 mirror。P2.15 验证脚本应该包含"前端 panel 拒绝 + 后端启动期拒绝" 双层确认。
- **P3.3 i18n 全量 review**：本任务只覆盖 en-US / zh-Hans 两套（CLAUDE.md `web/i18n/en-US/` 强制要求覆盖）；其它 22 种语言在 P3.3 才扫，OQ-2 fallback（缺 key 显示 raw key + console.warn）保证非中英用户在那之前界面仍可用。
- **第三方 runner / aggregator 注册指南**：可以在 `EXTENSION_GUIDE.md` 加一节"在前端不动一行代码的前提下加新 runner"——先 register、再补两套 i18n、刷新页面即可生效。本任务暂未触及该文档，留 P3.2 撰写 README + EXTENSION_GUIDE 时一并加。


---

### P2.12 - P2.12 Landing — 前端质量门：TS + lint + 三轴下拉 + DiagnosticsConfig + import-button mock-API 单测

> Source shard: `P2.12_LANDING.md`


日期：2026-04-29

#### 范围

把 P2.11 在 `web/node_modules` 缺失下未跑过的三道质量门补齐：

1. **`pnpm type-check:tsgo`** — 全量过；并修掉 P2.11 留下的 9 处 TS 报错
2. **`pnpm eslint --fix`** — `parallel-ensemble` 子树 0 errors / 0 warnings；并修掉 P2.11 留下的 5 处 lint warning
3. **8 份 spec.tsx 单测** — 75 cases，覆盖三轴下拉 + DynamicConfigForm 反射 + DiagnosticsConfig 边界 + ImportModelInfoButton SSRF 边界 + Panel 三轴编排 + useConfig 静态校验

#### review round 1 修订（2026-04-29）

外部 reviewer 指出 1 处可即修风险（另两处归 Phase 4 / 已记录），已修复：

| # | 问题 | 文件 | 修复 |
|---|---|---|---|
| 1 | `panel.tsx:166` 的 `ImportModelInfoButton` 只看 `readOnly` —— 模型注册表还在 loading 时仍可点；此时 `knownAliases === []`，导入会误报 "noneMatched" | `components/import-model-info-button.tsx`（新增 `isLoading?: boolean` prop，按钮 `disabled={readonly \|\| isLoading}`）+ `panel.tsx:167` 多传 `isLoading={isLoadingModels}` | 单测 +2：`import-button.spec.tsx` 加 "disables the button while the model registry is loading"，`panel.spec.tsx` 加 "disables the import button while the model registry is loading"（panel 级 wiring 校验）|
| 2（推迟）| `dynamic-config-form.tsx` 的 select / multi_select 把 numeric option value 字符串化，与 `UiFieldSchema.options?.value: string \| number` 契约不完全一致 | — | 当前 shipped runner（response_level / token_step）都没用 numeric select，不挡 P2.12；归 Phase 4 SPI 增量一起做（dispatch 时按 `options[i].value` 运行期类型回填）|
| 3（已记录）| `model_alias_select` 为占位提示 | — | 已在 `dynamic-config-form.tsx` 注释里说明 v0.2 暂未 plumb；等真有 runner 用 `judge_alias` 二级别名时再 wiring，无 shipped 用户 |

**不做**（按 TASKS.md 切片）：
- workflow / chat 模式 dev server 联调（P2.13 / P2.14）
- 性能基准 + SSRF 抗压 + Trace 大小 boundary（P2.15）

#### P2.11 落地后才发现的 9 处 TS 报错

P2.11 写盘时本地 `web/node_modules` 已经清掉，type-check 没在那个 PR 跑过。本次先 `pnpm install` 起来后跑 `tsgo`，捞出 9 处需要修的位置，全部归到本次：

| # | 文件 | 问题 | 修复 |
|---|---|---|---|
| 1 | `panel.tsx:167` | `Field` 的 `children?: JSX.Element \| string \| null` 拒绝两个并列 children（`<ModelSelector />` + `{renderIssue('model_aliases')}`）—— TS 推断为 `JSX.Element[]` | 用 `<>...</>` Fragment 包住两个 children，结果是单个 `JSX.Element` |
| 2 | `panel.tsx:213` | 同上，`AggregatorSelector` + `renderIssue('aggregator_name')` | 同上 |
| 3-5 | `import-model-info-button.tsx:73 / 83 / 93` | `toast.success({message: ...})` / `toast.error({message: ...})` —— dify-ui `ToastApi` 签名是 `(title: ReactNode, options?)`，第一参是 title 不是 options-with-message | 改为 `toast.error(t('...'))` / `toast.success(t('...'))` |
| 6 | `use-config.ts:30` | `runnersQuery.data?.runners ?? []` 经 oRPC `type<{ runners: RunnerMeta[] }>()` 后内部 `options` 字段被推为 `unknown`，与 `RunnerMeta.UiFieldSchema.options` 不兼容 | 用 `as ReadonlyArray<RunnerMeta>` 显式收紧；契约本身仍由 `contract/console/parallel-ensemble.ts` 钉住 wire schema |
| 7 | `use-config.ts:34` | 同上 `aggregators` | 同上 |
| 8 | `panel.tsx:175` | 同 #1（fragment 修复后顺带修正） | 同 #1 |
| 9 | `panel.tsx:221` | 同 #2 | 同 #2 |

修复后 `pnpm type-check:tsgo` 全量 0 错。

#### P2.11 落地后才发现的 5 处 lint warning

`pnpm eslint --fix` 跑一遍：

| # | 文件 | 问题 | 修复 |
|---|---|---|---|
| 1 | `panel.tsx:82` | `existingAliases = ensemble?.model_aliases ?? []` 是 logical fallback —— 每次渲染产生新数组引用，让 `useCallback` deps 抖动（`react/exhaustive-deps`） | 用 `useMemo` 锁住引用，依赖 `ensemble?.model_aliases` |
| 2 | `panel.tsx:115` | `issues.map((issue, idx) => ... key={idx})` 用数组下标做 React key（`react/no-array-index-key`） | 改用 `${field}:${severity}:${i18n_key ?? message}` 复合 key |
| 3 | `use-config.ts:62` | `aliases = inputs.ensemble?.model_aliases ?? []` 同 #1，污染 `validationIssues` useMemo | 同 #1 |
| 4 | `dynamic-config-form.tsx:62` | `border-state-warning-border` 不在 `tailwind-theme-var-define.ts` 里（不存在的 token） | 改成 `border-components-panel-border`（有定义），保留 `bg-state-warning-hover-alt` + `text-text-warning-secondary` 的视觉语义 |
| 5 | `dynamic-config-form.tsx:210` | `bg-components-panel-bg-subtle` 不存在 | 改成 `bg-components-panel-bg-alt`（最接近的有定义 token） |

修复后 `pnpm eslint --concurrency=auto --cache app/components/workflow/nodes/parallel-ensemble` 输出空（0 errors / 0 warnings）。

#### 8 份 spec.tsx + 73 cases

测试组织遵循 `web/docs/test.md` + `frontend-testing` skill：每个组件 / hook 一个 spec，sibling `__tests__/` 目录，AAA 结构，按行为而非实现细节断言。

```
web/app/components/workflow/nodes/parallel-ensemble/
├── __tests__/
│   ├── panel.spec.tsx                  # 14 cases — 三轴编排 + 路由 + 折叠 diagnostics + trace 输出条件
│   └── requirements-validation.spec.tsx# 7 cases — useConfig 静态校验 + Panel renderIssue 路由
└── components/__tests__/
    ├── model-selector.spec.tsx         # 10 cases — capability filter + tooltip + 选择互斥
    ├── runner-selector.spec.tsx        # 7 cases  — i18n 标签 + 描述 + 重选无副作用
    ├── aggregator-selector.spec.tsx    # 8 cases  — scope 过滤 + 占位 / loading / readonly
    ├── dynamic-config-form.spec.tsx    # 10 cases — 7 种白名单控件 + 非白名单 alert + 各控件 dispatch
    ├── diagnostics-config.spec.tsx     # 8 cases  — 7 switch + max_trace_tokens 边界 + storage allowlist
    └── import-button.spec.tsx          # 9 cases  — id-only 抽取 + SSRF 边界 + 解析失败 toast + 重选清值
```

##### 关键测试覆盖（按 TASKS.md P2.12 子项对照）

| TASKS.md 子项 | spec | 命中 case |
|---|---|---|
| `panel.test.tsx`：渲染所有配置项 + 三轴 selector | `__tests__/panel.spec.tsx` | "renders all configuration sections for a populated payload" + 路由组（5 case）|
| `model-selector.test.tsx`：mock `/local-models` API + 选 token_step runner，断言 anthropic backend 的模型被过滤掉 | `components/__tests__/model-selector.spec.tsx` | "Capability filtering — token_step runner" 4 case（greys / tooltip / 拒绝新选 / 允许已选去掉）|
| `runner-selector.test.tsx`：mock `/runners` API，渲染所有 runner + tooltip | `components/__tests__/runner-selector.spec.tsx` | "renders all runners with their i18n labels and descriptions" + 触发标签/占位 fallback |
| `aggregator-selector.test.tsx`：选 token_step 后只显示 scope=token 的 aggregator | `components/__tests__/aggregator-selector.spec.tsx` | "Scope filtering" 3 case（hide / show / 全空 disable）|
| `dynamic-config-form.test.tsx`：喂 ui_schema fixture（含全部 7 种白名单 + 一个非白名单），后者应渲染 fallback 错误 | `components/__tests__/dynamic-config-form.spec.tsx` | "Whitelisted controls (7)" 单测渲染所有 + "Unknown control fallback" 渲染 `role=alert` |
| `requirements-validation.test.tsx`：mock `/validate` API，断言 ValidationIssue 渲染到对应字段红框 + tooltip 文案 | `__tests__/requirements-validation.spec.tsx` | useConfig hook 测 6 case（capability / scope / 无 runner 跳过）+ Panel renderIssue 路由到 `model_aliases` / `aggregator_name` 字段 |
| `diagnostics-config.test.tsx`：改 storage 单选 → state 变化 → 持久化到 NodeData | `components/__tests__/diagnostics-config.spec.tsx` | "Storage select — P2.12 spec" 2 case（switch + 拒绝非 allowlist）|
| `import-button.test.tsx`：喂 `model_info.json` fixture，仅 id 字段被勾选 | `components/__tests__/import-button.spec.tsx` | "Parsing — id-only surface" 3 case（matched / dropped / count toast）+ SSRF 字段（url / api_key / api_key_env / EOS / stop_think）静默忽略 |

##### 范围调整 vs spec

spec 第 6 项写"mock `/validate` API"，**当前后端没有 `/validate` 端点**（P2.11 spec → 落地差异里已经记录，§9 startup pipeline 在运行期做完整校验，前端只镜像可静态复算的两条规则）。本次 `requirements-validation.spec.tsx` 的实现：

- 用 `renderHook(() => useConfig(...))` 直接驱动**真实** `useConfig` 计算 ValidationIssue，给 6 个组合 case：capability mismatch / 不需要 capability / 别名未注册（跳过）/ scope mismatch / scope match / 无 runner（跳过）
- 用 `render(<Panel />)` 把 ValidationIssue 通过实际 `renderIssue` 路径渲染出来，断言 `text-text-warning-secondary` token 出现在对应字段下（`model_aliases` 字段下出现 capability 错；`aggregator_name` 字段下出现 scope 错）

未来 P2.13 / P3 加 `/parallel-ensemble/validate` 端点时，把这两个 case 换成 mock fetch 即可，UI 路径不变。

##### 与 P2.11 fix #4（闭名单）的关系

P2.11 review round 1 fix #4 把"`response_level / token_step` 至少 2 个 alias"放到 `default.ts` 的 `checkValid` 里（前端静态校验，不依赖 RunnerMeta 字段）。这个分支由保存时的 `checkValid` 调用，**不**走 `useConfig.validationIssues` 的 in-panel 实时通道，所以本次 spec 没有覆盖（`default.ts` 的 `checkValid` 由 graphon 保存路径触发，单测应在 `default.ts` 的兄弟 spec —— 那是 P3.1 集成测试 / 后续 unit 的事）。

#### 测试基础设施补丁

部分单测要 mock 的对象在 dify-ui 是 Radix Portal 的 trigger / content 拆开三件套，happy-dom 没 portal mount。三个共用的 mock pattern：

1. **`@langgenius/dify-ui/dropdown-menu`**（model / runner / aggregator selector 共享）：内部用 `React.createContext` 跨 trigger / content 同步 `open` 状态，trigger 渲染为 `<button>`，content 仅在 `open` 时渲染，item 渲染为 `<div role="menuitem">` 让 `fireEvent.click` 能命中
2. **`@langgenius/dify-ui/tooltip`**（model-selector）：把 `Tooltip / TooltipTrigger / TooltipContent` 全部展开为 inline 渲染，`TooltipContent` 加 `role="tooltip"` 让测试可查
3. **`@langgenius/dify-ui/switch`**（dynamic-config-form / diagnostics-config）：渲染为 `<button role="switch">`，点击翻转 checked 调 `onCheckedChange`

panel 测试因为是组合层，全用 `vi.mock('../use-config')` 注入 `mockUseConfig` + 7 个 sibling 组件 stub，专测路由（哪个子组件回调对应哪个 handler 触发）。requirements-validation 是反过来：保留真 `useConfig` + 真 `panel`，只 mock `./use-registries` 来注入注册表。

#### 验证

```sh
cd web

# 1. 类型门
pnpm type-check:tsgo
# → 0 errors

# 2. lint 门
pnpm eslint --concurrency=auto --cache --fix app/components/workflow/nodes/parallel-ensemble
# → 0 errors / 0 warnings

# 3. 单测门
pnpm test app/components/workflow/nodes/parallel-ensemble
# → Test Files 8 passed (8); Tests 73 passed (73)
```

#### 文件清单

```
新增 8 份测试 + 1 份 doc
web/app/components/workflow/nodes/parallel-ensemble/__tests__/
├── panel.spec.tsx
└── requirements-validation.spec.tsx

web/app/components/workflow/nodes/parallel-ensemble/components/__tests__/
├── aggregator-selector.spec.tsx
├── diagnostics-config.spec.tsx
├── dynamic-config-form.spec.tsx
├── import-button.spec.tsx
├── model-selector.spec.tsx
└── runner-selector.spec.tsx

docs/ModelNet/P2.12_LANDING.md
```

```
修改（修 P2.11 留下的 TS / lint 问题）
web/app/components/workflow/nodes/parallel-ensemble/
├── panel.tsx                               # Fragment 包两处 Field children；useMemo 锁 existingAliases；issue 复合 key
├── use-config.ts                           # as 收紧 oRPC 推断；useMemo 锁 aliases
├── components/import-model-info-button.tsx # toast.success/error 改 (title) 签名
└── components/dynamic-config-form.tsx      # 两处 tailwind class 换成定义过的 token
```


---

## Phase 3.A - Response aggregation weighted upgrade

### P3.A.1 - P3.A.1 Landing — ensemble_aggregator 后端升级 + ADR-v3-8 SPI 切分

> Source shard: `P3.A.1_LANDING.md`


日期：2026-04-30

#### 范围

v3 升级阶段第 1 个**实现性**落地任务（P3.0 是文档钩子）。两件事：

1. **`ensemble_aggregator` 升级为 response 模式参考实现**：`AggregationInputRef`
   加 `weight`（静态 float 或动态 `VariableSelector`）/ `fallback_weight` / `extra`；
   策略侧 `majority_vote` 接权重做加权多数 + `concat` 加 `order_by_weight` +
   新增 `weighted_majority_vote` 作为 SPI 扩展示例
2. **ADR-v3-8 SPI context 切分提前到 A.1 落地**：
   `parallel_ensemble.spi.aggregator` 切成 `SourceAggregationContext`（sources /
   weights / source_meta / strategy_config）+ `BackendAggregationContext`（继承
   前者再追加 backends / capabilities / runner_name / runner_config / trace /
   elapsed_ms_so_far / step_index）。`ResponseAggregator` 仅消费前者，
   `TokenAggregator` 消费后者 —— response 策略永远看不到 backend / runner 内部字段

依赖：P3.0（v3 计划文档钩子，已落地）
对齐 ADR：v3-1 / v3-6 / v3-7 / v3-8 / v3-9（SPI 隔离）/ v3-13 / v3-15

#### 不做（按 v3 计划切片）

- 前端 `panel.tsx` / `input-list.tsx` 行内 weight 输入框：P3.A.2
- `weighted_majority_vote` 前端 ui_schema 反射 + i18n：P3.A.2
- 后端测试翻译完整版（dynamic weight 三分支 + weighted_majority_vote 完整覆盖 +
  Rv3-9 SPI 隔离回归）：P3.A.3 —— A.1 已落地基本骨架（24 net new cases），
  A.3 把 spec 里没补完的几个 corner 点（如 weighted_majority_vote 单边强权）
  写到位
- `parallel_ensemble.runners.response_level` 删除：P3.B.0（同时删
  `AggregationContext = BackendAggregationContext` 别名）
- `parallel_ensemble` 重定位 + `token-model-source` 节点：P3.B.* / P3.C.*

#### 1. `entities.py` — `AggregationInputRef` 三个新字段

```python
class AggregationInputRef(BaseModel):
    source_id: str
    variable_selector: list[str]                     # 既有
    weight: float | list[str] = 1.0                  # 新：静态 float 或 VariableSelector list
    fallback_weight: float | None = None             # 新：None=fail-fast / 数=优雅降级
    extra: dict[str, Any] = Field(default_factory=dict)  # 新：透传到 source_meta
```

##### `mode="before"` validator 防的三类静默强转 / 污染

| 类型 | 风险 | 处理 |
|---|---|---|
| `bool` | `True` / `False` 是 `int` 子类，pydantic 默认会硬塞成 `1.0` / `0.0`，DSL typo（写成 `weight: true`）会被静默接受 | `_weight_selector_well_formed` 显式 `isinstance(v, bool)` 先拦截，报错说明"bool is an int subclass and would coerce silently" |
| `NaN` / `±Inf` | 加权多数 / 加权和直接被毒化（NaN 算什么都还是 NaN，Inf 永远赢） | `math.isfinite(f)` 拒掉，错误信息含具体非有限值 |
| 残缺 selector list | 跑到 `variable_pool.get` 才挂，错误难定位 | 同 `variable_selector` 一样要求 `len ≥ 2` + 每段非空非空白 |

`fallback_weight` 走同一套有限性 + bool 防护。Review fix（提交前自查）：原版只在静态
分支查 NaN，动态 selector 解析回来的值在 `_resolve_weight` 里二次查；validator 这层
只能管 schema 端的输入，运行期解析失败由 `WeightResolutionError` 接管。

`strategy_name` literal 同步从 2 个扩到 3 个：`majority_vote` / `concat` /
`weighted_majority_vote`。

#### 2. `exceptions.py` — `WeightResolutionError`

```python
class WeightResolutionError(EnsembleAggregatorNodeError):
    def __init__(self, input_id: str, selector: list[str], reason: str): ...
```

ADR-v3-15 fail-fast 默认：动态 weight 解析失败抛此异常 → 节点 `FAILED`。
**不**做 silent fallback 到 1.0（论文里 weight=0.7/0.3 会被悄悄跑成 1.0/1.0
是研究 fork 不能容忍的）。用户要容错必须显式声明 `fallback_weight`。

`reason` 三种：`variable not present in pool` / `resolved value is None` /
`resolved value is not numeric (got <type>)` / `resolved value is not finite (got <value>)`。

#### 3. `node.py` — `_collect_inputs` + `_resolve_weight`

`_collect_inputs` 返回 4-元组：`(signals, weights, source_meta, weight_fallbacks)`。

```python
def _collect_inputs(self) -> tuple[
    list[ResponseSignal],          # 给策略的 SignalT
    dict[str, float],              # SourceAggregationContext.weights
    dict[str, dict],               # SourceAggregationContext.source_meta
    list[dict[str, Any]],          # process_data["weight_fallback_warnings"]
]: ...
```

变化点：

1. **从 `AggregationInput` TypedDict 切到 `ResponseSignal` TypedDict**（来自
   `parallel_ensemble.spi.aggregator`）—— 同一棵 SPI 树，response 模式两节点共享
2. **strategy_config 集中校验**：原版每个策略类内部 `model_validate`，现在改在
   `node.py::_run` 统一 `strategy.config_class.model_validate` 后传 typed config
   给 `aggregate(signals, context, config)`；策略类不再各自 `try/except ValidationError`
3. **`SourceAggregationContext` 仅含 4 个字段**（sources / weights / source_meta /
   strategy_config），不含 backends / capabilities / runner_name —— 因为
   ensemble_aggregator 的上游是 HTTP / Code / Agent / 任意 text 节点，根本
   不存在 backend 概念（ADR-v3-8）

##### `_resolve_weight`：静态 / 动态 / fallback 三分支

```
ref.weight: float | int → 直接返回 float()，validator 已挡 bool/NaN/Inf
ref.weight: list[str]   → variable_pool.get(selector)
                          ├─ None / value=None / 非数值 / bool / 非有限 → WeightResolutionError
                          │      ├─ ref.fallback_weight is None: 抛出，节点 FAILED
                          │      └─ ref.fallback_weight 有值：log.warning + append 到
                          │         weight_fallbacks，返回 fallback 值
                          └─ 数值且有限：返回 float(value)
```

##### `weight_fallback_warnings` 写到 `process_data` 而非 `inputs`

Review fix（落地中自我修订）：第一版我把 fallback 记录塞在 `inputs.weight_fallback_warnings`，
但 `inputs` 是节点**入参快照**，graphon UI 把它渲染成"调用参数"区块，
fallback 事件本质是**运行时 trace 等价物**，应在 trace 通道；本节点没有
`TraceCollector`（response 模式无 step trace），graphon 给非 trace 节点的
等价 surface 是 `NodeRunResult.process_data` —— 单步调试面板的 "process data"
区块独立可见。

```python
process_data: dict[str, Any] = {}
if weight_fallbacks:
    process_data["weight_fallback_warnings"] = weight_fallbacks
yield StreamCompletedEvent(
    node_run_result=NodeRunResult(
        ...
        inputs={"source_count": ..., "strategy": ...},
        process_data=process_data,                  # ← 这里
        outputs={"text": ..., "metadata": ...},
    ),
)
```

##### `_extract_variable_selector_to_variable_mapping` 暴露动态 weight selector

`workflow_entry` 启动期会预读所有节点 mapping 把变量预加载进 pool。原版只暴露
`variable_selector`，现在追加暴露 `weight: list[str]` 分支：

```python
mapping[f"{node_id}.inputs.{ref.source_id}"] = list(ref.variable_selector)
if isinstance(ref.weight, list):
    mapping[f"{node_id}.inputs.{ref.source_id}.weight"] = list(ref.weight)
```

#### 4. `parallel_ensemble.spi.aggregator` — ADR-v3-8 切分

| 层 | 字段 | 谁能看到 |
|---|---|---|
| `SourceAggregationContext` | `sources` / `weights` / `source_meta` / `strategy_config` | **所有** aggregator（response + token） |
| `BackendAggregationContext(SourceAggregationContext)` | + `backends` / `capabilities` / `runner_name` / `runner_config` / `trace` / `elapsed_ms_so_far` / `step_index` | **仅** `TokenAggregator` |

`Aggregator` 泛型从三参（`ConfigT` / `SignalT` / `ResultT`）扩到四参，加 `ContextT`：

```python
class Aggregator[
    ConfigT: BaseModel,
    SignalT,
    ResultT,
    ContextT: SourceAggregationContext,
](ABC):
    @abstractmethod
    def aggregate(self, signals: SignalT, context: ContextT, config: ConfigT) -> ResultT: ...
```

- `ResponseAggregator(...ContextT=SourceAggregationContext)` —— `ensemble_aggregator`
  的上游是 HTTP/Code/Agent/任意 text 节点，response 策略不该被迫感知 backend /
  runner 字段
- `TokenAggregator(...ContextT=BackendAggregationContext)` —— PN.py 风格 token
  aggregator 真的需要 backend.instance_capabilities 来 gate candidate

##### back-compat 别名 `AggregationContext = BackendAggregationContext`

P3.B.0 删；现阶段保留是因为：

1. `parallel_ensemble.runners.response_level` 还在（A.1 不删它，B.0 删整个 runner）
2. `parallel_ensemble.aggregators.{response,token}/*` 老 import 旧名
3. `runners/{response_level,token_step}.py` 构造 ctx 时改用 `BackendAggregationContext`
   显式名（向 B.0 靠拢），别名只服务 import 兼容

#### 5. 策略改造

##### `majority_vote` — v2.4 行为兼容 + 加权分支

```python
weighted_votes[s["text"]] += weights.get(s["source_id"], 1.0)
all_unit = all(math.isclose(w, 1.0) for w in weights.values())
votes_payload = {t: (int(c) if all_unit else c) for t, c in weighted_votes.items()}
metadata = {
    "votes": votes_payload,
    "winner_votes": int(max_score) if all_unit else max_score,
    "weighted": not all_unit,           # 前端可据此切换 metadata viewer
    ...
}
```

- 全 1 权重：`votes` 是 `dict[str, int]`、`weighted=False` —— 与 v2.4 输出**逐字节一致**
- 非 1 权重：`votes` 是 `dict[str, float]`、`weighted=True` —— 加权和

Tie-break 算法（lex-smallest voting source_id）原封保留 —— v2.4 DSL 测试钉死了
特定 tie 配置下的 winner，不能改。

##### `concat` — `order_by_weight` 默认 off

```python
if config.order_by_weight:
    ordered.sort(key=lambda s: -weights.get(s["source_id"], 1.0))   # stable, 降序
```

默认 `False` 时输出顺序匹配 declared `inputs`，v2.4 行为字节级一致。

##### `weighted_majority_vote` — 全新 SPI 扩展示例

放在 `strategies/weighted_majority_vote.py`，与 `majority_vote` 唯一区别：
**总是**走加权和路径，即便 weight 全 1（输出 `weighted` metadata 不掩盖、不退化）。
作为外部贡献者写自定义策略的 reference impl —— 仅依赖
`ResponseAggregator` + `SourceAggregationContext` 公开 surface，无任何
backend / runner 依赖。

Tie-break 与 `majority_vote` 一致（lex-smallest voter source_id），DSL 改策略名
而保留 inputs 不变时 winner 行为可预期。

##### `registry.py` — `list_strategies()` 改造

返回 `[{name, config_schema, ui_schema}]`，`config_schema` 是 pydantic
`model_json_schema()` 自动生成（A.2 前端 fallback 反射用），`ui_schema` 是策略类
显式声明（A.2 优先用这个），原 v2.4 的手写 `config_schema: dict` 字段删除。

#### 6. 老类型清理（ADR-v3-9 SPI 收敛）

`strategies/base.py` 改成纯 re-export：

```python
from core.workflow.nodes.parallel_ensemble.spi.aggregator import (
    ResponseAggregationResult, ResponseAggregator,
    ResponseSignal, SourceAggregationContext,
)
```

删掉的旧类型：

- `AggregationStrategy(ABC)` —— 由 `ResponseAggregator` 替代
- `AggregationInput: TypedDict` —— 由 `ResponseSignal: TypedDict` 替代
  （`ResponseSignal` 多了 `finish_reason` / `elapsed_ms` / `error` —— 同一棵
  SPI 树，从 ensemble_aggregator 港口移植到 parallel_ensemble 港口的策略 import 不变）
- `AggregationResult: TypedDict` —— 由 `ResponseAggregationResult: TypedDict` 替代

ADR-v3-13 决策：v2.4 DSL 不向上兼容，研究 fork 阶段无生产 DSL 需要保护。`strategy_name`
literal 收紧为 `Literal["majority_vote", "concat", "weighted_majority_vote"]`，
旧 DSL `strategy_name="<typo>"` 自然 `ValidationError`。

#### 测试

236 通过，+24 净新（A.1 落地基本骨架；A.3 补完整覆盖）。

```
api/tests/unit_tests/core/workflow/nodes/ensemble_aggregator/
├── test_entities.py    # +12 cases — weight/fallback finite 三分支（bool/NaN/Inf）/
│                       #              extra 透传 / weighted_majority_vote literal
├── test_strategies.py  # +24 cases — 3 策略 weighted/unit 行为 + Rv3-9 SPI 隔离回归
└── test_node.py        # +8  cases — 动态 weight 三分支（成功 / 缺变量 fail-fast /
                                       非数值 fail-fast）/ fallback 入 process_data /
                                       静态 weight / source_meta / extract mapping
```

`api/tests/unit_tests/core/workflow/nodes/parallel_ensemble/aggregators/conftest.py`
fixture 加 `sources` / `source_meta` / `strategy_config` 默认值（向后兼容老
token aggregator 测试）。

#### 验证

```sh
cd api
uv run pytest tests/unit_tests/core/workflow/nodes/ensemble_aggregator/ -q
# → 236 passed

uv run pytest tests/unit_tests/core/workflow/nodes/parallel_ensemble/ -q
# → 全套绿（response_level / token_step / aggregators / 既有 P2.10 单测）

uv run ruff check core/workflow/nodes/ensemble_aggregator/ \
                  core/workflow/nodes/parallel_ensemble/spi/
# → All checks passed
```

#### 文件清单

```
新增
api/core/workflow/nodes/ensemble_aggregator/strategies/weighted_majority_vote.py
api/tests/unit_tests/core/workflow/nodes/ensemble_aggregator/test_entities.py
api/tests/unit_tests/core/workflow/nodes/ensemble_aggregator/test_node.py
docs/ModelNet/P3.A.1_LANDING.md

修改（ensemble_aggregator）
api/core/workflow/nodes/ensemble_aggregator/
├── entities.py           # +weight/fallback_weight/extra + finite validator + literal 扩 3
├── exceptions.py         # +WeightResolutionError
├── node.py               # _collect_inputs 4-元组 / _resolve_weight / process_data 写 fallback
└── strategies/
    ├── __init__.py       # 导出 SPI re-export 名
    ├── base.py           # 纯 re-export 自 parallel_ensemble.spi.aggregator
    ├── concat.py         # +order_by_weight + ResponseAggregator 继承
    ├── majority_vote.py  # 加权分支 + weighted metadata + v2.4 兼容
    └── registry.py       # _REGISTRY 类型 + list_strategies() 暴露 ui_schema

修改（parallel_ensemble — ADR-v3-8 SPI 切分）
api/core/workflow/nodes/parallel_ensemble/
├── spi/__init__.py                  # 导出 SourceAggregationContext / BackendAggregationContext
├── spi/aggregator.py                # context 切两层 + Aggregator 加 ContextT 泛型
├── runners/response_level.py        # ctx 改用 BackendAggregationContext + sources/source_meta
├── runners/token_step.py            # 同上
└── aggregators/{response,token}/*   # adapt 新 context 类型

修改（测试）
api/tests/unit_tests/core/workflow/nodes/ensemble_aggregator/test_strategies.py  # +24 cases
api/tests/unit_tests/core/workflow/nodes/parallel_ensemble/aggregators/conftest.py  # fixture 加默认

修改（文档）
docs/ModelNet/active/TASKS.md          # P3.A.1 标 ✅；进度从 P3.0 → P3.0+P3.A.1
docs/ModelNet/history/DEVELOPMENT_PLAN_v2.md      # §6 banner（P3.0 钩子，本次提交一起 ship）
docs/ModelNet/history/DEVELOPMENT_PLAN_v3.md   # P3.0 文档主体（v3.0.2，16 ADR + 9 风险登记）
docs/ModelNet/architecture/EXTENSIBILITY_SPEC.md    # §3 banner：response_level v3 删除 → ResponseAggregator SPI
```


---

### P3.A.2 - P3.A.2 Landing — ensemble_aggregator 前端升级（response 模式 weight + ui_schema 反射）

> Source shard: `P3.A.2_LANDING.md`


日期：2026-04-30

#### 范围

把 P3.A.1 后端落地的三件事映射到画布节点：

1. **`AggregationInputRef` 加 `weight` / `fallback_weight` / `extra`** —— 类型定义到位，
   `input-list.tsx` 行内多两个控件：weight（数值 ↔ 变量引用模式切换）+ fallback_weight
   （仅动态模式可见 + ADR-v3-15 fail-fast tooltip）
2. **`strategy_name` literal 扩到 3 个** —— 下拉里增 `weighted_majority_vote` 选项；
   `strategies.<name>.{label, description, hint}` i18n 全量补齐
3. **`ui_schema` 反射策略私有 config** —— 复用 P2.11 `parallel-ensemble/components/
   dynamic-config-form.tsx`，按 `ENSEMBLE_STRATEGY_META[name].ui_schema` 渲染。
   策略集闭、与本节点同包发布，`ui_schema` 在前端静态镜像（不再加新 console
   endpoint）；后端 `extra="forbid"` + `default.ts::allowedKeysByStrategy`
   双向对齐，任一侧加字段必须改另一侧。

依赖：P3.A.1（已落地）
对齐 ADR：v3-6（response 不带 top_k_override）/ v3-9（SPI 隔离）/ v3-15（fail-fast）

#### 不做（按 v3 计划切片）

- 后端测试翻译（dynamic weight 三分支 / weighted_majority_vote 完整 / Rv3-9 SPI 回归）：P3.A.3
- 前端单测（input-list + strategy-selector）：P3.A.3
- console endpoint `/workspaces/current/ensemble-strategies` —— 当前策略集闭、ui_schema
  与代码同包发布，加端点的运营复杂度 > 收益。第三方策略真要靠注册表注入时再加
  endpoint（届时同 parallel-ensemble.aggregators 路径走 oRPC 契约）

#### 变更清单

```
web/app/components/workflow/nodes/ensemble-aggregator/
├── types.ts                       # +weight / +fallback_weight / +extra；strategy 3 项；新增 ENSEMBLE_STRATEGY_META 静态镜像
├── default.ts                     # checkValid 增 weight / fallback_weight / extra / order_by_weight 四类校验；undefined 兼容 v2.4 DSL
├── use-config.ts                  # +handleWeightChange / +handleFallbackWeightChange / +filterNumericVar；handleAddInput 默认 weight=1, fallback=null, extra={}；handleStrategyConfigChange 改为 dynamic-config-form 兼容（接 ConfigBlob 全量）
├── panel.tsx                      # 透传 4 个新 props 给 InputList
├── components/
│   ├── input-list.tsx             # 行内 weight 模式切换（# / {x}）+ 数值输入 / 变量 picker；动态模式追加 fallback_weight 行 + Tooltip 解释 ADR-v3-15
│   └── strategy-selector.tsx      # 3 项下拉；hasSchema 分支换为 DynamicConfigForm；保留 hint 文案
web/i18n/{en-US,zh-Hans}/workflow.json
└── nodes.ensembleAggregator.*     # 删 5 个旧 strategies.concat.*（被 dynamic form 接管）；加 22 个新 keys（fields.* / weight / fallback / weighted_majority_vote / errorMsg）
```

零后端改动。零新文件。

#### 关键设计决策

##### D1: `ui_schema` 反射不走 console endpoint

P2.11 给 `parallel-ensemble` 三个 console endpoint（local-models / runners /
aggregators）是为了 **第三方** runner / aggregator 通过 `model_net.yaml` 注册时
前端不需要重启即可发现新 plugin。`ensemble_aggregator` 的 3 个策略不同：

- 都跟 node 同包发布、跟 `EnsembleStrategyName` literal 绑定（DSL 写到一起）
- 没有 yaml-driven 第三方扩展点（`registry.py` 只暴露 `register` 装饰器，不读
  yaml；新加策略要改本仓库源码）
- `ui_schema` 列表本身就是 3 行（majority_vote `{}` / concat 3 keys /
  weighted_majority_vote `{}`），抽到 endpoint 价值低

所以 `ENSEMBLE_STRATEGY_META` 在 `types.ts` 里静态镜像。漂移防护：

| 漂移方向 | 拦截层 |
|---|---|
| 前端加字段、后端没加 | 后端 `concat._ConcatConfig.model_config = ConfigDict(extra="forbid")` 在 `model_validate` 时抛 `StrategyConfigError` |
| 后端加字段、前端没加 | 前端 `default.ts::ALLOWED_KEYS_BY_STRATEGY` 闭名单，新字段没出现在 ui_schema 里 = 表单没法填 = 用户绝不会写到 strategy_config（DSL 导入时也走 `unknownStrategyConfigKey` 报错） |
| `i18n_key_prefix` 漂移 | dynamic-config-form 找不到 `<prefix>.fields.<f>.label` 时**返回原始 key** 当作降级（`defaultValue: labelKey`，P2.11 OQ-2 约定），QA 立刻能看到字段名暴露在 panel 上 |

未来真要支持第三方策略时，路径是：

1. `registry.py` 增加从 yaml / plugin manifest 加载的入口（同 `parallel_ensemble.AggregatorRegistry.discover`）
2. 加 `controllers/console/workspace/ensemble_strategies.py` + 契约 + hook
3. 把 `ENSEMBLE_STRATEGY_META` 从静态 const 换成 `useEnsembleStrategies()` 返回值

P3.A.2 不做这步。

##### D2: weight 模式切换器（# ↔ {x}）而非合并 picker

dify-ui 的 `VarReferencePicker` 支持 `isSupportConstantValue` 提供数值 / 变量两态切换。但
它只对 string 常量 + 文本变量原生友好，数值常量需要传 `schema.type === 'number'`，且
切换时输入框语义随上下文变化（ValueSelector 模式下 `onChange` 收 `[]`，常量模式下收
`'foo'`）。当前节点要的是"static `number` ↔ dynamic `ValueSelector`"严格二态：

- 静态分支：number input，emptied → 1（"unweighted"），无效 NaN/Inf 留空原状（client-side
  也走有限性 guard，跟 backend `_weight_selector_well_formed` 一致）
- 动态分支：`VarReferencePicker` 带 `filterNumericVar`（`number | any`），上游产出非数值类型
  的不在候选里
- 切换时整段重置（数 → `[]`、变量 → `1`），并清掉 `fallback_weight`（fallback 仅动态模式
  有意义，留着会让 panel 显示一个无效字段）

合并 picker 在 v0.2 不值得：节点已经是研究 fork 的二次开发面，UX 复杂度的边际成本 >
切换器的视觉额外成本。

##### D3: `handleStrategyConfigChange` 接全量 ConfigBlob

旧版 `handleStrategyConfigChange(patch: Partial<ConcatConfig>)` 走的是"叠加 patch +
显式删 undefined 键"。`DynamicConfigForm` 内部 `handlePatchKey` 已经做了这件事
（`undefined` → `delete merged[key]`，匹配 ensemble-aggregator's patch semantics
注释），onChange 出去的就是全量 `ConfigBlob`。所以 `use-config.ts` 这层简化为
直接整段覆盖：`draft.strategy_config = { ...patch }`。语义不变，多一层叠加是冗余。

##### D4: undefined 兼容旧 DSL

`default.ts::checkValid` 在校验 `weight` / `fallback_weight` 时把 `undefined` 当作
"合法 — 走后端默认"。原因：v2.4 DSL 的 `AggregationInputRef` 没有这两个字段，旧
工作流导入到 v3 节点时 ref.weight 是 undefined。后端 pydantic 会用 `1.0` /
`None` 默认，前端如果 fail-fast 反而比后端更严，会让用户卡在"看似没动过的旧
节点突然报错"。

判定 ref.weight === undefined 后再 fallthrough 到合法分支，handleAddInput 新建的
inputs 永远带 `weight: 1`，所以新节点路径仍然得到强类型保证。

#### 质量门

| 门 | 命令 | 结果 |
|---|---|---|
| TS | `pnpm type-check:tsgo` | 0 errors |
| Lint | `pnpm exec eslint app/components/workflow/nodes/ensemble-aggregator/` | 0 errors / 1 warning（pre-existing `react/no-array-index-key`，与 P3.A.1 之前同步保留）|
| 回归 | `pnpm test -- --run app/components/workflow/nodes/parallel-ensemble` | 8 files / 75 cases 全过（dynamic-config-form 共享体没动） |

后端 P3.A.1 的 236 cases 不受影响（前端纯改）。

#### i18n 增量（en-US ↔ zh-Hans 完全对齐）

新增 22 keys：

```
concat.fields.{include_source_label, order_by_weight, separator}.{label, tooltip}    (6)
errorMsg.{extraMustBeObject, fallbackWeightInvalid, orderByWeightMustBeBoolean,      (4)
          weightInvalid}
fallbackWeight / fallbackWeightPlaceholder / fallbackWeightTooltip                    (3)
strategies.concat.hint                                                                (1)
strategies.weighted_majority_vote.{label, description, hint}                          (3)
strategyConfig                                                                        (1)
weight / weightModeNumber / weightModeVariable / weightToggleAria                     (4)
```

删除 5 keys（被 dynamic-config-form 反射接管）：

```
strategies.concat.{includeSourceLabel, includeSourceLabelTooltip,
                   separator, separatorTooltip}
```

`strategies.majority_vote.hint` 文案改写：原"无需额外配置 + 并列按源 ID 字典序"
更新为说明 weight=1 时退化为整数计数 / 非 1 时切加权多数（与 P3.A.1 后端
`majority_vote.py` 行为对齐）。

#### 后续

- P3.A.3 单测 + 后端测试翻译
- 🟢 ship A：response 模式从节点入口到画布反射全通；外部贡献者基于
  `ResponseAggregator` + `SourceAggregationContext` SPI 写自定义策略时，
  `ui_schema` 镜像到 `ENSEMBLE_STRATEGY_META` 即可在画布看到反射表单
- B 阶段（P3.B.*）的 token 模式不动这条路径；token 模式 prompt 在 token-model-source
  里渲染、聚合走 BackendAggregationContext 而非这里的 SourceAggregationContext


---

### P3.A.3 - P3.A.3 Landing — ensemble_aggregator 测试翻译 + 新增

> Source shard: `P3.A.3_LANDING.md`


日期：2026-04-30

#### 范围

P3.A 切片的最后一刀：把 A.1（后端 weight + ADR-v3-8 SPI 切分）/ A.2
（前端 weight + ui_schema 反射）落地时跳过的测试 corner 补完整，并
首次给 `ensemble-aggregator/components/` 写专属前端单测。

依赖：P3.A.1 + P3.A.2（均已 ✅ 落地，2026-04-30）。
对齐 ADR：v3-8（SPI context 切分）/ v3-9（SPI 隔离）/ v3-15（fail-fast）。

落地后：🟢 **ship A — response 模式完整可用**。

#### 不做（按 v3 计划切片）

- token 模式 backend SPI 升级 + `parallel_ensemble.runners.response_level`
  删除：P3.B.0
- `token-model-source` 节点：P3.B.1 / P3.B.2
- `parallel_ensemble` 重定位（删 model_aliases / question_variable，加
  token_sources）：P3.B.3 / P3.B.4
- 4 份 v3 DSL 示例 + EXTENSION_GUIDE 升级：P3.C.1
- `DEVELOPMENT_PLAN.md` v2.4 钩子全量化 + v3.1 状态切换：P3.C.2

#### 1. 后端测试增量（+9 cases）

A.1 已 ship 77 cases；A.3 在两个测试文件补 9 个 corner，到 **86 cases**：

##### `test_node.py::TestDynamicWeightResolution` — +6

A.1 落地了 happy / 缺变量 / 非数值 / bool / fallback 五条主路径。A.3 补
`_resolve_weight` 内部其余 `WeightResolutionError.reason` 分支、`±Inf`
双符号回归、以及 fallback 记录回归：

| 新 case | 覆盖什么 |
|---|---|
| `test_dynamic_weight_none_value_fail_fast` | pool 返回 NoneSegment（`segment.value is None`）→ 走 `reason="resolved value is None"`（或某些 VariablePool 实现把 None 当作不存在 → 走 "not present"）。无论哪条分支，error_type 必须是 `WeightResolutionError`，不能被静默 `float(None)` 拦下。 |
| `test_dynamic_weight_nan_value_fail_fast` | pool 返回 `float('nan')`（合法 float 但 `math.isfinite=False`）→ `reason="resolved value is not finite (got nan)"` |
| `test_dynamic_weight_inf_value_fail_fast` | 同上，`float('inf')` |
| `test_dynamic_weight_negative_inf_value_fail_fast` | 同上，`float('-inf')`，防止只覆盖正无穷导致负无穷漏检。 |
| `test_fallback_recovers_non_numeric_pool_value` | 验 fallback 路径不只对 "missing" 触发：pool 解析到字符串"three"也能被 fallback 接住，且 `process_data["weight_fallback_warnings"][0].reason` 含 "not numeric"（A.1 测试只覆盖了 missing 分支） |
| `test_multiple_fallbacks_recorded_in_declared_order` | 两个 source 都 fallback，`weight_fallback_warnings` 列表声明序保持（单步调试面板要按行列对齐 inputs，不能按字典序乱序）|

##### `test_strategies.py::TestWeightedMajorityVoteStrategy` — +3

A.1 已覆盖 highest-weight / unit-collapse-to-winner / lex tie-break /
weights-in-metadata。A.3 补 ADR-v3-9 / Rv3-9 关键差异点：

| 新 case | 覆盖什么 |
|---|---|
| `test_unit_weights_keep_weighted_metadata_shape` | unit weight 下 `weighted_majority_vote` 的 `scores` 字典必须保持 float（不像 `majority_vote` 全 1 时 collapse 到 int）。`metadata.strategy = "weighted_majority_vote"` 永不被静默降级 —— 这是 SPI 扩展示例的"公开承诺"，下游消费 `metadata.scores` 的代码靠 float 类型 |
| `test_dominant_single_voter_outweighs_unanimous_minority` | 1 个 weight=10 的 oracle 压倒 4 个 weight=1 的 minority；scores={minority:4.0, dominant:10.0}；tie-break **不**触发（差距 6.0）|
| `test_aggregated_minority_overpowers_single_strong_voter` | 加权和才是关键：3×1.5 = 4.5 > 4.0；如果代码错写成"单条最高权 wins"会被这条钉死 |

##### `test_strategies.py::TestSourceAggregationContextIsolation`

A.1 已落地（`model_fields` 钉死 4 字段 + 三策略全跑通）。A.3 不重复。

#### 2. 前端测试增量（+23 cases）

`web/app/components/workflow/nodes/ensemble-aggregator/components/__tests__/`
是一个**新建**的目录 —— A.2 落地时只跑了 `parallel-ensemble/` 共享体的
`pnpm test`（8 file / 75 case 全绿）确认没退化，但
`ensemble-aggregator` 自家的 input-list / strategy-selector 还没有专属
spec。A.3 补齐两份。

##### `input-list.spec.tsx` — 13 cases

| describe 块 | 覆盖什么 |
|---|---|
| Static weight mode (default) | 数值 input + 静态模式 toggle 文案 / `fallbackWeight` 行隐藏；2.5 finite number 透传；空字段 → emit `1`（与后端默认对齐） |
| Dynamic weight mode | `weight: []`（刚切换、没选）保持动态模式；两个 picker（变量选择 + weight）；fallback 行可见；选中后 emit `ValueSelector` 数组 |
| Mode toggle | 静→动：emit `[]`，**不**触 fallback 改写；动→静：emit `1` + `null` 清 fallback（fallback 在静态模式无意义 ADR-v3-15）|
| Fallback weight input | 空字段 → emit `null`（fail-fast，ADR-v3-15）；`0.25` finite → emit `0.25` |
| Readonly | 切换按钮 / picker disabled；add 按钮整段不渲染 |
| Source list management | 多行 onSourceIdChange / onRemove 索引正确；onAdd 调一次 |

##### `strategy-selector.spec.tsx` — 10 cases

| describe 块 | 覆盖什么 |
|---|---|
| Dropdown surface | trigger 显示活跃策略 i18n label；下拉列出 3 个策略（majority_vote / concat / weighted_majority_vote）—— 守 SPI literal 收紧不被某一侧悄悄改回 2 项 |
| Selection mutation | 选不同策略 fire `onStrategyChange(name)`；选同名 no-op（避免悄悄重置已经填好的 strategy_config） / readonly disabled |
| Schema reflection | `majority_vote` / `weighted_majority_vote` 走 hint 分支（`ui_schema={}`）；`concat` 走 `DynamicConfigForm` 分支，传入 3 keys（`include_source_label`, `order_by_weight`, `separator`）+ `i18nKeyPrefix = "nodes.ensembleAggregator.concat"`；form onChange 透传给 `onStrategyConfigChange`；readonly 透传 |

##### Mock 策略

按 `web/docs/test.md` 的"DO NOT mock base components / DO mock external
or portal-bound primitives"原则：

- `VarReferencePicker` 拉 workflow store + portal —— mock 成 thin
  stub，stub 内部用 `useRef` 给每个实例发稳定 ID（避免 React Hooks rules
  对工厂函数里 `useMemo` 的报错）
- `@langgenius/dify-ui/dropdown-menu` 的 Radix portal happy-dom 渲染不
  到 —— mock 成内联 context-driven 的 trigger / content（与 P2.11
  `runner-selector.spec.tsx` 同模式）
- `DynamicConfigForm` —— 测试 ensemble-aggregator/strategy-selector 自身
  反射逻辑而非 form 内部，捕获 props 即可（form 自有 spec 在
  `parallel-ensemble/components/__tests__/dynamic-config-form.spec.tsx`，
  本次 8 file / 75 case 不退化）
- `Tooltip` / `Field` / `RemoveButton` / `AddButton` / dify-ui `Input`
  等 base component **不** mock（按 `web/docs/test.md` D3）

##### TS / lint 处理

- `vi.fn<(args) => void>()` 显式声明签名 —— `vi.fn()` 默认 `Mock<Procedure>`
  无法窄化到 `(index, value) => void`，会被 tsgo 拒
- 工厂函数里 React 组件用 `React.useRef` 而非 `useMemo` —— `vi.mock`
  hoisting 让组件命名空间和外层闭包之间有解析顺序问题，`useRef` 不需要
  hooks-rules 的命名识别（实质上在 mock 内部就工作了）
- `RemoveButton` 没暴露 role/aria，按 destructive className 过滤匹配；
  这与组件内部 ActionButton 包装方式耦合（注释里写明了），后续如改成
  aria-labeled 时这条 selector 要更新

#### 3. 质量门

| 门 | 命令 | 结果 |
|---|---|---|
| 后端 pytest | `cd /home/xianghe/temp/dify && uv run --project api pytest api/tests/unit_tests/core/workflow/nodes/ensemble_aggregator/ api/tests/unit_tests/core/workflow/nodes/parallel_ensemble/ -q` | 245 passed（ensemble_aggregator 77→86，+9 net；parallel_ensemble 不退化） |
| TS | `pnpm type-check:tsgo` | 0 errors |
| Lint | `pnpm exec eslint app/components/workflow/nodes/ensemble-aggregator/` | 0 errors / 1 warning（pre-existing `react/no-array-index-key` 自 P3.A.2 起即存在） |
| 前端 vitest | `pnpm test -- --run app/components/workflow/nodes/ensemble-aggregator app/components/workflow/nodes/parallel-ensemble` | 10 files / 98 passed（ensemble-aggregator 2 files / 23 cases 新；parallel-ensemble 8 files / 75 cases 不退化）|

#### 4. 文件清单

```
新增
api/tests/unit_tests/core/workflow/nodes/ensemble_aggregator/test_strategies.py  # +3 cases (TestWeightedMajorityVoteStrategy)
api/tests/unit_tests/core/workflow/nodes/ensemble_aggregator/test_node.py        # +6 cases (TestDynamicWeightResolution)
web/app/components/workflow/nodes/ensemble-aggregator/components/__tests__/input-list.spec.tsx        # 13 cases
web/app/components/workflow/nodes/ensemble-aggregator/components/__tests__/strategy-selector.spec.tsx # 10 cases
docs/ModelNet/P3.A.3_LANDING.md

修改（文档）
docs/ModelNet/active/TASKS.md  # P3.A.3 标 ✅ + 5 项落地小结，进度 P3.0+P3.A.1+P3.A.2 → +P3.A.3
```

零生产代码改动 —— A.1 / A.2 已经把 SPI / panel / 策略全部落地，A.3 只
补测试。零新组件、零 i18n key 增删、零依赖更新。

#### 5. ship A 总结（A.1 + A.2 + A.3）

- 后端：`AggregationInputRef` 加 `weight` / `fallback_weight` / `extra`；
  `_resolve_weight` 三分支（静态 / 动态 / fallback）+ `process_data`
  trace；`SourceAggregationContext` SPI 切分（不含 backend / runner）；
  3 策略闭名单（`majority_vote` / `concat` / `weighted_majority_vote`）
- 前端：input-list 行内 weight 模式切换（# ↔ {x}）+ fallback 行；
  strategy-selector 反射 `ui_schema` 走 `parallel-ensemble/dynamic-config-form`；
  i18n 22 keys 完全对齐（en-US ↔ zh-Hans）
- 测试：后端 86 cases / 前端 23 cases / parallel-ensemble 75 cases
  不退化；`pnpm type-check:tsgo` + `eslint` + `pytest` 全绿

外部贡献者基于 `ResponseAggregator` + `SourceAggregationContext` SPI
即可写自定义策略：策略类继承 `ResponseAggregator`、声明
`config_class` / `i18n_key_prefix` / `ui_schema`，注册进
`registry.py::register`，前端在 `ENSEMBLE_STRATEGY_META` 镜像
`ui_schema` 后自动反射出表单 —— 不接触 backend / runner / token 语义。

#### 6. 后续

P3.B.* 启动条件已满足（response_level runner 删除 + ADR-v3-8 别名清理
+ token-model-source 节点新建）。预计 1.5d（B.0）+ 5d（B.1–B.5）→
ship B。


---

## Phase 3.B - Token-mode refactor and token source

### P3.B.0 - P3.B.0 Landing — backend SPI 扩展（ADR-v3-14）+ Aggregation context 切分（ADR-v3-8）

> Source shard: `P3.B.0_LANDING.md`


日期：2026-04-30

#### 范围

ship A 之后第一刀，把 token 模式所需的 backend SPI 升级一次性付清，并按
ADR-v3-9 删掉迁去 `ensemble_aggregator` 的 response 路径。三件事：

1. **`TokenStepParams` 新增 + `step_token` 签名迁移**：`spi/backend.py` 加
   `TokenStepParams(BaseModel, extra="forbid", frozen=True, arbitrary_types_allowed=True)`
   承载 `top_k / temperature / top_p / max_tokens / stop / seed / extra`；
   `ModelBackend.step_token(prompt: str, top_k: int)` → `step_token(prompt: str, params: TokenStepParams)`。
   PN.py 主循环里"同模型不同温度做 self-consistency"在 SPI 层有了一等
   入口，不再需要 backend 重建实例
2. **Aggregation context 切分定型（ADR-v3-8）**：`AggregationContext`
   back-compat 别名删除；`SourceAggregationContext` / `BackendAggregationContext`
   两层各司其职。token aggregators 只能从 `BackendAggregationContext` 进入，
   `runners/token_step.py` 真正给 `backends` 字段填了 `BackendInfo` 列表
   （A.1 落地时占位为 `[]`，A.3 没补，本切片付清）
3. **ADR-v3-9 删除**：`runners/response_level.py` + `aggregators/response/*`
   全部下线；response 路径在 ship A 已转给 `ensemble_aggregator`，留两份就
   是两份维护负担

依赖：ship A（P3.A.1 + P3.A.2 + P3.A.3）✅
对齐 ADR：v3-8（context 切分）/ v3-9（SPI 隔离）/ v3-14（per-call sampling）

#### 不做（按 v3 计划切片）

- `token-model-source` 节点（后端 entities + 前端 panel）：P3.B.1 / P3.B.2
- `parallel_ensemble` 重定位（删 `model_aliases` / `question_variable`，加
  `token_sources`，按 spec 拉 backend）：P3.B.3 / P3.B.4
- `parallel_ensemble` 测试翻译 + 新增（token 模式 panel / DSL / 端到端）：
  P3.B.5
- 4 份 v3 DSL 示例 + EXTENSION_GUIDE 升级：P3.C.1
- `DEVELOPMENT_PLAN.md` v2.4 钩子全量化 + v3.1 状态切换：P3.C.2

#### 1. `spi/backend.py` — `TokenStepParams`

```python
class TokenStepParams(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, arbitrary_types_allowed=True)

    top_k: int = Field(default=5, gt=0)
    temperature: float | None = Field(default=None, ge=0.0)
    top_p: float | None = Field(default=None, gt=0.0, le=1.0)
    max_tokens: int = Field(default=1, gt=0)
    stop: tuple[str, ...] = Field(default=())
    seed: int | None = None
    extra: Mapping[str, Any] = Field(default_factory=dict)

    @field_validator("extra", mode="after")
    @classmethod
    def _freeze_extra(cls, value: Mapping[str, Any]) -> Mapping[str, Any]:
        if isinstance(value, MappingProxyType):
            return value
        return MappingProxyType(dict(value))
```

##### 字段选型

| 字段 | 默认 | 为什么 |
|---|---|---|
| `top_k` | 5 | 与 `TokenStepConfig.top_k` 默认一致；`gt=0` 拒 0 / 负数 |
| `temperature` | `None` | None = "用 backend 自己默认"；`ge=0.0` 允许 greedy（temp=0），不允许负 |
| `top_p` | `None` | 同上；`gt=0.0, le=1.0` 是 nucleus sampling 的合法区间 |
| `max_tokens` | 1 | step_token 顾名思义是 single-token 推进；think_phase 走的是 `backend.generate`（GenerationParams 路径），不复用这个默认 |
| `stop` | `()` | tuple 而非 list —— frozen 模型语义一致，hashable 便于将来缓存 step params |
| `seed` | `None` | None = backend 决定；显式 int 让 self-consistency / 幂等回放可控 |
| `extra` | `MappingProxyType({})` | 见下节"`extra` 防泄漏"|

##### `extra` 防泄漏（`MappingProxyType` + `field_validator(mode="after")`）

token_step 主循环每步把**同一个** `params` 实例提交给 N 个 `step_token`
并发调用：

```python
for alias, backend in backends.items():
    future = self._executor.submit(backend.step_token, prompts[alias], params)
```

如果 `extra` 还是普通 `dict`，一个失误的第三方 backend 走

```python
def step_token(self, prompt, params):
    params.extra["my_key"] = "..."   # 跨线程泄漏到 sibling backend
```

会让 backend A 的状态污染 backend B —— frozen=True 只防字段重新赋值，**不**防
dict 里面被原地改。两层防护：

1. `field_validator(mode="after")` 把入参 dict **拷贝一份**再包成
   `MappingProxyType` —— caller 后续改自己手里那份不影响 params 实例
2. `MappingProxyType` 是只读 view，`params.extra[k] = v` 会抛
   `TypeError: 'mappingproxy' object does not support item assignment`，
   失误立刻 fail loud

##### `step_token` 签名迁移

```python
# 旧
def step_token(self, prompt: str, top_k: int) -> list[TokenCandidate]: ...

# 新
def step_token(self, prompt: str, params: TokenStepParams) -> list[TokenCandidate]: ...
```

`ModelBackend` 基类默认实现继续抛 `CapabilityNotSupportedError`；唯一内置
backend `LlamaCppBackend` 同步迁移。

#### 2. `backends/llama_cpp.py` — per-call 应用全部 knob

旧实现只把 `top_k` 拼进请求体；新实现按 ADR-v3-14 把 `params.{top_k,
temperature, top_p, stop, seed, max_tokens}` 全部反映到 llama.cpp
sampling chain，外加 `extra` 透传：

```python
def step_token(self, prompt: str, params: TokenStepParams) -> list[TokenCandidate]:
    body: dict[str, Any] = {
        "prompt": prompt,
        "max_tokens": params.max_tokens,
        "n_probs": params.top_k,
        "post_sampling_probs": True,
    }
    if params.temperature is not None:
        body["temperature"] = params.temperature
    if params.top_p is not None:
        body["top_p"] = params.top_p
    if params.stop:
        body["stop"] = list(params.stop)
    if params.seed is not None:
        body["seed"] = params.seed
    if params.extra:
        body.update(params.extra)   # 第三方 fork 加 mirostat 等专有键
    ...
```

##### 为什么 `None` 不发 vs `=0` / `=""` 发空值

llama.cpp 的 `/completion` endpoint 对未设字段会用服务端默认。如果 SDK 强行
`{"temperature": null}` 发过去，server 端反而会因为类型不匹配（期望 float）
拒掉。`None` 表示"由 server 决定"，`0.0`（greedy）会被显式发出，`0` 和
`null` 在 wire 层是两件事。

#### 3. `spi/aggregator.py` — `AggregationContext` 别名删除

```diff
-# ── Back-compat alias (deleted in v3 P3.B.0 alongside response_level
-#    runner). Kept now so token aggregators + the soon-to-be-deleted
-#    response_level runner keep importing the old name.
-AggregationContext = BackendAggregationContext
```

A.1 落地时给 `AggregationContext` 留了别名让 `aggregators/token/*` 不必同
切片改类型注解。本切片别名删掉，`spi/__init__.py` 导出表同步剔除，所有
token aggregator 的 `context: AggregationContext` 已在 A.1 改为
`BackendAggregationContext`，无残留 import。

#### 4. `runners/token_step.py` — `backends` 字段真正填值

A.1 占位实现：

```python
ctx = BackendAggregationContext(
    sources=list(backends.keys()),
    ...
    backends=[],   # ← 占位
    ...
)
```

第三方 token aggregator 从 `ctx.backends` 拿不到 backend 元数据，被迫去摸
`_spec` 私有属性。本切片付清：

```python
backend_infos: list[BackendInfo] = [
    BackendInfo(
        id=backend.id,
        backend=type(backend).name,                       # registry key（不是实例 alias）
        model_name=backend.model_name,
        capabilities=sorted(c.value for c in backend.instance_capabilities),
        metadata={},
    )
    for backend in backends.values()
]
```

##### 不变量

- 顺序与 `sources=list(backends.keys())` 一致 —— aggregator 可以
  `zip(ctx.sources, ctx.backends)` 不用走 dict lookup
- `backend` 字段是**注册表键**（`type(backend).name`，例如 `"llama_cpp"`），
  不是节点配置里的 alias —— capability gating 跨 alias 共享同一 backend
  class 时不会重复
- `capabilities` 用 `sorted(c.value for c in caps)` 输出 list[str]，跨步
  稳定可比；happy-dom / JSON 序列化都不会被 `frozenset` 顺序差搅乱
- `metadata={}` —— v0.2 没有节点级 metadata 通道，第三方 backend 想暴露
  自定义元数据走 `extra` / spec 字段（不在 SPI 范围）

##### 同切片建一次（不在循环里）

`backend_infos` 在 token loop 外构造一次；循环每步只把同一份 `list` 注入
`BackendAggregationContext`。`BackendInfo` 是 TypedDict，浅拷贝即引用
拷贝，零额外开销。

#### 5. `runners/think_phase.py` — 不动签名

`think_phase` 走的是 `backend.generate(prompt, params: GenerationParams)`，
不是 `step_token`；max_tokens=8196 + stop=[stop_think] 的 chain-of-thought
预跑跟 token-step 单 token 推进的语义不同，参数空间也不一样，所以
**不**复用 `TokenStepParams`，保持 `GenerationParams: TypedDict, total=False`
的现状。任务卡里写"think 同步改签名"在落地时确认是指 step_token 路径同步
迁移；think_phase 没有 step_token 调用点，无变化。

#### 6. ADR-v3-9 删除清单

```
api/core/workflow/nodes/parallel_ensemble/
├── runners/
│   ├── response_level.py          # 删
│   └── __init__.py                # 改：只 import token_step
└── aggregators/
    ├── response/                  # 整目录删
    │   ├── concat.py
    │   ├── majority_vote.py
    │   └── __init__.py
    └── __init__.py                # 改：只 import token

api/tests/unit_tests/core/workflow/nodes/parallel_ensemble/
├── runners/test_response_level_runner.py     # 删
├── aggregators/test_response_concat.py        # 删
└── aggregators/test_response_majority_vote.py # 删
```

注释清扫：`spi/capability.py` `TOKEN_STEP` 文档串改为
`step_token(prompt, params: TokenStepParams)`；`spi/aggregator.py`
`SourceAggregationContext.weights` 不再提 response_level；`node.py` /
`entities.py` 涉及 response_level 的引用同切片改成 token-only 措辞。

#### 7. 测试改造（mock 全量升级到新签名）

##### `runners/conftest.py::FakeBackend`

```diff
-def step_token(self, prompt: str, top_k: int) -> list[TokenCandidate]:
-    self.step_calls.append((prompt, top_k))
+def step_token(self, prompt: str, params: TokenStepParams) -> list[TokenCandidate]:
+    self.step_calls.append((prompt, params))
```

##### `aggregators/conftest.py::make_ctx`

`AggregationContext` 别名没了 → 直接构造 `BackendAggregationContext`，sources /
source_meta / strategy_config 三个 SourceAggregationContext 字段从 weights
推导（向后兼容现有 caller）。

##### 新增测试（pin 关键不变量）

| 测试 | 文件 | 钉死什么 |
|---|---|---|
| `test_token_step_populates_backend_aggregation_context` | `runners/test_token_step_runner.py` | `ctx.backends` 不是 `[]`；顺序与 `ctx.sources` 一致；`backend` 字段是 registry-key 而非 alias；`capabilities` 是 sorted list[str] |
| `test_per_call_sampling_knobs_propagate` | `test_llama_cpp_backend.py` | `temperature` / `top_p` / `stop` / `seed` / `extra` 全部反映到 wire body |
| `test_optional_knobs_absent_when_unset` | `test_llama_cpp_backend.py` | `None` 字段不发到 wire（避免 server 端拒掉 `{"temperature": null}`） |
| `test_extra_is_read_only_and_detached` | `test_llama_cpp_backend.py` | `params.extra` 是 `MappingProxyType`；caller 后续改自己 dict 不渗透；`params.extra[k] = v` 抛 `TypeError` |

##### 删除测试

`response_level` runner / `concat` / `majority_vote` 三套 spec 全删（迁去
`ensemble_aggregator` 后由 P1.x / P3.A.* 的 spec 覆盖；这里留着就是双份）。

##### `test_token_step_runner.py::test_run_rejects_response_aggregator`

原先 import `aggregators.response.concat::ConcatAggregator` 验"response 错
传给 token runner 失败"。删了 ConcatAggregator 之后改用 in-test 合成的
`_StubResponseAggregator(ResponseAggregator[_StubResponseConfig])`，断言不变
（`runner.run` 抛 `TypeError, match="TokenAggregator"`）。

##### `test_node.py` 大修

A.1 之前 `TestBackendFailures` / `TestTraceStorage` 用真的
`ResponseLevelRunner + MajorityVoteAggregator` 跑 finalize / failed 状态。
本切片改成合成 `_SummaryRecordingRunner` —— 直接往 `TraceCollector` 写
`error_count` / `backend_count` / 每 alias 的 `record_response`，节点
`_derive_status` 走的还是 `error_count >= backend_count` 那条 SUCCEEDED /
FAILED 分支，节点级契约不变。

`test_dsl_rejects_runner_config_smuggle` 由 `ResponseLevelConfig` 改用
`TokenStepConfig`：`extra="forbid"` 这条契约保护的是"内置 runner 一定打开
forbid"，换成留下的内置 runner 测试同样有效。

#### 8. 副产品修复

`api/controllers/console/workspace/aggregators.py:25` 早就有的 typo：

```diff
-def _project_aggregator(agg_cls: type[Aggregator[Any, Any, Any]]) -> dict[str, Any]:
+def _project_aggregator(agg_cls: type[Aggregator[Any, Any, Any, Any]]) -> dict[str, Any]:
```

`Aggregator` 在 P3.A.1 已经升到 4 参数泛型（加 `ContextT`），这个 controller
直到本切片才被 `test_local_models_api.py`（间接走到此 import）触发评估。
落地时一并修。

#### 9. 质量门

| 门 | 命令 | 结果 |
|---|---|---|
| 后端 pytest | `cd /home/xianghe/temp/dify && uv run --project api pytest api/tests/unit_tests/core/workflow/nodes/ensemble_aggregator/ api/tests/unit_tests/core/workflow/nodes/parallel_ensemble/ api/tests/unit_tests/controllers/console/workspace/ -q` | **440 passed**（parallel_ensemble 净 +2 cases；3 份 response 测试删除；440 - 删除 = 与 ship A 245 + 控制台 9 + 节点重测 不退化） |
| Lint | `uv run --project api ruff check api/core/workflow/nodes/parallel_ensemble/ api/tests/unit_tests/core/workflow/nodes/parallel_ensemble/ api/controllers/console/workspace/aggregators.py` | All checks passed |
| 类型 | `uv run --project api basedpyright api/core/workflow/nodes/parallel_ensemble/spi/backend.py api/core/workflow/nodes/parallel_ensemble/runners/token_step.py ...` | 仅 pre-existing warnings（裸 `dict` / 抽象类未声明 ABC），无新增 error |

#### 10. 文件清单

```
新增
api/core/workflow/nodes/parallel_ensemble/spi/backend.py             # +TokenStepParams + step_token 签名迁移
docs/ModelNet/P3.B.0_LANDING.md

修改
api/core/workflow/nodes/parallel_ensemble/spi/aggregator.py          # 删 AggregationContext 别名 + 注释清扫
api/core/workflow/nodes/parallel_ensemble/spi/__init__.py            # 导出表 -AggregationContext / +TokenStepParams
api/core/workflow/nodes/parallel_ensemble/spi/capability.py          # TOKEN_STEP 注释 step_token 签名同步
api/core/workflow/nodes/parallel_ensemble/backends/llama_cpp.py      # step_token 应用全部 sampling knob + extra
api/core/workflow/nodes/parallel_ensemble/runners/token_step.py      # backends 字段填 BackendInfo + step_params 构造
api/core/workflow/nodes/parallel_ensemble/runners/__init__.py        # 删 response_level import + 重写注释
api/core/workflow/nodes/parallel_ensemble/aggregators/__init__.py    # 删 response 子包 import + 重写注释
api/core/workflow/nodes/parallel_ensemble/aggregators/token/sum_score.py  # 注释 AggregationContext → BackendAggregationContext
api/core/workflow/nodes/parallel_ensemble/node.py                    # 注释清扫（response_level 引用 → token-only / 第三方 runner 措辞）
api/core/workflow/nodes/parallel_ensemble/entities.py                # 注释清扫（model_aliases / runner_config 文档不再举 response_level）
api/controllers/console/workspace/aggregators.py                     # Aggregator 泛型 3 → 4 参（pre-existing typo）

删除
api/core/workflow/nodes/parallel_ensemble/runners/response_level.py
api/core/workflow/nodes/parallel_ensemble/aggregators/response/__init__.py
api/core/workflow/nodes/parallel_ensemble/aggregators/response/concat.py
api/core/workflow/nodes/parallel_ensemble/aggregators/response/majority_vote.py

测试改造
api/tests/unit_tests/core/workflow/nodes/parallel_ensemble/runners/conftest.py             # FakeBackend.step_token 签名迁移
api/tests/unit_tests/core/workflow/nodes/parallel_ensemble/aggregators/conftest.py         # make_ctx 直接构造 BackendAggregationContext
api/tests/unit_tests/core/workflow/nodes/parallel_ensemble/runners/test_token_step_runner.py  # +backend ctx populated；rejects_response_aggregator 改合成 stub
api/tests/unit_tests/core/workflow/nodes/parallel_ensemble/test_llama_cpp_backend.py       # +per-call knobs / +optional knobs absent / +extra read-only & detached
api/tests/unit_tests/core/workflow/nodes/parallel_ensemble/test_node.py                    # ResponseLevelRunner→_SummaryRecordingRunner；smuggle 改用 TokenStepConfig
api/tests/unit_tests/core/workflow/nodes/parallel_ensemble/test_spi_freeze.py              # AggregationContext → SourceAggregationContext + step_token TokenStepParams
api/tests/unit_tests/core/workflow/nodes/parallel_ensemble/llama_cpp/test_backend_ssrf.py  # step_token 调用点改 TokenStepParams
api/tests/unit_tests/controllers/console/workspace/test_local_models_api.py                # AggregationContext → SourceAggregationContext

测试删除
api/tests/unit_tests/core/workflow/nodes/parallel_ensemble/runners/test_response_level_runner.py
api/tests/unit_tests/core/workflow/nodes/parallel_ensemble/aggregators/test_response_majority_vote.py
api/tests/unit_tests/core/workflow/nodes/parallel_ensemble/aggregators/test_response_concat.py
```

#### 11. 设计取舍记录

##### `stop` 用 `tuple[str, ...]` 而不是 `list[str]`

`frozen=True` 的 BaseModel 拿到一个 list 字段时只防"重新赋值给 `params.stop`"，
**不**防"`params.stop.append("...")`"。tuple 是不可变序列，跟模型的 frozen
语义一致。pydantic v2 会把传入的 list 自动 coerce 成 tuple，构造侧无感。

##### `extra` 选 `MappingProxyType` 而不是 `frozendict` / 第三方包

- stdlib，零依赖
- 是个 view 而不是新容器：`MappingProxyType(d)` 不复制 `d` 本身；要做"detach
  caller 持有的 dict"必须显式 `MappingProxyType(dict(value))`，validator 里就
  这么写
- 类型是 `Mapping[str, Any]`，`backends/llama_cpp.py::body.update(params.extra)`
  这种 caller 自然兼容，无需额外 cast

##### `BackendInfo.metadata={}` 不展开为 spec 透传字段

v0.2 `BackendInfo` 是 TypedDict 的公共投影，spec 私有字段（model_url / EOS /
stop_think 等）不应该泄漏到 aggregator 那一侧（SSRF / 信息隔离边界）。第三方
backend 想暴露元数据走"自家 spec 字段 + 自家 backend 类暴露读取方法 + 自家
aggregator 直接 cast"。本切片**不**给 metadata 加默认载体 —— 加了反而开了一
条不易关闭的口。

##### `_SummaryRecordingRunner` 比真 runner 更适合节点级单测

节点 `_derive_status` 的契约其实是"summary 里 error_count >= backend_count
则 FAILED"，跟具体 runner 怎么生成那两个数字解耦。删掉 ResponseLevelRunner
之后用合成 runner 直接写 trace 反而更精确地测了"节点契约"而不是"runner 行为"
—— P2.10 LANDING 文档里也是这个原则，只是 storage / failure 两条当时图省事
用了真 runner。本切片顺手把这块也合成化了。

#### 12. 后续

P3.B.0 落地后 token 模式 SPI 就位，P3.B.1（`token-model-source` 节点后端）
的入口已开：节点 `_run` 渲染 prompt 模板 → 输出
`ModelInvocationSpec(model_alias, prompt, sampling_params, extra)` →
P3.B.3 重定位后的 `parallel_ensemble` 用 `LocalModelRegistry` 拉
backend、把 `spec.sampling_params + TokenSourceRef.top_k_override` 合并打包成
`TokenStepParams` 走主循环。

预计：B.1（1d）→ B.2（2d）→ B.3（2d）→ B.4（1.5d）→ B.5（1.5d）→ ship B。


---

### P3.B.1 - P3.B.1 Landing — `token-model-source` 节点后端（ADR-v3-4 / ADR-v3-10）

> Source shard: `P3.B.1_LANDING.md`


日期：2026-04-30

#### 范围

P3.B.0 把 token 模式所需的 backend SPI 升级一次性付清后，B.1 落 token
模式上游：新建 `token-model-source` 节点的 **后端骨架**。这个节点在 v3
是 token 模式 ensemble 的**配置载体**——它本身**不**调模型（ADR-v3-10），
只做两件事：

1. **prompt 模板渲染**：解析 `{{#node.field#}}` 占位符，从 variable pool
   取段，按 graphon 的 `Segment.text` 规则渲染成最终 prompt（与
   `ensemble_aggregator` / LLM 节点的渲染契约一致）
2. **打包 `ModelInvocationSpec`**：把 `model_alias` + 渲染后的 prompt +
   per-source `sampling_params` + `extra` 通过 `outputs.spec` 推到 variable
   pool，下游 `parallel-ensemble`（P3.B.3 重定位后）按 alias 拉 backend、
   合并 `top_k_override` 后打包成 `TokenStepParams` 走 PN.py 主循环

依赖：P3.B.0 ✅
对齐 ADR：v3-4（token 上游 = `ModelInvocationSpec`）/ v3-10（节点不调模型）/
v3-7（强类型 `SamplingParams` + `extra` 扩展位）/ v3-14（`SamplingParams`
默认值与 `TokenStepParams` 跨字段一致）

#### 不做（按 v3 计划切片）

- `token-model-source` 前端（panel / 9 处注册 / i18n）：P3.B.2
- `parallel_ensemble` 重定位（删 `model_aliases` / `question_variable`，
  加 `token_sources`，按 spec 拉 backend）：P3.B.3
- `parallel_ensemble` 前端 + 测试翻译：P3.B.4 / P3.B.5
- 4 份 v3 DSL 示例 + EXTENSION_GUIDE 升级：P3.C.1

#### 1. `entities.py` — `SamplingParams` + `ModelInvocationSpec` + `TokenModelSourceNodeData`

##### `SamplingParams`

```python
class SamplingParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    top_k: int = Field(default=10, gt=0)
    temperature: float = Field(default=0.7, ge=0.0)
    max_tokens: int = Field(default=1024, gt=0)
    top_p: float | None = Field(default=None, gt=0.0, le=1.0)
    seed: int | None = None
    stop: list[str] = Field(default_factory=list)
```

###### 字段选型

| 字段 | 默认 | 为什么 |
|---|---|---|
| `top_k` | 10 | DEVELOPMENT_PLAN_v3 §4.3 直接给定；与 `TokenStepParams.top_k` 默认 5 故意不同——上游用户设的是"研究侧默认期望候选数"，下游 PN.py 主循环跑时还会被 `TokenSourceRef.top_k_override` 二次覆盖（ADR-v3-6） |
| `temperature` | 0.7 | 用户友好默认；`ge=0.0` 允许 greedy（temp=0 self-consistency 研究场景），不允许负 |
| `max_tokens` | 1024 | 这是节点配置层的"研究意图"上限；`step_token` 路径会被 PN.py 拆成 N 个 single-token 步（`TokenStepParams.max_tokens` 默认 1）；`think_phase` 路径走的是 `backend.generate`，会用上这个 1024（`GenerationParams.max_tokens`） |
| `top_p` | `None` | None = "用 backend 自己默认"；`gt=0.0, le=1.0` 是 nucleus sampling 的合法区间 |
| `seed` | `None` | 与 `TokenStepParams.seed` 同语义：None = backend 决定；显式 int 让 self-consistency / 幂等回放可控 |
| `stop` | `[]` | **这里**用 `list` 而非 `tuple`：`SamplingParams` 是用户在面板里填的 form 层，pydantic 标准 list 才能让 yaml DSL 自然 round-trip；`TokenStepParams.stop` 在 P3.B.3 合并阶段才转 tuple（frozen 一致性） |

###### `extra="forbid"` 的取舍

P3.B.0 的 `TokenStepParams` 用 forbid 是怕 yaml typo 静默无效（`temprature: 0.7`），
B.1 沿用同一思路。但 `SamplingParams` 不再带 `extra: dict[str, Any]`——backend
私有 knob（vLLM `repetition_penalty` / mirostat 等）是 `TokenModelSourceNodeData.extra`
的职责（外层），因为它跨"用户面板 → spec → parallel-ensemble → backend"
四层透传，统一在最外层一个口袋里走最易追溯。把 `extra` 同时放在
`SamplingParams` 和 `TokenModelSourceNodeData` 两层会让"哪个 extra 是给哪
一层用的"难定位（评论 4 同款问题）。

##### `ModelInvocationSpec`（TypedDict）

```python
class ModelInvocationSpec(TypedDict):
    model_alias: str
    prompt: str
    sampling_params: dict[str, Any]
    extra: dict[str, Any]
```

###### 为什么是 TypedDict 而不是 BaseModel

跟 SPI 里 `ChatMessage` / `GenerationParams` 同一逻辑：**spec 跨节点**
（`token-model-source.outputs.spec` → variable pool → `parallel-ensemble`
节点读取）。variable pool 序列化路径已经 dict-shaped，BaseModel 进
pool 还要 `model_dump()`、出 pool 还要 `model_validate()`，多了两次拷贝
和一组 ValidationError 还原成本，没有真实收益。同时 TypedDict 让第三方
扩展（如自家 token aggregator 想消费 spec）不必 import 我们的 pydantic
类——只对 shape 编程，符合 EXTENSIBILITY_SPEC §1.1 的 graphon-decoupled
原则。

##### `TokenModelSourceNodeData`

```python
class TokenModelSourceNodeData(BaseNodeData):
    type: NodeType = TOKEN_MODEL_SOURCE_NODE_TYPE

    model_alias: str = Field(..., min_length=1)
    prompt_template: str = ""
    sampling_params: SamplingParams = Field(default_factory=SamplingParams)
    extra: dict[str, Any] = Field(default_factory=dict)

    NODE_TYPE: ClassVar[str] = TOKEN_MODEL_SOURCE_NODE_TYPE

    @field_validator("model_alias")
    @classmethod
    def _model_alias_not_blank(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("model_alias must not be blank")
        return stripped
```

- 继承 `BaseNodeData(extra="allow")`：legacy 图字段（`selected` /
  `params` / `paramSchemas` / `datasource_label`）正常 round-trip
- **不**复制 `parallel_ensemble.entities` 的 `_FORBIDDEN_TOP_LEVEL_KEYS`
  防护：本节点没有 URL / api_key / endpoint 字段，没有 SSRF / 凭证泄漏面，
  把那套 deny-list 强行搬过来反而是噪音
- `model_alias` 走 `min_length=1` + trim 校验，**不**在 schema 层查
  registry：那是 runtime singleton 的事，留给下游 `parallel-ensemble`
  的 §9 startup validation（已经实现 alias 解析）
- `prompt_template` 默认 `""`：纯常量 prompt 是合法用法（用户写死指令、
  上游不传变量），不强制至少一个 `{{#var#}}`
- `model_alias` 的 trim normalize 跟 `AggregationInputRef.source_id` 一致：
  前端去重比较 trimmed 值，schema 层 persist trimmed 形式让 DSL 重写幂等

#### 2. `node.py` — `TokenModelSourceNode`

##### `_run`

```python
def _run(self) -> Generator[NodeEventBase, None, None]:
    node_data = self.node_data
    try:
        rendered = self._render_prompt(node_data.prompt_template)
    except TokenModelSourceNodeError as exc:
        logger.warning(...)
        yield StreamCompletedEvent(
            node_run_result=NodeRunResult(
                status=WorkflowNodeExecutionStatus.FAILED,
                inputs={"model_alias": node_data.model_alias},
                error=str(exc),
                error_type=type(exc).__name__,
            ),
        )
        return

    spec: ModelInvocationSpec = {
        "model_alias": node_data.model_alias,
        "prompt": rendered,
        "sampling_params": node_data.sampling_params.model_dump(),
        "extra": dict(node_data.extra),
    }
    yield StreamCompletedEvent(
        node_run_result=NodeRunResult(
            status=WorkflowNodeExecutionStatus.SUCCEEDED,
            inputs={"model_alias": node_data.model_alias},
            outputs={"spec": spec, "model_alias": node_data.model_alias},
        ),
    )
```

###### 关键点

- **唯一可失败动作 = prompt 渲染**。`extra="forbid"` 已经在 schema 层把
  `sampling_params` typo 拦了，spec 打包是纯字典构造，不会失败。整个
  `try` 块只裹 `_render_prompt`，事件序列就是 1 个 `StreamCompletedEvent`
  （SUCCEEDED 或 FAILED），没有 streaming chunk——这个节点不产 token
- **`outputs.model_alias` 与 `outputs.spec.model_alias` 双写**：debug
  panel / 单独消费 alias 的下游节点（比如未来的"挑选最便宜的 source"
  逻辑）不必拆 spec 字典；spec 仍然是单一权威载体
- **`dict(node_data.extra)` 防共享**：spec 进 pool 后下游可能 mutate
  （比如 P3.B.3 注入 per-call backend 私有键），不能让 mutation 反向
  污染 `node_data.extra`（本对象在 workflow run 内是共享的）

##### `_render_prompt`

```python
def _render_prompt(self, template: str) -> str:
    parser = VariableTemplateParser(template)
    selectors = parser.extract_variable_selectors()
    if not selectors:
        return template

    variable_pool = self.graph_runtime_state.variable_pool
    inputs: dict[str, str] = {}
    for selector in selectors:
        segment = variable_pool.get(list(selector.value_selector))
        if segment is None:
            raise PromptRenderError(
                template=template,
                missing_var=selector.variable,
                reason="variable not present in pool",
            )
        inputs[selector.variable] = segment.text
    return parser.format(inputs)
```

###### 与 LLM 节点不抽共享 util 的取舍（Rv3-2）

TASKS.md 写的是"**优先尝试**抽 `_render_prompt` 到
`core/workflow/utils/prompt_render.py`（与 LLM 节点共享）"。落地时尝试
后发现：

- LLM 节点在 vendored `graphon` 包内，已经直接用
  `VariableTemplateParser`，外层还包了 jinja2 / chat-template /
  files / memory / vision 一整套 LLM 私有处理；它**没有**一个干净
  的 `_render_prompt` 可以共享
- 抽出去的 util 实际唯一消费者就是本节点；`VariableTemplateParser`
  本身就是 graphon 提供的共享 seam，`agent_node` / `datasource_node`
  也是直接调它，没有额外包一层
- 抽 util 等于"为虚构的将来用例引入一层"，与 CLAUDE.md "Don't design
  for hypothetical future requirements. Three similar lines is better
  than a premature abstraction" 直接相左

结论：**不**抽，节点直接用 `VariableTemplateParser`。Rv3-2 的真实风险
（"两份模板渲染代码不同步"）已经被 graphon 的 `VariableTemplateParser`
本身收敛——格式语法、selector shape、`format` 行为是它一家说了算，
每个节点只是写"循环 + segment.text"几行胶水。

###### 用 `Segment.text` 而不是 `str(segment.value)`

跟 `ensemble_aggregator/node.py:139` 的契约一致：

- `NoneSegment.text == ""`（不是 `"None"`）
- `ObjectSegment.text` = JSON（双引号），不是 Python repr（单引号）
- `ArrayStringSegment.text` = JSON，空数组是 `""` 不是 `"[]"`

用 `segment.value` 经过 `VariableTemplateParser.format` 的 `str(...)`
fallback 会回到 Python repr，跨节点行为不一致。`Segment.text` 是
graphon 已经定型的"对人/对模型可读的文本投影"，哪个节点都该走这条路径。

##### `_extract_variable_selector_to_variable_mapping`

```python
@classmethod
def _extract_variable_selector_to_variable_mapping(
    cls, *, graph_config, node_id, node_data,
) -> Mapping[str, Sequence[str]]:
    mapping: dict[str, Sequence[str]] = {}
    for selector in VariableTemplateParser(
        node_data.prompt_template,
    ).extract_variable_selectors():
        mapping[f"{node_id}.{selector.variable}"] = list(selector.value_selector)
    return mapping
```

key shape `{node_id}.{selector.variable}` 跟 graphon 文档里 LLM 节点的
样例完全一致（`Node.extract_variable_selector_to_variable_mapping`
docstring 给的就是 `1747829548239.#1747829667553.result#`）。这条 key
是给 draft-variable preload pipeline（workflow_entry /
workflow_app_runner）用的，让 `_run` 拉变量时不会 miss。

#### 3. `exceptions.py` — `PromptRenderError`

```python
class TokenModelSourceNodeError(Exception):
    def __init__(self, message: str): ...

class PromptRenderError(TokenModelSourceNodeError):
    def __init__(self, *, template: str, missing_var: str | None, reason: str):
        ...
```

两层结构跟 `ensemble_aggregator/exceptions.py` 一致：基类让 `_run`
能用一个 `except TokenModelSourceNodeError` 一把抓；`PromptRenderError`
带 `missing_var` 字段是为了让面板告诉用户**哪条变量没接上**，而不是
"prompt 渲染失败"这种空泛的报错。

`missing_var` 用 `str | None`（结构性失败时 None）而不是开两个子类，
是因为节点目前**只**有一种结构性失败模式（变量缺失），开两个类是
为还没出现的失败模式预留接口，违反 YAGNI。等真有第二种失败需要不同
处理路径时再拆。

#### 4. 文件清单

```
新增
api/core/workflow/nodes/token_model_source/__init__.py        # NODE_TYPE = "token-model-source" + 注册导入
api/core/workflow/nodes/token_model_source/entities.py        # SamplingParams + ModelInvocationSpec + TokenModelSourceNodeData
api/core/workflow/nodes/token_model_source/exceptions.py      # TokenModelSourceNodeError + PromptRenderError
api/core/workflow/nodes/token_model_source/node.py            # TokenModelSourceNode + _render_prompt + variable mapping

api/tests/unit_tests/core/workflow/nodes/token_model_source/__init__.py
api/tests/unit_tests/core/workflow/nodes/token_model_source/test_entities.py  # 19 cases
api/tests/unit_tests/core/workflow/nodes/token_model_source/test_node.py      # 15 cases

docs/ModelNet/P3.B.1_LANDING.md
```

无修改、无删除——P3.B.1 是纯增量切片，token 模式上游节点首次进仓库。

#### 5. 测试矩阵

##### `test_entities.py`（19 cases）

| 用例类 | 覆盖点 |
|---|---|
| `TestSamplingParamsDefaults` | 默认值与 v3 plan §4.3 对齐 / 全字段覆写 round-trip |
| `TestSamplingParamsExtraForbid` | `temprature` typo 拦截 / `repetition_penalty` 在本层拒绝（必须走外层 `extra`） |
| `TestSamplingParamsRangeGuards` | `top_k` ≤ 0 拒 / `temperature` < 0 拒 / `temperature == 0` 接受（greedy）/ `max_tokens == 0` 拒 / `top_p` ∈ (0, 1] 边界 |
| `TestTokenModelSourceNodeData` | 最小 happy path / blank model_alias 拒 / 空 alias 拒 / alias trim normalize / 空 prompt_template 接受 / `extra` 透传 / 嵌套 `sampling_params` typo 一路冒泡到 `TokenModelSourceNodeData` 校验失败 |

##### `test_node.py`（15 cases）

| 用例类 | 覆盖点 |
|---|---|
| `TestRunHappyPath` | 单 `StreamCompletedEvent` + spec shape 对齐 ADR-v3-10 / 常量 prompt 短路不查 pool / sampling_params 覆写 round-trip 进 spec / `node_data.extra` round-trip / spec.extra 与 node_data.extra 解耦（写一不串到二） |
| `TestRenderPromptSegmentText` | ObjectSegment 渲染为 JSON（不是 Python repr）/ ArrayStringSegment 同 / NoneSegment 为 `""` |
| `TestRunFailurePaths` | 上游变量缺失 → FAILED 事件 + `error_type=PromptRenderError` + 错误消息含变量名 + `outputs == {}` |
| `TestExtractVariableSelectorMapping` | 单变量暴露 / 多变量各自暴露 / 空模板返回空 mapping / 深路径 selector（`upstream.structured_output.city`）verbatim 保留 |
| `TestNodeRegistration` | `node_type == "token-model-source"` / `version() == "1"` |

#### 6. 质量门

| 门 | 命令 | 结果 |
|---|---|---|
| 新包 pytest | `cd api && uv run pytest tests/unit_tests/core/workflow/nodes/token_model_source/ -v` | **34 passed**（test_entities 19 + test_node 15） |
| 邻包回归 | `uv run pytest tests/unit_tests/core/workflow/nodes/{ensemble_aggregator,parallel_ensemble,token_model_source}/ -q` | **257 passed**（与 P3.B.0 落地后基线一致：223 ensemble_aggregator + parallel_ensemble + 34 新增；不退化） |
| Lint | `uv run ruff check core/workflow/nodes/token_model_source/ tests/unit_tests/core/workflow/nodes/token_model_source/` | All checks passed |
| 类型 | `uv run mypy core/workflow/nodes/token_model_source/` | Success: no issues found in 4 source files |
| 注册回归 | `register_nodes(); mapping["token-model-source"]` | `{'1': TokenModelSourceNode, 'latest': TokenModelSourceNode}`——节点通过 `core.workflow.node_factory.register_nodes` 自动注册（导入 `core.workflow.nodes.token_model_source` 包触发 `Node.__init_subclass__` 写入 `Node._registry`），与 `ensemble_aggregator` / `parallel_ensemble` 走同一条注册路径，不需要在 `node_factory.py` 加 `node_init_kwargs_factories` 分支（本节点无外部依赖） |

#### 7. 设计取舍记录

##### `SamplingParams.top_k=10` 与 `TokenStepParams.top_k=5` 故意不一致

P3.B.0 把 `TokenStepParams.top_k` 默认设为 5——SPI 层"保守的内部默认"。
B.1 这一层是**用户面板**默认，DEVELOPMENT_PLAN_v3 §4.3 直接写了 10。
两层不一致是合理的：

- 用户面板默认应对齐"研究侧期望候选数"（10 是 PN.py 主循环 + token 投票
  策略调通的常用值）
- SPI 层默认应对齐"backend 没收到任何参数时给个最小可用值"（5 已经够
  跑通 sanity check）

P3.B.3 的合并优先级是 `TokenSourceRef.top_k_override` > `spec.sampling_params.top_k`
> `TokenStepParams` 默认（这个分支几乎不会走到——节点必给 `top_k`）。
两个默认值在哪里都不会"互相污染"。

##### `_render_prompt` 不抽 util（Rv3-2 实际处置）

见 §2 下"与 LLM 节点不抽共享 util 的取舍"。LLM 节点在 vendored
graphon 内，没有干净的可共享入口；为本节点单独建 `core/workflow/utils/`
违反 YAGNI。Rv3-2 的真实收敛点是 graphon 的 `VariableTemplateParser`，
不是更上层的 wrapper。

##### 不在节点里查 model_alias 是否注册

`model_alias` 校验留给 P3.B.3 重定位后的 `parallel-ensemble` §9
startup validation。理由：

- 本节点 schema 校验时 `LocalModelRegistry` singleton 不一定 ready（特别是
  workflow_entry 在加载 DSL 阶段做 schema 验证）
- alias 注册关系是"运行环境"问题，不是"DSL 静态形状"问题；DSL 应当
  在能运行的环境下才会被实例化，让运行时校验报错位置更准
- `parallel-ensemble` 已经实现完整的 §9 五步流程，复用即可，不要在两个
  地方做同一件事

##### `outputs.spec` + `outputs.model_alias` 双键

只暴露 `spec` 看起来更简洁，但调试场景里"我只想知道这个 source 走的
是哪个模型"是高频需求（panel 的"Run This Step"卡片、单步调试视图、
debug 日志）。`model_alias` 顶层暴露成本是 O(1)，收益是这些路径不必
拆 spec dict——keep it。

`spec.model_alias` 仍然是单一权威——`outputs.model_alias` 始终从
`spec.model_alias` 取，不会出现两者不一致的情况。

##### FAILED 事件不带 `outputs`

happy path `outputs={"spec": ..., "model_alias": ...}`；FAILED path
`outputs={}`。理由：

- spec 里的 `prompt` 字段在渲染失败时本来就没有值；强行塞 `prompt: ""`
  会让下游 `parallel-ensemble` 误以为这是个"空 prompt source"
- graphon 的 `error_strategy` 默认是 `FAIL`，FAILED 事件本来就不应有
  outputs；`error_strategy=DEFAULT_VALUE` 路径会被框架另起处理（用
  `default_value` 字段，跟节点的 `outputs` 解耦）

#### 8. 后续

P3.B.1 落地后 token 模式上游节点首次可单独运行（虽然只产生 spec 不产
内容）。下一步：

- **P3.B.2 前端（2d）**：5 个 .tsx 文件 + 9 处硬编码注册 + i18n。复用
  `parallel-ensemble` 已有的 `model-alias-select`、复用 P2.11 的
  `dynamic-config-form` 反射 `SamplingParams`
- **P3.B.3 重定位（2d）**：`parallel_ensemble.entities` 删
  `model_aliases` / 删 `question_variable`（ADR-v3-16）/ 加
  `token_sources: list[TokenSourceRef]`；`node._run` 改成"从 pool 取 N
  个 spec → 按 alias 拉 backend → 合并 sampling 打包 `TokenStepParams`"

P3.B.2 / P3.B.3 可并行——前者是前端面板，后者是后端 entities + node 改造，
依赖各自独立的 SPI 入口。


---

### P3.B.2 - P3.B.2 Landing — `token-model-source` 节点前端（ADR-v3-4 / ADR-v3-10）

> Source shard: `P3.B.2_LANDING.md`


日期：2026-04-30

#### 范围

P3.B.1 落了 `token-model-source` 后端（entities / node / exceptions /
注册），B.2 把对应的**前端面板**接上：DSL 用户在 Dify 画布上能新建节点、
绑定 `model_alias` + 写 prompt 模板 + 调采样参数，保存出的 DSL 与 P3.B.1
backend 的 `TokenModelSourceNodeData` 形状严格一致。

不下调模型——节点本身在 backend 是**配置载体**（ADR-v3-10），前端面板
只做 schema 配置，所有"运行时"行为（调 backend / 算 logits / 投票）
延迟到 P3.B.3 重定位后的 `parallel-ensemble` 节点。

依赖：P3.B.1 ✅
对齐 ADR：v3-4（token 上游 = `ModelInvocationSpec`）/ v3-10（节点不调
模型）/ v3-7（强类型 `SamplingParams` + `extra` 扩展位）

#### 不做（按 v3 计划切片）

- `parallel_ensemble` 后端重定位（删 `model_aliases` / `question_variable`，
  加 `token_sources`）：P3.B.3
- `parallel_ensemble` 前端重构（`token-source-list` 替换 `model-selector`）：P3.B.4
- 测试翻译 + 后端集成（`TokenStepParams` 合并优先级、per-source sampling
  真传到 backend）：P3.B.5
- 4 份 v3 DSL + EXTENSION_GUIDE 升级：P3.C.1

#### 1. `types.ts` — DSL 表层 + 默认值

##### `TokenModelSourceNodeType`

```ts
export type TokenModelSourceNodeType = CommonNodeType & {
  model_alias: string
  prompt_template: string
  sampling_params: SamplingParams
  extra: Record<string, unknown>
}
```

字段与 P3.B.1 backend `TokenModelSourceNodeData` 字段一一对应。`SamplingParams`
跟 backend `entities.py` 同名同形，序列化两边都能 round-trip：

```ts
export type SamplingParams = {
  top_k: number
  temperature: number
  max_tokens: number
  top_p: number | null
  seed: number | null
  stop: string[]
}
```

`null` 而非 `undefined`：JSON DSL 里"未设"的 top_p / seed 必须显式落
`null`，否则 yaml round-trip 会把 key 整丢，backend pydantic `top_p:
None` 与"键缺失"语义不同。

##### `ModelInvocationSpec`（仅类型，不构造）

ts 端不构造这个对象——它是 backend `_run` 产出的 `outputs.spec` 形状。
保留类型定义供 P3.B.4 `parallel-ensemble` 前端 `spec_selector` 的静态
契约校验复用。

##### `DEFAULT_SAMPLING_PARAMS`

```ts
export const DEFAULT_SAMPLING_PARAMS: SamplingParams = {
  top_k: 10, temperature: 0.7, max_tokens: 1024,
  top_p: null, seed: null, stop: [],
}
```

字段值与 P3.B.1 backend `SamplingParams` Field defaults 严格一致——前端
默认值是 backend pydantic 默认的"投影"，单源真相在 `entities.py`。

#### 2. `default.ts` — `NodeDefault.checkValid` 静态防护

##### 校验顺序

```
1. model_alias       非空 string（trim 后非空）
2. sampling_params   shape + 数值边界
   2.1 top_k         Number.isInteger > 0
   2.2 temperature   ≥ 0 finite
   2.3 max_tokens    Number.isInteger > 0
   2.4 top_p         null OR (number > 0 AND ≤ 1)
   2.5 seed          null OR Number.isInteger
   2.6 stop          Array<string>
3. extra             plain object 或 undefined（不允许 array）
```

###### 为什么 `Number.isInteger`（不是 `Number.isFinite`）

backend `SamplingParams.top_k` / `max_tokens` 是 Pydantic `int`——`1.5`
会让 backend `model_validate` 抛 422。Code review 第一轮指出了这点。
前端必须红线在 save 前，否则用户落 DSL → 跑流程 → 报 422，定位成本陡增。

###### 为什么 `top_p` 允许 `null`

`null` 是 backend "未启用 nucleus sampling"的语义；用户在 form 里清空
top_p 输入框对应 `null`（不是 `undefined`，不是 `0`）。`gt=0` 的边界
让 `top_p === 0` 在前端就被拒，而 `top_p === null` 直接放行。

###### 为什么 `extra` 守门

`extra` 是 backend-private knob 的扩展位（vLLM `repetition_penalty`、
mirostat、研究 tag 等）。守住它必须是 plain object 而非 array，因为
backend `Field(default_factory=dict)` 对 list 会 422。这层守门是为了 DSL
hand-edit / clipboard paste 路径——面板自身不会产出非 dict。

#### 3. `node.tsx` + `panel.tsx` — UI 面板

##### `panel.tsx` 三段结构

```
┌─ Section 1 ──────────────────────────────┐
│ Model alias  [ModelAliasSelect dropdown] │  ← 必填
└──────────────────────────────────────────┘
┌─ Section 2 ──────────────────────────────┐
│ Prompt template  [textarea, 6 rows]      │  ← 选填（常量 prompt 合法）
└──────────────────────────────────────────┘
┌─ Section 3 ──────────────────────────────┐
│ Sampling parameters                       │
│   top_k / temperature / max_tokens        │
│   top_p / seed / stop                     │
└──────────────────────────────────────────┘
─── output vars ─── spec / model_alias
```

###### 为什么 prompt 用纯 textarea，不上 `VarReferencePicker`

token-mode 的 prompt 经常是"长文本 + 多个 `{{#node.field#}}` 引用混
排"——单 `VarReferencePicker` 表达不了这种形态。backend
`_render_prompt` 已经走 `VariableTemplateParser`（与 LLM / agent / data
source 节点的同一个解析器），placeholder 语法对老用户透明。

###### 为什么 sampling 不开 `supportFold`

`Field` 的 fold 模式在 P2.x 给"可选 / 偶尔编辑"配置用（diagnostics
就是典型）。`SamplingParams` 是这个节点的**核心**配置——折叠会让用户
默认看不到 6 个最常调的旋钮。

##### `node.tsx` 画布 chip

未配 `model_alias` 时返回 `null`（与 `parallel-ensemble` 同款"未配置
就只显示标题 + icon"行为）。配置后只显示 alias 一行，不显示 prompt 摘要——
prompt 模板可能很长，画布 chip 寸土寸金，alias 已经能让用户在 graph
里一眼分辨"这个 source 走的是哪个模型"。

#### 4. `use-config.ts` + 注册数据复用

##### `useLocalModels` 直接复用 `parallel-ensemble/use-registries.ts`

```ts
// token-model-source/use-config.ts
import { useLocalModels } from '../parallel-ensemble/use-registries'
```

理由：

- 同一 console 端点（`GET /workspaces/current/local-models`），单源真相
  避免双订阅（react-query staleTime + gcTime 已在 parallel-ensemble
  那侧调好）
- 抽 shared hooks 模块（`workflow/hooks/use-local-models.ts`）只有两个
  消费者，CLAUDE.md "三处相似行 < 早期抽象"原则下不值得
- 后续 P3.B.3 重定位 `parallel-ensemble` 仍然用同一个 hook，不会再多
  消费方

token-model-source 节点不需要 `useRunners` / `useAggregators`——它没有
runner / aggregator 字段，那是下游 `parallel-ensemble` 的事。

##### `model-alias-select.tsx` 单选 vs `parallel-ensemble/model-selector.tsx` 多选

token-model-source **绑定一个**模型；fan-out 在 graph 层完成（多个
token-model-source 节点 → 同一个 parallel-ensemble）。多选组件的
"toggle 切选"语义在单选场景里会让"必须始终选一个"难表达。所以单独
写一个 `ModelAliasSelect` 组件，但接 backend 数据 / `BackendInfo`
projection 类型直接复用 `parallel-ensemble/types.ts`。

###### Capability 静态过滤（`token_step`）

```ts
const REQUIRED_CAPABILITY = 'token_step'
```

不兼容的 backend（缺 `token_step` capability）保持**可见但灰显** + Tooltip
解释，新选阻断、已选保留可点（防止 `model_net.yaml` 切换后"卡住"）。
这条静态过滤的合理性：

- token-model-source 是**专为 token 模式存在**的节点，没有"以后可能用
  在 response 模式"的歧义
- 没有 runner-supplied `required_capabilities` 可以反射（runner 在
  下游 `parallel-ensemble`），所以这里的能力契约是 canonical 而非
  configurable
- 沿用 `parallel-ensemble/model-selector.tsx` 的同款 grey + Tooltip 提示
  风格保持一致体验

#### 5. `sampling-params-form.tsx` — 不走 ui_schema 反射的取舍

P3.B.2 计划稿写过"按 ui_schema 反射，复用 P2.11 dynamic-config-form"。
落地时刻意偏离，原因：

1. `DynamicConfigForm` 反射的是 **runner / aggregator 上送的** `ui_schema`
   （第三方 runner 可以自由声明字段），形态自由
2. `SamplingParams` 是**固定 Pydantic schema**（`entities.py`），6 个字段、
   bound 全已知、扩展位走 `extra` 而不是新字段
3. 反射一个静态 schema 等于 (a) 在前端硬编码一个 `ui_schema` 常量再
   转给 `DynamicConfigForm`——纯绕弯没收益；或 (b) 让节点去拉一个不属
   于它的 registry 端点——架构错位

最终选择：手写 6 个 `<Input>` + 1 个 `<textarea>`，每个 handler 内联
field-specific 边界（`top_k` / `max_tokens` 拒小数、`top_p` clamp 到
(0, 1]、`stop` 按行 split + 跳空行）。新增 sampling 字段需要 entities.py
+ form 同步改——这正是 backend-pinned 契约该有的样子。这个取舍在
form 文件顶端用注释固化，避免下次重新讨论。

#### 6. 9 处硬编码注册

```
1. types.ts                              BlockEnum.TokenModelSource = 'token-model-source'
2. block-selector/constants.tsx          BLOCKS 列表（Transform 分类，紧跟 ParallelEnsemble）
3. nodes/components.ts                   NodeComponentMap + PanelComponentMap
4. block-icon.tsx                        DEFAULT_ICON_MAP + ICON_CONTAINER_BG_COLOR_MAP（VariableX + indigo-500）
5. constants.ts                          SUPPORT_OUTPUT_VARS_NODE
6. last-run/use-last-run.ts              singleRunFormParamsHooks + getDataForCheckMoreHooks（都填 undefined：暂不支持单步运行）
7. _base/components/variable/utils.ts    case BlockEnum.TokenModelSource → push spec / model_alias
8. utils/workflow.ts                     canRunBySingle 列表（保留扩展位；当前 hooks 都是 undefined）
9. constants/node.ts                     WORKFLOW_COMMON_NODES
```

`canRunBySingle` 加了项但 single-run hooks 是 undefined——意味着按当前
配置，节点出现在 single-run 兼容列表但没有具体的 hooks 接管。这与
`parallel-ensemble` / `ensemble-aggregator` 的现状一致（都是 P2.x 阶段
留扩展位）；将来真要支持单步运行（P3.C 阶段），只需补 hooks，不用
再改 9 处中的其他 8 处。

#### 7. i18n（en-US + zh-Hans 双套全量）

| Key 前缀 | 数量 | 覆盖 |
|---|---|---|
| `nodes.tokenModelSource.*` | 36 | title / modelAlias / promptTemplate / sampling.{topK/temperature/maxTokens/topP/seed/stop}.{label,tooltip,placeholder} / outputVars.{spec,modelAlias} / errorMsg.{topKPositive,maxTokensPositive,temperatureNonNegative,topPRange,seedInteger,stopList,extraMustBeObject,samplingParamsMissing,modelMissingCapability} |
| `blocks.token-model-source` | 1 | block-selector 显示名 |
| `blocksAbout.token-model-source` | 1 | block-selector hover description |

en-US + zh-Hans 双套同步落库（共 76 个新增 key）。zh-Hans 文案对齐
P2.x 既有节点的语调（口语 + 简洁，避免直译）。

#### 8. 文件清单

```
新增（11 文件）
web/app/components/workflow/nodes/token-model-source/
  types.ts                                       # 表层 + DEFAULT_SAMPLING_PARAMS
  default.ts                                     # NodeDefault.checkValid
  node.tsx                                       # 画布 chip
  panel.tsx                                      # 三段面板
  use-config.ts                                  # useNodeCrud + 4 个 handler
  components/model-alias-select.tsx              # 单选 + capability gating
  components/sampling-params-form.tsx            # 6 字段手写表单
  __tests__/default.spec.ts                      # 19 cases
  __tests__/panel.spec.tsx                       # 11 cases
  components/__tests__/sampling-params-form.spec.tsx  # 15 cases
  components/__tests__/model-alias-select.spec.tsx    # 9 cases

修改（11 文件，共 +105 行）
web/app/components/workflow/types.ts                                            # +1
web/app/components/workflow/block-selector/constants.tsx                        # +5
web/app/components/workflow/nodes/components.ts                                 # +4
web/app/components/workflow/block-icon.tsx                                      # +2
web/app/components/workflow/constants.ts                                        # +1
web/app/components/workflow/constants/node.ts                                   # +2
web/app/components/workflow/utils/workflow.ts                                   # +1
web/app/components/workflow/nodes/_base/components/workflow-panel/last-run/use-last-run.ts  # +2
web/app/components/workflow/nodes/_base/components/variable/utils.ts            # +11
web/i18n/en-US/workflow.json                                                    # +38
web/i18n/zh-Hans/workflow.json                                                  # +38

文档
docs/ModelNet/P3.B.2_LANDING.md
```

#### 9. 测试矩阵（54 cases）

##### `__tests__/default.spec.ts`（19 cases）

| 用例类 | 覆盖点 |
|---|---|
| `happy path` | 标准 payload / 空 prompt_template / `temperature=0` greedy / `top_p=1` 边界 |
| `model_alias guards` | 空字符串 / 全空白 trim 后空 |
| `sampling_params bound guards` | `top_k=0` / `top_k<0` / `top_k=1.5` 拒（int-only）/ `temperature<0` / `max_tokens=0` / `max_tokens=64.5` 拒 / `top_p=0` / `top_p>1` / `top_p=null` 接受 / fractional `seed` / 非 string 进 `stop` / `sampling_params` 替换为数组 |
| `extra bag guards` | `extra` 任意 dict（vLLM `repetition_penalty` 场景）/ `extra` 替换为数组 |

##### `__tests__/panel.spec.tsx`（11 cases）

| 用例类 | 覆盖点 |
|---|---|
| `Rendering` | 三段 section 全显示 / alias selector props 转发 / sampling form value 转发 / output-vars 双 VarItem / textarea 显示当前 template |
| `Wiring` | alias 变更 → `handleModelAliasChange` / sampling 变更 → `handleSamplingParamsChange` / textarea change → `handlePromptTemplateChange` |
| `Forwarded flags` | `isLoadingModels` 透传 / `readOnly` 同时穿透 alias selector + sampling form + prompt textarea / 空 models 列表透传 |

##### `components/__tests__/sampling-params-form.spec.tsx`（15 cases）

| 用例类 | 覆盖点 |
|---|---|
| `Rendering` | 5 number + 1 textarea / 默认值显示 / readonly 全 disable / 现有 stop 列表渲染为 newline-separated |
| `Boundary coercion` | `top_k` change emit number / `top_k` 清空不 emit / `top_k=1.5` 拒（int-only）/ `temperature=0` 接受 / `top_p` 清空 emit `null` / `seed` fractional 拒 / `seed` 清空 emit `null` / `max_tokens=64.5` 拒 / `stop` 多行 split + 空行剔除 / `stop` 清空 emit `[]` |

##### `components/__tests__/model-alias-select.spec.tsx`（9 cases）

| 用例类 | 覆盖点 |
|---|---|
| `Trigger label` | 未选时 placeholder / 已选时显示 alias / loading 时 "Loading…" / readonly 与 loading 都 disable trigger |
| `Menu — empty state` | 空 models 时显示 "No models registered" hint |
| `Menu — selection` | 兼容 alias 点击 emit / 不兼容 alias 点击不 emit / 已选不兼容 alias 仍可点（deselect path） |

#### 10. 质量门

| 门 | 命令 | 结果 |
|---|---|---|
| 新包 vitest | `node node_modules/vitest/vitest.mjs run app/components/workflow/nodes/token-model-source/` | **54 passed**（19 default + 11 panel + 15 sampling-form + 9 alias-select） |
| 邻包回归 | 同命令 + `parallel-ensemble/` + `ensemble-aggregator/` | **152 passed**（54 新增 + 既有 98 全绿，不退化） |
| 跨域回归 | 同命令 + `_base/components/__tests__/` + `utils/__tests__/workflow.spec.ts` | **218 passed**（变量解析器 + canRunBySingle 等 9 处注册位的下游） |
| Lint | `eslint app/components/workflow/nodes/token-model-source/` | All clean |
| 类型 | `tsc --noEmit` | Success：0 errors |

旁路：`web/app/components/workflow/constants/node.ts` 行 9 上 ESLint
报 `parallel-ensemble` 应排在 `http` 之后——这是预存的（main 分支上
也有），不在 P3.B.2 scope，不修。

#### 11. 设计取舍记录

##### 不抽 `useLocalModels` 到共享 hooks 模块

直接 `import { useLocalModels } from '../parallel-ensemble/use-registries'`。
跨节点 import 看起来不优雅，但当下只有两个消费者（parallel-ensemble +
token-model-source），抽 shared 模块属于 CLAUDE.md "三处相似行 < 早期
抽象" 反对的早期抽象。第三个消费者出现时再升级。

##### `ModelAliasSelect` 不复用 `ModelSelector`

单选与多选语义不同：多选支持"toggle 切除最后一个"，单选不支持。强行
复用要在多选组件内加 `mode: 'single' | 'multi'` 分支，让两种语义混在
一个组件里。隔离两个组件 + 共用 `BackendInfo` 类型 + 共用 capability
gating 的灰显模式，是更好的对称——对称性在视觉/行为/类型三个层面，
不在 React 组件层面。

##### `sampling-params-form` 不上 ui_schema 反射

见 §5。一句话：`SamplingParams` 是 backend-pinned 静态契约，反射只会
让"加新字段必须改两处"变成"加新字段必须改三处（entities.py + ui_schema
常量 + form 反射代码）"——倒退。

##### Capability 过滤是 hardcoded `'token_step'` 而非配置项

token-model-source 的存在前提就是给 token 模式 ensemble 喂数据。把
required capability 写成可配置项需要
(a) 暴露给 panel UI（用户不该选）或
(b) 拉一个新 registry endpoint（架构错位——runner 在下游）。
hardcoded 的成本是"P4 阶段加新 token-mode capability 时记得改这里"，
但这条 invariant 已经在常量定义旁的注释里固化。

##### `top_k` / `max_tokens` 用 `Number.isInteger` 校验

Code review 第一轮 catch 的真问题：`Number.isFinite` 放行 `1.5`，backend
`int` 类型 422。同一个错误曾在 v2.x 里出现过——前后端类型不严格对齐
是配置载体类节点的常见 trap。`default.ts` 的 `checkValid` + `sampling-
params-form` 的 input handler 双重守门（防 DSL paste 绕过 form）。

##### `outputs.spec` + `outputs.model_alias` 双键的前端镜像

backend `_run` 同时暴露 `spec`（完整 ModelInvocationSpec）+ `model_alias`
（顶层冗余）。前端 panel `OutputVars` 也同步声明两个 `VarItem`——下游
节点（panel 调试视图、debug 日志）能直接选 `outputs.model_alias`，不
用解 `spec.model_alias`。零运行成本，高调试价值。

#### 12. 后续

P3.B.2 落地后 `token-model-source` 节点在 Dify 画布上**完整可用**——
用户能拖、配、保存、加载。但保存出的 DSL 还没有任何下游节点会消费
`spec` selector：

- **P3.B.3 后端重定位（2d）**：`parallel_ensemble` 删 `model_aliases` /
  `question_variable`，加 `token_sources: list[TokenSourceRef]`；从 pool
  取 N 个 `ModelInvocationSpec` → 按 alias 拉 backend → 合并
  `top_k_override` 打包 `TokenStepParams` 走 PN.py 主循环
- **P3.B.4 前端重构（1.5d）**：`parallel-ensemble` 前端用
  `token-source-list` 组件替换 `model-selector`；`spec_selector` 限定
  为 `outputs.spec` 形态
- **P3.B.5 测试翻译 + 后端集成（1.5d）**：v2.4 测试改 fixture / 删
  `response_level` runner 测试 / 加 `TokenStepParams` 合并优先级 +
  per-source sampling 真传到 backend

P3.B.3 / P3.B.4 / P3.B.5 串行依赖；B.3 完成 token mode 在 Dify 画布上
首次端到端跑通的最后一块。


---

### P3.B.3 - P3.B.3 Landing — `parallel_ensemble` token 模式重定位（ADR-v3-16）

> Source shard: `P3.B.3_LANDING.md`


日期：2026-04-30

#### 范围

P3.B.0 把 SPI 升好，P3.B.1 / P3.B.2 把上游 `token-model-source` 节点（后端 +
前端）落完，P3.B.3 这一刀把下游 `parallel_ensemble` 节点彻底从"alias 列表 +
question 变量"重定位到"N 个 `ModelInvocationSpec` 上游"，让 PN.py 主循环首次
端到端跑在 v3 形状上。

四件事：

1. **entities 重写**：删 `model_aliases`、删 `question_variable`，新增
   `token_sources: list[TokenSourceRef]`（`source_id` / `spec_selector` /
   `weight` / `top_k_override` / `fallback_weight` / `extra`）。`source_id`
   去重 validator + SSRF 防护保留
2. **runner SPI 演化**：`EnsembleRunner.run(question: str, ...)` →
   `run(sources: dict[source_id, SourceInput], ...)`；新增
   `SourceInput(prompt / params / weight)` TypedDict 把 per-source 数据成束
   交给 runner，"同模型不同温度做 self-consistency"在 SPI 层有了一等位置
3. **node 重构**：`_run` 不再调 `_template_prompts` / 不再读 question；从
   variable pool 解析 N 个 spec → 按 `source_id` 实例化 backend → 合并
   `spec.sampling_params ⊕ top_k_override` 为 `TokenStepParams` →
   `spec.extra ⊕ ref.extra` 路由到 `params.extra`（backend-private 通道）→
   动态 weight 解析 + fallback。§9 step 4 用每个 source 的 effective top_k
   而不是 runner-config 顶层 top_k
4. **`TokenStepConfig.top_k` 移除**：runner 层 top_k 已被 per-source 覆盖，留
   着是误导性配置；`requirements()` 返回形状（`min_top_k=1` 占位 +
   `needs_logprobs`），节点在 §9 替换 value

依赖：P3.B.0 ✅ / P3.B.1 ✅ / P3.B.2 ✅
对齐 ADR：v3-6（per-source `top_k_override`）/ v3-8（context 两层）/ v3-14
（per-call sampling）/ v3-15（fail-fast + fallback）/ v3-16（去 alias 列表，
按 spec 拉 backend）

#### 不做（按 v3 计划切片）

- `parallel_ensemble` 前端重构（删 `model-selector.tsx` / 加
  `token-source-list.tsx`）：P3.B.4
- `parallel_ensemble` 测试翻译 + 新增（v2.4 fixture 全量替换 + 端到端）：
  P3.B.5
- 4 份 v3 DSL 示例 + EXTENSION_GUIDE 升级：P3.C.1
- `DEVELOPMENT_PLAN.md` v2.4 钩子全量化 + v3.1 状态切换：P3.C.2

#### 1. `entities.py` — `TokenSourceRef` + `ParallelEnsembleConfig`

##### `TokenSourceRef`

```python
class TokenSourceRef(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_id: str = Field(..., min_length=1)
    spec_selector: list[str] = Field(..., min_length=2)
    weight: float | list[str] = 1.0
    top_k_override: int | None = None
    fallback_weight: float | None = None
    extra: dict[str, Any] = Field(default_factory=dict)
```

###### 字段选型

| 字段 | 默认 | 为什么 |
|---|---|---|
| `source_id` | required | 同节点内唯一；trim normalize 与 `AggregationInputRef.source_id` 一致；trace / weights / per-model 错误字典都按这个键索引，不能用 alias（同 alias 可重用） |
| `spec_selector` | required (`min_length=2`) | `["<token_model_source_node_id>", "spec"]`，与 graphon 的 `VariableSelector` 同形 |
| `weight` | `1.0` | 与 `AggregationInputRef.weight` 同语义：static float 或 dynamic selector；`> 0` schema 校验，bool / NaN / Inf 全拒（与 ensemble_aggregator 同 finite + non-bool 守护） |
| `top_k_override` | `None` | ADR-v3-6：PN.py 联合投票要求每个 voter 同步 top_k（取 `min(per-source top_k)` 会截断更丰富的 voter），所以**消费侧**留一个 re-pin 入口；其他采样 knob（temperature / top_p / stop / seed / max_tokens）跟随 spec |
| `fallback_weight` | `None` | None = fail-fast；显式数值进 ADR-v3-15 graceful-degrade 路径（trace warning + 改用 fallback） |
| `extra` | `{}` | **backend-private 知识**：consumer-vocab 覆盖 producer-vocab；与 `spec.extra` 在 `_build_effective_params` 里合并到 `TokenStepParams.extra`（不进 aggregator metadata） |

###### `extra="forbid"` 的取舍

跟 `AggregationInputRef` 同款：DSL typo（`source_id_typo: "m1"`）必须在 schema
层就被拦下来。token_sources 是用户面板的一等字段，不允许"看似无效但静默接受"
的状态。

##### `ParallelEnsembleConfig`

```python
class ParallelEnsembleConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    token_sources: list[TokenSourceRef] = Field(..., min_length=1)
    runner_name: str = Field(min_length=1)
    runner_config: dict[str, object] = Field(default_factory=dict)
    aggregator_name: str = Field(min_length=1)
    aggregator_config: dict[str, object] = Field(default_factory=dict)
    diagnostics: DiagnosticsConfig = Field(default_factory=DiagnosticsConfig)

    @model_validator(mode="after")
    def _check_source_id_unique(self) -> ParallelEnsembleConfig:
        ...
```

- **删 `model_aliases`**：alias 选择已经下沉到上游 `token-model-source` 节点
- **删 `question_variable`**：prompt 渲染已经下沉到上游
- **`token_sources.min_length=1`**：schema 层最小宽度；`token_step` 自己的
  `validate_selection` 仍然要求 ≥ 2，留 1 是给将来 `judge`-style 单 contestant
  + 1 judge 的 runner 留口子
- **`source_id` 去重**：跟 `EnsembleAggregatorNodeData._check_source_id_unique`
  同款；trace / weights 都按 source_id 索引，重复键会让 metadata 错位
- **`_FORBIDDEN_TOP_LEVEL_KEYS`** 仅保留 SSRF/凭证（`model_url` / `api_key` /
  `api_key_env` / `url` / `endpoint`）；`model_aliases` 防护下线——内层
  `extra="forbid"` 已经把它当 typo 拒掉

#### 2. `spi/runner.py` — `SourceInput` + `run` 签名

##### `SourceInput`

```python
class SourceInput(TypedDict):
    prompt: str
    params: TokenStepParams
    weight: float
```

- 替代 `question: str` 进 runner.run 的入参；`source_id` → `SourceInput` 一对一
- `prompt` 是上游 `token-model-source` 已经渲染好的最终 prompt（不再走
  `_template_prompts`）
- `params` 是节点合并好的 per-source `TokenStepParams`（spec.sampling_params
  ⊕ top_k_override，且 spec.extra ⊕ ref.extra 已经路由进 `params.extra`）
- `weight` 是节点解析好的 per-source weight（static / dynamic / fallback）
- **不**带 `extra` 字段——backend-private knobs 已经在 `params.extra` 里走了，
  避免双通道造成"哪个 extra 给哪一层用"歧义（评论 4 同款问题）

##### `run` 签名

```python
def run(
    self,
    sources: dict[str, SourceInput],
    backends: dict[str, ModelBackend],
    aggregator: Aggregator,
    config: ConfigT,
    trace: TraceCollector,
) -> Iterator[RunnerEvent]:
```

`sources.keys() == backends.keys()`，都是 `source_id`。第三方 runner
要做的事很简单：用 `sources[sid]["prompt"]` 起步，每步把
`backend.step_token(prompts[sid], sources[sid]["params"])` 提交给
executor，algo 部分不变。

##### `validate_selection` 语义微调

`model_aliases: list[str]` 参数名保留不变（避免破 SPI），但 docstring 加注：
**post-ADR-v3-16 这个 list 是 per-source 的 alias，可以重复**（同模型出现在两
个 source）。runner 计数（`token_step` 的 ≥2）改用 `len(model_aliases)` 而不
是 `len(set(model_aliases))`，因为 source 数量才是关键。

#### 3. `node.py` — 五段式 `_run`

##### 整体流程

```
1. _collect_specs       从 variable pool 取 N 个 ModelInvocationSpec（fail-fast 校验 shape）
2. _build_effective_params  spec.sampling_params ⊕ top_k_override → TokenStepParams
                            spec.extra ⊕ ref.extra → params.extra（backend 私有通道）
3. _validate_at_startup §9 五步 + per-source effective top_k 替换
4. _instantiate_backends  按 source_id 创建 backend（同 alias 可现身两次）
5. _resolve_weights     static / dynamic selector / fallback_weight
6. _build_source_inputs SourceInput 三元组打包
7. runner.run(...)      yield 事件 → 节点翻译为 StreamChunkEvent
8. _finalize_outputs    trace + 真实 backend info → outputs / process_data
```

##### `_build_effective_params` — extras 路由

```python
spec_extra_dict: dict[str, Any] = dict(spec_extra) if isinstance(spec_extra, dict) else {}
merged_extra = {**spec_extra_dict, **dict(ref.extra)}
if merged_extra:
    sampling_clean["extra"] = merged_extra
try:
    out[ref.source_id] = TokenStepParams.model_validate(sampling_clean)
except ValidationError as exc:
    raise InvalidSpecError(
        source_id=ref.source_id,
        reason=f"sampling_params failed validation: {exc}",
    ) from exc
```

- **优先级**：ref.extra > spec.extra（consumer-vocab 覆盖 producer-vocab，跟
  `AggregationInputRef.extra` 在 ensemble_aggregator 的优先级一致）
- **路由到 `params.extra`** 而不是 `SourceInput.extra`：`llama_cpp.step_token`
  在 `body.update(params.extra)` 路径直接读，不会走 aggregator metadata
  side-channel
- **ValidationError 包装**：bare pydantic error 不带 source_id；面板要看
  "**哪个** source 配错"才能定位，节点统一包成 `InvalidSpecError(source_id=...,
  reason=...)`

##### `_resolve_weights` — 动态 weight `> 0` 强制

```python
resolved = float(value)
if not math.isfinite(resolved):
    raise WeightResolutionError(... reason=f"resolved value is not finite (got {resolved})")
if resolved <= 0.0:
    raise WeightResolutionError(... reason=f"resolved value must be > 0 (got {resolved})")
```

静态 weight 在 schema 层就过 `> 0` 守护；动态 selector 解析后等价检查必须
补齐——0 会让 voter 静默归零、负数能让其反噬其他 voter 的 weighted-sum
聚合。fallback_weight 走同样的 `> 0` schema 校验，所以兜底路径也安全。

##### `_validate_at_startup` — per-source effective top_k

```python
runner_requirements = runner_cls.requirements(runner_config)
for ref in cfg.token_sources:
    ...
    source_top_k = effective_params[ref.source_id].top_k
    per_source_reqs: list[Requirement] = []
    for req in runner_requirements:
        if req.get("kind") == "min_top_k":
            per_source_reqs.append({**req, "value": source_top_k})
        else:
            per_source_reqs.append(req)
    issues.extend(backend_cls.validate_requirements(spec, per_source_reqs))
```

- runner 的 `requirements()` 返回**形状**（`min_top_k` 占位 +
  `needs_logprobs`），节点在 §9 step 4 把 `min_top_k.value` 替换为该 source
  的 effective top_k
- 单个 source 的 `top_k_override=25` 触发该 source 的 cap rejection，姊妹
  source 用 spec 默认 top_k 不会被牵连——用例
  `test_top_k_override_drives_per_source_requirement` 钉死

##### `_instantiate_backends` — 按 `source_id` 索引

```python
backends: dict[str, ModelBackend] = {}
for ref in refs:
    alias = specs[ref.source_id]["model_alias"]
    spec: BaseSpec = self._model_registry.get(alias)
    backend_cls = self._backend_registry.get(spec.backend)
    backends[ref.source_id] = backend_cls(spec, http=self._http_client)
```

跟 v2.x 关键差异：dict key 从 alias 改成 source_id，所以"同 alias 出现两次"
拿到两个独立 backend instance。在不复用 backend 实例的语义下，"同模型不同
温度做 self-consistency" 这种研究配置才能真实跑通。

##### `_extract_variable_selector_to_variable_mapping`

```python
mapping[f"{node_id}.token_sources.{ref.source_id}"] = list(ref.spec_selector)
if isinstance(ref.weight, list):
    mapping[f"{node_id}.token_sources.{ref.source_id}.weight"] = list(ref.weight)
```

跟 `EnsembleAggregatorNode` 的 `inputs.{source_id}` 命名对称；draft-variable
preload pipeline 据此提前 materialize 上游变量，避免 `_run` 拉变量时 miss。

#### 4. `exceptions.py` — 三类新异常

```python
class MissingSpecError(ParallelEnsembleError):
    """spec_selector 没解析到任何值（上游 token-model-source 失败）"""

class InvalidSpecError(ParallelEnsembleError):
    """spec 解析到了但 shape 不对（少 model_alias / prompt / sampling_params）"""

class WeightResolutionError(ParallelEnsembleError):
    """动态 weight selector 解析失败（不在 pool / 非数值 / NaN / ≤ 0）"""
```

- `MissingSpecError` / `InvalidSpecError` 都是 fail-fast：联合投票循环没有"少
  一个 voter 也能继续"的语义（ADR-v3-15 留给 weight 用，不留给 spec）
- `WeightResolutionError` 是 ensemble_aggregator 同名异常的 token 版本，与
  `fallback_weight` 配合走 ADR-v3-15

#### 5. `runners/token_step.py` — `TokenStepConfig.top_k` 退场

##### Before

```python
class TokenStepConfig(BaseModel):
    top_k: int = Field(default=5, gt=0, le=20)
    max_len: int = Field(default=1000, gt=0)
    enable_think: bool = True

step_params = TokenStepParams(top_k=config.top_k)  # 主循环里整批 source 共用
```

##### After

```python
class TokenStepConfig(BaseModel):
    max_len: int = Field(default=1000, gt=0)
    enable_think: bool = True

prompts = {sid: src["prompt"] for sid, src in sources.items()}
params_per_source = {sid: src["params"] for sid, src in sources.items()}
weights = {sid: src["weight"] for sid, src in sources.items()}
# 主循环每步：backend.step_token(prompts[sid], params_per_source[sid])
```

- 删掉 `top_k`：runner-level 已经被 per-source `TokenStepParams` 覆盖，留着
  是误导性配置（评论 1 直接钉的问题）
- 删掉 `_template_prompts` + `_DEFAULT_SYSTEM_PROMPT`：prompt 渲染已下沉到
  上游，runner 不再做 chat template 应用
- `requirements()` 返回 `min_top_k=1` 占位（节点会替换）+ `needs_logprobs=True`
- `ui_schema` 移除 `top_k`：前端面板不再渲染该控件
- 主循环算法不变（PN.py joint vote），只是参数和 prompt 来源由"runner 内部
  构造"改为"caller 透传"

`source_meta` 改为 per-source 空 dict——extras 已经在 `params.extra`，aggregator
strategy 暂无消费 source-level metadata 的入口。将来 P3.B.5 / P3.C 如果要给
strategy 加自定义 source 元数据，可以在 TokenSourceRef 加新字段并通过
`SourceInput` 增字段透传，本次不动。

#### 6. `_finalize_outputs` — 真实 backend metadata

```python
backends_info: list[BackendInfo] = [
    BackendInfo(
        id=source_id,
        backend=type(backend).name,
        model_name=backend.model_name,
        capabilities=sorted(c.value for c in backend.instance_capabilities),
        metadata={"model_alias": specs[source_id]["model_alias"]},
    )
    for source_id, backend in backends.items()
]
```

第一版用了 stripped placeholder（`backend=""` / `capabilities=[]`），评论 5
指出 trace 的诊断价值丢了——runner 内部已经有真实 backend type 和 caps，
不该在 finalize 阶段降级。改成读真实 backend 实例的 `type(backend).name` +
`instance_capabilities`，trace 能告诉调试者"这次 run 这个 source 走的是
llama_cpp 还是 openai_compat"。`metadata.model_alias` 让消费者能交叉引用回
`specs`。

#### 7. 文件清单

```
修改
api/core/workflow/nodes/parallel_ensemble/entities.py        # 重写：TokenSourceRef + ParallelEnsembleConfig
api/core/workflow/nodes/parallel_ensemble/exceptions.py      # +MissingSpecError +InvalidSpecError +WeightResolutionError
api/core/workflow/nodes/parallel_ensemble/node.py            # 五段式 _run + per-source 校验 + extras 路由 + 真实 backend info
api/core/workflow/nodes/parallel_ensemble/runners/token_step.py  # 删 _template_prompts / TokenStepConfig.top_k；signature 切到 sources
api/core/workflow/nodes/parallel_ensemble/spi/runner.py      # +SourceInput；run() 签名 question → sources

api/tests/unit_tests/controllers/console/workspace/test_local_models_api.py  # mock runner 签名同步
api/tests/unit_tests/core/workflow/nodes/parallel_ensemble/runners/conftest.py            # +make_sources helper
api/tests/unit_tests/core/workflow/nodes/parallel_ensemble/runners/test_token_step_runner.py    # +per-source sampling 真传到 backend
api/tests/unit_tests/core/workflow/nodes/parallel_ensemble/runners/test_validation_pipeline.py  # _JudgeRunner 签名同步
api/tests/unit_tests/core/workflow/nodes/parallel_ensemble/test_node.py                         # 全面翻译 + 新增 7 个用例
api/tests/unit_tests/core/workflow/nodes/parallel_ensemble/test_spi_freeze.py                   # NoopRunner 签名同步

新增
docs/ModelNet/P3.B.3_LANDING.md
```

无删除——`runners/response_level.py` 在 P3.B.0 已经下线，本切片不再触动。

#### 8. 测试矩阵

##### `test_node.py`（29 cases）

| 用例类 | 覆盖点 |
|---|---|
| `TestEventSequence` | 3 token + done → 3 chunk + 1 closing chunk + 1 completed；`outputs.text` / `tokens_count` / `elapsed_ms` / `inputs.{sources, models}` shape |
| `TestStartupValidation` | scope mismatch / capability missing / requirements `top_logprobs > 20` / validate_selection 拒绝 / **`top_k_override` 单 source cap rejection 不影响姊妹 source** |
| `TestBackendFailures` | 1/2 backend timeout → SUCCEEDED；2/2 timeout → FAILED + `error == "all backends failed"` |
| `TestTraceStorage` | inline → `outputs.trace`；metadata → `process_data["ensemble_trace"]`；**trace 携带真实 backend class name + capabilities + model_alias metadata** |
| `TestDiagnosticsGating` | `include_token_candidates=False` → `per_model` 字段从 trace 行里剥掉 |
| `TestSpecResolution` | spec 缺失 → `MissingSpecError(source_id)`；spec 缺 prompt 字段 → `InvalidSpecError`；**sampling_params=`{top_k: -1}` → 包成 `InvalidSpecError(source_id, reason)`** |
| `TestExtraRouting`（新增） | **spec.extra 进 params.extra**；**ref.extra 覆盖 spec.extra（key 冲突），新 key 加和** |
| `TestWeightResolution` | 动态 weight 不在 pool → `WeightResolutionError`；fallback_weight 设了 → SUCCEEDED；**动态 weight = 0 / 0.0 / -1.0 / -0.0001 → `WeightResolutionError("must be > 0")`**（参数化） |
| `TestDSLSmuggle` | `model_url` / `api_key` / `api_key_env` / `url` / `endpoint` 全拒；`runner_config` 内 typo 在 runner.config_class 校验；**legacy `question_variable` / `model_aliases` 在 `extra="forbid"` 里被拒** |

##### `runners/test_token_step_runner.py`（11 cases）

新增 `test_per_source_sampling_passes_through_to_backend`：scripted 两个 source，
分别给 `top_k=12, temperature=0.3, seed=42` / `top_k=7, temperature=1.5`，断言
`backend.step_token(prompt, params)` 收到的 `params` 与各自 source 一致，且
step 0 / step 1 是同一个 frozen 实例（prove 没有重建）。

替换 `test_chat_template_invoked_for_capable_backends`：CHAT_TEMPLATE 已经移
出 token_step runner（prompt 渲染下沉到上游），那条用例的前提没了。

##### `runners/test_validation_pipeline.py`（4 cases）

`TokenStepConfig(top_k=…)` → `TokenStepConfig(max_len=10)`；其他不动。

##### `test_spi_freeze.py`（19 cases）/ `test_local_models_api.py`（9 cases）

mock runner `run(question, …)` → `run(sources, …)`，函数体不读它，签名同步即可。

#### 9. 质量门

| 门 | 命令 | 结果 |
|---|---|---|
| parallel_ensemble pytest | `cd api && uv run pytest tests/unit_tests/core/workflow/nodes/parallel_ensemble/ -v` | **151 passed**（v2 基线 137 + 新增 14：TestExtraRouting 2 + TestWeightResolution 4 参数化 + TestSpecResolution 1 + TestStartupValidation 1 + TestTraceStorage 1 + TestSpecResolution invalid sampling 1 + TestDSLSmuggle legacy 1 + per_source_sampling 1 + 调整 2） |
| 邻包回归 | `uv run pytest tests/unit_tests/core/workflow/nodes/{ensemble_aggregator,parallel_ensemble,token_model_source}/ tests/unit_tests/controllers/console/workspace/test_local_models_api.py -q` | **280 passed**（151 parallel_ensemble + 102 ensemble_aggregator + 18 token_model_source + 9 local_models_api；不退化） |
| Lint | `uv run ruff check core/workflow/nodes/parallel_ensemble/ tests/unit_tests/core/workflow/nodes/parallel_ensemble/` | All checks passed |
| pre-commit | `git commit` 触发 ruff hook | `All checks passed!` |

#### 10. 设计取舍记录

##### `SourceInput` 删 `extra` 字段（避免双通道）

第一版给 `SourceInput` 加了 `extra: dict[str, object]` 字段，让 `_build_source_inputs`
做了一次 spec.extra ⊕ ref.extra 合并（送给 aggregator 的 source_meta），同时
`params.extra` 还是空的——结果 backend 私有 knob（mirostat / repetition_penalty）
压根到不了 backend。

修复：删掉 `SourceInput.extra`，把合并直接放在 `_build_effective_params` 里
进 `TokenStepParams.extra`。这样：

- 单一通道：extras → params.extra → backend.step_token 的请求体
- aggregator 不能"意外"看到 backend 私有 knob（隔离 backend / aggregator 关
  注点的 v3 一贯原则）
- 将来 strategy 想要 source-level metadata，应该在 TokenSourceRef 加新字段而
  不是借 extra 通道

##### dict key 改成 `source_id` 而不是 alias

`backends: dict[str, ModelBackend]` 在 v2.x 是 `dict[alias, ...]`。v3 改成
`dict[source_id, ...]`，主要驱动是 ADR-v3-6 的 self-consistency 用例：同一个
模型 alias 在 token_sources 里出现两次，必须各自有独立 backend instance（独
立 sampling state、独立 trace 行、独立 weight）。trace / per_model_errors /
weights 都跟着改成按 source_id 索引。

代价：runner 内部 `model_aliases: list[str]` 参数变成"per-source 的 alias
list（可重复）"。token_step 的 `validate_selection` 用 `len(model_aliases) <
2` 而不是 `len(set(...))`，因为关键是 source 数。这个微妙处在
`spi/runner.py` 的 docstring 加注。

##### `requirements()` 返回形状而不是值

v2.x `requirements()` 用 `runner_config.top_k` 直接组装 min_top_k 的 value。
v3 把 top_k 移到 per-source，runner 没有"runner-level top_k"可填了。两条路：

A. 删掉 `min_top_k` requirement，让节点完全自己组装这个 requirement
B. `requirements()` 返回形状（`min_top_k=1` 占位 + `needs_logprobs`），节点
   在调用 `backend.validate_requirements` 之前用 per-source value 替换 placeholder

选 B：

- 运行时校验路径仍然是"runner 声明 → backend 验证"，没破契约
- 第三方 runner 不需要知道节点里发生了什么，沿用 P2.7 既有签名
- 节点的"per-source 替换"是位于已知 closed set（`min_top_k`）的简单字典
  合并，没有引入新 abstraction

##### 不在 `_collect_specs` 里 `model_validate(ModelInvocationSpec)`

`ModelInvocationSpec` 是 TypedDict（不是 BaseModel），没有 `model_validate`。
节点直接做 shape check（`isinstance(value, dict)` + 必需 key 集合 + 字段类
型）。理由跟 P3.B.1 一致：spec 跨节点经过 variable pool 序列化路径，TypedDict
是 wire shape，加一层 BaseModel 是噪音。

校验深度：必需键 + 类型；不查 alias 是否在 registry（那是 §9 step 3 的事）、
不查 sampling_params 内部字段（那是 `TokenStepParams.model_validate` 的事）。
两层职责分明。

##### Code review 修复（4 项）

1. **extras 路由**：spec.extra ⊕ ref.extra → `params.extra`（不是 `SourceInput.extra`）
   — 评论 4，已修
2. **动态 weight `> 0`**：`_resolve_weights` 加 `resolved <= 0.0` 检查 — 评论 5，已修
3. **`TokenStepConfig.top_k` 移除**：runner config 不再暴露 top_k，避免误导
   — 评论 1，已修
4. **`_finalize_outputs` 真实 backend metadata**：BackendInfo 用真实
   `type(backend).name` + `instance_capabilities` — 评论 5，已修
5. **`InvalidSpecError` 包装 sampling_params 错误**：bare ValidationError →
   带 `source_id` + `reason` — 评论 2，已修

每条都有对应的回归测试钉住（见 §8）。

#### 11. 后续

P3.B.3 落地后：

- **P3.B.4 前端重构（1.5d）**：`types.ts` 删 `model_aliases` / `question_variable`
  加 `token_sources`；删 `model-selector.tsx` / `import-model-info-button.tsx`；
  新增 `token-source-list.tsx`（行内 weight / top_k_override / fallback_weight
  三个输入框）；i18n key 改 `tokenSources.*`
- **P3.B.5 测试翻译 + 新增（1.5d）**：v2.4 `__tests__/` 全部用 `token_sources`
  fixture 替换；`response_level` runner 测试整体删除；新增端到端用例（4 份
  v3 DSL 跑 `validateDSLContent` 对应 mode）

P3.B.4 / P3.B.5 都依赖 P3.B.3 已经定好的后端 entities 形状和 SPI 签名，前后
端一起进入 ship B（token 模式完整可用）。


---

### P3.B.4 - P3.B.4 Landing — `parallel_ensemble` 前端重构（ADR-v3-16 token 模式）

> Source shard: `P3.B.4_LANDING.md`


日期：2026-04-30

#### 范围

P3.B.3 把后端 `ParallelEnsembleConfig` 从 "alias 列表 + question 变量" 重定位
到 "N 个 `TokenSourceRef`"，P3.B.4 把前端面板拉齐到同一个形状：节点不再让用户
直接选模型 alias 或填 question，而是引用上游 `token-model-source` 节点的
`outputs.spec`，让 PN.py joint vote 在 v3 形状下首次完整跑在画布上。

四件事：

1. **`types.ts` 重写**：删 `model_aliases` / `question_variable`，新增
   `token_sources: TokenSourceRef[]`（`source_id` / `spec_selector` /
   `weight: number | ValueSelector` / `top_k_override: number | null` /
   `fallback_weight: number | null` / `extra`）；后端 `TokenSourceRef`
   1:1 镜像
2. **`token-source-list.tsx` 新增**：参考 `ensemble-aggregator/input-list.tsx`
   做 InputList 行内表单（source_id / spec selector / weight 静态↔动态切换 /
   top_k_override / fallback_weight 仅在动态 weight 模式下出现）；删除
   `model-selector.tsx` + `import-model-info-button.tsx`
3. **`use-config.ts` / `panel.tsx` 重构**：去掉 `useLocalModels` + 模型能力
   静态校验（spec 在变量池运行时解析，能力检查移到后端 §9 startup pipeline）；
   新增 `handle{AddTokenSource, RemoveTokenSource, SourceIdChange,
   SpecSelectorChange, WeightChange, TopKOverrideChange, FallbackWeightChange}`
   handler；`filterSpecVar` 限定到 `outputs.spec` 形态
4. **`default.ts::checkValid` 重写**：替换 `question_variable` + `model_aliases`
   shape 校验为 `token_sources` 全套（min_length、source_id 唯一、selector
   ≥ 2 段、weight finite > 0、top_k_override 正整数、fallback_weight finite
   > 0）

依赖：P3.B.3 ✅
对齐 ADR：v3-6（per-source `top_k_override`）/ v3-15（fail-fast + fallback）
/ v3-16（去 alias 列表，按 spec 拉 backend）

#### 不做（按 v3 计划切片）

- v2.4 单测全量翻译 + 端到端：P3.B.5（本切片仅做"让 type-check / vitest 跑通"
  的最小翻译，新增组件级用例 1 份；`response_level` runner 测试整体删除留给
  P3.B.5）
- 4 份 v3 DSL 示例 + EXTENSION_GUIDE 升级：P3.C.1
- `DEVELOPMENT_PLAN.md` v2.4 钩子全量化 + v3.1 状态切换：P3.C.2

#### 1. `types.ts` — `TokenSourceRef`

```ts
export type TokenSourceRef = {
  source_id: string
  spec_selector: ValueSelector
  weight: number | ValueSelector
  top_k_override: number | null
  fallback_weight: number | null
  extra: Record<string, unknown>
}

export type ParallelEnsembleConfig = {
  token_sources: TokenSourceRef[]
  runner_name: string
  runner_config: ConfigBlob
  aggregator_name: string
  aggregator_config: ConfigBlob
  diagnostics: DiagnosticsConfig
}
```

| 字段 | 默认 | 备注 |
|---|---|---|
| `source_id` | required | 同节点内唯一；后端 `_check_source_id_unique` 在 schema 层兜底 |
| `spec_selector` | required (≥ 2 段) | 形如 `["<token_model_source_node_id>", "spec"]`，与 graphon `VariableSelector` 同形 |
| `weight` | `1` | 与 `AggregationInputRef.weight` 一致：finite 数 OR `ValueSelector` 形 `list[string]`；`> 0` schema 校验 |
| `top_k_override` | `null` | ADR-v3-6：consumer-side re-pin top_k；其他采样 knob 跟随上游 spec |
| `fallback_weight` | `null` | None = fail-fast；显式数值进 ADR-v3-15 graceful-degrade |
| `extra` | `{}` | per-source pass-through metadata |

##### 默认 runner / aggregator 切到 token 模式

```ts
export const DEFAULT_RUNNER_NAME = 'token_step'
export const DEFAULT_AGGREGATOR_NAME = 'sum_score'
```

P3.B.3 后端只剩 `token_step` runner + `sum_score` / `max_score`（token-scope）
aggregator；继续把默认值留在 `response_level` + `majority_vote` 会让"新建节点
加 source 后保存"的 DSL 在运行期必炸（runner 找不到）。Code review 评论 #1
钉死的问题。

##### `FORBIDDEN_DSL_KEYS` 收敛

只保留 SSRF / 凭证 5 项（`model_url` / `api_key` / `api_key_env` / `url` /
`endpoint`）。`model_aliases` 防护下线——后端 `extra="forbid"` 在 schema
层就拦下来了，前端再加一层是冗余。

#### 2. `components/token-source-list.tsx` — InputList 形态

```
<row>
  source_id 输入框          [×] 移除
  spec selector picker     （filter: type ∈ {object, any} && tail === 'spec'）
  weight: <Number|Variable> ↔ <input | picker>
  top_k_override: <input>  （留空 = 沿用 spec）
  fallback_weight: <input>  （仅动态 weight 模式下出现）
</row>
<button> 添加 token 源 </button>
```

- **结构借鉴** `ensemble-aggregator/input-list.tsx`（同 v3-15 weight 静态↔动态
  toggle 语义）；与 ensemble-aggregator 不同的是多了 `top_k_override` 行
- **静态↔动态切换**：从静态切到动态时 `weight = []`（picker 未指向状态）；
  从动态切回静态时 `weight = 1` **且** `fallback_weight = null`（fallback
  只在动态分支有意义，留下旧值会让面板看起来配错）
- **fallback 仅在动态模式渲染**：动态 weight 解析失败时才轮到 fallback 出场，
  在静态行里展示这个字段会误导用户

##### `filterSpecVar` 收紧到 `outputs.spec`

```ts
const filterSpecVar = useCallback(
  (varPayload: Var, valueSelector: ValueSelector) => {
    if (!SPEC_VAR_TYPES.includes(varPayload.type))
      return false
    const last = valueSelector[valueSelector.length - 1]
    return last === 'spec'
  },
  [],
)
```

只检查类型（object / any）会把 `http_request.body` 这种普通对象变量也放进来，
运行期 `ModelInvocationSpec.model_validate` 才抛错。Code review 评论 #2
要求 picker 在编辑期就拒绝非 `outputs.spec` 选择，避免用户交付一个看上去配
好其实必炸的 DSL。`SPEC_VAR_TYPES` 含 `VarType.any` 是兜底——上游若为
第三方节点输出类型未定，pool 经常推断为 any。

#### 3. `use-config.ts` — handler 翻新 + Registry 校验

##### 新增 7 个 handler

```ts
handleAddTokenSource()
handleRemoveTokenSource(index)
handleSourceIdChange(index, value)
handleSpecSelectorChange(index, selector)
handleWeightChange(index, number | ValueSelector)
handleTopKOverrideChange(index, number | null)
handleFallbackWeightChange(index, number | null)
```

替代 v2.4 的 `handleQuestionVariableChange` + `handleModelAliasesChange`。
默认 `source_id` 命名 `source_1` / `source_2` / …（与 ensemble-aggregator
的 `model_1` / `model_2` 风格一致），跳过已有 id 避免冲突。

##### `validationIssues` — registry membership + scope match

```ts
if (runnerName && runnersReady && !selectedRunner) {
  issues.push({
    severity: 'error', field: 'runner_name',
    i18n_key: 'parallelEnsemble.errors.runnerNotRegistered',
  })
}
if (aggregatorName && aggregatorsReady && !selectedAggregator) {
  issues.push({
    severity: 'error', field: 'aggregator_name',
    i18n_key: 'parallelEnsemble.errors.aggregatorNotRegistered',
  })
}
if (selectedRunner && selectedAggregator
    && selectedAggregator.scope !== selectedRunner.aggregator_scope) {
  issues.push({
    severity: 'error', field: 'aggregator_name',
    i18n_key: 'parallelEnsemble.errors.aggregatorScopeMismatch',
  })
}
```

`*Ready` 守护防止"registry 还在 fetch → 把任何已选名字都误报成 unknown"。
Code review 评论 #1 的子项："对 registry 中不存在的 runner/aggregator 显式
报错"——跨部署粘贴 DSL 是真实场景（v2.4 deployment 的 `response_level` DSL
被粘贴到 v3 deployment 时，面板必须立刻报错而不是等到运行期）。

##### `validationIssues` 删除模型能力子集检查

v2.4 的 use-config 用 `models.find(...)` 做能力子集校验，依赖 `useLocalModels`。
ADR-v3-16 后能力校验下沉到后端 §9 startup pipeline（spec 必须先在 variable
pool 解析才有 alias 可查），前端无法静态完成；所以前端直接放弃这一项，
runner / aggregator 注册校验 + scope match 是面板能做的全部。

#### 4. `default.ts::checkValid` — token_sources 全套校验

```
token_sources:
  Array.isArray + length ≥ minSources（token_step ≥ 2）
  source_id: 非空字符串、trim 后唯一
  spec_selector: ≥ 2 段、每段非空字符串
  weight: 静态分支 → finite > 0 + 非 bool；动态分支 → ≥ 2 段选择器
  top_k_override: null 或正整数（rejecting bool / NaN / non-int）
  fallback_weight: null 或 finite > 0
runner_name / aggregator_name: 非空字符串
runner_config / aggregator_config: 普通对象
diagnostics: storage allowlist + max_trace_tokens > 0
SSRF 5 键 forbid（保留）
```

策略与后端 `TokenSourceRef` 字段校验一致；UI 永远不产生这些 bad shape，
但 DSL 粘贴 / 手动编辑 yaml 会，所以前端早一步报错避免后端 ValidationError
的 raw 文本传给用户。

#### 5. `panel.tsx` — 三段式重排

```
<Field tokenSources>      <- TokenSourceList + renderIssue('token_sources')
<Field runner>            <- RunnerSelector + 可选 DynamicConfigForm(runner_config)
<Field aggregator>        <- AggregatorSelector + renderIssue('aggregator_name')
                              + 可选 DynamicConfigForm(aggregator_config)
<Split />
<Field diagnostics>       <- DiagnosticsConfigForm（supportFold）
<Split />
<OutputVars>              <- text / tokens_count / elapsed_ms (+ trace iff inline)
```

去掉 v2.4 的 "Section 1 Question variable" + "Section 2 Models"，三轴构图改为
"sources / runner / aggregator"。`renderIssue` 在 source 级（`token_sources`）
和 aggregator 级（`aggregator_name`）surfaces validation issues，错误标红与
v2.4 风格一致（`text-text-warning-secondary` 设计 token）。

`<TokenSourceList>` 嵌进 Field 时用 `<>fragment</>` 包裹两个子节点，避免
TS 报 "Element 不能赋给 string"——这是 Field 的 `children: ReactNode`
类型在多子节点场景下需要的常见 workaround。

#### 6. `node.tsx` — 画布 chip

```ts
const sourceCount = ensemble?.token_sources?.length ?? 0
if (sourceCount === 0) return null
// chip: "{runnerName}" + "{count} sources"
```

跟 v2.4 一样：fresh 节点不渲染 chip（仅显示 title + icon），添加 source 后
chip 出现。`modelCount_*` i18n 键改为 `sourceCount_*`。

#### 7. i18n（en-US + zh-Hans）

##### 删除

- `nodes.parallelEnsemble.questionVariable` / `questionVariableTooltip`
- `nodes.parallelEnsemble.models` / `modelsPlaceholder` / `modelsSelectedCount_*`
  / `modelsTooltip` / `noModelsAvailable`
- `nodes.parallelEnsemble.modelCount_one` / `_other`（→ `sourceCount_*`）
- `nodes.parallelEnsemble.importModelInfo` / `importToast.*`
- `nodes.parallelEnsemble.errorMsg.duplicateModelAlias` /
  `modelAliasMustBeString` / `modelMissingCapability` /
  `runnerNeedsTwoAliases`

##### 新增

- `nodes.parallelEnsemble.tokenSources.title` / `tooltip` / `addSource` /
  `sourceIdPlaceholder` / `weight` / `weightModeNumber` / `weightModeVariable`
  / `weightToggleAria` / `topKOverride` / `topKOverrideTooltip` /
  `topKOverridePlaceholder` / `fallbackWeight` / `fallbackWeightTooltip` /
  `fallbackWeightPlaceholder`
- `nodes.parallelEnsemble.sourceCount_one` / `_other`
- `nodes.parallelEnsemble.errorMsg.{runnerNeedsTwoSources, tokenSourceMalformed,
  sourceIdRequired, duplicateSourceId, specSelectorRequired,
  weightSelectorMalformed, weightMustBePositive, topKOverrideInvalid,
  fallbackWeightInvalid}`
- `parallelEnsemble.errors.{runnerNotRegistered, aggregatorNotRegistered}`

##### 改写

- `outputVars.tokensCount`：删掉 "（响应级是聚合文本长度）" 文案——P3.B.0
  把 `response_level` runner 下线后这句已经没语义
- `runnerTooltip`：改写为 token-mode-only，附一句 "响应级集成请使用
  ensemble-aggregator 节点" 引导用户

`parallelEnsemble.errors.{tooFewModels, thinkNoModels, thinkOffWithThinkModels,
modelMissingCapability}` 保留——后端 `_validate_at_startup` 仍然 emit 这些
i18n_key（结构化错误回传的语义层），前端是消费方。

#### 8. 测试

##### 新增 `components/__tests__/token-source-list.spec.tsx`（14 cases）

| 类别 | 用例 |
|---|---|
| 路由 | source_id 编辑 / spec selector 选择（数组） / 拒绝 string emit / top_k_override 输入 + clear / 拒绝 0 / 负数 / 非整数 / add + remove / readonly 隐藏 add+remove |
| Weight 切换 | 静态 weight 输入 / 空 → 1 / type=number 委托 / 静态→动态 reset 到 [] / 动态→静态 reset 到 1 + 清 fallback / fallback 仅在动态渲染 |
| fallback 输入 | 空 → null / 数字 → 数字 |

##### 翻译 `__tests__/panel.spec.tsx`（17 cases）

`token-source-list` mock 替代 `model-selector` mock；fixture pin 到
`token_step` + `sum_score` 配对（避免与 builder 的 runners 不一致触发
"unknown runner" 误报）；输出变量 / 诊断折叠 / 路由（add-source /
rename-source / pick-spec / set-weight / set-top-k / set-fallback /
change-runner / change-aggregator / change-diagnostics）全覆盖。

##### 翻译 `__tests__/requirements-validation.spec.tsx`（11 cases）

scope mismatch 用例保留；删掉 capability subset 用例（前端不再做该检查）；
新增：

- `runnerNotRegistered` / `aggregatorNotRegistered`：registry 加载完后报错
- `filterSpecVar` 三连：accept `outputs.spec` / reject `http_request.body` /
  reject 非 object 类型尾随 spec 选择器

##### 删除 `components/__tests__/{model-selector, import-button}.spec.tsx`

对应组件下线后单测无意义；P3.B.5 不再补回。

#### 9. 文件清单

```
修改
web/app/components/workflow/nodes/parallel-ensemble/types.ts          # TokenSourceRef + token_sources + 默认值切到 token_step/sum_score
web/app/components/workflow/nodes/parallel-ensemble/default.ts         # checkValid 全量翻新
web/app/components/workflow/nodes/parallel-ensemble/use-config.ts      # handler 翻新 + filterSpecVar 收紧 + registry 校验
web/app/components/workflow/nodes/parallel-ensemble/panel.tsx          # token_sources / runner / aggregator 三段式
web/app/components/workflow/nodes/parallel-ensemble/node.tsx           # sourceCount 替代 aliasCount
web/i18n/en-US/workflow.json                                           # tokenSources.* + sourceCount + registry-not-registered
web/i18n/zh-Hans/workflow.json                                         # 同步 zh

web/app/components/workflow/nodes/parallel-ensemble/__tests__/panel.spec.tsx                 # 翻译到 token-source-list
web/app/components/workflow/nodes/parallel-ensemble/__tests__/requirements-validation.spec.tsx  # 翻译 + 新增 registry/filter 用例

新增
web/app/components/workflow/nodes/parallel-ensemble/components/token-source-list.tsx
web/app/components/workflow/nodes/parallel-ensemble/components/__tests__/token-source-list.spec.tsx
docs/ModelNet/P3.B.4_LANDING.md

删除
web/app/components/workflow/nodes/parallel-ensemble/components/model-selector.tsx
web/app/components/workflow/nodes/parallel-ensemble/components/import-model-info-button.tsx
web/app/components/workflow/nodes/parallel-ensemble/components/__tests__/model-selector.spec.tsx
web/app/components/workflow/nodes/parallel-ensemble/components/__tests__/import-button.spec.tsx
```

`use-registries.ts` 没动——`useLocalModels` 在文件里仍然存在（registry
fetch 钩子是个 free 函数），只是 `use-config.ts` 不再调用它。`localModels`
console endpoint 还在被其他地方使用（如 token-model-source 的 `model-alias-select`），
留着无害。

#### 10. 质量门

| 门 | 命令 | 结果 |
|---|---|---|
| TypeScript | `pnpm exec tsc --noEmit -p tsconfig.json` | exit 0，0 errors |
| ESLint | `pnpm exec eslint app/components/workflow/nodes/parallel-ensemble` | 0 errors，1 warning（`token-source-list.tsx:150` `react/no-array-index-key`，与 `ensemble-aggregator/input-list.tsx:134` 同款，acceptable） |
| Vitest | `node node_modules/vitest/dist/cli.js run app/components/workflow/nodes/parallel-ensemble` | **71 passed**（panel 17 + requirements-validation 11 + token-source-list 14 + 4 个保留组件测试 29） |

#### 11. Code review 修复（4 项）

1. **默认 runner/aggregator** 改到 `token_step` + `sum_score`（types.ts），
   并在 use-config 加 registry membership 校验 + i18n key
   `runnerNotRegistered` / `aggregatorNotRegistered` — 评论 1，已修
2. **`filterSpecVar` 收紧到 `outputs.spec`** 形态：selector tail === 'spec'
   + 类型检查（use-config.ts），3 个 hook 级回归测试钉住 — 评论 2，已修
3. **`token-source-list.spec.tsx` 新增**（14 cases），覆盖 weight toggle /
   top_k / fallback / readonly / filter 透传 — 建议 1，已修
4. **i18n 文案 token-mode-only**：`outputVars.tokensCount` /
   `runnerTooltip`（en + zh）改写，删 response-level 描述 — 建议 2，已修

#### 12. 设计取舍记录

##### 默认值改到 `token_step` + `sum_score` 而不是空字符串

第一版考虑过把默认 runner / aggregator 留空（让用户必须主动选择），避免
后端能力变更时前端默认值发硬绑定。但 panel UX 跑通需要 `selectedRunner`
非空才会渲染 dynamic-config-form / 计算 requiredScope，所以"空字符串
默认"会让新建节点立刻处于 "请选择 runner" 的红字状态——既不友好也不
反映 v3 现状（后端只有 token_step 一个 runner）。改成 `token_step` +
`sum_score` 后：

- 新建节点立刻可保存（加 1 个 source 即可）
- 添加新 runner/aggregator 时只要更新 `DEFAULT_*_NAME` 即可
- registry 校验 + scope match 兜底，万一后端改名前端不会静默配错

##### 删除模型能力静态校验而不是迁移到 spec resolution

v2.4 的能力校验依赖 `models.find(alias => ...)`，alias 是面板字段。v3 后
alias 隐藏在 `ModelInvocationSpec` 里，要在前端复现校验需要：

A. 在前端做 spec selector 的"伪解析"（snapshot 上游 token-model-source
   节点的 `model_alias` config），但跨节点配置耦合是面板层面的反模式
B. 依赖运行期 variable pool（前端没有这个能力）

两条路都不好走。后端 §9 startup pipeline 在运行期能拿到真 spec，校验
更准。前端弃权，把"能力不匹配"当做运行期 ValidationError 在面板上的
结构化展示项处理（`parallelEnsemble.errors.modelMissingCapability`
i18n key 保留就是给后端回传用的）。

##### `panel.spec.tsx` mock 掉 `TokenSourceList` 而不是真渲染

panel.spec 关注的是"面板把哪些 prop 喂给哪个子节点 / 哪个子节点的回调
路由到哪个 handler"，不是 TokenSourceList 内部行为。把 TokenSourceList
mock 成 stub，露出 6 个测试按钮（rename-source / pick-spec / set-weight
/ set-top-k / set-fallback / add-source）就足够断言路由。

TokenSourceList 自身的真实渲染 / 静态↔动态切换 / 边界值由
`token-source-list.spec.tsx` 单独覆盖（评论建议 1 直接钉的事）。两个文件
分工：panel = 三轴构图，TokenSourceList = 行内交互。

#### 13. 后续

P3.B.4 落地后：

- **P3.B.5 测试翻译 + 新增（1.5d）**：v2.4 后端 `__tests__/`（事件序列 /
  §9 / storage / DSL 防护）尾巴清理；新增 P3.B.3 / P3.B.4 端到端用例
  （4 份 v3 DSL 跑 `validateDSLContent`）；本切片已经把前端 panel /
  requirements-validation / token-source-list 全部就位，P3.B.5 主要是
  后端 + DSL 维度
- **🟢 ship B**：P3.B.0–P3.B.5 全绿后 token 模式完整可用，PN.py 算法
  首次端到端跑在 Dify 画布上

P3.B.4 与 P3.B.3 共同构成 ship B 的关键 patches；前后端形状一致后下一步
就是 4 份 DSL（P3.C.1）+ 文档钩子收尾（P3.C.2）。


---

### P3.B.5 - P3.B.5 Landing — `parallel_ensemble` 测试翻译 + 后端新增（ship B 收尾）

> Source shard: `P3.B.5_LANDING.md`


日期：2026-04-30

#### 范围

P3.B.3 把后端 schema 切到 `token_sources` 形态时已经一并把 `__tests__/`
重写到新 fixture，P3.B.4 把前端 `panel.spec.tsx` / `requirements-validation.spec.tsx`
翻到 `token-source-list` 并删掉 `model-selector.spec.tsx`。本切片是
ship B 收尾：把 P3.B.5 三件事剩下的"backend 直接断言"窟窿补上 +
清理一处 v0.2 的 stale docstring。

P3.B.5 三件事现状：

1. **v2.4 `__tests__/` 翻译**：✅ P3.B.3 / P3.B.4 已经做了，本切片只是
   清理 stale comment（`runners/test_validation_pipeline.py` 文头）。
   `model_aliases` 标识符 / `response_level` runner 源文件已经清掉；
   `model_aliases` 在 SPI `validate_selection(config, model_aliases, registry)`
   里是参数名，v3 仍在用，不属于待删项
2. **新增后端 4 件**：本切片实际工作面，10 个新 test cases 落到
   `test_node.py`
3. **前端 panel 翻译 + 删 model-selector.spec**：✅ P3.B.4 已完成，
   本切片复核未回退

#### 不做（按 v3 计划切片）

- 4 份 v3 DSL（response_level v3 × 2 + token_level × 2）+ EXTENSION_GUIDE 升级：
  P3.C.1
- `DEVELOPMENT_PLAN.md` v2.4 钩子全量化 + v3.1 状态切换：P3.C.2
- 集成测试 (CI-only)：P3.1（独立切片）

#### 1. 后端新增 — `TestEffectiveParams`（2 cases）

`_build_effective_params` 把 `spec.sampling_params` ⊕ `TokenSourceRef.top_k_override`
合并成每 source 一份 frozen `TokenStepParams`。两条不变量：

- **`top_k_override` 覆盖 `top_k`**：consumer-vocab 优先；其他 sampling
  knob（temperature / top_p / stop / seed / max_tokens）原样从 spec 透
  传
- **per-source 隔离**：每个 source 拿到自己的 `TokenStepParams` 实例，
  避免 sibling 共享 ref 时一个 backend 的状态污染同 batch 的其他 fan-out

##### `test_top_k_override_wins_over_spec_top_k`

`spec.sampling_params.top_k = 5`，`ref[0].top_k_override = 25`，`ref[1]`
不设 override。Capturing runner 把 `sources[sid]["params"]` 直接 stash
到外层 dict，断言：

```python
captured["s0"].top_k == 25  # override wins
captured["s1"].top_k == 5   # fallthrough
```

钉死 ADR-v3-6。`TestStartupValidation::test_top_k_override_drives_per_source_requirement`
之前已经间接见证（§9 cap 在 25 处弹出），但那条只能证明 `validate_requirements`
拿到了 25——不能区分"merge 把 25 写进 params" 与 "merge 把 5 写进 params 但
override 走另一条路径到 cap 检查"。本测试直接读 params 字段，把这两种
实现路径分开。

##### `test_per_source_sampling_reaches_backend`

两条 source 各自 spec 不同 sampling 行（s0: `top_k=5/T=0.7/top_p=0.9/stop=["</s>"]/seed=42`，
s1: `top_k=3/T=1.5/top_p=0.5/stop=["END"]/seed=99`），capturing runner
读 `sources[sid]["params"]` 后逐字段断言。三件事一并钉住：

- **per-source sampling 真传**：spec 行的每个 knob 都到 params 上
  （`step_token` 调用前的最后一站）
- **list → tuple 强制**：`stop=["</s>"]` 落成 `("</s>",)`，与
  `TokenStepParams.stop: tuple[str, ...]` 的不可变契约对齐
- **不跨源 alias**：`captured["s0"] is not captured["s1"]` —— 共享
  ref 会让 s0/s1 的 stop tuple 相等，本断言用 identity 而不是 equality
  捕捉

#### 2. 后端新增 — `TestSpecResolution::test_invalid_spec_non_dict_resolved_value_raises`

`spec_selector` 解析到非 dict 值（string / int / list）→ `InvalidSpecError`
带 source_id 上抛；变量真缺失 → `MissingSpecError`（已有的
`test_missing_spec_raises` 覆盖）。两条边界都参数化进同一个测试，避免
"present but malformed" 与 "missing" 走错分支：

```python
@pytest.mark.parametrize(
    "bad_value",
    ["string-not-dict", 42, [1, 2, 3], None],
    ids=["string", "int", "list", "none"],
)
def test_invalid_spec_non_dict_resolved_value_raises(self, bad_value):
    ...
    if bad_value is None:
        with pytest.raises(MissingSpecError) as miss_exc:
            list(node._run())
        assert miss_exc.value.source_id == "s1"
        return
    with pytest.raises(InvalidSpecError) as exc:
        list(node._run())
    assert exc.value.source_id == "s1"
    assert "expected dict" in exc.value.reason
```

`bad_value=None` 这条故意不 add 到 pool，让 selector 真 miss——把"missing
vs malformed"的分类拍在一起，避免后续把 InvalidSpecError 路径误改成
silent-coerce 或 fallback。

#### 3. 后端新增 — `TestWeightResolution::test_dynamic_weight_non_finite_rejected`

`_resolve_weights` 在 `isinstance(value, (int, float))` 之后接 `math.isfinite`
guard：NaN 是 float 但不 finite；±Infinity 同理。三个值参数化：

```python
@pytest.mark.parametrize(
    "bad_value",
    [float("nan"), float("inf"), float("-inf")],
    ids=["nan", "+inf", "-inf"],
)
def test_dynamic_weight_non_finite_rejected(self, bad_value):
    ...
    assert exc.value.source_id == "s0"
    assert "not finite" in exc.value.reason
```

之前的 `test_dynamic_weight_non_positive_rejected` 只覆盖 0 / 负数（走
`> 0` 分支）。NaN 走 isfinite 分支：`NaN < 0` 是 False，所以 NaN 误绕过
`> 0` guard 会被 isfinite 接住——本测试钉死分支顺序，把"non-finite"
和"non-positive"两个错误信号分开。

补一个 `test_dynamic_weight_non_finite_falls_back`：fallback 配置时 NaN
仍降级到 `fallback_weight`，与已有的"missing variable + fallback"路径
对齐 ADR-v3-15 的 graceful-degrade 契约。

#### 4. 文档清理 — `runners/test_validation_pipeline.py`

文头 docstring 还在说 "v0.2 (only `token_step` / `response_level` are)"。
`response_level` runner 在 P3.B.0 已经被 ADR-v3-9 拆到独立的
ensemble-aggregator 节点，留旧文案会让新加 runner 的开发者理解错"in-box
runner 集合"的现状。改写为：

```
post-ADR-v3-9 only ``token_step`` is registered; the response-mode
runner moved out to the standalone ensemble-aggregator node
```

测试代码本身不动——`_JudgeRunner` 描述的 `validate_selection`
cross-field 校验契约 v3 仍然有效，只是 stale 的"v0.2 in-box runner"
描述不再准确。

#### 5. 文件清单

```
修改
api/tests/unit_tests/core/workflow/nodes/parallel_ensemble/test_node.py
   # +TestEffectiveParams 类（2 cases）
   # +TestSpecResolution.test_invalid_spec_non_dict_resolved_value_raises（4 参数）
   # +TestWeightResolution.test_dynamic_weight_non_finite_rejected（3 参数）
   # +TestWeightResolution.test_dynamic_weight_non_finite_falls_back
api/tests/unit_tests/core/workflow/nodes/parallel_ensemble/runners/test_validation_pipeline.py
   # 文头 docstring 清理 v0.2 stale reference

新增
docs/ModelNet/P3.B.5_LANDING.md
```

无新增 / 删除产品代码——本切片纯属测试维度。

#### 6. 质量门

| 门 | 命令 | 结果 |
|---|---|---|
| 后端 pytest（parallel_ensemble 全套） | `uv run --project api pytest api/tests/unit_tests/core/workflow/nodes/parallel_ensemble -q` | **161 passed**（test_node.py 30 → 40） |
| 后端 pytest（test_node.py 单文件） | `uv run --project api pytest api/tests/unit_tests/core/workflow/nodes/parallel_ensemble/test_node.py` | **40 passed** |
| 前端 vitest（parallel-ensemble 全套） | `vitest run app/components/workflow/nodes/parallel-ensemble` | **71 passed** / 7 files（与 P3.B.4 一致，无回归） |

新增的 10 个 test cases 全部一次通过。

#### 7. 设计取舍记录

##### 用 capturing runner 而不是真 `TokenStepRunner`

`TestEffectiveParams` 关心的是"node 的 `_build_effective_params` 把
什么塞给 runner"，不是 `TokenStepRunner` 的 fan-out 行为。在 unit 层
拉真 runner 会把 ThreadPoolExecutor / aggregator / backend.step_token
全卷进来——一旦 backend 调用变了或者 runner 内部 fan-out 顺序变了，
本测试就误报。Capturing runner 直接 snapshot `sources[sid]["params"]`
后立即 yield Done，把"node 准备 params"和"runner 用 params"两件事
分开测试。

`TokenStepRunner` 自己的 fan-out / step 流程在
`runners/test_token_step_runner.py` 里有 8 个独立 case 覆盖（包括
backend.step_token 的 mock + 候选解析 + diagnostics），不必在 node 层
重复。

##### 把"missing"和"malformed"拍在同一个参数化

`spec_selector` 解析时 None（缺失）走 MissingSpecError，其他非 dict 值
走 InvalidSpecError。如果分两个测试函数写，未来有人把 `_resolve_specs`
的 None 分支误改成 `InvalidSpecError(source_id, reason="None")`——两个
测试都会过（因为各自只检查自己分支的 exception 类型）。

参数化里把 `bad_value=None` 显式分到 MissingSpecError 断言，剩下三个
非 dict 值落 InvalidSpecError。一旦分类错乱，参数化会把分歧暴露成
"是 None 却进了 InvalidSpecError 分支"或反向——比起两个独立测试更难
误改进绿。

##### 非 finite 权重单测的存在意义

后端 `_resolve_weights` 的 isfinite guard 现在被
`test_dynamic_weight_non_positive_rejected` 间接覆盖一部分（0 / 负数
都是 finite），但 NaN / ±Infinity 是真正只有 isfinite 能挡的值——
isfinite guard 被误删的话，NaN 会 silent 进入 weighted-sum
（NaN ⊕ x = NaN，把整张投票表毒掉），±Infinity 会一票否决 sibling。
单独一个测试钉住这条分支比"靠 ADR review 抓回归"安全得多。

#### 8. 后续

- **🟢 ship B**：P3.B.0 → P3.B.5 全绿，token 模式完整可用。token-model-source
  → parallel-ensemble 端到端用 PN.py joint vote 算法首次跑在画布上；
  per-source sampling 真生效（不再被 backend 实例化时的全局值覆盖）
- **P3.C.1**（1d）：4 份 v3 DSL（response_level_ensemble_v3 × 2 +
  token_level_ensemble × 2）落到 `examples/`，各自跑 `validateDSLContent`
  + `model_validate`；EXTENSION_GUIDE 加章节（`TokenStepParams.extra`
  第三方 sampling 维度示例 / `SourceAggregationContext` vs
  `BackendAggregationContext` 选用指南 / `ModelBackend` 子类化模板）
- **P3.C.2**（0.5d）：`DEVELOPMENT_PLAN.md` v2.4 钩子全量化 +
  `BACKEND_CAPABILITIES.md` 加 "token-model-source 节点贡献的
  spec → backend 资格映射" 一节 + `DEVELOPMENT_PLAN_v3.md` 升级到
  v3.1 状态

P3.B.5 收尾后下一动作是 P3.C.1 的 4 份 DSL；ship B 同时点亮，意味着
v3 token 模式从此对最终用户可见。


---

