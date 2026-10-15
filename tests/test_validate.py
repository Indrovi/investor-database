"""Testy validátoru scripts/validate.py na fiktivních ukázkových datech.

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

import validate  # noqa: E402

VALID_DIR = ROOT / "data" / "examples" / "valid"
INVALID_DIR = ROOT / "data" / "examples" / "invalid"
TODAY = date(2026, 10, 14)

# Každá chyba vložená do data/examples/invalid (popis je ve sloupci notes daného záznamu).
EXPECTED_INVALID_ISSUES = {
    ("ERROR", "DUPLICATE_ID", "SRC-0011", "source_id"),
    ("ERROR", "INVALID_DATE", "SRC-0003", "published_date"),
    ("ERROR", "MISSING_VALUE", "SRC-0010", "accessed_date"),
    ("ERROR", "INVALID_URL", "SRC-0020", "url"),
    ("ERROR", "MISSING_SOURCE", "CIT-0010", "source_id"),
    ("ERROR", "UNKNOWN_REFERENCE", "CIT-0027", "source_id"),
    ("ERROR", "MISSING_QUOTE", "CIT-0028", "quote"),
    ("ERROR", "AGGREGATOR_AS_EVIDENCE", "CIT-0029", "source_id"),
    ("ERROR", "FUND_SIZE_TYPE_REQUIRED", "FND-0002", "size_type"),
    ("ERROR", "MISSING_CITATION", "FND-0002", "size"),
    ("ERROR", "MISSING_CURRENCY", "DEAL-0001", "round_currency"),
    ("ERROR", "FUND_INVESTOR_MISMATCH", "DEAL-0003", "fund_id"),
    ("ERROR", "DATE_BASIS_REQUIRED", "DEAL-0004", "date_basis"),
    ("ERROR", "UNKNOWN_REFERENCE", "DEAL-0007", "investor_id"),
    ("ERROR", "INVALID_ENUM", "DEAL-0008", "instrument"),
    ("ERROR", "INVALID_AMOUNT", "DEAL-0008", "round_amount"),
    ("ERROR", "FUTURE_DATE", "DEAL-0009", "investment_date"),
    ("ERROR", "REGISTRY_DATE_AS_INVESTMENT_DATE", "DEAL-0010", "investment_date"),
    ("ERROR", "REGISTRY_CONTRIBUTION_AS_AMOUNT", "DEAL-0010", "investor_amount"),
    ("ERROR", "MISSING_CURRENCY", "INV-0001", "ticket_currency"),
    ("ERROR", "TICKET_RANGE_INVALID", "INV-0001", "ticket_min"),
    ("ERROR", "AUM_DERIVED_NOT_ALLOWED", "INV-0001", "aum_status"),
    ("ERROR", "MISSING_CITATION", "INV-0001", "geographies"),
    ("ERROR", "SUBTYPE_TYPE_MISMATCH", "INV-0002", "subtype"),
    ("ERROR", "AUM_FOR_NATURAL_PERSON", "INV-0002", "aum_amount"),
    ("ERROR", "MISSING_CITATION", "INV-0002", "sectors"),
    ("ERROR", "MISSING_CITATION", "INV-0002", "geographies"),
    ("ERROR", "K3_NOT_MET", "INV-0002", ""),
    ("ERROR", "REJECTION_CODE_REQUIRED", "INV-0004", "rejection_code"),
    ("ERROR", "UNKNOWN_REFERENCE", "INV-0005", "merged_into"),
    ("ERROR", "INVALID_REGISTRY_ID", "INV-0006", "registry_id"),
    ("ERROR", "AUM_BASIS_REQUIRED", "INV-0006", "aum_basis"),
    ("ERROR", "MISSING_AS_OF", "INV-0006", "aum_as_of"),
    ("ERROR", "STATUS_VALUE_MISMATCH", "INV-0006", "sectors_status"),
    ("ERROR", "K2_NOT_MET", "INV-0006", ""),
    ("ERROR", "K3_NOT_MET", "INV-0006", ""),
    ("ERROR", "INVALID_ENUM", "INV-0007", "primary_type"),
    ("ERROR", "E9_REVIEW_MISSING", "INV-0008", "rejection_code"),
    ("WARNING", "POSSIBLE_PLACEHOLDER_DATE", "DEAL-0002", "investment_date"),
    ("WARNING", "AUM_MATCHES_FUND_TOTAL", "INV-0001", "aum_amount"),
    ("WARNING", "INVESTMENT_NOT_EXPLICIT", "DEAL-0006", "instrument"),
}


def issue_keys(report):
    return {(i.severity, i.code, i.entity_id, i.field) for i in report.issues}


def summaries(report):
    return {s.investor_id: s for s in report.investors}


def validate_modified(changes=(), added_rows=(), transform=None):
    """Zkopíruje platnou sadu, upraví ji a zvaliduje.

    changes: [(tabulka, id, sloupec, nová hodnota)]
    added_rows: [(tabulka, {sloupec: hodnota})]
    transform: funkce, která dostane cestu k adresáři s daty (úpravy mimo obsah buněk)
    """
    with tempfile.TemporaryDirectory() as tmp:
        data_dir = Path(tmp) / "data"
        shutil.copytree(VALID_DIR, data_dir)
        tables = {}
        for table, spec in validate.TABLES.items():
            with (data_dir / spec.file_name).open(encoding="utf-8", newline="") as handle:
                tables[table] = list(csv.DictReader(handle))
        for table, row_id, column, value in changes:
            spec = validate.TABLES[table]
            matched = [row for row in tables[table] if row[spec.id_column] == row_id]
            assert matched, f"{row_id} v {spec.file_name} neexistuje"
            for row in matched:
                row[column] = value
        for table, values in added_rows:
            tables[table].append({column: values.get(column, "")
                                  for column in validate.TABLES[table].columns})
        for table, spec in validate.TABLES.items():
            with (data_dir / spec.file_name).open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=spec.columns, lineterminator="\n")
                writer.writeheader()
                writer.writerows(tables[table])
        if transform:
            transform(data_dir)
        return validate.validate(data_dir, TODAY)


class ExampleDataTest(unittest.TestCase):
    def test_valid_examples_have_no_issues(self):
        report = validate.validate(VALID_DIR, TODAY)
        self.assertEqual([i.format() for i in report.issues], [])

    def test_invalid_examples_report_exactly_the_planted_issues(self):
        report = validate.validate(INVALID_DIR, TODAY)
        self.assertEqual(issue_keys(report), EXPECTED_INVALID_ISSUES)
        self.assertEqual(len(report.issues), len(EXPECTED_INVALID_ISSUES))

    def test_derived_values_of_valid_examples(self):
        result = summaries(validate.validate(VALID_DIR, TODAY))
        investor = result["INV-0001"]
        self.assertEqual((investor.activity_status, investor.confidence_grade,
                          investor.last_investment_date, investor.documented_deals),
                         ("active", "A", "2025-03-12", 2))
        self.assertEqual((result["INV-0003"].confidence_grade, result["INV-0003"].documented_deals),
                         ("C", 0))

    def test_cli_exit_codes(self):
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(validate.main([str(VALID_DIR), "--today", TODAY.isoformat()]), 0)
            self.assertEqual(validate.main([str(INVALID_DIR), "--today", TODAY.isoformat()]), 1)


class HighlightedCasesTest(unittest.TestCase):
    """Případy z požadavků: chybějící měna, neznámé datum, nejasný kapitál, zdroje odvozených
    hodnot, nejasný nástroj, údaje z obchodního rejstříku, AUM vs. upsaný kapitál fondů."""

    def test_missing_currency_is_an_error(self):
        report = validate.validate(INVALID_DIR, TODAY)
        missing = {(i.entity_id, i.field) for i in report.errors if i.code == "MISSING_CURRENCY"}
        self.assertEqual(missing, {("INV-0001", "ticket_currency"), ("DEAL-0001", "round_currency")})

    def test_unknown_date_keeps_investor_included_but_inactive(self):
        investor = summaries(validate.validate(VALID_DIR, TODAY))["INV-0002"]
        self.assertEqual((investor.record_status, investor.confidence_grade), ("included", "B"))
        self.assertEqual((investor.last_investment_date, investor.activity_status), ("", "inactive"))

    def test_unclear_capital_is_stored_as_ambiguous_not_as_aum(self):
        valid = validate.validate(VALID_DIR, TODAY)
        self.assertFalse(valid.errors)  # INV-0001: AUM prázdné, aum_status=ambiguous, citace CIT-0003
        invalid = validate.validate(INVALID_DIR, TODAY)
        self.assertIn(("ERROR", "AUM_BASIS_REQUIRED", "INV-0006", "aum_basis"), issue_keys(invalid))

    def test_derived_value_needs_original_source_not_only_method(self):
        report = validate_modified([("citations", "CIT-0010", "source_id", "")])
        keys = issue_keys(report)
        self.assertIn(("ERROR", "MISSING_SOURCE", "CIT-0010", "source_id"), keys)
        self.assertIn(("ERROR", "MISSING_CITATION", "INV-0002", "sectors"), keys)

    def test_derived_value_needs_method_description(self):
        report = validate_modified([("citations", "CIT-0010", "note", "")])
        self.assertEqual(issue_keys(report), {
            ("ERROR", "MISSING_METHOD", "INV-0002", "sectors"),
            ("ERROR", "MISSING_METHOD", "INV-0002", "geographies"),
        })

    def test_unclear_instrument_is_not_evidence_of_investing(self):
        # V platných datech je DEAL-0006 (unclear) evidovaná, ale nepočítá se mezi doložené.
        # INV-0001 má doložené jen DEAL-0001 a DEAL-0002 (DEAL-0005 je jen zápis v rejstříku).
        self.assertEqual(summaries(validate.validate(VALID_DIR, TODAY))["INV-0001"].documented_deals, 2)
        report = validate_modified([("investments", "DEAL-0003", "instrument", "unclear")])
        self.assertEqual(issue_keys(report), {("ERROR", "K3_NOT_MET", "INV-0002", "")})

    def test_registry_entry_and_czk_contribution_are_not_investment_date_and_amount(self):
        # Platná data: DEAL-0005 má jen datum zápisu a vklad 20 000 Kč. Poslední investicí
        # zůstává DEAL-0001, i když je zápis novější.
        investor = summaries(validate.validate(VALID_DIR, TODAY))["INV-0001"]
        self.assertEqual(investor.last_investment_date, "2025-03-12")
        report = validate.validate(INVALID_DIR, TODAY)
        self.assertIn(("ERROR", "REGISTRY_DATE_AS_INVESTMENT_DATE", "DEAL-0010", "investment_date"),
                      issue_keys(report))
        self.assertIn(("ERROR", "REGISTRY_CONTRIBUTION_AS_AMOUNT", "DEAL-0010", "investor_amount"),
                      issue_keys(report))

    def test_registry_only_deal_does_not_make_investor_active(self):
        report = validate_modified([("investments", "DEAL-0001", "investment_date", "2024")])
        self.assertEqual(summaries(report)["INV-0001"].activity_status, "inactive")

    def test_same_date_is_allowed_when_another_source_states_it(self):
        report = validate_modified(
            [("investments", "DEAL-0005", "investment_date", "2025-11-20"),
             ("investments", "DEAL-0005", "date_basis", "stated_in_source")],
            [("citations", {"citation_id": "CIT-0099", "entity_type": "investment",
                            "entity_id": "DEAL-0005", "fields": "investment_date",
                            "source_id": "SRC-0004",
                            "quote": "Do Ukázkové Energetiky vstoupil fond 20. listopadu 2025."})])
        self.assertEqual(report.issues, [])

    def test_aum_is_not_total_commitments_of_funds(self):
        report = validate_modified([("investors", "INV-0001", "aum_basis", "total_commitments")])
        self.assertIn(("ERROR", "INVALID_ENUM", "INV-0001", "aum_basis"), issue_keys(report))
        aum_reported = [("investors", "INV-0001", "aum_currency", "EUR"),
                        ("investors", "INV-0001", "aum_basis", "aum"),
                        ("investors", "INV-0001", "aum_as_of", "2025-09-22"),
                        ("investors", "INV-0001", "aum_status", "reported")]
        total = validate_modified(aum_reported + [("investors", "INV-0001", "aum_amount", "120000000")])
        self.assertEqual(issue_keys(total), {("WARNING", "AUM_MATCHES_FUND_TOTAL", "INV-0001", "aum_amount")})
        single = validate_modified(aum_reported + [("investors", "INV-0001", "aum_amount", "40000000")])
        self.assertEqual(issue_keys(single), {("WARNING", "AUM_MATCHES_FUND_SIZE", "INV-0001", "aum_amount")})


class FinalReviewTest(unittest.TestCase):
    """Poslední revize kroku 2: K2, samotný zápis v rejstříku, investment_unspecified,
    orientační hranice 500 tis. EUR a E9 až po prověření."""

    def test_included_investor_needs_k2_assessment(self):
        valid = summaries(validate.validate(VALID_DIR, TODAY))
        self.assertTrue(valid["INV-0001"].k2_verified)
        self.assertFalse(valid["INV-0003"].k2_verified)  # kandidát bez posouzení K2 je v pořádku
        report = validate_modified([("citations", "CIT-0009", "fields", "primary_type")])
        self.assertEqual(issue_keys(report), {("ERROR", "K2_NOT_MET", "INV-0002", "")})
        self.assertEqual(summaries(report)["INV-0002"].confidence_grade, "C")

    def test_registry_entry_alone_does_not_meet_k3(self):
        # Jediná investice INV-0002 je doložená jen výpisem zápisu společníka.
        report = validate_modified(
            [("investments", "DEAL-0003", "registry_entry_date", "2022-05-10"),
             ("citations", "CIT-0011", "source_id", "SRC-0099"),
             ("citations", "CIT-0011", "fields", "deal;registry_entry_date"),
             ("citations", "CIT-0011", "quote", "Společník: Jana Příkladová, zapsáno 10. května 2022")],
            [("sources", {"source_id": "SRC-0099", "url": "https://or.example/subjekt/vzorova-akademie",
                          "publisher": "Obchodní rejstřík (fiktivní ukázka)", "tier": "1",
                          "published_date": "2022-05-10", "accessed_date": "2026-10-14",
                          "archive_url": "https://archive.example/or.example/subjekt/vzorova-akademie"})])
        self.assertEqual(issue_keys(report), {("ERROR", "K3_NOT_MET", "INV-0002", "")})
        self.assertEqual(summaries(report)["INV-0002"].documented_deals, 0)

    def test_registry_entry_with_related_document_meets_k3(self):
        # DEAL-0005 (zápis + vklad 20 000 Kč) doplněný o listinu ze sbírky listin se počítá,
        # ale aktivitu dál určuje jen datum investice, ne datum zápisu.
        report = validate_modified(
            added_rows=[
                ("sources", {"source_id": "SRC-0099", "url": "https://or.example/listina/12345",
                             "publisher": "Sbírka listin (fiktivní ukázka)", "tier": "1",
                             "published_date": "2025-10-30", "accessed_date": "2026-10-14",
                             "archive_url": "https://archive.example/or.example/listina/12345"}),
                ("citations", {"citation_id": "CIT-0099", "entity_type": "investment",
                               "entity_id": "DEAL-0005", "fields": "deal", "source_id": "SRC-0099",
                               "quote": "Fiktivní Ventures s.r.o. převezme vklad 20 000 Kč za emisní "
                                        "kurs 8 000 000 Kč a stane se společníkem."})])
        self.assertEqual(report.issues, [])
        investor = summaries(report)["INV-0001"]
        self.assertEqual((investor.documented_deals, investor.last_investment_date), (3, "2025-03-12"))

    def test_general_financing_statement_is_not_evidence(self):
        report = validate_modified([("citations", "CIT-0011", "quote",
                                     "Vzorovou Akademii finančně podpořila Jana Příkladová.")])
        self.assertEqual(issue_keys(report), {
            ("WARNING", "INVESTMENT_NOT_EXPLICIT", "DEAL-0003", "instrument"),
            ("ERROR", "K3_NOT_MET", "INV-0002", ""),
        })

    def test_investment_loan_is_not_evidence(self):
        # „Investiční úvěr“ obsahuje slovo investice, ale jde o půjčku.
        report = validate_modified([("citations", "CIT-0011", "quote",
                                     "Jana Příkladová poskytla Vzorové Akademii investiční úvěr.")])
        self.assertIn(("ERROR", "K3_NOT_MET", "INV-0002", ""), issue_keys(report))

    def test_ticket_above_threshold_does_not_decide_type(self):
        # 500 tis. EUR je jen orientační vodítko: business angel s vyšším ticketem projde beze změny.
        report = validate_modified(
            [("investors", "INV-0002", "ticket_min", "600000"),
             ("investors", "INV-0002", "ticket_max", "1000000"),
             ("investors", "INV-0002", "ticket_currency", "EUR"),
             ("investors", "INV-0002", "ticket_status", "reported")],
            [("citations", {"citation_id": "CIT-0099", "entity_type": "investor",
                            "entity_id": "INV-0002", "fields": "ticket", "source_id": "SRC-0006",
                            "quote": "do jedné firmy obvykle vloží 600 tisíc až milion eur"})])
        self.assertEqual(report.issues, [])
        self.assertEqual(summaries(report)["INV-0002"].primary_type, "business_angel")

    def test_e9_requires_review_result(self):
        e9 = [("investors", "INV-0004", "rejection_code", "E9"),
              ("citations", "CIT-0014", "quote", "Za posouzení projektu účtujeme zakladatelům poplatek.")]
        self.assertEqual(issue_keys(validate_modified(e9)),
                         {("ERROR", "E9_REVIEW_MISSING", "INV-0004", "rejection_code")})
        reviewed = e9 + [("citations", "CIT-0014", "note",
                          "Prověřeno: poplatek potvrzuje web, žádná investice není doložená "
                          "v rejstříku ani v médiích.")]
        self.assertEqual(validate_modified(reviewed).issues, [])


class ActivityWindowTest(unittest.TestCase):
    """Aktivita: 24 měsíců, neúplné datum se vyhodnocuje konzervativně (plan.md, kap. 7.1)."""

    def activity_with_date(self, investment_date):
        report = validate_modified([("investments", "DEAL-0001", "investment_date", investment_date)])
        return summaries(report)["INV-0001"].activity_status

    def test_year_only_date_counts_from_first_day_of_year(self):
        self.assertEqual(self.activity_with_date("2024"), "inactive")
        self.assertEqual(self.activity_with_date("2025"), "active")

    def test_month_only_date_counts_from_first_day_of_month(self):
        self.assertEqual(self.activity_with_date("2024-10"), "inactive")
        self.assertEqual(self.activity_with_date("2024-11"), "active")

    def test_window_boundary_is_inclusive(self):
        self.assertEqual(self.activity_with_date("2024-10-14"), "active")
        self.assertEqual(self.activity_with_date("2024-10-13"), "inactive")


class SingleChangeTest(unittest.TestCase):
    """Jedna změna v platných datech musí vyvolat konkrétní hlášení.

    Každý případ je samostatný test (generuje se níže), aby ho unittest započítal zvlášť.
    """

    def test_semicolon_delimited_file_is_reported_once(self):
        def to_semicolons(data_dir):
            path = data_dir / "sources.csv"
            with path.open(encoding="utf-8", newline="") as handle:
                rows = list(csv.reader(handle))
            with path.open("w", encoding="utf-8", newline="") as handle:
                csv.writer(handle, delimiter=";", lineterminator="\n").writerows(rows)
        report = validate_modified(transform=to_semicolons)
        self.assertEqual(issue_keys(report), {("ERROR", "WRONG_DELIMITER", "", "")})

    def test_renamed_column_is_reported(self):
        def rename(data_dir):
            path = data_dir / "investors.csv"
            text = path.read_text(encoding="utf-8")
            path.write_text(text.replace(",notes\n", ",poznamky\n", 1), encoding="utf-8")
        report = validate_modified(transform=rename)
        self.assertEqual(issue_keys(report), {("ERROR", "MISSING_COLUMN", "", "notes"),
                                              ("WARNING", "UNKNOWN_COLUMN", "", "poznamky")})

    def test_missing_file_stops_content_checks(self):
        report = validate_modified(transform=lambda data_dir: (data_dir / "funds.csv").unlink())
        self.assertEqual(issue_keys(report), {("ERROR", "MISSING_FILE", "", "")})


SINGLE_CHANGE_CASES = [
    ([("investors", "INV-0001", "country", "Czechia")],
     ("ERROR", "INVALID_COUNTRY", "INV-0001", "country")),
    ([("investors", "INV-0001", "ticket_currency", "eur")],
     ("ERROR", "INVALID_CURRENCY", "INV-0001", "ticket_currency")),
    ([("investors", "INV-0001", "ticket_currency", "XYZ")],
     ("WARNING", "UNKNOWN_CURRENCY", "INV-0001", "ticket_currency")),
    ([("funds", "FND-0001", "size_amount", "")],
     ("WARNING", "CURRENCY_WITHOUT_AMOUNT", "FND-0001", "size_currency")),
    ([("funds", "FND-0001", "size_status", "derived")],
     ("ERROR", "INVALID_ENUM", "FND-0001", "size_status")),
    ([("investments", "DEAL-0001", "investor_amount", "2000000")],
     ("ERROR", "AMOUNT_EXCEEDS_ROUND", "DEAL-0001", "investor_amount")),
    ([("investments", "DEAL-0002", "investment_date", "")],
     ("ERROR", "DATE_BASIS_WITHOUT_DATE", "DEAL-0002", "date_basis")),
    ([("investments", "DEAL-0001", "date_basis", "registry_entry")],
     ("ERROR", "INVALID_ENUM", "DEAL-0001", "date_basis")),
    ([("investments", "DEAL-0005", "investor_amount", "20000"),
      ("investments", "DEAL-0005", "investor_currency", "CZK")],
     ("ERROR", "REGISTRY_CONTRIBUTION_AS_AMOUNT", "DEAL-0005", "investor_amount")),
    ([("investors", "INV-0005", "merged_into", "")],
     ("ERROR", "MERGED_INTO_INVALID", "INV-0005", "merged_into")),
    ([("investors", "INV-0001", "rejection_code", "E1")],
     ("ERROR", "REJECTION_CODE_NOT_ALLOWED", "INV-0001", "rejection_code")),
    ([("investors", "INV-0002", "identity_level", "I3")],
     ("ERROR", "K1_NOT_MET", "INV-0002", "identity_level")),
    ([("investors", "INV-0001", "registry_type", ""), ("investors", "INV-0001", "registry_id", "")],
     ("ERROR", "K1_NOT_MET", "INV-0001", "identity_level")),
    ([("investors", "INV-0001", "sectors_status", "")],
     ("ERROR", "MISSING_STATUS", "INV-0001", "sectors_status")),
    ([("investors", "INV-0003", "sectors", "fintech")],
     ("ERROR", "MISSING_STATUS", "INV-0003", "sectors_status")),
    ([("investors", "INV-0001", "sectors_original", "")],
     ("ERROR", "MISSING_ORIGINAL_LABEL", "INV-0001", "sectors_original")),
    ([("investors", "INV-0001", "sectors_original", "softwarových;fintech")],
     ("WARNING", "ORIGINAL_LABEL_NOT_IN_QUOTE", "INV-0001", "sectors_original")),
    ([("investors", "INV-0001", "aum_amount", "5000000"), ("investors", "INV-0001", "aum_currency", "EUR"),
      ("investors", "INV-0001", "aum_basis", "aum"), ("investors", "INV-0001", "aum_as_of", "2020"),
      ("investors", "INV-0001", "aum_status", "reported")],
     ("WARNING", "STALE_VALUE", "INV-0001", "aum_as_of")),
    ([("citations", "CIT-0001", "fields", "identity;country;ceo")],
     ("ERROR", "INVALID_CITATION_FIELD", "CIT-0001", "fields")),
    ([("citations", "CIT-0001", "entity_id", "INV-0999")],
     ("ERROR", "UNKNOWN_REFERENCE", "CIT-0001", "entity_id")),
    ([("citations", "CIT-0001", "quote", "x" * 301)],
     ("WARNING", "QUOTE_TOO_LONG", "CIT-0001", "quote")),
    ([("citations", "CIT-0015", "source_id", "SRC-0001")],
     ("WARNING", "UNUSED_SOURCE", "SRC-0010", "")),
    ([("sources", "SRC-0001", "archive_url", "")],
     ("WARNING", "MISSING_ARCHIVE", "SRC-0001", "archive_url")),
    ([("investors", "INV-0001", "investor_id", "INV-1")],
     ("ERROR", "INVALID_ID", "INV-1", "investor_id")),
]


def make_single_change_test(changes, expected):
    def test(self):
        self.assertIn(expected, issue_keys(validate_modified(changes)))
    return test


for index, (changes, expected) in enumerate(SINGLE_CHANGE_CASES, start=1):
    name = f"test_{index:02d}_{expected[1].lower()}_{expected[3] or 'record'}"
    setattr(SingleChangeTest, name, make_single_change_test(changes, expected))


class HelperTest(unittest.TestCase):
    def test_partial_dates(self):
        parsed = validate.parse_partial_date("2023")
        self.assertEqual((parsed.earliest, parsed.precision), (date(2023, 1, 1), "year"))
        self.assertEqual(validate.parse_partial_date("2023-07").precision, "month")
        for bad in ("2024-02-30", "2024-13", "23", "2024/05/01", "2024-5-1"):
            with self.assertRaises(ValueError):
                validate.parse_partial_date(bad)

    def test_months_before_clamps_day(self):
        self.assertEqual(validate.months_before(date(2024, 2, 29), 12), date(2023, 2, 28))
        self.assertEqual(validate.months_before(date(2026, 10, 14), 24), date(2024, 10, 14))

    def test_registry_checksums(self):
        self.assertTrue(validate.ico_is_valid("99999994"))
        self.assertFalse(validate.ico_is_valid("99999995"))
        self.assertFalse(validate.ico_is_valid("1234567"))
        self.assertTrue(validate.lei_is_valid("FIKTIVNILEI000000073"))
        self.assertFalse(validate.lei_is_valid("FIKTIVNILEI000000074"))

    def test_explicit_investment_terms(self):
        self.assertTrue(validate.is_explicit_investment("Mezi našimi investory je i Jana Příkladová."))
        self.assertTrue(validate.is_explicit_investment("X získal 20% podíl ve firmě Y."))
        self.assertFalse(validate.is_explicit_investment("X poskytl firmě Y finance na rozvoj."))
        self.assertFalse(validate.is_explicit_investment("X poskytl firmě Y investiční úvěr."))

    def test_country_list_is_complete(self):
        self.assertEqual(len(validate.COUNTRIES), 249)


if __name__ == "__main__":
    unittest.main()
