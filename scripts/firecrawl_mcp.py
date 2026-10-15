#!/usr/bin/env python3
"""Připojení k Firecrawl MCP (https://mcp.firecrawl.dev/v2/mcp) s klíčem ze souboru .env.

Klíč (FIRECRAWL_API_KEY) se čte jen ze souboru .env v kořeni repozitáře a nikdy se
nevypisuje. Když chybí, připojení proběhne bez klíče (veřejný přístup s denním limitem).

Použití:
    python3 scripts/firecrawl_mcp.py --headers
        Hlavičky pro Claude Code (headersHelper v .claude/agents/*.md): JSON s Authorization,
        nebo {} bez klíče.
    python3 scripts/firecrawl_mcp.py --check
        Ověří nastavení: zda je klíč v .env a zda se připojení podaří. Klíč nevypisuje.

Modul používá i scripts/check_quotes.py. Používá jen standardní knihovnu Pythonu.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

ENDPOINT = "https://mcp.firecrawl.dev/v2/mcp"
ENV_FILE = Path(__file__).resolve().parents[1] / ".env"
KEY_LINE = re.compile(r"^\s*FIRECRAWL_API_KEY\s*=\s*(.*?)\s*$")
# Parametry, se kterými se Firecrawl v projektu volá (kontroluje je i hook agentů).
SCRAPE_ARGUMENTS = {"formats": ["markdown"], "maxAge": 0, "onlyMainContent": False}


def read_key(path: Path = ENV_FILE) -> str:
    """Vrátí FIRECRAWL_API_KEY ze souboru .env, nebo prázdný řetězec."""
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (FileNotFoundError, PermissionError, UnicodeDecodeError):
        return ""
    key = ""
    for line in lines:
        match = KEY_LINE.match(line)
        if match:
            key = match.group(1).strip().strip("\"'")
    return key


def auth_headers(path: Path = ENV_FILE) -> dict[str, str]:
    key = read_key(path)
    return {"Authorization": f"Bearer {key}"} if key else {}


class McpSession:
    """Minimální klient MCP přes Streamable HTTP (initialize, tools/list, tools/call)."""

    def __init__(self, headers: dict[str, str], timeout: int = 180) -> None:
        self.headers = {"Content-Type": "application/json",
                        "Accept": "application/json, text/event-stream", **headers}
        self.timeout = timeout
        self.session: str | None = None
        self._post({"jsonrpc": "2.0", "id": 1, "method": "initialize",
                    "params": {"protocolVersion": "2025-06-18", "capabilities": {},
                               "clientInfo": {"name": "investor-database", "version": "1"}}})
        self._post({"jsonrpc": "2.0", "method": "notifications/initialized"})

    def _post(self, payload: dict) -> list[dict]:
        headers = dict(self.headers)
        if self.session:
            headers["Mcp-Session-Id"] = self.session
        request = urllib.request.Request(ENDPOINT, json.dumps(payload).encode(), headers)
        with urllib.request.urlopen(request, timeout=self.timeout) as response:
            body = response.read().decode("utf-8", "replace")
            self.session = response.headers.get("Mcp-Session-Id", self.session)
        messages = [json.loads(line[5:]) for line in body.splitlines() if line.startswith("data:")]
        if not messages and body.strip():
            messages = [json.loads(body)]
        return messages

    def tools(self) -> list[str]:
        result = self._post({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})[0]["result"]
        return [tool["name"] for tool in result["tools"]]

    def call(self, name: str, arguments: dict) -> str:
        """Zavolá nástroj a vrátí jeho textový výstup."""
        message = self._post({"jsonrpc": "2.0", "id": 3, "method": "tools/call",
                              "params": {"name": name, "arguments": arguments}})[0]
        if "error" in message:
            return json.dumps({"success": False, "error": message["error"].get("message", "")})
        content = message["result"].get("content", [])
        return "".join(part.get("text", "") for part in content if part.get("type") == "text")


def scrape(url: str) -> str:
    """Jedno volání firecrawl_scrape se schválenými parametry. Vrací textový výstup nástroje."""
    return McpSession(auth_headers()).call("firecrawl_scrape", {"url": url, **SCRAPE_ARGUMENTS})


def check() -> int:
    has_key = bool(read_key())
    print(f"Klíč FIRECRAWL_API_KEY v {ENV_FILE.name}: {'ano' if has_key else 'ne (přístup bez klíče)'}")
    try:
        tools = McpSession(auth_headers(), timeout=60).tools()
    except urllib.error.HTTPError as err:
        print(f"Připojení selhalo: HTTP {err.code}" + (" (klíč je zřejmě neplatný)" if err.code in (401, 403) else ""))
        return 1
    except (urllib.error.URLError, OSError, ValueError, KeyError, IndexError) as err:
        print(f"Připojení selhalo: {type(err).__name__}")
        return 1
    authenticated = len(tools) > 3
    print(f"Připojení: OK, nástrojů {len(tools)}, "
          f"{'s klíčem (plný přístup)' if authenticated else 'bez klíče (omezený přístup)'}")
    print(f"firecrawl_scrape dostupný: {'ano' if 'firecrawl_scrape' in tools else 'ne'}")
    if has_key and not authenticated:
        print("Pozor: klíč je v .env, ale server odpověděl jako bez klíče.")
        return 1
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Firecrawl MCP s klíčem z .env.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--headers", action="store_true", help="vypsat hlavičky pro headersHelper")
    mode.add_argument("--check", action="store_true", help="ověřit klíč a připojení")
    args = parser.parse_args(argv)
    if args.headers:
        print(json.dumps(auth_headers()))
        return 0
    return check()


if __name__ == "__main__":
    sys.exit(main())
