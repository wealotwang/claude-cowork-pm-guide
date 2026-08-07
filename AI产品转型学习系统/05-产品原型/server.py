#!/usr/bin/env python3
"""
05-产品原型 统一本地服务

这是合规工作台的共用后端，被网页前端（同目录 index.html）的两个 tab 共用：
  - 规则配置：读写 规则配置/rules_config.json（不需要 LLM key）
  - 规则执行：跑 规则执行/ 下的 checker.py 对某个数据集做一键评测（需要 LLM key）

迁移说明：本文件由 规则配置/server.py 升级而来（那份文件已标注归档，指向这里）。
规则配置相关的 load_rules/save_rules/Handler.do_GET("/api/rules") 逻辑完全没变，
只是路径从"同目录"改成指向 规则配置/ 子目录；新增的是 /api/datasets 和 /api/run
这两个"规则执行"模块的接口。

不依赖任何第三方包，只用 Python 标准库。

用法：
    cd "05-产品原型"
    python3 server.py
    # 浏览器打开 http://127.0.0.1:8787

规则配置这部分不需要 API key。规则执行这部分（点"运行评测"）需要你在启动 server.py
之前，在同一个终端里先设置好 DEEPSEEK_API_KEY（或 ANTHROPIC_API_KEY）：
    export DEEPSEEK_API_KEY="你自己的 key"
    python3 server.py
这个值只会被 checker.py 从环境变量里读一次去调用 LLM API，本脚本不会存储、不会记录它。
"""

import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RULES_DIR = os.path.join(SCRIPT_DIR, "规则配置")
EXEC_DIR = os.path.join(SCRIPT_DIR, "规则执行")
HITS_DIR = os.path.join(SCRIPT_DIR, "命中结果")

RULES_PATH = os.path.join(RULES_DIR, "rules_config.json")
INDEX_PATH = os.path.join(SCRIPT_DIR, "index.html")
PORT = 8787

REQUIRED_CATEGORY_FIELDS = {"name", "risk_level", "action", "description", "examples", "boundary_examples"}

# 规则执行模块（checker.py / run_eval.py / run_eval_csv.py）是兄弟目录下的独立文件，
# 不是 pip 包，所以手动把它加进 sys.path 才能 import。
sys.path.insert(0, EXEC_DIR)
import checker  # noqa: E402
import run_eval as mvp_eval  # noqa: E402
import run_eval_csv as csv_eval  # noqa: E402

CSV50_PATH = csv_eval.DEFAULT_CSV_PATH


# ---------- 规则配置：读写 rules_config.json ----------

def load_rules():
    with open(RULES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_rules(data):
    # 基本校验：不能保存一个明显残缺的结构，宁可拒绝也不要把 rules_config.json 存坏
    if "categories" not in data or not isinstance(data["categories"], dict):
        raise ValueError("缺少 categories 字段，或者它不是一个对象")
    for cat_id, cat in data["categories"].items():
        missing = REQUIRED_CATEGORY_FIELDS - set(cat.keys())
        if missing:
            raise ValueError(f"类目 {cat_id} 缺少字段：{', '.join(missing)}")
    with open(RULES_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


# ---------- 规则执行：一键跑评测 ----------

def normalize_mvp_cases(config):
    """把 eval_cases.json 的字段名对齐成 run_eval_csv.evaluate_one() 期望的形状。"""
    raw_cases = mvp_eval.load_cases()
    out = []
    for c in raw_cases:
        cat_meta = config["categories"].get(c["expected_category"], {})
        out.append({
            "id": c["id"],
            "expected_category": c["expected_category"],
            "category_name": cat_meta.get("name", ""),
            "text": c["input"],
            "risk_level": cat_meta.get("risk_level", "Low"),
            # MVP子集的 expected_action 还是 Day05 时期的旧动作名（Block/Warning等），
            # 跟当前 action_space 对不上，这里直接不比对动作，只比对类别，
            # 跟 run_eval.py 的既有做法保持一致。
            "expected_action": None,
            "rationale": c.get("note", ""),
        })
    return out


def resolve_cases(dataset, custom_path, config):
    if dataset == "mvp":
        return normalize_mvp_cases(config), "MVP子集（eval_cases.json）"
    if dataset == "csv50":
        if not os.path.exists(CSV50_PATH):
            raise ValueError(f"找不到默认CSV文件：{CSV50_PATH}")
        return csv_eval.load_cases(CSV50_PATH), "完整CSV50"
    if dataset == "custom":
        if not custom_path:
            raise ValueError("请填写自定义数据集的文件路径")
        if not os.path.exists(custom_path):
            raise ValueError(f"找不到文件：{custom_path}")
        return csv_eval.load_cases(custom_path), f"自定义（{custom_path}）"
    raise ValueError(f"未知的数据集类型：{dataset}")


def run_dataset(dataset, custom_path=None, workers=1):
    if not checker.has_llm_credentials():
        raise RuntimeError(
            "没有配置可用的 LLM key。请先停掉 server.py，在同一个终端里运行："
            '\n    export DEEPSEEK_API_KEY="你的key"'
            "\n（或者 export ANTHROPIC_API_KEY=\"你的key\"）"
            "\n然后重新运行 python3 server.py 再点一次运行评测。"
        )

    config = checker.load_config()
    cases, dataset_label = resolve_cases(dataset, custom_path, config)

    started = datetime.now()
    if workers and workers > 1:
        results = [None] * len(cases)
        with ThreadPoolExecutor(max_workers=workers) as executor:
            future_to_idx = {
                executor.submit(csv_eval.evaluate_one, c, config): i for i, c in enumerate(cases)
            }
            for future in as_completed(future_to_idx):
                results[future_to_idx[future]] = future.result()
    else:
        results = [csv_eval.evaluate_one(c, config) for c in cases]
    finished = datetime.now()

    summary = csv_eval.build_summary(results)

    run_id = started.strftime("%Y%m%d_%H%M%S")
    record = {
        "run_id": run_id,
        "dataset": dataset,
        "dataset_label": dataset_label,
        "custom_path": custom_path,
        "started_at": started.isoformat(timespec="seconds"),
        "finished_at": finished.isoformat(timespec="seconds"),
        "summary": summary,
        "results": results,
    }

    os.makedirs(HITS_DIR, exist_ok=True)
    out_path = os.path.join(HITS_DIR, f"hits_{run_id}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(record, f, ensure_ascii=False, indent=2)

    return record, out_path


# ---------- HTTP handler ----------

class Handler(BaseHTTPRequestHandler):
    def _send_json(self, payload, status=200):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            try:
                with open(INDEX_PATH, "rb") as f:
                    body = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            except FileNotFoundError:
                self._send_json({"error": "index.html 不存在"}, status=500)
            return

        if self.path == "/api/rules":
            try:
                data = load_rules()
                self._send_json(data)
            except Exception as e:
                self._send_json({"error": str(e)}, status=500)
            return

        if self.path == "/api/datasets":
            try:
                mvp_count = len(mvp_eval.load_cases())
            except Exception:
                mvp_count = None
            self._send_json({
                "presets": [
                    {
                        "key": "mvp",
                        "label": f"MVP子集（eval_cases.json，{mvp_count if mvp_count is not None else '?'}条）",
                    },
                    {
                        "key": "csv50",
                        "label": "完整CSV50",
                        "path": CSV50_PATH,
                        "exists": os.path.exists(CSV50_PATH),
                    },
                ],
                "has_api_key": checker.has_llm_credentials(),
                "llm_runtime": checker.describe_llm_runtime(),
            })
            return

        self._send_json({"error": "未知路径"}, status=404)

    def do_POST(self):
        if self.path == "/api/rules":
            length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(length)
            try:
                data = json.loads(raw.decode("utf-8"))
                save_rules(data)
                self._send_json({"status": "ok"})
            except json.JSONDecodeError as e:
                self._send_json({"error": f"提交的内容不是合法JSON：{e}"}, status=400)
            except ValueError as e:
                self._send_json({"error": f"校验没通过，没有保存：{e}"}, status=400)
            except Exception as e:
                self._send_json({"error": str(e)}, status=500)
            return

        if self.path == "/api/run":
            length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(length)
            try:
                body = json.loads(raw.decode("utf-8")) if raw else {}
                dataset = body.get("dataset")
                custom_path = body.get("custom_path")
                workers = int(body.get("workers") or 1)
                record, out_path = run_dataset(dataset, custom_path=custom_path, workers=workers)
                self._send_json({
                    "status": "ok",
                    "run_id": record["run_id"],
                    "dataset_label": record["dataset_label"],
                    "summary": record["summary"],
                    "results": record["results"],
                    "results_file": out_path,
                })
            except json.JSONDecodeError as e:
                self._send_json({"error": f"请求体不是合法JSON：{e}"}, status=400)
            except (ValueError, RuntimeError) as e:
                self._send_json({"error": str(e)}, status=400)
            except Exception as e:
                self._send_json({"error": f"内部错误：{e}"}, status=500)
            return

        self._send_json({"error": "未知路径"}, status=404)

    def log_message(self, format, *args):
        # 精简一下默认日志，只保留方法+路径+状态码
        print(f"[server] {self.command} {self.path} -> {args[1] if len(args) > 1 else ''}")


def main():
    if not os.path.exists(RULES_PATH):
        print(f"错误：找不到 {RULES_PATH}")
        return
    server = HTTPServer(("127.0.0.1", PORT), Handler)
    print(f"合规工作台已启动：http://127.0.0.1:{PORT}")
    print(f"当前 LLM 运行时：{checker.describe_llm_runtime()}")
    print("按 Ctrl+C 停止")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n已停止")


if __name__ == "__main__":
    main()
