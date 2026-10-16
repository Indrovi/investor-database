#!/usr/bin/env python3
"""Vypíše zůstatek kreditů Firecrawlu. Klíč se čte z .env přes scripts/firecrawl_mcp.py a nevypisuje se.

Použití: python3 scripts/pilot/credits.py
"""
import json
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import firecrawl_mcp  # noqa: E402

request = urllib.request.Request("https://api.firecrawl.dev/v2/team/credit-usage",
                                 headers={"Authorization": f"Bearer {firecrawl_mcp.read_key()}"})
with urllib.request.urlopen(request, timeout=30) as response:
    data = json.load(response).get("data", {})
print({key: value for key, value in data.items() if "credit" in key.lower() or "billing" in key.lower()})
