#!/bin/bash
# 双击这个文件（在 Finder 里双击，不是在终端里）直接跑一次评测，
# 不用开浏览器、不用敲命令、不用管key在哪——会自动从 .env 或旧的 .env.deepseek 里读取。
# 跑完会在这个窗口里直接打印出结果摘要，同时结果也会存进 命中结果/ 文件夹，
# 网页上的③④两个tab随时能看到同样的结果。
cd "$(dirname "$0")/规则执行"
python3 run_dataset_cli.py
echo ""
echo "按任意键关闭这个窗口……"
read -n 1 -s
