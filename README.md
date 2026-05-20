# ModelNet：面向模型互联网的 Dify 二开平台

ModelNet 是一个基于 [Dify](https://github.com/langgenius/dify) 的二次开发分支，用于把“模型互联网（AI-ModelNet）”从论文概念落到可运行、可导入、可复现、可扩展的工作流系统中。

它保留 Dify 的可视化工作流画布、模型管理、RAG 流水线、API 服务和 Docker 部署体系，并在此基础上增加模型互联所需的模型节点、协作通路、动态路由、token 级并联推理、响应级综合、数据集加载和实验复现能力。

如果你第一次进入本仓库，建议先读本 README，再进入 [ModelNet 文档入口](https://github.com/WNDS-JNU/ModelNet/blob/main/docs/ModelNet/README.md)。如果只想跑起来，直接看 [快速开始](#快速开始)。

> 本项目基于 Dify 开发。上游 Dify 的版权、署名和 [LICENSE](./LICENSE) 中的修改版 Apache 2.0 许可证条款仍然适用。

## 项目定位

ModelNet 的概念以 [《模型互联网：概念、现状和未来》](./docs/ModelNet/模型互联网.pdf) 为基础。该文提出的模型互联网不是简单的“多模型调用”，而是一种通过构建模型间标准化通路，实现模型互联互通、能力共享与协同推理的新范式。

在这个范式中，模型不再只是某个应用内部的推理后端，而是可以被发现、组合、调用和协作的能力节点。模型互联网希望解决“模型孤岛”问题，让云端模型、边缘模型、端侧模型、通用模型、领域模型和私有模型能够在统一任务中形成动态链路。

本仓库当前定位为工程化原型和研究平台，重点验证以下问题：

- 如何在 Dify 工作流中表达模型节点、模型通路和协作策略。
- 如何支持响应级、路由级、span/token 级等不同粒度的模型协作。
- 如何让模型 URL、能力标签和后端配置留在服务端，工作流侧只引用安全的模型别名。
- 如何把 DuetNet、AI-ModelNet、动态协作路由等论文方法转化为可导入的 DSL 和可跑的评测流程。

## 与模型互联网四层结构的对应关系

论文中的模型互联网由资源层、服务层、交互层和应用层组成。ModelNet 在 Dify 上做了一个面向研发验证的对应实现：

- **资源层**：由 Kubernetes 管理模型部署、Service、Ingress 和命名空间隔离；ModelNet 通过 K8s Ingress 自动发现将这些模型资源同步为服务端模型别名，本地开发也可用 `model_net.yaml` 手动注册。
- **服务层**：借助 Dify workflow 对任务进行拆解、编排、变量传递、数据集加载和执行状态管理。
- **交互层**：通过 `token-model-source`、`parallel-ensemble`、`response-aggregator` 等节点构建模型间的协作通路，支持串联、并联、路由和融合。
- **应用层**：通过可导入 DSL、workflow API 和评测脚本，把模型互联能力用于问答、选择题评测、论文复现和动态路由实验。

这不是完整的全球模型互联网基础设施，而是围绕“模型如何互联、如何协作、如何被调度和复现”的实验系统。

## 当前状态

当前仓库已经提供一组可在 Dify workflow 中直接使用的 ModelNet 能力：

- **工作流节点**：`token-model-source`、`parallel-ensemble`、`response-aggregator` 和 `data-loader` 已形成基本闭环。
- **服务端模型注册表**：生产环境可由 K8s 自动发现刷新模型别名、后端类型、能力标签和推理端点；本地开发可用 `model_net.yaml` 手动维护，workflow DSL 默认只引用别名。
- **协作推理路径**：支持响应级综合、token 级并联推理、DuetNet 聚合、动态协作路由和串并联混合路径。
- **示例与复现脚本**：`docs/ModelNet/examples/workflow_mode` 提供可导入 DSL，`dev/modelnet` 提供 DSL 生成、数据集评测和论文复现实验工具。
- **进行中方向**：vLLM token-level 兼容、chat logprob 探测、后端能力矩阵完善和自动 DSL 生成仍按路线图推进。

本文档只描述当前能力和入口路径，不把本地 smoke run 结果写成正式 benchmark 结论。实验数字以完整复现配置和报告为准。

## 核心能力

- **Token Model Source**：把一个模型抽象为可被下游消费的调用规格。它负责 prompt 模板、chat messages、采样参数、模型别名或内联后端配置。
- **Parallel Ensemble**：读取多个 `token-model-source` 输出，执行 token 级协作推理。内置 `sum_score`、`max_score`、`duet_net` 等 token 聚合器，并支持动态协作路由 runner。
- **Response Aggregator**：收集多个上游节点的完整回复，再按策略生成最终答案。适合投票、拼接、综合、互评、辩论后总结等响应级协作。
- **Data Loader**：在工作流中加载 benchmark 数据。内置 `inline_json` 和 `jsonl_file` loader，便于构建可重复评测流程。
- **模型注册表**：通过服务端 `model_net.yaml` 管理模型能力、后端类型和推理端点，工作流中默认只引用别名，避免把内部 URL 暴露给 DSL。
- **Trace 与诊断**：记录 token 决策、模型错误、路由结果、运行摘要和 artifact 下载信息，便于复现实验和排查模型协作过程。

## 工作流模式

### 响应级协作

适合多个模型、工具或 Agent 已经分别产出完整答案的场景。

```text
LLM / HTTP / Code / Agent 输出
        -> Response Aggregator
        -> End / Answer
```

典型用途包括多模型投票、候选答案综合、互评结果汇总、不同角色输出整合。

### Token 级协作

适合希望多个模型在解码过程中逐 token 或逐 span 协同的场景。

```text
Start / Data Loader
        -> N 个 Token Model Source
        -> Parallel Ensemble
        -> End / Answer
```

每个 `token-model-source` 渲染自己的 prompt 与采样参数。`parallel-ensemble` 解析这些 spec，实例化对应后端，应用每路 source 的权重和 `top_k_override`，再运行选定 runner 与 token 聚合器。

### 动态路由协作

适合模型能力、任务属性和协作关系需要动态匹配的场景。

```text
任务输入 / 数据集样本
        -> 路由特征或协作图
        -> Parallel Ensemble dynamic_collab_route
        -> 最终模型链路与答案
```

这一路径对应模型互联网中“根据任务性质与实时状态形成模型链路”的思想，当前用于复现动态协作路由相关论文。

## 快速开始

最短路径是：启动 Dify / ModelNet 服务栈，配置服务端模型别名，导入示例 DSL，然后从 Dify Studio 或 workflow API 运行。

### 1. 启动 Dify / ModelNet 服务栈

Docker 部署方式继承自 Dify：

```bash
cd docker
cp .env.example .env
docker compose up -d --build
```

启动后打开：

```text
http://localhost/install
```

公开部署时请从本 fork 构建并发布 API / Web 镜像。上游 `langgenius/dify-*` 镜像不包含 ModelNet 新增的工作流节点、控制台面板或 ModelNet 后端逻辑。

源码开发仍沿用 Dify 的前后端分工：

```bash
# 后端命令
uv run --project api <command>

# 前端命令
cd web
pnpm install
pnpm dev
```

### 2. 配置模型别名

生产环境推荐开启 K8s 自动发现，由后端从 Kubernetes Ingress 刷新服务端模型注册表；本地开发或没有集群权限时，可以复制样例配置并手动填写模型别名：

```bash
cp api/configs/model_net.yaml.example api/configs/model_net.yaml
```

每个条目至少需要确认 `id`、`backend`、`model_name`、`model_url` 和 `EOS`。如果是思考模型，还需要设置 `type: think` 和 `stop_think`；如果 llama.cpp fork 暴露 raw logits，再设置 `expose_raw_logits: true`。端口和模型名以实际启动的服务为准。

真实的 `api/configs/model_net.yaml` 已被 git 忽略。容器部署时，需要把 registry 挂载到 API / worker 容器中；如果不使用默认路径，请设置 `MODEL_NET_REGISTRY_PATH`。K8s 自动发现的开关、命名空间和刷新周期见下方注册表契约文档。

注册表契约见 [api/configs/MODEL_NET_README.md](./api/configs/MODEL_NET_README.md)。

### 3. 导入示例工作流

示例 DSL 位于 [docs/ModelNet/examples/workflow_mode](./docs/ModelNet/examples/workflow_mode)：

- [DuetNet token 级主流程](./docs/ModelNet/examples/workflow_mode/token_level_collaborative_reasoning_for_parallel_multi_models/duet_net_main.yml)
- [DuetNet 数据集循环流程](./docs/ModelNet/examples/workflow_mode/token_level_collaborative_reasoning_for_parallel_multi_models/duet_net_main_loop_dataset_zh.yml)
- [AI-ModelNet 混合路由流程](./docs/ModelNet/examples/workflow_mode/multi_model_serial_and_parallel_collaborative_inference_in_ai_modelnet/paper_hybrid_router.yml)
- [动态协作路由流程](./docs/ModelNet/examples/workflow_mode/dynamic_model_routing_based_on_collaborative_relationship/dynamic_collab_route.yml)

在 Dify Studio 中导入 DSL，配置对应模型别名或 Dify 模型供应商，即可从画布或 workflow API 运行。第一次联调建议先做小样本 smoke run，再启动完整 benchmark。

## 架构与扩展

ModelNet 的 token 级路径围绕三轴 SPI 组织：

```text
模型来源节点
        -> ModelBackend
        -> EnsembleRunner
        -> TokenAggregator
        -> Parallel Ensemble 输出
```

- **ModelBackend**：适配 llama.cpp、vLLM 等后端，将不同推理 API 归一为 token-step 接口。
- **EnsembleRunner**：定义模型之间如何协作，例如逐 token 并联、think phase、动态协作路由。
- **Aggregator**：定义候选 token、模型回复或路由结果如何融合。

常见二开入口：

- 新增 token 聚合器：`api/core/workflow/nodes/parallel_ensemble/aggregators/token/`
- 新增协作 runner：`api/core/workflow/nodes/parallel_ensemble/runners/`
- 新增模型后端：`api/core/workflow/nodes/parallel_ensemble/backends/`
- 新增响应级策略：`api/core/workflow/nodes/response_aggregator/strategies/`
- 仅消费 trace：在下游 Code 节点或评测脚本中读取 `ensemble_trace`

推荐先读：

- [模型互联网 PDF](./docs/ModelNet/模型互联网.pdf)
- [扩展性规范](./docs/ModelNet/architecture/EXTENSIBILITY_SPEC.md)
- [二次开发指南](./docs/ModelNet/architecture/EXTENSION_GUIDE.md)
- [三节点开发思路](./docs/ModelNet/architecture/THREE_NODES_BEGINNER_GUIDE.md)
- [后端能力矩阵](./docs/ModelNet/architecture/BACKEND_CAPABILITIES.md)

## 研究与复现

[dev/modelnet](./dev/modelnet) 是当前的研究脚本区，包含 DSL 生成、数据集评测和论文复现实验工具。

当前主要复现方向：

- **DuetNet**：token 级多模型并联协作推理。
- **AI-ModelNet**：串并联混合路径，覆盖 S2P / P2S 等协作范式。
- **动态协作路由**：基于模型协作关系图动态选择模型链路。
- **顶会相似工作映射**：将 MoA、Multiagent Debate、RouteLLM、Adaptive-RAG、Co-LLM 等方向映射到 ModelNet 工作流。

参考文档：

- [dev/modelnet/README.md](./dev/modelnet/README.md)
- [论文复现计划](./docs/ModelNet/research/PAPER_REPRODUCTION_PLAN.md)
- [顶会相似工作复现候选](./docs/ModelNet/research/TOP_CONFERENCE_REPRODUCTION_CANDIDATES.md)

## 仓库结构

```text
api/core/workflow/nodes/response_aggregator/   响应级综合节点
api/core/workflow/nodes/token_model_source/    模型调用规格节点
api/core/workflow/nodes/parallel_ensemble/     backend / runner / aggregator SPI 与 token runner
api/core/workflow/nodes/data_loader/           数据集加载节点
api/configs/model_net.yaml.example             服务端模型注册表模板
dev/modelnet/                                  DSL 生成与评测脚本
docs/ModelNet/                                 概念论文、架构、运维、研究和示例
web/app/components/workflow/nodes/             新增工作流节点的前端面板
```

## 开发检查

后端定向测试：

```bash
uv run --project api pytest \
  api/tests/unit_tests/core/workflow/nodes/response_aggregator \
  api/tests/unit_tests/core/workflow/nodes/token_model_source \
  api/tests/unit_tests/core/workflow/nodes/parallel_ensemble \
  api/tests/unit_tests/core/workflow/nodes/data_loader
```

前端定向检查：

```bash
cd web
pnpm type-check
pnpm exec eslint app/components/workflow/nodes/response-aggregator app/components/workflow/nodes/token-model-source app/components/workflow/nodes/parallel-ensemble app/components/workflow/nodes/data-loader
pnpm test -- --run app/components/workflow/nodes/response-aggregator app/components/workflow/nodes/token-model-source app/components/workflow/nodes/parallel-ensemble app/components/workflow/nodes/data-loader
```

集成测试主要面向 CI。本地研发建议先跑最小 workflow smoke，再启动完整 benchmark。

## 文档入口

ModelNet 文档入口见 [docs/ModelNet/README.md](https://github.com/WNDS-JNU/ModelNet/blob/main/docs/ModelNet/README.md)。按角色阅读时，可以从下面几条线进入：

- **工作流使用者**：先读 [三节点开发思路](./docs/ModelNet/architecture/THREE_NODES_BEGINNER_GUIDE.md)，再导入 [示例工作流](./docs/ModelNet/examples/workflow_mode)。
- **二开开发者**：先读 [二次开发指南](./docs/ModelNet/architecture/EXTENSION_GUIDE.md) 和 [扩展性规范](./docs/ModelNet/architecture/EXTENSIBILITY_SPEC.md)。
- **后端与推理服务实现者**：先读 [后端能力矩阵](./docs/ModelNet/architecture/BACKEND_CAPABILITIES.md)、[模型注册表说明](./api/configs/MODEL_NET_README.md) 和 [TokenLevel vLLM 计划](./docs/ModelNet/operations/vllm/TOKENLEVEL_VLLM_PLAN.md)。
- **研究与复现使用者**：先读 [dev/modelnet/README.md](./dev/modelnet/README.md)、[论文复现计划](./docs/ModelNet/research/PAPER_REPRODUCTION_PLAN.md) 和 [顶会相似工作复现候选](./docs/ModelNet/research/TOP_CONFERENCE_REPRODUCTION_CANDIDATES.md)。

常用长期入口：

- [模型互联网 PDF](https://github.com/WNDS-JNU/ModelNet/blob/main/docs/ModelNet/%E6%A8%A1%E5%9E%8B%E4%BA%92%E8%81%94%E7%BD%91.pdf)
- [当前路线图](https://github.com/WNDS-JNU/ModelNet/blob/main/docs/ModelNet/active/ROADMAP.md)
- [扩展性规范](https://github.com/WNDS-JNU/ModelNet/blob/main/docs/ModelNet/architecture/EXTENSIBILITY_SPEC.md)
- [二次开发指南](https://github.com/WNDS-JNU/ModelNet/blob/main/docs/ModelNet/architecture/EXTENSION_GUIDE.md)
- [后端能力矩阵](https://github.com/WNDS-JNU/ModelNet/blob/main/docs/ModelNet/architecture/BACKEND_CAPABILITIES.md)
- [TokenLevel vLLM 计划](https://github.com/WNDS-JNU/ModelNet/blob/main/docs/ModelNet/operations/vllm/TOKENLEVEL_VLLM_PLAN.md)
- [Auto DSL 生成计划](https://github.com/WNDS-JNU/ModelNet/blob/main/docs/ModelNet/operations/auto-dsl-gen/AUTO_DSL_GEN_PLAN.md)

## 来源与许可证

ModelNet 基于 Dify 构建，并保留上游开源许可证文件。商业使用、运营多租户服务，或修改前端 Logo / copyright 相关界面之前，请先阅读 [LICENSE](./LICENSE)。

上游项目：

- Dify GitHub：<https://github.com/langgenius/dify>
- Dify 文档：<https://docs.dify.ai>
