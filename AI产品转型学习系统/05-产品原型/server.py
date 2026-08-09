#!/usr/bin/env python3
"""
05-产品原型 统一本地服务

这是合规工作台的共用后端，被网页前端（同目录 index.html）的四个 tab 共用：
  ① 规则配置：读写 规则配置/rules_config.json（不需要 LLM key）
  ② 规则执行：跑 规则执行/ 下的 checker.py 对某个数据集做一键评测（需要 LLM key）
  ③ 命中结果：浏览 命中结果/ 下的历史跑分记录
  ④ 分析报告：从某次命中结果自动生成分析，可导出独立 HTML

不依赖任何第三方包，只用 Python 标准库。

用法：
    cd "05-产品原型"
    python3 server.py
    # 浏览器打开 http://127.0.0.1:8787

规则配置、命中结果、分析报告这三个 tab 都不需要 API key。只有"规则执行"点运行时需要，
且必须在启动 server.py 之前，在同一个终端里先设置好：
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
from urllib.parse import urlparse, parse_qs

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RULES_DIR = os.path.join(SCRIPT_DIR, "规则配置")
EXEC_DIR = os.path.join(SCRIPT_DIR, "规则执行")
HITS_DIR = os.path.join(SCRIPT_DIR, "命中结果")
REPORT_DIR = os.path.join(SCRIPT_DIR, "分析报告")

RULES_PATH = os.path.join(RULES_DIR, "rules_config.json")
INDEX_PATH = os.path.join(SCRIPT_DIR, "index.html")
PORT = 8787

REQUIRED_CATEGORY_FIELDS = {"name", "risk_level", "action", "description", "examples", "boundary_examples"}

# 规则执行/分析报告是兄弟目录下的独立文件，不是 pip 包，手动加进 sys.path 才能 import
sys.path.insert(0, EXEC_DIR)
sys.path.insert(0, REPORT_DIR)
import checker  # noqa: E402
import datasets as ds  # noqa: E402
import run_eval_csv as csv_eval  # noqa: E402
import report as report_mod  # noqa: E402


# ---------- ① 规则配置：读写 rules_config.json ----------

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


# ---------- ② 规则执行：一键跑评测 ----------

def run_dataset(dataset, custom_path=None, workers=1):
    if not checker.has_llm_credentials():
        raise RuntimeError(
            "没有配置可用的 LLM key。请先停掉 server.py，在同一个终端里运行："
            '\n    export DEEPSEEK_API_KEY="你的key"'
            '\n（或者 export ANTHROPIC_API_KEY="你的key"）'
            "\n然后重新运行 python3 server.py 再点一次运行评测。"
        )

    config = checker.load_config()
    cases, dataset_label, data_issues = ds.load_dataset_cases(dataset, config, custom_path=custom_path)
    if not cases:
        raise ValueError(f"数据集「{dataset_label}」里一条case都没有，检查一下文件内容")

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

    # run_id 用秒级时间戳，但两次跑分可能落在同一秒（小数据集+高并发时很容易），
    # 那样后一次会直接覆盖前一次的结果文件。所以撞了就加后缀，保证每次跑分的记录都留得下来。
    os.makedirs(HITS_DIR, exist_ok=True)
    base_run_id = started.strftime("%Y%m%d_%H%M%S")
    run_id = base_run_id
    suffix = 1
    while os.path.exists(os.path.join(HITS_DIR, f"hits_{run_id}.json")):
        suffix += 1
        run_id = f"{base_run_id}_{suffix}"

    record = {
        "run_id": run_id,
        "dataset": dataset,
        "dataset_label": dataset_label,
        "custom_path": custom_path,
        "data_issues": data_issues,
        "started_at": started.isoformat(timespec="seconds"),
        "finished_at": finished.isoformat(timespec="seconds"),
        "summary": summary,
        "results": results,
    }

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

    def _send_file(self, path, content_type):
        try:
            with open(path, "rb") as f:
                body = f.read()
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except FileNotFoundError:
            self._send_json({"error": f"文件不存在：{path}"}, status=404)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        if path in ("/", "/index.html"):
            self._send_file(INDEX_PATH, "text/html; charset=utf-8")
            return

        if path == "/api/rules":
            try:
                self._send_json(load_rules())
            except Exception as e:
                self._send_json({"error": str(e)}, status=500)
            return

        if path == "/api/datasets":
            try:
                self._send_json({
                    "datasets": ds.list_datasets(),
                    "has_api_key": checker.has_llm_credentials(),
                    "llm_runtime": checker.describe_llm_runtime(),
                })
            except Exception as e:
                self._send_json({"error": str(e)}, status=500)
            return

        # ③ 命中结果：列表 + 单次详情
        if path == "/api/runs":
            try:
                self._send_json({"runs": report_mod.list_runs()})
            except Exception as e:
                self._send_json({"error": str(e)}, status=500)
            return

        if path.startswith("/api/runs/"):
            run_id = path[len("/api/runs/"):]
            try:
                self._send_json(report_mod.load_run(run_id))
            except ValueError as e:
                self._send_json({"error": str(e)}, status=404)
            except Exception as e:
                self._send_json({"error": str(e)}, status=500)
            return

        # ④ 分析报告：生成 + 导出
        if path.startswith("/api/report/"):
            run_id = path[len("/api/report/"):]
            want_export = query.get("export", ["0"])[0] == "1"
            try:
                run = report_mod.load_run(run_id)
                rep = report_mod.build_report(run)
                if want_export:
                    out = report_mod.export_html(rep)
                    self._send_json({"status": "ok", "export_path": out, "report": rep})
                else:
                    self._send_json(rep)
            except ValueError as e:
                self._send_json({"error": str(e)}, status=404)
            except Exception as e:
                self._send_json({"error": str(e)}, status=500)
            return

        self._send_json({"error": "未知路径"}, status=404)

    def do_POST(self):
        path = urlparse(self.path).path

        if path == "/api/rules":
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

        if path == "/api/run":
            length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(length)
            try:
                body = json.loads(raw.decode("utf-8")) if raw else {}
                record, out_path = run_dataset(
                    body.get("dataset"),
                    custom_path=body.get("custom_path"),
                    workers=int(body.get("workers") or 1),
                )
                self._send_json({
                    "status": "ok",
                    "run_id": record["run_id"],
                    "dataset_label": record["dataset_label"],
                    "data_issues": record["data_issues"],
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
        print(f"[server] {self.command} {self.path} -> {args[1] if len(args) > 1 else ''}")


def main():
    if not os.path.exists(RULES_PATH):
        print(f"错误：找不到 {RULES_PATH}")
        return
    server = HTTPServer(("127.0.0.1", PORT), Handler)
    print(f"合规工作台已启动：http://127.0.0.1:{PORT}")
    print(f"当前 LLM 运行时：{checker.describe_llm_runtime()}")
    # 只报"从哪个文件读到的"，不打印key本身——方便你确认自动加载到底生没生效，
    # 而不用去猜是文件没找到、还是文件里没写对。
    if checker.LOADED_ENV_FILE:
        print(f"  （key 是从本地文件自动读取的：{checker.LOADED_ENV_FILE}）")
    elif not (os.environ.get("DEEPSEEK_API_KEY") or os.environ.get("ANTHROPIC_API_KEY")):
        print("  （没有找到任何 key：既没有手动 export，也没找到本地 .env 文件）")
    print(f"可用数据集：{len(ds.list_datasets())} 个（往 数据集/ 里丢CSV即可自动出现）")
    print("按 Ctrl+C 停止")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n已停止")


if __name__ == "__main__":
    main()
