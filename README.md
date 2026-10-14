# Investor Database

Spolehlivá databáze investorů do soukromých firem: VC fondů, PE fondů, family offices, angel investorů a velkých soukromých investorů. Hlavním požadavkem je spolehlivost dat. Každý záznam musí odpovídat skutečnému, aktivnímu investorovi a u každého údaje musí být doložený zdroj (data provenance).

Projekt vychází ze [zadání](docs/zadani.md) a pracuje výhradně s veřejně dostupnými daty.

## Výstupy (deliverables)

| Výstup | Umístění | Stav |
|---|---|---|
| Výsledný plán: inclusion/exclusion criteria, verification, odhad rozsahu a spolehlivosti, odhad nákladů | `docs/` | připravuje se |
| Data ze vzorku (sample) se zdrojem u každého údaje | `data/sample/` | připravuje se |
| Výsledky měření přesnosti (accuracy) | `results/` | připravuje se |

## Struktura repozitáře

```
docs/          zadání, plán a metodika
data/sample/   data z pilotního vzorku včetně zdrojů
results/       měření přesnosti, odhad nákladů
scripts/       skripty pro sběr, validaci a vyhodnocení dat
ai-log/        exporty konverzací s AI
```

## Práce s AI

Projekt vzniká ve spolupráci s AI asistentem. Tato část dokumentuje, k čemu se AI používala, jak se kontrolovaly její výstupy, jaké chyby se našly a jaká padla rozhodnutí.

- **Nástroj:** Claude Code (model Claude Opus 5.5)
- **Workflow:** postupuje se po krocích. Každý krok se nejdřív naplánuje a prodiskutuje, implementuje se až po odsouhlasení.
- **Exporty konverzací:** adresář [`ai-log/`](ai-log/), soubory pojmenované `YYYY-MM-DD_NN_tema.md` (export příkazem `/export` v Claude Code)

### Kontroly výstupů

Jak se ověřovaly výstupy AI (ruční kontrola, validační skripty, kontrola zdrojů).

| Datum | Co se kontrolovalo | Metoda | Výsledek |
|---|---|---|---|
| 2026-10-14 | Napojení lokálního repozitáře na GitHub | `git remote -v`, `gh repo view` | OK: veřejný repozitář, větev `main` |

### Nalezené chyby

Chyby ve výstupech AI nebo v datech a způsob jejich opravy.

| Datum | Popis chyby | Dopad | Oprava |
|---|---|---|---|
| | | | |

### Rozhodnutí (decision log)

| ID | Datum | Rozhodnutí | Zdůvodnění |
|---|---|---|---|
| D-001 | 2026-10-14 | Dokumentace česky, odborná terminologie anglicky, commit messages česky | Rozhodnutí autora projektu |
| D-002 | 2026-10-14 | Veřejný GitHub repozitář `Indrovi/investor-database`, hlavní větev `main` | Zadání chce výstupy v repozitáři; veřejný repozitář určil autor projektu |
