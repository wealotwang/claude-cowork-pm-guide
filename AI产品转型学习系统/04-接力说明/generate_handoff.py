#!/usr/bin/env python3
"""
自动生成"承上启下"交接摘要的骨架，减少每次交接时人/agent重读所有文件的成本。

参考思路来自 GitHub 上 softaworks/agent-toolkit 的 session-handoff skill：
不要每次都凭记忆手写一份完整总结，而是让机器先把"客观事实"（改了哪些文件、
多少个commit）自动算出来，人/agent只需要在这份骨架上补两件机器算不出来的事：
关键决策是什么、为什么这么决策、接下来该做什么。

原理：
- 上次交接记录的 commit hash 存在 00-当前进度与接力说明.md 顶部的
  <!-- last_handoff_commit: xxxxx --> 标记里
- 本脚本对比这个 hash 到当前 HEAD 之间的 git log 和 git diff --stat
- 自动生成"自上次交接以来改了什么"这一段
- 跑完脚本后，把输出里 [TODO] 标的两小段（关键决策/下一步）补进
  00-当前进度与接力说明.md 的"最新交接摘要"部分，然后把顶部的
  last_handoff_commit 标记更新成当前 HEAD

用法：
    cd "/Users/li/ai pm learning/claude-cowork-pm-guide"
    python3 "AI产品转型学习系统/04-接力说明/generate_handoff.py"
"""

import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]  # .../claude-cowork-pm-guide
HANDOFF_PATH = Path(__file__).resolve().parent / "00-当前进度与接力说明.md"
MARKER_RE = re.compile(r"<!--\s*last_handoff_commit:\s*([0-9a-f]+)\s*-->")


def run_git(args):
    result = subprocess.run(
        ["git", "-C", str(REPO_ROOT)] + args, capture_output=True, text=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} 失败：{result.stderr.strip()}")
    return result.stdout.strip()


def get_last_handoff_commit():
    if not HANDOFF_PATH.exists():
        return None
    text = HANDOFF_PATH.read_text(encoding="utf-8")
    m = MARKER_RE.search(text)
    return m.group(1) if m else None


def main():
    try:
        current_head = run_git(["rev-parse", "HEAD"])
    except RuntimeError as e:
        print(f"错误：{e}")
        sys.exit(1)

    last_commit = get_last_handoff_commit()

    print("=" * 60)
    print("交接摘要骨架（自动生成，只需要补充标了 [TODO] 的部分）")
    print("=" * 60)
    print(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"当前 HEAD：{current_head[:10]}")

    if not last_commit:
        print(
            "\n⚠️  没有在交接文档里找到 last_handoff_commit 标记（可能是第一次用这个脚本）。"
        )
        print(
            f"请在 00-当前进度与接力说明.md 最上面手动加一行：\n"
            f"<!-- last_handoff_commit: {current_head} -->\n"
            f"下次再跑这个脚本，就能自动算出这次到下次之间改了什么。"
        )
        sys.exit(0)

    if last_commit == current_head:
        print(
            f"\n✅ 自上次交接（commit {last_commit[:10]}）以来，没有新的 commit。"
            f"当前记录的状态应该还是最新的，不需要重新生成交接摘要。"
        )
        sys.exit(0)

    print(f"\n上次交接记录的 commit：{last_commit[:10]}")

    try:
        log = run_git(["log", "--oneline", f"{last_commit}..{current_head}"])
        diff_stat = run_git(["diff", "--stat", last_commit, current_head])
    except RuntimeError as e:
        print(f"\n⚠️  {e}")
        print(
            "（常见原因：上次记录的 commit hash 在当前分支历史里找不到，"
            "比如 rebase 过或者标记写错了。检查一下标记是否正确。）"
        )
        sys.exit(1)

    commit_lines = log.splitlines()
    print(f"\n自那以后一共有 {len(commit_lines)} 个新 commit：")
    for line in commit_lines:
        print(f"  - {line}")

    print(f"\n改动的文件（git diff --stat）：")
    print(diff_stat if diff_stat else "  (无文件级别改动)")

    print("\n" + "=" * 60)
    print("[TODO] 请在这份自动摘要基础上，只需要补充这两小段：")
    print("  1. 关键决策：这些改动里有没有做过什么值得记录的产品/架构判断？为什么？")
    print("  2. 下一步：接下来最该做的 1-3 件事是什么？")
    print("=" * 60)
    print(
        f"\n写完后，记得把 00-当前进度与接力说明.md 顶部的标记更新成：\n"
        f"<!-- last_handoff_commit: {current_head} -->"
    )


if __name__ == "__main__":
    main()
