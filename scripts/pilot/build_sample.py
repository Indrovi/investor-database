#!/usr/bin/env python3
"""Sestaví data pilotu (data/sample/*.csv) z rozhodnutí koordinátora v decisions.py.

Citace, URL a údaje o zdrojích se berou strojově z výstupů agentů (agentdata.py),
takže se při zápisu nezmění žádný znak. Výjimkou jsou dvě citace koordinátora z auditu
(KOORD_CLAIMS v decisions.py), jejichž doslovnost ověřuje verify_quotes.py. Tier zdroje určuje koordinátor (TIER v decisions.py).
candidates.csv vzniká ze snímku candidates_vyber.csv (build_candidates.py) s opravami párování
(SPLITS) a s výsledky ověření (CANDIDATES).

Použití: python3 scripts/pilot/build_sample.py
"""
import csv, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import agentdata  # noqa: E402
import decisions as D  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data/sample"
sys.path.insert(0, str(ROOT / "scripts"))
import validate  # noqa: E402

claims_cache, meta_cache = {}, {}


def resolve(ref):
    cid, rest = ref.split(":", 1)
    if cid == "KOORD":  # citace převzatá koordinátorem přímo ze stránky (decisions.KOORD_CLAIMS)
        meta_cache.setdefault(cid, {})
        return cid, D.KOORD_CLAIMS[rest]
    if cid not in claims_cache:
        claims_cache[cid] = agentdata.claims(cid)
        meta_cache[cid] = agentdata.source_meta(cid)
    row = claims_cache[cid].get(rest)
    if row is None:
        raise KeyError(f"tvrzení {ref} ve výstupu agenta není")
    return cid, row


def main():
    sources, source_rows, citations = {}, [], []
    for entity_type, items, id_key in (("investor", D.INVESTORS, "investor_id"),
                                       ("fund", D.FUNDS, "fund_id"),
                                       ("investment", D.DEALS, "deal_id")):
        for item in items:
            for ref, fields, note in item.get("cites", []):
                cid, row = resolve(ref)
                url = row["_url"]
                if url not in sources:
                    meta = meta_cache[cid].get(url, {})
                    override = D.SOURCE_OVERRIDES.get(url, {})
                    sid = f"SRC-{len(sources) + 1:04d}"
                    sources[url] = sid
                    source_rows.append({
                        "source_id": sid, "url": url,
                        "publisher": override.get("publisher") or meta.get("publisher", ""),
                        "title": override.get("title", meta.get("title", "")),
                        "tier": D.TIER[url],
                        "published_date": override.get("published_date", meta.get("published_date", "")),
                        "accessed_date": override.get("accessed_date", meta.get("accessed_date", "2026-10-16")),
                        "archive_url": ""})
                citations.append({
                    "citation_id": f"CIT-{len(citations) + 1:04d}", "entity_type": entity_type,
                    "entity_id": item[id_key], "fields": fields, "source_id": sources[url],
                    "quote": row["_quote"], "note": note})
    tables = {"sources": source_rows, "citations": citations,
              "investors": D.INVESTORS, "funds": D.FUNDS, "investments": D.DEALS}
    for name, rows in tables.items():
        spec = validate.TABLES[name]
        with (OUT / spec.file_name).open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=spec.columns, lineterminator="\n",
                                    extrasaction="ignore")
            writer.writeheader()
            for row in rows:
                writer.writerow({c: row.get(c, "") for c in spec.columns})
    # candidates.csv: doplnit investor_id a poznámky podle rozhodnutí
    with (OUT / "candidates_vyber.csv").open(encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    path = OUT / "candidates.csv"
    for row in rows:
        split = D.SPLITS.get((row["candidate_id"], row["name"]))
        if split:
            row["candidate_id"], row["note"] = split
    for row in rows:
        update = D.CANDIDATES.get(row["candidate_id"])
        if update:
            row["investor_id"] = update["investor_id"]
            if "note" in update:
                row["note"] = update["note"]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=validate.TABLES["candidates"].columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(f"zdroje {len(source_rows)}, citace {len(citations)}, investoři {len(D.INVESTORS)}, "
          f"fondy {len(D.FUNDS)}, investice {len(D.DEALS)}")


if __name__ == "__main__":
    main()
