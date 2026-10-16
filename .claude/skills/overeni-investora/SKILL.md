---
name: overeni-investora
description: Ověří jednoho zadaného investora podle metodiky projektu Investor Database. Průzkumník a auditor dohledají veřejné zdroje s doslovnými citacemi, skripty citace ověří a koordinátor vyhodnotí K1–K3, typ, aktivitu, požadované údaje a hodnocení spolehlivosti A/B/C. Použij, když uživatel chce ověřit konkrétního investora (VC, PE, family office, angel, velký soukromý investor).
argument-hint: "\"Název investora\" [výchozí stopy: URL nebo popis]"
allowed-tools: Bash(python3 scripts/*) Bash(scripts/pilot/run_one.sh *) Read Write Edit Grep Glob
---

# Ověření investora

Ověř investora ze zadání: **$ARGUMENTS**

První argument je název investora, případný zbytek jsou výchozí stopy (URL nebo popis). Když název chybí, zeptej se na něj a nic nespouštěj.

Postupuješ jako **koordinátor** podle [checklistu ověřovacího postupu](../../../docs/overovaci-postup.md). O zařazení rozhoduje [plan.md](../../../docs/plan.md), datový model je v [datovy-model.md](../../../docs/datovy-model.md). Žádná nová pravidla nezaváděj.

**Pevná pravidla:**
- **Do `data/sample/`, `results/` ani `docs/` nic nezapisuj.** Výsledek zůstává v adresáři běhu. Zařazení do databáze je samostatné rozhodnutí autora.
- **Soubor `.env` nečti.** Klíč Firecrawlu čtou jen skripty.
- **Citace neupravuj** (plan.md 6.2, checklist bod 16): žádné výpustky ani přepis. U fyzických osob jen profesní údaje.
- **Agenty pouštěj jen přes `scripts/pilot/run_one.sh`,** nikdy dva běhy souběžně (limit Firecrawlu).
- **Nástroje:** soubory čti a prohledávej nástroji Read, Grep a Glob, CSV zapisuj nástrojem Write. Z příkazů shellu spouštěj jen `python3 scripts/…` a `scripts/pilot/run_one.sh`, vždy relativní cestou z kořene repozitáře. Jiné příkazy (`head`, `grep`, `ls`, smyčky) ani vlastní pomocné skripty skill nepředschvaluje. V běhu bez interakce (`claude -p`) by se zamítly.

## 1. Příprava (bez nákladů)

1. **Už ho máme?** Najdi název (i varianty a zkratky) nástrojem Grep v `data/sample/investors.csv` a `data/sample/candidates.csv`.
   - Pokud je v `investors.csv`, řekni to uživateli a pokračuj jen na jeho výslovný pokyn.
   - Pokud je jen v `candidates.csv`, uveď ID kandidáta a pokračuj.
2. **Firecrawl:** `python3 scripts/firecrawl_mcp.py --check` musí hlásit vyplněný klíč.
3. **Kredity:** `python3 scripts/pilot/credits.py`. Při zůstatku pod 50 kreditů se zastav a řekni to uživateli. Jeden investor stál v pilotu 18–31 kreditů.
4. **ID běhu:** `SKILL-` + název bez diakritiky, malými písmeny a s pomlčkami (např. `SKILL-tensor-ventures`). Adresář běhu je `.cache/agents/pilot/<ID>/`.
   - **Pokud v adresáři už je `auditor.log` s řádkem `auditor exit`, agenti doběhli.** Přeskoč na krok 4 a nic znovu nespouštěj.

## 2. Zadání agentů

1. Vytvoř zadání ze šablon pilotu:

   ```bash
   python3 scripts/pilot/prompt.py <ID> "<Název>" "<stopy>" "Ověření jednoho investora mimo pilot. Typ investora předem neurčuj (VC, PE, family office, angel, velký soukromý investor) a hledej i doklady, které by ukázaly, že nejde o investora."
   ```

   - **Stopy:** ze zadání uživatele. Když chybí, napiš: „web investora; u českých subjektů obchodní rejstřík https://or.justice.cz/ a profil na https://cvca.cz/, pokud existuje; uložené kopie v .cache/pages/index.tsv“.
2. Šablony vznikly pro pilot českých VC. V `scout.txt` i `auditor.txt` proto nástrojem Edit nahraď úvodní větu „Krok 5 projektu, pilot českých VC.“ větou „Ověření investora (skill overeni-investora).“ Zbytek zadání neměň.

## 3. Řetězec agentů (asi 20 minut, 7–10 USD, 20–35 kreditů)

```bash
scripts/pilot/run_one.sh <ID> "<Název>"
```

- **Spusť na pozadí s časovým limitem 40 minut** (`run_in_background: true`, `timeout: 2400000`). Bez výslovného limitu by se příkaz po 10 minutách ukončil.
- **Počkej na oznámení o dokončení.** Stav opakovaně nekontroluj a nepoužívej `sleep`.
- **Skript udělá:**
  1. průzkumníka (limit 4 USD),
  2. uložení kopií stránek z Firecrawlu,
  3. kontrolu doslovnosti citací,
  4. předání tvrzení auditorovi souborem,
  5. auditora (limit 6 USD),
  6. znovu kontrolu citací a výpis zůstatku kreditů.
- **Po dokončení zkontroluj:**
  - `scout.log` a `auditor.log` obsahují `exit 0`,
  - `quotes_scout.txt` a `quotes_auditor.txt` mají v posledním řádku počet problémů.
  - Když skript skončí hláškou „Předání odmítnuto“, řekni to uživateli a nepokračuj.
- **Pravidlo zastavení z pilotu:** přesáhne-li investor 40 kreditů nebo 10 USD, sděl to uživateli dřív, než budeš pokračovat.

## 4. Vyhodnocení (checklist, část D)

Přečti `investor-source-scout.md`, `investor-evidence-auditor.md` a oba soubory `quotes_*.txt`. **Používej jen tvrzení, jejichž citace jsou DOSLOVNĚ.** Ostatní ber jako stopy, ne jako doklad.

Rozhodni podle plan.md (body 8–16 checklistu):

| Co | Pravidlo |
|---|---|
| **K1, identita** | I1 (registr), I2 (shoda nezávislých zdrojů: název, web, sídlo, osoby), I3. Párování a E10 podle checklistu, bod 3. |
| **K2, pravomoc** | citace `decision_authority` ze zdroje tier 1–3. Bez ní se investor nezařadí. |
| **K3, investice** | aspoň jeden nezávislý (tier 1/2) výslovný a datovaný doklad konkrétní investice. Stáří nerozhoduje. |
| **Typ** | plan.md 4.1–4.3. Dluhové financování se pro typ ani K3 nepočítá (plan.md 9). |
| **Aktivita** | `active` jen s nezávisle doloženou investicí za posledních 24 měsíců, jinak `inactive`. |
| **Údaje** | sektory, fáze, geografie, ticket, AUM, fondy: hodnota s citací, nebo stav `not_public`, `conflicting`, `ambiguous`. |
| **Rozpory** | vyšší tier, při stejném tieru novější zdroj (plan.md 9). Jinak `conflicting`. |

**Poučení z auditu pilotu** (results/README.md):
- **Investici k fondu přiřaď jen tehdy, když fond uvádí zdroj.**
- **Více publikací téhož prohlášení je jeden důkaz** (plan.md 6.3).
- **Nejistou investici nepočítej mezi doložené.** Patří sem například budoucí čas („získají investici“) nebo jen výběr do programu. Taková citace může doložit jen datum oznámení.
- **Nezaměňuj** ticket a limit programu, velikost fondu a AUM, ani poslední oznámenou a poslední doloženou investici.

**Rozhodnutí podle checklistu, část F, patří autorovi.** Zapiš je jako otevřené otázky a sám je nerozhoduj: nejasná právnická osoba, nerozhodnutelná K2 nebo typ, E9, citlivé údaje o osobách.

## 5. Návrh záznamu a kontrola skripty

1. **Zapiš návrh** do `.cache/agents/pilot/<ID>/data/` jako pět CSV souborů s hlavičkami přesně podle `data/sample/` (zkopíruj první řádek každého souboru):
   - `investors.csv`,
   - `funds.csv` (může mít jen hlavičku),
   - `investments.csv`,
   - `sources.csv`,
   - `citations.csv`.

   ID čísluj od `INV-0001`, `FND-0001`, `DEAL-0001`, `SRC-0001`, `CIT-0001`. **Citace kopíruj znak po znaku z výstupu agenta** (nástroj Read), včetně typografických uvozovek.
2. **Validátor** (K1–K3, aktivita a hodnocení A/B/C se počítají strojově):

   ```bash
   python3 scripts/validate.py .cache/agents/pilot/<ID>/data --today <dnešní datum>
   ```

   Chyby oprav. Varování `MISSING_ARCHIVE` je očekávané (archivace je odložená), ostatní varování vysvětli.
3. **Doslovnost citací:** `python3 scripts/pilot/verify_quotes.py --data .cache/agents/pilot/<ID>/data` musí hlásit 0 problémů. Bez přepínače `--firecrawl` nestojí nic.
   - Řádky „firecrawl_scrape“ ve výpisu znamenají čtení uložené kopie, ne volání Firecrawlu.
4. **Přehled pro čtení:** `python3 scripts/export_overview.py .cache/agents/pilot/<ID>/data --today <dnešní datum>`. Přehled se uloží do `data/investori_prehled.csv` v adresáři běhu.

## 6. Výsledek

Zapiš `.cache/agents/pilot/<ID>/vysledek.md` a uživateli ukaž stručné shrnutí:

1. **Verdikt:** `included` s hodnocením A/B (podle validátoru), `candidate` (co chybí), nebo vyřazení s kódem E.
2. **K1–K3 a typ:** u každého zdroj a citace.
3. **Doložené investice:** firma, datum, nástroj a zdroj. Aktivita k dnešnímu dni.
4. **Požadované údaje:** sektory, fáze, geografie, ticket, AUM a fondy, vždy s hodnotou a stavem.
5. **Nejistoty a otevřené otázky pro autora.**
6. **Náklady:** USD z řádků „Cena“ v `scout.log` a `auditor.log` a kredity podle `credits_after.txt`.

## Omezení

- **Postup, ceny a přesnost jsou změřené na 5 českých VC** (results/README.md). U PE, family offices, angelů a velkých soukromých investorů je to první vyzkoušení (plan.md 13.8).
- **Šablony zadání jsou psané pro české zdroje.** U zahraničních investorů je potřeba dát lepší stopy.
- **Lucemburské a jiné zahraniční registry** v katalogu zdrojů nejsou, struktury fondů tam zůstanou neověřené.
- **Tarif Firecrawl Free** (1 000 kreditů měsíčně) stačí asi na 30–40 ověření.
