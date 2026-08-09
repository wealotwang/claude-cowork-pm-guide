#!/bin/bash
# 双击这个文件（在 Finder 里双击，不是在终端里）就能启动合规工作台网页，
# 不用打开终端、不用敲任何命令。key 会自动从 .env 或旧的 .env.deepseek 里读取。
cd "$(dirname "$0")"
(sleep 1 && open "http://127.0.0.1:8787") &
python3 server.py
echo ""
echo "服务已停止。按任意键关闭这个窗口……"
read -n 1 -s
