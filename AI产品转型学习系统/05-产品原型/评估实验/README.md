# 评估实验

跟`规则执行/`、`命中结果/`、`分析报告/`那套正式流程分开放——这个文件夹放的是"面试冲刺阶段"的补充实验，
不是产品正式功能，改动/失败都不影响主demo。

## llm_judge_eval.py —— LLM as a Judge：审核判断理由的质量

背景：现有评测（`规则执行/run_dataset_cli.py`）只衡量"AI判断结果对不对"（召回率/精准率），
不衡量"AI给出的判断理由本身靠不靠谱"。这个脚本补一个新维度——找另一个LLM当"审核官"，
去审已经跑出来的`命中结果/hits_*.json`里每条case的`actual_rationale`：

1. **忠实度（faithful）**：理由里提到的内容，是不是原始文本里真实写了的？有没有编造原文没提到的信息？
2. **逻辑自洽（logic_supports_verdict）**：这些内容能不能真的支撑起最终给出的判断结论？

用法：
```bash
export DEEPSEEK_API_KEY="你自己的key"   # 跟 checker.py 用的是同一套凭证读取逻辑，会自动从 .env 读
cd "05-产品原型/评估实验"
python3 llm_judge_eval.py                          # 默认：用最新一份 hits_*.json，抽样18条
python3 llm_judge_eval.py --file hits_20260810_184404.json --sample 20
```

**2026-08-14 试跑记录**：脚本本身的抽样逻辑（优先囊括所有判断出错的case + 随机抽正确case做对照）
和文件读写都已经跑通验证过。但当前所在的Cowork沙盒环境网络出口不允许直连`api.deepseek.com`
（`Tunnel connection failed: 403 Forbidden`），脚本自动调用DeepSeek当judge这条路走不通。

改用了另一个方案：**直接让Claude（Cowork会话里的agent本身）当judge**，人工/agent审阅同样抽出的
18条case，产出格式跟脚本设计的输出完全一致，存成`judge_results_20260814.json`。这个方案意外地
更贴合"LLM as a judge"的方法论最佳实践——checker用的是DeepSeek，judge用Claude，天然是跨模型评审，
比"同一个模型自己判自己"更有说服力（同模型自审容易有系统性偏差，这也是行业里推荐跨模型评审的原因）。

**这次18条的结果**：
- 忠实度（faithful）：18/18 全部通过，没有发现任何编造/脑补原文没有的信息
- 逻辑自洽（logic_supports_verdict）：18/18 全部通过
- 但有4条标了`notable`，不是"错"，是值得记录的细节：
  - **MB219 / MB247 / MB267**（3条已知漏判case）：judge确认理由本身不是编的、逻辑也自洽——
    问题不是AI"想错了"，是当前4大类taxonomy本来就没覆盖"规避医院核查"这个场景（对应已经主动推迟
    的旧09类）。这是一次独立证据，佐证了Day08/09那次taxonomy重构的判断是对的：**这类漏判是产品
    设计的范围缺口，不是模型推理缺陷**——面试被问"怎么区分是数据问题、模型能力问题还是产品设计
    问题"时，这个是一个具体、可复现的证据案例。
  - **MB239**（"称兄道弟+主任口头说会罩着"）：技术上没有具体利益承诺，放行在当前规则下站得住，
    但属于"关系铺垫型"灰色地带，judge主动标出来建议人工复核，这类"关系型软性影响"目前的4大类
    规则也没有覆盖，可以记进未来方向。

如果之后想要一版真正走DeepSeek API的对照结果（比如想验证换一个judge模型结论会不会不一样），
在自己电脑终端里跑：
```bash
export DEEPSEEK_API_KEY="你自己的key"
cd "05-产品原型/评估实验"
python3 llm_judge_eval.py
```

面试里可以用这份材料回答"你怎么控制/发现模型的幻觉"这类追问——这是Day11模拟追问里被问到、
之前没有具体实证材料的一个点，现在有了。

## claude_crossmodel_results60.json —— 跨模型验证：换Claude当分类器，结果稳不稳

背景：README"未来方向"一直挂着一条"多模型验证：同一套规则换成Anthropic等其他模型跑一遍，
验证规则设计是否只对DeepSeek有效"，2026-08-14实际做了一次。

**方法**：从DeepSeek那轮300条真实结果里，按risk_level分层抽样60条（41条Critical/Reject +
19条Low/Pass，比例对齐300条总体分布）。原计划走`ANTHROPIC_API_KEY`真实调用Anthropic API（这个
域名沙盒网络是通的，测过返回401而不是403，说明网络没被挡，只是没配key），但当时没有现成key，
于是还是用了跟judge实验一样的方式——**Claude直接读原文、套用`规则配置/system_prompt.md`+
`rules_config.json`独立判断**，不参考DeepSeek已经给出的结果，产出`claude_action`列。

**结果**：60条里，Claude和DeepSeek在**59条上给出了完全一样的判断**——不是聚合指标凑巧接近，
是逐条判断结果基本一致。唯一的分歧点还是`MB219`，也不是真正的分歧：两个模型都判了Pass，都在
同一个已知的taxonomy缺口上"犯了同一个错"，原因相同（当前4类规则没覆盖"规避核查"这类违规）。

这次的Critical召回率97.6%（40/41）、精准率100%（0误报），跟DeepSeek全量300条的95.6%~98.5%召回率、
100%精准率区间高度吻合。**结论**：现有的taxonomy设计和prompt结构不是只对DeepSeek这一个模型的
脾气调出来的效果，换一个模型家族结果基本不变，说明规则设计本身是稳的，问题（MB219这类）出在
规则覆盖范围，不是被某个模型的特性"凑"出来的假象。

如果之后拿到真实的`ANTHROPIC_API_KEY`，可以走真正的API调用重跑一次做对照（沙盒网络本身支持，
不需要像DeepSeek那样交给自己电脑跑）：
```bash
export ANTHROPIC_API_KEY="你自己的key"
cd "05-产品原型/规则执行"
python3 run_dataset_cli.py 简化二分类版
```
