#!/usr/bin/env python3
"""Seznam kandidátů z ověřeného výstupu průzkumníka (hledání kandidátů) podle data/sample/README.md.

Zapíše dva snímky pro výběr vzorku (scripts/select_sample.py):
- data/sample/candidates_vyber.csv: seznam v okamžiku původního výběru (párování, triáž),
- data/sample/candidates_vyber_oprava.csv: týž seznam s opravenou duplicitou CAN-0028 → CAN-0025.

data/sample/candidates.csv (s výsledky ověření) z nich sestaví build_sample.py.

Použití: python3 scripts/pilot/build_candidates.py
"""
import csv, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import check_quotes as cq  # noqa: E402

RUN = ROOT / ".cache/agents/pilot/hledani/investor-source-scout.md"
FOUND_DATE = "2026-10-16"
SOURCES = {"1": ("ZDR-09", "list"), "2": ("ZDR-10", "list"), "3": ("ZDR-12", "list"),
           "4": ("ZDR-13", "deal_report"), "5": ("ZDR-17", "list")}
# Párování: stejná značka (název nebo web) = stejný kandidát. Klíč = značka.
BRAND = {
    "Credo Ventures a.s.": "Credo", "Credo Ventures": "Credo",
    "Depo Ventures": "DEPO", "DEPO Ventures": "DEPO",
    "ARX Equity Partners": "ARX", "ARX Equity Partners B.V.": "ARX",
    "EVERITA Capital": "EVERITA", "EVERITA Capital sro": "EVERITA",
    "KAYA VC": "KAYA", "KAYA Advisory s.r.o.": "KAYA", "Kaya VC": "KAYA",
    "Orbit Capital": "Orbit", "OGD Advisory s.r.o.": "Orbit",  # EIF: web fondu orbitcapital.com
    "Tensor Ventures": "Tensor", "Tensor Advisory s.r.o.": "Tensor",
    "Národní rozvojová investiční": "NRI", "NRI": "NRI",
    "Rockaway Ventures": "Rockaway", "Rockaway Capital Partners": "Rockaway",
}
NOTES = {
    "Tensor": "EIF u fondu Tensor Co-Investment Fund SCSp uvádí web kaya.vc; spárováno podle názvu.",
    "Rockaway": "Rockaway Ventures (CzechCrunch) a Rockaway Capital Partners (StartupYard): stejná značka, investiční subjekt určí ověření.",
    "Tila Impact Partners": "Možná totéž jako Tilia Impact Ventures (název se liší o písmeno): nejistá shoda, nespárováno.",
    "N1": "Možná totéž jako Nation1: nejistá shoda, nespárováno.",
    "skupina ČMZRB": "Skupina, do které patří NRI? Nejistá shoda, nespárováno.",
    "JSK": "Ze zdroje nelze určit, zda jde o firmu, nebo o osobu.",
    "Orbit": "EIF uvádí správce OGD Advisory s.r.o. u fondu Orbit Growth Debt II s webem orbitcapital.com.",
}
TESTED = {"Credo", "Presto Ventures"}
DUPLICATE_NOTE = ("Oprava duplicity (2026-10-16): původně samostatný kandidát CAN-0028. „Tila Impact Partners“ "
                  "je překlep v seznamu EIF pro tým Tilia, proto jde o tentýž kandidát jako CAN-0025.")
NON_VC = re.compile(r"private equity|buy-?out|buy out|buy-and-build|\bmbo\b|\bmbi\b|\blbo\b|odkup|akvizic|"
                    r"acquisition|debt|dluh|lending|mezzanine", re.I)
VC = re.compile(r"\bvcs?\b|venture capital|\bseed\b|pre-seed|startup|start-up|rizikového kapitálu", re.I)


def write(path, rows):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main():
    rows = [r for t in cq.markdown_tables(RUN.read_text(encoding="utf-8")) for r in t if "claim" in r]
    order, findings, labels, sites = [], {}, {}, {}
    for r in rows:
        name, field = r["entita"], r["pole"]
        brand = BRAND.get(name, name)
        source = r["claim"].split("-")[0][0]
        if field == "kandidat":
            if brand not in findings:
                order.append(brand)
                findings[brand] = []
            key = (name, source, r["url"])
            if key not in [(f[0], f[1], f[2]) for f in findings[brand]]:
                findings[brand].append((name, source, r["url"]))
            if source == "2":  # řádek tabulky EIF obsahuje sloupec Strategy
                labels.setdefault(brand, []).append(r["doslovná citace"])
        elif field == "oznaceni":
            labels.setdefault(brand, []).append(r["hodnota"])
        elif field == "sidlo_tymu":
            sites.setdefault(brand, []).append(r["hodnota"])
    out = []
    for number, brand in enumerate(order, 1):
        cid = f"CAN-{number:04d}"
        texts = labels.get(brand, [])
        non_vc = any(NON_VC.search(t) for t in texts)
        vc = any(VC.search(t) for t in texts)
        if brand in TESTED:
            note = "mimo pilot: testováno dříve (docs/agenti.md, kap. 5)"
        elif any(not re.search(r"czech|česk|prague|praha|brno", s, re.I) for s in sites.get(brand, [])):
            note = "mimo pilot: sídlo"
        elif non_vc and not vc:
            note = "mimo pilot: typ podle zdroje (" + "; ".join(t for t in texts if NON_VC.search(t))[:150] + ")"
        else:
            note = NOTES.get(brand, "")
        for name, source, url in findings[brand]:
            via, how = SOURCES[source]
            out.append({"candidate_id": cid, "name": name, "found_via": via, "found_url": url,
                        "found_date": FOUND_DATE, "how": how, "investor_id": "", "note": note})
    write(ROOT / "data/sample/candidates_vyber.csv", out)
    corrected = [dict(row) for row in out]
    for row in corrected:
        if row["candidate_id"] == "CAN-0028":
            row["candidate_id"] = "CAN-0025"
            row["note"] = DUPLICATE_NOTE
    write(ROOT / "data/sample/candidates_vyber_oprava.csv", corrected)
    excluded = {r["candidate_id"] for r in out if r["note"].startswith("mimo pilot:")}
    print(f"{len(order)} kandidátů, {len(out)} nálezů, mimo pilot {len(excluded)}, ve výběru {len(order) - len(excluded)}")


if __name__ == "__main__":
    main()
