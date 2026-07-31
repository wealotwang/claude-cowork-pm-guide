from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import textwrap


@dataclass(frozen=True)
class Inputs:
    task: str
    audience: str
    output_language: str
    out_dir: Path


def _now_local() -> str:
    return datetime.now().astimezone().strftime("%Y-%m-%d %H:%M %Z")


def _md_h1(title: str) -> str:
    return f"# {title}\n"


def _wrap(s: str) -> str:
    return textwrap.dedent(s).strip() + "\n"


def _agent_vs_workflow_decision(task: str) -> str:
    return _wrap(
        f"""
        {_md_h1("01｜Agent vs Workflow：决策卡")}

        ## 你的任务
        {task}

        ## 快速判断（先从 Workflow 开始）
        - 你能否把任务拆成有限的 5–9 步，并且每步有明确输入/输出/验收？
          - 能：优先 Workflow（更快、更便宜、更可控）
          - 不能：考虑 Agent（步骤不确定/需要探索/需要动态改策略）

        ## 什么时候“必须用 Agent”
        - 问题开放式，研究路径强依赖新发现，无法预先写死步骤
        - 需要在执行中反复判断“下一步做什么/查哪里/是否停止”
        - 需要工具使用与自我纠错循环（plan → act → check → revise）

        ## 什么时候“不要上 Agent”
        - 只是写作/整理/格式化（Workflow 足够）
        - 结果必须稳定一致（Workflow 更稳）
        - 预算/时延敏感（Workflow 更省）

        ## 本次建议
        - 默认：先做 Workflow 版本（可验收、可复用）
        - 升级：当你发现步骤常常“走不下去/要临场换路”，再引入 Agent 或多智能体
        """
    )


def _workflow_plan(task: str, audience: str, output_language: str) -> str:
    return _wrap(
        f"""
        {_md_h1("02｜Workflow 方案：Decompose → Equip → Compose")}

        生成时间：{_now_local()}

        ## 任务
        {task}

        ## 目标受众
        {audience}

        ## 输出语言
        {output_language}

        ## Decompose（拆解 5–9 步）
        1. 输入整理：收集并确认输入材料（文件/链接/原始记录）
        2. 目标澄清：把“要什么”写成可验收的交付物清单
        3. 信息抽取：把原始材料抽成结构化要点/表格
        4. 归纳与聚类：主题/问题/机会点聚合
        5. 草稿生成：生成第 1 版交付物
        6. 质检与校对：一致性、遗漏、引用、风险与边界
        7. 迭代修订：按反馈修订至可交付版本
        8. 输出落盘：写入文件并生成变更摘要（Changelog）

        ## Equip（每一步的“最小技能/工具”）
        - Step 1 输入整理：清单模板 + 缺失信息提问模板
        - Step 2 目标澄清：验收标准清单（Definition of Done）
        - Step 3 信息抽取：固定输出 schema（表头/字段）
        - Step 4 归纳聚类：主题命名口径 + 证据引用规则
        - Step 5 草稿生成：交付物模板（PRD/报告/邮件/周报任选）
        - Step 6 质检校对：多视角 Reviewer（工程/风控/老板/用户）
        - Step 7 迭代修订：差异对比（改了什么/为什么）
        - Step 8 输出落盘：文件命名规范 + Changelog 模板

        ## Compose（串联与人类拍板点）
        - 人类拍板点 1：目标与边界（做什么/不做什么）
        - 人类拍板点 2：优先级取舍
        - 人类拍板点 3：风险与口径（对外能不能说）
        """
    )


def _context_strategy(task: str) -> str:
    return _wrap(
        f"""
        {_md_h1("03｜上下文工程：Write / Select / Compress / Isolate")}

        ## 任务
        {task}

        ## Write（写入：把关键状态写到“外部记忆”）
        - 写入：关键决策、术语表、约束边界、待验证清单、当前进度
        - 形式：`memory.md` / `NOTES.md` / 项目规则文件（AGENTS.md/CLAUDE.md）

        ## Select（选择：只加载相关信息）
        - 资料选择：只放“本次要用”的资料，不要把所有资料全塞进上下文
        - 工具选择：只启用必要工具/技能（最小可行工具集）

        ## Compress（压缩：摘要/修剪）
        - 压缩对象：旧的工具输出、重复材料、长对话中的中间过程
        - 压缩保留：架构决策、未解决问题、关键证据、实现细节

        ## Isolate（隔离：把复杂度拆开）
        - 多线程/多智能体：把子任务隔离成独立上下文
        - 沙箱：把中间处理放到沙箱/本地脚本，不把中间结果全回填
        """
    )


def _claude_md_template(inputs: Inputs) -> str:
    return _wrap(
        f"""
        {_md_h1("CLAUDE.md（项目规则模板）")}

        ## 目标
        - 任务：{inputs.task}
        - 输出语言：{inputs.output_language}
        - 受众：{inputs.audience}

        ## 输出规范（必须遵守）
        - 优先输出最终可交付物，其次再解释
        - 结论必须可验收：给清单/表格/步骤，不给空泛段落
        - 遇到关键不确定信息时先提问，不要猜

        ## 边界与禁止项
        - 不输出敏感信息（密钥、个人隐私、内部账号）
        - 不做不可逆操作前，必须请求确认

        ## 引用与证据
        - 所有关键结论都给出处（链接/文件名/截图说明）

        ## 验收标准（Definition of Done）
        - 交付物文件齐全且命名符合规范
        - 结论有证据，风险有边界，下一步可执行
        """
    )


def _agents_md_template(inputs: Inputs) -> str:
    return _wrap(
        f"""
        {_md_h1("AGENTS.md（角色分工模板）")}

        ## Lead（规划与总控）
        - 职责：拆解任务、分配子任务、整合结果、暴露风险与待澄清问题
        - 必须输出：计划（按步骤/按文件）、人类拍板点、验收清单

        ## Researcher（研究与证据）
        - 职责：找资料、提炼证据、整理引用链接与关键摘录
        - 必须输出：证据列表（每条结论对应至少 1 个来源）

        ## Writer（成稿与结构）
        - 职责：把信息变成可读可交付的文档结构
        - 必须输出：目录、要点、最终稿

        ## Reviewer（质检）
        - 职责：挑错与补漏：一致性、遗漏、风险、边界、可执行性
        - 必须输出：问题清单 + 修改建议（按优先级）

        ## 本次任务
        {inputs.task}
        """
    )


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def generate(inputs: Inputs) -> list[Path]:
    outputs: list[tuple[str, str]] = [
        ("01-decision.md", _agent_vs_workflow_decision(inputs.task)),
        ("02-workflow-plan.md", _workflow_plan(inputs.task, inputs.audience, inputs.output_language)),
        ("03-context-strategy.md", _context_strategy(inputs.task)),
        ("CLAUDE.md", _claude_md_template(inputs)),
        ("AGENTS.md", _agents_md_template(inputs)),
    ]
    written: list[Path] = []
    for name, content in outputs:
        p = inputs.out_dir / name
        _write(p, content)
        written.append(p)
    return written


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="agent_workflow_generator",
        description="Generate offline-friendly workflow/agent/context templates from a task description.",
    )
    parser.add_argument("--task", required=False, help="Task description. If omitted, reads from stdin.")
    parser.add_argument("--audience", default="自己/团队内部", help="Target audience of the deliverable.")
    parser.add_argument("--lang", default="中文", help="Output language.")
    parser.add_argument("--out", default=".", help="Output directory.")
    args = parser.parse_args()

    task = (args.task or "").strip()
    if not task:
        task = (input().strip() if not task else task)
    if not task:
        raise SystemExit("task is required via --task or stdin")

    inputs = Inputs(
        task=task,
        audience=str(args.audience).strip() or "自己/团队内部",
        output_language=str(args.lang).strip() or "中文",
        out_dir=Path(args.out).expanduser().resolve(),
    )
    written = generate(inputs)
    print("Generated files:")
    for p in written:
        print(f"- {p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

