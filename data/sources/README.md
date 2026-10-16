# Katalog zdrojů

> **Stav:** schváleno 2026-10-16 (krok 3). Zatím jen zdroje pro české VC investory.
> **Zjištění a závěry:** [docs/zdroje-cr.md](../../docs/zdroje-cr.md)

Katalog popisuje **veřejné zdroje**: co obsahují, jak se k datům dostat, k čemu je lze použít a jak moc se na ně dá spolehnout. Tvoří ho tři tabulky:

| Soubor | Jeden řádek = | Obsah |
|---|---|---|
| `catalog.csv` | jeden zdroj nebo typ zdroje | popis: provozovatel, přístup, formát, aktualizace, podmínky, omezení |
| `uses.csv` | jedno použití zdroje | k čemu zdroj slouží (hledání kandidátů nebo doklad konkrétního údaje), tier, spolehlivost, podmínky a důkazy |
| `evidence.csv` | jedno zjištění o zdroji | URL a doslovná citace z původního zdroje, kontrola citace, verdikt auditora |

**Pravidlo:** každé hodnocení v `uses.csv` odkazuje na důkazy v `evidence.csv` (`evidence_ids`). Výjimkou jsou hodnocení, která plynou přímo ze schválené metodiky. U nich je to uvedeno v `conditions` i s odkazem na kapitolu plánu.

## `catalog.csv`

| Sloupec | Popis |
|---|---|
| `source_key` | `ZDR-00` pro konkrétní zdroj, `TYP-00` pro typ zdroje (např. weby investorů) |
| `kind` | `zdroj`, nebo `typ`. Typ popisuje skupinu podobných zdrojů, konkrétní příklady jsou v `evidence.csv`. |
| `name`, `operator`, `url` | název, provozovatel a hlavní adresa |
| `access`, `format` | jak data získat (web, API, hromadné stažení, registrace, platba) a v jakém formátu |
| `update_frequency` | jak často se data mění nebo k jakému datu platí |
| `terms` | licence a podmínky použití, hlavně pro automatické stahování a další použití |
| `limitations` | omezení: CAPTCHA, limity, neúplnost, střet zájmů, GDPR |
| `automation` | jak zdroj v projektu číst: `skript`, `firecrawl`, `rucne`, `ne` (s upřesněním) |
| `checked_date` | kdy byl zdroj naposledy prověřen |

## `uses.csv`

| Sloupec | Hodnoty | Popis |
|---|---|---|
| `source_key` | z `catalog.csv` | zdroj |
| `use` | `kandidati`, pole datového modelu (kap. 4, např. `identity`, `deal`, `fund`, `aum`), `kontext`, `nepouzivat` | k čemu zdroj slouží. Jeden zdroj má obvykle víc řádků. |
| `tier` | `1`–`4` podle plan.md 6.1, `n/a` | tier pro toto použití. Tentýž web může být pro jedno pole tier 2 a pro jiné tier 3. |
| `reliability` | `vysoka`, `stredni`, `nizka` | u `kandidati`: jak úplný je seznam a kolik obsahuje šumu (neinvestorů). U polí: jak správné a aktuální údaje jsou. |
| `conditions` | text | kdy a jak zdroj použít, na co dát pozor |
| `evidence_ids` | ID z `evidence.csv` oddělená `;` | důkazy, o které se hodnocení opírá |

Zdroj s rolí jen `kandidati` (typicky tier 4) **nikdy nedokládá údaj** (plan.md 6.1). Kandidáta z něj vždy ověřujeme ve zdrojích, které mají řádek pro dané pole.

**Zdroje s omezujícími podmínkami použití** (Czechia Dealroom, OpenVC, CEE Funding Map, databáze CC+): jen ruční a interní hledání jmen. Agenti se na ně neposílají a data se z nich nepřebírají v rozporu s podmínkami.

## `evidence.csv`

| Sloupec | Popis |
|---|---|
| `evidence_id` | `G1-C38` a podobně: skupina běhu (`G1`–`G4`) a číslo tvrzení, nové důkazy auditora `G1-A3`. Příklady z testů agentů jsou `T2-…` (Credo Ventures) a `T3-…` (Presto Ventures). |
| `source_key` | zdroj nebo typ z `catalog.csv` |
| `field`, `value` | o čem zjištění je a co zdroj uvádí (z výstupu agenta) |
| `url`, `quote` | úplná URL a doslovná citace z původního zdroje |
| `found_by` | `průzkumník`, nebo `auditor` |
| `quote_check` | jak byla ověřena doslovnost (viz níže) |
| `audit` | verdikt auditora (`CONFIRMED`, `CORRECTED`, `NOT_SUPPORTED`, `CANNOT_VERIFY`, `neprověřeno`), `nový důkaz auditora`, nebo `příklad z testu` |
| `note` | upřesnění ke kontrole citace, např. zkrácená citace nebo text jen v metadatech |

**Hodnoty `quote_check`:**

- `DOSLOVNĚ (přímo)` nebo `DOSLOVNĚ (firecrawl)`: `scripts/check_quotes.py` našel citaci ve stažené stránce.
- `DOSLOVNĚ (záznam Firecrawl)`: citace je ve stránce, kterou Firecrawl vrátil agentovi a která je uložená v záznamu běhu. Nové stažení se nepodařilo (blokace, nečitelné PDF), nebo citaci upravil agent. Co přesně, uvádí `note`.
- `NEJISTÉ`: text je ve stránce jen jako metadata, cíl odkazu nebo formátování, ne jako viditelný text. Na takové důkazy se závěry neopírají samostatně.

Text v `value` a `quote` se přebírá strojově z výstupů agentů, nikdo ho ručně nepřepisuje. Opravy auditora (`CORRECTED`) jsou zapracované do `catalog.csv` a `uses.csv`. V `evidence.csv` zůstává původní tvrzení i s verdiktem.

## Původ kandidátů (`candidates.csv`)

Aby šlo u každého kandidáta zjistit, odkud ho máme, zapisuje se v datech tabulka `candidates.csv`. Jeden řádek je jeden nález kandidáta v jednom zdroji z tohoto katalogu (`found_via` = `source_key`). `investor_id` zůstává prázdné, dokud kandidáta neověříme. Sloupce a kontroly popisuje [datový model](../../docs/datovy-model.md), kap. 3.6.

Kandidát nalezený ve více zdrojích má víc řádků. Z toho půjde později spočítat, které zdroje přinášejí skutečné investory a kolik šumu.

## Jak katalog vzniká

1. **Průzkumník** zjistí fakta o zdroji z vlastních stránek provozovatele, každé s URL a citací.
2. **Auditor** je kriticky prověří a navrhne použití a spolehlivost.
3. **Koordinátor:**
   - ověří citace skriptem,
   - sestaví `evidence.csv`,
   - podle metodiky vyplní `catalog.csv` a `uses.csv`,
   - zkontroluje konzistenci: každé použití má existující důkazy a žádné se neopírá jen o nejisté nebo neověřené.
