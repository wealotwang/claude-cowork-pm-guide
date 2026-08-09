#!/usr/bin/env python3
"""
用完整 50 条 CSV benchmark（或任意外部 CSV，如 Day07 的 300 case）跑一次当前 demo，
并输出更贴近 Release Gate 的结果。

迁移说明：从 03-学习成果/demo/run_eval_csv.py 迁移而来（原文件已归档，标注指向这里）。
评测逻辑没变，两处更新：CSV读取改为复用 datasets.py（统一列名兼容，网页和CLI共用同一套
解析），默认数据集改为指向 ../数据集/ 下产品自带的那份。

默认数据集：
    ../数据集/csv50-医药CRM合规评测集.csv

用法：
    export DEEPSEEK_API_KEY="你的key"
    python3 run_eval_csv.py
    python3 run_eval_csv.py ../数据集/200case-医药CRM合规压力测试集.csv --workers 4 --progress-every 20
"""

import argparse
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict

import datasets as ds
from checker import classify, describe_llm_runtime, has_llm_credentials, load_config

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# 默认数据集改成产品自带的那份（数据集/ 文件夹是所有评测数据的统一入口），
# 不再指向仓库根目录的散落文件——换台机器就不用改代码了。
DEFAULT_CSV_PATH = os.path.join(
    os.path.dirname(SCRIPT_DIR), "数据集", "csv50-医药CRM合规评测集.csv"
)

ACTION_MAP = {
    "Reject (一票否决)": "Reject",
    "Reject": "Reject",
    "Block (数据阻断)": "Block",
    "Block": "Block",
    "Warning (打回修改)": "Warning",
    "Warning": "Warning",
    "Notice (合规提醒)": "Notice",
    "Notice": "Notice",
    "Pass (通过并提示)": "Pass",
    "Pass (完全通过)": "Pass",
    "Pass (Notice)": "Pass",
    "Pass": "Pass",
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


def normalize_category_id(category_id):
    raw = str(category_id or "").strip()
    if not raw:
        return raw
    if raw.isdigit():
        return raw.zfill(2)
    return raw


def normalize_expected_action(action):
    raw = str(action or "").strip()
    if not raw:
        return None
    return ACTION_MAP.get(raw, raw)


def load_cases(csv_path, config=None):
    """读CSV。列名归一化统一交给 datasets.py 处理，这样CLI和网页用的是同一套解析逻辑，
    不会出现"网页能读这个CSV、命令行读不了"的情况。"""
    rows, issues = ds.load_csv_cases(csv_path, config)
    for issue in issues:
        print(f"[数据质量] {issue['case_id']}: {issue['problem']}", file=sys.stderr)
    return rows


def evaluate_one(case, config):
    try:
        actual = classify(case["text"], config)
        return {
            **case,
            "actual_category": normalize_category_id(actual["matched_category"]),
            "actual_action": actual["action"],
            "actual_risk_level": actual["risk_level"],
            "actual_rationale": actual.get("rationale", ""),
            # 有些数据集（比如简化过的300case v2）不带分类标注，expected_category是None，
            # 这种情况下"分类判没判对"这件事根本无从谈起，用None表示"这个维度不参与评测"，
            # 不能算False——False意味着"判错了"，但事实是我们压根没有标准答案可比对。
            "exact_category": (
                normalize_category_id(actual["matched_category"]) == case["expected_category"]
                if case["expected_category"] is not None
                else None
            ),
            "exact_action": (
                normalize_action_for_diagnostic(actual["action"])
                == normalize_action_for_diagnostic(case["expected_action"])
                if case["expected_action"] is not None
                else None
            ),
            "status": "OK",
        }
    except RuntimeError as e:
        return {
            **case,
            "actual_category": None,
            "actual_action": None,
            "actual_risk_level": None,
            "actual_rationale": "",
            "exact_category": False if case["expected_category"] is not None else None,
            "exact_action": None,
            "status": f"ERROR: {e}",
        }


def evaluate(csv_path, max_workers=1, progress_every=0, results_out=None):
    if not has_llm_credentials():
        raise RuntimeError(
            "没有找到可用的 LLM key。请先在你自己的终端里设置：\n"
            '    export DEEPSEEK_API_KEY="你的key"\n'
            "再重新运行。"
        )

    config = load_config()
    cases = load_cases(csv_path, config)
    indexed_results = [None] * len(cases)
    results_fp = open(results_out, "w", encoding="utf-8") if results_out else None
    completed = 0
    try:
        if max_workers <= 1:
            for idx, case in enumerate(cases):
                result = evaluate_one(case, config)
                indexed_results[idx] = result
                completed += 1
                if results_fp:
                    results_fp.write(json.dumps(result, ensure_ascii=False) + "\n")
                    results_fp.flush()
                if progress_every and completed % progress_every == 0:
                    print(f"[progress] {completed}/{len(cases)}", file=sys.stderr, flush=True)
        else:
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_idx = {
                    executor.submit(evaluate_one, case, config): idx for idx, case in enumerate(cases)
                }
                for future in as_completed(future_to_idx):
                    idx = future_to_idx[future]
                    result = future.result()
                    indexed_results[idx] = result
                    completed += 1
                    if results_fp:
                        results_fp.write(json.dumps(result, ensure_ascii=False) + "\n")
                        results_fp.flush()
                    if progress_every and completed % progress_every == 0:
                        print(f"[progress] {completed}/{len(cases)}", file=sys.stderr, flush=True)
    finally:
        if results_fp:
            results_fp.close()
    return indexed_results


def build_summary(results):
    total = len(results)
    tested = [r for r in results if r["status"] == "OK"]
    errored = [r for r in results if r["status"] != "OK"]
    action_labeled = [r for r in results if r["exact_action"] is not None]
    exact_action_hits = sum(1 for r in action_labeled if r["exact_action"])
    # 只在"有分类标注"的case里算分类准确率——None表示这条case压根没有标准答案可比对，
    # 不能跟"判错了"混在一起算，不然一个不带分类的数据集会显示成离谱的0%准确率。
    category_labeled = [r for r in results if r["exact_category"] is not None]
    exact_category_hits = sum(1 for r in category_labeled if r["exact_category"])

    critical = [r for r in results if r["risk_level"] in HIGH_RISK_LEVELS]
    critical_caught = [r for r in critical if r["actual_risk_level"] in HIGH_RISK_LEVELS]
    critical_category_labeled = [r for r in critical if r["exact_category"] is not None]
    critical_exact_category = [r for r in critical_category_labeled if r["exact_category"]]

    expected_medium = [r for r in results if r["risk_level"] in MEDIUM_RISK_LEVELS]
    predicted_medium = [r for r in tested if r["actual_risk_level"] in MEDIUM_RISK_LEVELS]
    true_medium_pred = [r for r in predicted_medium if r["risk_level"] in MEDIUM_RISK_LEVELS]

    expected_low = [r for r in results if r["risk_level"] in LOW_RISK_LEVELS]
    low_false_positives = [r for r in expected_low if r["actual_risk_level"] not in LOW_RISK_LEVELS]

    per_category = defaultdict(lambda: {"total": 0, "exact_category": 0, "exact_action": 0, "action_labeled": 0})
    for r in results:
        if r["expected_category"] is None:
            continue  # 没有分类标注的case不进这张按类别拆解的表，不然会多出一个假的"None"分类
        stat = per_category[r["expected_category"]]
        stat["total"] += 1
        stat["exact_category"] += int(bool(r["exact_category"]))
        if r["exact_action"] is not None:
            stat["action_labeled"] += 1
            stat["exact_action"] += int(r["exact_action"])

    return {
        "model": describe_llm_runtime(),
        "total": total,
        "tested": len(tested),
        "errored": len(errored),
        "overall_exact_action_accuracy": exact_action_hits / len(action_labeled) if action_labeled else None,
        "overall_exact_category_accuracy": (
            exact_category_hits / len(category_labeled) if category_labeled else None
        ),
        "critical_recall_release_gate": len(critical_caught) / len(critical) if critical else 0,
        "critical_exact_category_recall_diagnostic": (
            len(critical_exact_category) / len(critical_category_labeled) if critical_category_labeled else None
        ),
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
        "has_category_labels": len(category_labeled) > 0,
        "per_category": {
            cat: {
                "total": stat["total"],
                "exact_category_accuracy": stat["exact_category"] / stat["total"],
                "exact_action_accuracy": (
                    stat["exact_action"] / stat["action_labeled"] if stat["action_labeled"] else None
                ),
            }
            for cat, stat in sorted(per_category.items())
        },
        "action_failures": [r for r in results if r["exact_action"] is False],
        "category_failures": [r for r in results if r["exact_category"] is False],
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
    print("Diagnostic 指标：")
    if summary["overall_exact_category_accuracy"] is not None:
        print(f"- Overall Exact Category Accuracy：{summary['overall_exact_category_accuracy']:.0%}")
        print(f"- Critical Exact Category Recall：{summary['critical_exact_category_recall_diagnostic']:.0%}")
    else:
        print("- Overall/Critical Exact Category Accuracy：当前数据集没有分类标注，不纳入评测")
    print(f"- Medium Recall：{summary['medium_recall_diagnostic']:.0%}")
    if summary["overall_exact_action_accuracy"] is not None:
        print(f"- Overall Exact Action Accuracy：{summary['overall_exact_action_accuracy']:.0%}")
    else:
        print("- Overall Exact Action Accuracy：当前数据集未提供或未使用预期动作，不纳入评测")
    if not summary["per_category"]:
        print("\n（当前数据集没有分类标注，跳过按类别拆解）")
    else:
        print("\n按类别结果：")
        for cat, stat in summary["per_category"].items():
            parts = [
                f"- {cat}: total={stat['total']}",
                f"exact_category_accuracy={stat['exact_category_accuracy']:.0%}",
            ]
            if stat["exact_action_accuracy"] is not None:
                parts.append(f"exact_action_accuracy={stat['exact_action_accuracy']:.0%}")
            print(", ".join(parts))
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


def parse_args():
    parser = argparse.ArgumentParser(description="运行 CSV 合规评测")
    parser.add_argument("csv_path", nargs="?", default=DEFAULT_CSV_PATH)
    parser.add_argument("--workers", type=int, default=1, help="并发 worker 数，默认 1")
    parser.add_argument("--progress-every", type=int, default=0, help="每处理 N 条打印一次进度")
    parser.add_argument("--results-out", default=None, help="逐条结果输出到 jsonl 文件")
    return parser.parse_args()


def main():
    args = parse_args()
    results = evaluate(
        args.csv_path,
        max_workers=max(1, args.workers),
        progress_every=max(0, args.progress_every),
        results_out=args.results_out,
    )
    summary = build_summary(results)
    print_summary(args.csv_path, summary)


if __name__ == "__main__":
    main()
