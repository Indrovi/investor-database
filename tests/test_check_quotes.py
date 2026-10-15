"""Testy skriptu scripts/check_quotes.py (bez síťových volání).

Spuštění z kořene repozitáře:
    python3 -m unittest discover -s tests -v
"""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_quotes as cq  # noqa: E402

# Patička webu: adresa je ve třech prvcích, na stránce mezi nimi žádné čárky nejsou.
FOOTER_HTML = """<html><head><style>.x{}</style><script>var a = "Karlovo";</script></head>
<body><p>Investice vedl <a href="#">Credo Ventures</a>, a Czech early-stage investor.</p>
<div>Karlovo Náměstí 10</div><div>120 00, Prague</div><div>Czech Republic</div>
<p>„Rozhodli jsme se navýšit“ – řekl partner.</p></body></html>"""

AGENT_OUTPUT = """## Zdroje
| url | publisher |
|---|---|
| https://a.example/clanek | A |

## Tvrzení
| claim | entita | pole | hodnota | url | doslovná citace | text z |
|---|---|---|---|---|---|---|
| C01 | investice | deal | ano | https://a.example/clanek | "Kolo vedl fond X." | firecrawl |

## Nové důkazy z vlastního hledání
| claim (A1, A2…) | entita | pole | hodnota | url | doslovná citace |
|---|---|---|---|---|---|
| A1 | investice | deal | ano | https://b.example/zprava | `Fond X investoval do firmy Y.` |
"""

# Neúplné záznamy, které kontrola musí odmítnout (ne přeskočit).
INCOMPLETE_OUTPUT = """## Tvrzení
| claim | entita | pole | hodnota | src | url | doslovná citace |
|---|---|---|---|---|---|---|
| C01 | investice | deal | ano | S01 |  | Kolo vedl fond X. |
| C02 | investice | deal | ano |  | stejná jako C01 | Fond X vedl kolo. |
| C03 | investor | aum | – |  | https://a.example/clanek | – |
|  | investice | deal | ano |  | https://a.example/clanek | Fond X vedl kolo. |
| C05 | investice | deal | ano |  | a.example/clanek | Fond X vedl kolo. |
"""


def silent(_message):
    pass


class TextTest(unittest.TestCase):
    def test_html_text_skips_scripts_and_fixes_spacing_before_punctuation(self):
        text = cq.html_to_text(FOOTER_HTML)
        self.assertNotIn("var a", text)
        self.assertIn("Credo Ventures, a Czech early-stage investor.", text)
        self.assertIn('"Rozhodli jsme se navýšit" - řekl partner.', text)

    def test_quote_with_added_commas_is_not_verbatim(self):
        text = cq.html_to_text(FOOTER_HTML)
        found, ratio, window = cq.find_quote(text, "Karlovo Náměstí 10, 120 00, Prague, Czech Republic")
        self.assertFalse(found)
        self.assertGreater(ratio, 0.9)
        self.assertTrue(window.startswith("Karlovo Náměstí 10 120 00"))
        self.assertTrue(cq.find_quote(text, "Karlovo Náměstí 10 120 00, Prague Czech Republic")[0])

    def test_number_spacing_is_a_difference(self):
        text = cq.normalize("Identifikační číslo: 285 38 137")
        self.assertFalse(cq.find_quote(text, "Identifikační číslo: 28538137")[0])

    def test_markdown_from_firecrawl_is_converted_to_text(self):
        text = cq.markdown_to_text("## Titulek\n\n- **Kdo investuje:** kolo vede [Tilia](https://t.example).\n")
        self.assertIn("Titulek Kdo investuje: kolo vede Tilia.", text)


class InputTest(unittest.TestCase):
    def test_claims_from_agent_markdown(self):
        claims = cq.claims_from_markdown(AGENT_OUTPUT)
        self.assertEqual(claims, [
            cq.Claim("C01", "https://a.example/clanek", "Kolo vedl fond X."),
            cq.Claim("A1", "https://b.example/zprava", "Fond X investoval do firmy Y."),
        ])
        self.assertTrue(all(not claim.problems() for claim in claims))

    def test_incomplete_rows_are_kept_with_reasons(self):
        claims = cq.claims_from_markdown(INCOMPLETE_OUTPUT)
        self.assertEqual(len(claims), 5)  # žádný řádek se nepřeskočí
        reasons = {claim.claim_id or "?": claim.problems() for claim in claims}
        self.assertIn("chybí úplná URL", reasons["C01"][0])   # jen odkaz na zdroj (src), bez URL
        self.assertIn("chybí úplná URL", reasons["C02"][0])   # „stejná jako C01“
        self.assertEqual(reasons["C03"], ["chybí citace"])
        self.assertEqual(reasons["?"], ["chybí ID"])
        self.assertIn("chybí úplná URL", reasons["C05"][0])   # adresa bez https://

    def test_claims_from_example_data(self):
        claims = cq.claims_from_data(ROOT / "data" / "examples" / "valid")
        self.assertEqual(len(claims), 18)
        self.assertTrue(all(not claim.problems() for claim in claims))


class CheckTest(unittest.TestCase):
    def test_result_and_exit_code(self):
        pages = {
            "https://a.example/clanek": cq.Page(200, cq.normalize("Text. Kolo vedl fond X. Konec."), "přímo"),
            "https://b.example/zprava": cq.Page(200, cq.normalize("Fond X investoval do firmy Z."), "přímo"),
        }
        claims = cq.claims_from_markdown(AGENT_OUTPUT)
        lines = []
        self.assertEqual(cq.check_claims(claims, pages.__getitem__, lines.append), 1)
        self.assertTrue(lines[0].startswith("C01    DOSLOVNĚ"))
        self.assertTrue(lines[1].startswith("A1     NEDOSLOVNĚ"))
        self.assertEqual(cq.check_claims(claims[:1], pages.__getitem__, silent), 0)

    def test_incomplete_rows_are_rejected_without_fetching(self):
        fetched = []
        lines = []
        code = cq.check_claims(cq.claims_from_markdown(INCOMPLETE_OUTPUT), fetched.append, lines.append)
        self.assertEqual(code, 1)
        self.assertEqual(fetched, [])
        self.assertEqual(sum("NEÚPLNÝ" in line for line in lines), 5)
        self.assertIn("problém: 5", lines[-1])

    def test_blocked_page_is_not_checked(self):
        challenge = cq.Page(403, "Just a moment...", "přímo", "HTTP 403")
        lines = []
        code = cq.check_claims([cq.Claim("A5", "https://c.example", "cokoli")], lambda url: challenge,
                               lines.append)
        self.assertEqual(code, 1)
        self.assertIn("NESTAŽENO", lines[0])
        self.assertTrue(cq.looks_blocked(200, "<title>Vercel Security Checkpoint</title>"))
        self.assertFalse(cq.looks_blocked(200, "Běžný článek"))


if __name__ == "__main__":
    unittest.main()
