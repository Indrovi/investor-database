#!/usr/bin/env python3
"""Kontrola doslovnosti citací (nástroj koordinátora, docs/agenti.md).

Stáhne každou citovanou stránku a ověří, že citace je v jejím textu doslova. Porovnává
text bez HTML značek a sjednocuje jen:
- bílé znaky,
- typografické uvozovky a pomlčky,
- mezeru před interpunkcí, která vzniká spojením HTML prvků (např. odkaz a za ním čárka).

Jiné rozdíly (čárky, mezery v číslech, velikost písmen) jsou neshoda.

Každý záznam musí mít ID, úplnou URL (http/https) a citaci. Neúplný záznam se nepřeskočí,
ale odmítne (NEÚPLNÝ) a kontrola skončí chybou.

Použití:
    python3 scripts/check_quotes.py --markdown VYSTUP_AGENTA.md
        Tabulky ve výstupu agenta se sloupcem „doslovná citace“ (nebo „citace“): každý řádek
        musí mít vlastní úplnou URL ve sloupci „url“.
    python3 scripts/check_quotes.py --data DATA_DIR
        citations.csv a sources.csv podle docs/datovy-model.md.

Stahuje se přímo. Když stránka vrátí chybu nebo ochranu proti robotům, zkusí se Firecrawl
(scripts/firecrawl_mcp.py, s klíčem z .env, pokud je vyplněný). Klíč se nikdy nevypisuje.
Přepínač --no-firecrawl zálohu vypne.

Návratový kód je 1, pokud některý záznam není úplný, citace není ve zdroji doslova nebo
zdroj nejde stáhnout. Používá jen standardní knihovnu Pythonu.
"""

from __future__ import annotations

import argparse
import csv
import difflib
import html
import json
import re
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import Callable
from urllib.parse import urlparse

import firecrawl_mcp

USER_AGENT = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
              "Chrome/124.0 Safari/537.36")
BLOCKED_STATUSES = {401, 403, 429, 503}
BLOCKED_MARKERS = ("Just a moment...", "Vercel Security Checkpoint", "Attention Required!",
                   "cf-browser-verification", "challenge-platform")
QUOTE_COLUMNS = ("doslovná citace", "citace", "quote")
ID_COLUMNS = ("claim", "id", "citation_id")
EMPTY_VALUES = {"", "-", "–", "—"}
TIMEOUT = 60
# Přímo stažený text kratší než tento počet znaků je nejspíš jen kostra stránky
# vykreslované skriptem (JavaScript); pak se stránka načte přes Firecrawl.
MIN_DIRECT_TEXT = 200
TEXT_TYPES = ("html", "json", "text/plain", "xml")
# Tarif Free u Firecrawlu povoluje zhruba 10 požadavků za minutu.
FIRECRAWL_MIN_INTERVAL = 6.5
_last_firecrawl_call = 0.0


@dataclass(frozen=True)
class Claim:
    claim_id: str
    url: str
    quote: str

    def problems(self) -> list[str]:
        """Proč je záznam neúplný (prázdný seznam = úplný)."""
        issues = []
        if self.claim_id in EMPTY_VALUES:
            issues.append("chybí ID")
        if not is_full_url(self.url):
            issues.append(f"chybí úplná URL (je tam „{self.url}“)")
        if self.quote in EMPTY_VALUES:
            issues.append("chybí citace")
        return issues


@dataclass(frozen=True)
class Page:
    status: int | None
    text: str
    method: str  # "přímo" nebo "firecrawl"
    error: str = ""


def is_full_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in ("http", "https") and bool(parsed.netloc) and " " not in value


# --- Text a porovnání ---

class _TextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript", "template"):
            self.skip += 1

    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript", "template") and self.skip:
            self.skip -= 1

    def handle_data(self, data):
        if not self.skip:
            self.parts.append(data)


def normalize(text: str) -> str:
    text = html.unescape(text)
    for old, new in ((" ", " "), (" ", " "), ("“", '"'), ("”", '"'), ("„", '"'),
                     ("’", "'"), ("‘", "'"), ("–", "-"), ("—", "-")):
        text = text.replace(old, new)
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r" ([,.;:!?)])", r"\1", text)
    return text.replace("( ", "(").strip()


def html_to_text(raw: str) -> str:
    parser = _TextParser()
    parser.feed(raw)
    return normalize(" ".join(parser.parts))


def markdown_to_text(markdown: str) -> str:
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", markdown)       # obrázky
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)         # odkazy -> jejich text
    text = re.sub(r"(\*\*|__|\*|`)", "", text)                   # zvýraznění
    text = re.sub(r"^\s{0,3}(#+|>|[-*+])\s+", "", text, flags=re.M)
    return normalize(text.replace("\\", ""))


def find_quote(page_text: str, quote: str) -> tuple[bool, float, str]:
    """Vrátí (nalezeno doslova, podobnost nejbližšího úseku, nejbližší úsek)."""
    wanted = normalize(quote)
    if wanted and wanted in page_text:
        return True, 1.0, wanted
    matcher = difflib.SequenceMatcher(None, page_text, wanted, autojunk=False)
    match = matcher.find_longest_match(0, len(page_text), 0, len(wanted))
    start = max(0, match.a - match.b)
    window = page_text[start:start + len(wanted)]
    return False, difflib.SequenceMatcher(None, window, wanted).ratio(), window


# --- Vstupy ---

def _cells(line: str) -> list[str]:
    """Buňky řádku markdownové tabulky. Escapovaná svislá čára („\\|“) je text buňky."""
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|") and not line.endswith("\\|"):
        line = line[:-1]
    return [cell.replace("\\|", "|").strip() for cell in re.split(r"(?<!\\)\|", line)]


def _clean(value: str) -> str:
    value = value.strip()
    while len(value) >= 2 and value[0] == value[-1] and value[0] in "\"`'":
        value = value[1:-1].strip()
    return value


def markdown_tables(text: str) -> list[list[dict[str, str]]]:
    tables, current = [], []
    for line in text.splitlines() + [""]:
        if line.strip().startswith("|"):
            current.append(line)
            continue
        if len(current) >= 2 and set(current[1].replace("|", "").strip()) <= set("-: "):
            header = [cell.lower() for cell in _cells(current[0])]
            tables.append([dict(zip(header, _cells(row))) for row in current[2:]])
        current = []
    return tables


def claim_from_row(row: dict[str, str]) -> Claim | None:
    """Záznam z řádku tabulky se sloupcem citace (None, pokud tabulka citace nemá)."""
    quote_column = next((c for c in QUOTE_COLUMNS if c in row), None)
    if quote_column is None:
        return None
    claim_id = next((row[c] for c in row if c.split(" ")[0] in ID_COLUMNS and row[c]), "")
    return Claim(claim_id, _clean(row.get("url", "")), _clean(row[quote_column]))


def claims_from_markdown(text: str) -> list[Claim]:
    """Všechny řádky tabulek se sloupcem citace, včetně neúplných (ty kontrola odmítne)."""
    return [claim for table in markdown_tables(text) for row in table
            if (claim := claim_from_row(row)) is not None]


def claims_from_data(data_dir: Path) -> list[Claim]:
    with (data_dir / "sources.csv").open(encoding="utf-8-sig", newline="") as handle:
        urls = {row["source_id"]: row["url"] for row in csv.DictReader(handle)}
    with (data_dir / "citations.csv").open(encoding="utf-8-sig", newline="") as handle:
        return [Claim(row["citation_id"], urls.get(row["source_id"], ""), row.get("quote", ""))
                for row in csv.DictReader(handle)]


# --- Stažení ---

def looks_blocked(status: int | None, text: str) -> bool:
    return status in BLOCKED_STATUSES or any(marker in text[:5000] for marker in BLOCKED_MARKERS)


def fetch_direct(url: str) -> Page:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
            status, body = response.status, response.read()
            content_type = response.headers.get("Content-Type", "")
            charset = response.headers.get_content_charset() or "utf-8"
    except urllib.error.HTTPError as err:
        return Page(err.code, err.read().decode("utf-8", "replace"), "přímo", f"HTTP {err.code}")
    except (urllib.error.URLError, TimeoutError, OSError) as err:
        return Page(None, "", "přímo", str(getattr(err, "reason", err)))
    if content_type and not any(kind in content_type for kind in TEXT_TYPES):
        # PDF, XLSX a podobné soubory text přímo nedají, přečte je Firecrawl.
        return Page(status, "", "přímo", f"formát {content_type.split(';')[0]}")
    raw = body.decode(charset, "replace")
    text = normalize(raw) if "json" in content_type else html_to_text(raw)
    return Page(status, text, "přímo")


def fetch_firecrawl(url: str) -> Page:
    """Jedno volání firecrawl_scrape se schválenými parametry (firecrawl_mcp.SCRAPE_ARGUMENTS)."""
    global _last_firecrawl_call
    wait = FIRECRAWL_MIN_INTERVAL - (time.monotonic() - _last_firecrawl_call)
    if wait > 0:
        time.sleep(wait)
    _last_firecrawl_call = time.monotonic()
    try:
        text = firecrawl_mcp.scrape(url)
    except (urllib.error.URLError, OSError, KeyError, IndexError, ValueError) as err:
        return Page(None, "", "firecrawl", f"Firecrawl nedostupný: {type(err).__name__}")
    try:
        document = json.loads(text)
    except ValueError:
        # Chyby (např. vyčerpaný limit bez klíče) vrací Firecrawl jako prostý text.
        return Page(None, "", "firecrawl", "Firecrawl: " + " ".join(text.split())[:120])
    if document.get("success") is False:
        return Page(None, "", "firecrawl", str(document.get("code") or document.get("error"))[:120])
    document = document.get("data", document)
    status = document.get("metadata", {}).get("statusCode")
    return Page(status, markdown_to_text(document.get("markdown") or ""), "firecrawl")


def direct_is_usable(page: Page) -> bool:
    """Přímo stažená stránka má čitelný text (ne blokaci, PDF ani kostru stránky ze skriptu)."""
    return page.status == 200 and not looks_blocked(page.status, page.text) and len(page.text) >= MIN_DIRECT_TEXT


def fetch(url: str, use_firecrawl: bool = True, log: Callable[[str], None] = print) -> Page:
    page = fetch_direct(url)
    if not use_firecrawl or direct_is_usable(page):
        return page
    fallback = fetch_firecrawl(url)
    log(f"  firecrawl_scrape {url} -> statusCode {fallback.status} {fallback.error}".rstrip())
    return fallback if fallback.status == 200 else page


# --- Vyhodnocení ---

def check_claims(claims: list[Claim], fetcher: Callable[[str], Page],
                 log: Callable[[str], None] = print,
                 rerender: Callable[[str], Page] | None = None) -> int:
    """Ověří záznamy. Když citace v přímo stažené stránce není, zkusí `rerender`
    (stránka vykreslená Firecrawlem, např. obsah načítaný skriptem)."""
    pages: dict[str, Page] = {}
    rendered: dict[str, Page] = {}
    problems = 0
    for claim in claims:
        label = claim.claim_id or "?"
        incomplete = claim.problems()
        if incomplete:
            problems += 1
            log(f"{label:6} NEÚPLNÝ     záznam odmítnut: {'; '.join(incomplete)}")
            continue
        if claim.url not in pages:
            pages[claim.url] = fetcher(claim.url)
        page = pages[claim.url]
        where = f"{page.method}, HTTP {page.status}"
        if page.status != 200 or looks_blocked(page.status, page.text):
            problems += 1
            log(f"{label:6} NESTAŽENO   ({where}) {page.error} {claim.url}")
            continue
        found, ratio, window = find_quote(page.text, claim.quote)
        if not found and rerender is not None and page.method == "přímo":
            if claim.url not in rendered:
                rendered[claim.url] = rerender(claim.url)
                log(f"  firecrawl_scrape {claim.url} -> statusCode {rendered[claim.url].status} "
                    f"{rendered[claim.url].error}".rstrip())
            second = rendered[claim.url]
            if second.status == 200:
                found2, ratio2, window2 = find_quote(second.text, claim.quote)
                if found2 or ratio2 > ratio:
                    page, found, ratio, window = second, found2, ratio2, window2
                    where = f"{page.method}, HTTP {page.status}"
        if found:
            log(f"{label:6} DOSLOVNĚ    ({where}) {claim.quote[:70]}")
        else:
            problems += 1
            log(f"{label:6} NEDOSLOVNĚ  ({where}, podobnost {ratio:.2f}) {claim.quote[:70]}")
            log(f"       na stránce: {window[:160]}")
    log(f"\nZáznamů: {len(claims)}, doslovně: {len(claims) - problems}, problém: {problems}")
    return 1 if problems else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Kontrola doslovnosti citací.")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--markdown", type=Path, help="výstup agenta (markdown s tabulkami)")
    source.add_argument("--data", type=Path, help="adresář s citations.csv a sources.csv")
    parser.add_argument("--no-firecrawl", action="store_true", help="nepoužívat Firecrawl jako zálohu")
    args = parser.parse_args(argv)
    if args.markdown:
        claims = claims_from_markdown(args.markdown.read_text(encoding="utf-8"))
    else:
        claims = claims_from_data(args.data)
    if not claims:
        print("Nenalezen žádný záznam s citací.", file=sys.stderr)
        return 2
    use_firecrawl = not args.no_firecrawl
    return check_claims(claims, lambda url: fetch(url, use_firecrawl),
                        rerender=fetch_firecrawl if use_firecrawl else None)


if __name__ == "__main__":
    sys.exit(main())
