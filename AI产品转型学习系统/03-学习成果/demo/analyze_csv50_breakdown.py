#!/usr/bin/env python3
"""
基于当前 checker 配置，对 CSV50 benchmark 生成结果拆解视图。

【已归档，功能已被取代】这个脚本当初解决的问题是"把已实现类别和未实现类别的结果拆开看"，
现在这件事由 ../../05-产品原型/分析报告/report.py 做得更完整（失败根因分三桶、范围内真实
准确率、按类别拆解、跟上次跑分对比、可导出HTML），而且是从命中结果自动生成、不用重新跑一遍
评测。所以这个脚本没有迁移到 05-产品原型，保留在这里只作为 Day07 分析思路的历史记录。

注意：
- 不修改原始数据集 `medical_crm_compliance_eval_dataset_cn.csv`
- 只输出派生分析结果，供 Day07 复盘使用
"""

import csv
import os

from checker import classify, load_config


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "..", ".."))
CSV_PATH = os.path.join(REPO_ROOT, "medical_crm_compliance_eval_dataset_cn.csv")
IMPLEMENTED_CATEGORIES = {"01", "03", "05", "06", "07", "10"}


def load_rows():
    with open(CSV_PATH, "r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def main():
    config = load_config()
    rows = load_rows()

    implemented_success = []
    implemented_failures = []
    unimplemented_success = []
    unimplemented_failures = []
    errors = []

    for row in rows:
        expected = row["分类ID"]
        bucket = "implemented" if expected in IMPLEMENTED_CATEGORIES else "unimplemented"

        try:
            result = classify(row["CRM拜访记录文本"], config)
            item = {
                "id": row["Case ID"],
                "expected": expected,
                "actual": result["matched_category"],
                "matched_by": result.get("matched_by", ""),
                "risk": row["风险等级"],
                "text": row["CRM拜访记录文本"],
                "rationale": result.get("rationale", ""),
            }
            if result["matched_category"] == expected:
                if bucket == "implemented":
                    implemented_success.append(item)
                else:
                    unimplemented_success.append(item)
            else:
                if bucket == "implemented":
                    implemented_failures.append(item)
                else:
                    unimplemented_failures.append(item)
        except Exception as e:
            errors.append(
                {
                    "id": row["Case ID"],
                    "expected": expected,
                    "bucket": bucket,
                    "risk": row["风险等级"],
                    "text": row["CRM拜访记录文本"],
                    "error": str(e),
                }
            )

    print("=== CSV50 Breakdown ===")
    print(f"原始 benchmark: {CSV_PATH}")
    print("说明：上面是 raw data；下面全部是本次运行派生出的 analysis result。")
    print()
    print(f"已实现类别命中正确: {len(implemented_success)}")
    print(f"已实现类别失败样例: {len(implemented_failures)}")
    for item in implemented_failures:
        print(
            f"IMP_FAIL {item['id']} expected={item['expected']} actual={item['actual']} "
            f"matched_by={item['matched_by']} text={item['text']}"
        )
    print()
    print(f"未实现类别命中正确: {len(unimplemented_success)}")
    print(f"未实现类别失败样例: {len(unimplemented_failures)}")
    for item in unimplemented_failures:
        print(
            f"UNIMP_FAIL {item['id']} expected={item['expected']} actual={item['actual']} "
            f"matched_by={item['matched_by']} text={item['text']}"
        )
    print()
    print(f"运行报错: {len(errors)}")
    for item in errors:
        print(
            f"ERROR {item['id']} expected={item['expected']} bucket={item['bucket']} "
            f"error={item['error']} text={item['text']}"
        )


if __name__ == "__main__":
    main()
