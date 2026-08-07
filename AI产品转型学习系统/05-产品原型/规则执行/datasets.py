#!/usr/bin/env python3
"""
数据集发现与加载

解决两个实际问题：

1. **数据集散落在各处**：以前跑大样本要在网页上填一长串绝对路径（`/Users/li/Downloads/300 case...csv`），
   换台机器、文件挪个位置就失效。现在约定：所有评测数据集都放在 `05-产品原型/数据集/` 这一个
   文件夹里，本模块自动扫描该目录下的所有 `.csv`，网页上直接下拉选择即可。想加新数据集？
   把 CSV 拷进那个文件夹就行，不用改任何代码。

2. **不同数据集的表头不一样**：CSV50 用的是 `Case ID` / `风险等级` / `预期处置动作`，
   200case 用的是 `ID` / `风险级别`、并且没有预期动作列。以前 `run_eval_csv.load_cases()`
   写死了 CSV50 的列名，喂 200case 会直接 KeyError 崩掉。本模块用"列名别名表"做归一化，
   两种表头都能读，缺失的列（比如预期动作）按 None 处理而不是报错。

对外主要接口：
    list_datasets()              -> 列出所有可用数据集（内置MVP子集 + 数据集/ 下的所有CSV）
    load_dataset_cases(key)      -> 按 key 读出统一结构的 case 列表
"""

import csv
import json
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PRODUCT_ROOT = os.path.dirname(SCRIPT_DIR)
DATASETS_DIR = os.path.join(PRODUCT_ROOT, "数据集")
MVP_CASES_PATH = os.path.join(SCRIPT_DIR, "eval_cases.json")

# 列名别名：不同来源的数据集表头不统一，统一映射到内部字段名
COLUMN_ALIASES = {
    "id": ["Case ID", "case id", "ID", "id", "编号", "用例ID"],
    "category": ["分类ID", "类别ID", "category_id"],
    "category_name": ["风险分类", "分类名称", "类别"],
    "text": ["CRM拜访记录文本", "拜访记录", "文本", "text"],
    "risk_level": ["风险等级", "风险级别", "risk_level"],
    "expected_action": ["预期处置动作", "预期动作", "处置动作", "expected_action"],
    "rationale": ["合规判定依据", "判定依据", "依据", "rationale"],
}

# 从 rules_config.json 里的类别推断风险等级时用的兜底
DEFAULT_RISK_LEVEL = "Low"

# 完整风险分类体系是 01-10 十类（见 03-学习成果/CRM-Compliance-Eval框架说明.md）。
# demo 当前只实现了其中 6 类，另外 4 类（02/04/08/09）是主动收敛、暂不实现的范围。
# 区分这两种情况很重要：
#   - 数据集里出现 02/04/08/09 → 正常，是"已知未实现"，不是数据错误，跑分时会自然miss
#   - 数据集里出现 107 这种压根不在体系内的ID → 真的是数据录入错误，该修数据
FULL_TAXONOMY = {"01", "02", "03", "04", "05", "06", "07", "08", "09", "10"}

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


def _resolve_columns(fieldnames):
    """把实际表头映射成 {内部字段名: 实际列名}，找不到的字段不出现在结果里。"""
    available = {name.strip(): name for name in (fieldnames or [])}
    resolved = {}
    for internal, aliases in COLUMN_ALIASES.items():
        for alias in aliases:
            if alias in available:
                resolved[internal] = available[alias]
                break
    return resolved


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


def load_csv_cases(csv_path, config=None):
    """读一个 CSV，返回统一结构的 case 列表 + 数据质量问题清单。

    统一结构（跟 run_eval_csv.evaluate_one() 期望的一致）：
      id / expected_category / category_name / text / risk_level / expected_action / rationale
    """
    rows = []
    issues = []
    with open(csv_path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        cols = _resolve_columns(reader.fieldnames)
        missing_required = [k for k in ("category", "text") if k not in cols]
        if missing_required:
            raise ValueError(
                f"{os.path.basename(csv_path)} 缺少必需的列：{missing_required}。"
                f"实际表头是：{reader.fieldnames}"
            )

        for idx, row in enumerate(reader, start=1):
            def get(field, default=""):
                col = cols.get(field)
                return row.get(col, default) if col else default

            case_id = str(get("id") or f"row{idx}").strip()
            category = normalize_category_id(get("category"))
            risk_level = str(get("risk_level") or "").strip()

            # 数据质量检查：只报"真的错了"的，不报"已知未实现"的
            if category and category not in FULL_TAXONOMY:
                issues.append({
                    "case_id": case_id,
                    "problem": f"分类ID「{category}」不在 01-10 的风险分类体系内，疑似数据录入错误",
                    "detail": f"该case的风险分类写的是「{get('category_name')}」，建议核对后修正数据",
                })

            # 有些数据集没有风险等级列，用规则配置里该类别的等级兜底
            if not risk_level and config:
                risk_level = config.get("categories", {}).get(category, {}).get("risk_level", DEFAULT_RISK_LEVEL)
            if not risk_level:
                risk_level = DEFAULT_RISK_LEVEL

            rows.append({
                "id": case_id,
                "expected_category": category,
                "category_name": str(get("category_name") or "").strip(),
                "text": str(get("text") or "").strip(),
                "risk_level": risk_level,
                "expected_action": normalize_expected_action(get("expected_action")),
                "rationale": str(get("rationale") or "").strip(),
            })
    return rows, issues


def load_mvp_cases(config):
    """MVP子集（eval_cases.json）字段名跟CSV不一样，单独转换。"""
    with open(MVP_CASES_PATH, "r", encoding="utf-8") as f:
        raw_cases = json.load(f)["cases"]
    out = []
    for c in raw_cases:
        cat_meta = (config or {}).get("categories", {}).get(c["expected_category"], {})
        out.append({
            "id": c["id"],
            "expected_category": c["expected_category"],
            "category_name": cat_meta.get("name", ""),
            "text": c["input"],
            "risk_level": cat_meta.get("risk_level", DEFAULT_RISK_LEVEL),
            # MVP子集的 expected_action 还是 Day05 时期的旧动作名（Block/Warning等），
            # 跟当前 action_space 对不上，所以不比对动作、只比对类别，
            # 跟 run_eval.py 的既有做法保持一致。
            "expected_action": None,
            "rationale": c.get("note", ""),
        })
    return out, []


def list_datasets():
    """列出所有可选数据集：内置的MVP子集 + 数据集/ 文件夹里的每个CSV。"""
    items = [{
        "key": "mvp",
        "label": "MVP子集（自拟case，30条）",
        "kind": "builtin",
        "path": MVP_CASES_PATH,
        "exists": os.path.exists(MVP_CASES_PATH),
    }]

    if os.path.isdir(DATASETS_DIR):
        for name in sorted(os.listdir(DATASETS_DIR)):
            if not name.lower().endswith(".csv"):
                continue
            path = os.path.join(DATASETS_DIR, name)
            try:
                with open(path, "r", encoding="utf-8-sig", newline="") as f:
                    count = max(0, sum(1 for _ in f) - 1)
            except Exception:
                count = None
            items.append({
                "key": f"file:{name}",
                "label": f"{name}（{count if count is not None else '?'}条）",
                "kind": "csv",
                "path": path,
                "exists": True,
            })
    return items


def load_dataset_cases(key, config, custom_path=None):
    """按 key 加载数据集，返回 (cases, 人类可读的数据集名, 数据质量问题清单)。"""
    if key == "mvp":
        cases, issues = load_mvp_cases(config)
        return cases, "MVP子集（eval_cases.json）", issues

    if key and key.startswith("file:"):
        name = key[len("file:"):]
        path = os.path.join(DATASETS_DIR, name)
        if not os.path.exists(path):
            raise ValueError(f"数据集文件不存在：{path}")
        cases, issues = load_csv_cases(path, config)
        return cases, name, issues

    if key == "custom":
        if not custom_path:
            raise ValueError("选择了自定义数据集，但没有填写文件路径")
        if not os.path.exists(custom_path):
            raise ValueError(f"找不到文件：{custom_path}")
        cases, issues = load_csv_cases(custom_path, config)
        return cases, f"自定义（{os.path.basename(custom_path)}）", issues

    raise ValueError(f"未知的数据集：{key}")
