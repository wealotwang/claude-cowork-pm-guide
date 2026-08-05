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
    # 推荐 Day06 直接走 DeepSeek 路线
    export DEEPSEEK_API_KEY="你自己的 key"   # 必须由你自己在终端设置，本脚本不存储/不上传这个值
    python3 checker.py "这个月表现不错，给你包个红包"

    # 如果未来要切回 Anthropic，也仍然支持
    export ANTHROPIC_API_KEY="你自己的 key"
    python3 checker.py "这个月表现不错，给你包个红包"

当前版本已经按三层拆开：
  - 固定 system prompt：../Day06-System-Prompt-固定模板.md
  - 用户规则配置：../Day06-用户规则配置模板-v2.2.json
  - 内部实现增强：保留在代码里（例如 05 类结构化 PII 检测）
"""

import json
import os
import re
import socket
import sys
import urllib.error
import urllib.request

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ARTIFACTS_DIR = os.path.dirname(SCRIPT_DIR)
USER_RULES_PATH = os.path.join(ARTIFACTS_DIR, "Day06-用户规则配置模板-v2.2.json")
SYSTEM_PROMPT_DOC_PATH = os.path.join(ARTIFACTS_DIR, "Day06-System-Prompt-固定模板.md")

ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_VERSION = "2023-06-01"
DEEPSEEK_API_URL = os.environ.get("DEEPSEEK_API_URL", "https://api.deepseek.com/chat/completions")
DEFAULT_ANTHROPIC_MODEL = os.environ.get("ANTHROPIC_MODEL", os.environ.get("CHECKER_MODEL", "claude-sonnet-5"))
DEFAULT_DEEPSEEK_MODEL = os.environ.get("DEEPSEEK_MODEL", os.environ.get("CHECKER_MODEL", "deepseek-v4-flash"))

INTERNAL_STRUCTURED_DETECTORS = {
    "05": [
        {
            "label": "身份证号(18位)",
            "regex": r"[1-9]\d{5}(18|19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d{3}[\dXx]",
        },
        {"label": "手机号", "regex": r"1[3-9]\d{9}"},
        {"label": "病案号/病历号标注", "regex": r"病案号[:：]?\s*\S+|病历号[:：]?\s*\S+"},
    ]
}


def load_config():
    with open(USER_RULES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def load_system_prompt_template():
    with open(SYSTEM_PROMPT_DOC_PATH, "r", encoding="utf-8") as f:
        content = f.read()
    match = re.search(r"```(?:text)?\n(.*?)\n```", content, re.DOTALL)
    if not match:
        raise RuntimeError(f"无法从 {SYSTEM_PROMPT_DOC_PATH} 提取固定 system prompt 模板。")
    return match.group(1).strip()


def regex_prefilter(text, config):
    """系统内部结构化识别增强：当前先覆盖 05 类结构化 PII。"""
    cat = config["categories"]["05"]
    for p in INTERNAL_STRUCTURED_DETECTORS["05"]:
        if re.search(p["regex"], text):
            return {
                "input": text,
                "matched_category": "05",
                "matched_rule_id": "05",
                "category_name": cat["name"],
                "matched_rule_name": cat["name"],
                "risk_level": cat["risk_level"],
                "action": cat["action"],
                "rationale": f"命中结构化PII正则规则：{p['label']}，未脱敏直接暴露患者可识别信息。",
                "matched_by": "regex",
            }
    return None


def render_user_rules_for_prompt(config):
    lines = [
        f"当前启用规则总数：{len(config['categories'])}",
        f"默认通过规则ID：{config['default_rule_id']}",
        f"允许输出的动作：{', '.join(config.get('action_space', []))}",
        "",
        "当前启用规则如下：",
    ]
    for rule_id, rule in sorted(config["categories"].items()):
        lines.append(
            f"\n【{rule_id} {rule['name']}】风险等级={rule['risk_level']}，命中后动作={rule['action']}"
        )
        lines.append(f"规则说明：{rule['description']}")
        if rule.get("examples"):
            lines.append("违规示例：" + "；".join(rule["examples"]))
        if rule.get("boundary_examples"):
            lines.append("边界示例/应避免误报的样例：" + "；".join(rule["boundary_examples"]))
    return "\n".join(lines)


def build_llm_system_prompt(config):
    """固定 system prompt + 当前启用规则配置，拼成真正发送给 LLM 的系统提示词。"""
    template = load_system_prompt_template()
    rules_block = render_user_rules_for_prompt(config)
    lines = [
        template,
        "",
        "下面是本次审核时动态传入的用户规则配置：",
        rules_block,
    ]
    return "\n".join(lines)


def get_llm_runtime():
    """自动选择当前可用的 LLM 提供方，优先 DeepSeek，其次 Anthropic。"""
    deepseek_api_key = os.environ.get("DEEPSEEK_API_KEY")
    if deepseek_api_key:
        return {
            "provider": "deepseek",
            "api_key": deepseek_api_key,
            "model": DEFAULT_DEEPSEEK_MODEL,
            "api_url": DEEPSEEK_API_URL,
        }

    anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY")
    if anthropic_api_key:
        return {
            "provider": "anthropic",
            "api_key": anthropic_api_key,
            "model": DEFAULT_ANTHROPIC_MODEL,
            "api_url": ANTHROPIC_API_URL,
        }

    return None


def has_llm_credentials():
    return get_llm_runtime() is not None


def describe_llm_runtime():
    runtime = get_llm_runtime()
    if not runtime:
        return "未配置 LLM 凭证"
    return f"{runtime['provider']} / {runtime['model']}"


def extract_first_json_object(raw_text):
    """防御性解析：从模型输出里提取第一个 JSON 对象。"""
    match = re.search(r"\{.*\}", raw_text, re.DOTALL)
    if not match:
        raise RuntimeError(f"LLM 返回内容无法解析为 JSON，原始返回：{raw_text}")
    return json.loads(match.group(0))


def call_anthropic(text, system_prompt, runtime):
    body = {
        "model": runtime["model"],
        "max_tokens": 300,
        "system": system_prompt,
        "messages": [{"role": "user", "content": text}],
    }
    req = urllib.request.Request(
        runtime["api_url"],
        data=json.dumps(body).encode("utf-8"),
        headers={
            "x-api-key": runtime["api_key"],
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
    except (urllib.error.URLError, TimeoutError, socket.timeout) as e:
        raise RuntimeError(f"调用 Anthropic API 超时或网络失败：{e}")

    raw_text = "".join(block.get("text", "") for block in resp_data.get("content", []))
    return extract_first_json_object(raw_text)


def call_deepseek(text, system_prompt, runtime):
    body = {
        "model": runtime["model"],
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text},
        ],
        "max_tokens": 300,
        "temperature": 0,
    }
    req = urllib.request.Request(
        runtime["api_url"],
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {runtime['api_key']}",
            "content-type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            resp_data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"调用 DeepSeek API 失败：HTTP {e.code} - {e.read().decode('utf-8', 'ignore')}")
    except (urllib.error.URLError, TimeoutError, socket.timeout) as e:
        raise RuntimeError(f"调用 DeepSeek API 超时或网络失败：{e}")

    raw_text = resp_data.get("choices", [{}])[0].get("message", {}).get("content", "")
    return extract_first_json_object(raw_text)


def llm_classify(text, config):
    runtime = get_llm_runtime()
    if not runtime:
        raise RuntimeError(
            "没有找到可用的 LLM key。Day06 推荐直接在你自己的终端里运行："
            '\n    export DEEPSEEK_API_KEY="你的key"'
            "\n如果你未来要切回 Anthropic，也仍然支持："
            '\n    export ANTHROPIC_API_KEY="你的key"'
            "\n再重新运行本脚本。这个值不会被本脚本存储或上传到任何地方。"
        )

    system_prompt = build_llm_system_prompt(config)
    if runtime["provider"] == "deepseek":
        parsed = call_deepseek(text, system_prompt, runtime)
    else:
        parsed = call_anthropic(text, system_prompt, runtime)

    default_rule_id = config.get("default_rule_id", "10")
    cat_id = str(parsed.get("matched_rule_id") or parsed.get("matched_category") or default_rule_id)
    cat_meta = config["categories"].get(cat_id, config["categories"][default_rule_id])
    action = parsed.get("action", cat_meta.get("action", "Pass"))
    if config.get("action_space") and action not in config["action_space"]:
        action = cat_meta.get("action", "Pass")

    return {
        "input": text,
        "matched_category": cat_id,
        "matched_rule_id": cat_id,
        "category_name": cat_meta["name"],
        "matched_rule_name": cat_meta["name"],
        "risk_level": parsed.get("risk_level", cat_meta["risk_level"]),
        "action": action,
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
