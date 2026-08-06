# Demo：AI Compliance Check Assistant（Day05-07 最小可运行原型）

更新时间：2026-08-06（已同步 Day07 的 6 类规则口径、300 case 压测结果与 runner 新能力）

---

## 这是什么

Day05 设计、Day06 接入 DeepSeek 跑通验证的最小 demo，Day07 进入评测驱动迭代。**当前实际生效的是 6 类风险子集**，以 `../Day06-用户规则配置模板-v2.2.json` 为准：

| 类别 | 名称 | 风险等级 | 处置动作 | 判断方式 |
|---|---|---|---|---|
| 01 | 商业贿赂与利益交换 | Critical | Reject | LLM（语义关系判断） |
| 03 | 主动超说明书 / 超适应症推广 | Critical | Reject | LLM（语义关系判断） |
| 05 | 患者隐私泄漏 | Critical | Reject | 正则前置（结构化PII）+ LLM兜底 |
| 06 | 讲课费 / 学术赞助对价化 | Medium | PassWithNotice | LLM（语义关系判断） |
| 07 | 夸大疗效与绝对化宣讲 | Medium | PassWithNotice | LLM（语义关系判断） |
| 10 | 学术表述不严谨/完全合规 | Low | Pass | LLM（兜底类别） |

Day06 把动作空间也收敛过一次：当前只有 `Reject / PassWithNotice / Pass` 三种，不再用 `Block/Warning` 这两个旧名字（历史文档里出现的 Block/Warning 已经是旧版本说法）。

## 为什么是”正则 + LLM”混合架构

Day04 复盘时发现：05类隐私信息（身份证号、手机号）是结构化、格式固定的，正则就能可靠识别，快且不花 token；而01/07这类的判断难点在语义关系（比如”讲课费”本身不违规，关键是有没有和处方量/进院挂钩），只有 LLM 能做这种判断。不是所有 case 都应该无脑丢给 LLM——这个架构选择本身就是一个可以在面试里讲的产品判断。

Day06 进一步把系统拆成三层，避免后续优化混层：
- **固定 system prompt**（`../Day06-System-Prompt-固定模板.md`）：系统角色、输入输出格式、判断原则，基本不改
- **用户规则配置**（`../Day06-用户规则配置模板-v2.2.json`）：规则说明、违规示例、边界示例、动作——这是企业/我们平时改规则时唯一要动的文件
- **内部实现增强**（`checker.py` 里的 `INTERNAL_STRUCTURED_DETECTORS`）：正则前置这类系统内部能力，不需要也不应该让用户去配置

## 文件说明

- `checker.py` —— 核心引擎：`regex_prefilter()` 处理05类结构化PII，`llm_classify()` 处理其余类别的语义判断，`classify()` 是统一入口，优先走 DeepSeek，没配置则退回 Anthropic。也可以直接当 CLI 用。
- `../Day06-用户规则配置模板-v2.2.json` —— 规则定义唯一来源（**注意：不再是本目录下的 `rules_config.json`，后者现在只是镜像/兼容文件，不是主来源**）。
- `../Day06-System-Prompt-固定模板.md` —— 固定 system prompt。
- `../Day06-内部实现说明-v1.md` —— 内部实现层的说明文档。
- `eval_cases.json` —— MVP 子集评测，约30条，覆盖违规/边界/near-miss/已知局限四种类型（`expected_action` 字段还是 Day05 时期的旧动作名，不影响跑分——`run_eval.py` 只比对类别，不比对动作名，但迟早该更新成新名字）。
- `run_eval.py` —— 跑 eval_cases.json（MVP子集），按高危类看 Recall、中低危/合规类看误报率分开算指标。
- `run_eval_csv.py` —— 跑 CSV benchmark。现在除了仓库根目录的 `medical_crm_compliance_eval_dataset_cn.csv`，也支持直接传入更大的外部 CSV（例如 Day07 的 300 case）。已支持：
  - `分类ID` 自动补零
  - 忽略或可选处理 `预期动作`
  - `--workers` 并发
  - `--progress-every` 进度输出
  - `--results-out` 逐条结果落盘

## 怎么跑

```bash
export DEEPSEEK_API_KEY=”你的key”   # Day06起默认优先走DeepSeek；没设置也支持ANTHROPIC_API_KEY兜底

cd 03-学习成果/demo
python3 checker.py “这个月表现不错，给你包个红包”   # 单条测试
python3 run_eval.py                                # MVP子集评测
python3 run_eval_csv.py                             # 完整CSV50压力测试
```

不设置 LLM key 也能跑：05类的正则部分不需要 key，会正常工作；其余类别的案例会被清楚地标记为“跳过”，而不是报错崩溃。

## 已知局限（demo 阶段主动收敛，不是遗漏）

- 05类目前除了结构化PII，也开始覆盖一部分“具名患者 + 联系方式/住址/病历信息”的非结构化隐私；但低风险汇总样本仍然可能被误伤
- 当前虽然已经补入 `03` 与 `06`，但 `02 / 04 / 08 / 09` 仍未形成独立稳定的分类能力
- `06` 当前的主要难点不是能不能识别风险，而是容易被更粗粒度地吸到 `01 商业贿赂`
- 目前是纯文本分类，没有接入 RAG 做依据引用（规则4.5的能力扩展留到demo稳定之后再加）

## Day06 已完成：第一版真实基线

用 DeepSeek 跑出的基线（详见 `../Day06-学习卡.md`）：
- MVP子集（30条，仅测已实现的4类）：29通过/1失败（失败的就是已知局限`05-gap-1`），高危Recall 100%，应放行case误报率0%
- 完整CSV50（覆盖全部10类）：47/50跑通，3条报错；高危Recall 45%、中危Precision 77%、低危误报率0%——这个数字里混杂了“已实现类别测得怎样”和“根本没实现的类别自然测不出”两种情况，Day07 已开始拆开看

## Day07 当前状态

Day07 已经完成的事：
1. 统一了当前规则口径：现在以 `01 / 03 / 05 / 06 / 07 / 10` 这 6 类为准
2. 完成了一轮 Day06 vs Day07 的 before / after：
   - `CSV50` 高危Recall 从 `45%` 提升到 `50%`
   - 报错从 `3` 降到 `1`
3. 跑通了新的 `300 case` benchmark：
   - 成功 `273 / 300`
   - 高风险召回率 `87%`
   - 中风险判断准确率 `96%`
   - 低风险误伤率 `5%`

Day07 还没做完的重点：
1. 围绕 `300 case` 的问题样本继续深挖
2. 在 `05 / 06 / 04 / 09 / 输出稳定性` 之间，选一个最值得的方向做第二轮优化
3. 再做一次“改前 -> 改后 -> 再跑一轮”的闭环
