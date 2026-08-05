#!/usr/bin/env python3
"""
AI Compliance Check Assistant - 最小可运行 demo（Day05/06 产出）

架构：混合两层判断，不是所有内容都上 LLM。
  1. regex 前置层：结构化、格式固定的 PII（身份证号/手机号/病历号标注）用正则直接判 05 类 Block，
     快、准、不花 token。
  2. LLM 判断层：01(商业贿赂)/07(夸大疗效)/10(合规兜底) 这三类，难点在语义关系判断
     （比如"讲课费"本身不违规，判断关键是有没有和处方量/进院挂钩），交给 LLM 结合规则说明
     + 违规示例 + 边界示例来判断。

用法：
    export ANTHROPIC_API_KEY="你自己的 key"   # 必须由你自己在终端设置，本脚本不存储/不上传这个值
    python3 checker.py "这个月表现不错，给你包个红包"

规则定义、违规示例、边界示例全部读自同目录下的 rules_config.json，不在代码里硬编码，
方便后续加类别或改规则时不用改代码。
"""

import json
import os
import re
import sys
import urllib.request
import urllib.error

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(SCRIPT_DIR, "rules_config.json")

ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_VERSION = "2023-06-01"
# 可以用环境变量 CHECKER_MODEL 覆盖，默认用一个判断质量优先的模型
DEFAULT_MODEL = os.environ.get("CHECKER_MODEL", "claude-sonnet-5")


def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def regex_prefilter(text, config):
    """结构化 PII 检测，命中即返回 05 类 Block 结果，不需要调用 LLM。"""
    cat = config["regex_categories"]["05"]
    for p in cat["patterns"]:
        if re.search(p["regex"], text):
            return {
                "input": text,
                "matched_category": "05",
                "category_name": cat["name"],
                "risk_level": cat["risk_level"],
                "action": cat["action"],
                "rationale": f"命中结构化PII正则规则：{p['label']}，未脱敏直接暴露患者可识别信息。",
                "matched_by": "regex",
            }
    return None


def build_llm_system_prompt(config):
    """把 01/07/10 的规则说明+违规示例+边界示例拼成给 LLM 的系统提示词。"""
    cats = config["llm_categories"]
    lines = [
        "你是一个医药代表 CRM 拜访记录的合规审核助手。给定一段拜访记录文本，判断它应该命中下面哪一类规则，"
        "如果都不命中，判为 10 类（Pass，默认兜底）。",
        "",
        "判断的关键不是有没有出现敏感词，而是内容的实际语义关系（比如费用有没有和处方量/进院挂钩、"
        "疗效描述有没有超出说明书范围或做绝对化承诺）。",
        "",
        "只返回一个 JSON 对象，不要有任何其他文字，格式：",
        '{"matched_category": "01|07|10", "risk_level": "...", "action": "Reject|Warning|Pass", "rationale": "一句话说明依据"}',
        "",
        "可选类别定义：",
    ]
    for cat_id in ["01", "07", "10"]:
        c = cats[cat_id]
        lines.append(f"\n【{cat_id} {c['name']}】风险等级={c['risk_level']}，命中后动作={c['action_if_hit']}")
        lines.append(f"规则说明：{c['description']}")
        if c.get("violation_examples"):
            lines.append("违规示例：" + "；".join(c["violation_examples"]))
        if c.get("boundary_examples_should_pass"):
            lines.append("容易误判但其实应该放行的边界示例：" + "；".join(c["boundary_examples_should_pass"]))
        if c.get("should_pass_examples"):
            lines.append("应该判 Pass 的样例：" + "；".join(c["should_pass_examples"]))
    return "\n".join(lines)


def llm_classify(text, config):
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError(
            "没有找到 ANTHROPIC_API_KEY 环境变量。请先在你自己的终端里运行："
            '\n    export ANTHROPIC_API_KEY="你的key"\n再重新运行本脚本。这个值不会被本脚本存储或上传到任何地方。'
        )

    system_prompt = build_llm_system_prompt(config)
    body = {
        "model": DEFAULT_MODEL,
        "max_tokens": 300,
        "system": system_prompt,
        "messages": [{"role": "user", "content": text}],
    }
    req = urllib.request.Request(
        ANTHROPIC_API_URL,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "x-api-key": api_key,
            "anthropic-version": ANTHROPIC_VERSION,
            "content-type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            resp_data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"调用 Anthropic API 失败：HTTP {e.code} - {e.read().decode('utf-8', 'ignore')}")

    raw_text = "".join(block.get("text", "") for block in resp_data.get("content", []))

    # 防御性解析：从返回文本里找第一个 JSON 对象
    match = re.search(r"\{.*\}", raw_text, re.DOTALL)
    if not match:
        raise RuntimeError(f"LLM 返回内容无法解析为 JSON，原始返回：{raw_text}")
    parsed = json.loads(match.group(0))

    cat_id = parsed.get("matched_category", "10")
    cat_meta = config["llm_categories"].get(cat_id, config["llm_categories"]["10"])

    return {
        "input": text,
        "matched_category": cat_id,
        "category_name": cat_meta["name"],
        "risk_level": parsed.get("risk_level", cat_meta["risk_level"]),
        "action": parsed.get("action", cat_meta.get("action_if_hit", "Pass")),
        "rationale": parsed.get("rationale", ""),
        "matched_by": "llm",
    }


def classify(text, config=None):
    """主入口：先 regex，再 LLM。"""
    if config is None:
        config = load_config()
    result = regex_prefilter(text, config)
    if result:
        return result
    return llm_classify(text, config)


def main():
    if len(sys.argv) < 2:
        print('用法: python3 checker.py "要检查的拜访记录文本"')
        sys.exit(1)
    text = sys.argv[1]
    config = load_config()
    try:
        result = classify(text, config)
    except RuntimeError as e:
        print(f"错误：{e}")
        sys.exit(1)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
