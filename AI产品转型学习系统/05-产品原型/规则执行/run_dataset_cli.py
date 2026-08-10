#!/usr/bin/env python3
"""
命令行/双击跑一次评测——不用开浏览器，也不用敲一长串命令。

这是"规则执行"模块的另一种入口：网页版（../server.py 的"②规则执行"tab）和这个脚本
调的是同一个 server.run_dataset() 逻辑、写的是同一份 命中结果/hits_*.json。跑完之后
网页的③命中结果、④分析报告两个tab里能看到跟这里打印出来的一样的结果，不会对不上。

用法：
    python3 run_dataset_cli.py                        # 不带参数：交互式选数据集
    python3 run_dataset_cli.py csv50                   # 输入简写，模糊匹配数据集
    python3 run_dataset_cli.py 200case --workers 4     # 直接跑200case，4并发

更省事的方式：双击同目录上一级的 跑评测.command（在Finder里双击，全程不用打开终端、
不用敲任何命令，也不用管key在哪——key会自动从 ../.env 或旧的 .env.deepseek 里读取）。
"""

import argparse
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PRODUCT_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, SCRIPT_DIR)
sys.path.insert(0, os.path.join(PRODUCT_ROOT, "分析报告"))
sys.path.insert(0, PRODUCT_ROOT)  # server.py 在产品根目录，不在这个脚本自己的目录里，之前漏加了这一行会导致 import server 直接崩溃

import checker  # noqa: E402
import datasets as ds  # noqa: E402
import server  # noqa: E402  复用 server.run_dataset()，保证跟网页版结果格式完全一致
import report as report_mod  # noqa: E402


def resolve_dataset_key(user_input, available):
    """允许输一个简写（比如 'csv50'）而不用记住完整的 'file:csv50-医药CRM合规评测集.csv'。"""
    user_input = user_input.strip()
    for d in available:
        if d["key"] == user_input:
            return d["key"]
    matches = [d for d in available
               if user_input.lower() in d["key"].lower() or user_input.lower() in d["label"].lower()]
    if len(matches) == 1:
        return matches[0]["key"]
    if len(matches) > 1:
        print(f"「{user_input}」匹配到多个数据集，请输入更精确的名字：")
        for d in matches:
            print(f"   {d['key']}")
        sys.exit(1)
    return None


def interactive_pick(available):
    print("可用数据集：")
    for i, d in enumerate(available, 1):
        print(f"  {i}. {d['label']}")
    choice = input("输入编号选择要跑的数据集：").strip()
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(available):
            return available[idx]["key"]
    except ValueError:
        pass
    print("没识别出有效选择，退出。")
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="跑一次评测，不用开浏览器")
    parser.add_argument("dataset", nargs="?", help="数据集key或简写，不填则进入交互选择")
    parser.add_argument("--workers", type=int, default=2, help="并发数，默认2")
    args = parser.parse_args()

    if not checker.has_llm_credentials():
        print("没有找到可用的 LLM key。")
        print(f"在 {os.path.join(PRODUCT_ROOT, '.env')} 里写一行 DEEPSEEK_API_KEY=你的key，")
        print("或者在终端里先 export 一下再运行这个脚本。")
        sys.exit(1)

    available = ds.list_datasets()
    if not available:
        print("数据集/ 文件夹里没有找到任何可用数据集。")
        sys.exit(1)

    if args.dataset:
        dataset_key = resolve_dataset_key(args.dataset, available)
        if not dataset_key:
            print(f"没找到匹配「{args.dataset}」的数据集，可用的有：")
            for d in available:
                print(f"   {d['key']}  ({d['label']})")
            sys.exit(1)
    else:
        dataset_key = interactive_pick(available)

    label = next(d["label"] for d in available if d["key"] == dataset_key)
    print(f"\n开始跑：{label}　（并发数 {args.workers}，用的是 {checker.describe_llm_runtime()}）")
    print("数据量大的话会跑几分钟，别关这个窗口……\n")

    record, out_path = server.run_dataset(dataset_key, workers=args.workers)
    s = record["summary"]

    def _pct(v):
        return "不适用（这份数据集没有分类/中危标注）" if v is None else f"{v:.0%}"

    print(f"\n跑完了：{record['run_id']}")
    print(f"  总用例数：{s['total']}　成功：{s['tested']}　报错：{s['errored']}")
    print(f"  整体类别准确率：{_pct(s['overall_exact_category_accuracy'])}")
    print(f"  高危 Recall（召回率，漏报的反面）：{_pct(s['critical_recall_release_gate'])}")
    if s.get("has_category_labels", True):
        print(f"  中危 Precision：{_pct(s['medium_precision_release_gate'])}")
    else:
        print("  中危 Precision：不适用（当前4大类规则已经没有Medium这一档了，这个指标先跳过）")
    print(f"  低危误报率（FPR）：{_pct(s['low_false_positive_rate_release_gate'])}")
    if record["data_issues"]:
        print(f"  数据质量提示：{len(record['data_issues'])} 条，详见结果文件")
    print(f"  完整结果：{out_path}")

    # 顺手生成一次分析报告，省得再开一次网页点一次
    try:
        rep = report_mod.build_report(record)
        html_path = report_mod.export_html(rep)
        print(f"  分析报告已生成：{html_path}")
        print(f"  （范围内真实准确率：{_pct(rep['in_scope']['accuracy'])}，排除了还没实现的类别之后的真实水平）")
    except Exception as e:
        print(f"  （分析报告生成时出了点问题，不影响跑分结果本身：{e}）")

    print("\n想看逐条结果和根因分析，双击 启动网页.command，去「③命中结果」「④分析报告」tab看更详细的。")


if __name__ == "__main__":
    main()
