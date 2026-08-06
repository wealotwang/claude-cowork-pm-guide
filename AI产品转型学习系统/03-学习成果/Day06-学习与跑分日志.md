# Day06 学习与跑分日志

日期：2026-08-05
主题：把 demo 接入 DeepSeek，并分别用 demo 子集评测与完整 CSV50 benchmark 跑出第一版真实结果

---

## 这份日志的作用
这不是“流水账”，而是 Day06 当天的学习与优化记录。

它回答 4 个问题：
- 今天到底做了什么
- 为什么要这么做
- 哪一步带来了什么结果
- 下一步该优先补哪里

---

## Day06 起点
开始 Day06 时，项目状态是：
- demo 已经能跑
- regex 前置层（05 类结构化 PII）已验证可工作
- LLM 路线最初写的是 Anthropic
- 但用户手头现成可用的是 DeepSeek key

因此 Day06 的目标被重新定义为：
- 不是“申请 Anthropic key”
- 而是“把 demo 接入 DeepSeek，并跑出第一版真实基线结果”

---

## 今日动作记录

### 1. 先把 Day06 的目标校准清楚
做了什么：
- 确认 Day06 不需要重新造一批数据
- 明确先用现有评测集跑

为什么：
- 前面已经有 `eval_cases.json`
- 后面又补充了更完整的 `medical_crm_compliance_eval_dataset_cn.csv`
- Day06 的重点应是“拿真实结果”，不是“继续堆数据”

结论：
- Day06 的核心是：接模型、跑评测、记结果、准备迭代

---

### 2. 把 demo 从 Anthropic-only 改成优先支持 DeepSeek
涉及文件：
- `03-学习成果/demo/checker.py`
- `03-学习成果/demo/run_eval.py`
- `03-学习成果/demo/README.md`

做了什么：
- 新增 provider 自动选择逻辑
- 优先读 `DEEPSEEK_API_KEY`
- 保留 `ANTHROPIC_API_KEY` 作为兜底
- 更新提示信息和 README 用法

为什么：
- 用户当前真实可用的是 DeepSeek
- 不应该让 Day06 卡在“拿不到 Anthropic key”

结果：
- demo 现在默认走 DeepSeek 路线

---

### 3. 做 Day06 预检
做了什么：
- 在没有可用 key 时跑 `run_eval.py`

为什么：
- 先确认代码链路没问题
- 区分“环境未配好”和“代码本身跑不通”

结果：
- 预检通过
- 没 key 时会优雅降级，不会直接崩溃

---

### 4. 用 demo 自带子集评测跑第一版真实基线
使用文件：
- `03-学习成果/demo/eval_cases.json`
- `03-学习成果/demo/run_eval.py`

跑出来的结果：
- 总用例数：30
- 通过：29
- 失败：1
- 高危类 Recall：100%
- 应放行 case 误报率：0%

怎么理解：
- 这是“当前 MVP 在自己已经实现的 4 类范围内”的结果
- 适合证明：这个 demo 不是空壳，已经能在自己声明的范围里跑得不错

唯一失败：
- `05-gap-1`
- 失败原因不是意外，而是我们事先定义的已知局限：
  - 当前 05 主要靠结构化 PII 正则
  - 不覆盖“电话号码”这种非结构化敏感表达

---

### 5. 对齐完整 Eval 定义，再跑 CSV50 benchmark
使用文件：
- `/medical_crm_compliance_eval_dataset_cn.csv`
- `03-学习成果/CRM-Compliance-Eval框架说明.md`
- `03-学习成果/CRM-Compliance-Eval-框架-v2.html`

为什么要再跑这一轮：
- 上一轮只证明了 demo 子集范围内的能力
- 用户需要看清完整产品框架下，当前 MVP 到底差在哪里

为此新增：
- `03-学习成果/demo/run_eval_csv.py`

这个 runner 的作用：
- 用完整 50 条 CSV benchmark 跑当前 demo
- 按完整框架的 Release Gate 口径输出结果
- 同时保留 Diagnostic 指标，帮助解释错因

---

### 6. 第一次 CSV50 跑分暴露了稳定性问题
发生了什么：
- 直接跑 CSV50 时，部分 case 触发了 DeepSeek 非 JSON / 空返回
- 导致整轮评测中途退出

这一步的学习价值：
- 说明完整 benchmark 不只是测“对不对”
- 也会测出“稳不稳定”

随后优化：
- 把 `run_eval_csv.py` 改成稳健模式
- 单条报错记为 `ERROR`
- 整轮继续跑完

---

### 7. 最终 CSV50 跑分结果
使用模型：
- `deepseek-v4-flash`

使用数据集：
- `medical_crm_compliance_eval_dataset_cn.csv`

最终结果：
- 总用例数：50
- 成功跑完：47
- 报错：3

当前采用的核心口径：
- 先看风险层级上的 release 指标
- 不再把动作兼容性当作当前阶段重点
- 这版分数里混合了“已实现类别的真实能力”与“未实现类别的自然漏报”

Release Gate 指标：
- 高危类（01-05）Recall：45%（10/22）
- 中危类（06-09）Precision：77%（10/13）
- 低危误报率：0%（0/9）

Day07 要继续补的一步：
- 把这 45% 拆开成“已实现类别里测得怎样”与“未实现类别自然测不出”两部分，而不是只看一个总数

---

## 今天真正学到的东西

### 1. 同一个系统，在不同 evals 下会呈现完全不同的面貌
- 用 `eval_cases.json` 跑时，像是在看“当前 MVP 的最佳工作区间”
- 用 `medical_crm_compliance_eval_dataset_cn.csv` 跑时，像是在看“完整产品框架压当前 MVP 的真实压力测试”

这两个结果不矛盾，而是分别回答两个不同问题：
- 它在已实现范围内表现怎样？
- 它距离完整产品能力还差多少？

### 2. 当前差距主要不是模型厂商，而是能力覆盖范围
从 CSV50 的失败模式看，主要差距来自：
- 02 / 03 / 04 / 06 / 09 这些类本来就没在当前 demo 里实现
- 05 类只覆盖了结构化 PII，没有覆盖非结构化隐私
- 少量 case 暴露了 LLM 输出稳定性问题

所以现在不应该把重点放在：
- “是不是换个模型就好了”

而应该放在：
- “当前到底缺哪几类规则能力”
- “哪些能力最值得优先补”

---

## 失败原因归因表

### A. 规则缺失 / 类别未实现
典型类别：
- 02 非法获取统方数据
- 03 主动超说明书 / 超适应症推广
- 04 隐瞒 / 延迟报告不良反应
- 06 讲课费 / 学术赞助对价化
- 09 规避备案 / 违规区域拜访

### B. 侦测能力不足
典型类别：
- 05 患者隐私泄漏

表现：
- 结构化号码能抓到
- 掩码号码、姓名、住址、病历照片、非结构化隐私表达抓不住
- Day07 已先在规则配置层补充一轮说明和示例，准备验证是否能改善这部分失败

### C. 运行稳定性问题
典型表现：
- 非 JSON 返回
- 空返回

这部分不是规则覆盖问题，但会直接影响线上可靠性

---

## 今天的阶段性结论
- `eval_cases.json` 的结果可以证明：当前 MVP 在已实现范围内有可展示价值
- `medical_crm_compliance_eval_dataset_cn.csv` 的结果可以证明：当前 MVP 还不能代表完整 10 类产品能力
- 这不是坏消息，反而让后续优化优先级变得更清楚

---

## 下一步建议优先级
1. 先把 `CSV50` 按“已实现类别 / 未实现类别”拆开统计
2. 优先验证 `05` 规则层小更新是否改善非结构化 PII 相关失败
3. 再决定是继续深挖 `05`，还是转向 `03` 超适应症

为什么这样排：
- `05` 和 `03` 都直接影响高危 Recall
- 是最容易在作品集中讲成“改前后对比”的两类

---

## 相关文件
- [Day06-DeepSeek-跑分报告.html](file:///Users/li/ai%20pm%20learning/claude-cowork-pm-guide/AI产品转型学习系统/03-学习成果/Day06-DeepSeek-跑分报告.html)
- [Day06-CSV50-跑分报告.html](file:///Users/li/ai%20pm%20learning/claude-cowork-pm-guide/AI产品转型学习系统/03-学习成果/Day06-CSV50-跑分报告.html)
- [Day06-System-Prompt-固定模板.md](file:///Users/li/ai%20pm%20learning/claude-cowork-pm-guide/AI产品转型学习系统/03-学习成果/Day06-System-Prompt-固定模板.md)
- [Day06-用户规则配置模板-v2.2.json](file:///Users/li/ai%20pm%20learning/claude-cowork-pm-guide/AI产品转型学习系统/03-学习成果/Day06-用户规则配置模板-v2.2.json)
- [Day06-内部实现说明-v1.md](file:///Users/li/ai%20pm%20learning/claude-cowork-pm-guide/AI产品转型学习系统/03-学习成果/Day06-内部实现说明-v1.md)
- [demo/run_eval.py](file:///Users/li/ai%20pm%20learning/claude-cowork-pm-guide/AI产品转型学习系统/03-学习成果/demo/run_eval.py)
- [demo/run_eval_csv.py](file:///Users/li/ai%20pm%20learning/claude-cowork-pm-guide/AI产品转型学习系统/03-学习成果/demo/run_eval_csv.py)
- [demo/rules_config.json](file:///Users/li/ai%20pm%20learning/claude-cowork-pm-guide/AI产品转型学习系统/03-学习成果/demo/rules_config.json)
