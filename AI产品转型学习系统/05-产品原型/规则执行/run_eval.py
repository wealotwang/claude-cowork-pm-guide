#!/usr/bin/env python3
"""
跑 eval_cases.json，输出基线分数报告。

迁移说明：从 03-学习成果/demo/run_eval.py 迁移而来（原文件已归档，标注指向这里），
逻辑未改动，只是和同目录下迁移后的 checker.py / eval_cases.json 放在一起。

分开算两类指标（对应 Day04 的关键判断：高危类和中低危类不能用同一套指标逻辑）：
  - 高危类（01/05）：看 Recall（漏报=0 才算达标）
  - 中低危/合规类（07/10）：看 Precision 和误报率

用法：
    export DEEPSEEK_API_KEY="你自己的 key"
    python3 run_eval.py
"""

import json
import os
import sys

from checker import classify, describe_llm_runtime, has_llm_credentials, load_config

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CASES_PATH = os.path.join(SCRIPT_DIR, "eval_cases.json")


def load_cases():
    with open(CASES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)["cases"]


def run():
    config = load_config()
    cases = load_cases()
    has_api_key = has_llm_credentials()

    results = []
    for case in cases:
        text = case["input"]
        expected_cat = case["expected_category"]

        # Day07 起去掉了 regex 前置层，所有类别（含05）统一走 LLM，都需要 API key
        if not has_api_key:
            results.append({**case, "actual_category": None, "actual_action": None, "status": "SKIPPED(无API key)"})
            continue

        try:
            actual = classify(text, config)
        except RuntimeError as e:
            results.append({**case, "actual_category": None, "actual_action": None, "status": f"ERROR: {e}"})
            continue

        match = actual["matched_category"] == expected_cat
        status = "PASS" if match else "FAIL"
        results.append({
            **case,
            "actual_category": actual["matched_category"],
            "actual_action": actual["action"],
            "actual_rationale": actual.get("rationale", ""),
            "status": status,
        })

    print_report(results, has_api_key)
    return results


def print_report(results, has_api_key):
    print("=" * 60)
    print("Eval 结果报告")
    print("=" * 60)

    if not has_api_key:
        print("⚠️  没有设置可用的 LLM key，Day07 起所有类别都需要 LLM 判断（已去掉 regex 前置层），本轮全部跳过。")
        print("    推荐：export DEEPSEEK_API_KEY=\"你的key\"")
        print("    之后重新运行可以测完整 pipeline。\n")
    else:
        print(f"当前 LLM 运行时：{describe_llm_runtime()}\n")

    total = len(results)
    passed = sum(1 for r in results if r["status"] == "PASS")
    failed = [r for r in results if r["status"] == "FAIL"]
    skipped = [r for r in results if r["status"].startswith("SKIPPED") or r["status"].startswith("ERROR")]
    known_gaps = [r for r in results if r.get("type") == "known_gap"]

    print(f"总用例数：{total}　通过：{passed}　失败：{len(failed)}　跳过/出错：{len(skipped)}\n")

    def tested(rs):
        return [r for r in rs if not r["status"].startswith("SKIPPED") and not r["status"].startswith("ERROR")]

    # 高危类（01/05）Recall：真正的违规case有没有被测出来（漏报）——只统计实际跑过LLM/regex的case
    critical_violations = tested([r for r in results if r.get("expected_category") in ("01", "05") and r.get("type") == "violation"])
    critical_caught = [r for r in critical_violations if r["status"] == "PASS"]
    if critical_violations:
        recall = len(critical_caught) / len(critical_violations)
        print(f"高危类(01/05) Recall：{recall:.0%}　（{len(critical_caught)}/{len(critical_violations)}条已测case中，目标100%，漏一条都要当作release blocker）")
    else:
        print("高危类(01/05) Recall：本轮没有可测的case（可能都因缺API key被跳过）")

    # 中低危/合规类（07/10）：看有没有把边界case误判成违规（False Positive）——同样只统计实际跑过的
    should_pass = tested([r for r in results if r.get("expected_action") == "Pass" and r.get("type") != "known_gap"])
    correctly_passed = [r for r in should_pass if r["status"] == "PASS"]
    if should_pass:
        fp_rate = 1 - (len(correctly_passed) / len(should_pass))
        print(f"应放行case的误报率：{fp_rate:.0%}　（{len(should_pass) - len(correctly_passed)}/{len(should_pass)}条已测case中被错误拦截，目标≤10%）")
    else:
        print("应放行case误报率：本轮没有可测的case（可能都因缺API key被跳过）")

    n_skipped_or_error = len([r for r in results if r["status"].startswith("SKIPPED") or r["status"].startswith("ERROR")])
    if n_skipped_or_error:
        print(f"\n（另有 {n_skipped_or_error} 条因缺 API key 被跳过，未计入上面两个指标——设置好 key 后重跑能看到完整分数）")

    if known_gaps:
        print(f"\n已知局限案例（预期可能miss，不计入上面两个指标）：{len(known_gaps)} 条")
        for g in known_gaps:
            print(f"  - [{g['id']}] {g['input'][:30]}... 原因：{g.get('note', '')}")

    if failed:
        print("\n失败详情：")
        for r in failed:
            print(f"  - [{r['id']}] 输入：{r['input'][:40]}")
            print(f"    期望：{r['expected_category']}/{r['expected_action']}　实际：{r.get('actual_category')}/{r.get('actual_action')}")

    errors = [r for r in results if r["status"].startswith("ERROR")]
    if errors:
        print("\n报错详情（不是分类判断问题，是调用/解析层出了问题）：")
        for r in errors:
            print(f"  - [{r['id']}] 输入：{r['input'][:40]}")
            print(f"    {r['status']}")


if __name__ == "__main__":
    run()
