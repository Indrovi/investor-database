#!/usr/bin/env python3
"""Kontrola doslovnosti s funkcemi scripts/check_quotes.py, šetrná ke kreditům Firecrawlu.

1. přímé stažení stránky (zdarma),
2. když stránka přímo nejde nebo citaci neobsahuje: uložená kopie výstupu Firecrawlu
   z .cache/pages (stejný text, jaký dostal agent; pages.py),
3. Firecrawl jen s přepínačem --firecrawl.

Použití:
    python3 scripts/pilot/verify_quotes.py --markdown VÝSTUP_AGENTA.md
    python3 scripts/pilot/verify_quotes.py --data data/sample [--firecrawl] [--only CIT-0001,CIT-0002]
"""
import argparse
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import check_quotes as cq  # noqa: E402


def stored_index():
    index = {}
    path = ROOT / ".cache/pages/index.tsv"
    if path.exists():
        with path.open(encoding="utf-8") as handle:
            for row in csv.DictReader(handle, delimiter="\t"):
                index[row["url"]] = row
    return index


def main():
    parser = argparse.ArgumentParser(description="Kontrola doslovnosti citací (přímo, uložená kopie, Firecrawl).")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--markdown", type=Path)
    group.add_argument("--data", type=Path)
    parser.add_argument("--firecrawl", action="store_true", help="povolit Firecrawl (stojí kredity)")
    parser.add_argument("--only", default="", help="jen vybraná ID oddělená čárkou")
    args = parser.parse_args()
    claims = (cq.claims_from_markdown(args.markdown.read_text(encoding="utf-8")) if args.markdown
              else cq.claims_from_data(args.data))
    if args.only:
        wanted = set(args.only.split(","))
        claims = [claim for claim in claims if claim.claim_id in wanted]
    index = stored_index()

    def stored(url):
        row = index.get(url) or index.get(url.rstrip("/")) or index.get(url + "/")
        if not row:
            return None
        text = (ROOT / row["soubor"]).read_text(encoding="utf-8")
        return cq.Page(200, cq.markdown_to_text(text), f"uložená kopie {row['stazeno']}")

    def fetcher(url):
        page = cq.fetch_direct(url)
        if cq.direct_is_usable(page):
            return page
        copy = stored(url)
        if copy:
            return copy
        return cq.fetch_firecrawl(url) if args.firecrawl else page

    def rerender(url):
        copy = stored(url)
        if copy:
            return copy
        return cq.fetch_firecrawl(url) if args.firecrawl else cq.Page(None, "", "bez kopie")

    return cq.check_claims(claims, fetcher, rerender=rerender)


if __name__ == "__main__":
    sys.exit(main())
