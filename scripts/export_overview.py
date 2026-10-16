#!/usr/bin/env python3
"""Přehled zařazených investorů pro čtení (generuje se z dat, ručně se neupravuje).

Jeden řádek = jeden zařazený investor (record_status=included). Vyřazené záznamy, včetně
sloučených E10, a kandidáti se nevypisují. Kódy jsou převedené na čitelný text a chybějící údaje
mají uvedený důvod. Nic se nedopočítává: aktivitu, poslední doloženou investici, počet doložených
investic a hodnocení přebírá přehled z validátoru (scripts/validate.py).

Každá skupina údajů má sloupec se zdroji ve tvaru „URL (CIT-0000)“. Doslovnou citaci k ID
najdete v citations.csv. Ticket je vždy deklarovaná hodnota ze zdroje (případně pro strategii
v ticket_scope), ne investovaná částka; vypisují se jen investice, které splňují K3.

Použití:
    python3 scripts/export_overview.py DATA_DIR [--today YYYY-MM-DD] [--out SOUBOR]

Výchozí výstup je DATA_DIR/investori_prehled.csv. Pokud validace najde chybu, přehled se
nevytvoří (návratový kód 1). Používá jen standardní knihovnu Pythonu.
"""

from __future__ import annotations

import argparse
import csv
import sys
from datetime import date
from decimal import Decimal
from pathlib import Path

import validate

OUTPUT_NAME = "investori_prehled.csv"

TYPES = {"vc": "venture capital (VC)", "pe": "private equity (PE)", "family_office": "family office",
         "business_angel": "business angel", "large_private_investor": "velký soukromý investor"}
SUBTYPES = {"corporate": "korporátní (CVC)", "accelerator": "akcelerátor", "public": "veřejný (státní)",
            "institutional": "institucionální", "angel_fund": "angel fond", "multi_family": "multi-family office"}
SECTORS = {
    "software_saas": "software a SaaS", "ai_data": "AI a data", "fintech": "fintech",
    "health_life_sciences": "zdraví a life sciences", "cleantech_energy": "cleantech a energetika",
    "mobility_transport": "mobilita a doprava", "ecommerce_retail": "e-commerce a retail",
    "consumer": "spotřebitelské produkty a služby", "edtech": "edtech",
    "proptech_construction": "proptech a stavebnictví", "agrifood": "zemědělství a potraviny",
    "industrial_manufacturing": "průmysl a výroba", "deeptech_hardware": "deeptech a hardware",
    "cybersecurity": "kybernetická bezpečnost", "media_gaming": "média a hry", "logistics": "logistika",
    "business_services": "služby pro firmy", "generalist": "bez oborového zaměření",
}
STAGES = {"pre_seed": "pre-seed", "seed": "seed", "series_a": "Series A", "series_b": "Series B",
          "series_c_plus": "Series C+", "growth": "growth", "buyout": "buyout"}
REGIONS = {"CEE": "střední a východní Evropa", "DACH": "DACH", "NORDICS": "severské země",
           "EUROPE": "Evropa", "GLOBAL": "celosvětově"}
COUNTRY_NAMES = {
    "CZ": "Česko", "SK": "Slovensko", "PL": "Polsko", "HU": "Maďarsko", "AT": "Rakousko", "DE": "Německo",
    "CH": "Švýcarsko", "LU": "Lucembursko", "NL": "Nizozemsko", "FR": "Francie", "GB": "Spojené království",
    "IE": "Irsko", "EE": "Estonsko", "LV": "Lotyšsko", "LT": "Litva", "BG": "Bulharsko", "RO": "Rumunsko",
    "UA": "Ukrajina", "US": "USA",
}
MISSING = {"not_public": "nezveřejněno", "conflicting": "zdroje si odporují",
           "not_applicable": "nevztahuje se", "ambiguous": "nejasné (zdroj neuvádí jednoznačnou hodnotu)",
           "": "neuvedeno"}
VALUE_NOTE = {"reported": "", "derived": " (odvozeno)", "estimate": " (odhad)"}
SIZE_TYPES = {"target": "cílová velikost", "first_close": "první uzavření", "final_close": "konečná velikost"}
AUM_BASES = {"aum": "AUM", "regulatory_aum": "regulatorní AUM"}
ACTIVITY = {"active": "aktivní (doložená investice za posledních 24 měsíců)",
            "inactive": "neaktivní (bez doložené investice za posledních 24 měsíců)"}
GRADES = {"A": "A (nejméně 2 nezávislé důkazy investic)", "B": "B (1 nezávislý důkaz investice)"}

COLUMNS = (
    "Název", "Typ", "Podtyp", "Město", "Země", "Web", "Sektory", "Fáze", "Investiční geografie",
    "Typická investice (ticket)", "Fondy a jejich velikost", "AUM (celkový spravovaný kapitál)",
    "Aktivita", "Poslední doložená investice", "Doložené investice (firmy)", "Počet doložených investic",
    "Hodnocení spolehlivosti", "ID v databázi", "Zdroje: identita, sídlo a typ",
    "Zdroje: rozhodovací pravomoc (K2)", "Zdroje: zaměření a ticket", "Zdroje: fondy a AUM",
    "Zdroje: doložené investice",
)
MAX_LISTED_DEALS = 8
SOURCE_GROUPS = {
    "Zdroje: identita, sídlo a typ": ("identity", "country", "city", "primary_type"),
    "Zdroje: rozhodovací pravomoc (K2)": ("decision_authority",),
    "Zdroje: zaměření a ticket": ("sectors", "stages", "geographies", "ticket"),
}


def read(data_dir: Path, table: str) -> list[dict[str, str]]:
    with (data_dir / validate.TABLES[table].file_name).open(encoding="utf-8-sig", newline="") as handle:
        return [{key: (value or "").strip() for key, value in row.items()} for row in csv.DictReader(handle)]


def money(amount: str, currency: str) -> str:
    value = Decimal(amount)
    text = f"{value:,.2f}".rstrip("0").rstrip(".") if value % 1 else f"{int(value):,}"
    return f"{text.replace(',', ' ')} {currency}"


def listed(codes: str, names: dict[str, str]) -> str:
    return ", ".join(names.get(code, code) for code in validate.split_list(codes))


def with_status(text: str, status: str) -> str:
    return text + VALUE_NOTE.get(status, "") if text else MISSING.get(status, MISSING[""])


def ticket(row: dict[str, str]) -> str:
    """Deklarovaná typická investice ze zdroje, ne konkrétní investovaná částka ani limit programu."""
    low, high, currency = row["ticket_min"], row["ticket_max"], row["ticket_currency"]
    if low and high and low == high:
        text, label = money(low, currency), "deklarovaná výše"
    elif low and high:
        text, label = f"{money(low, currency).rsplit(' ', 1)[0]}–{money(high, currency)}", "deklarované rozpětí"
    elif low or high:
        text = f"od {money(low, currency)}" if low else f"do {money(high, currency)}"
        label = "deklarované rozpětí"
    else:
        return MISSING.get(row["ticket_status"], MISSING[""])
    if row["ticket_status"] != "reported":
        return with_status(text, row["ticket_status"])
    scope = f" pro {row['ticket_scope']}" if row["ticket_scope"] else ""
    return f"{text} ({label}{scope})"


def deal_text(deal: dict[str, str]) -> str:
    details = [deal["investment_date"] or "datum neuvedeno"]
    if deal["round_stage"] in STAGES:
        details.append(STAGES[deal["round_stage"]])
    return f"{deal['company_name']} ({', '.join(details)})"


def deals_text(documented: list[dict[str, str]]) -> str:
    if not documented:
        return "žádná nezávisle doložená investice"
    shown = "; ".join(deal_text(deal) for deal in documented[:MAX_LISTED_DEALS])
    rest = len(documented) - MAX_LISTED_DEALS
    return shown + (f"; a další ({rest})" if rest > 0 else "")


def fund_text(fund: dict[str, str]) -> str:
    if fund["size_amount"]:
        size = (f"{money(fund['size_amount'], fund['size_currency'])} "
                f"({SIZE_TYPES.get(fund['size_type'], fund['size_type'])}, k {fund['size_as_of']})")
    else:
        size = "velikost: " + MISSING.get(fund["size_status"], MISSING[""])
    return f"{fund['name']} – {size}"


def aum(row: dict[str, str]) -> str:
    if not row["aum_amount"]:
        return MISSING.get(row["aum_status"], MISSING[""])
    basis = AUM_BASES.get(row["aum_basis"], row["aum_basis"])
    return f"{money(row['aum_amount'], row['aum_currency'])} ({basis} k {row['aum_as_of']})" + \
        VALUE_NOTE.get(row["aum_status"], "")


def sources(citations: list[dict[str, str]], urls: dict[str, str], entity_type: str, entity_ids: set[str],
            fields: tuple[str, ...]) -> str:
    found = []
    for citation in citations:
        if citation["entity_type"] != entity_type or citation["entity_id"] not in entity_ids:
            continue
        if set(validate.split_list(citation["fields"])) & set(fields):
            entry = f"{urls.get(citation['source_id'], '?')} ({citation['citation_id']})"
            if entry not in found:
                found.append(entry)
    return " | ".join(found) if found else "–"


def build_rows(data_dir: Path, today: date) -> tuple[list[dict[str, str]], list[str]]:
    """Řádky přehledu a chyby validace (při chybách se přehled nevytváří)."""
    report = validate.validate(data_dir, today)
    if report.errors:
        return [], [issue.format() for issue in report.errors]
    summaries = {summary.investor_id: summary for summary in report.investors}
    investors = read(data_dir, "investors")
    funds = read(data_dir, "funds")
    deals = {deal["deal_id"]: deal for deal in read(data_dir, "investments")}
    citations = read(data_dir, "citations")
    urls = {source["source_id"]: source["url"] for source in read(data_dir, "sources")}
    rows = []
    for investor in investors:
        if investor["record_status"] != "included":
            continue
        iid, summary = investor["investor_id"], summaries[investor["investor_id"]]
        own_funds = [fund for fund in funds if fund["investor_id"] == iid]
        last = deals.get(summary.last_deal_id)
        documented = [deals[deal_id] for deal_id in summary.documented_deal_ids]
        row = {
            "Název": investor["name"],
            "Typ": TYPES.get(investor["primary_type"], investor["primary_type"]),
            "Podtyp": SUBTYPES.get(investor["subtype"], investor["subtype"]) or "–",
            "Město": investor["city"] or MISSING[""],
            "Země": COUNTRY_NAMES.get(investor["country"], investor["country"]),
            "Web": investor["website"] or MISSING[""],
            "Sektory": with_status(listed(investor["sectors"], SECTORS), investor["sectors_status"]),
            "Fáze": with_status(listed(investor["stages"], STAGES), investor["stages_status"]),
            "Investiční geografie": with_status(
                listed(investor["geographies"], {**COUNTRY_NAMES, **REGIONS}), investor["geographies_status"]),
            "Typická investice (ticket)": ticket(investor),
            "Fondy a jejich velikost": "; ".join(fund_text(fund) for fund in own_funds) or MISSING[""],
            "AUM (celkový spravovaný kapitál)": aum(investor),
            "Aktivita": ACTIVITY.get(summary.activity_status, summary.activity_status),
            "Poslední doložená investice": (f"{last['company_name']} ({summary.last_investment_date})"
                                            if last else "žádná datovaná nezávisle doložená investice"),
            "Doložené investice (firmy)": deals_text(documented),
            "Počet doložených investic": str(summary.documented_deals),
            "Hodnocení spolehlivosti": GRADES.get(summary.confidence_grade, summary.confidence_grade),
            "ID v databázi": iid,
        }
        for column, fields in SOURCE_GROUPS.items():
            row[column] = sources(citations, urls, "investor", {iid}, fields)
        fund_sources = sources(citations, urls, "fund", {fund["fund_id"] for fund in own_funds}, ("fund", "size"))
        aum_sources = sources(citations, urls, "investor", {iid}, ("aum",))
        row["Zdroje: fondy a AUM"] = " | ".join(part for part in (fund_sources, aum_sources) if part != "–") or "–"
        row["Zdroje: doložené investice"] = sources(
            citations, urls, "investment", {deal["deal_id"] for deal in documented[:MAX_LISTED_DEALS]},
            ("deal", "investment_date"))
        rows.append(row)
    return rows, []


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Přehled zařazených investorů pro čtení.")
    parser.add_argument("data_dir", type=Path)
    parser.add_argument("--today", type=date.fromisoformat, default=date.today(),
                        help="datum, ke kterému se počítá aktivita (výchozí: dnes)")
    parser.add_argument("--out", type=Path, help=f"výstupní soubor (výchozí: DATA_DIR/{OUTPUT_NAME})")
    args = parser.parse_args(argv)
    rows, errors = build_rows(args.data_dir, args.today)
    if errors:
        print("Přehled se nevytvořil, data obsahují chyby (scripts/validate.py):", file=sys.stderr)
        for error in errors:
            print("  " + error, file=sys.stderr)
        return 1
    out = args.out or args.data_dir / OUTPUT_NAME
    with out.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(f"Přehled: {out} ({len(rows)} zařazených investorů, aktivita k {args.today.isoformat()})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
