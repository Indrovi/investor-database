#!/usr/bin/env python3
"""Reprodukovatelný výběr vzorku pilotu z candidates.csv (pravidla v data/sample/README.md).

Pravidla:
- kandidát, který má u kteréhokoli nálezu poznámku začínající „mimo pilot:“, se nevybírá,
- zdroje (found_via) se procházejí v pořadí prvního výskytu v souboru a z každého se vezme
  jeden dosud nevybraný kandidát,
- pořadí kandidátů určuje SHA-256 z textu „seed|jméno“ (jméno z prvního nálezu kandidáta),
- když zdroj nemá dalšího kandidáta, doplní se další v pořadí z celého seznamu.

Skript nic nezapisuje, jen vypíše výběr a celé pořadí. Používá jen standardní knihovnu.

Použití:
    python3 scripts/select_sample.py data/sample/candidates.csv --seed TEXT [--count 5]
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import sys
from dataclasses import dataclass, field
from pathlib import Path

EXCLUDED_PREFIX = "mimo pilot:"


@dataclass
class Candidate:
    candidate_id: str
    name: str
    sources: list[str] = field(default_factory=list)
    excluded: bool = False


def load(path: Path) -> list[Candidate]:
    candidates: dict[str, Candidate] = {}
    with path.open(encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            candidate_id = (row.get("candidate_id") or "").strip()
            if not candidate_id:
                continue
            candidate = candidates.setdefault(
                candidate_id, Candidate(candidate_id, (row.get("name") or "").strip()))
            source = (row.get("found_via") or "").strip()
            if source and source not in candidate.sources:
                candidate.sources.append(source)
            if (row.get("note") or "").strip().casefold().startswith(EXCLUDED_PREFIX):
                candidate.excluded = True
    return list(candidates.values())


def order_key(seed: str, name: str) -> str:
    return hashlib.sha256(f"{seed}|{name}".encode("utf-8")).hexdigest()


def select(candidates: list[Candidate], seed: str, count: int) -> list[tuple[Candidate, str]]:
    """Vrátí [(kandidát, odkud vybrán)]: zdroj, nebo „doplnění“."""
    eligible = sorted((c for c in candidates if not c.excluded), key=lambda c: order_key(seed, c.name))
    strata = list(dict.fromkeys(source for c in candidates for source in c.sources))
    chosen: list[tuple[Candidate, str]] = []
    taken: set[str] = set()
    for stratum in strata:
        if len(chosen) == count:
            break
        pick = next((c for c in eligible if stratum in c.sources and c.candidate_id not in taken), None)
        if pick is not None:
            chosen.append((pick, stratum))
            taken.add(pick.candidate_id)
    for candidate in eligible:
        if len(chosen) == count:
            break
        if candidate.candidate_id not in taken:
            chosen.append((candidate, "doplnění"))
            taken.add(candidate.candidate_id)
    return chosen


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Reprodukovatelný výběr vzorku pilotu.")
    parser.add_argument("candidates", type=Path)
    parser.add_argument("--seed", required=True)
    parser.add_argument("--count", type=int, default=5)
    args = parser.parse_args(argv)
    candidates = load(args.candidates)
    chosen = select(candidates, args.seed, args.count)
    print(f"Seed: {args.seed}\nKandidátů: {len(candidates)}, ve výběru: "
          f"{sum(not c.excluded for c in candidates)}, mimo pilot: {sum(c.excluded for c in candidates)}\n")
    print("| pořadí | candidate_id | jméno | vybrán ze zdroje | SHA-256 (začátek) |\n|---|---|---|---|---|")
    for number, (candidate, stratum) in enumerate(chosen, 1):
        print(f"| {number} | {candidate.candidate_id} | {candidate.name} | {stratum} "
              f"| {order_key(args.seed, candidate.name)[:12]} |")
    print("\nCelé pořadí kandidátů ve výběru:")
    eligible = sorted((c for c in candidates if not c.excluded), key=lambda c: order_key(args.seed, c.name))
    for candidate in eligible:
        print(f"  {order_key(args.seed, candidate.name)[:12]}  {candidate.candidate_id}  "
              f"{candidate.name}  ({', '.join(candidate.sources)})")
    return 0 if len(chosen) == args.count else 1


if __name__ == "__main__":
    sys.exit(main())
