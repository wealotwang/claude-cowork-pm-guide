# Day03 输出：AI Compliance Eval 设计学习报告

日期：2026-07-31  
主题：从“评估 AI 分得准不准”转向“验证产品能不能安全上线”

---

## 一、这份报告记录什么
本文档记录 `Medical CRM Compliance Checker` 的 Eval 方案设计过程中，团队在指标、数据集、人工复核和上线门槛上的关键认知变化。

目标不是复述讨论过程，而是沉淀一套后续可复用的方法论：
- 为什么企业级 AI Eval 不能照搬通用模型 benchmark 思路
- 如何区分 `Dataset`、`Evaluation Policy`、`Release Metrics`
- 如何让 Eval 真正服务于产品上线，而不是只服务于模型分析

---

## 二、最大的认知变化
### Eval 不是为了证明 AI 很聪明，而是为了证明产品可以上线
这是今天最重要的收获。

一开始，我们自然会从模型视角出发，关心：
- `Accuracy`
- `Category Accuracy`
- `Severity Accuracy`
- `Recall`
- `Precision`

这是一种典型的 `Machine Learning Benchmark` 思路，核心问题是：

> 模型到底分得准不准？

但在继续讨论后，我们意识到：

- `Compliance Checker` 不是一个研究模型能力的项目
- 它首先是一个企业产品
- 企业真正关心的不是模型是否“分类漂亮”，而是：

> 这个 AI 能不能让我放心上线？

所以，Eval 的目标应该从：
- `Evaluate AI Capability`

转变为：
- `Validate Business Risk`

这次转向，决定了后面所有设计取舍。

---

## 三、关键设计变化
### 1. Metrics 不是越多越好
最开始我们设计了很多指标：
- `Recall`
- `False Negative Rate`
- `Category Accuracy`
- `Severity Accuracy`
- `Boundary Case Accuracy`
- `Reason Score`
- `Explainability Score`

但后来发现，很多指标其实在回答同一个问题。

例如：
- `Recall = 1 - False Negative Rate`

这两者本质上是同一件事的不同表达，没有必要同时保留。

最终我们得到的经验是：

> 一个好的 Eval，不是指标越多越专业，而是每个指标都要回答一个不同的业务问题。

---

### 2. 不要为了 AI 设计指标，而要为了业务设计指标
这是第二个很大的认知变化。

例如 `Category Accuracy`。

从 AI 社区视角看：
- 分类必须准确

但从业务视角看，很多时候真正关心的是：
- 风险有没有被拦住

举例：
- 输入：`这个药可以治疗糖尿病`
- 模型判成：`False Claim`
- 而不是：`Off-label Promotion`

虽然分类错了，但如果系统已经正确拦截了内容，那么：
- 业务风险已经被控制
- 上线目标已经达成

所以，`Category Accuracy` 很重要，但它更适合作为：
- `Diagnostic Metrics`（诊断指标）

而不是：
- `Release Metrics`（上线指标）

这意味着：

> 不同指标的地位不同，有些用来放行产品，有些用来帮助分析问题。

---

### 3. Dataset 和 Evaluation Policy 必须分离
这是今天最重要的设计调整之一。

一开始，我们在 case 里加入了类似：
- `Must Detect = Yes`

后来重新分析后发现，这个字段设计得不对。

原因是：
- 一个 case 本身只是一个“事实”
- 它不会天然告诉你“必须 100% 检出”还是“95% 也能接受”

真正决定这件事的，不是数据，而是企业的风险策略。

所以我们把两件事拆开：

#### Dataset 负责表达事实
例如：
- `Category = Bribery`
- `Risk Level = Critical`

#### Evaluation Policy 负责表达企业要求
例如：
- `Critical Recall = 100%`

这本质上是一个很典型的软件设计原则：

> Data 与 Policy 分离。

以后做任何 Eval，都要优先检查：

> 我是不是把数据和策略混在一起了？

---

### 4. Risk Level 属于数据，Recall Threshold 属于策略
这是上一条继续推导出来的结论。

最开始我们想把：
- `Must Detect`

放在 case 数据里。

后来发现，真正应该保留在数据层的是：
- `Risk Level`

例如：
- `Critical`
- `High`
- `Medium`

因为 `Risk Level` 描述的是：
- 这个 case 本身的风险属性

而 `Recall Threshold` 描述的是：
- 企业对不同风险等级的容忍度

例如：

| Risk Level | Recall 要求 |
|---|---|
| Critical | 100% |
| High | 95% |
| Medium | 视业务场景而定 |

这两个层级不应该混在一起。

---

### 5. Human-in-the-loop 的定位变了
最开始我们认为：
- 人工要参与每条 Eval

但后来发现，这种方式成本太高，也不利于持续运行。

人工真正应该参与的是两类环节：

#### A. Benchmark Construction
由合规专家提前标注：
- 是否违规
- 风险类别
- 风险等级

#### B. Failure Case Review
在 AI 自动跑完之后，人工重点复核：
- 漏报案例
- 高风险误判
- 修改建议质量

而不是：
- Review every case

这意味着：

> Eval 可以持续自动跑，人工只在最值钱的位置介入。

---

### 6. Release Metrics 和 Diagnostic Metrics 必须分开
这是很多团队都会踩的坑。

有些指标非常有分析价值，但不应该直接决定是否上线。

例如：
- 各类风险的分类覆盖情况
- 各类别的 Recall 分布
- 说明文本质量

这些很适合放在 Dashboard 或分析报告里，但它们不是 Release Gate。

真正决定上线的，是那些直接回答业务风险的问题，例如：
- `Critical Recall = 100%`
- `高危漏报 = 0`

所以，后续设计中我们会把指标分成两类：

#### Release Metrics
直接决定能不能上线

#### Diagnostic Metrics
帮助排查问题和指导优化

这个区分非常重要。

---

### 7. 不要一开始就追求真实数据
一开始我们反复担心：
- 没有真实数据怎么办？

后来意识到：
- 在上线前，本来就不一定有足够真实数据
- Eval Dataset 本身就可以是“人为构造”的

真正重要的不是：
- 数据是不是来自生产环境

而是：
- 它是否覆盖了关键业务风险

这个思路很重要，因为否则很多团队会一直等待“真实数据”，导致：

> Eval 永远起不来。

---

### 8. Case 的作用不是模拟真实，而是覆盖风险
最开始我们希望：
- case 越真实越好

后来逐渐发现，Benchmark 更重要的是：
- `Coverage`

如果 50 条 case 全部都是同一类风险，即使 Recall 很高，也没有太大意义。

真正应该覆盖的是：
- 各类高风险模式
- 关键中风险模式
- 典型边界样例
- 容易误伤的 near-miss 样例

所以，Benchmark 应该优先按：
- `Risk Taxonomy`

来设计，而不是随机采样。

---

## 四、最终形成的方法论
经过这一天的讨论，我们最后沉淀出一条比较完整的方法链路：

1. `Compliance` 定义 `Risk Taxonomy`  
2. 构造 `Benchmark Dataset`  
3. 定义 `Evaluation Policy`  
4. 由 `AI` 自动运行测试  
5. 自动生成 `Release Metrics`  
6. 人工 `Review Failure Cases`  
7. 将失败案例补充回 `Benchmark`，形成持续迭代

一句话概括：

> 先定义风险，再设计数据，再定义策略，最后才让 AI 去跑。

---

## 五、今天最大的收获
如果只用一句话总结今天的认知变化，我会写成：

> AI Eval 的设计，不应该从模型出发，而应该从业务风险出发。

过去我们容易问：
- 模型有没有分对？

而今天我们真正问的是：
- 业务风险有没有被控制住？

这两个问题看起来接近，但代表的是两种完全不同的产品思维。

---

## 六、可沉淀成团队 Checklist 的通用原则
建议把今天提炼出的经验沉淀成一套 AI Eval Checklist：

- 先定义业务目标，再定义模型指标
- 区分 `Dataset`（事实）与 `Evaluation Policy`（策略），不要混在一起
- `Release Metrics` 保持精简，每个指标只回答一个明确业务问题
- `Diagnostic Metrics` 用于分析与迭代，不直接作为上线门槛
- `Human-in-the-loop` 重点放在基准数据建设和失败案例复核，而不是参与每一次评测
- `Benchmark` 的目标是覆盖风险，而不是追求“像真实数据”
- 随着失败案例积累，持续更新 `Benchmark`，让 Eval 成为一个演进中的体系，而不是一次性测试

---

## 七、为什么这份经验可迁移
这套经验并不只适用于 `Medical CRM Compliance Checker`。

它同样适用于：
- 合同审核
- 客服质检
- 金融风控
- 企业知识库审核
- 其他企业级 AI 风险控制产品

因为这些场景都有一个共同点：

> 最终要验证的，不是模型能力本身，而是企业风险是否被稳定控制。

