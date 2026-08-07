# AI 产品经理转型学习系统

更新时间：2026-08-06  
根目录：`/Users/li/ai pm learning/claude-cowork-pm-guide/AI产品转型学习系统`

---

## 这是什么
这是一个围绕“医疗/药企背景 PM 转型为 AI 产品经理”的学习与项目实践目录。

它的目标不是只存放资料，而是把下面 4 类内容分开管理：

1. 学习原始材料  
2. 学习计划  
3. 学习成果  
4. 接力说明 / 当前进度

这样后续无论是人还是新的 agent 接手，都能快速知道：
- 资料从哪里来
- 当前计划是什么
- 今天学到哪里了
- 下一步应该做什么

---

## 目录结构
### `01-学习原始材料`
记录学习资料来源，包括：
- 仓库内已有离线资料
- 飞书/网页/课程等外部来源
- 每份资料的用途

### `02-学习计划`
记录学习计划本身，包括：
- 当前统一版学习计划
- 计划生成思路
- 变更记录与更新理由

### `03-学习成果`
记录每天真实学出来的内容，包括：
- 每日学习卡
- 荣誉墙
- 项目方向说明
- 后续作品集沉淀

### `04-接力说明`
给后续 agent 或协作者看的当前状态说明。

---

## 当前学习主线
当前已经从“泛泛学习 AI 工具”收束到一个更聚焦的方向：

## 主项目方向
`AI Compliance Check Assistant`

### 当前定位
- 面向药企 / 医疗场景的 AI 辅助合规审核系统
- 用自然语言规则 + 示例帮助企业配置审核能力
- 核心不是内容生成，而是风险识别、阻拦与标记

### 当前学习方式
- 采用“小卡片模式”
- 每天只推进 1 个核心概念
- 每天结束后形成：
  - 一张学习卡
  - 一份荣誉墙文案
- 2026-08-05 起补充固定 4 步：
  - 开场定焦
  - 主卡推进
  - 费曼复述
  - 隔天回忆
- 详细说明见 [02-学习互动方式-v2.md](./02-学习计划/02-学习互动方式-v2.md)

---

## 当前进度（2026-08-06 更新）
当前已经完成：
- 学习体系目录结构设计
- 统一学习总纲与离线手册整理
- Day01：定义 AI compliance check 的基本产品边界与规则雏形
- Day02：规则模板 v1 定稿（含2条完整规则示例），详见 [规则模板-v1.md](./03-学习成果/规则模板-v1.md)
- Day03 进行中：导入并评审了一份 CRM Compliance Eval 框架（10类风险 + 50条case），决定文档保留全貌、demo 只做 01/05/07/10 四类子集，详见 [CRM-Compliance-Eval框架说明.md](./03-学习成果/CRM-Compliance-Eval框架说明.md)
- Day03：补充沉淀了一份方法论复盘输出，见 [Day03-AI-Compliance-Eval-设计学习报告.md](./03-学习成果/Day03-AI-Compliance-Eval-设计学习报告.md)
- Day03：补充了一份更适合浏览与展示的可视化 HTML 版本，见 [Day03-AI-Compliance-Eval-设计学习报告-可视化版.html](./03-学习成果/Day03-AI-Compliance-Eval-设计学习报告-可视化版.html)
- Day04：完成对 eval 方案的产品化复盘，确认高危/中低危指标差异、MVP 阶段 case 收敛策略，并沉淀 HTML 版评估方案，见 [crm-compliance-checker-eval-v1.html](./03-学习成果/crm-compliance-checker-eval-v1.html)
- Day05：设计并写出了最小可运行 demo（正则+LLM混合架构），代码已在沙盒实测regex部分，见 [demo/README.md](./03-学习成果/demo/README.md)
- Day05：补充完成产品侧成果，明确双端结构、核心审核字段、最小规则配置字段，并归档双端 mock，见 [Day05-双端Mock与规则配置复盘.md](./03-学习成果/Day05-双端Mock与规则配置复盘.md) 与 [Day05-AI-Compliance-双端Mockup.html](./03-学习成果/Day05-AI-Compliance-双端Mockup.html)
- 学习方法：从单纯“小卡片模式”升级为“定焦-主卡-费曼复述-隔天回忆”，并落成 [02-学习互动方式-v2.md](./02-学习计划/02-学习互动方式-v2.md)
- Day06：已完成 DeepSeek 接入、MVP 子集评测、CSV50 完整 benchmark 跑分，并把系统正式拆成“固定 system prompt / 用户规则配置 / 内部实现”三层，见 [Day06-学习卡.md](./03-学习成果/Day06-学习卡.md)、[Day06-CSV50-跑分报告.html](./03-学习成果/Day06-CSV50-跑分报告.html)、[Day06-System-Prompt-固定模板.md](./03-学习成果/Day06-System-Prompt-固定模板.md)、[Day06-用户规则配置模板-v2.2.json](./03-学习成果/Day06-用户规则配置模板-v2.2.json)、[Day06-内部实现说明-v1.md](./03-学习成果/Day06-内部实现说明-v1.md)
- Day06：补充沉淀了当天的讨论转变与好问题总结，见 [Day06-讨论转变与好问题总结.md](./03-学习成果/Day06-讨论转变与好问题总结.md)
- Day07：已统一当前规则口径，当前主配置以 `01 / 03 / 05 / 06 / 07 / 10` 这 6 类为准，并同步到 [Day07-学习卡.md](./03-学习成果/Day07-学习卡.md)、[demo/README.md](./03-学习成果/demo/README.md) 与 [Day06-CSV50-跑分报告.html](./03-学习成果/Day06-CSV50-跑分报告.html)
- Day07：已完成一轮 Day06 vs Day07 的 before / after，对同一模型、同一 CSV50 benchmark 做规则层小更新后复跑；结果从 `47/50, 高危Recall 45%` 提升到 `49/50, 高危Recall 50%`，对比见 [Day07-Day06-before-after-对比记录.md](./03-学习成果/Day07-Day06-before-after-对比记录.md)
- Day07：已新增 [Day07-CSV50-结果拆解.md](./03-学习成果/Day07-CSV50-结果拆解.md)，明确区分 `CSV50 raw benchmark` 与 `结果拆解`；并进一步确认 Day06 的低分主要来自未实现类别，而不是 raw dataset 本身
- Day07：已跑通 `300 case` 新 benchmark，并把结果、规则配置、数据集设计思路、上线门槛、问题案例集一并写进新版 [Day06-CSV50-跑分报告.html](./03-学习成果/Day06-CSV50-跑分报告.html)；当前结果为：成功 `273/300`、高风险召回率 `87%`、中风险判断准确率 `96%`、低风险误伤率 `5%`
- Day07：已新增当天沉淀文件 [Day07-学习与跑分日志.md](./03-学习成果/Day07-学习与跑分日志.md) 与 [Day07-荣誉墙.md](./03-学习成果/Day07-荣誉墙.md)，记录今天的学习心得、阶段性结论、以及“Day07 还没做完但方向已经对了”的收尾状态
- Day07：从 300 case 问题样本里逐条核对根因，定位到两个范围内真实bug（`MB143` 05类误伤、`MB197` 06/01边界模糊）并修复；排查 MB143 时发现根因是 05 类的 regex 有疏漏，进一步推动了一次架构调整——去掉 05 类的 regex 前置层，全部 6 类统一改为纯 LLM 判断，原因是这层 regex 违反了"业务人员只写自然语言规则"的产品定位，详见 [Day07-架构调整-去掉regex改纯LLM.md](./03-学习成果/Day07-架构调整-去掉regex改纯LLM.md)。改动已完成，待用自己的 API key 重新验证效果

- Day07：MB143/MB197 单条验证通过，`run_eval.py` 完整重跑 MVP 子集 **30/30 全部通过，0失败0报错**（含曾经的已知局限`05-gap-1`），高危Recall 100%、误报率0%；同时给 `checker.py` 加了失败重试一次的逻辑、`LLM_MAX_TOKENS`从300调到600，缓解截断类报错
- Day07收尾：产品文件结构重组——新增 [05-产品原型/](./05-产品原型/) 文件夹，规则配置/system prompt/内部实现说明从day编号的历史文件迁移到统一位置（旧文件保留，标注归档，不丢失历史），并做了"规则配置"模块的本地可视化编辑器（起本地服务，浏览器改规则，不用手改JSON）。产品改动历史统一记在 [05-产品原型/CHANGELOG.md](./05-产品原型/CHANGELOG.md)，接力交接机制也同步做了轻量化改造，见 [04-接力说明/00-当前进度与接力说明.md](./04-接力说明/00-当前进度与接力说明.md)
- **合规工作台四个模块全部完成**（[05-产品原型/](./05-产品原型/)）：`python3 server.py` 起本地服务，浏览器里一条完整闭环——① 规则配置（可视化改规则）→ ② 规则执行（选数据集一键跑评测）→ ③ 命中结果（历史跑分列表+逐条筛选）→ ④ 分析报告（失败根因分三桶、范围内真实准确率、自动跟上次对比、可导出HTML）。评测数据集也纳入产品管理（[05-产品原型/数据集/](./05-产品原型/数据集/)，丢CSV进去自动出现在下拉框），CSV50 和 200case 已迁入。过程中修了3个真实bug：200case的分类ID录入错误、同秒跑分结果互相覆盖、跑分对比在同秒完成时找不到上一次。详见 [05-产品原型/CHANGELOG.md](./05-产品原型/CHANGELOG.md)

当前下一步：
- **用真实 API key 跑一次大样本**（200case / CSV50）——这是现在最该做的一件事。四个模块的链路已用 mock LLM 完整验证过，但真实调用下的耗时、稳定性、以及 Day07 那轮改动（去regex+两个规则修复+重试逻辑）在大样本上的真实效果，都还没测过（目前只验证了 MVP 子集 30 条）
- 那份 300 case 数据集还在 `~/Downloads` 里没进仓库，拷进 `05-产品原型/数据集/` 就能直接用（命令见 [数据集/README.md](./05-产品原型/数据集/README.md)）
- 拿到大样本真实结果后，在「04/09新类别 vs 输出稳定性治理」之间决定下一个优化方向
- 之后按压缩排期推进：竞品/行业调研 → 面试 README + 讲稿

### 关键背景（影响后续排期）
用户是 Veeva 产品经理，转型 AI 产品经理，求职/面试时间线是几周内，作品集需要包含能跑的demo。详见 [04-接力说明/00-当前进度与接力说明.md](file:///Users/li/ai%20pm%20learning/claude-cowork-pm-guide/AI产品转型学习系统/04-接力说明/00-当前进度与接力说明.md) 第0节和 [02-学习计划/00-统一学习计划.md](file:///Users/li/ai%20pm%20learning/claude-cowork-pm-guide/AI产品转型学习系统/02-学习计划/00-统一学习计划.md)。

---

## 重要关联文件
如果是新的 agent 接手，建议优先阅读：

- [04-接力说明/00-当前进度与接力说明.md](file:///Users/li/ai%20pm%20learning/claude-cowork-pm-guide/AI产品转型学习系统/04-接力说明/00-当前进度与接力说明.md)
- [02-学习计划/00-统一学习计划.md](file:///Users/li/ai%20pm%20learning/claude-cowork-pm-guide/AI产品转型学习系统/02-学习计划/00-统一学习计划.md)
- [02-学习计划/02-学习互动方式-v2.md](file:///Users/li/ai%20pm%20learning/claude-cowork-pm-guide/AI产品转型学习系统/02-学习计划/02-学习互动方式-v2.md)
- [03-学习成果/Day01-学习卡.md](file:///Users/li/ai%20pm%20learning/claude-cowork-pm-guide/AI产品转型学习系统/03-学习成果/Day01-学习卡.md)
- [03-学习成果/Day04-学习卡.md](file:///Users/li/ai%20pm%20learning/claude-cowork-pm-guide/AI产品转型学习系统/03-学习成果/Day04-学习卡.md)
- [03-学习成果/Day05-学习卡.md](file:///Users/li/ai%20pm%20learning/claude-cowork-pm-guide/AI产品转型学习系统/03-学习成果/Day05-学习卡.md)
- [03-学习成果/Day06-学习卡.md](file:///Users/li/ai%20pm%20learning/claude-cowork-pm-guide/AI产品转型学习系统/03-学习成果/Day06-学习卡.md)
- [03-学习成果/Day07-学习卡.md](file:///Users/li/ai%20pm%20learning/claude-cowork-pm-guide/AI产品转型学习系统/03-学习成果/Day07-学习卡.md)
- [03-学习成果/Day07-荣誉墙.md](file:///Users/li/ai%20pm%20learning/claude-cowork-pm-guide/AI产品转型学习系统/03-学习成果/Day07-荣誉墙.md)
- [03-学习成果/Day07-学习与跑分日志.md](file:///Users/li/ai%20pm%20learning/claude-cowork-pm-guide/AI产品转型学习系统/03-学习成果/Day07-学习与跑分日志.md)
- [03-学习成果/Day07-Day06-before-after-对比记录.md](file:///Users/li/ai%20pm%20learning/claude-cowork-pm-guide/AI产品转型学习系统/03-学习成果/Day07-Day06-before-after-对比记录.md)
- [03-学习成果/Day07-CSV50-结果拆解.md](file:///Users/li/ai%20pm%20learning/claude-cowork-pm-guide/AI产品转型学习系统/03-学习成果/Day07-CSV50-结果拆解.md)
- [03-学习成果/Day06-讨论转变与好问题总结.md](file:///Users/li/ai%20pm%20learning/claude-cowork-pm-guide/AI产品转型学习系统/03-学习成果/Day06-讨论转变与好问题总结.md)
- [03-学习成果/Day06-System-Prompt-固定模板.md](file:///Users/li/ai%20pm%20learning/claude-cowork-pm-guide/AI产品转型学习系统/03-学习成果/Day06-System-Prompt-固定模板.md)
- [03-学习成果/Day06-用户规则配置模板-v2.2.json](file:///Users/li/ai%20pm%20learning/claude-cowork-pm-guide/AI产品转型学习系统/03-学习成果/Day06-用户规则配置模板-v2.2.json)
- [03-学习成果/Day06-内部实现说明-v1.md](file:///Users/li/ai%20pm%20learning/claude-cowork-pm-guide/AI产品转型学习系统/03-学习成果/Day06-内部实现说明-v1.md)
- [03-学习成果/Day05-双端Mock与规则配置复盘.md](file:///Users/li/ai%20pm%20learning/claude-cowork-pm-guide/AI产品转型学习系统/03-学习成果/Day05-双端Mock与规则配置复盘.md)
- [03-学习成果/Day05-AI-Compliance-双端Mockup.html](file:///Users/li/ai%20pm%20learning/claude-cowork-pm-guide/AI产品转型学习系统/03-学习成果/Day05-AI-Compliance-双端Mockup.html)
- [03-学习成果/crm-compliance-checker-eval-v1.html](file:///Users/li/ai%20pm%20learning/claude-cowork-pm-guide/AI产品转型学习系统/03-学习成果/crm-compliance-checker-eval-v1.html)

同时可参考仓库根目录中的历史文件：
- [overall-learning-plan-zh.md](file:///Users/li/ai%20pm%20learning/claude-cowork-pm-guide/overall-learning-plan-zh.md)
- [offline-handbook-zh.md](file:///Users/li/ai%20pm%20learning/claude-cowork-pm-guide/offline-handbook-zh.md)
- [feishu-anthropic-notes-offline.md](file:///Users/li/ai%20pm%20learning/claude-cowork-pm-guide/feishu-anthropic-notes-offline.md)
- [学习材料包_给Trae用.md](file:///Users/li/ai%20pm%20learning/claude-cowork-pm-guide/学习材料包_给Trae用.md)
- [AGENT_HANDOFF_zh.md](file:///Users/li/ai%20pm%20learning/claude-cowork-pm-guide/AGENT_HANDOFF_zh.md)

---

## 使用约定
- 不要一次给用户太多信息
- 每次优先推进 1 个概念、1 个小产出
- 新知识点可先进入题库池，后续再拆成小测
- 任何学习进度都尽量落成 Markdown，而不是只停留在对话里
