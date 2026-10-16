# Pilot: české VC (krok 5)

> **Stav:** krok 5 uzavřen 2026-10-16. Po opravě duplicity ve výběru je ověřeno 5 unikátních investorů, všech 5 je zařazených (`included`). Audit v kroku 6 našel 6 chyb a 1 nejistotu; **data obsahují původní, neopravené hodnoty** (opravy v kroku 8, viz kap. Otevřené otázky pro krok 6).
> **Postup:** [ověřovací postup](../../docs/overovaci-postup.md) · **Pravidla:** [plan.md](../../docs/plan.md) · **Data:** [datový model](../../docs/datovy-model.md) · **Zdroje:** [katalog](../sources/)

## Rozsah

- **5 různorodých českých VC investorů.** Na nich se důkladně ověří celý postup od nálezu kandidáta po zápis dat. Rozšíření přijde, až se postup osvědčí.
- **Český VC investor:** investiční tým nebo správce doložitelně sídlí v ČR, bez ohledu na domicil fondu (plan.md 11.1). Typ určují pravidla v plan.md 4.1, CVC se počítá jako VC (4.2).
- **Kandidáti jen ze zmapovaných zdrojů** (katalog kroku 3), vybraní automaticky a reprodukovatelně (kap. Výběr vzorku). Credo Ventures a Presto Ventures jsou vynechané, protože prošly testy agentů.
- **Datum stavu: 2026-10-16.** Aktivita se počítá k tomuto dni: `python3 scripts/validate.py data/sample --today 2026-10-16`.

## Soubory

| Soubor | Obsah |
|---|---|
| `candidates.csv` | odkud kandidáty máme (i ti, kteří do vzorku nepatří), s výsledkem párování |
| `candidates_vyber.csv` | přesná podoba seznamu kandidátů v okamžiku výběru (původní výběr, pro audit) |
| `candidates_vyber_oprava.csv` | týž seznam s opravenou duplicitou CAN-0028 → CAN-0025 (opravený výběr) |
| `investors.csv`, `funds.csv`, `investments.csv` | údaje o investorech, fondech a investicích |
| `sources.csv`, `citations.csv` | zdroj, datum a doslovná citace u každého údaje |
| `investori_prehled.csv` | **přehled zařazených investorů pro čtení**, generuje ho `python3 scripts/export_overview.py data/sample --today 2026-10-16` (datovy-model.md, kap. 9.1) |

Výstupy agentů (`.cache/agents/pilot/`) zůstávají mimo repozitář.

## Výběr vzorku (pravidla zapsaná před hledáním kandidátů, 2026-10-16)

**1. Hledání kandidátů:** jeden běh průzkumníka nad zmapovanými zdroji pro hledání kandidátů bez omezeného přístupu, v tomto pořadí:

| Pořadí | Zdroj | Stránky |
|---|---|---|
| 1 | CVCA, řádní členové (ZDR-09) | https://cvca.cz/clenstvi/radni-clenove/ |
| 2 | EIF, správci equity fondů v ČR (ZDR-10) | https://www.eif.org/files/attachments/czechia-equity-fundmanagers.pdf |
| 3 | NRI (ZDR-12) | https://www.nrinvesticni.cz/realizovane-investice/ |
| 4 | CzechCrunch (ZDR-13) | dva nejnovější články na https://cc.cz/tag/ccvc/, které mají v titulku „investic“ |
| 5 | StartupYard (ZDR-17) | https://startupyard.com/ a https://startupyard.com/faq |

- **Měsíční přehledy investic** CzechCrunch dnes vycházejí jen v newsletteru [G3-A8], proto je nahrazují souhrnné články.
- **Uložené kopie:** stránky, které Firecrawl stáhl už v kroku 3, čtou agenti z uložené kopie (`.cache/pages/`), aby se nestahovaly znovu.
- **Kontrola jmen:** průzkumník vrátí jméno kandidáta přesně podle zdroje a označení, které mu zdroj dává, vždy s citací. `check_quotes.py` ověří, že jméno na stránce opravdu je.

**2. Zápis do `candidates.csv`:**

- **ID kandidátů** se přidělují v pořadí zdrojů v tabulce výše a v každém zdroji podle pořadí na stránce.
- **Stejná značka** (název nebo web) znamená stejného kandidáta.
- **Fyzické osoby** se nezapisují, uvede se jen jejich počet.

**3. Triáž** (poznámka v `note` s předponou `mimo pilot:`), jinak kandidát zůstává ve výběru:

| Pravidlo | Poznámka |
|---|---|
| Credo Ventures, Presto Ventures | `mimo pilot: testováno dříve` |
| Zdroj subjekt označuje jako PE, buyout, dluhový fond, poradce, banku, platformu nebo realitní fond | `mimo pilot: typ podle zdroje` |
| Zdroj uvádí investiční tým nebo správce mimo ČR (plan.md 11.1) | `mimo pilot: sídlo` |

Triáž o zařazení nerozhoduje. To dělá až ověření podle checklistu.

**4. Výběr 5 investorů:** `python3 scripts/select_sample.py data/sample/candidates_vyber.csv --seed pilot-cz-vc-2026-10-16`

- Ze zdrojů v pořadí prvního výskytu vybere po jednom kandidátovi.
- Pořadí kandidátů určuje SHA-256 z textu `seed|jméno`. Když ve zdroji nezbude nikdo, doplní se další v pořadí z celého seznamu.
- **Bez náhrad:** vybraný kandidát, který metodiku nesplní, se zapíše jako výsledek a nenahrazuje se.

## Výsledek výběru

**Hledání kandidátů** (2026-10-16, jeden běh průzkumníka):

- **151 tvrzení** z 5 zdrojů, všechna doslovně na stránkách (135 přímo, 16 z PDF EIF proti uložené kopii).
- **74 kandidátů v 96 nálezech.** Fyzické osoby se jmény nezapsaly: u investic jich zdroje jmenují 7.
- **Triáž vyřadila 19 kandidátů:** 17 podle označení ve zdroji (PE, buyout, dluh) a 2 dříve testované (Credo, Presto). Ve výběru zůstalo **55 kandidátů**.
- **Výklad triáže:** jako označení se berou jen tvrzení `oznaceni` a sloupec Strategy v tabulce EIF, ne jména fondů ani stupně kol. Vyřazuje se, jen když zdroj označuje subjekt jako PE, buyout nebo dluh a **žádný** zdroj ho zároveň neoznačuje jako VC.

**Vylosovaní kandidáti:**

| Pořadí | Kandidát | Ze zdroje | SHA-256 (začátek) |
|---|---|---|---|
| 1 | CAN-0025 Tilia Impact Ventures | ZDR-09 (CVCA) | 0dc6c85ba8df |
| 2 | CAN-0028 Tila Impact Partners | ZDR-10 (EIF) | 147a43d335d1 |
| 3 | CAN-0055 Rockaway Ventures | ZDR-13 (CzechCrunch) | 0078d351f13b |
| 4 | CAN-0074 StartupYard | ZDR-17 (StartupYard) | 31ef2cc69d92 |
| 5 | CAN-0030 Národní rozvojová investiční | ZDR-12 (NRI) | 0d4993a64ac3 |

### Oprava duplicity ve výběru (2026-10-16)

**Proč:** CAN-0028 „Tila Impact Partners“ (ze seznamu EIF) se při ověření ukázal jako tentýž subjekt jako CAN-0025 Tilia Impact Ventures. „Tila“ je v seznamu EIF překlep, fond II, LP a sídlo se shodují. Při triáži jsem tuto shodu nechal jako nejistou, takže výběr obsahoval jen 4 unikátní subjekty.

**Co se změnilo:** jde o **opravu duplicity**, ne o náhradu neúspěšného investora.

- V opraveném snímku `candidates_vyber_oprava.csv` jsou nálezy CAN-0028 přiřazené ke CAN-0025. Nic jiného se nemění: oddělení Rockaway Capital Partners (CAN-0075) je jiná oprava párování a do snímku se nepromítá, protože by změnila už ověřeného kandidáta.
- Výběr se opakuje stejným skriptem a stejným seedem: `python3 scripts/select_sample.py data/sample/candidates_vyber_oprava.csv --seed pilot-cz-vc-2026-10-16`.
- Výsledek: kandidáti 1, 3, 4 a 5 jsou beze změny. Ze zdroje EIF (ZDR-10) se místo duplicity vybral další kandidát v pořadí, **CAN-0019 Orbit Capital** (SHA-256 1c4d5c73d941). Ostatní kandidáti z EIF jsou v pořadí až za ním (Tensor 26ba…, KAYA cc3c…).
- Původní výběr (`candidates_vyber.csv`) zůstává beze změny pro audit.

| Pořadí | Kandidát (opravený výběr) | Ze zdroje | SHA-256 (začátek) |
|---|---|---|---|
| 1 | CAN-0025 Tilia Impact Ventures | ZDR-09 (CVCA) | 0dc6c85ba8df |
| 2 | **CAN-0019 Orbit Capital** | ZDR-10 (EIF) | 1c4d5c73d941 |
| 3 | CAN-0055 Rockaway Ventures | ZDR-13 (CzechCrunch) | 0078d351f13b |
| 4 | CAN-0074 StartupYard | ZDR-17 (StartupYard) | 31ef2cc69d92 |
| 5 | CAN-0030 Národní rozvojová investiční | ZDR-12 (NRI) | 0d4993a64ac3 |

## Výsledky ověření (po přehodnocení)

**Proč byli všichni napoprvé kandidáti:** důkazy chyběly jen u K2 Rockaway. U ostatních šlo o přísnější vyhodnocení, než jaké metodika vyžaduje. K1 jsem napoprvé posuzoval tak, že musí být určena jedna konkrétní právnická osoba s IČO. Metodika ale u fondových struktur a značek připouští I2: shodnou identifikaci v nezávislém zdroji (název, web, sídlo, klíčové osoby). Investiční subjekt je proto tým a značka. Jeho právnické osoby jsou sloučené jako E10 se svým IČO (overovaci-postup.md, bod 3).

| Kandidát | Záznam | K1 | K2 (rozhodovací pravomoc) | K3 a aktivita | Typ | Status |
|---|---|---|---|---|---|---|
| CAN-0025 Tilia Impact Ventures | INV-0001 | **I2:** shodný název, sídlo a osoby v rejstříku (tier 1), seznamu EIF (tier 2) a na webu | investiční výbor Tilie schvaluje investice fondu II; tým kola vede (Vestbee); formálním správcem je GP téhož týmu | 5 investic, 4 nezávisle doložené za 24 měsíců; **active** (2026-05-19) | VC | **included** (A) |
| CAN-0028 Tila Impact Partners | INV-0001 | – | – | – | – | **oprava duplicity:** tentýž subjekt jako CAN-0025 (překlep v seznamu EIF), ve výběru nahrazen dalším unikátním kandidátem |
| CAN-0055 Rockaway Ventures | INV-0002 | **I2:** značka ve skupině Rockaway Capital, General Partners (tech.eu, Lupa), Praha | fond vedou General Partners z Rockaway, investiční výbor z lidí Rockaway (Unquote 2023, CzechCrunch 2021); AMISTA obhospodařuje jen český feeder, který investuje do lucemburského fondu (KID AMISTA) | Filuta AI, Remix, AdSpawn; **active** (2026-04-22) | VC | **included** (A) |
| CAN-0074 StartupYard | INV-0003 | **I2:** provozovatel Startup Yard Limited (Companies House, Lupa), sídlo vehiklů v Praze | investice kol jdou přes vehikla, jejichž jediným jednatelem je ředitel StartupYardu (Lupa 2020, rejstřík); follow-on rozhoduje DEPO | Fungies.io 2023, Qoobus 2020, Vistag 2018; **inactive** (2023-07-26) | VC, subtype accelerator (investuje vlastní hotovost) | **included** (A) |
| CAN-0030 Národní rozvojová investiční | INV-0004 | **I1:** IČO 08465797 | zapsaná správa fondu fondů; NRI spravuje IPO fond a sama vybírá a kupuje akcie (MPO, Seznam Zprávy) | Hardwario 2022 (Lupa, ČTK); **inactive** (2022-10-18) | VC, subtype public (úřední název „osoba rizikového kapitálu“, menšinové podíly v růstových úpisech) | **included** (A) |
| CAN-0019 Orbit Capital | INV-0011 | **I2:** tým a značka (Praha a Varšava, partneři) podle EIF, Mews, CzechCrunch a Unquote | tým má investiční výbor, partneři fond vedou (CzechCrunch); kapitálový fond je vlastní lucemburský Orbit Growth SCSp | Mews a Preply (Series C, 2022); novější financování je dluh a nepočítá se; **inactive** (2022-12-15) | VC (podle kapitálových investic, plan.md 9) | **included** (A) |

**Nejtěsnější rozhodnutí:**

- **Rockaway, K2:** auditor doplňujícího ověření K2 hodnotil jako sporné. Chybí výpis z lucemburského registru pro GP a fond. Auditor také nevyloučil externího AIFM lucemburského fondu, žádný zdroj ho ale neuvádí. Skutečnou pravomoc týmu dokládají dva nezávislé zdroje a AMISTA je vyloučená strukturou feederu. Pokud by měl být vyžadován i výpis z registru, záznam se vrátí na `candidate`.
- **Orbit, K2 a typ:** stejná výhrada k lucemburskému GP jako u Rockaway. Orbit kombinuje growth equity a venture debt; podle plan.md 9 rozhodují jen doložené kapitálové investice, a protože jsou dvě, nejde o věřitele (E3).
- **NRI, typ:** hraniční. Část firem je zavedená a kotovaná na trhu START, část činnosti tvoří vstupy do fondů jako LP. Rozhodlo vodítko plan.md 4.1, krok 3: menšinové podíly v rostoucích firmách, a ne kontrolní podíly. K tomu úřední název.

**Sloučené právnické osoby (E10, kvůli párování podle IČO):**

- **Tilia:** Tilia Impact Ventures, osoba rizikového kapitálu, s.r.o. (17848911) a Tilia Impact Partners s.r.o. (17621615).
- **Rockaway:** feeder Rockaway Ventures Fund SICAV a.s. (14235781) a Rockaway Ventures Advisors a.s. (14125129).
- **StartupYard:** StartupYard Batch 15 s.r.o. (22266852) a odštěpný závod Startup Yard Limited (03764931).
- **Orbit:** OGD Advisory s.r.o. (22269720) a ORBIT Capital GP s.r.o. (08319961).
- **Nesloučeno, protože role nedoložena:** Rockaway Ventures a.s. (06387136).
- **Nesloučeno, protože ho obhospodařuje jiná skupina:** Conseq-Orbit SICAV, a.s. (08223467, dluhový fond I Orbitu, obhospodařovatel Conseq Funds IS).
- **Samostatný investor:** Rockaway Capital SE (CAN-0075).

**Vyplněnost záznamů** (město týmu je u všech pěti Praha, s citací):

| Investor | Typ | Web | Sektory | Fáze | Geografie | Ticket | AUM | Fondy | Investice |
|---|---|---|---|---|---|---|---|---|---|
| Tilia | vc | ano | generalist (`reported`) | pre-seed až Series A (`derived`) | CEE | 0,3–1,2 mil. EUR | `ambiguous` (nedatovaný údaj CVCA) | 2 (first close 26 mil. EUR, 43 mil. Kč) | 5 |
| Rockaway | vc | ano | 8 odvětví (`reported`) | seed, Series A | CEE, Evropa | `not_public` | `not_public` | 1 (final close ~55 mil. EUR) | 4 (1× `unclear`) |
| StartupYard | vc / accelerator | ano | AI, kyberbezpečnost, IoT | pre-seed, seed | CEE | 25 000 EUR (hotovost) | `not_public` | 0 (velikosti nezveřejněny) | 4 (1× `unclear`) |
| NRI | vc / public | ano | `not_public` (zaměření neuvedeno) | growth (`derived`) | CZ | `not_public` (80 mil. Kč je jen limit programu) | `not_public` (500 mil. EUR je zákonný strop) | 2 (velikost `not_public` / `conflicting`) | 3 (2 jen z vlastního zdroje) |
| Orbit | vc | ano | software a SaaS (podle „Technology and technology-enabled“) | growth | CEE | 6–15 mil. EUR (growth equity) | `ambiguous` (jen dolní mez „more than €200m“) | 3 (kapitálový: first close 42 mil. EUR; 2 dluhové) | 2 (dluhové financování se nezapisuje) |

**Data celkem:**

- **Záznamy:** 13 záznamů v `investors.csv` (5 `included`, 8 sloučených E10), 8 fondů a 18 investic.
- **Zdroje a citace:** 75 zdrojů a 142 citací. Validátor hlásí 0 chyb a jen varování `MISSING_ARCHIVE`.
- **Doslovnost citací:** 142 ze 142. Při poslední kontrole prošlo 141 živě nebo proti kopii Firecrawlu. Citace z Unquote (CIT-0021) se teď nedá stáhnout, protože server vrací 429. V této relaci ji ale jednou ověřil Firecrawl a od té doby se nezměnila.

## Otevřené otázky pro krok 6 (ruční audit)

**Vyhodnoceno v kroku 6** ([results/README.md](../../results/README.md)): otázky rozhodla AI podle metodiky, nejistoty jsou zapsané. NRI má hodnocení B, Vistag se do K3 nepočítá, K2 u Rockaway, Tilie a Orbitu je doložené na úrovni týmu. Audit našel 6 chyb a 1 nejistotu. **Data zatím obsahují původní, neopravené hodnoty**, aby zůstal skutečný výsledek kontroly. Opravy se zapracují v kroku 8, seznam je v [results/README.md](../../results/README.md#souhrn-chyby-nejistoty-a-doporučené-opravy).

Původní znění otázek z kroku 5 (rozhodnutí v datech byla podle metodiky, ale hraniční):

1. **NRI, nezávislost důkazů a hodnocení A.** Jediná doložená investice (Hardwario, 2022) má dva vydavatele, Lupu a ČTK (Forbes). Oba ale přebírají totéž prohlášení firmy.
   - **Ověřit:** jde o dva nezávislé důkazy podle plan.md 6.3?
   - **Pokud ne,** hodnocení je B.
   - Hraniční je i typ (VC, subtype public): menšinové úpisy na trhu START, část firem je zavedená.
2. **Rockaway, K2.** Auditor doplňujícího ověření hodnotil K2 jako sporné.
   - **Chybí:** výpis z lucemburského registru pro GP Rockaway Venture Partners (GP) S.à r.l. a fond Rockaway Ventures Fund SCSp (B263215).
   - **Nevyloučeno:** externí AIFM lucemburského fondu.
   - **Pokud audit výpis vyžaduje, nebo zjistí externího AIFM,** záznam se vrací na `candidate`.
3. **Právnické struktury Tilie a Orbitu.**
   - **Tilia:** GP fondu II (Tilia Impact Ventures II GP S.à r.l.) je doložený jen vlastním zdrojem. Vehikl fondu I není známý a role obou českých s.r.o. (sloučených jako E10) vůči fondům není doložená.
   - **Orbit:** GP ani AIFM kapitálového fondu Orbit Growth SCSp nejsou ověřené v registru. Role OGD Advisory s.r.o. a ORBIT Capital GP s.r.o. (E10) vůči fondům doložená není. Conseq-Orbit SICAV obhospodařuje jiná skupina.
   - **Pokud audit zjistí samostatný subjekt s vlastní investiční pravomocí,** párování (E10) se opraví.
4. **StartupYard, Vistag (DEAL-0012).** Je investice skutečně uskutečněná?
   - Citace CzechCrunch (2018-10-30) je v budoucím čase („získají investici“), titulek článku uvádí „investoval“.
   - **Ověřit:** zda StartupYard do Vistagu opravdu investoval (např. zápis ve vehiklu kola nebo pozdější zmínka).
   - **Pokud ne,** investice se nepočítá a StartupYardu zůstanou 2 doložené investice (hodnocení A trvá díky dvěma vydavatelům u Fungies.io).

## Problémy během pilotu

1. **Párování podle značky při triáži bylo příliš hrubé.**
   - „Rockaway Capital Partners“ ze StartupYardu jsem spojil s Rockaway Ventures. Ověření ukázalo, že jde o skupinu Rockaway Capital, která investuje sama.
   - Nález je teď oddělený jako CAN-0075. Kdyby byl samostatný už při triáži, vylosoval by se ze zdroje StartupYard místo StartupYardu.
   - Vylosovaný výběr se podle pravidla bez náhrad nemění.
2. **Nejistou shodu Tila a Tilia jsem při triáži nechal jako dva kandidáty.** Vzorek proto obsahoval tentýž subjekt dvakrát. Opraveno jako oprava duplicity (kap. Výsledek výběru), pátým unikátním kandidátem je Orbit Capital.
3. **Obchodní rejstřík zobrazuje IČO s mezerami** (např. „084 65 797“), Firecrawl bez nich.
   - 5 citací průzkumníka u Rockaway (výsledky hledání v rejstříku) proto kontrolou neprošlo a do dat se nepoužily.
   - Ostatní citace IČO jsou ověřené proti kopii Firecrawlu.
4. **Agenti 20× zkusili Firecrawl s nepovoleným parametrem `objective`.** Hook všechna volání zablokoval, kredity to nestálo, jen kroky agentů.
5. **První vyhodnocení bylo přísnější než metodika.** Vyžadoval jsem konkrétní právnickou osobu s IČO, i když K1 připouští I2. Při přehodnocení jsou investiční subjekt tým a značka a jejich právnické osoby jsou sloučené jako E10.
6. **Část zdrojů je za paywallem nebo vyžaduje členství** (Forbes, SeeNews). Necitují se, nebo jen jako druhý zdroj vedle volně dostupného.

## Jak data vznikla (pomocné skripty v `scripts/pilot/`)

Data se nepíšou ručně. Sestavují se z výstupů agentů a z rozhodnutí koordinátora:

| Krok | Příkaz | Co dělá |
|---|---|---|
| 1 | `python3 scripts/pilot/build_candidates.py` | z ověřeného výstupu hledání kandidátů sestaví `candidates_vyber.csv` (párování, triáž) a `candidates_vyber_oprava.csv` (oprava duplicity) |
| 2 | `python3 scripts/select_sample.py data/sample/candidates_vyber_oprava.csv --seed pilot-cz-vc-2026-10-16` | reprodukovatelný výběr 5 kandidátů |
| 3 | `python3 scripts/pilot/prompt.py CAN-ID "NÁZEV" "stopy" ["upřesnění"]` a `scripts/pilot/run_one.sh CAN-ID "NÁZEV"` | zadání ze šablon a celý řetězec agentů pro jednoho kandidáta; skutečně použitá zadání jsou v `scripts/pilot/zadani/` |
| 4 | `python3 scripts/pilot/build_sample.py` | z rozhodnutí v `scripts/pilot/decisions.py` zapíše data; citace a URL bere strojově z výstupů agentů (`agentdata.py`) |
| 5 | `python3 scripts/validate.py data/sample --today 2026-10-16`, `python3 scripts/pilot/verify_quotes.py --data data/sample`, `python3 scripts/export_overview.py data/sample --today 2026-10-16` | validace, doslovnost citací (přímo, jinak proti uložené kopii Firecrawlu) a přehled pro čtení |

**Pomocné nástroje:**

- `scripts/pilot/pages.py` ukládá stránky, které Firecrawl už vrátil agentům, do `.cache/pages/`, aby se nestahovaly znovu.
- `scripts/pilot/credits.py` vypíše zůstatek kreditů Firecrawlu. Klíč nevypisuje.

**Reprodukovatelnost:**

- Výstupy agentů a uložené kopie stránek (`.cache/`) nejsou v repozitáři, protože obsahují plné texty cizích stránek. Celé sestavení lze proto zopakovat jen lokálně.
- Každý údaj v datech má URL a doslovnou citaci, takže je dohledatelný i bez nich.
- 2026-10-16 jsem ověřil, že kroky 1, 4 a 5 dávají bajt po bajtu stejné soubory jako v repozitáři.

## Jak se spouští agenti

Jeden investor = jeden běh průzkumníka a jeden běh auditora, vždy za sebou. Mezi nimi kontrola citací (checklist, body 4–7).

```bash
B=.cache/agents/pilot/CAN-0000
python3 scripts/agents.py run investor-source-scout --prompt-file $B/scout.txt --out $B --max-budget-usd 4
python3 scripts/check_quotes.py --markdown $B/investor-source-scout.md
python3 scripts/agents.py handoff $B/investor-source-scout.md --investor "NÁZEV" --out $B/handoff.json
python3 scripts/agents.py run investor-evidence-auditor --prompt-file $B/auditor.txt --out $B --max-budget-usd 6
python3 scripts/check_quotes.py --markdown $B/investor-evidence-auditor.md
python3 scripts/agents.py calls $B/investor-source-scout.jsonl   # volání Firecrawlu (totéž pro auditora)
```

### Šablona zadání: průzkumník

```text
Krok 5 projektu, pilot českých VC. Investor: {NÁZEV}. Nic nezapisuj.

Uložené kopie stránek: .cache/pages/index.tsv (url, soubor, stazeno). Kopie je výstup
Firecrawlu z dřívějšího běhu a platí jako otevřená stránka: čti ji nástrojem Read, ve sloupci
`text z` uveď `firecrawl` a jako accessed_date datum ze sloupce stazeno. Firecrawlem otevírej
jen stránky, které v indexu nejsou.

Najdi a vytěž k tomuto investorovi, vždy s úplnou URL a doslovnou citací:
1. Identita: právnické osoby spojené se značkou (správce, investiční společnost, fondová vehikula,
   GP, poradenská společnost) s registračním číslem a sídlem z úředního zdroje.
2. Fakta k rozhodovací pravomoci: kdo o investicích rozhoduje (obhospodařovatel, GP, investiční
   výbor, tým) a kde sídlí investiční tým.
3. Doložené investice: přednostně nejnovější, ale i starší. U každé firma, datum, nástroj a
   nejlépe nezávislý zdroj (tisková zpráva firmy, redakční článek, listina). Nejvýš 6 investic.
4. Popisné údaje: sektory, fáze, regiony, typická investice, fondy (velikost, typ, datum), AUM.

Výchozí stopy (zmapované zdroje): {STOPY}

Omezení:
- Nepoužívej Czechia Dealroom, OpenVC, CEE Funding Map, databázi CC+ ani jiné databáze,
  jejichž podmínky zakazují automatický přístup.
- Otevři nejvýš 20 stránek. Velká PDF (výroční zprávy, příručky) neotevírej, uveď je ve Stopách.
- U fyzických osob jen jméno a role. Z výpisu rejstříku cituj jen řádek s rolí nebo podílem.
- Nejvýš 30 tvrzení.
```

### Šablona zadání: auditor

```text
Krok 5 projektu, pilot českých VC. Investor: {NÁZEV}. Nic nezapisuj.

Tvrzení průzkumníka jsou v souboru {HANDOFF}. Načti ho nástrojem Read.

Uložené kopie stránek: .cache/pages/index.tsv (url, soubor, stazeno). Kopie je výstup
Firecrawlu z dřívějšího běhu a platí jako otevřená stránka: čti ji nástrojem Read, ve sloupci
`text z` uveď `firecrawl` a jako accessed_date datum ze sloupce stazeno. Firecrawlem otevírej
jen stránky, které v indexu nejsou.

Kromě obvyklého postupu zvlášť prověř:
- která právnická osoba má skutečnou investiční pravomoc a zda jiná osoba téže značky
  rozhoduje sama (docs/overovaci-postup.md, bod 3),
- zda doložené investice patří tomuto investorovi, ne subjektu s podobným názvem,
- K3 i u starších investic. Hranice 24 měsíců se týká jen aktivity.

Omezení: stejné databáze jako průzkumník nepoužívej, otevři nejvýš 12 stránek, velká PDF
neotevírej. U fyzických osob jen jméno a role.
```

## Náklady

Firecrawl zůstává v tarifu Free: k 2026-10-16 zbývá 448 kreditů do 2026-11-12.

- **Strop na investora:** 20 stránek průzkumník a 12 auditor, tedy asi 35 kreditů i se zálohou při kontrole citací. Na 5 investorů nejvýš asi 175 kreditů.
- **Měření:** kredity podle `creditsUsed` v záznamech běhů a podle zůstatku účtu, jako v kroku 3.
- **Agenti:** limit 4 USD na průzkumníka a 6 USD na auditora (`--max-budget-usd`).
- **Pravidlo zastavení:** když jeden investor přesáhne 40 kreditů nebo 10 USD, pilot se zastaví a probere s autorem.

| Běh | Průzkumník (USD, min) | Auditor (USD, min) | Kredity Firecrawlu | Poznámka |
|---|---|---|---|---|
| Hledání kandidátů | 2,63 (9) | – | 2 | ostatní stránky z uložených kopií |
| CAN-0025 Tilia Impact Ventures | 3,29 (8) | 4,13 (10) | 21 | CAN-0028 spárován bez dalšího běhu |
| CAN-0055 Rockaway Ventures | 3,48 (9) | 4,64 (15) | 31 | nejvíc rejstříkových stránek |
| CAN-0074 StartupYard | 3,30 (7) | 3,86 (10) | 21 | |
| CAN-0030 NRI | 3,07 (7) | 4,13 (11) | 18 | |
| Doplňující ověření K2 Rockaway | 2,15 (6) | 3,04 (9) | 15 | jen 6 + 4 stránky |
| Kontrola citací v datech | – | – | 1 | Unquote vracel 429 |
| CAN-0019 Orbit Capital (oprava duplicity) | 3,11 (8) | 4,63 (11) | 26 | |
| **Celkem** | **21,03** | **24,43** | **135** | **45,46 USD**, asi 122 minut běhu agentů; zůstatek 313 kreditů |

- **Kontrola citací** spotřebovala 0 kreditů. Stránky, které přímo stáhnout nešly, se ověřily proti kopii výstupu Firecrawlu.
- **Ani jeden investor nepřekročil pravidlo zastavení** (40 kreditů nebo 10 USD).
- **Práce koordinátora** (hlavní relace) se do tabulky nepočítá.

## Omezení pilotu a mezery v pokrytí

- **Zdroje s omezeným přístupem jsou vynechané:** Czechia Dealroom, OpenVC, CEE Funding Map a databáze CC+ (zdroje-cr.md, kap. 8).
- **ČNB JERRS** (správci podle § 15) vyžaduje ruční hledání kvůli CAPTCHA a **WS JERRS** žádost s certifikátem. V pilotu se nepoužívají, takže menší správci mimo ostatní zdroje mohou chybět.
- **Měsíční přehledy investic CzechCrunch** se systematicky neprocházejí. Kandidáti z médií tak chybějí, pokud nejsou v jiném zmapovaném zdroji.
- **Vzorek je malý a rozvrstvený podle zdrojů.** Výběr je automatický a reprodukovatelný, ale 5 unikátních investorů ověří postup, nikoli přesnost pro všechna česká VC.
- **Lucemburské registry (RCS, CSSF) a seznamy ČNB** nejsou v katalogu ani v pilotu. Proto zůstala neověřená identita GP fondů a registrace podle § 15.
- **Souhrnné články CzechCrunch** jsou z let 2025 a 2026 (2025-08-01 a 2026-01-02), protože novější měsíční přehledy jsou jen v newsletteru.
- **Andělé a další typy** nejsou součástí pilotu.
- **Archivace zdrojů** je odložená do dokončení pilotu (varování `MISSING_ARCHIVE` je očekávané).
