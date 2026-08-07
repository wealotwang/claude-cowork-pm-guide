#!/usr/bin/env python3
"""
AI Compliance Check Assistant - 核心判断引擎

迁移说明：从 03-学习成果/demo/checker.py 迁移而来（原文件已归档，标注指向这里）。
这是"规则执行"模块的核心，被 CLI（本文件直接运行）和本地网页工具（../server.py）共用。

架构：全部规则统一交给 LLM 判断，不用 regex 做前置匹配（Day07 的架构决策，详见
../CHANGELOG.md 和 03-学习成果/Day07-架构调整-去掉regex改纯LLM.md）。

用法：
    export DEEPSEEK_API_KEY="你自己的 key"   # 必须由你自己在终端设置，本脚本不存储/不上传这个值
    python3 checker.py "这个月表现不错，给你包个红包"

    # 如果要切回 Anthropic，也仍然支持
    export ANTHROPIC_API_KEY="你自己的 key"

读取的文件（同属05-产品原型，跟本文件是兄弟目录）：
  - 固定 system prompt：../规则配置/system_prompt.md
  - 用户规则配置：../规则配置/rules_config.json（业务人员唯一需要打交道的文件，纯自然语言）
  - 内部实现增强：已清空，不再有任何 regex/detector（历史见 ../规则配置/内部实现说明.md）
"""

import json
import os
import re
import socket
import sys
import urllib.error
import urllib.request

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PRODUCT_ROOT = os.path.dirname(SCRIPT_DIR)  # 05-产品原型/
RULES_DIR = os.path.join(PRODUCT_ROOT, "规则配置")
USER_RULES_PATH = os.path.join(RULES_DIR, "rules_config.json")
SYSTEM_PROMPT_DOC_PATH = os.path.join(RULES_DIR, "system_prompt.md")

ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_VERSION = "2023-06-01"
DEEPSEEK_API_URL = os.environ.get("DEEPSEEK_API_URL", "https://api.deepseek.com/chat/completions")
DEFAULT_ANTHROPIC_MODEL = os.environ.get("ANTHROPIC_MODEL", os.environ.get("CHECKER_MODEL", "claude-sonnet-5"))
DEFAULT_DEEPSEEK_MODEL = os.environ.get("DEEPSEEK_MODEL", os.environ.get("CHECKER_MODEL", "deepseek-v4-flash"))

# 300 太紧了：Day07 验证 MB143 时实测到一次返回被截断（"rationale": "该 后直接断在这），
# 因为 JSON 里 rationale 是完整句子，配合较长的 matched_rule_name，输出经常压线甚至超过 300 tokens。
# 提高到 600 留出安全余量，避免因为截断导致"明明分类判对了，却因为解析不出JSON而报错"。
LLM_MAX_TOKENS = 600


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
        "max_tokens": LLM_MAX_TOKENS,
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
        "max_tokens": LLM_MAX_TOKENS,
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
            "没有找到可用的 LLM key。推荐直接在你自己的终端里运行："
            '\n    export DEEPSEEK_API_KEY="你的key"'
            "\n如果你未来要切回 Anthropic，也仍然支持："
            '\n    export ANTHROPIC_API_KEY="你的key"'
            "\n再重新运行本脚本/重启server.py。这个值不会被本脚本存储或上传到任何地方。"
        )

    system_prompt = build_llm_system_prompt(config)
    call_fn = call_deepseek if runtime["provider"] == "deepseek" else call_anthropic

    # Day07 实测发现：就算把 max_tokens 提到 600，LLM 仍然偶尔会把 JSON 截断或返回异常内容
    # （非必现，同一条 case 重跑一次可能就正常了）。与其指望一次调用永远稳定，不如失败了
    # 就重试一次——这是内部实现层的健壮性，不涉及规则内容，用户不需要关心这层。
    last_error = None
    parsed = None
    for attempt in range(2):
        try:
            parsed = call_fn(text, system_prompt, runtime)
            break
        except RuntimeError as e:
            last_error = e
    if parsed is None:
        raise RuntimeError(f"重试一次后仍然失败：{last_error}")

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
    """主入口：统一走 LLM 判断，不再有 regex 前置层。"""
    if config is None:
        config = load_config()
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
