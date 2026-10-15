#!/usr/bin/env python3
"""Spouštění agentů a předávání tvrzení souborem (nástroj koordinátora, docs/agenti.md).

Agent běží přímo jako relace Claude Code (`claude -p --agent`), takže jeho výstup se uloží
do souboru přesně tak, jak ho agent vrátil. Auditor dostane tvrzení v souboru JSON, který
si načte nástrojem Read. Žádný jazykový model mezi tím text nepřepisuje, a citace se tak
nemohou změnit (např. typografické apostrofy).

Použití:
    python3 scripts/agents.py run investor-source-scout --prompt-file ZADANI.txt --out .cache/agents/BEH
        Spustí agenta, uloží záznam relace (AGENT.jsonl) a výstup (AGENT.md) a vypíše volání Firecrawlu.
    python3 scripts/agents.py handoff .cache/agents/BEH/investor-source-scout.md --investor "Název" \\
            --out .cache/agents/BEH/handoff.json
        Sestaví předání pro auditora. Neúplný řádek (bez ID, úplné URL nebo citace) předání odmítne.
    python3 scripts/agents.py calls .cache/agents/BEH/investor-evidence-auditor.jsonl
        Vypíše skutečná volání Firecrawlu: nástroj, URL, parametry, výsledek.

Adresář .cache/ je v .gitignore. Používá jen standardní knihovnu Pythonu.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import check_quotes

AGENT_TOOLS = "Read Grep Glob WebSearch WebFetch mcp__firecrawl__firecrawl_scrape"
CLAIM_COLUMNS = ("entita", "pole", "hodnota")


# --- Záznam relace (stream-json) ---

def events(path: Path):
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                continue


def final_result(path: Path) -> dict:
    return next((event for event in events(path) if event.get("type") == "result"), {})


def _tool_result_text(content) -> str:
    if isinstance(content, str):
        return content
    return "".join(part.get("text", "") for part in content or [] if isinstance(part, dict))


def _outcome(text: str, is_error: bool) -> str:
    if "kontrola parametrů" in text:
        return "zablokováno hookem: " + text.split("kontrola parametrů:", 1)[-1].split(". Povoleno")[0].strip()
    try:
        document = json.loads(text)
    except ValueError:
        return "chyba: " + " ".join(text.split())[:100] if is_error or text else "bez výstupu"
    if document.get("success") is False:
        return f"chyba: {document.get('code') or document.get('error')}"
    metadata = document.get("data", document).get("metadata", {})
    return f"statusCode {metadata.get('statusCode')}" + (f" ({metadata['error']})" if metadata.get("error") else "")


def firecrawl_calls(path: Path) -> list[dict]:
    """Volání nástrojů Firecrawlu v záznamu relace, včetně zablokovaných hookem."""
    pending, calls = {}, []
    for event in events(path):
        message = event.get("message")
        if not isinstance(message, dict) or not isinstance(message.get("content"), list):
            continue
        for part in message["content"]:
            if part.get("type") == "tool_use" and part.get("name", "").startswith("mcp__firecrawl__"):
                pending[part["id"]] = {"tool": part["name"].rsplit("__", 1)[-1], **part.get("input", {})}
            elif part.get("type") == "tool_result" and part.get("tool_use_id") in pending:
                call = pending.pop(part["tool_use_id"])
                call["outcome"] = _outcome(_tool_result_text(part.get("content")), bool(part.get("is_error")))
                calls.append(call)
    return calls


def print_calls(calls: list[dict]) -> None:
    print("| # | nástroj | URL | formats | maxAge | onlyMainContent | výsledek |\n|---|---|---|---|---|---|---|")
    for number, call in enumerate(calls, 1):
        print(f"| {number} | {call['tool']} | {call.get('url', '')} | {json.dumps(call.get('formats'))} "
              f"| {json.dumps(call.get('maxAge'))} | {json.dumps(call.get('onlyMainContent'))} | {call['outcome']} |")
    print(f"\nVolání Firecrawlu: {len(calls)}")


# --- Příkazy ---

def run(agent: str, prompt: str, out_dir: Path, budget: float) -> int:
    out_dir.mkdir(parents=True, exist_ok=True)
    log_path, output_path = out_dir / f"{agent}.jsonl", out_dir / f"{agent}.md"
    command = ["claude", "-p", "--agent", agent, "--output-format", "stream-json", "--verbose",
               "--no-session-persistence", "--permission-mode", "dontAsk",
               "--allowedTools", AGENT_TOOLS, "--max-budget-usd", str(budget), prompt]
    with log_path.open("w", encoding="utf-8") as log, open(out_dir / f"{agent}.stderr", "w") as err:
        code = subprocess.run(command, stdin=subprocess.DEVNULL, stdout=log, stderr=err).returncode
    result = final_result(log_path)
    output_path.write_text(result.get("result") or "", encoding="utf-8")
    print(f"Agent: {agent}, návratový kód {code}, výsledek: {result.get('subtype')}")
    print(f"Cena: {result.get('total_cost_usd', 0):.2f} USD, čas: {result.get('duration_ms', 0) / 1000:.0f} s")
    print(f"Výstup: {output_path}\nZáznam: {log_path}\n")
    print_calls(firecrawl_calls(log_path))
    return 0 if code == 0 and result.get("subtype") == "success" else 1


def build_handoff(scout_output: str, investor: str) -> tuple[dict | None, list[str]]:
    """Předání pro auditora: tvrzení beze změny znaků. Vrací (předání, chyby)."""
    tables = check_quotes.markdown_tables(scout_output)
    errors, claims = [], []
    for row in (row for table in tables for row in table):
        claim = check_quotes.claim_from_row(row)
        if claim is None:
            continue
        issues = claim.problems()
        if issues:
            errors.append(f"{claim.claim_id or '?'}: {'; '.join(issues)}")
            continue
        claims.append({"claim": claim.claim_id, **{c: row.get(c, "") for c in CLAIM_COLUMNS},
                       "url": claim.url, "citace": claim.quote})
    if not claims and not errors:
        errors.append("ve výstupu není žádná tabulka tvrzení se sloupcem citace")
    sources = [{"url": row["url"], "publisher": row.get("publisher", "")}
               for table in tables for row in table
               if "publisher" in row and check_quotes.is_full_url(row.get("url", ""))]
    if errors:
        return None, errors
    return {"investor": investor, "created": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "claims": claims, "sources_used_by_scout": sources}, []


def handoff(scout_md: Path, investor: str, out: Path) -> int:
    data, errors = build_handoff(scout_md.read_text(encoding="utf-8"), investor)
    if errors:
        print("Předání odmítnuto, neúplné záznamy:", file=sys.stderr)
        for error in errors:
            print("  " + error, file=sys.stderr)
        return 1
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Předání: {out} ({len(data['claims'])} tvrzení, {len(data['sources_used_by_scout'])} zdrojů)")
    print("Zadání pro auditora může odkázat na soubor, např.:")
    print(f"  Investor: {investor}. Tvrzení k prověření jsou v souboru {out}. Načti ho nástrojem Read.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Spouštění agentů a předávání souborem.")
    commands = parser.add_subparsers(dest="command", required=True)
    run_parser = commands.add_parser("run", help="spustit agenta")
    run_parser.add_argument("agent", choices=["investor-source-scout", "investor-evidence-auditor"])
    run_parser.add_argument("--prompt-file", type=Path, required=True)
    run_parser.add_argument("--out", type=Path, required=True)
    run_parser.add_argument("--max-budget-usd", type=float, default=10.0)
    handoff_parser = commands.add_parser("handoff", help="sestavit předání pro auditora")
    handoff_parser.add_argument("scout_output", type=Path)
    handoff_parser.add_argument("--investor", required=True)
    handoff_parser.add_argument("--out", type=Path, required=True)
    calls_parser = commands.add_parser("calls", help="vypsat volání Firecrawlu ze záznamu relace")
    calls_parser.add_argument("log", type=Path)
    args = parser.parse_args(argv)
    if args.command == "run":
        prompt = args.prompt_file.read_text(encoding="utf-8")
        return run(args.agent, prompt, args.out, args.max_budget_usd)
    if args.command == "handoff":
        return handoff(args.scout_output, args.investor, args.out)
    print_calls(firecrawl_calls(args.log))
    return 0


if __name__ == "__main__":
    sys.exit(main())
