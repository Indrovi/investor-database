"""Testy nástrojů pro agenty (bez síťových volání a bez spouštění agentů):

- .claude/hooks/firecrawl_guard.py: kontrola skutečných parametrů Firecrawlu,
- scripts/firecrawl_mcp.py: klíč z .env a hlavičky pro headersHelper,
- scripts/agents.py: předání souborem a výpis volání Firecrawlu.

Spuštění z kořene repozitáře:
    python3 -m unittest discover -s tests -v
"""

import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import agents  # noqa: E402
import firecrawl_mcp  # noqa: E402

GUARD = ROOT / ".claude" / "hooks" / "firecrawl_guard.py"
SCRAPE = "mcp__firecrawl__firecrawl_scrape"
GOOD_INPUT = {"url": "https://cc.cz/clanek/", "formats": ["markdown"], "maxAge": 0, "onlyMainContent": False}


def run_guard(payload) -> dict | None:
    """Spustí hook jako Claude Code: JSON na stdin, rozhodnutí na stdout."""
    raw = payload if isinstance(payload, str) else json.dumps(payload)
    completed = subprocess.run([sys.executable, str(GUARD)], input=raw, capture_output=True,
                               text=True, check=True)
    return json.loads(completed.stdout) if completed.stdout.strip() else None


def denial(result) -> str:
    output = result["hookSpecificOutput"]
    assert output["permissionDecision"] == "deny"
    return output["permissionDecisionReason"]


class FirecrawlGuardTest(unittest.TestCase):
    def test_approved_scrape_passes(self):
        self.assertIsNone(run_guard({"tool_name": SCRAPE, "tool_input": GOOD_INPUT}))
        with_pdf = {**GOOD_INPUT, "parsers": ["pdf"], "waitFor": 1000}
        self.assertIsNone(run_guard({"tool_name": SCRAPE, "tool_input": with_pdf}))

    def test_wrong_parameters_are_denied(self):
        cases = {
            "maxAge je 172800000": {**GOOD_INPUT, "maxAge": 172800000},
            "maxAge je false": {**GOOD_INPUT, "maxAge": False},
            "maxAge je null": {k: v for k, v in GOOD_INPUT.items() if k != "maxAge"},
            "onlyMainContent je true": {**GOOD_INPUT, "onlyMainContent": True},
            "onlyMainContent je null": {k: v for k, v in GOOD_INPUT.items() if k != "onlyMainContent"},
            'formats je ["markdown", "summary"]': {**GOOD_INPUT, "formats": ["markdown", "summary"]},
            "url není úplná": {**GOOD_INPUT, "url": "cc.cz/clanek"},
            "nepovolené parametry: actions": {**GOOD_INPUT, "actions": [{"type": "click"}]},
        }
        for expected, tool_input in cases.items():
            with self.subTest(expected):
                self.assertIn(expected, denial(run_guard({"tool_name": SCRAPE, "tool_input": tool_input})))

    def test_other_firecrawl_tools_are_denied(self):
        for tool in ("firecrawl_search", "firecrawl_map", "firecrawl_monitor_create"):
            with self.subTest(tool):
                reason = denial(run_guard({"tool_name": f"mcp__firecrawl__{tool}",
                                           "tool_input": {"query": "x"}}))
                self.assertIn(f"nástroj {tool} není povolený", reason)

    def test_unreadable_input_is_denied(self):
        self.assertIn("vstup hooku nejde přečíst", denial(run_guard("není to JSON")))


class FirecrawlKeyTest(unittest.TestCase):
    def env_file(self, content: str) -> Path:
        handle = tempfile.NamedTemporaryFile("w", suffix=".env", delete=False, encoding="utf-8")
        handle.write(content)
        handle.close()
        self.addCleanup(Path(handle.name).unlink)
        return Path(handle.name)

    def test_key_is_read_from_env_file(self):
        path = self.env_file("# komentář\nOTHER=1\nFIRECRAWL_API_KEY=fc-test123\n")
        self.assertEqual(firecrawl_mcp.read_key(path), "fc-test123")
        self.assertEqual(firecrawl_mcp.auth_headers(path), {"Authorization": "Bearer fc-test123"})
        self.assertEqual(firecrawl_mcp.read_key(self.env_file('FIRECRAWL_API_KEY="fc-q"\n')), "fc-q")

    def test_missing_key_means_no_auth_header(self):
        self.assertEqual(firecrawl_mcp.auth_headers(self.env_file("FIRECRAWL_API_KEY=\n")), {})
        self.assertEqual(firecrawl_mcp.auth_headers(Path("/neexistuje/.env")), {})

    def test_env_file_is_ignored_by_git_and_example_is_not(self):
        ignored = subprocess.run(["git", "check-ignore", ".env"], cwd=ROOT, capture_output=True)
        example = subprocess.run(["git", "check-ignore", ".env.example"], cwd=ROOT, capture_output=True)
        self.assertEqual((ignored.returncode, example.returncode), (0, 1))


SCOUT_OUTPUT = """## Zdroje
| url | publisher | title |
|---|---|---|
| https://a.example/clanek | Médium A | Titulek |

## Tvrzení
| claim | entita | pole | hodnota | url | doslovná citace | text z | doslovnost | poznámka |
|---|---|---|---|---|---|---|---|---|
| C1 | investice X → Y | deal | ano | https://a.example/clanek | Since 2016, we’ve invested „€40M“ – firm’s data | firecrawl | verbatim | tier 3 |
| C2 | investice X → Y | round_amount | 3000000 EUR | https://a.example/clanek | raised a €3 million pre-seed round | firecrawl | verbatim | – |
"""


class HandoffTest(unittest.TestCase):
    def test_handoff_keeps_quotes_exactly(self):
        data, errors = agents.build_handoff(SCOUT_OUTPUT, "Investor X")
        self.assertEqual(errors, [])
        self.assertEqual([claim["claim"] for claim in data["claims"]], ["C1", "C2"])
        # Typografické znaky (’ „ “ – €) zůstanou beze změny.
        self.assertEqual(data["claims"][0]["citace"], "Since 2016, we’ve invested „€40M“ – firm’s data")
        self.assertEqual(data["claims"][0]["url"], "https://a.example/clanek")
        self.assertNotIn("poznámka", data["claims"][0])  # poznámky průzkumníka se nepředávají
        self.assertEqual(data["sources_used_by_scout"], [{"url": "https://a.example/clanek",
                                                          "publisher": "Médium A"}])
        with tempfile.TemporaryDirectory() as tmp:
            scout_md, out = Path(tmp) / "scout.md", Path(tmp) / "handoff.json"
            scout_md.write_text(SCOUT_OUTPUT, encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(agents.handoff(scout_md, "Investor X", out), 0)
            saved = json.loads(out.read_text(encoding="utf-8"))
            self.assertEqual(saved["claims"][0]["citace"], data["claims"][0]["citace"])

    def test_handoff_rejects_incomplete_rows(self):
        broken = SCOUT_OUTPUT.replace("| C2 | investice X → Y | round_amount | 3000000 EUR | https://a.example/clanek",
                                      "| C2 | investice X → Y | round_amount | 3000000 EUR | stejná jako C1")
        data, errors = agents.build_handoff(broken, "Investor X")
        self.assertIsNone(data)
        self.assertEqual(len(errors), 1)
        self.assertTrue(errors[0].startswith("C2: chybí úplná URL"))

    def test_handoff_rejects_output_without_claims(self):
        data, errors = agents.build_handoff("## Nenalezeno\n- nic\n", "Investor X")
        self.assertIsNone(data)
        self.assertIn("žádná tabulka tvrzení", errors[0])


class FirecrawlCallsTest(unittest.TestCase):
    def test_calls_with_status_and_hook_denial(self):
        def tool_use(call_id, name, tool_input):
            return {"type": "assistant", "message": {"content": [
                {"type": "tool_use", "id": call_id, "name": name, "input": tool_input}]}}

        def tool_result(call_id, text, is_error=False):
            return {"type": "user", "message": {"content": [
                {"type": "tool_result", "tool_use_id": call_id, "is_error": is_error,
                 "content": [{"type": "text", "text": text}]}]}}

        ok = json.dumps({"metadata": {"statusCode": 200}})
        missing = json.dumps({"metadata": {"statusCode": 404, "error": "Not Found"}})
        lines = [
            tool_use("1", SCRAPE, GOOD_INPUT), tool_result("1", ok),
            tool_use("2", SCRAPE, {**GOOD_INPUT, "url": "https://x.example/404"}), tool_result("2", missing),
            tool_use("3", SCRAPE, {**GOOD_INPUT, "onlyMainContent": True}),
            tool_result("3", "Volání Firecrawlu zablokovala kontrola parametrů: onlyMainContent je true, "
                             "musí být false. Povoleno: …", True),
            tool_use("4", "WebFetch", {"url": "https://y.example"}), tool_result("4", "text"),
        ]
        with tempfile.TemporaryDirectory() as tmp:
            log = Path(tmp) / "run.jsonl"
            log.write_text("\n".join(json.dumps(line) for line in lines) + "\n", encoding="utf-8")
            calls = agents.firecrawl_calls(log)
        self.assertEqual([call["outcome"] for call in calls], [
            "statusCode 200",
            "statusCode 404 (Not Found)",
            "zablokováno hookem: onlyMainContent je true, musí být false",
        ])
        self.assertEqual(calls[0]["tool"], "firecrawl_scrape")
        self.assertIs(calls[2]["onlyMainContent"], True)


if __name__ == "__main__":
    unittest.main()
