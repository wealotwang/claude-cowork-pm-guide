#!/usr/bin/env python3
"""
用完整 50 条 CSV benchmark 跑一次当前 demo，并输出更贴近 Release Gate 的结果。

默认数据集：
    /Users/li/ai pm learning/claude-cowork-pm-guide/medical_crm_compliance_eval_dataset_cn.csv

用法：
    export DEEPSEEK_API_KEY="你的key"
    python3 run_eval_csv.py
"""

import csv
import json
import os
import sys
from collections import defaultdict

from checker import classify, describe_llm_runtime, has_llm_credentials, load_config

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CSV_PATH = "/Users/li/ai pm learning/claude-cowork-pm-guide/medical_crm_compliance_eval_dataset_cn.csv"

ACTION_MAP = {
    "Reject (一票否决)": "Reject",
    "Block (数据阻断)": "Block",
    "Warning (打回修改)": "Warning",
    "Notice (合规提醒)": "Notice",
    "Pass (通过并提示)": "Pass",
    "Pass (完全通过)": "Pass",
}

HIGH_RISK_LEVELS = {"Critical"}
MEDIUM_RISK_LEVELS = {"Medium"}
LOW_RISK_LEVELS = {"Low"}


def normalize_action_for_diagnostic(action):
    if action in ("Reject", "Block"):
        return "Reject"
    if action in ("Warning", "Notice", "PassWithNotice"):
        return "PassWithNotice"
    if action == "Pass":
        return "Pass"
    return action


def load_cases(csv_path):
    rows = []
    with open(csv_path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(
                {
                    "id": row["Case ID"],
                    "expected_category": row["分类ID"],
                    "category_name": row["风险分类"],
                    "text": row["CRM拜访记录文本"],
                    "risk_level": row["风险等级"],
                    "expected_action": ACTION_MAP[row["预期处置动作"]],
                    "rationale": row["合规判定依据"],
                }
            )
    return rows


def evaluate(csv_path):
    if not has_llm_credentials():
        raise RuntimeError(
            "没有找到可用的 LLM key。请先在你自己的终端里设置：\n"
            '    export DEEPSEEK_API_KEY="你的key"\n'
            "再重新运行。"
        )

    config = load_config()
    cases = load_cases(csv_path)
    results = []
    for case in cases:
        try:
            actual = classify(case["text"], config)
            results.append(
                {
                    **case,
                    "actual_category": actual["matched_category"],
                    "actual_action": actual["action"],
                    "actual_risk_level": actual["risk_level"],
                    "actual_rationale": actual.get("rationale", ""),
                    "exact_category": actual["matched_category"] == case["expected_category"],
                    "exact_action": normalize_action_for_diagnostic(actual["action"])
                    == normalize_action_for_diagnostic(case["expected_action"]),
                    "status": "OK",
                }
            )
        except RuntimeError as e:
            results.append(
                {
                    **case,
                    "actual_category": None,
                    "actual_action": None,
                    "actual_risk_level": None,
                    "actual_rationale": "",
                    "exact_category": False,
                    "exact_action": False,
                    "status": f"ERROR: {e}",
                }
            )
    return results


def build_summary(results):
    total = len(results)
    tested = [r for r in results if r["status"] == "OK"]
    errored = [r for r in results if r["status"] != "OK"]
    exact_action_hits = sum(1 for r in results if r["exact_action"])
    exact_category_hits = sum(1 for r in results if r["exact_category"])

    critical = [r for r in results if r["risk_level"] in HIGH_RISK_LEVELS]
    critical_caught = [r for r in critical if r["actual_risk_level"] in HIGH_RISK_LEVELS]
    critical_exact_category = [r for r in critical if r["exact_category"]]

    expected_medium = [r for r in results if r["risk_level"] in MEDIUM_RISK_LEVELS]
    predicted_medium = [r for r in tested if r["actual_risk_level"] in MEDIUM_RISK_LEVELS]
    true_medium_pred = [r for r in predicted_medium if r["risk_level"] in MEDIUM_RISK_LEVELS]

    expected_low = [r for r in results if r["risk_level"] in LOW_RISK_LEVELS]
    low_false_positives = [r for r in expected_low if r["actual_risk_level"] not in LOW_RISK_LEVELS]

    per_category = defaultdict(lambda: {"total": 0, "exact_category": 0, "exact_action": 0})
    for r in results:
        stat = per_category[r["expected_category"]]
        stat["total"] += 1
        stat["exact_category"] += int(r["exact_category"])
        stat["exact_action"] += int(r["exact_action"])

    return {
        "model": describe_llm_runtime(),
        "total": total,
        "tested": len(tested),
        "errored": len(errored),
        "overall_exact_action_accuracy": exact_action_hits / total if total else 0,
        "overall_exact_category_accuracy": exact_category_hits / total if total else 0,
        "critical_recall_release_gate": len(critical_caught) / len(critical) if critical else 0,
        "critical_exact_category_recall_diagnostic": len(critical_exact_category) / len(critical) if critical else 0,
        "medium_precision_release_gate": len(true_medium_pred) / len(predicted_medium) if predicted_medium else 0,
        "medium_recall_diagnostic": (
            sum(1 for r in expected_medium if r["actual_risk_level"] in MEDIUM_RISK_LEVELS) / len(expected_medium)
            if expected_medium
            else 0
        ),
        "low_false_positive_rate_release_gate": len(low_false_positives) / len(expected_low) if expected_low else 0,
        "critical_counts": {"caught": len(critical_caught), "total": len(critical)},
        "medium_precision_counts": {"tp": len(true_medium_pred), "predicted": len(predicted_medium)},
        "low_fp_counts": {"fp": len(low_false_positives), "total": len(expected_low)},
        "per_category": {
            cat: {
                "total": stat["total"],
                "exact_category_accuracy": stat["exact_category"] / stat["total"],
                "exact_action_accuracy": stat["exact_action"] / stat["total"],
            }
            for cat, stat in sorted(per_category.items())
        },
        "action_failures": [r for r in results if not r["exact_action"]],
        "category_failures": [r for r in results if not r["exact_category"]],
        "errors": errored,
    }


def print_summary(csv_path, summary):
    print("=" * 60)
    print("CSV Eval 结果报告")
    print("=" * 60)
    print(f"模型：{summary['model']}")
    print(f"数据集：{csv_path}")
    print(f"总用例数：{summary['total']}（成功跑完 {summary['tested']}，报错 {summary['errored']}）")
    print()
    print(
        "Release Gate 指标："
        f"\n- 高危类(01-05) Recall：{summary['critical_recall_release_gate']:.0%}"
        f"（{summary['critical_counts']['caught']}/{summary['critical_counts']['total']}）"
        f"\n- 中危类(06-09) Precision：{summary['medium_precision_release_gate']:.0%}"
        f"（{summary['medium_precision_counts']['tp']}/{summary['medium_precision_counts']['predicted']}）"
        f"\n- 低危/正常样本误报率：{summary['low_false_positive_rate_release_gate']:.0%}"
        f"（{summary['low_fp_counts']['fp']}/{summary['low_fp_counts']['total']}）"
    )
    print()
    print(
        "Diagnostic 指标："
        f"\n- Overall Exact Action Accuracy：{summary['overall_exact_action_accuracy']:.0%}"
        f"\n- Overall Exact Category Accuracy：{summary['overall_exact_category_accuracy']:.0%}"
        f"\n- Critical Exact Category Recall：{summary['critical_exact_category_recall_diagnostic']:.0%}"
        f"\n- Medium Recall：{summary['medium_recall_diagnostic']:.0%}"
    )
    print("\n按类别结果：")
    for cat, stat in summary["per_category"].items():
        print(
            f"- {cat}: total={stat['total']}, "
            f"exact_category_accuracy={stat['exact_category_accuracy']:.0%}, "
            f"exact_action_accuracy={stat['exact_action_accuracy']:.0%}"
        )
    if summary["action_failures"]:
        print("\n前 12 条 action failure：")
        for row in summary["action_failures"][:12]:
            print(
                f"- [{row['id']}] 期望={row['expected_category']}/{row['expected_action']} "
                f"实际={row['actual_category']}/{row['actual_action']} 文本={row['text'][:40]}"
            )
    if summary["errors"]:
        print("\n报错样例：")
        for row in summary["errors"][:12]:
            print(f"- [{row['id']}] {row['status']} 文本={row['text'][:40]}")


def main():
    csv_path = DEFAULT_CSV_PATH
    if len(sys.argv) > 1:
        csv_path = sys.argv[1]
    results = evaluate(csv_path)
    summary = build_summary(results)
    print_summary(csv_path, summary)


if __name__ == "__main__":
    main()
