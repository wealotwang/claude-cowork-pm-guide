# Demo：AI Compliance Check Assistant（Day05/06 最小可运行原型）

更新时间：2026-07-31

---

## 这是什么

Day05 设计、待 Day06 用真实 API 跑通验证的最小 demo。只覆盖 4 类风险子集：

| 类别 | 名称 | 风险等级 | 处置动作 | 判断方式 |
|---|---|---|---|---|
| 01 | 商业贿赂与利益交换 | Critical | Reject | LLM（语义关系判断） |
| 05 | 患者隐私泄漏 | Critical | Block | 正则（结构化PII） |
| 07 | 夸大疗效与绝对化宣讲 | Medium | Warning | LLM（语义关系判断） |
| 10 | 学术表述不严谨/完全合规 | Low | Pass | LLM（兜底类别） |

## 为什么是"正则 + LLM"混合架构

Day04 复盘时发现：05类隐私信息（身份证号、手机号）是结构化、格式固定的，正则就能可靠识别，快且不花 token；而01/07这类的判断难点在语义关系（比如"讲课费"本身不违规，关键是有没有和处方量/进院挂钩），只有 LLM 能做这种判断。不是所有 case 都应该无脑丢给 LLM——这个架构选择本身就是一个可以在面试里讲的产品判断。

## 文件说明

- `rules_config.json` —— 规则定义唯一来源，包含每类的说明、违规示例、边界示例。改规则改这里，不用碰代码。
- `checker.py` —— 核心引擎：`regex_prefilter()` 处理05类，`llm_classify()` 处理01/07/10类，`classify()` 是统一入口。也可以直接当 CLI 用。
- `eval_cases.json` —— 合并自 `评测集-v1.md` 自拟case + CRM框架筛选case，约30条，覆盖违规/边界/near-miss/已知局限四种类型。
- `run_eval.py` —— 跑 eval_cases.json，按 Day04 的判断分开算指标：高危类看 Recall，中低危/合规类看误报率。

## 怎么跑

```bash
# 1. 设置你自己的 Anthropic API key（这一步必须你自己做，不会被本项目存储或上传）
export ANTHROPIC_API_KEY="你的key"

# 2. 单条测试
cd 03-学习成果/demo
python3 checker.py "这个月表现不错，给你包个红包"

# 3. 跑完整评测集，看基线分数
python3 run_eval.py
```

不设置 API key 也能跑：05类的正则部分不需要 key，会正常工作；01/07/10类的case会被清楚地标记为"跳过"而不是报错崩溃，报告里也会说明有多少条因为没有 key 没测。

## 已知局限（demo 阶段主动收敛，不是遗漏）

- 05类正则只覆盖身份证号/手机号/病历号标注这类结构化PII，姓名、住址等非结构化PII识别没做（eval_cases.json 里 `05-gap-1` 这条 case 专门用来证明这一点）
- 02/03/04/06/08/09 六类风险在 `CRM-Compliance-Eval框架说明.md` 里有完整设计，但demo阶段不实现
- 目前是纯文本分类，没有接入 RAG 做依据引用（规则4.5的能力扩展留到demo稳定之后再加）

## 下一步（Day06）

用真实 API key 实际跑一遍 `run_eval.py`，记录基线分数（Recall / 误报率），然后至少做1轮"改规则前后对比"的迭代——这是评测驱动方法论最终要在作品集里体现的证据。
