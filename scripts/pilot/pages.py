#!/usr/bin/env python3
"""Uloží stránky, které Firecrawl už vrátil agentům, do .cache/pages/ (bez nových volání).

Agenti pak čtou uloženou kopii místo nového stažení (šetří kredity) a kontrola citací
(verify_quotes.py) ji použije, když stránka přímo nejde stáhnout.

index.tsv: url, soubor, datum stažení (podle záznamu běhu), statusCode, záznam běhu.
Při více kopiích platí nejnovější. Spouští se po každém běhu agenta (run_one.sh to dělá sám).

Použití: python3 scripts/pilot/pages.py
"""
import glob
import hashlib
import json
import os
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / ".cache" / "pages"


def scrapes(path):
    pending = {}
    for line in open(path, encoding="utf-8"):
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        message = event.get("message")
        if not isinstance(message, dict) or not isinstance(message.get("content"), list):
            continue
        for part in message["content"]:
            if part.get("type") == "tool_use" and part.get("name") == "mcp__firecrawl__firecrawl_scrape":
                pending[part["id"]] = part["input"].get("url", "")
            elif part.get("type") == "tool_result" and part.get("tool_use_id") in pending:
                url = pending.pop(part["tool_use_id"])
                content = part.get("content")
                text = content if isinstance(content, str) else "".join(
                    c.get("text", "") for c in content or [] if isinstance(c, dict))
                try:
                    doc = json.loads(text)
                except ValueError:
                    continue
                doc = doc.get("data", doc) if isinstance(doc, dict) else {}
                if doc.get("markdown"):
                    yield url, doc["markdown"], doc.get("metadata", {})


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    best = {}
    for log in sorted(glob.glob(str(ROOT / ".cache/agents/**/*.jsonl"), recursive=True)):
        mtime = os.path.getmtime(log)
        for url, markdown, meta in scrapes(log):
            if meta.get("statusCode") != 200:
                continue
            if url not in best or best[url][0] <= mtime:
                best[url] = (mtime, markdown, meta, log)
    rows = []
    for url, (mtime, markdown, meta, log) in sorted(best.items()):
        name = hashlib.sha1(url.encode()).hexdigest()[:12] + ".md"
        (OUT / name).write_text(markdown, encoding="utf-8")
        rows.append("\t".join([url, f".cache/pages/{name}", date.fromtimestamp(mtime).isoformat(),
                               str(meta.get("statusCode")), os.path.relpath(log, ROOT)]))
    (OUT / "index.tsv").write_text("url\tsoubor\tstazeno\tstatusCode\tzaznam\n" + "\n".join(rows) + "\n",
                                   encoding="utf-8")
    print(f"Uloženo {len(rows)} stránek do {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
