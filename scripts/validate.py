#!/usr/bin/env python3
"""Validace dat databáze investorů.

Kontroluje CSV tabulky popsané v docs/datovy-model.md:
- formát a povolené hodnoty sloupců,
- že každý důležitý údaj má v citations.csv zdroj (URL, datum) a krátkou citaci,
- propojení tabulek (investor, fond, investice, zdroj, citace),
- pravidla z docs/plan.md (K1–K3, AUM vs. velikost fondu, vyřazení),
- duplicitní registrační čísla (stejné IČO = jeden záznam) a původ kandidátů
  v nepovinném candidates.csv (zdroj z katalogu data/sources/catalog.csv).

Duplicity validátor jen hlásí. Ke kterému záznamu zjištění patří (párování),
rozhoduje koordinátor podle docs/overovaci-postup.md.

Odvozené hodnoty (počet doložených investic, poslední doložená investice,
aktivita, hodnocení A/B/C) se do CSV neukládají, počítá je tento skript.
Vyzkoušeno na Pythonu 3.12.13 a 3.14.4, používá jen standardní knihovnu.

Použití:
    python3 scripts/validate.py DATA_DIR [--today YYYY-MM-DD]

Návratový kód je 1, pokud validace najde alespoň jednu chybu.
"""

from __future__ import annotations

import argparse
import calendar
import csv
import re
import sys
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from pathlib import Path
from urllib.parse import urlparse

ERROR = "ERROR"
WARNING = "WARNING"

# --- Číselníky (docs/datovy-model.md, kapitola 7) ---

RECORD_STATUSES = {"included", "candidate", "rejected"}
REJECTION_CODES = {f"E{i}" for i in range(1, 11)}
PRIMARY_TYPES = {"vc", "pe", "family_office", "business_angel", "large_private_investor"}
NATURAL_PERSON_TYPES = {"business_angel", "large_private_investor"}
SUBTYPE_ALLOWED_TYPES = {
    "corporate": {"vc"},
    "accelerator": {"vc", "pe"},
    "public": {"vc", "pe"},
    "institutional": {"vc", "pe"},
    "angel_fund": {"vc", "pe"},
    "multi_family": {"family_office"},
}
REGISTRY_TYPES = {"cz_ico", "lei", "uk_company_number", "sec_crd", "other"}
IDENTITY_LEVELS = {"I1", "I2", "I3"}
SECTORS = {
    "software_saas", "ai_data", "fintech", "health_life_sciences", "cleantech_energy",
    "mobility_transport", "ecommerce_retail", "consumer", "edtech", "proptech_construction",
    "agrifood", "industrial_manufacturing", "deeptech_hardware", "cybersecurity",
    "media_gaming", "logistics", "business_services", "generalist",
}
STAGES = {"pre_seed", "seed", "series_a", "series_b", "series_c_plus", "growth", "buyout"}
REGIONS = {"CEE", "DACH", "NORDICS", "EUROPE", "GLOBAL"}
VALUE_STATUSES = {"reported", "derived", "estimate"}
MISSING_STATUSES = {"not_public", "conflicting", "not_applicable", "ambiguous"}
FUND_SIZE_STATUSES = {"reported", "not_public", "conflicting", "ambiguous"}
AUM_BASES = {"aum", "regulatory_aum"}
FUND_SIZE_TYPES = {"target", "first_close", "final_close"}
DATE_BASES = {"announcement", "stated_in_source"}
INSTRUMENTS = {"equity", "convertible_loan", "safe", "other_quasi_equity", "investment_unspecified",
               "unclear"}
# „unclear“ = není jasné, zda jde o kapitálovou investici, nebo půjčku. Taková investice
# se eviduje, ale jako doklad investování (K3, aktivita) se nepočítá.
EVIDENCE_INSTRUMENTS = INSTRUMENTS - {"unclear"}
# „investment_unspecified“ se jako doklad počítá jen tehdy, když citace výslovně mluví
# o investici nebo podílu a nemluví o úvěru (plan.md, K3). Jde o hrubou kontrolu textu
# pro pilot (čeština, angličtina); obsah citace nakonec posuzuje člověk.
INVESTMENT_TERMS = ("invest", "podíl", "akcie", "akcií", "akcion", "společník", "stake", "shares",
                    "shareholder")
LOAN_TERMS = ("úvěr", "půjč", "dluh", "loan", "debt")
ROUND_STAGES = STAGES | {"unknown"}
FOLLOW_ON_VALUES = {"true", "false", "unknown"}
TIERS = {"1", "2", "3", "4"}
CITABLE_TIERS = {"1", "2", "3"}
INDEPENDENT_TIERS = {"1", "2"}

COUNTRIES = set("""
AD AE AF AG AI AL AM AO AQ AR AS AT AU AW AX AZ BA BB BD BE BF BG BH BI BJ BL BM BN
BO BQ BR BS BT BV BW BY BZ CA CC CD CF CG CH CI CK CL CM CN CO CR CU CV CW CX CY CZ
DE DJ DK DM DO DZ EC EE EG EH ER ES ET FI FJ FK FM FO FR GA GB GD GE GF GG GH GI GL
GM GN GP GQ GR GS GT GU GW GY HK HM HN HR HT HU ID IE IL IM IN IO IQ IR IS IT JE JM
JO JP KE KG KH KI KM KN KP KR KW KY KZ LA LB LC LI LK LR LS LT LU LV LY MA MC MD ME
MF MG MH MK ML MM MN MO MP MQ MR MS MT MU MV MW MX MY MZ NA NC NE NF NG NI NL NO NP
NR NU NZ OM PA PE PF PG PH PK PL PM PN PR PS PT PW PY QA RE RO RS RU RW SA SB SC SD
SE SG SH SI SJ SK SL SM SN SO SR SS ST SV SX SY SZ TC TD TF TG TH TJ TK TL TM TN TO
TR TT TV TW TZ UA UG UM US UY UZ VA VC VE VG VI VN VU WF WS YE YT ZA ZM ZW
""".split())
CURRENCIES = set("""
EUR USD CZK GBP CHF PLN HUF RON BGN SEK NOK DKK ISK JPY CNY HKD SGD KRW INR AUD NZD
CAD BRL MXN ILS AED SAR TRY UAH ZAR
""".split())

# Pole, která lze doložit citací, podle typu entity (docs/datovy-model.md, kapitola 4).
CITABLE_FIELDS = {
    "investor": {"identity", "primary_type", "decision_authority", "country", "city", "sectors", "stages",
                 "geographies", "ticket", "aum", "rejection"},
    "fund": {"fund", "size"},
    "investment": {"deal", "investment_date", "round_amount", "investor_amount",
                   "registry_entry_date", "registry_contribution"},
}
ENTITY_TABLES = {"investor": "investors", "fund": "funds", "investment": "investments"}

# Skupiny popisných údajů investora a sloupce s jejich hodnotou. Ke každé skupině
# patří sloupec <skupina>_status s původem hodnoty nebo důvodem, proč chybí.
VALUE_GROUPS = {
    "sectors": ("sectors",),
    "stages": ("stages",),
    "geographies": ("geographies",),
    "ticket": ("ticket_min", "ticket_max"),
    "aum": ("aum_amount",),
}

STRUCTURE_CODES = {"MISSING_FILE", "MISSING_COLUMN", "WRONG_DELIMITER"}
QUOTE_MAX_LENGTH = 300
ACTIVE_WINDOW_MONTHS = 24
STALE_AFTER_MONTHS = 36

PARTIAL_DATE_RE = re.compile(r"(\d{4})(?:-(\d{2})(?:-(\d{2}))?)?")
FULL_DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")
AMOUNT_RE = re.compile(r"\d+(?:\.\d+)?")
CURRENCY_RE = re.compile(r"[A-Z]{3}")
PRECISION_RANK = {"year": 0, "month": 1, "day": 2}
CANDIDATE_METHODS = {"list", "search", "deal_report", "portfolio"}
CATALOG_PATH = Path(__file__).resolve().parents[1] / "data" / "sources" / "catalog.csv"


@dataclass(frozen=True)
class TableSpec:
    file_name: str
    id_column: str
    id_prefix: str
    columns: tuple[str, ...]
    optional: bool = False  # soubor nemusí existovat
    unique_ids: bool = True  # False: víc řádků smí mít stejné ID (víc nálezů téhož kandidáta)


TABLES = {
    "sources": TableSpec("sources.csv", "source_id", "SRC", (
        "source_id", "url", "publisher", "title", "tier", "published_date", "accessed_date",
        "archive_url",
    )),
    "investors": TableSpec("investors.csv", "investor_id", "INV", (
        "investor_id", "record_status", "rejection_code", "merged_into", "name", "aliases",
        "primary_type", "subtype", "country", "city", "website", "registry_type", "registry_id",
        "identity_level", "sectors", "sectors_original", "sectors_status", "stages", "stages_status",
        "geographies", "geographies_status", "ticket_min", "ticket_max", "ticket_currency",
        "ticket_status", "ticket_scope", "aum_amount", "aum_currency", "aum_basis", "aum_as_of", "aum_status",
        "notes",
    )),
    "funds": TableSpec("funds.csv", "fund_id", "FND", (
        "fund_id", "investor_id", "name", "vintage_year", "domicile_country", "size_amount",
        "size_currency", "size_type", "size_as_of", "size_status", "notes",
    )),
    "investments": TableSpec("investments.csv", "deal_id", "DEAL", (
        "deal_id", "investor_id", "fund_id", "company_name", "company_country",
        "company_registry_type", "company_registry_id", "investment_date", "date_basis",
        "instrument", "round_stage", "is_follow_on", "round_amount", "round_currency",
        "investor_amount", "investor_currency", "registry_entry_date",
        "registry_contribution_amount", "registry_contribution_currency", "notes",
    )),
    "citations": TableSpec("citations.csv", "citation_id", "CIT", (
        "citation_id", "entity_type", "entity_id", "fields", "source_id", "quote", "note",
    )),
    "candidates": TableSpec("candidates.csv", "candidate_id", "CAN", (
        "candidate_id", "name", "found_via", "found_url", "found_date", "how", "investor_id", "note",
    ), optional=True, unique_ids=False),
}


# --- Pomocné funkce ---

@dataclass(frozen=True)
class PartialDate:
    """Datum se známou přesností: rok, měsíc, nebo den (ISO 8601)."""

    raw: str
    earliest: date
    precision: str


def parse_partial_date(value: str) -> PartialDate:
    match = PARTIAL_DATE_RE.fullmatch(value)
    if not match:
        raise ValueError("očekávaný formát je YYYY, YYYY-MM nebo YYYY-MM-DD")
    year, month, day = match.groups()
    try:
        earliest = date(int(year), int(month or 1), int(day or 1))
    except ValueError as err:
        raise ValueError("takové datum neexistuje") from err
    precision = "day" if day else "month" if month else "year"
    return PartialDate(value, earliest, precision)


def months_before(day: date, months: int) -> date:
    index = day.year * 12 + day.month - 1 - months
    year, month = divmod(index, 12)
    month += 1
    return date(year, month, min(day.day, calendar.monthrange(year, month)[1]))


def split_list(value: str) -> list[str]:
    return [item.strip() for item in value.split(";") if item.strip()]


def is_valid_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc) and " " not in value


def is_explicit_investment(quote: str) -> bool:
    """Citace výslovně zmiňuje investici nebo podíl a nezmiňuje úvěr."""
    text = quote.casefold()
    return any(term in text for term in INVESTMENT_TERMS) and not any(
        term in text for term in LOAN_TERMS)


def ico_is_valid(value: str) -> bool:
    """České IČO: 8 číslic, poslední je kontrolní (vážený součet modulo 11)."""
    if not re.fullmatch(r"\d{8}", value):
        return False
    total = sum(int(digit) * weight for digit, weight in zip(value[:7], range(8, 1, -1)))
    return (11 - total % 11) % 10 == int(value[7])


def lei_is_valid(value: str) -> bool:
    """LEI (ISO 17442): 20 znaků, kontrolní číslice podle ISO 7064 MOD 97-10."""
    if not re.fullmatch(r"[A-Z0-9]{18}\d{2}", value):
        return False
    return int("".join(str(int(char, 36)) for char in value)) % 97 == 1


# --- Výsledek validace ---

@dataclass(frozen=True)
class Issue:
    severity: str
    code: str
    table: str
    line: int | None
    entity_id: str
    field: str
    message: str

    def format(self) -> str:
        label = "CHYBA" if self.severity == ERROR else "VAROVÁNÍ"
        location = self.table + ".csv" + (f":{self.line}" if self.line else "")
        parts = [f"[{label}]", self.code, location]
        if self.entity_id:
            parts.append(self.entity_id)
        if self.field:
            parts.append(f"({self.field})")
        return " ".join(parts) + f" – {self.message}"


@dataclass(frozen=True)
class InvestorSummary:
    investor_id: str
    record_status: str
    primary_type: str
    k2_verified: bool | None
    documented_deals: int | None
    last_investment_date: str
    activity_status: str
    confidence_grade: str
    last_deal_id: str = ""  # investice, ze které je last_investment_date
    documented_deal_ids: tuple[str, ...] = ()  # doložené investice (K3), od nejnovější


@dataclass
class Report:
    data_dir: Path
    today: date
    counts: dict[str, int]
    issues: list[Issue]
    investors: list[InvestorSummary]

    @property
    def errors(self) -> list[Issue]:
        return [issue for issue in self.issues if issue.severity == ERROR]

    @property
    def warnings(self) -> list[Issue]:
        return [issue for issue in self.issues if issue.severity == WARNING]


@dataclass
class Row:
    table: str
    line: int
    values: dict[str, str]

    def __getitem__(self, column: str) -> str:
        return self.values.get(column, "")

    @property
    def id(self) -> str:
        return self[TABLES[self.table].id_column]


@dataclass(frozen=True)
class Support:
    """Platná citace, která dokládá jeden údaj: zdroj, úryvek a případný popis metody."""

    citation_id: str
    source: Row
    quote: str
    note: str


# --- Validace ---

def load_catalog_keys(path: Path) -> set[str]:
    """Klíče zdrojů z katalogu (source_key). Chybějící katalog = prázdná množina."""
    if not path.exists():
        return set()
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return {(row.get("source_key") or "").strip() for row in csv.DictReader(handle)} - {""}


class Validator:
    def __init__(self, data_dir: Path, today: date, catalog: Path = CATALOG_PATH) -> None:
        self.data_dir = data_dir
        self.today = today
        self.catalog = catalog
        self.catalog_keys = load_catalog_keys(catalog)
        self.issues: list[Issue] = []
        self.rows: dict[str, list[Row]] = {name: [] for name in TABLES}
        self.by_id: dict[str, dict[str, Row]] = {name: {} for name in TABLES}
        self.support: dict[tuple[str, str, str], list[Support]] = {}
        self.used_sources: set[str] = set()
        self.source_published: dict[str, PartialDate] = {}
        self.deal_dates: dict[str, PartialDate] = {}
        self.fund_sizes: dict[str, list[tuple[Decimal, str]]] = {}
        self.deals_by_investor: dict[str, list[Row]] = {}
        self.inclusion_ok: dict[str, bool] = {}

    def run(self) -> Report:
        self._load()
        if any(issue.code in STRUCTURE_CODES for issue in self.issues):
            # Při chybné struktuře souborů by obsahové kontroly hlásily jen navazující chyby.
            counts = {name: len(rows) for name, rows in self.rows.items()}
            return Report(self.data_dir, self.today, counts, self.issues, [])
        for deal in self.rows["investments"]:
            self.deals_by_investor.setdefault(deal["investor_id"], []).append(deal)
        self._check_sources()
        self._check_citations()
        self._check_funds()
        self._check_investments()
        self._check_investors()
        self._check_duplicate_registry()
        self._check_candidates()
        self._check_unused_sources()
        counts = {name: len(rows) for name, rows in self.rows.items()}
        return Report(self.data_dir, self.today, counts, self.issues, self._summaries())

    # --- hlášení ---

    def _add(self, severity: str, row: Row, column: str, code: str, message: str) -> None:
        self.issues.append(Issue(severity, code, row.table, row.line, row.id, column, message))

    def _error(self, row: Row, column: str, code: str, message: str) -> None:
        self._add(ERROR, row, column, code, message)

    def _warn(self, row: Row, column: str, code: str, message: str) -> None:
        self._add(WARNING, row, column, code, message)

    # --- načtení ---

    def _load(self) -> None:
        for name, spec in TABLES.items():
            path = self.data_dir / spec.file_name
            if not path.exists() and spec.optional:
                continue
            if not path.exists():
                self.issues.append(Issue(ERROR, "MISSING_FILE", name, None, "", "",
                                         f"Soubor {spec.file_name} neexistuje."))
                continue
            with path.open(encoding="utf-8-sig", newline="") as handle:
                reader = csv.DictReader(handle)
                header = reader.fieldnames or []
                if len(header) == 1 and ";" in header[0]:
                    self.issues.append(Issue(
                        ERROR, "WRONG_DELIMITER", name, 1, "", "",
                        "Soubor je uložený se středníkem jako oddělovačem (typicky Excel s českým "
                        "nastavením). Oddělovačem sloupců musí být čárka."))
                    continue
                for column in spec.columns:
                    if column not in header:
                        self.issues.append(Issue(ERROR, "MISSING_COLUMN", name, 1, "", column,
                                                 "V hlavičce chybí povinný sloupec."))
                for column in header:
                    if column not in spec.columns:
                        self.issues.append(Issue(WARNING, "UNKNOWN_COLUMN", name, 1, "", column,
                                                 "Neznámý sloupec, validátor ho ignoruje."))
                for record in reader:
                    values = {key: (value or "").strip()
                              for key, value in record.items() if isinstance(key, str)}
                    if any(values.values()):
                        self._register(Row(name, reader.line_num, values), spec)

    def _register(self, row: Row, spec: TableSpec) -> None:
        self.rows[row.table].append(row)
        row_id = row.id
        if not row_id:
            self._error(row, spec.id_column, "MISSING_VALUE", "Chybí ID záznamu.")
            return
        if not re.fullmatch(rf"{spec.id_prefix}-\d{{4}}", row_id):
            self._error(row, spec.id_column, "INVALID_ID",
                        f"ID musí mít tvar {spec.id_prefix}-0000.")
        first = self.by_id[row.table].get(row_id)
        if first is not None and not spec.unique_ids:
            return
        if first is not None:
            self._error(row, spec.id_column, "DUPLICATE_ID",
                        f"ID už je použité na řádku {first.line}.")
        else:
            self.by_id[row.table][row_id] = row

    # --- kontroly jednotlivých hodnot ---

    def _require(self, row: Row, *columns: str) -> None:
        for column in columns:
            if not row[column]:
                self._error(row, column, "MISSING_VALUE", "Povinná hodnota chybí.")

    def _check_enum(self, row: Row, column: str, allowed: set[str], hint: str = "") -> bool:
        value = row[column]
        if value and value not in allowed:
            message = f"Neplatná hodnota „{value}“. Povolené: {', '.join(sorted(allowed))}."
            self._error(row, column, "INVALID_ENUM", f"{message} {hint}".strip())
            return False
        return True

    def _check_list(self, row: Row, column: str, allowed: set[str]) -> None:
        for item in split_list(row[column]):
            if item not in allowed:
                self._error(row, column, "INVALID_ENUM",
                            f"Neplatná položka „{item}“ (viz číselník v docs/datovy-model.md).")

    def _check_country(self, row: Row, column: str) -> None:
        value = row[column]
        if value and value not in COUNTRIES:
            self._error(row, column, "INVALID_COUNTRY",
                        f"„{value}“ není kód země podle ISO 3166-1 alpha-2 (např. CZ).")

    def _check_url(self, row: Row, column: str) -> None:
        value = row[column]
        if value and not is_valid_url(value):
            self._error(row, column, "INVALID_URL", f"„{value}“ není platná adresa http(s).")

    def _check_partial_date(self, row: Row, column: str) -> PartialDate | None:
        value = row[column]
        if not value:
            return None
        try:
            parsed = parse_partial_date(value)
        except ValueError as err:
            self._error(row, column, "INVALID_DATE", f"Neplatné datum „{value}“: {err}.")
            return None
        if parsed.earliest > self.today:
            self._error(row, column, "FUTURE_DATE", f"Datum {value} je v budoucnosti.")
            return None
        return parsed

    def _check_full_date(self, row: Row, column: str) -> date | None:
        value = row[column]
        if not value:
            return None
        parsed = None
        if FULL_DATE_RE.fullmatch(value):
            try:
                parsed = date.fromisoformat(value)
            except ValueError:
                parsed = None
        if parsed is None:
            self._error(row, column, "INVALID_DATE",
                        f"Neplatné datum „{value}“, očekávaný formát je YYYY-MM-DD.")
            return None
        if parsed > self.today:
            self._error(row, column, "FUTURE_DATE", f"Datum {value} je v budoucnosti.")
            return None
        return parsed

    def _check_money(self, row: Row, amount_columns: tuple[str, ...],
                     currency_column: str) -> dict[str, Decimal]:
        amounts = {}
        for column in amount_columns:
            value = row[column]
            if not value:
                continue
            if AMOUNT_RE.fullmatch(value) and Decimal(value) > 0:
                amounts[column] = Decimal(value)
            else:
                self._error(row, column, "INVALID_AMOUNT",
                            f"„{value}“ není platná částka. Zapisuje se kladné číslo v základních "
                            "jednotkách bez mezer a zkratek, např. 1500000.")
        present = any(row[column] for column in amount_columns)
        currency = row[currency_column]
        if present and not currency:
            self._error(row, currency_column, "MISSING_CURRENCY",
                        "Částka je vyplněná, ale chybí měna (ISO 4217, např. EUR).")
        elif currency and not CURRENCY_RE.fullmatch(currency):
            self._error(row, currency_column, "INVALID_CURRENCY",
                        f"„{currency}“ není kód měny podle ISO 4217 (např. EUR).")
        elif currency and currency not in CURRENCIES:
            self._warn(row, currency_column, "UNKNOWN_CURRENCY",
                       f"Měna {currency} není v seznamu běžných měn, ověřte ji.")
        if currency and not present:
            self._warn(row, currency_column, "CURRENCY_WITHOUT_AMOUNT",
                       "Měna je vyplněná, ale částka chybí.")
        return amounts

    def _check_registry(self, row: Row, type_column: str, id_column: str) -> None:
        if not self._check_enum(row, type_column, REGISTRY_TYPES):
            return
        registry_type, registry_id = row[type_column], row[id_column]
        if registry_id and not registry_type:
            self._error(row, type_column, "MISSING_VALUE", "K registračnímu číslu chybí typ registru.")
        elif registry_type and not registry_id:
            self._error(row, id_column, "MISSING_VALUE", "Typ registru je vyplněný, ale číslo chybí.")
        elif registry_type == "cz_ico" and not ico_is_valid(registry_id):
            self._error(row, id_column, "INVALID_REGISTRY_ID",
                        f"IČO {registry_id} nemá 8 číslic nebo platný kontrolní součet.")
        elif registry_type == "lei" and not lei_is_valid(registry_id):
            self._error(row, id_column, "INVALID_REGISTRY_ID",
                        f"LEI {registry_id} nemá platný formát nebo kontrolní číslice.")

    def _check_reference(self, row: Row, column: str, table: str) -> Row | None:
        value = row[column]
        if not value:
            return None
        target = self.by_id[table].get(value)
        if target is None:
            self._error(row, column, "UNKNOWN_REFERENCE",
                        f"Odkaz na neexistující záznam {value} v {TABLES[table].file_name}.")
        return target

    # --- citace ---

    def _supports(self, entity_type: str, entity_id: str, field: str) -> list[Support]:
        return self.support.get((entity_type, entity_id, field), [])

    def _sources_for(self, entity_type: str, entity_id: str, field: str,
                     tiers: set[str] = CITABLE_TIERS) -> list[Row]:
        return [support.source for support in self._supports(entity_type, entity_id, field)
                if support.source["tier"] in tiers]

    def _has_note(self, entity_type: str, entity_id: str, field: str) -> bool:
        return any(support.note for support in self._supports(entity_type, entity_id, field))

    def _require_source(self, row: Row, entity_type: str, field: str) -> None:
        if not self._sources_for(entity_type, row.id, field):
            self._error(row, field, "MISSING_CITATION",
                        "Údaj nemá v citations.csv platnou citaci se zdrojem a krátkou citací.")

    # --- tabulky ---

    def _check_sources(self) -> None:
        for row in self.rows["sources"]:
            self._require(row, "url", "publisher", "tier", "accessed_date")
            self._check_url(row, "url")
            self._check_enum(row, "tier", TIERS)
            published = self._check_partial_date(row, "published_date")
            accessed = self._check_full_date(row, "accessed_date")
            if published:
                self.source_published[row.id] = published
                if accessed and published.earliest > accessed:
                    self._error(row, "published_date", "INVALID_DATE",
                                "Datum publikace je pozdější než datum přístupu.")
            if row["archive_url"]:
                self._check_url(row, "archive_url")
            else:
                self._warn(row, "archive_url", "MISSING_ARCHIVE",
                           "Chybí archivní kopie zdroje (např. Wayback Machine).")

    def _check_citations(self) -> None:
        for row in self.rows["citations"]:
            self._require(row, "entity_type", "entity_id", "fields")
            entity_type, entity_id = row["entity_type"], row["entity_id"]
            if not self._check_enum(row, "entity_type", set(CITABLE_FIELDS)) or not entity_type:
                continue
            entity_exists = bool(entity_id) and entity_id in self.by_id[ENTITY_TABLES[entity_type]]
            if entity_id and not entity_exists:
                self._error(row, "entity_id", "UNKNOWN_REFERENCE",
                            f"Citovaný záznam {entity_id} neexistuje.")
            fields = []
            for field in split_list(row["fields"]):
                if field in CITABLE_FIELDS[entity_type]:
                    fields.append(field)
                else:
                    self._error(row, "fields", "INVALID_CITATION_FIELD",
                                f"Pole „{field}“ nelze u entity {entity_type} citovat. Povolená: "
                                f"{', '.join(sorted(CITABLE_FIELDS[entity_type]))}.")
            # Každá citace musí mít zdroj a úryvek, i u odvozených a odhadnutých hodnot:
            # popis metody v note nestačí, musí být dohledatelné i původní zdroje.
            source = None
            if not row["source_id"]:
                self._error(row, "source_id", "MISSING_SOURCE",
                            "Citace nemá zdroj. U odvozené nebo odhadnuté hodnoty musí odkazovat "
                            "na původní zdroj, ze kterého výpočet vychází; popis metody v note nestačí.")
            else:
                source = self.by_id["sources"].get(row["source_id"])
                if source is None:
                    self._error(row, "source_id", "UNKNOWN_REFERENCE",
                                f"Zdroj {row['source_id']} neexistuje v sources.csv.")
                else:
                    self.used_sources.add(source.id)
                    if source["tier"] == "4":
                        self._error(row, "source_id", "AGGREGATOR_AS_EVIDENCE",
                                    "Agregátor (tier 4) slouží jen k hledání kandidátů, "
                                    "ne jako doklad údaje (plan.md, kap. 6.1).")
                        source = None
                if not row["quote"]:
                    self._error(row, "quote", "MISSING_QUOTE", "Chybí krátká citace ze zdroje.")
                elif len(row["quote"]) > QUOTE_MAX_LENGTH:
                    self._warn(row, "quote", "QUOTE_TOO_LONG",
                               f"Citace má víc než {QUOTE_MAX_LENGTH} znaků, zkraťte ji.")
            if source is not None and row["quote"] and entity_exists:
                for field in fields:
                    self.support.setdefault((entity_type, entity_id, field), []).append(
                        Support(row.id, source, row["quote"], row["note"]))

    def _check_funds(self) -> None:
        for row in self.rows["funds"]:
            self._require(row, "investor_id", "name")
            self._check_reference(row, "investor_id", "investors")
            vintage = row["vintage_year"]
            if vintage and not re.fullmatch(r"\d{4}", vintage):
                self._error(row, "vintage_year", "INVALID_DATE", "Vintage je rok ve tvaru YYYY.")
            elif vintage and int(vintage) > self.today.year:
                self._error(row, "vintage_year", "FUTURE_DATE", f"Rok {vintage} je v budoucnosti.")
            self._check_country(row, "domicile_country")
            size = self._check_money(row, ("size_amount",), "size_currency")
            if size and row["size_currency"]:
                self.fund_sizes.setdefault(row["investor_id"], []).append(
                    (size["size_amount"], row["size_currency"]))
            self._check_enum(row, "size_type", FUND_SIZE_TYPES)
            self._check_partial_date(row, "size_as_of")
            status = row["size_status"]
            status_ok = self._check_enum(
                row, "size_status", FUND_SIZE_STATUSES,
                hint="Velikost fondu se neodvozuje ani neodhaduje (plan.md, kap. 10.1).")
            if row["size_amount"]:
                if not row["size_type"]:
                    self._error(row, "size_type", "FUND_SIZE_TYPE_REQUIRED",
                                "U velikosti fondu musí být typ: target, first_close, nebo final_close.")
                if not row["size_as_of"]:
                    self._error(row, "size_as_of", "MISSING_AS_OF",
                                "U velikosti fondu chybí datum, ke kterému platí.")
                if not status:
                    self._error(row, "size_status", "MISSING_STATUS",
                                "Velikost fondu je vyplněná, ale chybí size_status=reported.")
                elif status_ok and status != "reported":
                    self._error(row, "size_status", "STATUS_VALUE_MISMATCH",
                                f"Stav „{status}“ znamená chybějící hodnotu, ale velikost je vyplněná.")
                self._require_source(row, "fund", "size")
            elif status == "reported":
                self._error(row, "size_status", "STATUS_VALUE_MISMATCH",
                            "Stav „reported“ vyžaduje vyplněnou velikost fondu.")
            elif status in {"ambiguous", "conflicting"}:
                self._require_source(row, "fund", "size")
            self._require_source(row, "fund", "fund")

    def _check_investments(self) -> None:
        for row in self.rows["investments"]:
            self._require(row, "investor_id", "company_name", "instrument", "round_stage",
                          "is_follow_on")
            self._check_reference(row, "investor_id", "investors")
            fund = self._check_reference(row, "fund_id", "funds")
            if fund is not None and fund["investor_id"] != row["investor_id"]:
                self._error(row, "fund_id", "FUND_INVESTOR_MISMATCH",
                            f"Fond {fund.id} patří investorovi {fund['investor_id']}, "
                            f"ne {row['investor_id']}.")
            self._check_country(row, "company_country")
            self._check_registry(row, "company_registry_type", "company_registry_id")
            deal_date = self._check_partial_date(row, "investment_date")
            if deal_date:
                self.deal_dates[row.id] = deal_date
                if deal_date.precision == "day" and deal_date.raw.endswith("-01-01"):
                    self._warn(row, "investment_date", "POSSIBLE_PLACEHOLDER_DATE",
                               "Datum 1. 1. bývá doplněný odhad. Pokud zdroj uvádí jen rok, "
                               "uložte jen rok (plan.md, kap. 7.1).")
            self._check_enum(row, "date_basis", DATE_BASES,
                             hint="Datum zápisu do rejstříku patří do registry_entry_date, "
                                  "není to datum investice.")
            if row["investment_date"] and not row["date_basis"]:
                self._error(row, "date_basis", "DATE_BASIS_REQUIRED",
                            "U data investice chybí, z čeho pochází (announcement, stated_in_source).")
            elif row["date_basis"] and not row["investment_date"]:
                self._error(row, "date_basis", "DATE_BASIS_WITHOUT_DATE",
                            "date_basis je vyplněné, ale datum investice chybí.")
            self._check_partial_date(row, "registry_entry_date")
            self._check_enum(row, "instrument", INSTRUMENTS,
                             hint="Čistě dluhové financování není investice a do investments.csv "
                                  "nepatří (plan.md, kap. 3).")
            if row["instrument"] == "investment_unspecified":
                supports = self._transaction_supports(row)
                if supports and not any(is_explicit_investment(s.quote) for s in supports):
                    self._warn(row, "instrument", "INVESTMENT_NOT_EXPLICIT",
                               "Citace výslovně nezmiňuje investici ani podíl, nebo zmiňuje úvěr. "
                               "Obecné „poskytl financování“ nestačí a investice se jako doklad "
                               "nepočítá. Pokud zdroj víc neříká, použijte instrument=unclear; "
                               "jinak citujte větu, která investici výslovně uvádí.")
            self._check_enum(row, "round_stage", ROUND_STAGES)
            self._check_enum(row, "is_follow_on", FOLLOW_ON_VALUES)
            round_amount = self._check_money(row, ("round_amount",), "round_currency")
            own_amount = self._check_money(row, ("investor_amount",), "investor_currency")
            contribution = self._check_money(row, ("registry_contribution_amount",),
                                             "registry_contribution_currency")
            if (round_amount and own_amount and row["round_currency"] == row["investor_currency"]
                    and own_amount["investor_amount"] > round_amount["round_amount"]):
                self._error(row, "investor_amount", "AMOUNT_EXCEEDS_ROUND",
                            "Částka investora je vyšší než celé kolo.")
            self._require_source(row, "investment", "deal")
            for column in ("investment_date", "round_amount", "investor_amount", "registry_entry_date"):
                if row[column]:
                    self._require_source(row, "investment", column)
            if row["registry_contribution_amount"]:
                self._require_source(row, "investment", "registry_contribution")
            self._check_registry_copies(row, round_amount | own_amount, contribution)

    def _check_registry_copies(self, row: Row, amounts: dict[str, Decimal],
                               contribution: dict[str, Decimal]) -> None:
        """Datum zápisu a vklad z rejstříku nejsou datum a výše investice (plan.md, kap. 7.1).

        Shoda je chyba, pokud hodnotu investice nedokládá žádný jiný zdroj než ten,
        ze kterého pochází zápis v rejstříku.
        """
        registry_sources = self._registry_sources(row.id)

        def only_from_registry(field: str) -> bool:
            return {s.id for s in self._sources_for("investment", row.id, field)} <= registry_sources

        if (row["investment_date"] and row["investment_date"] == row["registry_entry_date"]
                and only_from_registry("investment_date")):
            self._error(row, "investment_date", "REGISTRY_DATE_AS_INVESTMENT_DATE",
                        "Datum investice je převzaté z data zápisu do rejstříku. Zápis bývá až po "
                        "investici; datum investice uveďte jen ze zdroje, který ho výslovně uvádí.")
        if not contribution:
            return
        value = contribution["registry_contribution_amount"]
        currency = row["registry_contribution_currency"]
        for column, currency_column in (("round_amount", "round_currency"),
                                        ("investor_amount", "investor_currency")):
            if (amounts.get(column) == value and row[currency_column] == currency
                    and only_from_registry(column)):
                self._error(row, column, "REGISTRY_CONTRIBUTION_AS_AMOUNT",
                            "Částka je převzatá ze vkladu zapsaného v rejstříku. Vklad do základního "
                            "kapitálu bývá jen zlomek skutečné investice (zbytek tvoří ážio); "
                            "výši investice uveďte jen ze zdroje, který ji výslovně uvádí.")

    def _check_investors(self) -> None:
        for row in self.rows["investors"]:
            status = row["record_status"]
            primary_type, subtype = row["primary_type"], row["subtype"]
            self._require(row, "record_status", "name")
            self._check_enum(row, "record_status", RECORD_STATUSES)
            self._check_enum(row, "rejection_code", REJECTION_CODES)
            type_ok = self._check_enum(row, "primary_type", PRIMARY_TYPES)
            subtype_ok = self._check_enum(row, "subtype", set(SUBTYPE_ALLOWED_TYPES))
            self._check_enum(row, "identity_level", IDENTITY_LEVELS)
            self._check_country(row, "country")
            self._check_url(row, "website")
            self._check_registry(row, "registry_type", "registry_id")
            self._check_list(row, "sectors", SECTORS)
            self._check_list(row, "stages", STAGES)
            self._check_list(row, "geographies", COUNTRIES | REGIONS)
            ticket = self._check_money(row, ("ticket_min", "ticket_max"), "ticket_currency")
            aum = self._check_money(row, ("aum_amount",), "aum_currency")
            self._check_enum(row, "aum_basis", AUM_BASES,
                             hint="Celkový upsaný kapitál fondů (committed capital) není AUM; "
                                  "jednotlivé fondy patří do funds.csv (plan.md, kap. 10.1).")
            aum_as_of = self._check_partial_date(row, "aum_as_of")

            if type_ok and subtype_ok and subtype and primary_type not in SUBTYPE_ALLOWED_TYPES[subtype]:
                allowed = ", ".join(sorted(SUBTYPE_ALLOWED_TYPES[subtype]))
                self._error(row, "subtype", "SUBTYPE_TYPE_MISMATCH",
                            f"Subtype „{subtype}“ nelze kombinovat s typem "
                            f"„{primary_type or '(prázdný)'}“. Povolené typy: {allowed}.")
            if len(ticket) == 2 and ticket["ticket_min"] > ticket["ticket_max"]:
                self._error(row, "ticket_min", "TICKET_RANGE_INVALID",
                            "Typická investice „od“ je vyšší než „do“.")
            self._check_aum(row, aum.get("aum_amount"), aum_as_of)
            self._check_value_statuses(row, included=status == "included")
            self._check_sector_labels(row)

            for column, field in (("registry_id", "identity"), ("country", "country"), ("city", "city"),
                                  ("primary_type", "primary_type")):
                if row[column]:
                    self._require_source(row, "investor", field)

            if status == "rejected":
                self._check_rejection(row)
            elif row["rejection_code"] or row["merged_into"]:
                self._error(row, "rejection_code", "REJECTION_CODE_NOT_ALLOWED",
                            "rejection_code a merged_into patří jen k vyřazeným záznamům.")
            if status == "included":
                self._require(row, "primary_type", "country", "identity_level")
                k1 = self._check_k1(row)
                k2 = self._check_k2(row)
                k3 = self._check_k3(row)
                self.inclusion_ok[row.id] = k1 and k2 and k3

    def _check_duplicate_registry(self) -> None:
        """Stejné registrační číslo = stejná právnická osoba = jeden záznam, i mezi vyřazenými.

        Jde jen o kontrolu duplicit. Párování (ke kterému záznamu nové zjištění patří, a zda
        další právnickou osobu značky sloučit jako E10) rozhoduje koordinátor podle
        docs/overovaci-postup.md, bod 3. Validátor nic neslučuje.
        """
        first_with: dict[tuple[str, ...], Row] = {}
        for row in self.rows["investors"]:
            key: tuple[str, ...] = (row["registry_type"], row["registry_id"])
            if not all(key):
                continue
            if row["registry_type"] == "other":
                key += (row["country"],)  # čísla různých zahraničních registrů se mohou shodovat
            first = first_with.setdefault(key, row)
            if first is not row:
                self._error(row, "registry_id", "DUPLICATE_REGISTRY_ID",
                            f"Registrační číslo {row['registry_id']} už má záznam {first.id}. "
                            "Jedna právnická osoba má jeden záznam: zjištění přiřaďte k existujícímu "
                            "záznamu (docs/overovaci-postup.md, bod 3).")

    def _check_candidates(self) -> None:
        """Původ kandidátů: jeden řádek = jeden nález kandidáta v jednom zdroji z katalogu.

        Kandidát nalezený ve více zdrojích má víc řádků se stejným candidate_id. investor_id je
        nepovinné a vyplní se, až kandidát dostane záznam v investors.csv.
        """
        first_of: dict[str, Row] = {}
        for row in self.rows["candidates"]:
            self._require(row, "name", "found_via", "found_url", "found_date", "how")
            source_key = row["found_via"]
            if source_key and source_key not in self.catalog_keys:
                self._error(row, "found_via", "UNKNOWN_SOURCE_KEY",
                            f"Zdroj {source_key} není v katalogu zdrojů ({self.catalog.name}). "
                            "Nový zdroj se nejdřív popíše v data/sources/.")
            self._check_url(row, "found_url")
            self._check_full_date(row, "found_date")
            self._check_enum(row, "how", CANDIDATE_METHODS)
            self._check_reference(row, "investor_id", "investors")
            if not row.id:
                continue
            first = first_of.setdefault(row.id, row)
            if first is not row and first["investor_id"] != row["investor_id"]:
                self._error(row, "investor_id", "CANDIDATE_INVESTOR_MISMATCH",
                            f"Stejný kandidát má na řádku {first.line} investor_id "
                            f"„{first['investor_id'] or '(prázdné)'}“. Všechny nálezy jednoho "
                            "kandidáta patří k jednomu záznamu.")

    def _check_sector_labels(self, row: Row) -> None:
        """Původní označení sektorů ze zdroje se uchovává doslovně vedle číselníku."""
        if row["sectors"] and not row["sectors_original"]:
            self._error(row, "sectors_original", "MISSING_ORIGINAL_LABEL",
                        "Chybí původní označení sektorů ze zdroje (doslovně, oddělené středníkem).")
        elif row["sectors_original"] and not row["sectors"]:
            self._error(row, "sectors", "MISSING_VALUE",
                        "Původní označení je vyplněné, ale chybí zařazení do číselníku sektorů.")
        quotes = [support.quote.casefold() for support in self._supports("investor", row.id, "sectors")]
        if not quotes:
            return  # chybějící citaci hlásí kontrola stavů
        for label in split_list(row["sectors_original"]):
            if not any(label.casefold() in quote for quote in quotes):
                self._warn(row, "sectors_original", "ORIGINAL_LABEL_NOT_IN_QUOTE",
                           f"Původní označení „{label}“ není doslovně v žádné citaci sektorů.")

    def _check_aum(self, row: Row, aum: Decimal | None, aum_as_of: PartialDate | None) -> None:
        if row["aum_status"] == "derived":
            self._error(row, "aum_status", "AUM_DERIVED_NOT_ALLOWED",
                        "AUM se neodvozuje, např. jako součet fondů (plan.md, kap. 10.1).")
        if not row["aum_amount"]:
            return
        # AUM shodné s velikostí fondu nebo se součtem fondů naznačuje záměnu s upsaným kapitálem.
        sizes = [amount for amount, currency in self.fund_sizes.get(row.id, [])
                 if currency == row["aum_currency"]]
        if aum is not None and aum in sizes:
            self._warn(row, "aum_amount", "AUM_MATCHES_FUND_SIZE",
                       "AUM je shodné s velikostí jednoho fondu. Ověřte, že zdroj opravdu uvádí "
                       "AUM, ne velikost fondu.")
        elif aum is not None and len(sizes) >= 2 and aum == sum(sizes):
            self._warn(row, "aum_amount", "AUM_MATCHES_FUND_TOTAL",
                       "AUM je shodné se součtem velikostí fondů. Ověřte, že nejde o celkový upsaný "
                       "kapitál fondů (committed capital), který se jako AUM nezapisuje.")
        if row["primary_type"] in NATURAL_PERSON_TYPES:
            self._error(row, "aum_amount", "AUM_FOR_NATURAL_PERSON",
                        "Fyzická osoba nespravuje AUM a osobní majetek se jako AUM nezapisuje "
                        "(plan.md, kap. 10.1).")
        if not row["aum_basis"]:
            self._error(row, "aum_basis", "AUM_BASIS_REQUIRED",
                        "Chybí aum_basis. Pokud zdroj neříká, co částka představuje, nechte AUM "
                        "prázdné a nastavte aum_status=ambiguous.")
        if not row["aum_as_of"]:
            self._error(row, "aum_as_of", "MISSING_AS_OF", "U AUM chybí datum, ke kterému platí.")
        elif aum_as_of and aum_as_of.earliest < months_before(self.today, STALE_AFTER_MONTHS):
            self._warn(row, "aum_as_of", "STALE_VALUE", "Údaj o AUM je starší než 3 roky.")

    def _check_value_statuses(self, row: Row, included: bool) -> None:
        for group, columns in VALUE_GROUPS.items():
            column = f"{group}_status"
            status = row[column]
            if not self._check_enum(row, column, VALUE_STATUSES | MISSING_STATUSES):
                continue
            present = any(row[value_column] for value_column in columns)
            if present and not status:
                self._error(row, column, "MISSING_STATUS",
                            "Hodnota je vyplněná, ale chybí její původ (reported, derived, estimate).")
            elif present and status in MISSING_STATUSES:
                self._error(row, column, "STATUS_VALUE_MISMATCH",
                            f"Stav „{status}“ znamená chybějící hodnotu, ale hodnota je vyplněná.")
            elif not present and status in VALUE_STATUSES:
                self._error(row, column, "STATUS_VALUE_MISMATCH",
                            f"Stav „{status}“ vyžaduje vyplněnou hodnotu.")
            elif not present and not status and included:
                self._error(row, column, "MISSING_STATUS",
                            "Zařazený investor musí mít hodnotu, nebo důvod, proč chybí "
                            "(not_public, conflicting, not_applicable, ambiguous).")
            if present or status in {"ambiguous", "conflicting"}:
                self._require_source(row, "investor", group)
            if (present and status in {"derived", "estimate"}
                    and self._supports("investor", row.id, group)
                    and not self._has_note("investor", row.id, group)):
                self._error(row, group, "MISSING_METHOD",
                            "Odvozená nebo odhadnutá hodnota musí mít v citaci popis metody (note).")

    def _check_rejection(self, row: Row) -> None:
        code = row["rejection_code"]
        if not code:
            self._error(row, "rejection_code", "REJECTION_CODE_REQUIRED",
                        "Vyřazený záznam musí mít kód důvodu E1–E10 (plan.md, kap. 8).")
        if code == "E10":
            if not row["merged_into"]:
                self._error(row, "merged_into", "MERGED_INTO_INVALID",
                            "Kód E10 vyžaduje merged_into s ID nadřazeného záznamu.")
            elif row["merged_into"] == row.id:
                self._error(row, "merged_into", "MERGED_INTO_INVALID",
                            "Záznam nemůže být sloučený sám do sebe.")
            else:
                target = self._check_reference(row, "merged_into", "investors")
                if target is not None and target["record_status"] == "rejected":
                    self._error(row, "merged_into", "MERGED_INTO_INVALID",
                                f"Cílový záznam {target.id} je také vyřazený.")
        elif row["merged_into"]:
            self._error(row, "merged_into", "MERGED_INTO_INVALID",
                        "merged_into se používá jen s kódem E10.")
        self._require_source(row, "investor", "rejection")
        if (code == "E9" and self._supports("investor", row.id, "rejection")
                and not self._has_note("investor", row.id, "rejection")):
            self._error(row, "rejection_code", "E9_REVIEW_MISSING",
                        "E9 se použije až po prověření, varovné signály samy nestačí. Citace "
                        "rejection musí v note popsat, co bylo prověřeno a co podezření potvrdilo "
                        "(plan.md, kap. 8). Do té doby zůstává záznam kandidátem.")

    def _check_k1(self, row: Row) -> bool:
        level = row["identity_level"]
        if not level:
            return False
        if level == "I1":
            ok = bool(row["registry_type"] and row["registry_id"]) and bool(
                self._sources_for("investor", row.id, "identity", {"1"}))
            message = "I1 vyžaduje registrační číslo a citaci identity z úředního zdroje (tier 1)."
        elif level == "I2":
            ok = bool(self._sources_for("investor", row.id, "identity", INDEPENDENT_TIERS))
            message = "I2 vyžaduje citaci identity z nezávislého zdroje (tier 1 nebo 2)."
        else:
            ok = False
            message = "Zařazený investor musí mít identitu I1 nebo I2 (plan.md, K1)."
        if not ok:
            self._error(row, "identity_level", "K1_NOT_MET", message)
        return ok

    def _check_k2(self, row: Row) -> bool:
        if self._sources_for("investor", row.id, "decision_authority"):
            return True
        self._error(row, "", "K2_NOT_MET",
                    "K2 není posouzená: chybí citace decision_authority, ze které plyne, že investor "
                    "sám rozhoduje o investicích (plan.md, K2). Bez ní se investor nezařazuje.")
        return False

    def _registry_sources(self, deal_id: str) -> set[str]:
        """Zdroje, ze kterých pochází zápis společníka v rejstříku (citují pole registry_*)."""
        return {source.id for field in ("registry_entry_date", "registry_contribution")
                for source in self._sources_for("investment", deal_id, field)}

    def _transaction_supports(self, deal: Row) -> list[Support]:
        """Citace deal z nezávislých zdrojů (tier 1/2) kromě výpisu zápisu v rejstříku.

        Zápis společníka dokládá vlastnictví podílu, ne investiční transakci. Zdroj, ze kterého
        pochází, se proto u téže investice jako doklad nepočítá (plan.md, kap. 6.4).
        """
        registry = self._registry_sources(deal.id)
        return [support for support in self._supports("investment", deal.id, "deal")
                if support.source["tier"] in INDEPENDENT_TIERS and support.source.id not in registry]

    def _deal_evidence(self, deal: Row) -> list[Row]:
        """Nezávislé zdroje, které dokládají investiční transakci a mají k ní datum.

        Nepočítá se investice s nástrojem „unclear“ (nevíme, zda nejde o půjčku) a u nástroje
        „investment_unspecified“ citace, která investici výslovně nezmiňuje. Datem dokladu
        je datum investice, jinak datum publikace zdroje.
        """
        if deal["instrument"] not in EVIDENCE_INSTRUMENTS:
            return []
        supports = self._transaction_supports(deal)
        if deal["instrument"] == "investment_unspecified":
            supports = [support for support in supports if is_explicit_investment(support.quote)]
        if deal.id not in self.deal_dates:
            supports = [support for support in supports
                        if support.source.id in self.source_published]
        return [support.source for support in supports]

    def _check_k3(self, row: Row) -> bool:
        if any(self._deal_evidence(deal) for deal in self.deals_by_investor.get(row.id, [])):
            return True
        self._error(row, "", "K3_NOT_MET",
                    "Chybí investice doložená nezávislým zdrojem (tier 1 nebo 2) s datem (plan.md, K3). "
                    "Nepočítá se instrument=unclear, samotný zápis společníka v rejstříku ani "
                    "investment_unspecified bez výslovné zmínky o investici.")
        return False

    def _check_unused_sources(self) -> None:
        for source_id, row in self.by_id["sources"].items():
            if source_id not in self.used_sources:
                self._warn(row, "", "UNUSED_SOURCE", "Zdroj není použitý v žádné citaci.")

    # --- odvozené hodnoty ---

    def _summaries(self) -> list[InvestorSummary]:
        cutoff = months_before(self.today, ACTIVE_WINDOW_MONTHS)
        summaries = []
        for row in self.rows["investors"]:
            status = row["record_status"]
            if status == "rejected":
                summaries.append(InvestorSummary(row.id, status, row["primary_type"], None, None,
                                                 "", "", ""))
                continue
            evidenced = [deal for deal in self.deals_by_investor.get(row.id, [])
                         if self._deal_evidence(deal)]
            dated = [deal for deal in evidenced if deal.id in self.deal_dates]
            last_deal = max(dated, key=lambda deal: (self.deal_dates[deal.id].earliest,
                                                     PRECISION_RANK[self.deal_dates[deal.id].precision]),
                            default=None)
            last = self.deal_dates[last_deal.id] if last_deal else None
            newest_first = sorted(evidenced, reverse=True, key=lambda deal: (
                (self.deal_dates[deal.id].earliest, PRECISION_RANK[self.deal_dates[deal.id].precision])
                if deal.id in self.deal_dates else (date.min, -1)))
            activity = "active" if last and last.earliest >= cutoff else "inactive"
            sources = {source.id for deal in evidenced for source in self._deal_evidence(deal)}
            if status == "included" and self.inclusion_ok.get(row.id):
                grade = "A" if len(sources) >= 2 else "B"
            else:
                grade = "C"
            k2 = bool(self._sources_for("investor", row.id, "decision_authority"))
            summaries.append(InvestorSummary(row.id, status, row["primary_type"], k2, len(evidenced),
                                             last.raw if last else "", activity, grade,
                                             last_deal.id if last_deal else "",
                                             tuple(deal.id for deal in newest_first)))
        return summaries


def validate(data_dir: Path, today: date) -> Report:
    return Validator(data_dir, today).run()


def print_report(report: Report) -> None:
    print(f"Validace dat: {report.data_dir}")
    print(f"Datum vyhodnocení: {report.today.isoformat()}")
    print("Načteno: " + ", ".join(f"{name} {count}" for name, count in report.counts.items()))
    for title, issues in (("Chyby", report.errors), ("Varování", report.warnings)):
        print(f"\n{title}: {len(issues)}")
        for issue in issues:
            print("  " + issue.format())
    print("\nPřehled investorů (odvozené hodnoty, do CSV se neukládají):")
    header = ("investor_id", "record_status", "primary_type", "K2", "doložené inv.",
              "poslední inv.", "aktivita", "hodnocení")
    rows = [header] + [
        (s.investor_id, s.record_status, s.primary_type or "–",
         "–" if s.k2_verified is None else "ověřeno" if s.k2_verified else "neověřeno",
         "–" if s.documented_deals is None else str(s.documented_deals),
         s.last_investment_date or "–", s.activity_status or "–", s.confidence_grade or "–")
        for s in report.investors
    ]
    widths = [max(len(row[i]) for row in rows) for i in range(len(header))]
    for row in rows:
        print("  " + "  ".join(value.ljust(width) for value, width in zip(row, widths)).rstrip())
    errors = len(report.errors)
    error_word = "chyba" if errors == 1 else "chyby" if 2 <= errors <= 4 else "chyb"
    verdict = "CHYBY NALEZENY" if errors else "OK"
    print(f"\nVýsledek: {verdict} ({errors} {error_word}, {len(report.warnings)} varování)")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validace CSV dat databáze investorů.")
    parser.add_argument("data_dir", type=Path, help="adresář s CSV soubory")
    parser.add_argument("--today", type=date.fromisoformat, default=date.today(),
                        help="datum, ke kterému se počítá aktivita (výchozí: dnes)")
    args = parser.parse_args(argv)
    if not args.data_dir.is_dir():
        print(f"Adresář {args.data_dir} neexistuje.", file=sys.stderr)
        return 2
    report = validate(args.data_dir, args.today)
    print_report(report)
    return 1 if report.errors else 0


if __name__ == "__main__":
    sys.exit(main())
