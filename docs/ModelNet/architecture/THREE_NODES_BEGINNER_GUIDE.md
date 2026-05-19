# 三节点开发思路（新人版）

> 读者画像：计算机本科生，**没有接触过 Dify**，刚刚拿到这个 fork。
> 目的：用一份文档让你看懂"我们为什么要加这三个节点 + 它们要怎么落进 Dify"。
>
> 配套文档：
> - `docs/ModelNet/active/ROADMAP.md` + `docs/ModelNet/active/TASKS.md` — 当前活跃路线和执行清单
> - `docs/ModelNet/architecture/EXTENSION_GUIDE.md` — 扩展点详细参考（spec 的操作手册版）
> - `docs/ModelNet/architecture/EXTENSIBILITY_SPEC.md` — backend / runner / aggregator SPI 契约
> - `docs/ModelNet/research/references/PN.py` — 核心算法验证版

---

## 一、先建立心智模型：Dify workflow 是什么

把 Dify 想象成一个**给 LLM 应用做的"乐高拼图"**——和小学生玩的 Scratch、或者你可能见过的 ComfyUI（画图节点编辑器）是同一种东西。

- 画布上拖几个**节点**（Start、LLM、End），用**线**把它们连起来。
- 每条线代表"上一个节点的某个输出变量"流到"下一个节点的某个输入字段"。
- 用户点"运行" → 后端按拓扑顺序一个一个跑节点，最后吐结果。

```
┌───────┐    question     ┌────────┐  answer   ┌──────┐
│ Start │ ───────────────►│  LLM   │ ─────────►│ End  │
└───────┘                 └────────┘           └──────┘
```

**关键术语**：

| 术语 | 含义 |
|---|---|
| 节点（Node） | 画布上的一个方块；代码层面 = 一个 Python 类 + 一个 React 组件 |
| DSL | workflow 的 YAML 描述文件，可导出/导入/复制 |
| variable pool | 节点之间传值的"共享内存"。上游节点跑完把输出塞进去，下游节点读它 |
| GraphEngine | 后端执行引擎，按拓扑顺序调度节点；遇到分叉会开线程池并发 |

---

## 二、为什么必须改源码，不能写"插件"

Dify 有插件系统，但**插件只能加 4 类东西**：模型供应商、工具、Agent 策略、HTTP 端点。**插件不能新增 workflow 节点类型。**

证据在 `api/core/workflow/node_factory.py` 的 `register_nodes()`——它只扫描两个包：
1. `graphon.nodes`（外部 pip 包里的内置节点：LLM、IF-ELSE、Code、Loop 等）
2. `api/core/workflow/nodes/`（仓库内可改的节点）

没有插件钩子。所以**唯一路线是把项目 fork 下来，在第 2 个目录里加节点**。这也是当前 `/home/xianghe/temp/dify` 仓库的状态——它已经是 Dify 的 fork。

---

## 三、你要加的三个节点 —— 算法动机先讲清楚

我们的研究算法 `PN.py`：N 个本地 LLM 同时解一道题，**在每一步生成 token 时**把各家模型的 top-k logit 汇总投票，选出共识 token，循环到结束。这叫 **token 级集成**。

但工程化进 Dify 时，发现一个硬约束：

> Dify 的流式块（`StreamChunkEvent`）**只会发给前端 UI 显示**，**不会写进 variable pool**。下游节点只能在上游"整体跑完"之后，从最终结果里读输出。

意思是：**不可能让一个聚合节点接收 N 个 LLM 节点的"逐 token 流"**。逐 token 协作必须由"自己负责调模型 + 自己投票"的一个**胖节点**完成。

所以三节点分工是这样的：

| 节点 | 干什么 | 输入 | 输出 | 类比 |
|---|---|---|---|---|
| **token-model-source** | 描述"用哪个模型 + 什么 prompt"，**不调模型** | 来自 Start 的 question | 一个叫 `spec` 的"调用规格"对象 | 点菜单上写"我要北京烤鸭"，但还没下单 |
| **parallel-ensemble** | 收 N 个 spec → 自己开线程并发调 N 个 llama.cpp → 每步投票 → 流式吐 token | N 个 `spec` | `text`, `tokens_count`, `elapsed_ms`，可选 `trace` | 厨房里同时炒 N 个菜，每口尝一下选最合口的 |
| **response-aggregator** | 收 N 个**已完整生成**的字符串 → 调一个聚合 LLM 综合 | N 个 `text` + 权重 + 聚合模型 | `text`, `metadata` | 4 个翻译同事各交一份稿子，主编写终稿 |

画在画布上是这样：

### Token 级路径（一次推理）

```
Start ──► token-model-source(q1)─┐
       ├► token-model-source(q2)─┤
       ├► token-model-source(g4)─┼─► parallel-ensemble ─► End
       └► token-model-source(L3)─┘
```

### 响应级路径（先各跑完，再交给聚合模型综合）

```
Start ──► LLM(modelA) ─┐
       ├► LLM(modelB) ─┼─► response-aggregator ─► End
       └► LLM(modelC) ─┘
```

> ⚠ **反直觉的点**：响应级路径**根本不需要新建"并联容器"节点**——Dify 的 GraphEngine 看到一个节点拉出 N 条边到 N 个下游，会自动开线程池并发跑这 N 个节点。你只需要新建一个"接收多上游"的聚合节点就够了。
>
> 另一个容易混淆的点：早期设计里 `response-aggregator` 做过 `majority_vote` / `concat` 这类固定策略；当前实现已经升级成 **synthesis-only**：它读取多路完整回复，构造一个合成 prompt，然后调用用户在面板里配置的聚合模型输出最终答案。

---

## 四、后端怎么写（从"最小节点"到当前三节点）

Dify/graphon 里的一个最小可运行节点，通常就是 `api/core/workflow/nodes/<节点名>/` 下这几类文件：

```
api/core/workflow/nodes/token_model_source/
├── __init__.py        # 触发自动注册
├── entities.py        # NodeData 配置 schema（Pydantic 模型）
├── node.py            # 节点主类，写 _run()
├── exc.py             # 自定义异常
└── (可选) registry/   # 如果有"策略可插拔"，放这里
```

当前三节点里，`token_model_source` 还接近这个最小形态；`parallel_ensemble` 已经是一个小框架，下面还有 `backends/`、`runners/`、`aggregators/`、`registry/`、`spi/`；`response_aggregator` 则接入了 Dify 原生 LLM 调用链，所以要由 factory 注入模型实例、prompt serializer、file saver 等依赖。

无论复杂度如何，**核心还是两个文件**：

### 1. `entities.py` —— 节点的"配置长什么样"

```python
class TokenModelSourceNodeData(BaseNodeData):
    type: NodeType = "token-model-source"          # ⚠ 必填
    model_alias: str                               # 用 model_net.yaml 里哪个别名
    prompt_template: str                           # 含 {{#start.question#}} 这样的占位
    messages_template: list[ChatMessageTemplate] | None = None
    raw_completion: bool = False
    inline_spec: dict[str, Any] | None = None       # 自定义模型时才填
    expose_raw_logits: bool | None = None           # None = 继承注册表
    sampling_params: SamplingParams = Field(...)
    extra: dict[str, Any] = Field(default_factory=dict)
```

这个类描述"用户在右侧面板填什么"。Pydantic 会自动做类型校验。

### 2. `node.py` —— 节点的"运行时干什么"

```python
class TokenModelSourceNode(Node[TokenModelSourceNodeData]):
    node_type: ClassVar[NodeType] = "token-model-source"  # ⚠ 必填

    @classmethod
    def version(cls) -> str:
        return "1"

    def _run(self) -> Generator[NodeEventBase, None, None]:
        # 1. 从 variable pool 读上游变量（解析 prompt 里的 {{#x.y#}}）
        # 2. 构造 ModelInvocationSpec 对象
        # 3. yield StreamCompletedEvent(
        #        node_run_result=NodeRunResult(outputs={
        #            "spec": spec,
        #            "model_alias": self.node_data.model_alias,
        #        })
        #    )
```

**继承 `Node[XxxNodeData]` + 类属性 `node_type` + `version()` 三件齐了，graphon 的 `Node.__init_subclass__` 会自动把这个类塞进全局注册表。** 你不用手写 "register me" 之类的代码。

### 三个节点的关键差异

| 节点 | `_run()` 的核心动作 | 流式？ |
|---|---|---|
| token-model-source | 渲染 prompt → 装进 spec → 一次 yield 完事 | 否 |
| **parallel-ensemble** | 开线程池 → N 个 worker 各打 `http://llama-cpp/completion` 拿 top_probs → 主循环每步投票 → 每选出一个 token 就 `yield StreamChunkEvent(...)` → 末尾 yield 一个 `is_final=True` 的封口块 + `StreamCompletedEvent` | **是** |
| response-aggregator | 读 N 个上游的 `text` + 权重 → 构造 synthesis prompt → 调一个 Dify LLM → 流式转发聚合模型输出 → yield 结果 | 可转发 LLM 流 |

### 一个容易忽略的安全细节

**模型 URL 不能让用户在节点配置里随便填**——会有 SSRF（让 Dify 服务器去打内网地址）。约定：

- URL 集中放在 `api/configs/model_net.yaml`，节点配置只引用"别名"（如 `q1`、`g4`）。
- HTTP 调用必须走 `core.helper.ssrf_proxy`，不要直接 `httpx.post`。
- `parallel-ensemble` 的 DSL 里显式拒绝 `model_url` / `api_key` / `api_key_env` / `url` / `endpoint` 这类字段；如果要临时调自定义模型，走 `token-model-source.inline_spec`，最终仍由后端 backend spec + SSRF proxy 接管。

---

## 五、前端怎么改 —— 新手踩坑最多的地方

前端任务量比后端大，因为 React 不像 Python 有"自动发现"。**每加一个节点至少要硬编码 9 个地方**，少一个就出诡异 bug。当前三节点还额外接了 registry 查询、trace store、run panel，所以实际改动点比 9 个更多。

### 前端文件结构（每节点 5 个文件）

```
web/app/components/workflow/nodes/token-model-source/
├── default.ts        # 节点默认配置（拖出来时的初始值 + 校验）
├── node.tsx          # 画布上的方块长什么样
├── panel.tsx         # 右侧配置面板长什么样
├── types.ts          # TypeScript 类型（和后端 entities.py 对齐）
└── use-config.ts     # 配置编辑逻辑 hook
```

### 9 处必改注册点

| # | 文件 | 干什么 |
|---|---|---|
| 1 | `web/app/components/workflow/types.ts` 的 `BlockEnum` | 加节点类型字符串常量 |
| 2 | `web/app/components/workflow/block-selector/constants.tsx` 的 `BLOCKS` | 让"加节点"菜单里能看到 |
| 3 | `web/app/components/workflow/nodes/components.ts` | 把 `node.tsx`、`panel.tsx` 注册成组件 |
| 4 | `web/app/components/workflow/nodes/_base/components/variable/utils.ts` 的 `formatItem`（~ line 329） | **【关键】** 告诉下游节点"我有什么输出变量" |
| 5 | 同一个 `utils.ts` 的 `getNodeOutputVars`（~ line 2092） | **【关键 2】** 返回变量选择器列表 |
| 6 | `web/i18n/en-US/workflow.json` + `zh-Hans/workflow.json` | 用户可见字符串 i18n |
| 7 | `web/app/components/workflow/constants.ts` 的 `SUPPORT_OUTPUT_VARS_NODE` | 让下游变量选择器承认这个节点有输出 |
| 8 | `workflow-panel/last-run/use-last-run.ts` 的单节点运行 hook 映射 | 让右侧面板的单节点运行路径不缺表单参数 |
| 9 | `block-icon.tsx`、`constants/node.ts`、`utils/workflow.ts` 等全量映射 | 补默认值、图标、颜色、`canRunBySingle` 等能力开关 |

### 最重要的坑（团队踩过 3 次）

第 4、5 两个 switch 在同一个 `utils.ts` 文件里，**必须同时改、字段一一对应**。只改一个就会出现这种诡异现象：

> 在节点 panel 里能选到上游变量；但 End 节点的变量下拉里**看不到**新节点的输出 → 把数据接到 End 上时直接没选项。

**原因**：`formatItem` 返回的是"带类型 schema 的变量列表"，被 `toNodeOutputVars` 真正消费；找不到对应 case 就返回 `vars=[]`，紧接着被 `.filter(item => item.vars.length > 0)` 过滤掉，节点从下拉里消失。

**记住**：picker 列出的变量必须和节点配置门控匹配。比如 `token-model-source` 当前稳定输出 `spec` 和 `model_alias`，`formatItem` / `getNodeOutputVars` 就应只列这两个；不要一股脑把内部字段都列上。`parallel-ensemble.trace` 也只有在 `diagnostics.storage="inline"` 时才进 variable pool，所以 picker 需要按配置门控。

---

## 六、跑通验收路径（建议按顺序做）

1. **后端先空跑**
   - 把 token-model-source 写成"输入啥输出啥"的 echo 节点
   - 用 `uv run --project api pytest` 跑节点单测，确认节点能被注册和实例化
2. **前端能看见**
   - `pnpm dev` 起前端 → 打开任一 workflow → 点 "+"
   - 能在菜单里看到新节点 → 拖出来 → 右侧面板能编辑配置
3. **变量能传**
   - 把 Start → token-model-source → End 连起来
   - End 节点下拉里能选到 `spec` → 点运行 → 看 trace 里 spec 值对不对
4. **接真实 llama.cpp**
   - parallel-ensemble 流式吐 token → UI 上能看到逐字出现
5. **DSL 往返**
   - 导出 YAML → 删工作流 → 重新导入 → 还能跑

---

## 七、给新人的学习顺序建议

1. **先玩 1 小时 Dify**
   - 自己拖一个最简单的 workflow（Start → LLM → End），跑通，导出 YAML 看一眼
2. **读一个最简单的内置节点源码**
   - `api/core/workflow/nodes/agent/` 是仓库内可改的最简单参考
   - 前端看 `web/app/components/workflow/nodes/iteration/` 作为目录结构标准
3. **再回头看已落地的三节点代码**
   - 仓库里已经有 `token_model_source` / `parallel_ensemble` / `response_aggregator`
   - **这份开发思路实质上是把"已经走过的路"再用新人语言讲一遍**——遇到不懂的就回这三个已存在的目录看
4. **看路线图**
   - `docs/ModelNet/active/ROADMAP.md` + `docs/ModelNet/active/TASKS.md` 是当前活跃路线和执行清单
   - `docs/ModelNet/architecture/EXTENSION_GUIDE.md` 是扩展点详细参考
   - 历史路线（v2/v3 development plan、各 P*_LANDING）归档在 `docs/ModelNet/history/`

---

## 八、三个节点的字段详解

这一节按"新人打开 panel 时会看到什么"来解释字段。先不用记类名，先记住：**source 节点负责描述一次模型调用，parallel 节点负责执行 token 级协作，response 节点负责合成完整回复**。

### 1. `token-model-source`

它的输出不是文本，而是一个 `spec` 对象。这个对象会进 variable pool，供下游 `parallel-ensemble` 读取。

| 字段 | 新人理解 | 运行时去向 |
|---|---|---|
| `model_alias` | 这一路用哪个模型。注册表模式下是 `api/configs/model_net.yaml` 里的 `id`；自定义模式下是这一路的逻辑名字 | 变成 `spec.model_alias` |
| `prompt_template` | 普通 prompt 模板，可写 `{{#start.question#}}` | 运行时用 `VariableTemplateParser` 渲染成 `spec.prompt` |
| `messages_template` | 显式 chat 模板，适合 system + few-shot + user 多角色结构 | 渲染成 `spec.messages`，下游会走 backend 的 `apply_template` |
| `raw_completion` | 是否跳过 chat-template 自动包裹 | `False` 时，chat-capable backend 会把 prompt 包成 user message；`True` 时按 PN.py 原始 completion 方式发送 |
| `sampling_params` | 这一路的采样参数 | 进入 `spec.sampling_params`，后面会合并 `top_k_override` |
| `inline_spec` | 不走 yaml 注册表，直接在节点里填一个自定义 backend spec | 下游按 backend 的 Pydantic spec 校验后实例化 |
| `expose_raw_logits` | 对注册表 alias 的 raw-logit 覆盖 | `None` 继承 yaml；布尔值只影响当前 source |
| `extra` | 给后端实验参数留的扩展口 | 合进 `TokenStepParams.extra`，例如后续 vLLM 私有参数 |

`prompt_template` 和 `messages_template` 互斥。原因很简单：如果两者都填，下游不知道该把哪个作为模型输入；所以 schema 在导入 DSL 时直接拒绝。

`token-model-source` 成功后输出大概长这样：

```json
{
  "spec": {
    "model_alias": "14",
    "prompt": "Answer: what is 2+2",
    "messages": null,
    "raw_completion": false,
    "sampling_params": {
      "top_k": 10,
      "temperature": 0.7,
      "max_tokens": 1024,
      "top_p": null,
      "seed": null,
      "stop": []
    },
    "extra": {},
    "expose_raw_logits": null,
    "inline_spec": null
  },
  "model_alias": "14"
}
```

### 2. `parallel-ensemble`

它是 token 级协作真正执行的节点。它不再自己保存 `question_variable` 或 `model_aliases`，而是读取多个上游 `token-model-source.outputs.spec`。

| 字段 | 新人理解 | 运行时去向 |
|---|---|---|
| `ensemble.token_sources[]` | N 路参与投票的来源 | 每个 source 先 resolve 出一个 `ModelInvocationSpec` |
| `source_id` | 这一路在 trace 和权重表里的名字 | 作为 backends、sources、weights 字典 key |
| `spec_selector` | 指向上游 `token-model-source` 的 `spec` 输出 | 从 variable pool 读 spec |
| `weight` | 这一路投票权重。可以是数字，也可以是变量选择器 | resolve 成 `dict[source_id, float]` |
| `fallback_weight` | 动态权重读取失败时是否降级 | 不填就是 fail-fast；填了就记录 warning 并继续 |
| `top_k_override` | 在聚合处强制覆盖 top-k | 只覆盖 `top_k`，其他采样参数仍来自 source |
| `runner_name` | 用哪种执行算法 | 当前默认 `token_step` |
| `runner_config` | runner 自己的参数 | 用 runner 的 Pydantic `config_class` 校验 |
| `aggregator_name` | 每步 token 候选怎么合并 | 当前默认 `sum_score`，另有 `max_score` / `duet_net` 等 token aggregator |
| `aggregator_config` | aggregator 自己的参数 | 用 aggregator 的 `config_class` 校验 |
| `diagnostics` | trace 记录开关 | 控制 token candidates、logits、reasoning、think trace、实时 trace stream 等 |

`parallel-ensemble` 的启动校验顺序很重要：

1. 先检查 runner 和 aggregator 的 scope 是否匹配，比如 token runner 只能配 token aggregator。
2. 再校验 `runner_config` / `aggregator_config` 的 schema。
3. 再检查每个 backend 的 capability 是否满足 runner 要求。
4. 再做更细的 requirement 校验，例如 top-k 上限、raw logits 能力。
5. 最后做 cross-field 校验，例如 `token_step` 至少要两个 source。

成功运行时，它会先不断 yield `StreamChunkEvent(selector=[node_id, "text"], chunk=...)`，让 UI 逐 token 显示；最后必须 yield 一个 `chunk=""`、`is_final=True` 的封口块，再 yield `StreamCompletedEvent`。少了封口块，下游 Answer/End 类节点可能不 flush。

### 3. `response-aggregator`

它是 response 级综合节点。上游可以是多个普通 LLM 节点，也可以是其他已经产出文本的节点。它不是 token 级投票器，而是"把多份完整答案交给一个聚合 LLM 写终稿"。

| 字段 | 新人理解 | 运行时去向 |
|---|---|---|
| `inputs[]` | 多个上游完整回复 | 每个 selector 从 variable pool 读 `Segment.text` |
| `source_id` | 这份回复的名字 | 写入 synthesis prompt 和 metadata |
| `variable_selector` | 指向上游文本输出 | 例如 `["llm_a", "text"]` |
| `weight` | 告诉聚合模型哪一路更重要 | 被写进合成 prompt，也写进输出 metadata |
| `fallback_weight` | 动态权重失败时是否继续 | 同 `parallel-ensemble`，不填就是 fail-fast |
| `extra` | 预留扩展字段 | 当前 synthesis prompt 不直接消费，但保留给后续策略 |
| `instruction` | 给聚合模型的任务说明 | 空字符串会回退到内置默认 instruction |
| `model` | 真正负责写终稿的 Dify LLM | 走 `LLMNode.invoke_llm`，因此有 usage / price / streaming |

它成功后输出：

- `outputs.text`：最终综合答案。
- `outputs.metadata.contributions`：每个 source 的原始文本。
- `outputs.metadata.weights`：每个 source 的最终权重。
- `process_data.prompts`：实际发给聚合模型的 system/user prompt，方便排查。
- `llm_usage` / `metadata.total_tokens`：Dify 原生 LLM 计费用量信息。

---

## 九、后端执行链路细节

### 1. 节点注册是怎么发生的

每个后端节点都继承 `Node[NodeData]`，并声明：

```python
node_type: ClassVar[NodeType] = "parallel-ensemble"

@classmethod
def version(cls) -> str:
    return "1"
```

graphon 的 `Node.__init_subclass__` 会把这个类注册进全局 registry。Dify 的 `node_factory.py` 启动时 import `api/core/workflow/nodes/` 下的包，所以 `__init__.py` 里要把 `Node` 类导出或触发 import。常见症状：

- 后端单测里 `Node._registry` 没有你的类型：通常是 `__init__.py` 没 import 到 `node.py`。
- 前端能保存 DSL，但运行时报 unknown node type：通常是后端包没有被 factory 扫到，或 `node_type` 字符串和前端 `BlockEnum` 不一致。

### 2. variable pool 只保存最终输出

这点是整个三节点设计的核心：

- `StreamChunkEvent` 是给 UI 实时显示的，不会作为变量给下游消费。
- `StreamCompletedEvent.node_run_result.outputs` 才会写进 variable pool。
- 所以 token 级协作不能做成"多个 LLM 节点流式输出 → 一个聚合节点逐 token 接收"。
- 正确形态是 `parallel-ensemble` 自己持有所有 backend，并在自己的 `_run()` 内部逐 token 调度。

`token-model-source` 正是为了这个形态服务的：它不调模型，只把每一路的配置渲染成 `spec`；`parallel-ensemble` 一次性读完 N 个 `spec` 后，自己启动 runner。

### 3. `_extract_variable_selector_to_variable_mapping` 很关键

如果节点配置里引用了上游变量，只在 `_run()` 里手动 `variable_pool.get(...)` 还不够。还要实现：

```python
@classmethod
def _extract_variable_selector_to_variable_mapping(...):
    return {
        f"{node_id}.inputs.{source_id}": variable_selector,
    }
```

这个 mapping 会被 Dify 的 draft-variable preload、单步调试等路径使用。漏掉它的后果是：全图运行可能正常，但单节点运行、调试预加载、某些导入后的 dry-run 会找不到上游变量。

当前三节点分别处理：

- `token-model-source`：扫描 `prompt_template` 和 `messages_template[].content` 里的 `{{#...#}}`。
- `parallel-ensemble`：暴露每个 `spec_selector`，如果 `weight` 是变量选择器也要暴露。
- `response-aggregator`：暴露每个 `variable_selector`，如果 `weight` 是变量选择器也要暴露。

### 4. `Segment.text` 比 `str(segment.value)` 更可靠

从 variable pool 读出来的是 `Segment`。要把上游输出作为文本时，优先用 `segment.text`：

- `NoneSegment` 会变成空字符串。
- object / array 会按 graphon 规范渲染。
- 和其他内置节点的变量显示语义一致。

`response-aggregator` 读取上游完整回复时就是这样做的；`token-model-source` 渲染 prompt 时也把 selector 对应的 segment 转成 text 后再交给 `VariableTemplateParser.format()`。

### 5. factory 注入依赖

普通 echo 节点可以只靠 `Node.__init__`。这三个节点里有两个需要额外依赖：

- `parallel-ensemble` 需要 `model_registry`、`runner_registry`、`aggregator_registry`、`backend_registry`、共享 `ThreadPoolExecutor`、`http_client`。
- `response-aggregator` 需要准备好的聚合模型实例、prompt serializer、LLM file saver，否则 `_run_synthesis()` 会 fail。

这类依赖不应该在节点里自己 new。要让 `node_factory.py` 负责注入，因为 factory 才知道租户、工作流、模型配置和 SSRF 代理。

---

## 十、前端落地细节

### 1. 三节点目录结构

三个节点在前端都在：

```text
web/app/components/workflow/nodes/
├── token-model-source/
├── parallel-ensemble/
└── response-aggregator/
```

每个目录最少有：

- `types.ts`：TypeScript DSL 类型，必须和后端 `entities.py` 对齐。
- `default.ts`：拖节点时的初始值、分类、排序、`checkValid`。
- `node.tsx`：画布卡片。
- `panel.tsx`：右侧配置面板。
- `use-config.ts`：更新节点 data 的 hook。
- `components/`：复杂表单拆分。
- `__tests__/`：RTL/Vitest 单测。

### 2. 新节点必须被前端"认识"

至少检查这些位置：

| 位置 | 漏掉后的症状 |
|---|---|
| `web/app/components/workflow/types.ts` 的 `BlockEnum` | DSL 类型没有枚举值，很多 Record 全量映射会报错 |
| `block-selector/constants.tsx` | 加节点菜单里看不到 |
| `nodes/components.ts` | 画布上渲染成 unknown，右侧 panel 不出现 |
| `constants/node.ts` | 拖出来没有默认 data，或保存时报空字段 |
| `block-icon.tsx` | icon/颜色缺失，某些 Record 全量检查失败 |
| `constants.ts` 的 `SUPPORT_OUTPUT_VARS_NODE` | 下游变量选择器看不到这个节点输出 |
| `variable/utils.ts` 的 `formatItem` | 变量 picker 有节点但没有正确字段 schema |
| `variable/utils.ts` 的 `getNodeOutputVars` | End/Answer 这类下游节点看不到输出 |
| `workflow-panel/last-run/use-last-run.ts` | 单节点运行表单路径缺映射 |
| `utils/workflow.ts` 的 `canRunBySingle` | 右侧 panel 不能单独运行 |
| `web/i18n/*/workflow.json` | UI 显示 key 名，或测试里找不到文案 |

`parallel-ensemble` 还有额外运行态 UI：

- `web/contract/console/parallel-ensemble.ts`：声明 local-models / runners / aggregators 三个只读接口。
- `web/app/components/workflow/nodes/parallel-ensemble/use-registries.ts`：拉取注册表元信息。
- `web/app/components/workflow/hooks/use-workflow-run-event/use-workflow-parallel-ensemble-trace.ts`：监听实时 trace。
- `web/app/components/workflow/store/workflow/parallel-ensemble-trace-slice.ts`：按 node id 保存 trace steps。
- `web/app/components/workflow/run/parallel-ensemble-trace/`：运行面板里的 trace 展示。

### 3. 输出变量要前后端一致

当前约定：

| 节点 | 后端 `outputs` | 前端变量 picker 应展示 |
|---|---|---|
| `token-model-source` | `spec`, `model_alias` | 至少 `spec`，调试场景可用 `model_alias` |
| `parallel-ensemble` | `text`, `tokens_count`, `elapsed_ms`，`storage="inline"` 时有 `trace` | `text`, `tokens_count`, `elapsed_ms`，按配置展示 `trace` |
| `response-aggregator` | `text`, `metadata` | `text`, `metadata` |

不要在前端变量 picker 里列出后端不会稳定输出的字段。反过来，如果后端新增了稳定输出，也要同步 `formatItem` / `getNodeOutputVars`，否则用户接不到这个值。

### 4. i18n 不是最后补的杂项

Dify 前端用户可见字符串必须进 `web/i18n/en-US/workflow.json` 和 `web/i18n/zh-Hans/workflow.json`。这包括：

- block 名称和描述。
- panel label、tooltip、placeholder。
- `checkValid` 的错误信息。
- runner / aggregator 的 `i18n_key_prefix` 对应字段。
- trace 面板里显示的列名和状态。

如果你只在组件里写英文硬编码，短期能跑，长期会在 lint、review 或中文 UI 下暴露。

---

## 十一、从零配置一个 token 级工作流

下面按 UI 操作来跑通最小 token 级协作。

### Step 1：确认模型注册表

注册表在：

```text
api/configs/model_net.yaml
```

每个模型大致长这样：

```yaml
models:
  - id: "14"
    backend: llama_cpp
    model_name: qwen3-4b-instruct-2507-q4km
    model_url: http://219.222.20.79:30584
    EOS: "<|im_end|>"
    type: normal
    stop_think: "<|None|>"
```

前端通过 `/workspaces/current/local-models` 只能拿到 `id`、`backend`、`model_name`、`capabilities`、`metadata`，拿不到 `model_url` 和 credential。这是故意的。

### Step 2：画布结构

最小结构：

```text
Start
 ├─ token-model-source(source_a)
 ├─ token-model-source(source_b)
 └─ token-model-source(source_c)
        │
        ▼
parallel-ensemble
        │
        ▼
End
```

每个 `token-model-source`：

- 选一个 `model_alias`，例如 `"14"`、`"18"`。
- `prompt_template` 填同一个问题模板，例如 `{{#start.question#}}`。
- `top_k` 建议先保持 10，`temperature` 先用 0.7。
- 如果模型是 chat 模型，默认 `raw_completion=false`，让下游自动套 chat template。

`parallel-ensemble`：

- 在 `token_sources` 里加三行。
- 每行 `spec_selector` 选择对应 source 的 `spec`。
- `source_id` 用稳定名字，例如 `qwen4b`、`phi4mini`、`gemma4b`。
- runner 先选 `token_step`。
- aggregator 先选 `sum_score`。
- diagnostics 先保持默认；如果要看每步候选，再打开 `include_token_candidates` 和 `enable_trace_stream`。

### Step 3：运行时应该看到什么

如果通了：

- UI 上 `parallel-ensemble` 会逐 token 出字。
- End 节点能选到 `parallel-ensemble.text`。
- run trace 里 `parallel-ensemble.outputs.text` 是最终答案。
- 如果打开 trace stream，运行面板能看到每一步 selected token、score、耗时；如果打开 candidates，还能看到各模型候选。

如果不通，优先看错误类型：

- `MissingSpecError`：`spec_selector` 没接对，或上游 `token-model-source` 失败。
- `InvalidSpecError`：上游输出不是合法 spec，常见于 DSL 手改字段。
- `StructuredValidationError`：runner / aggregator / backend capability 不匹配。
- `WeightResolutionError`：动态权重 selector 读不到或不是正数。
- llama.cpp HTTP 错误：模型服务没开、端口错、响应格式不符合 backend parser。

---

## 十二、从零配置一个 response 级工作流

response 级不需要 `token-model-source`，直接用 Dify 原生 LLM 节点并发生成完整答案。

```text
Start
 ├─ LLM(model_a)
 ├─ LLM(model_b)
 └─ LLM(model_c)
        │
        ▼
response-aggregator
        │
        ▼
End
```

配置要点：

- 三个 LLM 节点都读取同一个 Start 问题。
- `response-aggregator.inputs[]` 分别选择三个 LLM 的文本输出。
- `source_id` 用人能看懂的名字，例如 `qwen`、`llama`、`gemma`。
- `weight` 默认 1.0；如果某个模型更可信，可以设成 1.5 或 2.0。
- `instruction` 写给聚合模型，例如"综合多份候选答案，保留事实一致部分，冲突时说明依据"。
- `model` 选择一个 Dify 已配置好的 chat model，作为主编模型。

它的优点是工程风险低：不依赖 llama.cpp top logprobs，不需要 backend raw-logit 能力；缺点是它不是逐 token 协作，模型已经各自完整生成，后面只是二次综合。

---

## 十三、测试和验收命令

后端目标测试：

```bash
uv run --project api pytest api/tests/unit_tests/core/workflow/nodes/token_model_source/ -v -o addopts=""
uv run --project api pytest api/tests/unit_tests/core/workflow/nodes/parallel_ensemble/ -v -o addopts=""
uv run --project api pytest api/tests/unit_tests/core/workflow/nodes/response_aggregator/ -v -o addopts=""
uv run --project api pytest api/tests/unit_tests/core/workflow/test_node_factory.py -v -o addopts=""
```

`-o addopts=""` 的原因是仓库 pytest 配置可能默认带 coverage，本地环境没装 coverage 插件时会因为测试工具链而不是业务代码失败。

前端目标测试：

```bash
cd web
pnpm test web/app/components/workflow/nodes/token-model-source
pnpm test web/app/components/workflow/nodes/parallel-ensemble
pnpm test web/app/components/workflow/nodes/response-aggregator
pnpm type-check
```

如果只改文档，不需要跑这些；如果改了节点逻辑或 panel，至少跑对应目录的单测和 type-check。

验收时按这个顺序更省时间：

1. 后端 schema 单测先过，证明 DSL 形状正确。
2. 后端 node 单测再过，证明 `_run()` 事件和 outputs 正确。
3. 前端 panel 单测过，证明用户能填出合法 DSL。
4. 本地 UI 拖节点，看变量 picker 是否能选到输出。
5. 最后接真实模型服务，排 HTTP / backend parser /性能问题。

---

## 十四、常见排错清单

### 前端看不到新节点

检查：

- `BlockEnum` 是否有对应字符串。
- `block-selector/constants.tsx` 是否加进 `BLOCKS`。
- `nodes/components.ts` 是否注册 `NodeComponentMap` 和 `PanelComponentMap`。
- i18n key 是否存在，避免菜单里只显示 key。

### 节点能拖出来，但 End 选不到输出

检查：

- `SUPPORT_OUTPUT_VARS_NODE` 是否包含该节点。
- `variable/utils.ts` 的 `formatItem` 是否返回了字段 schema。
- `getNodeOutputVars` 是否返回同名字段。
- 后端 `NodeRunResult.outputs` 是否真的有这些字段。

### `parallel-ensemble` 运行前就失败

先看错误是不是 `StructuredValidationError`。如果是，优先检查：

- runner 和 aggregator 的 scope 是否匹配。
- `token_step` 是否至少有两个 token source。
- 选的模型是否有 runner 要求的 capability，比如 top probabilities / raw logits。
- `top_k_override` 是否超过 backend 支持上限。

### `token-model-source` prompt 渲染失败

常见原因：

- `{{#start.question#}}` 里的节点 id 或变量名写错。
- 上游节点没有跑成功，所以 variable pool 没有对应值。
- `prompt_template` 和 `messages_template` 同时设置，被 schema 拒绝。

### response 聚合模型没被准备好

`response-aggregator` 依赖 factory 注入的 LLM 对象。若报：

- `aggregation model was not prepared`
- `LLM file saver was not prepared`

说明问题通常不在 node 本身，而在 `node_factory.py` 的注入分支、模型配置、或单测构造 node 时漏传 mock。

### trace 太大或 UI 卡

`parallel-ensemble` 的 diagnostics 要按需打开：

- 默认只保留轻量 timing 和 per-backend error。
- `include_token_candidates`、`include_logits`、`include_aggregator_reasoning` 都可能让每步 trace 变大。
- `max_trace_tokens` 是最后 N 步保留窗口，不是总生成 token 数上限。
- `enable_trace_stream` 会把每步 trace 通过 SSE 发给前端，调试时开，常规运行时关。

---

## 十五、如果要继续扩展

### 加一个新的 token aggregator

适合场景：你只想改变"每一步从各模型 top-k 候选里选哪个 token"。

要做：

1. 在 `api/core/workflow/nodes/parallel_ensemble/aggregators/token/` 新增类。
2. 继承 `TokenAggregator`，声明 `scope = "token"`、`config_class`、`ui_schema`、`i18n_key_prefix`。
3. 用 registry decorator 注册。
4. 加后端单测，覆盖 tie-break、权重、空候选、错误候选。
5. 补前端 i18n，让 dropdown 能显示名字和字段。

不需要改 `parallel-ensemble` 节点主类，除非你需要新的 UI control 类型。

### 加一个新的 runner

适合场景：算法流程变了，比如不再每步同步投票，而是先让模型独立生成草稿，再让 judge 选择。

要做：

1. 在 `api/core/workflow/nodes/parallel_ensemble/runners/` 新增 runner。
2. 定义 `config_class`、`aggregator_scope`、`required_capabilities`。
3. 实现 `requirements(config)` 和 `run(...)`。
4. 若需要特殊 cross-field 规则，覆写 `validate_selection(...)`。
5. 补 `ui_schema` 和 i18n。

### 加一个新的 backend

适合场景：要接 vLLM、OpenAI-compatible、Anthropic 或别的推理服务。

要做：

1. 新建 backend spec，继承 `BaseSpec`，用 Pydantic 限制 URL、api key、模型名等字段。
2. 实现 `ModelBackend.step_token(...)`，把服务响应统一成 `TokenCandidate`。
3. 声明 capability，比如是否支持 top logprobs、raw logits、chat template。
4. 在 `BackendRegistry` 注册 spec/backend。
5. 更新 `BACKEND_CAPABILITIES.md`，说明概率语义是 logprob、prob 还是 raw logits。
6. 加跨 backend 的 fixture，保证 `sum_score` 等 aggregator 读到的分数语义一致。

不要为了新 backend 去改 `token-model-source` 的核心 schema。backend 私有字段应放进 `inline_spec` 或 yaml spec，由 backend 自己的 Pydantic schema 校验。

---

## 十六、一句话总结

在 Dify 里加节点 = **后端**写一个 `Node` 子类 + Pydantic 配置 schema（自动注册），**前端**硬编码 9 处注册 + 5 个组件文件。

最大的坑是前端 `utils.ts` 里两个并行 switch 必须同时改；token 级集成因为 Dify 流式块不进 variable pool，所以必须用"聚合器即执行器"的胖节点形态，而响应级集成则只需一个收 N 上游完整文本、再调用聚合 LLM 的节点（并发由 GraphEngine 自动处理）。
