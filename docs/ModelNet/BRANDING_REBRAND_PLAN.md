# Dify 标识替换为暨南大学 ModelNet 的实施计划

## 目标

将 Dify 前端和用户可见触点中的默认品牌标识替换为「暨南大学 ModelNet」，包括 Logo、页面标题、PWA 信息、登录页、控制台头部、分享页、嵌入式聊天、邮件模板和主要中英文文案。

本计划只针对用户可见品牌，不进行内部工程命名重构。以下内部标识默认保留：

- `dify_config`、`DifyConfig`、`DifyApp` 等 Python 类名和配置名
- `@langgenius/dify-ui` 等 npm 包名和导入路径
- Docker 镜像名、插件标识、数据库默认名、API 内部命名
- 上游服务和协议中必须保留的 Dify 兼容字段

## 合规前置

实际替换前必须先确认 Dify 书面授权或商业许可，这是执行阻断条件。

仓库 `LICENSE` 中明确限制：使用 Dify 前端时，不得移除或修改 Dify 的 Logo 或版权信息，除非获得相应授权。没有授权时，不执行代码和资源替换，只能做内部评估、影响面梳理、素材准备和 allowlist 设计。

当前状态：

- Dify 授权已确认，可以进入实际替换准备阶段。
- 后续交付物中需要保留授权记录或授权文件引用，便于上线和审计时追溯。

合规确认需要覆盖：

- 前端 Logo 和 copyright 修改授权
- 是否允许用 Dify 源码运行多租户环境
- 是否允许替换 `Powered by Dify`、LangGenius copyright、邮件 Logo 和邮件落款
- 是否需要保留 Dify 上游来源说明、开源许可证链接或第三方声明
- 对外部署域名、服务条款、隐私政策和支持邮箱是否已由 ModelNet 承接

## 品牌规范输入

实施前需要准备以下素材和命名：

- 主品牌名：`暨南大学 ModelNet`
- 短品牌名：`ModelNet`
- 英文名：`JNU ModelNet` 或 `ModelNet`
- 官网：`https://www.aimodelnetwork.cn/`
- 代码地址：暂时置空
- 技术支持邮箱：`15225743339@63.com`
- 浅色背景 Logo
- 深色背景 Logo
- 纯白 Logo
- favicon
- PWA 图标，覆盖当前仓库里的全部尺寸：72、96、128、144、152、192、256、384、512
- Apple touch icon
- Windows tile 颜色和图标适配
- 嵌入式聊天 Header Logo
- 嵌入式聊天默认头像 Logo
- 邮件 Logo，可以公开访问，建议由 ModelNet 自有域名或应用静态资源承载
- 品牌主色，用于 `theme_color`、`msapplication-TileColor` 和 PWA 背景
- copyright 文案，例如 `暨南大学 ModelNet. All rights reserved.`
- 隐私政策、服务条款、帮助文档、社区、技术支持邮箱等替换链接

命名需要统一选择，不要在页面里混用多种写法：

- 浏览器标题和控制台 Header：建议 `ModelNet`
- PWA `name` 和邮件正式落款：建议 `暨南大学 ModelNet`
- 英文文案：建议 `JNU ModelNet`

当前素材状态：

- 授权已确认。
- 官网和支持邮箱已确认。
- 代码地址暂时置空，页面中如必须展示代码仓库入口，应先隐藏或留待后续补充。
- Logo、favicon、PWA 图标、邮件 Logo 等素材包暂未提供，先不执行资源文件替换；可以先完成文本、链接、审计和 allowlist 准备。

## 实施范围

### 1. 静态资源

替换或新增以下资源：

- `web/public/logo/logo.svg`
- `web/public/logo/logo-monochrome-white.svg`
- `web/public/logo/logo-site.png`
- `web/public/logo/logo-site-dark.png`
- `web/public/logo/logo-embedded-chat-avatar.png`
- `web/public/logo/logo-embedded-chat-header.png`
- `web/public/logo/logo-embedded-chat-header@2x.png`
- `web/public/logo/logo-embedded-chat-header@3x.png`
- `web/public/favicon.ico`
- `web/public/apple-touch-icon.png`
- `web/public/icon-*.png`
- `web/public/browserconfig.xml`
- `web/public/_offline.html`

注意：资源文件名可以保持不变，减少代码改动范围；文件内容替换为 ModelNet 品牌素材。

嵌入式聊天资源不能漏掉。当前代码通过 `logo-embedded-chat-header.tsx` 和 `logo-embedded-chat-avatar.tsx` 加载专用图片，如果只替换 `logo.svg`，嵌入式聊天仍会显示 Dify 资源。

### 2. 浏览器和 PWA 元信息

更新：

- `web/public/manifest.json`
- `web/app/layout.tsx`
- `web/public/browserconfig.xml`
- `web/public/_offline.html`

替换内容包括：

- `name`
- `short_name`
- `description`
- `apple-mobile-web-app-title`
- `theme_color`
- `background_color`
- favicon / icon 引用
- Windows tile color
- 离线页 `<title>` 和页面内可见品牌文案

建议：

- `name`: `暨南大学 ModelNet`
- `short_name`: `ModelNet`
- `description`: `Multi-model collaborative inference platform`

### 3. 默认页面标题

更新：

- `web/hooks/use-document-title.ts`

当前默认标题在无企业 branding 配置时回退到 `Dify`。需要改为 `ModelNet` 或 `暨南大学 ModelNet`。

同时更新对应测试：

- `web/hooks/use-document-title.spec.ts`

还需要搜索并处理绕过 `useDocumentTitle` 的标题写法，例如：

- `web/app/components/datasets/list/datasets.tsx` 中的 `document.title = ... - Dify`
- `web/public/_offline.html` 中的 `Dify - Offline`
- 其他 `document.title`、`useTitle`、`useFavicon` 调用

### 4. Logo 组件

更新：

- `web/app/components/base/logo/dify-logo.tsx`
- `web/app/components/base/logo/logo-embedded-chat-avatar.tsx`
- `web/app/components/base/logo/logo-embedded-chat-header.tsx`
- `web/app/components/base/logo/logo-site.tsx`
- `web/app/components/base/logo/index.stories.tsx`
- `web/app/components/base/logo/__tests__/`

建议保留组件名 `DifyLogo`，只替换显示资源和 alt 文案。这样可以避免大范围 import 重命名。

alt 文案建议改为：

- `ModelNet logo`

如果保留 `DifyLogo` 组件名，需要在 allowlist 中标注它是内部组件名，不是用户可见品牌。

### 5. 前端主要页面

优先检查并替换以下区域：

- 登录页和注册页
- 忘记密码和重置密码页
- 控制台顶部 Header
- Account / About 页面
- Billing / pricing 页面
- 分享应用页面
- WebApp 页面
- 嵌入式聊天 Header
- `Powered by Dify` 区域
- 自定义 WebApp 品牌预览区域
- 安装页和激活页
- OAuth 授权页
- Human Input 表单和各种提交状态页
- Apps / Datasets 页脚
- 账号下拉里的帮助、社区、支持入口
- 离线页

重点文件入口：

- `web/app/signin/_header.tsx`
- `web/app/signin/layout.tsx`
- `web/app/signup/layout.tsx`
- `web/app/forgot-password/page.tsx`
- `web/app/reset-password/page.tsx`
- `web/app/install/page.tsx`
- `web/app/activate/page.tsx`
- `web/app/account/oauth/authorize/layout.tsx`
- `web/app/(shareLayout)/webapp-signin/layout.tsx`
- `web/app/(shareLayout)/webapp-reset-password/layout.tsx`
- `web/app/(humanInputLayout)/form/[token]/form.tsx`
- `web/app/account/(commonLayout)/header.tsx`
- `web/app/components/header/index.tsx`
- `web/app/components/header/account-about/index.tsx`
- `web/app/components/header/account-dropdown/support.tsx`
- `web/app/components/header/utils/util.ts`
- `web/app/components/base/chat/embedded-chatbot/index.tsx`
- `web/app/components/base/chat/embedded-chatbot/header/index.tsx`
- `web/app/components/base/chat/embedded-chatbot/chat-wrapper.tsx`
- `web/app/components/base/chat/embedded-chatbot/utils.ts`
- `web/app/components/base/chat/chat-with-history/sidebar/index.tsx`
- `web/app/components/share/text-generation/text-generation-sidebar.tsx`
- `web/app/components/apps/footer.tsx`
- `web/app/components/apps/list.tsx`
- `web/app/components/datasets/list/index.tsx`
- `web/app/components/datasets/list/datasets.tsx`
- `web/app/components/custom/custom-web-app-brand/components/powered-by-brand.tsx`
- `web/app/components/custom/custom-web-app-brand/components/chat-preview-card.tsx`
- `web/app/components/custom/custom-web-app-brand/index.tsx`
- `web/app/components/billing/pricing/header.tsx`
- `web/app/education-apply/education-apply-page.tsx`
- `web/app/components/goto-anything/actions/commands/forum.tsx`

注意：前端用户可见字符串应进入 `web/i18n/en-US/` 和 `web/i18n/zh-Hans/`，不要新增硬编码文案。已有硬编码示例，例如 `Talk to Dify`，应迁移到 i18n 后再替换。

### 6. 国际化文案

优先替换中文和英文：

- `web/i18n/zh-Hans/*.json`
- `web/i18n/en-US/*.json`

优先级：

1. 登录、注册、重置密码、邀请、账号相关文案
2. 页面标题、导航、关于页面、帮助入口
3. WebApp 和嵌入式聊天中的品牌文案
4. Billing、Enterprise、Marketplace 中的 Dify 官方说明
5. 文档示例和模板中的 Dify 示例
6. 维护通知、帮助入口、支持邮箱和社区入口

额外检查：

- `web/i18n-config/language.ts`
- `web/context/i18n.ts`
- `web/app/components/develop/template/*.mdx`
- `web/app/components/base/*/*.stories.tsx`
- `web/app/components/**/__tests__/*` 中与真实文案强绑定的断言

其他语言可以分两种策略：

- 暂时保留，后续统一翻译
- 如果产品只面向中英文用户，隐藏其他语言入口，降低残留品牌风险

如果保留其他语言入口，需要至少替换其中的 `support@dify.ai`、`Powered by Dify`、登录/帮助/账号相关品牌文案，否则用户切换语言后仍会看到旧品牌。

### 7. 外链和联系方式

搜索并分类处理以下内容：

- `dify.ai`
- `docs.dify.ai`
- `cloud.dify.ai`
- `forum.dify.ai`
- `marketplace.dify.ai`
- `assets.dify.ai`
- `api.dify.ai`
- `updates.dify.ai`
- `creators.dify.ai`
- `support@dify.ai`
- `LangGenius`

处理策略：

- 隐私政策、服务条款、官网、技术支持邮箱替换为 ModelNet 自有地址
- Dify 上游文档、插件市场、插件兼容性说明如果仍依赖上游，可以保留但需要明确其为上游链接
- 不再使用的 Dify Cloud、pricing、billing 链接应隐藏或删除
- `assets.dify.ai` 中的 Dify Logo 必须替换；非品牌通用图标可以保留，但需要写入 allowlist
- 如果不使用 Dify Marketplace / Creators Platform，应禁用入口并清理相关默认 URL
- 如果继续使用 Dify Marketplace，应在界面和 allowlist 中明确它是上游生态服务，不是 ModelNet 自有服务

当前外链决策：

- 官网统一替换为 `https://www.aimodelnetwork.cn/`。
- 技术支持邮箱统一替换为 `15225743339@63.com`。
- 代码地址先置空；相关入口暂时隐藏或加入待补充清单。
- 先保留部分 Dify 上游文档链接，但必须在 allowlist 中标注保留原因，并避免把 Dify 文档误写成 ModelNet 自有文档。

重点文件和配置入口：

- `web/context/i18n.ts`
- `web/app/components/header/account-dropdown/support.tsx`
- `web/app/components/header/utils/util.ts`
- `web/app/components/apps/footer.tsx`
- `web/app/components/goto-anything/actions/commands/forum.tsx`
- `web/app/components/workflow/nodes/human-input/components/delivery-method/method-selector.tsx`
- `web/.env.example`
- `api/.env.example`
- `api/configs/feature/__init__.py`
- `docker/.env.example`
- `docker/middleware.env.example`
- `docker/docker-compose.yaml`
- `docker/docker-compose-template.yaml`
- `docker/ssrf_proxy/squid.conf.template`

### 8. 邮件默认品牌

更新：

- `api/libs/email_i18n.py`
- `api/templates/`
- `api/templates/without-brand/`

重点替换：

- 默认 `application_title`
- 邮件 Logo URL
- 邮件 alt 文案
- 邮件主题
- 注册邮件
- 邀请邮件
- 登录验证码邮件
- 重置密码邮件
- 修改邮箱邮件
- 工作区所有权转移邮件
- 删除账号邮件
- 工作流通知邮件
- 队列监控和知识库自动禁用通知
- 触发事件和 API rate limit 通知，如果对应模板存在或后续补齐

建议默认标题：

- `暨南大学 ModelNet`

重要细节：

- `api/libs/email_i18n.py` 中 branding 开启时会使用 `branded_template_path`，当前很多 `branded_template_path` 指向 `without-brand/*`，所以不能只替换根目录模板。
- `branding.enabled = false` 时 `application_title` 会回退到 `Dify`，如果目标是默认品牌替换，需要把默认回退也改为 ModelNet，并同步测试。
- 删除账号、知识库通知等主题目前仍有硬编码 `Dify.AI` / `Dify`，不能只依赖 `application_title`。
- 模板中的 `https://assets.dify.ai/images/logo.png` 是远程 Dify Logo，需要替换为 ModelNet 邮件 Logo。
- 实施前应检查 `create_default_email_config()` 引用的所有 `template_path` 和 `branded_template_path` 是否真实存在，避免品牌替换时掩盖既有模板缺失问题。

### 9. 后端系统功能接口

检查：

- `api/services/feature_service.py`
- `web/types/feature.ts`
- `web/context/app-context-provider.tsx`
- 所有 `systemFeatures.branding.enabled` 条件分支

确认系统 branding 默认值和前端类型定义一致。

不要为了重品牌而简单强制 `branding.enabled = true`。当前前端有多处逻辑用 `branding.enabled` 控制功能和页面区域是否展示，例如邀请按钮、页脚、条款链接、自定义 branding 上传能力等。强行开启可能改变产品行为。

建议选择一种实现模式：

1. 默认品牌替换模式：保持 `branding.enabled = false`，替换默认资源、默认标题、默认邮件和默认文案。这是社区版默认品牌替换的主要路径。
2. 企业 branding 配置模式：只在已有企业 branding 能力开启时，把 `application_title`、`workspace_logo`、`login_page_logo`、`favicon` 设置为 ModelNet 素材，并完整回归所有 `branding.enabled` 条件分支。

## 不建议修改的内容

以下内容不建议为了去品牌而改名：

- Python 类名、模块名和配置名中的 `Dify`
- 数据库表、迁移、内部枚举和协议字段
- npm 包名、workspace 包名和 import alias
- Docker Compose 服务名、镜像名和环境变量名
- 插件 marketplace unique identifier
- 单元测试中只作为普通示例输入的 `Hello Dify`
- `X-Dify-Version`、Dify DSL、插件兼容性字段、workflow-as-tool compact type 等协议兼容标识
- `Dify Version Compatibility` 这类描述上游插件最低 Dify 版本的技术文案
- License、README 中用于说明上游来源和合规边界的文字

这些内容不是主要用户可见品牌，强行替换会增加升级和维护成本。

但以下内容虽然包含 Dify 字样，仍需要按用户可见性判断：

- 文档模板、API 示例、控制台示例中的 `api.dify.ai` 如果会展示给用户，需要替换为当前部署 API 域名或解释为上游示例
- `isDify()` 这类域名判断如果影响嵌入式聊天 Logo，需要改为 ModelNet 域名或抽象为配置项
- Storybook 和测试里如果断言真实 alt/title/可见文案，需要随实际文案更新

## 搜索和审计命令

实施前建立基线：

```bash
rg -n "Dify|DIFY|dify\.ai|docs\.dify|cloud\.dify|forum\.dify|marketplace\.dify|assets\.dify|api\.dify|updates\.dify|creators\.dify|support@dify\.ai|Powered by Dify|LangGenius" web api docker \
  -g '!node_modules' \
  -g '!dist' \
  -g '!build' \
  -g '!*.lock'
```

聚焦用户可见范围：

```bash
rg -n "Dify|dify\.ai|docs\.dify|cloud\.dify|forum\.dify|marketplace\.dify|assets\.dify|api\.dify|updates\.dify|creators\.dify|support@dify\.ai|Powered by Dify|LangGenius" \
  web/app web/public web/i18n/en-US web/i18n/zh-Hans web/i18n-config web/context \
  api/templates api/libs/email_i18n.py api/services/feature_service.py api/configs/feature \
  web/.env.example api/.env.example docker/.env.example docker/middleware.env.example
```

标题和 PWA 专项检查：

```bash
rg -n "document\.title|useTitle|useDocumentTitle|useFavicon|apple-mobile-web-app-title|Dify - Offline|manifest|browserconfig" \
  web/app web/hooks web/public
```

Logo 和远程品牌资源专项检查：

```bash
rg -n "logo-embedded|logo-site|logo\.svg|Dify logo|assets\.dify\.ai|logo\.png|favicon|apple-touch-icon" \
  web/app web/public api/templates
```

邮件模板完整性检查：

```bash
find api/templates -type f | sort
rg -n "template_path|branded_template_path|application_title|Dify|assets\.dify\.ai|support@dify\.ai" \
  api/libs/email_i18n.py api/templates
```

实施后复查：

```bash
rg -n "Dify|dify\.ai|docs\.dify|cloud\.dify|forum\.dify|marketplace\.dify|assets\.dify|api\.dify|updates\.dify|creators\.dify|support@dify\.ai|Powered by Dify|LangGenius" \
  web/app web/public web/i18n/en-US web/i18n/zh-Hans web/i18n-config web/context \
  api/templates api/libs/email_i18n.py api/services/feature_service.py api/configs/feature \
  web/.env.example api/.env.example docker/.env.example docker/middleware.env.example
```

对剩余结果建立 allowlist，至少包含：

- 文件路径和行号
- 保留原因
- 是否用户可见
- 是否需要授权
- 后续责任人和复查日期

## 验证计划

### 静态检查

前端：

```bash
# 从仓库根目录执行
pnpm lint:fix
pnpm type-check
pnpm --dir web i18n:check
```

如只改少量文件，可以先跑针对性检查：

```bash
pnpm eslint --fix <changed-files>
pnpm --dir web type-check
pnpm --dir web test hooks/use-document-title.spec.ts app/components/base/logo/__tests__/dify-logo.spec.tsx
```

后端：

```bash
uv run --project api pytest api/tests/unit_tests/libs/test_email_i18n.py api/tests/unit_tests/tasks/test_mail_send_task.py -q
```

如果改动了 `FeatureService` 或邮件配置，再补充：

```bash
uv run --project api pytest api/tests/unit_tests/services api/tests/unit_tests/libs/test_email_i18n.py -q
```

如本地环境不具备完整依赖，至少运行相关文件的 lint、类型检查、单测和搜索审计。集成测试按仓库约定主要由 CI 覆盖。

### 页面验收

重点手工检查：

- `/signin`
- `/signup`
- `/forgot-password`
- `/reset-password`
- `/install`
- `/activate`
- `/account/oauth/authorize`
- WebApp 登录和重置密码页
- 控制台首页
- 应用详情页
- Knowledge / Dataset 页面
- Account / About 页面
- Account dropdown 帮助、社区、支持入口
- Apps 页脚和 Dataset 页脚
- 分享 WebApp 页面
- Text generation 分享页面
- 嵌入式聊天
- Human Input 表单：正常、成功、过期、已提交、限流、表单不存在
- 自定义 WebApp 品牌设置和预览
- Marketplace / plugin 页面，如果仍启用
- Billing / pricing / education 页面，如果仍启用
- 离线页 `_offline.html`
- PWA 安装弹窗
- 浏览器 tab 标题和 favicon

检查项：

- 页面不再展示未授权的 Dify Logo 或 LangGenius copyright
- 页面标题显示 ModelNet 或约定的完整品牌名
- favicon 和 PWA 图标已更新
- Windows tile 图标和颜色已更新
- 深色模式和浅色模式 Logo 均可读
- `Powered by Dify` 已替换、隐藏或按授权要求处理
- 隐私、条款、帮助、支持邮箱不再指向错误的 Dify 官方页面
- 如果保留 Dify Marketplace、Dify Docs 或插件兼容性文案，页面能清楚表达这是上游服务或上游兼容字段
- 中英文切换后无旧品牌泄漏
- 其他语言入口如果仍开放，至少无旧支持邮箱和 Powered by Dify

### 邮件验收

发送或渲染以下邮件模板：

- 注册邮件
- 邀请成员邮件
- 登录验证码邮件
- 重置密码邮件
- 修改邮箱邮件
- 工作区所有权转移邮件
- 删除账号邮件
- 工作流通知邮件
- 队列监控邮件
- 知识库自动禁用邮件

检查主题、正文、Logo、alt 文案、链接、支持邮箱和落款。

邮件验收需要覆盖两种状态：

- `branding.enabled = false`：默认品牌应为 ModelNet，不应回退到 Dify
- `branding.enabled = true`：企业 branding 模板也不应引用 Dify Logo 或 Dify 文案，除非在 allowlist 中说明

## 交付物

- 授权或商业许可确认记录
- 品牌资源文件替换清单
- 代码改动清单
- Dify 残留文本 allowlist
- 外链和远程资源 allowlist
- i18n 变更清单
- 页面截图验收记录
- 邮件模板验收记录
- 配置和环境变量变更清单
- 回滚说明

## 建议执行顺序

1. 确认授权和品牌素材
2. 选择实现模式：默认品牌替换，或企业 branding 配置模式
3. 建立搜索基线和初始 allowlist
4. 替换静态资源、嵌入式聊天资源、PWA 元信息、browserconfig 和离线页
5. 替换默认标题、favicon 逻辑、Logo 组件及其测试
6. 替换登录页、安装/激活页、控制台 Header、分享页、嵌入式聊天、Human Input、页脚和自定义品牌预览
7. 替换中英文 i18n 文案，并决定其他语言策略
8. 替换邮件默认品牌、根目录模板和 `without-brand` 模板
9. 处理外链、支持渠道、Marketplace / Docs / Cloud / Creators 配置
10. 搜索审计并建立最终 allowlist
11. 运行 lint、type-check、i18n check 和相关测试
12. 部署 staging，完成页面、邮件、PWA 和缓存验收

## 回滚策略

所有品牌替换应在独立分支完成，例如：

```bash
git checkout -b brand/modelnet-rebrand
```

回滚时优先恢复：

- `web/public/logo/*`
- `web/public/icon-*.png`
- `web/public/favicon.ico`
- `web/public/manifest.json`
- `web/public/browserconfig.xml`
- `web/public/_offline.html`
- `web/app/layout.tsx`
- `web/hooks/use-document-title.ts`
- `web/app/components/base/logo/*`
- `web/app/components/header/*`
- `web/app/components/base/chat/*`
- `web/app/components/share/*`
- `web/app/(humanInputLayout)/*`
- `web/i18n/en-US/*`
- `web/i18n/zh-Hans/*`
- `web/i18n-config/*`
- `web/context/i18n.ts`
- `web/.env.example`
- `api/.env.example`
- `api/libs/email_i18n.py`
- `api/templates/*`
- `api/configs/feature/__init__.py`
- `docker/.env.example`
- `docker/middleware.env.example`
- `docker/docker-compose.yaml`
- `docker/docker-compose-template.yaml`

如部署到 CDN，需要同步清理静态资源缓存、浏览器缓存、PWA service worker 缓存和邮件客户端可缓存的远程 Logo，否则 favicon、PWA 图标或邮件 Logo 可能继续显示旧品牌。
