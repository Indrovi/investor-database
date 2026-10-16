#!/usr/bin/env python3
"""Vyplní šablony zadání pro průzkumníka a auditora jednoho kandidáta.

Šablony jsou v data/sample/README.md (oddíly „Šablona zadání: průzkumník“ a „… auditor“).
Výstup: .cache/agents/pilot/CAN-ID/scout.txt a auditor.txt. Skutečně použitá zadání pilotu
jsou uložená v scripts/pilot/zadani/.

Použití:
    python3 scripts/pilot/prompt.py CAN-0019 "Orbit Capital" "výchozí stopy (URL)" ["upřesnění"]
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def template(kind: str) -> str:
    readme = (ROOT / "data/sample/README.md").read_text(encoding="utf-8")
    marker = "### Šablona zadání: průzkumník" if kind == "scout" else "### Šablona zadání: auditor"
    return readme.split(marker, 1)[1].split("```text\n", 1)[1].split("```", 1)[0]


def main(argv: list[str]) -> int:
    if len(argv) < 3:
        print(__doc__, file=sys.stderr)
        return 2
    cid, name, stops = argv[:3]
    extra = argv[3] if len(argv) > 3 else ""
    out = ROOT / ".cache/agents/pilot" / cid
    out.mkdir(parents=True, exist_ok=True)
    scout = template("scout").replace("{NÁZEV}", name).replace("{STOPY}", stops)
    if extra:
        scout = scout.replace("\nOmezení:", f"\nUpřesnění: {extra}\n\nOmezení:")
    (out / "scout.txt").write_text(scout, encoding="utf-8")
    auditor = template("auditor").replace("{NÁZEV}", name).replace(
        "{HANDOFF}", f".cache/agents/pilot/{cid}/handoff.json")
    (out / "auditor.txt").write_text(auditor, encoding="utf-8")
    print(out.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
