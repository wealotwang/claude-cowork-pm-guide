# Anthropic 工程博客阅读笔记（飞书文档离线学习版）

来源（飞书）：https://my.feishu.cn/wiki/MfUqwbEx9iUDuHkeszEckudhnch  
整理时间：2026-06-13  

## 目录
- [怎么读这份笔记](#怎么读这份笔记)
- [核心心智模型：Agent vs Workflow](#核心心智模型agent-vs-workflow)
- [工作流模式速查（从简单到复杂）](#工作流模式速查从简单到复杂)
- [Multi-agent：什么时候需要、系统长什么样](#multi-agent什么时候需要系统长什么样)
- [上下文工程（Context Engineering）速查](#上下文工程context-engineering速查)
- [Skill.md：三层披露与按需加载](#skillmd三层披露与按需加载)
- [工具工程（Tools）与评测（Evals）](#工具工程tools与评测evals)
- [MCP 的代码执行：让代理更省 token](#mcp-的代码执行让代理更省-token)
- [Claude 平台的 Context Management（编辑 + Memory）](#claude-平台的-context-management编辑--memory)
- [练习：一天内跑通一个“研究型代理”闭环](#练习一天内跑通一个研究型代理闭环)
- [自测题](#自测题)
- [信息来源（链接）](#信息来源链接)

---

## 怎么读这份笔记
这份离线版的目标不是“背概念”，而是帮你建立一个可复用的判断与落地框架：
- 先学会区分：什么任务用 Workflow，什么任务才需要 Agent
- 再学会治理：多轮、多工具、多代理时如何管上下文与成本
- 最后学会固化：把流程写成可运行的 Skill / Rules / Evals

---

## 核心心智模型：Agent vs Workflow
来自 Anthropic 的划分是最实用的一刀：
- Workflow：LLM 和工具按预定义的代码路径被编排（更像流水线）
- Agent：LLM 动态决定下一步做什么、用什么工具、走多久（更像“自己会改路线的司机”）

关键取舍：
- Workflow 通常更便宜、更快、更可控，适合结果要稳定一致的任务
- Agent 通常更灵活，但代价是延迟更高、成本更高、调试更难

一个好用的判断法：
- 你能否把任务拆成有限的、可预先写死的步骤？
  - 能：优先 Workflow
  - 不能（步骤数不确定、需要探索、需要随结果改变策略）：再考虑 Agent

---

## 工作流模式速查（从简单到复杂）
把“能不能预先写死步骤”进一步细分，你会得到一套常用模式库：

### 串行（Serial）
- 特征：前一个输出是后一个输入
- 适合：写 PRD 章节、从资料生成摘要再生成结论
- 风险：前一步错会传染到后一步

### 路由（Router）
- 特征：先分类，再走不同路径（专家分流）
- 适合：客服分流（账单/售后/技术）、文档类型分流（PRD/纪要/周报）

### 并行（Parallel）
- 特征：多个独立视角并行处理，最后汇总
- 适合：多视角评审（工程/风控/老板）、海量评论情感分析

### 编排者-执行者（Orchestrator/Worker）
- 特征：一个“总控”动态拆子任务，多个 worker 执行
- 适合：无法预先知道子任务数量的探索类任务

### 评估者-优化者（Generator/Evaluator/Optimizer）
- 特征：生成→评估→反馈→再生成（循环）
- 适合：有明确评估标准的任务（格式、覆盖率、准确率、风格一致性）

### Agent（开放式）
- 特征：步骤不确定，需要自主规划、纠错与工具使用
- 适合：研究型任务、开放式排障、跨系统复杂落地

---

## Multi-agent：什么时候需要、系统长什么样
飞书笔记强调的经验点可以浓缩成一句话：
多 Agent 不是为了“更高级”，而是为了“把探索并行化、把上下文隔离掉”。

### 什么时候值得用
- 研究类任务：路径依赖强、不断发现新线索、无法写死步骤
- 需要同时覆盖多个子主题/来源：并行查证能显著提速

### 常见系统结构（研究型多代理）
一个典型角色分工：
- Lead/Planner：制定研究计划，拆分子问题
- Subagents：并行搜索、阅读、提取要点
- Memory：保存中间成果与关键上下文
- Citation/Verifier：对引用与证据做插入与校验

### 多代理的“真实坑位”（飞书笔记 + Anthropic 经验合并）
- 错误会积累：需要设计错误检查点与从错误处重试的机制
- 每次路径不同：难复现、难调试，需要更强的追踪与日志（监控行为与决策，而不一定监控全部对话内容）
- 上线更新复杂：系统在跑，更新不能“一把梭”，需要灰度/彩虹发布
- 协同瓶颈：同步机制容易让整体被单点卡住；异步机制又带来结果协调与一致性难题

---

## 上下文工程（Context Engineering）速查
一句话定义：
上下文工程是在每一步把“最该带进上下文窗口的 token”选出来，既让模型做对事，又别把窗口撑爆。

飞书笔记给的类比很稳：
- LLM 像操作系统/CPU
- Context window 像内存（RAM）

### 上下文是什么（常见类型）
- Instructions：系统提示词、规则、few-shot 示例
- Knowledge：事实、领域资料、项目背景
- Tools：工具定义、工具使用结果（tool results）

### 长上下文的失败模式（可当排障清单）
- 分散：过度依赖上下文（像人过度依赖“经验”），重复旧结论，难创新
- 幻觉：胡言乱语
- 混淆：不相关内容影响生成（例如其实用不到工具但工具列表让模型乱调用）
- 冲突：前后逻辑不一致（多轮中间错误结论被带入后续）

### 四种通用策略：写入 / 选择 / 压缩 / 隔离
- 写入（Write）：把关键进度与状态写到“外部记忆/记事本”（scratchpad/memory）
- 选择（Select）：用 RAG/检索只塞相关资料；只加载相关工具
- 压缩（Compress）：修剪与摘要（接近上限时自动 compact），保留架构决策、未解决缺陷、实现细节，丢掉冗余工具输出
- 隔离（Isolate）：多代理拆分、沙箱隔离、给上下文标记状态

---

## Skill.md：三层披露与按需加载
飞书笔记提到的 “skill.md 三层披露机制” 可以理解为：
把“我可能要告诉模型的一切”拆成三层，按需加载，降低 token 压力。

一个常见三层结构：
- Level 1：Metadata（YAML）——始终加载（很短，约百 token 级）
- Level 2：Body（Markdown）——触发技能时加载（控制在几千 token 级）
- Level 3：External files（脚本/数据/说明）——需要时再加载（理论上可很大）

运行方式（离线理解版）：
- Metadata 会跟 system prompt + 用户问题一起进入上下文窗口
- 真需要工具调用时，代理再去读取 skill.md 的后两层或外部文件

---

## 工具工程（Tools）与评测（Evals）
一条核心原则：
代理的上限取决于工具的质量；工具的质量取决于可评测性。

你可以把“工具”当成确定性系统的接口：
- 选择工具时要克制：最小可行工具集
- 工具边界要清晰：命名、参数、返回值都要围绕“用途明确”
- 工具返回要可用：给模型足够上下文，但要 token 友好

提升工具效果的常见抓手：
- 先做 eval：把“好工具”的定义写成评测集
- 再用代理优化工具：让模型针对 eval 迭代工具描述、参数设计与输出格式

---

## MCP 的代码执行：让代理更省 token
飞书笔记给出的直观总结：
- MCP 的优势：减少上下文 token 消耗、管理大量工具
- 代码执行的优势：少来回交互、减少冗余工具定义、把中间过程放到沙箱编排，最后只回传结果；还能保护隐私

离线版的关键理解：
- 当工具变多时，把“调用工具”变成“写代码去调用工具”更 scalable
- 你可以让代理只把关键产出写回上下文，而不是把每个中间结果都塞回对话

---

## Claude 平台的 Context Management（编辑 + Memory）
核心是两件事：
- Context editing：接近 token 上限时清理旧的工具调用与结果，保留对话流
- Memory tool：把关键信息写到上下文窗口之外的持久存储（文件系统），跨会话复用

你可以把它当成：
- Context editing = 自动清理“内存碎片/旧日志”
- Memory = 把关键决策与结论写进“磁盘/项目笔记”

---

## 练习：一天内跑通一个“研究型代理”闭环
目标：用你熟悉的工具（Cowork / TRAE / 任何 agent 框架）做出一个可复用闭环。

### 练习题：从 0 到 1 做一个“研究报告生成器”
- 输入：一个研究问题（例如“某个产品/技术的现状、关键趋势、风险与机会”）
- 输出：
  - `01-plan.md`（研究计划：子问题清单 + 信息源策略）
  - `02-findings.md`（分主题要点 + 引用链接）
  - `03-report.md`（最终报告：结论、建议、风险、待验证清单）
  - `04-memory.md`（写入的长期记忆：术语表、关键假设、关键结论）

### 验收标准（用来避免“看起来很努力但没产出”）
- 每条关键结论都能对应到至少一个来源链接
- 至少包含 5 条“待验证问题”（你下一步去找人/找数据验证）
- 报告最后包含“工具与上下文策略复盘”：你用了哪些 Write/Select/Compress/Isolate

### 固化（把练习变成资产）
- 把 `01-plan.md` 固化成模板（计划结构不变，内容替换）
- 把“引用格式/证据结构”固化成规则文件（例如 `AGENTS.md` 或 `CLAUDE.md`）

---

## 自测题
- 什么任务你会优先用 Workflow 而不是 Agent？给出 2 个真实例子。
- 并行（Parallel）和 Orchestrator/Worker 的差别是什么？各自最常见的失败方式是什么？
- 你认为“上下文失败”里最容易在你工作中发生的是哪一种？你会用 Write/Select/Compress/Isolate 里的哪两招先解决？
- 你会如何设计一个工具的 eval，保证“迭代是可测量的”？

---

## 信息来源（链接）
- 飞书原文： https://my.feishu.cn/wiki/MfUqwbEx9iUDuHkeszEckudhnch
- Building effective agents： https://www.anthropic.com/engineering/building-effective-agents
- How we built our multi-agent research system： https://www.anthropic.com/engineering/multi-agent-research-system
- Writing effective tools for agents — with agents： https://www.anthropic.com/engineering/writing-tools-for-agents
- Code execution with MCP： https://www.anthropic.com/engineering/code-execution-with-mcp
- Effective context engineering for AI agents： https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
- LangChain Context Engineering： https://blog.langchain.com/context-engineering-for-agents/
- How to Fix Your Context： https://www.dbreunig.com/2025/06/26/how-to-fix-your-context.html
- Managing context on the Claude Developer Platform： https://claude.com/blog/context-management

