# Claude Cowork / TRAE / Codex：离线自学手册（1 天速成 + 6 周项目计划）

整理时间：2026-06-13  
来源：本仓库 [README.md](file:///Users/li/ai%20pm%20learning/claude-cowork-pm-guide/README.md) + README 中外链文章/课程/视频页面（已做离线摘要，非逐字转载）+ Trae/Codex 官方资料（见文末“信息来源”）

## 目录
- [你今天的通关目标](#你今天的通关目标)
- [这份手册现在怎么用](#这份手册现在怎么用)
- [学习材料地图](#学习材料地图)
- [6 周学习路线（统一版）](#6-周学习路线统一版)
- [主项目定义：医疗 RAG + Story Card](#主项目定义医疗-rag--story-card)
- [60 分钟快速上手（官方入门离线版）](#60-分钟快速上手官方入门离线版)
- [核心概念：8 要素 + 20 概念速查](#核心概念8-要素--20-概念速查)
- [扩展到 TRAE 与 Codex（对照表 + 迁移方法）](#扩展到-trae-与-codex对照表--迁移方法)
- [TRAE 快速上手（离线版）](#trae-快速上手离线版)
- [Codex 快速上手（离线版）](#codex-快速上手离线版)
- [不配 OpenAI：DeepSeek 路线（也能完整练通）](#不配-openaideepseek-路线也能完整练通)
- [一日学习路径（按产出驱动）](#一日学习路径按产出驱动)
- [工作流落地：拆解-配备-组合](#工作流落地拆解-配备-组合)
- [Connectors 离线指南（把数据接进来）](#connectors-离线指南把数据接进来)
- [课程与案例库：离线摘要版](#课程与案例库离线摘要版)
- [实操题库（选 1 条链路跑通）](#实操题库选-1-条链路跑通)
- [模板区（可直接复制）](#模板区可直接复制)
- [自查清单（今天结束前）](#自查清单今天结束前)
- [信息来源（链接）](#信息来源链接)

---

## 你今天的通关目标
只做 3 件事，做完就算“会用且能复用”：
- 产物 A：一张能力地图（你能用一句话解释每个模块能解决什么问题）
- 产物 B：跑通一条你自己的端到端链路（有输入、有步骤、有可验收输出）
- 产物 C：沉淀一个可复用 Skill（最小可用版本：输入/输出/约束清楚）

---

## 这份手册现在怎么用
这份手册已经从“1 天速通版”升级成两层用途：

- 第一层：当日上手  
  适合你今天马上开始，用来快速理解 Cowork / TRAE / Codex / DeepSeek 路线、跑通最小任务闭环。
- 第二层：6 周项目学习  
  适合你接下来围绕一个真实项目持续推进，把概念、方法论、评测、作品集整合起来。

推荐搭配方式：
- 今天先读这份手册里的 `60 分钟快速上手`、`核心概念`、`不配 OpenAI：DeepSeek 路线`
- 接着配合 [feishu-anthropic-notes-offline.md](file:///Users/li/ai%20pm%20learning/claude-cowork-pm-guide/feishu-anthropic-notes-offline.md) 学 `Workflow / Agent / 上下文工程`
- 再配合 [学习材料包_给Trae用.md](file:///Users/li/ai%20pm%20learning/claude-cowork-pm-guide/学习材料包_给Trae用.md) 与 [overall-learning-plan-zh.md](file:///Users/li/ai%20pm%20learning/claude-cowork-pm-guide/overall-learning-plan-zh.md) 进入 6 周项目计划

---

## 学习材料地图
你现在仓库里的 4 份核心材料，功能已经可以明确分工：

- [offline-handbook-zh.md](file:///Users/li/ai%20pm%20learning/claude-cowork-pm-guide/offline-handbook-zh.md)  
  角色：工具认知与离线速查手册  
  重点：Cowork / TRAE / Codex / DeepSeek / Workflow 基础 / 一天内可跑通的任务

- [feishu-anthropic-notes-offline.md](file:///Users/li/ai%20pm%20learning/claude-cowork-pm-guide/feishu-anthropic-notes-offline.md)  
  角色：Agent / Workflow / Context Engineering 方法论手册  
  重点：什么时候用 Workflow、什么时候才需要 Agent、多代理与上下文治理

- [学习材料包_给Trae用.md](file:///Users/li/ai%20pm%20learning/claude-cowork-pm-guide/学习材料包_给Trae用.md)  
  角色：转型目标、评测驱动、复盘模板、面试导向说明  
  重点：医疗 RAG 方向、6 周节奏、红线、旧项目复盘模板

- [overall-learning-plan-zh.md](file:///Users/li/ai%20pm%20learning/claude-cowork-pm-guide/overall-learning-plan-zh.md)  
  角色：统一总纲  
  重点：把上面三份材料串成一个 6 周项目式学习系统

一句话记法：
- 这份手册回答“怎么开始”
- 飞书离线笔记回答“为什么这样做”
- 学习材料包回答“按什么标准学”
- 统一总纲回答“接下来 6 周到底怎么走”

---

## 6 周学习路线（统一版）
你的学习主线已经从“广泛了解 AI 工具”升级为“围绕一个真实项目练 AI PM 核心能力”。

### 目标项目
- 医疗 RAG 知识库问答 + Story Card 生成器

### 核心目标
- 用一个真实业务场景练会：立项、评测、RAG、上下文工程、AI coding、医疗合规、作品集包装

### 每周目标
| 周次 | 核心主题 | 核心产出 | 重点能力 |
|---|---|---|---|
| W1 | 旧项目复盘 + 评测驱动入门 | 失败复盘文档、评测驱动学习笔记 | 复盘、Baseline、Judge、方法论 |
| W2 | 新项目立项 + 评测集 | 产品定义文档、30 条评测集、资料清单 | 立项、范围控制、定义“什么是好” |
| W3 | v1 搭建 | 可运行 MVP、检索结果、基线分数 | 数据管道、chunk、检索、引用 |
| W4 | 评测驱动迭代 | 3 轮迭代记录、分数变化 | 分析失败、针对性改进、验证无回退 |
| W5 | Story Card + 医疗合规 | Story Card 模板、拒答机制、演示视频 | 输出物料、claim-evidence 绑定、边界控制 |
| W6 | 面试打包 | README、10 分钟项目讲稿、模拟问答 | 作品集包装、表达、复盘总结 |

### 并行副线
- 黑客级竞品调研
- 每周至少产出一份竞调相关文档
- 目标不是“做竞品表”，而是学会从体验、能力、评测三层逆向拆解 AI 产品

### 每周固定节奏
- 周一：明确本周目标与验收标准
- 周二到周四：做主项目
- 周五：跑评测与改进
- 周六：做竞品调研与阅读整理
- 周日：交付本周产出，做复盘，安排下周任务

如果你要按正式计划推进，请以 [overall-learning-plan-zh.md](file:///Users/li/ai%20pm%20learning/claude-cowork-pm-guide/overall-learning-plan-zh.md) 为主文档，这里保留离线速查版。

---

## 主项目定义：医疗 RAG + Story Card
这是目前最适合你的主项目，因为它同时满足 4 个条件：
- 有真实行业场景：医疗 B 端、药企、一线代表
- 有高价值红线：幻觉、越界、无引用在这个场景都不能接受
- 有明显作品集亮点：检索问答 + 引用 + 一页式物料
- 能顺手训练 AI PM 的评测驱动方法，而不是只做一个 demo

### 用户与场景
- 用户：一线医药代表
- 场景：拜访医生前后，从药企内部 `PPT / PDF / DOCX` 资料中检索证据，并生成一页式 Story Card

### 输入
- `PPT`
- `PDF`
- `DOCX`
- 后续可扩展内部 FAQ、Markdown、网页摘录

### 输出
- 带引用的知识问答结果
- One-page Story Card
- 二维码入口（跳转证据包或详情页）

### 必守红线
- 不碰患者隐私数据
- 不做诊断建议
- 没有证据就输出 `unknown`
- 每条 claim 都要有 evidence

### 这个项目对应你要学的 AI PM 能力
- 立项：为什么是一线代表，而不是泛医疗问答
- 方法论：为什么医疗场景必须评测驱动
- 产品设计：问答与 Story Card 如何拆链路
- 技术理解：文档抽取、chunk、检索、生成、引用
- 合规意识：拒答、溯源、边界
- 面试表达：从失败复盘到重做成功的故事

---

## 60 分钟快速上手（官方入门离线版）
来源：https://support.claude.com/en/articles/13345190-get-started-with-claude-cowork（已做离线摘要）

### 0) 你在做什么（先校准心智模型）
把 Cowork 当成“桌面工作台”，它不是只会对话的窗口，而是能在你授权范围内：
- 读写本地文件夹
- 拆解并执行多步骤任务
- 产出真实的文件（报告/表格/清单/脚本/总结等）

### 1) 前置条件（5 分钟确认）
- 需要 Claude Desktop（Cowork 不在网页版里用）
- 需要付费套餐（Pro/Max/Team/Enterprise）
- 执行任务时需要联网，并且 Desktop 要保持打开（电脑休眠/锁屏可能中断任务）

### 2) 权限与安全（10 分钟把“边界”立好）
你可以把它想成“把某个文件柜的钥匙临时交给一个助理”，但钥匙只开这一个柜子：
- 文件读写：Claude 只能访问你选择共享的本地文件夹
- 删除保护：永久删除会弹窗，需要你手动允许
- 联网与组织管控：团队/企业场景存在额外管控项（例如某些联网能力可在组织设置中关闭）

### 3) 第一个任务（25 分钟，跑通“读→写”闭环）
目标：让 Cowork 从你的一个文件夹里读入材料，输出一份结构化文档写回同一文件夹。

建议用这条最小指令（把方括号替换成你的真实内容）：

> 读取工作区里的 [会议纪要.md / 用户反馈.txt / 需求草稿.md]，输出一份 `00-整理输出.md`，包含：背景、关键结论、待澄清问题、下一步行动清单（负责人/截止时间/依赖）。

验收标准：
- 你能在本地看到一个新文件 `00-整理输出.md`
- 文件里有明确的“待澄清问题”（至少 3 条），并且每条都能反问到具体信息来源

### 4) 常见卡点（快速排查）
- 任务中断：检查 Desktop 是否关闭、电脑是否休眠/锁屏
- 输出文件找不到：通常是没有给到正确文件夹权限或输出路径写错
- 用量消耗快：把轻问答放 Chat，把相关事项尽量合并成“一次 Cowork 任务”

---

## 核心概念：8 要素 + 20 概念速查
### 8 Core Elements（仓库原文要点离线版）
来源：[README.md:L18-L34](file:///Users/li/ai%20pm%20learning/claude-cowork-pm-guide/README.md#L18-L34)

用“工厂模型”记最稳：
- Chat：便利店窗口，适合一次性问答与文本生成；不操作本地文件
- Cowork：车间工作台，可授权读写本地文件，执行多步骤任务（核心）
- Code：工程机修间，偏命令行/编程与自动化
- Projects：档案柜/项目大脑，把背景、规范、口径沉淀成长期上下文
- Skills：标准作业卡（SOP），把重复劳动变成一键执行
- Connectors：水电管线，接入 Drive/Notion/Gmail/Slack 等真实数据源
- Plugins：成套工具箱，把 Skills + Connectors + Sub-agents 打包复用
- Sub-agents / Dispatch / Scheduled Tasks：并行项目组 / 远程派单 / 定时流水线

### 20 个概念速查（新手最有用版本）
来源：https://aidiscoveries.io/20-claude-cowork-concepts-explained-beginner-to-advanced-2025-complete-guide/（已做离线摘要）

只记“最能立刻提升交付质量”的 8 个：
- Workspace Folder：你允许它动手的本地文件夹（所有产出落地的地方）
- `CLAUDE.md`：项目级固定说明（口径、格式、禁止项、验收标准），让输出稳定
- Global Instructions：全局偏好（语言、风格、默认输出格式）
- Context Window：同一会话能“同时记住”的信息容量；长会话要学会分层存放
- Multimodal：支持图片/PDF/截图等输入（适合评审原型、读图表）
- Web Search：用于实时信息（注意引用来源与可验证性）
- Skills / Slash Commands：把高频工作变成“一键流程”
- Connectors：把云端工具接进来，用真实数据驱动产出

---

## 扩展到 TRAE 与 Codex（对照表 + 迁移方法）
这一节解决的是：“我已经会用 Cowork 的思路了，怎么迁移到 Trae 和 Codex，不用重新学一遍？”

你可以把三者理解成同一套能力在不同“载体”里的落地：
- Claude Cowork：桌面工作台取向，擅长知识工作 + 文档/文件交付
- TRAE：IDE 取向（IDE mode）+ 自治代理取向（SOLO），擅长工程落地与可视化控制
- Codex：本地 CLI/应用/IDE 扩展/网页形态的编码代理，擅长在代码仓库内完成实现、测试与验证

### 你刚提到的“几个场景”，到底怎么区分（教程内置的选择题）
把场景切开，你就不会“到底用哪个”纠结：
- 场景 1：写作/整理/研究（产物是文档/表格/清单）  
  - 典型输入：纪要、访谈、竞品资料、截图/PDF  
  - 典型输出：PRD 草稿、洞察报告、竞品对比表、会议行动清单  
  - 优先工具：Cowork（其次 TRAE/SOLO 也能做，但 Cowork更顺手）
- 场景 2：代码仓库内落地（产物是“代码改动 + 可验证”）  
  - 典型输入：仓库、Issue、报错日志、测试失败  
  - 典型输出：提交级别的改动、测试通过、修复说明  
  - 优先工具：TRAE IDE mode 或 Codex CLI/IDE extension
- 场景 3：把重复流程变成“一键”（产物是可复用 Skill/模板/命令）  
  - 典型输入：你每周都会做的工作（周报/复盘/需求评审/上线检查）  
  - 典型输出：Skill、Slash command、固定验收清单、规则文件  
  - 优先工具：三者都可以做，但建议：先在 Cowork 把流程跑顺，再迁移到 TRAE/Codex 固化为工程化能力
- 场景 4：外部工具/数据源联动（产物是“跨系统跑通”）  
  - 典型输入：Notion/Drive/Gmail/Slack/任务系统  
  - 典型输出：自动汇总、自动发布、自动同步状态  
  - 优先工具：Cowork（Connectors）或 TRAE/Codex（MCP）

### 最重要的迁移结论（只记 3 条）
- 把“对话”迁移成“项目规则文件”：Cowork 里常见 `CLAUDE.md`；Codex 里常见 `AGENTS.md`（作为记忆/规则入口）；TRAE 里对应的是项目级 Memory / Rules / Skills（不同版本的入口名称略有差异）
- 把“重复劳动”迁移成“技能/工作流”：Cowork 的 Skills → TRAE 的 Skills（支持全局与项目级）→ Codex 的 Slash Commands / Skills（存放在其配置或项目目录体系里）
- 把“多步骤链路”迁移成“可复用编排”：Cowork 的 Sub-agents → TRAE 的 agent team/自定义 agents → Codex 的多代理/审批与沙箱执行

### 选择哪一个工具（快速决策）
- 你要交付文档、整理信息、做研究报告：优先 Cowork
- 你要在 IDE 里边写边改边看诊断，并希望 AI 帮你执行工具链：优先 TRAE（IDE mode）
- 你要在代码仓库里做实现/重构/跑测试/写脚本自动化：优先 Codex（CLI/IDE extension）
- 你想“丢给 AI 自己推进到可用版本”，但你保留强审查权：TRAE SOLO / Codex app 都是更合适的载体

### 对照表（把概念映射起来）
| 目标 | Claude Cowork | TRAE | Codex |
|---|---|---|---|
| 项目上下文（长期记住） | Projects / `CLAUDE.md` | Memory（全局/项目级） | `AGENTS.md`（记忆入口） |
| 可复用流程 | Skills | Skills（支持全局与项目级） | Slash Commands / Skills |
| 外部工具接入 | Connectors / Plugins | MCP（项目级能力）、内置集成 | MCP servers |
| 安全执行 | 文件夹授权 + 删除确认 | 命令执行模式/审查（含沙箱策略） | Sandbox & approvals |
| 并行与编排 | Sub-agents | 多 agents、可自定义 agents | 多代理与审批/任务侧边栏等 |

---

## TRAE 快速上手（离线版）
目标：用最短路径把 Cowork 的“拆解→配备→组合”迁移到 TRAE 的 IDE 工作流里。

### 1) 你在用哪种模式（先选“驾驶舱”）
- IDE mode：你在写代码/改文件/看诊断时用，强调“边写边修边验证”
- SOLO mode：你把任务委托给代理，自己更多做审阅与决策（适合从 0 到 1 的交付或大改动）

### 2) TRAE 里最值得优先学的 4 个点
（以下为离线整理的“最小有用集合”，不追版本名细节）
- Skills：支持全局 Skills 和项目级 Skills，且可启用/禁用；还能在对话过程中创建/上传 Skills
- Memory：支持全局与项目级记忆（可开关、可手工增删），用于稳定口径与减少重复解释
- MCP（项目级能力）：可在项目内启用 MCP 能力，让 agent 能接外部资源/工具
- 命令执行安全策略：可配置沙箱/白名单/手动执行等方式，避免“一句话把电脑搞崩”

### 3) 你今天在 TRAE 里要完成的“首个闭环”
目标：在一个项目里完成一次“从需求到改动到验证”的闭环，产出至少一个可复用 Skill。

推荐任务指令（把方括号替换为你的真实项目）：
> 打开项目 [你的仓库]。请先列出要做的改动计划（按文件分组），我确认后再修改。修改完成后运行项目现有的检查/测试命令并汇总结果。最后输出一份 `CHANGELOG.md`（改了什么/为什么/如何验证）。

验收标准：
- 你看到明确的计划（按文件/步骤/风险点）
- 你能审阅每一次改动（不要一次性吞掉所有 diff）
- 有验证动作（至少 lint 或 tests 或能启动并预览）

### 4) 把 Cowork 的方法论迁移成 TRAE 的“默认姿势”
- Decompose：先让 agent 出 plan，再开始改；计划必须可审阅（按文件/模块）
- Equip：把“你的风格与边界”沉淀成项目级 Memory / Skills（例如 PRD 模板、代码风格、禁止项）
- Compose：让 agent 负责执行与产出，人负责拍板与验收；每次都留出“我确认再继续”的闸门

---

## Codex 快速上手（离线版）
目标：让 Codex 成为你的“代码仓库内的执行引擎”，把实现/重构/测试/验证做成可重复的流程。

### 0) 如果你不想配 OpenAI：这一节可以先跳过
Codex（OpenAI）最顺的两条路径是：
- ChatGPT 登录（用你的 ChatGPT 订阅）
- OpenAI API Key

如果你明确不使用 OpenAI，那么建议你用“TRAE + DeepSeek”完成同样的“定位→修改→测试→汇总”闭环，见下一节。

### 1) 安装与启动（离线摘录）
你可以用 npm 或 Homebrew：

```bash
npm install -g @openai/codex
```

或：

```bash
brew install --cask codex
```

启动：

```bash
codex
```

### 2) 登录与计费（两条路线）
- 用 ChatGPT 账号登录：在 Codex CLI 中选择 Sign in with ChatGPT（适用于 Plus/Pro/Team/Edu/Enterprise 计划）
- 用 OpenAI API Key：需要额外配置（适合企业用量、自动化、CI 场景）

### 3) 配置、记忆与工具接入（你最该关心的）
- 配置文件：`~/.codex/config.toml`
- 记忆文件：`AGENTS.md`（让 Codex 在项目里稳定遵循规则与口径）
- MCP：Codex 可访问 MCP servers，用于接外部工具与数据源
- 非交互执行：`codex exec` 适合脚本化/流水线场景（例如在 CI 里跑）

### 4) 你今天在 Codex 里要完成的“首个闭环”
目标：选一个小问题（修 bug/补测试/小重构），让 Codex 完成“定位→修改→测试→汇总”。

推荐提示（贴到 Codex 里即可）：
> 在当前仓库中定位 [问题描述]。先给出最小修复方案与影响范围。得到确认后再修改。修改后运行项目现有测试命令，并输出：改动摘要、测试结果、回滚方案。

验收标准：
- 在修改前给出最小可行修复与风险点
- 修改后有测试或至少可复现/可验证的步骤
- 输出包含“我该怎么确认它真的修好了”

---

## 不配 OpenAI：DeepSeek 路线（也能完整练通）
你现在的状态非常典型：想把工作流练熟，但不想被某一个厂商的 Key 卡住。DeepSeek 的官方文档明确提到它提供兼容 OpenAI/Anthropic 格式的 API，因此很多支持“OpenAI-compatible”的工具都能接入（不需要你改代码，只需要改配置）。

来源：https://api-docs.deepseek.com/（离线摘要）

### 1) 最重要的 3 个配置要点（不碰 OpenAI 也能用）
- OpenAI 兼容 base_url：`https://api.deepseek.com`  
- Anthropic 兼容 base_url：`https://api.deepseek.com/anthropic`  
- 模型名建议优先用：`deepseek-v4-flash` / `deepseek-v4-pro`  
  - `deepseek-chat`、`deepseek-reasoner` 官方标注将在 2026/07/24 之后弃用

### 2) 你在“流程上”到底能不能走通
能走通，原因是：我们练的是“工作流”，不是“某个按钮”。
- 你要练的核心闭环：拆解（plan）→ 执行（改/写/跑）→ 验证（检查/测试）→ 固化（Skill/模板）
- 这个闭环对模型的硬要求只有：能理解上下文 + 能遵循结构化输出 + 能在工具侧执行与验证

所以你可以：
- Cowork 负责：研究/写作/整理/产出文档
- TRAE 负责：在仓库里落地、跑命令、看诊断、做可验证的改动
- DeepSeek 负责：作为 TRAE/其他工具的后端模型（前提是该工具支持 DeepSeek 或 OpenAI-compatible 方式）

### 3) 最小练习（用 DeepSeek 路线完成“代码闭环”）
不管你用的是哪个具体工具（IDE/CLI/代理框架），你都可以按这张任务卡走：
- 输入：一个小问题（报错日志/失败测试/小需求）
- 指令骨架：
  - “先解释问题原因，列出 2 个最小修复方案与风险点”
  - “等我确认后再改代码（按文件分组，逐块提交改动）”
  - “改完跑测试/检查命令，汇总结果（通过/失败/下一步）”
  - “写一份 `CHANGELOG.md`：改了什么、为什么、如何验证、回滚方案”

### 4) 安全与密钥（你需要知道的边界）
- 不要把 `DEEPSEEK_API_KEY` 写进仓库文件或提交到 git
- 优先使用环境变量或工具的密钥管理界面
- 任何会“读写文件/跑命令”的代理模式，都建议默认开启审查/确认闸门（先出计划→你确认→再执行）

---

## 一日学习路径（按产出驱动）
来源：[README.md:L37-L64](file:///Users/li/ai%20pm%20learning/claude-cowork-pm-guide/README.md#L37-L64)（离线改写版）

### 上午：建立认知体系（你要能讲清楚“它能干什么/不能干什么”）
- 读一遍 8 要素（写下你的工厂类比）
- 完成一次“读→写”的最小任务（见上文 60 分钟快速上手）

### 下午：搭建生态（你要能让它拿到真实材料）
- 选一个你常用的数据源：Drive/Notion/Sheets/Gmail/Slack 任一
- 目标不是“连接越多越好”，而是“能稳定取到你今天要用的数据”

### 晚上：跑通业务链路（你要能交付一个真实产物）
- 从工作里选最短闭环：会议纪要 → 需求列表 → PRD 骨架 / 用户反馈 → 聚类 → 洞察
- 用“拆解→配备→组合”跑通一遍
- 把最稳的一段固化成 Skill（最小可用）

---

## 工作流落地：拆解-配备-组合
来源：[README.md:L67-L79](file:///Users/li/ai%20pm%20learning/claude-cowork-pm-guide/README.md#L67-L79)

你可以把 PM 工作当成“三段式生产线”：

### 1) Decompose（拆解链路）
目标：把黑盒任务切成“可观察、可验收”的小步。
- 每步都要写清：输入、输出、验收标准
- 每步都要能回答：如果输出很差，你能在哪里纠偏？

### 2) Equip（配置能力）
目标：给每一步配一张“作业卡”，至少是固定模板或提示词。
- 能复用的内容优先沉淀成 Skill
- 需要多视角审阅的步骤，优先用子角色（例如：工程视角/风控视角/老板视角）

### 3) Compose（重组工作流）
目标：把步骤串起来，明确人类拍板点。
- AI 适合：信息收集、归纳、生成草稿、格式化、批处理
- 人类必须拍板：取舍、优先级、风险边界、最终口径

---

## Connectors 离线指南（把数据接进来）
来源：https://www.coworkease.com/blog/claude-cowork-connectors-guide（已做离线摘要）

### Connectors 能解决什么
当你发现“我需要它读 Notion/Drive/邮件/任务系统”时，就进入 Connector 领域：把数据接进来，让产出从“写得像”变成“基于事实”。

### 常见支持的数据源（文中列举）
- 设计：Canva、Figma
- 效率与知识：Notion、Google Drive、Google Sheets
- 沟通：Gmail、Slack
- 商务与管理：Stripe、Asana、Linear

### 典型接入流程（离线版）
1) 在目录页连接账号（通常是 OAuth 授权）  
2) 在任务中直接提及目标服务与目标动作（例如“从 Sheets 读取数据，生成总结并发到 Slack”）  
3) 先用测试数据跑通，再扩大范围

### 最佳实践（能明显提升成功率）
- 最小化接入：只连你今天要用的 1 个服务
- 权限复核：授权前看清范围；不需要就撤销
- 先试跑再上生产：先用非敏感数据验证流程
- 大数据别硬怼：大表/大库先抽样或先导出本地再处理

### 风险提醒（离线版）
- 不同 Connector 能力差异大，先明确“能读/能写/能否双向”
- 金融/支付类数据优先当只读，关键动作必须人工复核

---

## 课程与案例库：离线摘要版
这一节的目标是：你不需要现在去刷长课，但你知道“每个资源能帮你补哪块短板”。

### 1) Claude 101（Skilljar）课程结构速览
来源：https://anthropic.skilljar.com/claude-101（已做离线摘要）

它的课程目录可以理解为一条从“会聊”到“会组织与扩展”的主线：
- 初识 Claude：第一段对话、如何拿到更好结果
- 组织知识：Projects
- 创作交付：Artifacts
- 复用流程：Skills
- 扩展触达：Connecting your tools、Enterprise search、Research mode
- 角色用例：按不同岗位给用法示例

离线建议用法：
- 你不需要逐课刷完，先对照这份目录，把你最缺的 2 个点补齐：
  - 如果你“总要重复解释背景”：先补 Projects
  - 如果你“每次都从零写提示词”：先补 Skills
  - 如果你“缺少可交付物形态”：先补 Artifacts

### 2) DeepLearning.AI：Agent Skills with Anthropic（你会学到什么）
来源：https://learn.deeplearning.ai/courses/agent-skills-with-anthropic/lesson/ldn5c3/introduction（抓取到的页面以平台使用指南为主）

离线可用要点（平台层）：
- 学习形式偏 Notebook/交互式练习
- 你需要掌握：如何打开课程文件、下载 notebook、重置 workspace

如果你的目标是“1 天游程通关”，这门课更适合作为后续补强：当你要系统学习 Agent 的设计与编排时再进入。

### 3) Anthropic 研究：AI 如何改变 Anthropic 的工作方式（观点摘录）
来源：https://www.anthropic.com/research/how-ai-is-transforming-work-at-anthropic（已做离线摘要）

你可以把它当成“组织级使用 AI 的真实后果清单”：
- 正面：产出更快、个人更全栈、学习与迭代速度上升、以前被忽略的小任务更容易做完
- 风险：深度能力可能被稀释、监督 AI 输出的能力成为瓶颈、人与人协作可能变少

离线落地建议：
- 给自己加一条硬规则：关键结论必须有“证据与出处”，并留出“人类复核点”
- 每次让 AI 生成结论后，强制加一步：列出 3 个可能错的地方（自我审计）

### 4) CCforPMs：交互式课程网站（目录 + 你该怎么用）
来源：https://ccforpms.com（可抓取到完整目录结构）

它的价值在于：把“在 Claude Code 里学 Claude Code”设计成了任务流。
- Module 0：安装与启动
- Module 1：文件操作、Agents、Sub-agents、Project Memory、导航
- Module 2：PRD、数据分析、策略
- Module 4：Plan/Build/Iterate/GitHub/Go Live（更偏完整交付）

离线建议用法：
- 把它当成“题库”，你只做一条最短路径：
  - 如果你想练写文档：直奔 Module 2.1（Write a PRD）的思路（不一定要把全部课程跑完）
  - 如果你想练数据：直奔 Module 2.2（Analyze Data）

### 5) 视频资源（离线摘要：基于公开视频页面简介）
说明：公开视频抓取结果通常只有标题/简介，无法保证拿到完整字幕；这里提供“你该带着什么问题去看”。

- How Anthropic uses Claude in Product Management  
  - 来源：https://www.youtube.com/watch?v=91AJ0cpgLlQ  
  - 你带着的问题去看：不用 SQL 如何做取数与分析？输出如何落成可用结论（而不是一堆字）？

- Claude Code for Product Managers with Sachin Rekhi（Reforge）  
  - 来源：https://www.youtube.com/watch?v=zsAAaY8a63Q  
  - 你带着的问题去看：如何把“自定义 Skill”做成可复用 SOP？有哪些 PM 日常能立刻自动化？

- Claude Code + Analytics Masterclass: Automate Product Analytics（Aakash Gupta）  
  - 来源：https://www.youtube.com/watch?v=WK0bZrS8pVs  
  - 你带着的问题去看：取数→清洗→分析→结论→汇报，这条链路如何自动化？人类拍板点放在哪？

### 6) Substack 付费长文（可读到部分信息）
来源：https://aimaker.substack.com/p/claude-cowork-review-agentic-ai-guide（页面显示为 Paid）

离线可用结论（从可见部分归纳）：
- 这类文章通常聚焦“从工具到系统”的跃迁：把 Cowork/Code 当成你的个人操作系统
- 真正的门槛不是工具，而是把工作流写成可执行的系统指令与模板（例如 `CLAUDE.md`、角色分工、验收清单）

---

## 实操题库（选 1 条链路跑通）
你今天只做一题，但必须做完整闭环：有输入、有输出、有验收、有复盘。

### 题 A：会议纪要 → 需求列表 → PRD 骨架
- 输入：会议纪要（原文即可）
- 输出：`01-决策与待办.md`、`02-需求列表.md`、`03-PRD-骨架.md`
- 验收：每条需求都有 用户/场景/价值/非目标；PRD 骨架包含 风险/指标/待澄清问题

### 题 B：用户反馈 → 主题聚类 → 洞察与机会点
- 输入：20–100 条反馈
- 输出：`01-主题聚类.md`、`02-洞察与机会点.md`
- 验收：每个主题簇至少 3 条原文证据；每条机会点包含可验证指标与最小验证方式

### 题 C：竞品对比 → 定位差异 → 下一版本建议
- 输入：2–3 个竞品的功能清单/网页文案
- 输出：`01-竞品对比表.md`、`02-差异化叙事.md`、`03-版本建议.md`
- 验收：建议明确 做什么/不做什么/为什么；至少 1 条建议可被数据验证

---

## 模板区（可直接复制）
### 模板 1：8 要素一句话卡片（产物 A）
- Chat：  
- Cowork：  
- Code：  
- Projects：  
- Skills：  
- Connectors：  
- Plugins：  
- Sub-agents / Dispatch / Scheduled Tasks：  

### 模板 2：拆解-配备-组合卡（产物 B）
- 链路名称：  
- 目标（1 句话）：  
- 输入（文件/链接/数据）：  
- Decompose（步骤 1–9，每步写输入/输出/验收）：  
- Equip（每步用的 Skill/提示词/角色）：  
- Compose（串联顺序 + 人类拍板点）：  
- 最终交付物（文件列表）：  
- 验收清单（5–10 条）：  

### 模板 3：最小 Skill 规格（产物 C）
- Skill 名称：  
- 使用场景：  
- 输入：  
- 输出：  
- 约束（口径/风格/禁止项）：  
- 失败条件（出现哪些情况必须停下来问我）：  
- 示例输入（1 个）：  
- 示例输出片段（1 段）：  

---

## 自查清单（今天结束前）
- 我能解释：为什么某任务要用 Cowork 而不是 Chat（至少 2 条理由）
- 我已跑通一次“读→写”闭环，并在本地拿到产出文件
- 我有一条端到端链路，且每步都有可验收输出
- 我至少沉淀了 1 个可复用模板/Skill（哪怕很简陋）
- 我标出了 3 个“必须人工拍板”的点（取舍/优先级/风险/口径）

---

## 信息来源（链接）
- Claude Cowork 指南仓库：README.md（本仓库）  
- Cowork 官方入门： https://support.claude.com/en/articles/13345190-get-started-with-claude-cowork  
- Cowork 概念解释（20 concepts）： https://aidiscoveries.io/20-claude-cowork-concepts-explained-beginner-to-advanced-2025-complete-guide/  
- Connectors 指南（第三方整理）： https://www.coworkease.com/blog/claude-cowork-connectors-guide  
- TRAE IDE 更新日志： https://www.trae.ai/changelog  
- Trae Agent（CLI）仓库： https://github.com/ByteDance/trae-agent  
- Codex CLI（README）： https://raw.githubusercontent.com/openai/codex/main/README.md  
- Codex 变更日志： https://developers.openai.com/codex/changelog  
