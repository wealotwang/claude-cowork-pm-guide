#!/usr/bin/env python3
"""
LLM as a Judge 小实验：审核 checker.py 给出的判断理由是否站得住脚。

背景：现在的评测方法（run_dataset_cli.py）只衡量"判断结果对不对"（召回率/精准率），
不衡量"给出的理由（rationale）本身靠不靠谱"。这个脚本补一个新维度——找另一个LLM当"审核官"，
去审已经跑出来的 命中结果/hits_*.json 里每条 case 的 actual_rationale：

  1. 忠实度（faithful）：这条理由里提到的内容，是不是原始 text 里真实写了的？
     有没有编造原文没提到的信息、或者过度脑补？
  2. 逻辑自洽（logic_supports_verdict）：就算引用的都是原文真事，这些内容能不能
     真的支撑起 actual_action 这个结论？

不改动任何现有demo代码和 命中结果/ 里已有的文件，是一个独立的、只读的补充分析脚本。

用法：
    export DEEPSEEK_API_KEY="你自己的 key"   # 跟 checker.py 用的是同一套凭证读取逻辑
    python3 llm_judge_eval.py                          # 默认：用最新一份 hits_*.json，抽样约18条
    python3 llm_judge_eval.py --file hits_20260810_184404.json --sample 20
"""

import argparse
import glob
import json
import os
import random
import sys
import time

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PRODUCT_ROOT = os.path.dirname(SCRIPT_DIR)  # 05-产品原型/
HITS_DIR = os.path.join(PRODUCT_ROOT, "命中结果")
OUT_DIR = SCRIPT_DIR  # 结果就存在这个实验文件夹自己底下，不混进正式的 命中结果/

sys.path.insert(0, os.path.join(PRODUCT_ROOT, "规则执行"))
import checker  # noqa: E402  复用同一套 key 读取 / API 调用 / 重试逻辑，不重新造轮子


JUDGE_SYSTEM_PROMPT = """你是一名严格的审核官，专门审查另一个AI（"合规检查AI"）给出的判断理由是否站得住脚。
你不需要重新判断这段拜访记录该不该被拦截——那件事合规检查AI已经做过了。你只审查它给出的
理由（rationale）本身有没有问题。

请审查两件事：
1. faithful（忠实度）：理由里提到的内容，是不是原始文本里真实写了的？有没有编造原文没提到的信息、
   或者做了原文支撑不了的过度推断？
2. logic_supports_verdict（逻辑自洽）：就算引用的都是原文真事，这些内容能不能真的支撑起
   最终给出的判断（action/risk_level）？还是牵强附会、理由和结论对不上？

只输出一个JSON对象，不要输出任何其他文字，格式：
{
  "faithful": true 或 false,
  "faithful_issue": "如果faithful=false，一句话说明编造/脑补了什么；否则留空字符串",
  "logic_supports_verdict": true 或 false,
  "logic_issue": "如果logic_supports_verdict=false，一句话说明理由和结论哪里对不上；否则留空字符串",
  "judge_note": "一句话总评，不超过40字"
}
"""


def build_judge_user_message(case):
    return (
        f"【原始拜访记录文本】\n{case['text']}\n\n"
        f"【合规检查AI的判断】action={case['actual_action']}，risk_level={case.get('actual_risk_level', '')}\n\n"
        f"【合规检查AI给出的理由】{case['actual_rationale']}\n\n"
        "请按系统提示的要求审查这条理由，只输出JSON。"
    )


def call_judge(case, runtime):
    """复用 checker.py 的底层 HTTP 调用函数，只是换一套 system prompt。"""
    user_message = build_judge_user_message(case)
    call_fn = checker.call_deepseek if runtime["provider"] == "deepseek" else checker.call_anthropic
    last_error = None
    for attempt in range(2):  # 跟 checker.llm_classify 一样，失败重试一次
        try:
            return call_fn(user_message, JUDGE_SYSTEM_PROMPT, runtime)
        except RuntimeError as e:
            last_error = e
            time.sleep(1)
    raise RuntimeError(f"judge调用重试一次后仍失败：{last_error}")


def latest_hits_file():
    files = sorted(glob.glob(os.path.join(HITS_DIR, "hits_*.json")))
    if not files:
        raise SystemExit(f"没在 {HITS_DIR} 找到任何 hits_*.json，先跑一次评测再来做这个实验。")
    return files[-1]


def load_results(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["results"], data.get("run_id", os.path.basename(path))


def stratified_sample(results, sample_size, seed=42):
    """抽样策略：优先把所有"判断出错"的case全部纳入（这些最值得审），
    剩下的名额从"判断正确的高危case"和"判断正确的正常case"里各抽一半，尽量覆盖不同情况。"""
    rng = random.Random(seed)
    wrong = [r for r in results if r.get("exact_action") is False]
    correct_critical = [r for r in results if r.get("exact_action") is True and r.get("risk_level") == "Critical"]
    correct_low = [r for r in results if r.get("exact_action") is True and r.get("risk_level") != "Critical"]

    remaining = max(sample_size - len(wrong), 0)
    half = remaining // 2
    picked_critical = rng.sample(correct_critical, min(half, len(correct_critical)))
    picked_low = rng.sample(correct_low, min(remaining - len(picked_critical), len(correct_low)))

    sample = wrong + picked_critical + picked_low
    return sample


def main():
    parser = argparse.ArgumentParser(description="LLM as a judge：审核已有跑分结果里的判断理由质量")
    parser.add_argument("--file", help="要审的 hits_*.json 文件名（不填则用最新一份）")
    parser.add_argument("--sample", type=int, default=18, help="抽样条数，默认18")
    args = parser.parse_args()

    if not checker.has_llm_credentials():
        print("没有找到可用的 LLM key，跟跑正式评测一样，先配置 DEEPSEEK_API_KEY 再运行本脚本。")
        sys.exit(1)

    hits_path = os.path.join(HITS_DIR, args.file) if args.file else latest_hits_file()
    if not os.path.isfile(hits_path):
        raise SystemExit(f"找不到文件：{hits_path}")

    results, run_id = load_results(hits_path)
    sample = stratified_sample(results, args.sample)
    runtime = checker.get_llm_runtime()

    print(f"审的是：{os.path.basename(hits_path)}（run_id={run_id}）")
    print(f"抽样 {len(sample)} 条（judge用的是 {checker.describe_llm_runtime()}）\n")

    judged = []
    flagged = []
    for i, case in enumerate(sample, 1):
        print(f"[{i}/{len(sample)}] 审 {case['id']} ...", end=" ", flush=True)
        try:
            verdict = call_judge(case, runtime)
        except RuntimeError as e:
            print(f"跳过（{e}）")
            continue
        record = {
            "id": case["id"],
            "text": case["text"],
            "actual_action": case["actual_action"],
            "actual_rationale": case["actual_rationale"],
            "exact_action": case.get("exact_action"),
            "judge": verdict,
        }
        judged.append(record)
        ok = verdict.get("faithful", False) and verdict.get("logic_supports_verdict", False)
        if not ok:
            flagged.append(record)
            print(f"⚠️ 被标记 —— {verdict.get('judge_note', '')}")
        else:
            print("通过")

    faithful_count = sum(1 for r in judged if r["judge"].get("faithful"))
    logic_count = sum(1 for r in judged if r["judge"].get("logic_supports_verdict"))
    total = len(judged)

    print("\n" + "=" * 50)
    print(f"共审 {total} 条")
    if total:
        print(f"忠实度通过：{faithful_count}/{total}（{faithful_count/total:.0%}）")
        print(f"逻辑自洽通过：{logic_count}/{total}（{logic_count/total:.0%}）")
    print(f"被标记（两项任一不过）：{len(flagged)} 条")
    for r in flagged:
        print(f"  - {r['id']}：{r['judge'].get('judge_note', '')}")

    timestamp = time.strftime("%Y%m%d_%H%M%S")
    out_path = os.path.join(OUT_DIR, f"judge_results_{timestamp}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({
            "source_file": os.path.basename(hits_path),
            "source_run_id": run_id,
            "sample_size": len(sample),
            "judge_model": checker.describe_llm_runtime(),
            "faithful_rate": faithful_count / total if total else None,
            "logic_rate": logic_count / total if total else None,
            "flagged_count": len(flagged),
            "results": judged,
        }, f, ensure_ascii=False, indent=2)
    print(f"\n完整结果已存：{out_path}")


if __name__ == "__main__":
    main()
