#!/usr/bin/env python3
"""
分析报告：从命中结果自动生成分析，替代手工维护的跑分报告 HTML

这是合规工作台的第 4 个模块。它不重新跑评测，只读 `命中结果/hits_*.json`，
把"一堆逐条结果"变成"能回答问题的分析"。

要回答的三个问题（也是这个模块存在的理由）：

1. **这次跑分，哪些miss是我该修的，哪些是本来就测不出来的？**
   以前看到"高危Recall 87%"只能干着急，因为分不清剩下的13%里，有多少是规则写得不好、
   有多少是那条case属于压根没实现的类别（02/04/08/09）。本模块把失败按根因分桶，
   把"我该修的"和"本来就不该期待"分开。

2. **跟上次比，是变好了还是变坏了？**
   自动找同一个数据集的上一次跑分做对比，避免"改完规则感觉好像好了一点"这种错觉。

3. **哪一类最弱？**
   按类别拆解准确率，直接告诉你下一步该往哪使劲。

用法（一般不用直接跑，网页上点就行）：
    python3 report.py ../命中结果/hits_20260807_195837.json
"""

import json
import os
import sys
from collections import defaultdict, Counter
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PRODUCT_ROOT = os.path.dirname(SCRIPT_DIR)
HITS_DIR = os.path.join(PRODUCT_ROOT, "命中结果")
RULES_PATH = os.path.join(PRODUCT_ROOT, "规则配置", "rules_config.json")
EXPORT_DIR = SCRIPT_DIR

FULL_TAXONOMY_NAMES = {
    "01": "商业贿赂与利益交换",
    "02": "非法获取统方数据",
    "03": "主动超说明书/超适应症推广",
    "04": "隐瞒/延迟报告不良反应",
    "05": "患者隐私泄漏",
    "06": "讲课费/学术赞助对价化",
    "07": "夸大疗效与绝对化宣讲",
    "08": "无证据竞品对比与贬低",
    "09": "规避备案/违规区域拜访",
    "10": "学术表述不严谨/完全合规",
}


def load_implemented_categories():
    try:
        with open(RULES_PATH, "r", encoding="utf-8") as f:
            return set(json.load(f)["categories"].keys())
    except Exception:
        return set()


def list_runs():
    """列出所有历史跑分，按时间倒序。只读摘要，不加载逐条结果（大数据集会很慢）。"""
    if not os.path.isdir(HITS_DIR):
        return []
    runs = []
    for name in sorted(os.listdir(HITS_DIR), reverse=True):
        if not (name.startswith("hits_") and name.endswith(".json")):
            continue
        path = os.path.join(HITS_DIR, name)
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            s = data.get("summary", {})
            runs.append({
                "run_id": data.get("run_id", name),
                "file": name,
                "dataset": data.get("dataset"),
                "dataset_label": data.get("dataset_label", ""),
                "started_at": data.get("started_at", ""),
                "finished_at": data.get("finished_at", ""),
                "total": s.get("total", 0),
                "tested": s.get("tested", 0),
                "errored": s.get("errored", 0),
                "overall_exact_category_accuracy": s.get("overall_exact_category_accuracy"),
                "critical_recall": s.get("critical_recall_release_gate"),
                "medium_precision": s.get("medium_precision_release_gate"),
                "low_fp_rate": s.get("low_false_positive_rate_release_gate"),
                "model": s.get("model", ""),
            })
        except Exception as e:
            runs.append({"run_id": name, "file": name, "error": f"读取失败：{e}"})
    return runs


def load_run(run_id):
    """按 run_id 读一次完整跑分记录。"""
    if not os.path.isdir(HITS_DIR):
        raise ValueError("还没有任何跑分记录")
    for name in os.listdir(HITS_DIR):
        if not (name.startswith("hits_") and name.endswith(".json")):
            continue
        path = os.path.join(HITS_DIR, name)
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if data.get("run_id") == run_id or name == run_id:
            return data
    raise ValueError(f"找不到跑分记录：{run_id}")


def _order_key(run):
    """排序用的键。只用 started_at 不够：它只精确到秒，同一秒内跑完的两次会并列，
    导致"上一次"找不出来。run_id 在撞秒时会带 _2/_3 后缀，正好能当稳定的次序补充。"""
    return (run.get("started_at", ""), run.get("run_id", ""))


def find_previous_run(current):
    """找同一数据集上、时间上紧邻的前一次跑分，用于做对比。"""
    current_key = _order_key(current)
    candidates = [
        r for r in list_runs()
        if r.get("dataset_label") == current.get("dataset_label")
        and r.get("run_id") != current.get("run_id")
        and "error" not in r
        and _order_key(r) < current_key
    ]
    if not candidates:
        return None
    return max(candidates, key=_order_key)


def _is_correct(r):
    """判断一条case算不算"判对了"。

    有分类标注的数据集，按分类判没判对来看（跟之前一样）。但有些数据集（比如2026-08-09
    简化过的300case v2）压根不带分类列，只有风险等级+处置动作，这时候exact_category是
    None——不代表"判错了"，只是这个维度没有标准答案可比。这种情况退化成看动作判没判对，
    动作也没有的话再退化成看风险等级本身对不对，不能什么都没有就直接当成miss。
    """
    if r.get("exact_category") is not None:
        return bool(r.get("exact_category"))
    if r.get("exact_action") is not None:
        return bool(r.get("exact_action"))
    return r.get("risk_level") == r.get("actual_risk_level")


def bucket_failures(results, implemented):
    """把所有"没judge对"的case按根因分桶——这是整个报告最有价值的部分。

    分三类，对应三种完全不同的后续动作：
      - out_of_scope：期望类别压根没实现，miss是必然的 → 不用改规则，要么接受、要么去实现新类别
      - runtime_error：调用/解析层报错，不是判断问题 → 属于内部实现层的健壮性问题
      - real_miss：范围内的真实误判 → 这才是"规则该改"的部分
    """
    buckets = {"out_of_scope": [], "runtime_error": [], "real_miss": []}
    for r in results:
        if r.get("status") != "OK":
            buckets["runtime_error"].append(r)
            continue
        if _is_correct(r):
            continue
        expected = r.get("expected_category")
        if implemented and expected and expected not in implemented:
            buckets["out_of_scope"].append(r)
        else:
            buckets["real_miss"].append(r)
    return buckets


def classify_real_miss(r):
    """范围内的真实误判，再细分方向——漏报和误报的严重性完全不一样。"""
    expected_risk = r.get("risk_level")
    actual_risk = r.get("actual_risk_level")
    if expected_risk == "Critical" and actual_risk != "Critical":
        return "漏报高危（最严重：真违规被放过）"
    if expected_risk == "Low" and actual_risk != "Low":
        return "误伤合规（合规内容被拦截，影响可用性）"
    if expected_risk == actual_risk:
        return "同风险等级内串类（风险判断对，具体归类不准）"
    return "风险等级判断偏移"


def build_report(run):
    results = run.get("results", [])
    summary = run.get("summary", {})
    implemented = load_implemented_categories()
    buckets = bucket_failures(results, implemented)

    # 按类别拆解，并标注这个类别当前实现了没有。
    # 没有分类标注的case（expected_category是None）直接跳过，不塞进一个假的"?"分类里——
    # 如果整个数据集都没有分类标注，这张表最后就是空的，网页/HTML那边要对着这个空表给出说明，
    # 不能留一个看起来像是漏了什么的空表格。
    per_cat = defaultdict(lambda: {"total": 0, "correct": 0})
    for r in results:
        cat = r.get("expected_category")
        if cat is None:
            continue
        per_cat[cat]["total"] += 1
        per_cat[cat]["correct"] += int(bool(r.get("exact_category")))

    category_breakdown = []
    for cat in sorted(per_cat.keys()):
        stat = per_cat[cat]
        category_breakdown.append({
            "category": cat,
            "name": FULL_TAXONOMY_NAMES.get(cat, ""),
            "implemented": cat in implemented if implemented else None,
            "total": stat["total"],
            "correct": stat["correct"],
            "accuracy": stat["correct"] / stat["total"] if stat["total"] else 0,
        })

    real_miss_reasons = Counter(classify_real_miss(r) for r in buckets["real_miss"])

    # 只统计"范围内"的case，算一个更诚实的分数：
    # 把未实现类别的case排除掉之后，当前这套规则到底做得怎么样。
    # 没有分类标注的case（expected_category是None）没法判断它是不是"未实现类别"，
    # 默认算在范围内，用_is_correct()做兜底判断（分类没有就退化成看动作/风险等级）。
    in_scope = [
        r for r in results
        if r.get("expected_category") is None or not implemented or (r.get("expected_category") in implemented)
    ]
    in_scope_ok = [r for r in in_scope if r.get("status") == "OK"]
    in_scope_correct = [r for r in in_scope_ok if _is_correct(r)]

    prev = find_previous_run(run)
    comparison = None
    if prev:
        def delta(now, before):
            if now is None or before is None:
                return None
            return now - before
        comparison = {
            "previous_run_id": prev["run_id"],
            "previous_started_at": prev.get("started_at", ""),
            "overall_exact_category_accuracy": {
                "now": summary.get("overall_exact_category_accuracy"),
                "before": prev.get("overall_exact_category_accuracy"),
                "delta": delta(summary.get("overall_exact_category_accuracy"),
                               prev.get("overall_exact_category_accuracy")),
            },
            "critical_recall": {
                "now": summary.get("critical_recall_release_gate"),
                "before": prev.get("critical_recall"),
                "delta": delta(summary.get("critical_recall_release_gate"), prev.get("critical_recall")),
            },
            "errored": {
                "now": summary.get("errored"),
                "before": prev.get("errored"),
                "delta": delta(summary.get("errored"), prev.get("errored")),
            },
        }

    return {
        "run_id": run.get("run_id"),
        "dataset_label": run.get("dataset_label", ""),
        "started_at": run.get("started_at", ""),
        "finished_at": run.get("finished_at", ""),
        "model": summary.get("model", ""),
        "headline": {
            "total": summary.get("total", 0),
            "tested": summary.get("tested", 0),
            "errored": summary.get("errored", 0),
            "overall_exact_category_accuracy": summary.get("overall_exact_category_accuracy"),
            "critical_recall": summary.get("critical_recall_release_gate"),
            "medium_precision": summary.get("medium_precision_release_gate"),
            "low_fp_rate": summary.get("low_false_positive_rate_release_gate"),
        },
        "in_scope": {
            "total": len(in_scope),
            "tested": len(in_scope_ok),
            "correct": len(in_scope_correct),
            "accuracy": len(in_scope_correct) / len(in_scope_ok) if in_scope_ok else None,
            "note": (
                "这份数据集没有分类标注，这个数按风险等级/处置动作判得对不对来算，不涉及具体分类"
                if not category_breakdown else
                "只统计当前已实现类别的case，排除掉还没做的类别——这个数才代表当前规则的真实水平"
            ),
        },
        "failure_buckets": {
            "out_of_scope": {
                "count": len(buckets["out_of_scope"]),
                "meaning": "期望类别当前还没实现，miss属于预期内，不是规则问题",
                "action": "要么接受这个范围收敛，要么把该类别加进规则配置",
                "cases": [_slim(r) for r in buckets["out_of_scope"][:30]],
            },
            "runtime_error": {
                "count": len(buckets["runtime_error"]),
                "meaning": "LLM返回空/截断/解析失败，属于内部实现层的稳定性问题，不是判断错",
                "action": "看重试逻辑是否够用、max_tokens是否还需要调整",
                "cases": [_slim(r) for r in buckets["runtime_error"][:30]],
            },
            "real_miss": {
                "count": len(buckets["real_miss"]),
                "meaning": "范围内的真实误判——这才是规则该改的部分",
                "action": "逐条看rationale，判断是规则说明不清楚、还是缺边界示例",
                "reasons": dict(real_miss_reasons),
                "cases": [_slim(r) for r in buckets["real_miss"][:50]],
            },
        },
        "category_breakdown": category_breakdown,
        "has_category_labels": bool(category_breakdown),
        "comparison": comparison,
    }


def _slim(r):
    """逐条结果里只留报告要用的字段，避免报告JSON过大。"""
    return {
        "id": r.get("id"),
        "text": (r.get("text") or "")[:120],
        "expected_category": r.get("expected_category"),
        "actual_category": r.get("actual_category"),
        "risk_level": r.get("risk_level"),
        "actual_risk_level": r.get("actual_risk_level"),
        "actual_rationale": (r.get("actual_rationale") or "")[:200],
        "status": r.get("status"),
    }


# ---------- 导出成独立 HTML（方便面试展示/发给别人看） ----------

def _pct(v):
    return "-" if v is None else f"{v * 100:.0f}%"


def _esc(s):
    return (str(s or "")
            .replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def render_html(report):
    h = report["headline"]
    ins = report["in_scope"]
    fb = report["failure_buckets"]

    cat_rows = "".join(
        f"<tr><td>{_esc(c['category'])}</td><td>{_esc(c['name'])}</td>"
        f"<td>{'已实现' if c['implemented'] else '未实现'}</td>"
        f"<td>{c['total']}</td><td>{c['correct']}</td><td>{_pct(c['accuracy'])}</td></tr>"
        for c in report["category_breakdown"]
    )

    def bucket_block(key, title):
        b = fb[key]
        rows = "".join(
            f"<tr><td>{_esc(c['id'])}</td><td>{_esc(c['text'])}</td>"
            f"<td>{_esc(c['expected_category'])}</td><td>{_esc(c['actual_category'] or '-')}</td>"
            f"<td>{_esc(c['actual_rationale'] or c['status'])}</td></tr>"
            for c in b["cases"]
        )
        reasons = ""
        if b.get("reasons"):
            reasons = "<ul>" + "".join(
                f"<li>{_esc(k)}：{v} 条</li>" for k, v in b["reasons"].items()
            ) + "</ul>"
        table = (f"<table><thead><tr><th>ID</th><th>输入</th><th>期望</th><th>实际</th>"
                 f"<th>模型理由 / 报错</th></tr></thead><tbody>{rows}</tbody></table>") if rows else ""
        return f"""
      <div class="bucket">
        <h3>{title}：{b['count']} 条</h3>
        <p class="meaning">{_esc(b['meaning'])}</p>
        <p class="action"><strong>该怎么办：</strong>{_esc(b['action'])}</p>
        {reasons}
        {table}
      </div>"""

    comparison_block = ""
    if report.get("comparison"):
        c = report["comparison"]

        def row(label, d):
            if d["before"] is None or d["now"] is None:
                return ""
            if isinstance(d["now"], float):
                now, before = _pct(d["now"]), _pct(d["before"])
                delta = f"{d['delta'] * 100:+.0f}pp"
            else:
                now, before, delta = d["now"], d["before"], f"{d['delta']:+d}"
            return f"<tr><td>{label}</td><td>{before}</td><td>{now}</td><td>{delta}</td></tr>"

        comparison_block = f"""
      <h2>跟上次比</h2>
      <p>对比对象：同一数据集的上一次跑分 <code>{_esc(c['previous_run_id'])}</code>（{_esc(c['previous_started_at'])}）</p>
      <table><thead><tr><th>指标</th><th>上次</th><th>这次</th><th>变化</th></tr></thead><tbody>
        {row('整体类别准确率', c['overall_exact_category_accuracy'])}
        {row('高危Recall', c['critical_recall'])}
        {row('报错数', c['errored'])}
      </tbody></table>"""

    return f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>分析报告 {_esc(report['run_id'])} · AI Compliance Check Assistant</title>
<style>
 body {{ font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Segoe UI", sans-serif;
   line-height: 1.7; color: #1f2937; max-width: 960px; margin: 0 auto; padding: 32px 24px; background: #f5f7fb; }}
 h1 {{ font-size: 24px; margin: 0 0 4px; }} h2 {{ font-size: 18px; margin-top: 32px; }}
 h3 {{ font-size: 16px; margin: 0 0 6px; }}
 .sub {{ color: #6b7280; font-size: 14px; margin-bottom: 24px; }}
 .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 12px; }}
 .metric {{ background: #fff; border: 1px solid #e5e7eb; border-radius: 12px; padding: 12px 14px; }}
 .metric .l {{ font-size: 12px; color: #6b7280; }} .metric .v {{ font-size: 22px; font-weight: 600; }}
 table {{ width: 100%; border-collapse: collapse; font-size: 13px; background: #fff;
   border: 1px solid #e5e7eb; border-radius: 8px; margin-top: 10px; }}
 th, td {{ text-align: left; padding: 7px 10px; border-bottom: 1px solid #e5e7eb; vertical-align: top; }}
 th {{ color: #6b7280; font-weight: 600; background: #f9fafb; }}
 .bucket {{ background: #fff; border: 1px solid #e5e7eb; border-radius: 12px; padding: 16px; margin-bottom: 14px; }}
 .meaning {{ color: #6b7280; font-size: 14px; margin: 0 0 6px; }}
 .action {{ font-size: 14px; margin: 0; }}
 .callout {{ background: #eef2ff; border: 1px solid #c7d2fe; border-radius: 12px; padding: 14px 16px; }}
 code {{ background: #f3f4f6; padding: 1px 5px; border-radius: 4px; font-size: 13px; }}
</style></head><body>
<h1>分析报告</h1>
<div class="sub">数据集 {_esc(report['dataset_label'])}　·　模型 {_esc(report['model'])}　·　跑分ID <code>{_esc(report['run_id'])}</code>　·　{_esc(report['started_at'])} → {_esc(report['finished_at'])}</div>

<h2>整体结果</h2>
<div class="metrics">
  <div class="metric"><div class="l">总用例数</div><div class="v">{h['total']}</div></div>
  <div class="metric"><div class="l">成功 / 报错</div><div class="v">{h['tested']} / {h['errored']}</div></div>
  <div class="metric"><div class="l">整体类别准确率</div><div class="v">{_pct(h['overall_exact_category_accuracy'])}</div></div>
  <div class="metric"><div class="l">高危 Recall</div><div class="v">{_pct(h['critical_recall'])}</div></div>
  <div class="metric"><div class="l">中危 Precision</div><div class="v">{_pct(h['medium_precision'])}</div></div>
  <div class="metric"><div class="l">低危误报率</div><div class="v">{_pct(h['low_fp_rate'])}</div></div>
</div>

<h2>只看范围内的真实水平</h2>
<div class="callout">
  <p style="margin:0 0 6px"><strong>范围内准确率：{_pct(ins['accuracy'])}</strong>（{ins['correct']} / {ins['tested']} 条已测）</p>
  <p style="margin:0; color:#4338ca; font-size:14px">{_esc(ins['note'])}</p>
</div>

<h2>失败根因分桶</h2>
{bucket_block('real_miss', '范围内真实误判')}
{bucket_block('runtime_error', '调用/解析层报错')}
{bucket_block('out_of_scope', '未实现类别的自然miss')}

<h2>按类别拆解</h2>
{f'<table><thead><tr><th>类别</th><th>名称</th><th>状态</th><th>条数</th><th>判对</th><th>准确率</th></tr></thead><tbody>{cat_rows}</tbody></table>' if report['has_category_labels'] else '<p class="sub">这份数据集没有分类标注，只有风险等级和处置动作，跳过按类别拆解——上面的Release Gate指标和失败根因分桶依然是有效的，只是没法细分到具体是哪个规则类别的问题。</p>'}
{comparison_block}

<p class="sub" style="margin-top:32px">本报告由 <code>05-产品原型/分析报告/report.py</code> 从命中结果自动生成，不是手工维护的数字。</p>
</body></html>"""


def export_html(report, out_path=None):
    if out_path is None:
        os.makedirs(EXPORT_DIR, exist_ok=True)
        out_path = os.path.join(EXPORT_DIR, f"报告_{report['run_id']}.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(render_html(report))
    return out_path


def main():
    if len(sys.argv) < 2:
        runs = list_runs()
        if not runs:
            print("还没有任何跑分记录。先去网页上跑一次评测，或者用 规则执行/run_eval.py。")
            return
        print("可用的跑分记录：")
        for r in runs:
            print(f"  {r['run_id']}　{r.get('dataset_label','')}　{r.get('started_at','')}")
        print('\n用法：python3 report.py <run_id>')
        return

    run = load_run(sys.argv[1])
    report = build_report(run)
    path = export_html(report)
    print(json.dumps(report["headline"], ensure_ascii=False, indent=2))
    print(f"\nHTML 报告已导出：{path}")


if __name__ == "__main__":
    main()
