# Investor Database

Spolehlivá databáze investorů do soukromých firem: VC fondů, PE fondů, family offices, angel investorů a velkých soukromých investorů. Hlavním požadavkem je spolehlivost dat. Každý záznam musí odpovídat skutečnému, aktivnímu investorovi a u každého údaje musí být doložený zdroj (data provenance).

Projekt vychází ze [zadání](docs/zadani.md) a pracuje výhradně s veřejně dostupnými daty.

## Výstupy (deliverables)

| Výstup | Umístění | Stav |
|---|---|---|
| Výsledný plán: inclusion/exclusion criteria, verification, odhad rozsahu a spolehlivosti, odhad nákladů | [docs/plan.md](docs/plan.md) | rozpracováno: kroky 2–7 hotové, odhad pro celý svět v kap. 13; u kroku 1 zbývá potvrdit hraniční případy a GDPR |
| Datový model a validátor | [docs/datovy-model.md](docs/datovy-model.md), `scripts/validate.py` | hotovo |
| Agenti pro hledání a ověřování zdrojů | [docs/agenti.md](docs/agenti.md), `.claude/`, `scripts/agents.py`, `scripts/check_quotes.py` | hotovo: vyzkoušeno na testech Credo a Presto Ventures, opravy ověřené; API klíč Firecrawl doplní autor do `.env` |
| Mapa veřejných zdrojů pro české VC (krok 3) | [docs/zdroje-cr.md](docs/zdroje-cr.md), [data/sources/](data/sources/) | hotovo: 20 zdrojů a 5 typů zdrojů, 289 doložených zjištění |
| Ověřovací postup (krok 4) | [docs/overovaci-postup.md](docs/overovaci-postup.md) | hotovo: checklist pro pilot nad existujícími postupy |
| Data ze vzorku (sample) se zdrojem u každého údaje | [data/sample/](data/sample/) | hotovo (krok 5): 5 unikátních investorů, všech 5 zařazených (`included`); otevřené otázky pro krok 6 v [data/sample/README.md](data/sample/README.md) |
| Přehled zařazených investorů pro čtení | [data/sample/investori_prehled.csv](data/sample/investori_prehled.csv) | generuje se z dat (`scripts/export_overview.py`) |
| Výsledky měření přesnosti (accuracy) | [results/](results/README.md) | hotovo (krok 6): autor ručně zkontroloval 10 údajů, 8/10 správně; kontrola AI se s ruční shoduje 10/10; 6 chyb a 1 nejistota, opravy odložené do kroku 8 |

## Struktura repozitáře

```
.claude/         projektoví subagenti Claude Code (agents/), hook pro Firecrawl (hooks/), oprávnění (settings.json)
docs/            zadání, plán, datový model, agenti
data/sample/     data z pilotního vzorku včetně zdrojů
data/examples/   fiktivní ukázková data pro datový model a testy
data/sources/    katalog veřejných zdrojů: zdroje, použití se spolehlivostí, důkazy
results/         měření přesnosti, odhad nákladů
scripts/         skripty: validate.py (validace dat), check_quotes.py (kontrola citací),
                 agents.py (spouštění agentů a předání souborem), firecrawl_mcp.py (Firecrawl s klíčem z .env),
                 select_sample.py (výběr vzorku), export_overview.py (přehled investorů pro čtení)
scripts/pilot/   sestavení dat pilotu z výstupů agentů a rozhodnutí koordinátora, použitá zadání agentů
tests/           testy skriptů
ai-log/          exporty konverzací s AI (zatím jen lokálně)
.env.example     vzor pro .env s API klíčem (.env je v .gitignore)
```

Validace dat a testy (jen standardní knihovna Pythonu, vyzkoušeno na verzích 3.12.13 a 3.14.4):

```bash
python3 scripts/validate.py data/examples/valid --today 2026-10-14
python3 scripts/check_quotes.py --markdown VYSTUP_AGENTA.md
python3 scripts/firecrawl_mcp.py --check        # ověří klíč v .env, klíč nevypisuje
python3 -m unittest discover -s tests -v
```

## Práce s AI

Projekt vzniká ve spolupráci s AI asistentem. Tato část dokumentuje, k čemu se AI používala, jak se kontrolovaly její výstupy, jaké chyby se našly a jaká padla rozhodnutí.

- **Nástroj:** Claude Code (model Claude Opus 5.5)
- **Workflow:** postupuje se po krocích. Každý krok se nejdřív naplánuje a prodiskutuje, implementuje se až po odsouhlasení.
- **Agenti:** hlavní relace Claude Code je koordinátor. Práci rozděluje mezi dva projektové subagenty:
  - `investor-source-scout` (průzkumník) hledá kandidáty, investice a zdroje a vytahuje z nich údaje s citacemi,
  - `investor-evidence-auditor` (kritický kontrolor) se tvrzení snaží vyvrátit, hledá další nezávislé důkazy a rozpory a posuzuje K1–K3.

  Oba čtou stránky přes Firecrawl a nic nezapisují. Tvrzení si předávají souborem (`scripts/agents.py`). Parametry Firecrawlu hlídá hook. Doslovnost a úplnost citací ověřuje koordinátor skriptem. Podrobnosti jsou v [docs/agenti.md](docs/agenti.md).
- **Exporty konverzací:** textové soubory z příkazu `/export` v Claude Code, název začíná datem a časem exportu. Ukládají se do adresáře `ai-log/`, ale do veřejného repozitáře se zatím nepřidávají (rozhodnutí autora).

### Kontroly výstupů

Jak se ověřovaly výstupy AI (ruční kontrola, validační skripty, kontrola zdrojů).

| Datum | Co se kontrolovalo | Metoda | Výsledek |
|---|---|---|---|
| 2026-10-14 | Napojení lokálního repozitáře na GitHub | `git remote -v`, `gh repo view` | OK: veřejný repozitář, větev `main` |
| 2026-10-14 | Údaje o členech CVCA v plánu | stažení stránek členů a textové vyhledávání | 27 řádných a 57 přidružených členů, potvrzeno |
| 2026-10-14 | Statistiky EBAN a BAE k hranici 500 tis. EUR | čtení zdrojového PDF a stránky BAE | čísla a strany potvrzeny, citace doplněny |
| 2026-10-14 | Fiktivní IČO v ukázkových datech | dotaz do ARES (API) | použitá IČO v ARES neexistují |
| 2026-10-14 | Konzistence pravidel v plánu | ruční revize celého `plan.md` | nalezeny a opraveny rozpory (viz Nalezené chyby) |
| 2026-10-15 | Plán, datový model a validátor vůči 5 bodům revize autora (rejstřík, K2, `investment_unspecified`, 500 tis. EUR, E9) | ruční kontrola textu a kódu | ani jeden bod nebyl vyřešený úplně, viz Nalezené chyby |
| 2026-10-15 | Validátor a datový model | 56 testů (`unittest`) na Pythonu 3.12.13 a 3.14.4 | 56/56 OK na obou verzích |
| 2026-10-15 | Že nové testy opravdu hlídají nová pravidla | každé pravidlo zvlášť vypnuto v kopii kódu (mutation check) | při vypnutí kteréhokoli z 5 pravidel testy selžou |
| 2026-10-15 | Fiktivní ukázková data | `validate.py` | platná sada 0 chyb a 0 varování; neplatná přesně 38 vložených chyb a 3 varování |
| 2026-10-15 | Podpora projektových subagentů v Claude Code | oficiální dokumentace (sub-agents, tools-reference), `claude plugin validate .claude/agents` | podporováno (`.claude/agents/`); WebFetch vrací text zpracovaný modelem; hlavičky agentů platné |
| 2026-10-15 | Funkčnost agentů (test Credo Ventures) | scout → auditor (jen tvrzení) → kontrola doslovnosti skriptem (curl) | 6 tvrzení: 5 citací doslovně, 1 ne (auditor ji chybně potvrdil); podrobně v [docs/agenti.md](docs/agenti.md#5-testy) |
| 2026-10-15 | WebFetch vs. Firecrawl na stejných zdrojích | přímé volání Firecrawl MCP bez klíče, porovnání se záznamy WebFetch a se skriptem | Firecrawl vrací skutečný text; WebFetch adresu přeformuloval a větu C4 nevrátil celou ani jednou |
| 2026-10-15 | Firecrawl jen u agentů | nová relace `claude -p`: seznam nástrojů hlavní relace, volání ze subagenta | hlavní relace Firecrawl nevidí, auditor ho volá správně; v už běžící relaci se server nepřipojil (nutný restart) |
| 2026-10-15 | Zákaz `firecrawl_search` (`disallowedTools`) | nová relace, oprávnění nástroj povolují, agent ho má zkusit použít | agent nástroj nemá („No such tool available“) |
| 2026-10-15 | Skript `check_quotes.py` | 8 nových testů bez sítě a ostrý běh na výstupu auditora z testu Credo | 64/64 testů OK na Pythonu 3.12.13 a 3.14.4; 21/21 citací, 3 stránky přes zálohu Firecrawl |
| 2026-10-15 | Opravy před uzavřením architektury | cílené technické běhy agentů přes `scripts/agents.py`, bez testu investora | předání souborem beze změny znaků; neúplné záznamy odmítnuty (6/6); hook zablokoval 2 volání se špatnými parametry; čtení `.env` zablokováno |
| 2026-10-15 | Python testy po opravách | `python3 -m unittest discover -s tests` | 77/77 OK na Pythonu 3.12.13 a 3.14.4 |
| 2026-10-15 | Test agentů na Presto Ventures | scout → auditor (předání skriptem) → `check_quotes.py`; výpis všech 43 volání Firecrawlu | auditor odhalil záměnu investorů (investice odděleného fondu), 22 nových důkazů; citace 19/20 a 21/22 doslovně; podrobně v [docs/agenti.md](docs/agenti.md#54-test-presto-ventures-2026-10-15-nové-instrukce-firecrawl) |
| 2026-10-16 | Mapa zdrojů ČR (krok 3) | průzkumník (4 skupiny) → auditor → `check_quotes.py`; tvrzení o zdrojích s URL a citací | 193 tvrzení: 153 potvrzeno, 23 opraveno, 1 nedoloženo, 9 neověřitelných; 83 nových důkazů auditora |
| 2026-10-16 | Doslovnost citací v katalogu | `check_quotes.py`, dověření proti stránkám uloženým v záznamech běhů (bez nových kreditů) | 284 z 289 doslovně, 5 označeno jako nejisté |
| 2026-10-16 | Konzistence katalogu a dokumentace | skript: existence důkazů u každého použití, odkazy v dokumentu, počty, přehled vs. `uses.csv`, sloupce vs. README | vše sedí; jediné hodnocení bez důkazu plyne z metodiky a je tak označené |
| 2026-10-16 | Spotřeba kreditů Firecrawlu | `creditsUsed` ze záznamů běhů a zůstatek účtu | 491 kreditů, z toho asi 243 jedno 81stránkové PDF čtené třikrát |
| 2026-10-16 | Python testy | `python3 -m unittest discover -s tests` | 80/80 OK |
| 2026-10-16 | Python testy po fázi 0 kroku 5 (`candidates.csv`, duplicitní IČO) | `python3 -m unittest discover -s tests` | 93/93 OK; každý ze 60 kódů validátoru má test |
| 2026-10-16 | Pilot: hledání kandidátů a výběr | průzkumník nad 5 zmapovanými zdroji, `check_quotes` (přímo a proti kopii Firecrawlu), triáž, `select_sample.py` se seedem zapsaným předem | 151/151 citací doslovně; 74 kandidátů, 55 ve výběru, 5 vylosováno |
| 2026-10-16 | Pilot: ověření 5 kandidátů | průzkumník → auditor → kontrola citací → rozhodnutí podle checklistu | 4 subjekty ověřeny, K3 splněno u všech, K1 sporné u 3, typ sporný u 1 |
| 2026-10-16 | Pilot: data | `validate.py data/sample --today 2026-10-16` a kontrola doslovnosti všech citací v datech | 0 chyb (jen `MISSING_ARCHIVE`); 83/83 citací doslovně (70 živě, 13 proti kopii Firecrawlu) |
| 2026-10-16 | Pilot: přehodnocení K1–K3 | K1 i podle I2 (tým a značka), K2 jednoznačná pravomoc; doplňující ověření K2 u Rockaway (průzkumník a auditor, 10 stránek) | 4 subjekty `included` (A); právnické osoby týmů jako E10; nejtěsnější: K2 Rockaway (auditor: sporné) a typ NRI |
| 2026-10-16 | Pilot: data po přehodnocení | `validate.py data/sample --today 2026-10-16`, kontrola doslovnosti všech citací | 0 chyb (jen `MISSING_ARCHIVE`); 110/110 citací doslovně (90 živě, 19 proti kopii Firecrawlu, 1 přes Firecrawl) |
| 2026-10-16 | Přehled pro čtení | `export_overview.py data/sample --today 2026-10-16` a kontrola proti datům a validátoru | 4 řádky = 4 zařazení investoři; město, počty, poslední doložená investice a všechny odkazy na zdroje a citace sedí |
| 2026-10-16 | Python testy po přidání přehledu a pole `city` | `python3 -m unittest discover -s tests` | 103/103 OK |
| 2026-10-16 | Oprava duplicity ve výběru | opravený snímek kandidátů (CAN-0028 → CAN-0025), `select_sample.py` se stejným seedem | 4 kandidáti beze změny, 5. unikátní: CAN-0019 Orbit Capital |
| 2026-10-16 | Ověření Orbit Capital a data | průzkumník → auditor → kontrola citací; `validate.py`, kontrola doslovnosti, přehled | included (A); 0 chyb; 141/142 citací ověřeno nyní, 1 (Unquote, 429) ověřena dříve; přehled 5 řádků sedí s daty |
| 2026-10-16 | Přehled: doložené investice a deklarovaný ticket | `export_overview.py data/sample --today 2026-10-16`, `validate.py`, `python3 -m unittest discover -s tests` | 5 řádků; u každého investora firmy s doloženými investicemi; ticket označen jako deklarovaný, u Orbitu pro growth equity; 0 chyb; 105/105 testů OK |
| 2026-10-16 | Reprodukovatelnost dat pilotu | `scripts/pilot/build_candidates.py`, `build_sample.py`, `export_overview.py` z uložených výstupů agentů; porovnání s daty v repozitáři | všechny soubory v `data/sample/` bajt po bajtu shodné; výběr shodný |
| 2026-10-16 | Python testy po pilotu (`select_sample.py`) | `python3 -m unittest discover -s tests` | 96/96 OK |

### Nalezené chyby

Chyby ve výstupech AI nebo v datech a způsob jejich opravy.

| Datum | Popis chyby | Dopad | Oprava |
|---|---|---|---|
| 2026-10-14 | AI navrhla hranici 500 tis. EUR mezi business angelem a large private investorem bez opory ve zdroji (zjištěno dotazem autora). | Nedoložené pravidlo v plánu | Doloženo statistikami EBAN a BAE, hranice je vedená jako orientační |
| 2026-10-14 | Rozpory v plánu. Pravidlo E9 vyřazovalo subjekty, které měly zůstat kandidáty. Zůstalo staré 36měsíční okno. Holding s týmem byl zároveň large private investor i family office. | Pravidla si odporovala | Opraveno při kontrole konzistence |
| 2026-10-14 | Validátor při CSV se středníkem (Excel s českým nastavením) hlásil 106 navazujících chyb. | Nepřehledný výstup | Jedna chyba `WRONG_DELIMITER`, při chybě struktury souborů se dál nepokračuje |
| 2026-10-15 | Datový model povoloval: odvozené hodnoty bez původního zdroje; investice s nejasným nástrojem jako důkaz; datum zápisu do rejstříku jako datum investice; celkový upsaný kapitál fondů jako AUM (zjištěno revizí autora). | Riziko nedoložených nebo zaměněných údajů | Opraveno v modelu, validátoru a testech, viz [datovy-model.md](docs/datovy-model.md) |
| 2026-10-15 | AI uvedla počty testů nejasně: „18 testů“ a „21 testů jedné změny“. 21 případů přitom běželo uvnitř jediného z 18 testů. | Zavádějící informace o rozsahu testování | Každý případ je samostatný test, `unittest` hlásí skutečný počet |
| 2026-10-15 | Validátor počítal samotný zápis společníka v rejstříku jako důkaz investice (K3) a plán ho v kap. 6.4 označoval za „silný Tier 1 důkaz investice“. Zápis přitom dokazuje jen vlastnictví podílu. (Zjištěno revizí autora.) | Investor mohl být zařazený bez doložené investiční transakce | K3 vyžaduje další doklad (listina, oznámení), zdroj zápisu se nepočítá; plán, model a testy upraveny |
| 2026-10-15 | K2 se nijak neevidovala a validátor ji nekontroloval. Investor tak mohl být zařazený a dostat hodnocení A/B bez posouzení K2, přestože ji plán (kap. 6.3) vyžaduje. (Zjištěno revizí autora.) | Rozpor mezi plánem a validátorem | Citace `decision_authority`, chyba `K2_NOT_MET`, sloupec K2 v přehledu |
| 2026-10-15 | U `investment_unspecified` validátor nijak nekontroloval, že zdroj investici výslovně oznamuje. Stačila i věta „poskytl financování“. (Zjištěno revizí autora.) | Půjčka mohla projít jako doklad investování | Hrubá kontrola výrazů, varování `INVESTMENT_NOT_EXPLICIT`, investice se nepočítá |
| 2026-10-15 | Kap. 4.3 sice označovala 500 tis. EUR za orientační hranici, ale formulace „je Large Private Investor, pokud splní alespoň jedno“ z ní dělala automatické pravidlo. E9 i po dřívější opravě vyřazovalo jen na základě varovných signálů (např. anonymní tým). (Zjištěno revizí autora.) | Pravidla v plánu odporovala zamýšlenému výkladu | 4.3 a E9 přeformulovány; E9 vyžaduje výsledek prověření (`E9_REVIEW_MISSING`) |
| 2026-10-15 | Auditor (AI) potvrdil citaci z webu Credo Ventures jako doslovnou, ačkoli se od textu stránky liší interpunkcí. WebFetch vrací text zpracovaný modelem. | Riziko nedoslovných citací v datech | Doslovnost rozhoduje kontrola skriptem u koordinátora; instrukce auditora upřesněna |
| 2026-10-15 | Koordinátor (AI) při předání tvrzení auditorovi zapsal do sloupce pole `instrument` a `is_follow_on`, které nejsou citovatelná pole. Scout je uvedl jen v poznámce. Auditor chybu zachytil. | Chyba vnesená při předání mezi agenty | Tvrzení se předávají beze změn (docs/agenti.md, kap. 2) |
| 2026-10-15 | Seznam `tools` v definici agenta neomezil nástroje MCP serveru definovaného v agentovi. Oba agenti zkusili `firecrawl_search`, zastavila je jen oprávnění testovací relace. | V interaktivní relaci by agenti používali nepovolený nástroj | Zákaz v `disallowedTools`, ověřeno testem |
| 2026-10-15 | Kontrolní skript koordinátora (AI): hlásil neshodu kvůli mezeře před čárkou (spojení prvků HTML), řádky bez URL potichu přeskočil a chybu Firecrawlu vypsal nesrozumitelně | Falešné neshody, neúplná kontrola | Opraveno v `check_quotes.py`. Neúplný záznam (bez ID, úplné URL nebo citace) se odmítne, testy doplněny. |
| 2026-10-15 | Spouštěcí relace (AI) při předání tvrzení auditorovi nahradila typografické apostrofy a uvozovky rovnými | Změna znaků citací při předání | Předání souborem JSON (`scripts/agents.py`), agent ho čte nástrojem Read. Ověřeno: citace dorazí beze změny. |
| 2026-10-15 | Průzkumník (AI) přiřadil Presto Ventures investice fondu, který byl od skupiny Presto oddělen v dubnu 2025. Auditor záměnu odhalil. | Do dat by šly investice jiného investora | Tvrzení `NOT_SUPPORTED`, K3 doloženo jinými doklady |
| 2026-10-15 | Auditor (AI) převzal do dvou citací citlivé údaje o fyzické osobě | Rozpor s plan.md, kap. 6.5 | Do dat ani dokumentace se nepřebírají; navrženo doplnit pravidlo do instrukcí auditora |
| 2026-10-15 | AI v souhrnu kroku 2 uvedla jako zbývající ke schválení jen tiers, A/B/C a E1–E10. Vynechala hraniční případy (kap. 9) a GDPR (kap. 6.5), které plán vedl jako neschválené. | Neúplná informace o stavu schválení | Doplněno do plánu (kap. 12) a do souhrnu pro autora |
| 2026-10-16 | Kontrolní skript koordinátora (AI) neuměl stránky vykreslované JavaScriptem, PDF ani XLSX a escapovanou svislou čáru v tabulce bral jako oddělovač | 48 falešných neshod citací | Záloha přes Firecrawl pro tyto případy, druhý pokus nad vykreslenou stránkou, odstup volání, 3 nové testy |
| 2026-10-16 | Průzkumník (AI) u 11 citací porušil pravidla doslovnosti (výpustky, markdown, metadata, adresa odkazu místo textu) | Citace neprošly kontrolou | 7 dověřeno proti uloženým stránkám, 4 označeny jako nejisté (pátá nejistá citace je auditorova) |
| 2026-10-16 | Koordinátor (AI) v souhrnu kroku 3 uvedl chybná čísla (19 místo 13 blokací hookem, 42 místo 48 falešných neshod), spotřebu kreditů přisoudil PDF bez měření a dvě hodnocení ČNB odkázal na důkazy jiného zdroje | Nepřesná dokumentace | Čísla opravena a kredity změřeny ze záznamů běhů; odkazy opraveny, konzistence ověřena skriptem |
| 2026-10-16 | Souběžné běhy agentů překročily limit Firecrawlu a jedno 81stránkové PDF se četlo třikrát | Zhruba polovina kreditů tarifu Free za měsíc | Doporučení v docs/agenti.md: velká PDF číst jednou, agenty pouštět za sebou |
| 2026-10-16 | Průzkumník (AI) při mapování četl přes Firecrawl veřejné stránky Czechia Dealroom, jehož podmínky automatický přístup zakazují | Riziko porušení podmínek zdroje | Zdroje s omezujícími podmínkami jen ručně a interně (D-019) |
| 2026-10-16 | Koordinátor (AI) po vytvoření `check_quotes.py` neopravil plan.md a datovy-model.md, které dál uváděly kontrolu citací na webu jako odloženou do kroku 4 | Dokumentace neodpovídala nástrojům | Opraveno při kroku 4, odkazy na `check_quotes.py` |
| 2026-10-16 | Koordinátor (AI) při triáži spároval „Rockaway Capital Partners“ s Rockaway Ventures jen podle značky | Chybný kandidát ve výběru ovlivnil los ze zdroje StartupYard | Opraveno při ověření (CAN-0075), snímek výběru uložen, výběr bez náhrad zachován |
| 2026-10-16 | Koordinátor (AI) nechal při triáži nejistou shodu „Tila“ / „Tilia“ jako dva kandidáty | Vzorek obsahoval tentýž subjekt dvakrát (jen 4 unikátní investoři) | Oprava duplicity: opravený snímek a doplnění 5. unikátního kandidáta podle seedu |
| 2026-10-16 | Průzkumník (AI) citoval IČO z výsledků hledání v rejstříku bez mezer | 5 nedoslovných citací | Do dat nepoužity; IČO doložena jinými citacemi |
| 2026-10-16 | Agenti (AI) 20× volali Firecrawl s nepovoleným parametrem `objective` | Zbytečné kroky (kredity ne, hook volání zablokoval) | Bez zásahu; hook funguje |
| 2026-10-16 | Koordinátor (AI) v prvním vyhodnocení pilotu vyžadoval u K1 konkrétní právnickou osobu s IČO, ačkoli metodika připouští I2 | Všichni 4 investoři zůstali kandidáty | Přehodnoceno: investiční subjekt je tým a značka (I2), právnické osoby jako E10 |
| 2026-10-16 | Koordinátor (AI) zapsal u NRI do typické investice (`ticket_max`) limit programu 80 mil. Kč | Záměna typické investice s limitem programu | Opraveno: ticket `not_public`, limit jen v citaci a poznámce |

### Rozhodnutí (decision log)

Úplný přehled je v [plan.md, kap. 12](docs/plan.md#12-přehled-rozhodnutí-a-otevřené-otázky).

| ID | Datum | Rozhodnutí | Zdůvodnění |
|---|---|---|---|
| D-001 | 2026-10-14 | Dokumentace česky, odborná terminologie anglicky, commit messages česky | Rozhodnutí autora projektu |
| D-002 | 2026-10-14 | Veřejný GitHub repozitář `Indrovi/investor-database`, hlavní větev `main` | Zadání chce výstupy v repozitáři; veřejný repozitář určil autor projektu |
| D-003 | 2026-10-14 | Investor = sám rozhoduje + veřejně doložená investice. Pět typů ze zadání, jeden záznam = jeden investiční subjekt. | Účel: rychle najít skutečné investory pro projekt |
| D-004 | 2026-10-14 | K zařazení stačí 1 kvalitní nezávislý důkaz. Úřední registr není povinný (identita I1/I2/I3). | Registr nemusí existovat u fyzických osob a části FO |
| D-005 | 2026-10-14 | Aktivita `active` / `inactive` (24 měsíců), bez automatického vyřazení. Neúplné datum se vyhodnocuje konzervativně. | Chybějící doklad neznamená konec investování |
| D-006 | 2026-10-14 | Velikost fondu ≠ AUM, součty fondů se nepočítají. Pilot: české VC = tým nebo správce sídlí v ČR. | Zabránit záměně údajů |
| D-007 | 2026-10-15 | Datový model: 5 CSV tabulek, každý důležitý údaj s citací (zdroj, datum, úryvek), validátor v Pythonu | Strukturovaná a zpětně ověřitelná data |
| D-008 | 2026-10-15 | Číselník 18 sektorů + doslovné původní označení. Aktivita jen z nezávislých zdrojů. Důvod `ambiguous`. Fáze a regiony podle návrhu. Bez přepočtu měn. | Revize datového modelu autorem |
| D-009 | 2026-10-15 | Odvozené hodnoty s původními zdroji. Nejasný nástroj není důkaz investování. Zápis a vklad v rejstříku nejsou datum a výše investice. Upsaný kapitál fondů není AUM. | Revize datového modelu autorem |
| D-010 | 2026-10-15 | Samotný zápis společníka v rejstříku nesplní K3 ani nezakládá `active`. `investment_unspecified` se počítá jen při výslovném oznámení investice. | Zápis dokazuje vlastnictví podílu, ne investici; obecné „financování“ může být půjčka |
| D-011 | 2026-10-15 | K2 je povinná a eviduje se citací `decision_authority`. Bez posouzení K2 se investor nezařadí. | Evidovat, zda a na základě čeho byla K2 ověřena |
| D-012 | 2026-10-15 | 500 tis. EUR jen orientační vodítko, ne automatické pravidlo. E9 až po prověření, samotné varovné signály nevyřazují. | Revize plánu autorem |
| D-013 | 2026-10-15 | Schváleny úrovně zdrojů Tier 1–4, hodnocení A/B/C a pravidla vyřazení E1–E8 a E10 | Výslovné schválení autorem |
| D-014 | 2026-10-15 | Exporty konverzací se zatím nepřidávají do veřejného repozitáře | Obsahují celé konverzace, rozhodnutí autora |
| D-015 | 2026-10-15 | Dva projektoví subagenti Claude Code (scout, auditor) bez dalších frameworků, jen v `.claude/agents/` tohoto repozitáře. Koordinuje hlavní relace a jen ta zapisuje data. | Oddělit hledání od nezávislé kontroly; agenti bez zápisových nástrojů |
| D-016 | 2026-10-15 | Role: průzkumník vyhledává a vytěžuje, auditor je kritický kontrolor (kontext, vlastní nezávislé důkazy, rozpory, K1–K3). Oba používají Firecrawl bez klíče, definovaný jen v hlavičce agentů. Finální kontrola citací skriptem zůstává. Pravidla zařazení beze změny. | Agenti se mají doplňovat, ne opakovat stejnou práci; WebFetch přeformulovával citace |
| D-017 | 2026-10-15 | Ostatní nástroje Firecrawlu zakázané v `disallowedTools`. Auditor dává verdikt ke každému klíčovému tvrzení a uvádí všechny rozpory. Kontrola citací je skript `scripts/check_quotes.py` se zálohou přes Firecrawl. | Opravy po testu Credo, schválené autorem |
| D-018 | 2026-10-15 | Uzavření architektury agentů. Tvrzení se předávají souborem JSON (`scripts/agents.py`). Neúplný záznam bez úplné URL se odmítne. Parametry Firecrawlu vynucuje hook `PreToolUse`. API klíč je v `.env`, čte ho jen `headersHelper` a agenti mají čtení `.env` zakázané. | Požadavek autora: žádné změny znaků v citacích, žádné tiché přeskočení, kontrola mimo prompt, klíč mimo repozitář a konverzaci |
| D-019 | 2026-10-16 | Krok 3 jen pro ČR, celosvětový odhad až v závěrečné analýze. Katalog zdrojů ve třech tabulkách (zdroje, použití se spolehlivostí, důkazy). Zdroje s omezujícími podmínkami jen ručně a interně. Evidence původu kandidátů v pilotu. | Schválení mapy zdrojů autorem |
| D-020 | 2026-10-16 | Ověřovací postup jako checklist nad existujícími postupy. Archivace odložena do dokončení pilotu. Stejné IČO = stejný subjekt. U značky s více právnickými osobami rozhoduje investiční pravomoc, jako E10 se slučují jen osoby bez ní. Automatické párování v pilotu. Pro K3 se hledají i starší investice, 24 měsíců určuje jen aktivitu. Citace zůstávají doslovné, osobní údaje se chrání výběrem úryvku. Sankční seznamy zatím otevřené. | Schválení checklistu autorem: využít hotové postupy, metodiku ani architekturu agentů neměnit |
| D-021 | 2026-10-16 | Pilot nejdřív na 5 různorodých českých VC, rozšíření až po osvědčení postupu. Kandidáti jen ze zmapovaných zdrojů, zdroje s omezeným přístupem vynechané, současný tarif Firecrawl. `candidates.csv` s `investor_id` až po ověření. Validátor hlásí duplicitní IČO, párování dělá koordinátor. | Rozhodnutí autora k návrhu pilotu |
| D-022 | 2026-10-16 | Pilot: kandidáti automaticky ze zmapovaných zdrojů, triáž a výběr 5 kandidátů reprodukovatelně (seed zapsaný předem, jeden z každého zdroje), Credo a Presto vynechány, bez náhrad. Kandidáti, u nichž rozhodnutí patří autorovi, zůstávají `candidate`. | Pokyn autora ke spuštění pilotu |
| D-023 | 2026-10-16 | Přehodnocení pilotu: K1 splní i identita týmu a značky I2 z nezávislých zdrojů bez IČO, K2 musí jednoznačně doložit skutečnou rozhodovací pravomoc. Kandidát může mít úplný profil, chybějící údaje mají důvod. | Pokyn autora |
| D-024 | 2026-10-16 | Nové pole `city` (město sídla investičního týmu, jen s citací). Přehled zařazených investorů pro čtení se generuje z dat skriptem, druhá databáze nevzniká. | Požadavek autora na prakticky použitelný výstup |
| D-025 | 2026-10-16 | Duplicita ve výběru se opravuje novým snímkem kandidátů a opakovaným výběrem se stejným seedem; původní výběr zůstává pro audit. Nejde o náhradu neúspěšného investora. | Požadavek autora na 5 unikátních investorů |
| D-026 | 2026-10-16 | Nové pole `ticket_scope` (ke které strategii se deklarovaný ticket vztahuje). Přehled vypisuje všechny doložené investice a ticket jako deklarovanou hodnotu. Hraniční rozhodnutí (hodnocení A u NRI, K2 Rockaway) jsou body pro ruční audit v kroku 6. | Pokyn autora k uzavření kroku 5 |
