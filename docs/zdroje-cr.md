# Veřejné zdroje pro české VC investory

> **Stav:** schváleno 2026-10-16 (krok 3). Jen Česká republika. Celosvětový odhad počtu investorů je přesunutý do závěrečné analýzy (plan.md, kap. 2).
> **Katalog:** [catalog.csv](../data/sources/catalog.csv) (zdroje) · [uses.csv](../data/sources/uses.csv) (použití a spolehlivost) · [evidence.csv](../data/sources/evidence.csv) (důkazy) · **Struktura:** [data/sources/README.md](../data/sources/README.md)

Každé zjištění má v `evidence.csv` řádek s URL a doslovnou citací z původního zdroje. Odkazy v hranatých závorkách (např. [G1-A3]) jsou `evidence_id`.

## 1. Shrnutí

**Rozsah:** 20 konkrétních zdrojů a 5 typů zdrojů.

**289 zjištění:**

- 193 tvrzení průzkumníka; auditor 153 potvrdil, 23 opravil, 1 nedoložil, 9 nešlo ověřit, 7 vedlejších nechal neprověřených,
- 83 nových důkazů auditora,
- 13 příkladů z testů agentů.

**Doslovnost citací:**

- 284 citací je doslovně ověřených: 273 kontrolou skriptem, 11 proti stránkám uloženým v záznamech běhů,
- 5 je nejistých (kap. 6).

Každé použití zdroje má vlastní hodnocení: k čemu zdroj slouží (hledání kandidátů, nebo doklad konkrétního údaje), jaký má pro to tier a jak spolehlivé je.

## 2. K čemu je který zdroj použitelný

Přehled je vygenerovaný z `uses.csv`, podmínky a důkazy ke každému řádku jsou tam.

| Zdroj | Hledání kandidátů | Doklad údajů (tier, spolehlivost) |
|---|---|---|
| ČNB – JERRS (seznamy regulovaných subjektů) (ZDR-01) | střední (tier 1) | `identity` 1, vysoká; `decision_authority` 1, vysoká (licence ČNB) / střední (správce podle § 15); `fund` 1, vysoká |
| ČNB – WS JERRS (webové služby) (ZDR-02) | nízká (tier 1) | `identity` 1, vysoká |
| ČNB – statistický seznam investičních fondů (ZDR-03) | střední (tier 1) | nic nedokládá |
| ARES (ZDR-04) | nízká (tier 1) | `identity` 1, vysoká; `country` 1, vysoká |
| Obchodní rejstřík (veřejný rejstřík) (ZDR-05) | střední (tier 1) | `identity` 1, vysoká; `registry_entry_date` 1, vysoká; `registry_contribution` 1, vysoká |
| Sbírka listin (ZDR-06) | ne | `deal` 1, vysoká; `investor_amount` 1, střední; `size` 3, nízká |
| Otevřená data veřejného rejstříku (ZDR-07) | střední (tier 1) | `registry_entry_date` 1, vysoká; `registry_contribution` 1, vysoká |
| Czechia Dealroom (Dealroom.co) (ZDR-08) | střední (tier 4) | nic nedokládá |
| CVCA – členové a statistiky (ZDR-09) | nízká (tier 4) | `sectors` 3, střední; `aum` 3, nízká |
| EIF – seznam správců equity fondů v ČR (ZDR-10) | střední (tier 2) | `fund` 2, vysoká; `decision_authority` 2, střední |
| CzechInvest – Startup data (ZDR-11) | ne | jen kontext |
| Národní rozvojová investiční (NRI) (ZDR-12) | střední (tier 2) | `fund` 2, střední; `deal` 3, nízká |
| CzechCrunch – články a měsíční přehled investic (ZDR-13) | vysoká (tier 2) | `deal` 2, vysoká; `round_amount` 2, střední; `size` 2, střední |
| CzechCrunch – databáze VC investic (CC+) (ZDR-14) | střední (tier 4) | nic nedokládá |
| Tech.eu Funding Explorer (ZDR-15) | střední (tier 4) | nic nedokládá |
| CBAA – Czech Business Angel Association (ZDR-16) | nízká (tier 4) | `ticket` 3, nízká |
| StartupYard (ZDR-17) | nízká (tier 3) | `ticket` 3, střední |
| ČNB – otevřená data seznamů (ZDR-18) | ne | nepoužívat |
| CEE Funding Map (ZDR-19) | nízká (tier 4) | nic nedokládá |
| OpenVC (ZDR-20) | nízká (tier 4) | nic nedokládá |
| Weby investorů (vlastní prezentace, portfolio, tým) (TYP-01) | střední (tier 3) | `sectors` 3, střední; `size` 3, nízká; `decision_authority` 3, střední; `deal` 3, nízká |
| Weby a tiskové zprávy portfoliových firem (TYP-02) | střední (tier 2) | `deal` 2, vysoká; `investment_date` 2, vysoká; `round_amount` 2, vysoká |
| Články o investičních kolech (redakční média) (TYP-03) | vysoká (tier 2) | `deal` 2, vysoká; `round_amount` 2, střední; `investment_date` 2, střední |
| Oznámení co-investorů a LP (TYP-04) | střední (tier 2) | `deal` 2, střední; `fund` 2, vysoká |
| Oznámení poradců o transakcích (advokátní kanceláře) (TYP-05) | střední (tier 2) | `deal` 2, střední |

**Jak to číst:**

- Zdroj, který jen pomáhá **hledat kandidáty**, nic nedokládá. Kandidáta z něj ověřujeme ve zdrojích, které mají pro dané pole tier 1–3.
- U kandidátů znamená spolehlivost, jak úplný je seznam a kolik obsahuje šumu (neinvestorů). U údajů znamená správnost a aktuálnost.

## 3. Nové zdroje

**CEE Funding Map** (ZDR-19): podle partnerů projektu interaktivní mapa VC a PE fondů, které za posledních 12 měsíců investovaly [G4-C1, C2].

- Provozovatel Warsaw Equity Group je sám investor [G4-A3].
- Metodika aktivity není zveřejněná a liší se od naší (12 místo 24 měsíců, neznámý zdroj dat) [G4-C2].
- Odkaz z tiskové zprávy vede na mapu „funds-poland“, pokrytí ČR je proto neověřené [G4-C3, A14].
- Popis pochází jen z tiskové zprávy partnerů [G4-A1].
- Mapu jsme kvůli kreditům a neznámým podmínkám platformy neotevírali.
- **Hodnocení:** kandidáti, nízká spolehlivost.

**OpenVC** (ZDR-20): přes 16 000 investorů z celého světa podle provozovatele [G4-C6].

- Podmínky zakazují scraping, automatické vytěžování, odvozené databáze i redistribuci [G4-C11, A6, A7] a dovolují jen interní použití [G4-C14].
- Provozovatel investory podle vlastních podmínek neprověřuje [G4-C15, A13], což odporuje jeho marketingu [G4-C10].
- **Hodnocení:** jen ruční vyhledávání jmen, nízká spolehlivost.

## 4. Typy zdrojů: weby investorů, startupů a články o kolech

Tyto zdroje nejsou jeden web, ale skupina. Tier a roli jim dává plan.md 6.1, příklady jsou ověřené citace z testů agentů (docs/agenti.md, kap. 5).

| Typ | K čemu | Na co dát pozor | Příklady |
|---|---|---|---|
| **Weby investorů** (TYP-01) | Kandidáti přes portfolio. Zaměření, tickety a fondy jako vlastní tvrzení (tier 3). Tým a rozhodovací orgány (K2). | Nesplní K3. Údaje mohou být zastaralé. „Investováno X“ není AUM ani velikost fondu. | [T2-C37], [T3-C13], [T3-C9] |
| **Weby a tiskové zprávy startupů** (TYP-02) | Doklad investice (tier 2, strana dealu jiná než investor), datum oznámení a velikost kola | Text může dodat investor. Datum v textu je datum oznámení. | [T2-A1], [T2-A2] |
| **Články o investičních kolech** (TYP-03) | Nejčerstvější zdroj kandidátů a doklad dealu (tier 2) | Částky jsou většinou za celé kolo. **Hrozí záměna investorů**: v testu Presto článek jmenoval fond, který už patřil jinému subjektu [T3-C15]. | [T2-C17], [T2-A8], CzechCrunch [T2-C20] |
| **Oznámení co-investorů a LP** (TYP-04) | Existence fondu a vazba na správce (EIF, NRI), někdy i deal | Společná zpráva s investorem je spíš vlastní tvrzení. Vklad LP není velikost fondu. | [T3-A21], [G2-E1], [G3-C3] |
| **Oznámení poradců o transakcích** (TYP-05) | Kandidáti a doklad dealu | Často chybí slovo „investice“, takže u nástroje `investment_unspecified` samo nestačí. Weby blokují roboty. | [T2-A5] |

**Doporučené použití v pilotu:** články o kolech a seznamy (ČNB, CzechCrunch, LP) najdou kandidáty. Weby investorů doplní popisné údaje jako tier 3. Investice dokládají tiskové zprávy startupů, články a listiny.

## 5. Co z toho plyne pro pilot

1. **Kandidáty hledat kombinací zdrojů:** ČNB (správci a investiční společnosti), CzechCrunch (měsíční přehled), články o kolech, LP (EIF, NRI) a portfolia na webech investorů. Ručně a jen interně pak Czechia Dealroom, CVCA, OpenVC a CEE Funding Map. Žádný zdroj sám nestačí.
2. **K2 u správců podle § 15** dokládá ČNB jen fakt registrace. Strategie je deklarace správce, kterou ČNB neověřuje [G1-A3].
3. **K3 dokládají hlavně volně dostupná média a tiskové zprávy startupů.** Databáze investic (CC+, Dealroom, OpenVC) jsou placené nebo licenčně nepoužitelné pro automatické čtení.
4. **AUM českých VC veřejně spolehlivě není.** Pole „AUM“ v CVCA míchá různé údaje [G2-A19–A22], takže půjde většinou o `ambiguous` nebo `not_public`.
5. **Archivace citací je nutná.** Obchodní rejstřík přejde na nový portál [G1-A1], CzechCrunch dočítá další články a Dealroom má v metadatech `noarchive` [G2-A9, nejisté]. Archivace je zatím odložena do dokončení pilotu ([ověřovací postup](overovaci-postup.md)).
6. **Původ kandidátů:** v kroku 5 vznikne tabulka `candidates.csv`, kde bude u každého nálezu kandidáta zdroj z katalogu, URL, datum a způsob nalezení (data/sources/README.md). Návrh je schválený, zavede se s pilotem jako doplnění datového modelu.

## 6. Revize dosavadních výsledků

Výsledky jsem znovu prošel skriptem i ručně, bez nového průzkumu. Co jsem opravil nebo označil:

**Citace (14 nedoslovných z první části kroku 3):**

- **9 ověřeno proti stránkám uloženým v záznamech běhů:**
  - 4 zkrácené výpustkou, každá část je na stránce doslova [G2-D12, D13, D23, D24],
  - 2 markdown odkazy [G2-E4, E6],
  - 1 se zpětnými apostrofy [G3-C25],
  - 2 z PDF, které Firecrawl při novém čtení přečetl zkomoleně [G1-A20, A21].
- **5 je nejistých:**
  - 2 text jen v metadatech stránky [G2-D6, A9],
  - 2 jen cíl odkazu na soubor [G2-C9, C10],
  - 1 rozdíl ve formátování [G3-C23].

  Závěry, které se o ně opírají, jsou označené: `noarchive` u Dealroomu, statistiky CVCA „nejnověji za rok 2022“ doložené jen názvy souborů, limity Tech.eu, které auditor v kontextu potvrdil.

**Další opravy:**

- **Opravy auditora** (23 tvrzení `CORRECTED`) jsou zapracované v katalogu. Tvrzení `NOT_SUPPORTED` (datum u členů CVCA [G2-C8]) se nepoužívá.
- **Tvrzení, která auditor nemohl ověřit** (výpis Dealroomu [G2-D7–D10], marketingová stránka OpenVC [G4-C6–C10]), se používají jen jako vlastní tvrzení provozovatele a jsou tak označená.
- **ČNB JERRS:** dvě hodnocení odkazovala na důkazy z jiného zdroje (číselník WS JERRS). Opraveno na vlastní důkazy JERRS.
- **Struktura:** jedna spolehlivost na zdroj nestačila. Proto vznikla tabulka `uses.csv`, kde má hodnocení každé použití zdroje zvlášť.
- **Kredity:** v minulé verzi jsem jen odhadl, že spotřebu způsobila hlavně PDF. Teď je to změřené ze záznamů běhů (kap. 7).
- **Kontrola konzistence (skript):** každé použití má existující důkazy a žádné se neopírá jen o nejisté nebo neověřené. Jediná výjimka: „vlastní web investora nesplní K3“ plyne přímo z metodiky (plan.md 5) a je tak označená.

## 7. Náklady

- **Agenti celkem 24,53 USD:**
  - průzkumníci 9,93 USD,
  - auditoři 14,60 USD,
  - z toho doladění (CEE Funding Map, OpenVC) 3,41 USD.
- **Firecrawl celkem 491 kreditů:** první část kroku 3 spotřebovala 481, doladění 10. V tarifu Free zbývá 448 kreditů do 2026-11-12.
- **Měření ze záznamů agentů:**
  - **Jediné PDF**, 81stránková uživatelská příručka otevřených dat obchodního rejstříku, stálo pokaždé 81 kreditů. Četli ho průzkumník, auditor i kontrolní skript, celkem **asi 243 kreditů, polovina spotřeby**.
  - **Další PDF** stála zhruba 70 kreditů (popis rozhraní ČNB, 17 stran, čtený několikrát).
  - **Běžné stránky** stojí 1 kredit.
- **Doporučení:**
  - velká PDF číst jen jednou a sdílet výsledek,
  - u PDF zvážit omezení počtu stran,
  - agenty pouštět za sebou kvůli limitu zhruba 10 požadavků za minutu.

## 8. Rozhodnutí a otevřené otázky

**Rozhodnuto 2026-10-16:**

1. **Struktura katalogu:** tři tabulky (`catalog.csv`, `uses.csv`, `evidence.csv`), viz data/sources/README.md.
2. **Zdroje s omezujícími podmínkami použití:**
   - Czechia Dealroom, OpenVC, CEE Funding Map a databáze CC+ se používají jen ručně a interně a agenti se na ně neposílají.
   - Data se z nich nepřebírají v rozporu s podmínkami. Kandidát odtud se vždy dokládá jinými zdroji.
3. **Původ kandidátů:** tabulka `candidates.csv` se zavede v kroku 5 (pilot).
4. **Nejisté citace** (kap. 6) zůstávají v `evidence.csv` označené a závěry se o ně samostatně neopírají.

**Otevřené otázky** (nemusí se řešit hned):

1. **Pokrytí ČR v CEE Funding Map** je neověřené, protože odkaz vede na mapu „funds-poland“.
2. **Komerční užití dat obchodního rejstříku:** podmínky si odporují. Případně písemný dotaz na MSp (dataor@msp.justice.cz).
3. **Seznam správců podle § 15 ve WS JERRS:** případně ověřit dotazem na ČNB (jerrsws@cnb.cz).

## 9. Ještě neprověřeno

Tyto zdroje jsou zatím jen stopy, bez dokladů:

- registry ESMA (správci EuVECA),
- GLEIF,
- evidence skutečných majitelů,
- nový portál veřejného rejstříku,
- úřední znění ZISIF v e-Sbírce,
- katalog otevřených dat ARES,
- zprávy EBAN o českých andělích,
- Ambit VC Deals Report,
- angel sítě (Keiretsu Forum Prague, Garage Angels, LUMUS, Business Angels Czech),
- JIC,
- Czech Founders,
- připravovaný státní Venture fond pod NRI,
- Seedtable,
- databáze investorů CzechCrunch,
- podmínky platformy PamPam,
- ceník OpenVC.
