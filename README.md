# ModelNet

ModelNet 是一个基于 [Dify](https://github.com/langgenius/dify) 的研究型分支，用于构建、运行和评估多模型协作推理工作流。

本项目保留了 Dify 的可视化工作流画布、模型管理、RAG 流水线、API 服务和 Docker 部署体系，并在此基础上加入 ModelNet 所需的响应级综合、token 级联合解码、数据集加载和 AI-ModelNet / DuetNet 复现实验能力。

> 本仓库基于 Dify 开发。上游 Dify 的版权、署名和 [LICENSE](./LICENSE) 中的修改版 Apache 2.0 许可证条款仍然适用。

## ModelNet 新增能力

- **Response Aggregator**：收集多个上游节点的完整回复，并调用一个聚合模型生成最终答案。输入支持静态权重、变量权重、显式 fallback 权重和诊断元数据。
- **Token Model Source**：在画布上配置单个模型来源，包括 prompt 模板、chat messages、采样参数、已注册模型别名，或内联 llama.cpp 后端配置。
- **Parallel Ensemble**：从多个 `token-model-source` 节点读取模型调用规格，执行 token 级协作解码。内置 token 聚合器包括 `sum_score`、`max_score` 和 `duet_net`。
- **llama.cpp 后端 SPI**：支持服务端模型注册表、内联自定义端点、通过 Console API 代理探测 `/v1/models`、chat-template 应用、top-k 概率，以及通过 `expose_raw_logits` 启用的可选 raw-logit 模式。
- **Data Loader**：新增可扩展的工作流数据加载节点，内置 `inline_json` 和 `jsonl_file` loader，用于 benchmark 和评测工作流。
- **实验资产**：[`docs/ModelNet`](./docs/ModelNet) 下包含 C-Eval / BoolQ JSONL 样例、AI-ModelNet 复现 DSL、DuetNet DSL、论文笔记和实现计划。
- **诊断与安全边界**：使用 `model_net.yaml` 时，模型 URL 保留在服务端；出站模型请求走工作流运行时的 SSRF proxy 路径。

## 工作流模式

### 响应级协作

适合多个模型或工具已经分别产出完整答案的场景。

```text
LLM / HTTP / Code / Agent 输出
        -> Response Aggregator
        -> End / Answer
```

`response-aggregator` 节点现在是 synthesis-only 路径：配置输入 selector、权重、聚合指令和聚合模型即可。旧版 `strategy_name` / `strategy_config` 字段会被主动拒绝，避免导入旧 DSL 后静默跑错语义。

### Token 级协作

适合希望多个模型在解码过程中逐 token 协作的场景。

```text
Data Loader 或 Start
        -> N 个 Token Model Source
        -> Parallel Ensemble
        -> End / Answer
```

每个 `token-model-source` 负责渲染自己的 prompt 和采样参数。`parallel-ensemble` 解析这些 spec，实例化后端，应用每路 source 的权重和 `top_k_override`，再运行选定的 token 聚合器。

## 快速开始

### 1. 启动 Dify / ModelNet 服务栈

Docker 部署方式继承自 Dify。

```bash
cd docker
cp .env.example .env
docker compose up -d --build
```

启动后打开：

```text
http://localhost/install
```

公开部署时请从本 fork 构建并发布 API / Web 镜像。上游 `langgenius/dify-*` 镜像不包含 ModelNet 新增的工作流节点。

源码开发仍沿用 Dify 的前后端分工：

```bash
# 后端命令
uv run --project api <command>

# 前端命令
pnpm install
pnpm dev
```

### 2. 配置 ModelNet 模型别名

如果使用注册表模式，先复制样例配置，再填入自己的 llama.cpp 端点：

```bash
cp api/configs/model_net.yaml.example api/configs/model_net.yaml
```

真实的 `api/configs/model_net.yaml` 已被 git 忽略。容器部署时，需要把你的 registry 挂载到 API / worker 容器中；如果不使用默认路径，请设置 `MODEL_NET_REGISTRY_PATH`。

如果只是临时实验，`Token Model Source` 面板也支持直接填写自定义 llama.cpp inline spec，不必先写入注册表。

### 3. 导入示例工作流

示例 DSL 位于：

- [`docs/ModelNet/examples/workflow_mode`](./docs/ModelNet/examples/workflow_mode)
- [`docs/ModelNet/examples/chat_mode`](./docs/ModelNet/examples/chat_mode)

这些示例覆盖 response aggregation demo、DuetNet token 级路径、AI-ModelNet SI / PI / S2P / P2S 复现路径，以及 C-Eval data-loader 验证工作流。

## 仓库结构

```text
api/core/workflow/nodes/response_aggregator/   响应级综合节点
api/core/workflow/nodes/token_model_source/    模型 source spec 节点
api/core/workflow/nodes/parallel_ensemble/     token 级 runner / backend / aggregator SPI
api/core/workflow/nodes/data_loader/           数据集加载节点
api/configs/model_net.yaml.example             服务端模型注册表模板
dev/modelnet/                                  数据集导出和验证脚本
docs/ModelNet/                                 设计文档、论文、示例和复现计划
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

前端检查：

```bash
cd web
pnpm type-check
pnpm exec eslint app/components/workflow/nodes/response-aggregator app/components/workflow/nodes/token-model-source app/components/workflow/nodes/parallel-ensemble app/components/workflow/nodes/data-loader
pnpm test -- --run app/components/workflow/nodes/response-aggregator app/components/workflow/nodes/token-model-source app/components/workflow/nodes/parallel-ensemble app/components/workflow/nodes/data-loader
```

集成测试主要面向 CI，本地环境不要求每次都跑。

## 关键文档

- [`docs/ModelNet/DEVELOPMENT_PLAN_v3.md`](./docs/ModelNet/DEVELOPMENT_PLAN_v3.md)：当前 token-source / parallel-ensemble 架构。
- [`docs/ModelNet/BACKEND_CAPABILITIES.md`](./docs/ModelNet/BACKEND_CAPABILITIES.md)：后端能力矩阵，以及 probability / logit 语义边界。
- [`docs/ModelNet/EXTENSIBILITY_SPEC.md`](./docs/ModelNet/EXTENSIBILITY_SPEC.md)：backend、runner、aggregator 的 SPI 边界。
- [`docs/ModelNet/EXTENSION_GUIDE.md`](./docs/ModelNet/EXTENSION_GUIDE.md)：新增策略和后端的二次开发指南。
- [`api/configs/MODEL_NET_README.md`](./api/configs/MODEL_NET_README.md)：模型注册表契约和 SSRF 说明。

## 来源与许可证

ModelNet 基于 Dify 构建，并保留上游开源许可证文件。商业使用、运营多租户服务，或修改前端 Logo / copyright 相关界面之前，请先阅读 [LICENSE](./LICENSE)。

上游项目：

- Dify GitHub：<https://github.com/langgenius/dify>
- Dify 文档：<https://docs.dify.ai>
