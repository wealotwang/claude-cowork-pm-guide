#!/usr/bin/env python3
"""
规则配置模块 - 本地服务

【已归档，不再是当前生效版本】这份文件已经升级为统一后端，当前生效版本是
../server.py（同时支持规则配置 + 规则执行两个tab），配套前端是 ../index.html。
这份文件保留作为Module 1单独开发阶段的历史快照，不建议再从这里启动。

这是"05-产品原型"合规工作台四个模块里的第一个（规则配置）。用一个纯标准库的本地
HTTP 服务 + 单页 HTML 前端，让你能在浏览器里直接看/改 rules_config.json 里的每条
规则，不用手改 JSON 文本、不用担心少个逗号改坏格式。

不依赖任何第三方包（不用 pip install 任何东西），只用 Python 标准库的 http.server。

用法：
    cd "05-产品原型/规则配置"
    python3 server.py
    # 然后浏览器打开 http://127.0.0.1:8787

这一步只负责"规则配置"本身的读写，不涉及跑评测、不调用任何 LLM API，
所以不需要设置 DEEPSEEK_API_KEY 之类的东西——那是"规则执行"模块（下一步）的事。

保存后，checker.py（在 ../../03-学习成果/demo/checker.py）会直接读到你在这里改的内容，
因为两边指向的是同一份 rules_config.json，不存在"改了这里、那边没同步"的问题。
"""

import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RULES_PATH = os.path.join(SCRIPT_DIR, "rules_config.json")
INDEX_PATH = os.path.join(SCRIPT_DIR, "index.html")
PORT = 8787

REQUIRED_CATEGORY_FIELDS = {"name", "risk_level", "action", "description", "examples", "boundary_examples"}


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

        self._send_json({"error": "未知路径"}, status=404)

    def do_POST(self):
        if self.path != "/api/rules":
            self._send_json({"error": "未知路径"}, status=404)
            return

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

    def log_message(self, format, *args):
        # 精简一下默认日志，只保留方法+路径+状态码
        print(f"[server] {self.command} {self.path} -> {args[1] if len(args) > 1 else ''}")


def main():
    if not os.path.exists(RULES_PATH):
        print(f"错误：找不到 {RULES_PATH}")
        return
    server = HTTPServer(("127.0.0.1", PORT), Handler)
    print(f"规则配置编辑器已启动：http://127.0.0.1:{PORT}")
    print("按 Ctrl+C 停止")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n已停止")


if __name__ == "__main__":
    main()
