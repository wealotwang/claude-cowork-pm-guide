# Claude Cowork 自学路线 (完整深度抓取版)

> 本文档由 Python 爬虫 (BeautifulSoup4 + Markdownify) 自动生成，完整保留了网页的所有文本、层级结构和超链接。

China CRM · PM Team

[核心要素](#concepts)
[学习路径](#roadmap)
[Design Week](#designweek)
[学习建议](#tips)

Self-Study Program · PM Team

# Claude Cowork 面向 PM 的 AI-Native 工作流自学路线

从 4/21 建立认知，到 5/21 PM Design Week 实战 AI-Native PM 工作流。
3 个阶段，约 9 小时投入，结合 Veeva 日常工作场景，完成一次团队级的能力升级。

3 个阶段
约 9 小时
无需编程背景
全部免费资源

Program Dates

4/21 — 5/20

终点是 5/20 PM Design Week—— 届时我们将详细拆解 AI-Native PM 工作流中各主要步骤的自动化实现。

Pacing · 节奏

## 3 阶段 · 30 天 · 1 场 Design Week

4/21 → 5/20

01
必修

建立认知

4/21 – 4/26 · ~2h

02
动手核心

生态搭建

4/27 – 5/3 · ~3h

03
工作流深练

工作流深练

5/4 – 5/19 · ~4h

★
工作坊

PM Design Week

5/21 - 5/22

§ 01 · Concepts

## 先认清这 8 个核心要素

理解这些概念，学习过程中不再困惑。

一句话：
Claude 三种模式（Chat 问答 / Cowork 干活 / Code 编程）各司其职，Projects 记住你，
Skills 提供专业模板，Connectors 打通数据，Plugins 打包一切，Sub-agents 并行提速，
Dispatch 手机遥控，Scheduled Tasks 定时自动跑。

01 · Mode

### Claude 三种模式

本期学习的核心是 Cowork——
它让 Claude 走出对话框，可以读写本地文件、调用 Skills、跨多步骤完成真实工作。

本期重点

Chat

对话

网页/桌面对话窗口，适合问答与快速写作。无法操作本地文件。

Cowork

桌面 AI 工作台

可访问本地文件，执行多步骤复杂任务。本期学习核心。

Code

命令行

面向开发者的命令行编程助手。

02 · Memory

### Projects

持久化知识库。上传文档、设定背景，Claude 在每次会话中记住你的项目上下文。

03 · Templates

### Skills

预置专业能力模板。生成 PPT、分析竞品、整理会议记录——一键调用，无需从零写 Prompt。

04 · Integrations

### Connectors

连接外部工具（Google Drive、Slack、Notion 等），Claude 直接读取并操作你的数据源。

05 · Bundle

### Plugins

Skills + Connectors + Sub-agents 的打包组合，按角色或场景一键安装，开箱即用。

06 · Parallelism

### Sub-agents

并行执行多个子任务的 AI 线程。复杂任务可拆解，多个 agent 同时运行，大幅提速。

07 · Remote

### Dispatch

手机遥控桌面。扫码配对后，手机端发任务，Claude 在电脑端自动执行并返回结果。

08 · Automation

### Scheduled Tasks

定时自动化任务。描述一次，按计划重复执行——每天自动整理收件箱、生成日报等。

已认识 8 个核心要素？

进入第一阶段资源清单 ↓

§ 02 · Roadmap

## 4 阶段学习路径

点击阶段标题展开资源清单 · 每阶段 3–5 份精选材料

01

必修 · 认知
4/21 – 4/26 · ~2h

### 建立认知：Cowork 是什么，核心要素是什么？

官方课程 + 官方场景教程 + Academy 双线切入，在动手之前先建立完整心智模型。全部来自 Anthropic 官方，质量有保障。

▸

[必看
Official Guide

#### Get Started with Claude Cowork

官方入门指南，涵盖安装、文件夹授权、第一个任务的完整流程。读完对整体有清晰预期。

官方 Help Center

20 分钟](https://support.claude.com/en/articles/13345190-get-started-with-claude-cowork)

[必看
Article

#### 20 Claude Cowork Concepts Explained

系统梳理 20 个核心概念：从 Cowork 模式到 Sub-agents、Memory、Plugins，覆盖全面。配合官方文档一起看，建立完整知识框架。

AI Discoveries

30 分钟](https://aidiscoveries.io/20-claude-cowork-concepts-explained-beginner-to-advanced-2025-complete-guide/)

必看
Official Tutorials

#### Claude for Product Management · 官方场景教程 →

Anthropic 官方为 PM 设计的 4 个场景教程，全部来自真实工作流。其中
「Using Claude & Design for Prototypes and UX」
直接解答了我们的一个长期痛点——AI 生成的原型与自有系统风格不符：文章给出了如何将设计规范注入提示词、让原型贴近真实产品的标准思路，值得细读。

Anthropic 官方

40 分钟

推荐
Official Academy

#### Anthropic Academy · 免费官方课程平台 →

官方学习平台，免费注册即可观看。推荐本阶段重点学习
Claude 101——系统建立与 Claude 交互的基础认知框架，约 1 小时；
Claude Code in Action 适合对技术实现感兴趣的 PM 进阶参考。
直达课程：[Claude 101](https://anthropic.skilljar.com/claude-101) /
[Claude Code in Action](https://anthropic.skilljar.com/claude-code-in-action)

Anthropic Academy · 免费注册

Claude 101 约 1h

[推荐
Official Course

#### Agent Skills with Anthropic

Anthropic 与 DeepLearning.AI 合作的免费官方短课。系统讲解 Agent Skills 的设计理念、构建方式与最佳实践——理解 Claude 核心能力的权威入门，适合想深入了解的 PM 进阶阅读。

DeepLearning.AI · Anthropic

约 1 小时](https://learn.deeplearning.ai/courses/agent-skills-with-anthropic/lesson/ldn5c3/introduction)

02

动手 · 搭建
4/27 – 5/3 · ~3h

### 生态搭建：把 Skills、Connectors、Plugins 配置到位

安装 PM 专用 Skills 并在真实场景中上手；连通 Google Drive、Filesystem 等 Connector；
再用「Create with Claude」模式创建自己的第一个 Skill——本阶段结束时，你的 Cowork 已经能处理日常工作的核心流程。

▸

Step 1 · 从官方开始

打开 Cowork → Skills / Connectors / Plugins，在 Anthropic & Partner 分区找 PM 常用工具。
优先安装 Plugin 「Product Management」，内含 PRD、竞品分析等核心 Skills，用标准模板跑几个真实任务热身。

Step 2 · 接入数据源

连接 Google Drive、Filesystem 等 Connector，让 Claude 直接读写真实文件，
效果远超粘贴文本。按需接入 Jira、Figma 等其他工具。

Step 3 · 定制自己的 Skill

在 Cowork 中选 「Create with Claude」 模式，基于用得最顺手的 Skill 定制一个专属版本，
沉淀到团队 Plugin，人人开箱即用。

[必看
Video · YouTube

#### How Anthropic Uses Claude in Product Management

Anthropic PM Lisa Crofoot 演示内部真实场景——数据查询、Evals 生成，无需 SQL。
直接展示 BigQuery MCP 等 Connector 的接入效果，是 Step 1–2 最直观的官方参照。

YouTube · Lisa Crofoot

25 分钟](https://www.youtube.com/watch?v=91AJ0cpgLlQ)

[必看
Video · YouTube

#### Claude Code for Product Managers · Sachin Rekhi

前 LinkedIn PM Sachin Rekhi 的实战教程，覆盖 PRD 审阅、竞品分析 Skills 的构建。
手把手演示「Create with Claude」自定义 Skill，与 Step 3 直接对应，本阶段最实操的一课。

YouTube · Sachin Rekhi

约 1 小时](https://www.youtube.com/watch?v=zsAAaY8a63Q)

[推荐
Video · YouTube

#### Claude Code + Analytics Masterclass

PM 工作流自动化实战：反馈合成、PRD 生成与 MCP 工具整合。
展示 Plugins 配置与 UX 数据分析扩展，帮你从标准 Skills 平滑过渡到自定义场景。

YouTube

45 分钟](https://www.youtube.com/watch?v=WK0bZrS8pVs)

[启发阅读
Connectors

#### Claude Cowork Connectors Guide 2026

文章不长，但几个工作流的 Example 颇有启发——重点看各 Connector 的实际使用场景，帮你判断哪些值得优先接入。

CoworkEase

按需浏览](https://www.coworkease.com/blog/claude-cowork-connectors-guide)

03

工作流深练
5/4 – 5/19 · ~4h

### 工作流深练：尝试设计一个可复用的 AI 工作流

选一条你最想深入的 PM 链路（如：用户访谈 → 洞察梳理 → PRD 草稿），
先在虚构场景里跑通，再迁移到 Veeva 真实项目——最终打磨成一个可复用、可展示的工作流。

▸

📍 Design Week 预演 checklist：
（1）用 Veeva 真实项目素材跑通一次；（2）整理一份 < 10 分钟的演示脚本；（3）5/16 前做一次内部 dry-run；（4）把 Skill + Prompt 沉淀到团队共享 Project 中。

[必看
Interactive Course · Free

#### Claude Code for PMs (ccforpms.com)

完全免费的实践型课程，所有练习都在 Cowork 里完成，没有视频——边做边学。
模块 2 让你在虚构公司 TaskFlow 上写 PRD、分析数据、做竞品策略，
跑通后直接迁移到 Veeva 真实场景，是本阶段最好的"实验沙盒"。

ccforpms.com · 免费

按模块选取](https://ccforpms.com)

[必看
Workshop Series

#### The AI-Native Product Manager (Maven · Lenny)

Lenny Rachitsky × Maven 的 AI-Native PM 免费工作坊系列，嘉宾包括 Tomer Cohen、Peter Yang 等。
给"可复用工作流"的设计提供方法论框架——先看几集，再动手实践。

Maven · 免费

按需选看](https://maven.com/x/ai-native-pm-lenny)

[推荐
Official Research

#### How AI Is Transforming Work at Anthropic

Anthropic 披露内部各团队（含 PM、工程、运营）如何用 Claude 做实际工作，附具体生产力指标。
适合作为团队讨论材料：对照「Anthropic 内部用法」与「Veeva 当前实践」，找出 3–5 个可迁移的工作流。

Anthropic Research

25 分钟](https://www.anthropic.com/research/how-ai-is-transforming-work-at-anthropic)

[推荐
Deep Dive

#### Cowork + Agentic Workflow 深度指南

详解如何设计 claude.md（全局规则 + 项目规则）、
用 Cowork 管理端到端 PM 链路（产品探索 → 竞品分析 → PRD 生成）。
按文中思路，尝试把你选定的工作流跑成一个自动化闭环。

aimaker.substack

30 分钟](https://aimaker.substack.com/p/claude-cowork-review-agentic-ai-guide)

§ 03 · The Finale

## 5/21 · PM Design Week

这一天，我们会把 PM 的日常工作流拆解成不同步骤，针对关键环节设置独立 Workshop，一起探讨如何用 Claude 更高效地完成——最终目标不只是学会用 AI，而是沉淀出一套团队共享的 AI-Native PM Workflow。

Final Goal

实现

AI-Native
PM Workflow

让 Claude 变成团队的默认工作方式

Design Week 的做法 · 三步走

01
Decompose

### 拆解 PM 工作流

把日常工作切成可观察的步骤：发现问题 → 用户研究 → 竞品分析 → 撰写 PRD → 设计评审 → 跟进落地。
把默会的流程摆到台面上。

02
Equip

### 每步分享一个最佳实践

对每个步骤，现场分享最匹配的 Skill / Prompt / Sub-agent 套路——从"要干这件事"
到"该调哪个技能"。共享到团队 Plugin，人人开箱即用。

03
Compose

### 组合出 AI-Native Workflow

把所有步骤串起来：AI 处理重复和发散，PM 专注判断与决策。
最终形成一套团队级共享的 AI-Native PM Workflow。

Decompose
→
Equip with Skills
→
AI-Native PM Workflow

§ 04 · Advice

## 学习建议

执行胜过阅读。每个阶段尽量把学到的东西跑一次真实工作任务——哪怕只是整理一次会议记录。
学习时长是估算值，真正的收益在动手那一刻发生。

01

Practice First

安装好后立刻用自己的真实文件练手，比看教程有效 10 倍。

02

Leverage Skills

优先体验 Skills——用预置模板做 PRD、竞品分析，比从零写 Prompt 快得多。

03

Connect Your Data

第二阶段把 Google Drive、Gmail、Filesystem、PowerPoint、Figma 都连上，Claude 能直接读你的真实数据，效果天差地别。

04

Weekly Share

每周 15 分钟团队分享，各讲一个新用例——互相启发效果翻倍。

05

Real Tasks, Not Drills

每阶段结束挑一个真实工作任务交给 Claude 完成，直接为 Design Week 的 demo 蓄力。

Copyright © Veeva Systems 2026 · 为 China CRM · PM Team 设计

4/21 kickoff · 5/20 Design Week · v4