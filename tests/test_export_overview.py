"""Testy přehledu investorů pro čtení (scripts/export_overview.py) na fiktivních ukázkových datech.

Spuštění z kořene repozitáře:
    python3 -m unittest discover -s tests -v
"""

import contextlib
import csv
import io
import shutil
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import export_overview  # noqa: E402

VALID_DIR = ROOT / "data" / "examples" / "valid"
INVALID_DIR = ROOT / "data" / "examples" / "invalid"
TODAY = date(2026, 10, 14)


def rows_by_id(data_dir=VALID_DIR):
    rows, errors = export_overview.build_rows(data_dir, TODAY)
    assert not errors, errors
    return {row["ID v databázi"]: row for row in rows}


class ExportOverviewTest(unittest.TestCase):
    def test_only_included_investors_without_e10_records(self):
        self.assertEqual(sorted(rows_by_id()), ["INV-0001", "INV-0002"])

    def test_readable_values_and_explicit_missing_values(self):
        rows = rows_by_id()
        vc, angel = rows["INV-0001"], rows["INV-0002"]
        self.assertEqual((vc["Typ"], vc["Město"], vc["Země"]), ("venture capital (VC)", "Praha", "Česko"))
        self.assertEqual(vc["Typická investice (ticket)"], "250 000–2 000 000 EUR (deklarované rozpětí)")
        self.assertEqual(vc["Fáze"], "pre-seed, seed")
        self.assertEqual(vc["Investiční geografie"], "Česko, střední a východní Evropa")
        self.assertTrue(vc["AUM (celkový spravovaný kapitál)"].startswith("nejasné"))
        self.assertEqual(angel["Typ"], "business angel")
        self.assertEqual(angel["Město"], "neuvedeno")
        self.assertEqual(angel["Typická investice (ticket)"], "nezveřejněno")
        self.assertEqual(angel["AUM (celkový spravovaný kapitál)"], "nevztahuje se")
        self.assertEqual(angel["Sektory"], "edtech (odvozeno)")

    def test_fund_sizes_are_listed_per_fund_not_as_aum(self):
        vc = rows_by_id()["INV-0001"]
        self.assertIn("Fiktivní Ventures Fund I – 40 000 000 EUR (konečná velikost, k 2021-06)",
                      vc["Fondy a jejich velikost"])
        self.assertIn("80 000 000 EUR (cílová velikost", vc["Fondy a jejich velikost"])
        self.assertNotIn("EUR", vc["AUM (celkový spravovaný kapitál)"])

    def test_last_documented_investment_ignores_unclear_and_registry_only_deals(self):
        vc = rows_by_id()["INV-0001"]
        self.assertEqual(vc["Poslední doložená investice"], "Ukázková Robotika s.r.o. (2025-03-12)")
        self.assertEqual(vc["Počet doložených investic"], "2")
        with tempfile.TemporaryDirectory() as tmp:
            data_dir = Path(tmp) / "data"
            shutil.copytree(VALID_DIR, data_dir)
            path = data_dir / "investments.csv"
            with path.open(encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))
            for row in rows:
                if row["deal_id"] == "DEAL-0006":  # instrument unclear, novější oznámení
                    row["investment_date"] = "2026-01-10"
            with path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
                writer.writeheader()
                writer.writerows(rows)
            later = rows_by_id(data_dir)["INV-0001"]
        self.assertEqual(later["Poslední doložená investice"], "Ukázková Robotika s.r.o. (2025-03-12)")

    def test_documented_investments_list_only_deals_meeting_k3(self):
        vc = rows_by_id()["INV-0001"]
        self.assertEqual(vc["Doložené investice (firmy)"],
                         "Ukázková Robotika s.r.o. (2025-03-12, seed); Demo Health a.s. (2023, pre-seed)")
        self.assertNotIn("Logistika", vc["Doložené investice (firmy)"])   # instrument unclear
        self.assertNotIn("Energetika", vc["Doložené investice (firmy)"])  # jen zápis v rejstříku

    def test_ticket_is_labelled_as_declared_and_scoped(self):
        with tempfile.TemporaryDirectory() as tmp:
            data_dir = Path(tmp) / "data"
            shutil.copytree(VALID_DIR, data_dir)
            path = data_dir / "investors.csv"
            with path.open(encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))
            for row in rows:
                if row["investor_id"] == "INV-0001":
                    row["ticket_scope"] = "growth equity"
            with path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
                writer.writeheader()
                writer.writerows(rows)
            vc = rows_by_id(data_dir)["INV-0001"]
        self.assertEqual(vc["Typická investice (ticket)"],
                         "250 000–2 000 000 EUR (deklarované rozpětí pro growth equity)")

    def test_values_are_traceable_to_sources_and_citations(self):
        vc = rows_by_id()["INV-0001"]
        self.assertIn("https://or.example/subjekt/99999994 (CIT-0001)", vc["Zdroje: identita, sídlo a typ"])
        self.assertIn("(CIT-", vc["Zdroje: rozhodovací pravomoc (K2)"])
        self.assertIn("https://ukazkova-robotika.example/novinky/seed-kolo", vc["Zdroje: doložené investice"])
        self.assertTrue(vc["Hodnocení spolehlivosti"].startswith("A"))

    def test_no_overview_from_invalid_data(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "prehled.csv"
            with contextlib.redirect_stderr(io.StringIO()):
                code = export_overview.main([str(INVALID_DIR), "--today", TODAY.isoformat(), "--out", str(out)])
            self.assertEqual(code, 1)
            self.assertFalse(out.exists())


if __name__ == "__main__":
    unittest.main()
