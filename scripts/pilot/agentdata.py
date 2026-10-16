"""Načtení výstupů agentů pilotu (.cache/agents/pilot/CAN-ID/): tvrzení s citací a URL a údaje
o zdrojích, beze změny znaků. Odkaz „S:C1“ = tvrzení průzkumníka, „A:A1“ = nový důkaz auditora."""
import re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import check_quotes as cq  # noqa: E402

DATE = re.compile(r"\d{4}(?:-\d{2}(?:-\d{2})?)?")


def _tables(cid, agent):
    path = ROOT / ".cache/agents/pilot" / cid / f"investor-{agent}.md"
    return cq.markdown_tables(path.read_text(encoding="utf-8"))


def claims(cid):
    """{'S:A1': row, 'A:A12': row} – S = průzkumník, A = nové důkazy auditora."""
    out = {}
    for prefix, agent in (("S", "source-scout"), ("A", "evidence-auditor")):
        try:
            tables = _tables(cid, agent)
        except FileNotFoundError:
            continue
        for table in tables:
            for row in table:
                claim = cq.claim_from_row(row)
                if claim is None or not claim.claim_id:
                    continue
                row = dict(row)
                row["_url"], row["_quote"] = claim.url, claim.quote
                out.setdefault(f"{prefix}:{claim.claim_id}", row)
    return out


def source_meta(cid):
    """url -> {publisher, title, tier, published_date, accessed_date} z tabulek agentů."""
    meta = {}
    for agent in ("source-scout", "evidence-auditor"):
        try:
            tables = _tables(cid, agent)
        except FileNotFoundError:
            continue
        for table in tables:
            for row in table:
                url = cq._clean(row.get("url", ""))
                if not url.startswith("http") or "publisher" not in row:
                    continue
                pub = row.get("published_date", "")
                pub_m = DATE.match(pub.strip())
                acc_m = DATE.search(row.get("accessed_date", "") or row.get("text z", ""))
                entry = meta.setdefault(url, {})
                entry.setdefault("publisher", row.get("publisher", ""))
                entry.setdefault("title", row.get("title", ""))
                entry.setdefault("tier", row.get("tier", "").strip()[:1])
                if pub_m:
                    entry.setdefault("published_date", pub_m.group(0))
                if acc_m and len(acc_m.group(0)) == 10:
                    entry.setdefault("accessed_date", acc_m.group(0))
    return meta
