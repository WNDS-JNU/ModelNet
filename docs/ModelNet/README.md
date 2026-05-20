# ModelNet 文档入口

本目录是 ModelNet 二开分支的文档中心。ModelNet 的概念基础来自 [《模型互联网：概念、现状和未来》](./模型互联网.pdf)：通过构建模型间标准化通路，实现模型互联互通、能力共享与协同推理。

如果只想理解本项目，请先读根目录 [README.md](../../README.md)。如果要继续开发、复现实验或扩展后端，请按下面的读者路径进入。

## 先读这几份

- [模型互联网 PDF](./模型互联网.pdf)：ModelNet / AI-ModelNet 的概念来源，重点是模型节点、标准化通路、动态发现、按需组合、协同推理，以及资源层/服务层/交互层/应用层。
- [active/ROADMAP.md](./active/ROADMAP.md)：当前研发路线、主要 source of truth 和阅读顺序。
- [active/TASKS.md](./active/TASKS.md)：详细执行清单、阶段状态和历史落地说明。
- [architecture/EXTENSIBILITY_SPEC.md](./architecture/EXTENSIBILITY_SPEC.md)：backend / runner / aggregator 三轴 SPI 合约。
- [architecture/EXTENSION_GUIDE.md](./architecture/EXTENSION_GUIDE.md)：新增聚合器、runner、后端和 trace 消费逻辑的二开指南。
- [architecture/BACKEND_CAPABILITIES.md](./architecture/BACKEND_CAPABILITIES.md)：后端能力矩阵，以及 probability / logit 语义边界。

## 按读者进入

### 工作流使用者

- [architecture/THREE_NODES_BEGINNER_GUIDE.md](./architecture/THREE_NODES_BEGINNER_GUIDE.md)：用新人视角解释 `token-model-source`、`parallel-ensemble`、`response-aggregator` 三个核心节点。
- [examples/workflow_mode](./examples/workflow_mode)：可导入 Dify Studio 的 workflow DSL。
- [模型注册表说明](../../api/configs/MODEL_NET_README.md)：`model_net.yaml` 的字段、加载路径和 SSRF 边界。

### 二开开发者

- [architecture/EXTENSION_GUIDE.md](./architecture/EXTENSION_GUIDE.md)：最小可工作示例，覆盖响应级策略、token 聚合器、runner、backend、trace 消费和单测脚手架。
- [architecture/EXTENSIBILITY_SPEC.md](./architecture/EXTENSIBILITY_SPEC.md)：稳定的 SPI 设计边界。
- [architecture/THREE_NODES_BEGINNER_GUIDE.md](./architecture/THREE_NODES_BEGINNER_GUIDE.md)：前后端节点注册、变量输出、i18n 和常见坑。

### 后端与推理服务实现者

- [architecture/BACKEND_CAPABILITIES.md](./architecture/BACKEND_CAPABILITIES.md)：后端 capability、top-k 概率、raw logits、OpenAI/vLLM 语义差异。
- [operations/vllm/TOKENLEVEL_VLLM_PLAN.md](./operations/vllm/TOKENLEVEL_VLLM_PLAN.md)：vLLM completion/chat-token 路径、logprob 兼容和后续迁移计划。
- [operations/runtime/MODELNET_LOCAL_CHAT_TEMPLATES.md](./operations/runtime/MODELNET_LOCAL_CHAT_TEMPLATES.md)：本地 chat-template 运行说明。
- [模型注册表说明](../../api/configs/MODEL_NET_README.md)：服务端模型别名与后端 spec 契约。

### 研究与复现使用者

- [research/PAPER_REPRODUCTION_PLAN.md](./research/PAPER_REPRODUCTION_PLAN.md)：论文复现的阶段计划和数据集设置。
- [research/UNDERGRAD_RESEARCH_PLAYBOOK.md](./research/UNDERGRAD_RESEARCH_PLAYBOOK.md)：面向学生的研究路线和实验理解指南。
- [research/TOP_CONFERENCE_REPRODUCTION_CANDIDATES.md](./research/TOP_CONFERENCE_REPRODUCTION_CANDIDATES.md)：可映射到 ModelNet 工作流的顶会相似工作。
- [../../dev/modelnet/README.md](../../dev/modelnet/README.md)：DSL 生成、DuetNet / AI-ModelNet 评测和动态协作路由脚本。

### 维护者与运维者

- [operations/auto-dsl-gen/AUTO_DSL_GEN_PLAN.md](./operations/auto-dsl-gen/AUTO_DSL_GEN_PLAN.md)：从自然语言意图生成 Dify DSL 的方案。
- [operations/fixes/DUET_NET_TRACE_PUSH_FIX_PLAN.md](./operations/fixes/DUET_NET_TRACE_PUSH_FIX_PLAN.md)：trace artifact 下载修复计划。
- [operations/branding/BRANDING_REBRAND_PLAN.md](./operations/branding/BRANDING_REBRAND_PLAN.md)：品牌与重命名相关计划。
- [history/LANDING.md](./history/LANDING.md)：历史落地记录合集。

## 示例工作流

- [DuetNet 主流程](./examples/workflow_mode/token_level_collaborative_reasoning_for_parallel_multi_models/duet_net_main.yml)
- [DuetNet 数据集循环流程](./examples/workflow_mode/token_level_collaborative_reasoning_for_parallel_multi_models/duet_net_main_loop_dataset_zh.yml)
- [AI-ModelNet 混合路由流程](./examples/workflow_mode/multi_model_serial_and_parallel_collaborative_inference_in_ai_modelnet/paper_hybrid_router.yml)
- [动态协作路由流程](./examples/workflow_mode/dynamic_model_routing_based_on_collaborative_relationship/dynamic_collab_route.yml)

## 目录说明

- `active/`：当前项目状态、路线图和下一步计划。
- `architecture/`：稳定架构合约、扩展指南和能力矩阵。
- `operations/`：运行时说明、兼容性计划、修复计划、品牌和运维记录。
- `research/`：论文复现计划、研究指南、参考论文、模型元数据和参考代码。
- `examples/`：workflow-mode DSL 示例。
- `history/`：已被替代的开发计划和历史 landing 记录。

## 维护规则

本目录顶层尽量只保留该 README 和长期入口文档。新的实现计划优先放到 `operations/<topic>/`；历史落地记录追加到 `history/LANDING.md`，不要继续在顶层散落临时文档。
