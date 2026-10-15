#!/usr/bin/env python3
"""PreToolUse hook agentů (.claude/agents/*.md): kontrola skutečných parametrů Firecrawlu.

Pustí jen nástroj firecrawl_scrape s parametry, na kterých stojí ověřování citací:
- url je úplná adresa http(s),
- formats je přesně ["markdown"] (žádné formáty zpracované jazykovým modelem),
- maxAge je 0 (čerstvá verze, ne cache),
- onlyMainContent je false (celá stránka včetně patičky).

Jiné volání zablokuje a agentovi vrátí důvod. Když vstup nejde přečíst, volání také
zablokuje (selhání nesmí volání propustit).
"""

import json
import sys
from urllib.parse import urlparse

ALLOWED_TOOL = "mcp__firecrawl__firecrawl_scrape"
ALLOWED_KEYS = {"url", "formats", "maxAge", "onlyMainContent", "waitFor", "timeout", "parsers", "proxy"}
RULE = 'Povoleno: firecrawl_scrape s url (http/https), formats ["markdown"], maxAge 0, onlyMainContent false.'


def problems(tool_name: str, tool_input: dict) -> list[str]:
    if tool_name != ALLOWED_TOOL:
        return [f"nástroj {tool_name.rsplit('__', 1)[-1]} není povolený, z Firecrawlu jen firecrawl_scrape"]
    issues = []
    url = tool_input.get("url")
    parsed = urlparse(url) if isinstance(url, str) else None
    if not parsed or parsed.scheme not in ("http", "https") or not parsed.netloc or " " in url:
        issues.append("url není úplná adresa http(s)")
    if tool_input.get("formats") != ["markdown"]:
        issues.append(f"formats je {json.dumps(tool_input.get('formats'))}, musí být [\"markdown\"]")
    max_age = tool_input.get("maxAge")
    if isinstance(max_age, bool) or not isinstance(max_age, (int, float)) or max_age != 0:
        issues.append(f"maxAge je {json.dumps(max_age)}, musí být 0")
    if tool_input.get("onlyMainContent") is not False:
        issues.append(f"onlyMainContent je {json.dumps(tool_input.get('onlyMainContent'))}, musí být false")
    extra = sorted(set(tool_input) - ALLOWED_KEYS)
    if extra:
        issues.append("nepovolené parametry: " + ", ".join(extra))
    return issues


def decision(raw: str) -> dict | None:
    try:
        data = json.loads(raw)
        issues = problems(data.get("tool_name", ""), data.get("tool_input") or {})
    except (ValueError, AttributeError, TypeError):
        issues = ["vstup hooku nejde přečíst"]
    if not issues:
        return None
    return {"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": "Volání Firecrawlu zablokovala kontrola parametrů: "
                                    + "; ".join(issues) + ". " + RULE,
    }}


def main() -> int:
    result = decision(sys.stdin.read())
    if result:
        print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
