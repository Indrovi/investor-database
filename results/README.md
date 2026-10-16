# Krok 6: ruční audit a měření přesnosti pilotu

> **Stav:** hotovo (2026-10-16).
> - **Ruční kontrola:** autor osobně zkontroloval 10 údajů ve dvou kolech. **Podle ruční kontroly bylo správných 8 z 10.** Kontrola AI se s ruční kontrolou shodla v 10 z 10.
> - **Audit celkem:** našel 6 chyb a 1 nejistotu (kap. Souhrn).
> - **Data:** audit a měření se vztahují k datům před opravami (commit `c96c21e`). Chyby jsou v `data/sample/` opravené v kroku 8, nejistý Vistag zůstává označený a mezi doložené investice se nepočítá (kap. Stav oprav).
> **Data:** [data/sample/](../data/sample/) · **Otevřené otázky z kroku 5:** [data/sample/README.md](../data/sample/README.md) · **Pravidla:** [plan.md](../docs/plan.md)

## Soubory

| Soubor | Obsah |
|---|---|
| [audit_pilot.csv](audit_pilot.csv) | auditní tabulka: 122 kontrolovaných údajů pěti zařazených investorů (původní hodnota, zdroj, automatická kontrola, kontrola AI, nalezená chyba či nejistota, navržená oprava, ruční ověření) |
| [audit_triaz.csv](audit_triaz.csv) | vzorek 5 kandidátů vyřazených při triáži |
| [rucni_kontrola.csv](rucni_kontrola.csv) | ruční kontrola 10 údajů (2 kola): odkaz, co najít na stránce, otázka, odpověď a poznámka autora (ANO / NE / NEDOKÁŽU URČIT) |
| [presnost.csv](presnost.csv) | počty a podíly s 95% intervaly |
| [kontrola_citaci.txt](kontrola_citaci.txt) | záznam automatické kontroly doslovnosti všech citací |
| [odhad_svet.csv](odhad_svet.csv) | **krok 7:** vstupy odhadu pro celý svět (zdroje s citacemi, měření pilotu, předpoklady), výsledek v [plan.md, kap. 13](../docs/plan.md#13-odhad-pro-celý-svět-krok-7) |

Vše vygeneroval `python3 scripts/pilot/audit.py --online` nad daty z commitu `c96c21e`; odpovědi autora se při opakovaném spuštění zachovají. **Po opravách v kroku 8 se audit nad aktuálními daty znovu nespouští:** výsledky by se míchaly s opravenými hodnotami a ID citací se posunula. Pro reprodukci je potřeba vrátit `data/sample/` na commit `c96c21e`.

## Úrovně ověření

Audit rozlišuje tři úrovně a výsledek jedné úrovně se nevydává za jinou.

| Úroveň | Kdo nebo co | Co ověřuje |
|---|---|---|
| **Automatická kontrola** | `validate.py`, `pilot/verify_quotes.py` | formální pravidla (K1–K3, stavy, číselníky, duplicity), doslovnost citací |
| **Kontrola AI (koordinátor)** | hlavní relace Claude Code, bez nových agentů | zda citace v kontextu původního zdroje opravdu dokládá zapsanou hodnotu, přiřazení investice, typ, datum, částky |
| **Rozhodnutí sporů (AI podle metodiky)** | koordinátor | odborné otázky (právní struktury, K2, hodnocení, typ) podle plánu a dostupných důkazů; co nejde spolehlivě určit, je zapsané jako nejistota |
| **Ruční kontrola (člověk)** | autor | faktická kontrola vybraných údajů přečtením původní stránky, bez odborného posouzení |

Kontrolu AI dělá stejná rodina modelů jako agenti, kteří data vytěžili. **Není nezávislá a nenahrazuje lidský audit.** Její výsledky jsou předběžné a slouží k výběru toho, co má posoudit člověk.

## Pravidla zapsaná před auditem (2026-10-16)

1. **Rozsah:** 5 zařazených investorů (INV-0001 až INV-0004, INV-0011), jejich sloučené právnické osoby (E10), fondy a investice. Jeden řádek auditu je jeden kontrolovaný údaj.
2. **Vzorek vyřazených kandidátů:**
   - Ze 17 kandidátů vyřazených při triáži jako `mimo pilot: typ podle zdroje` se vybere 5 s nejnižším SHA-256 z textu `audit-triaz-2026-10-16|jméno`.
   - Credo a Presto se nevybírají, protože nebyly vyřazené kvůli typu.
3. **Ruční kontrola člověkem:**
   - **Původně** (zapsáno před auditem): 12 řádků z těch, které kontrola AI vyhodnotila jako OK, s nejnižším SHA-256 z textu `audit-rucni-2026-10-16|ID řádku`.
   - **Změna 2026-10-16, na pokyn autora a před jakoukoli ruční kontrolou:** odborné otázky rozhoduje AI podle metodiky a člověk kontroluje jen fakta na stránce.
   - Vybírá se ze **všech** řádků bez ohledu na verdikt AI, tedy ne jen ze snadných nebo bezchybných.
   - Vybírají se jen typy údajů, které jde ověřit přečtením jedné stránky: sídlo, zaměření, ticket, velikost fondu, investor u investice, datum a částka.
   - Zůstává stejný seed a pořadí, nejdřív se kontroluje prvních 5. Výběr hlídá `audit.py`.
   - **2. kolo (na pokyn autora):** jeden údaj pro každého z pěti investorů. U každého se vezme první dosud nekontrolovaný údaj stejného typu podle stejného pořadí SHA-256.
4. **Měření přesnosti:** viz níže. Přesnost údajů se počítá jen z ručně zkontrolovaných položek. Ukazatele, které vycházejí z kontroly AI, jsou tak označené.

## Výsledky automatické kontroly a kontroly AI

**Automatická kontrola:**

- **Validátor:** 0 chyb (jen varování o chybějící archivaci).
- **Doslovnost citací:** 142/142. Z toho 116 proti živé stránce a 26 proti kopii, kterou Firecrawl vrátil agentovi.
- **Vzorek triáže:** 5/5 citací doslovně.

**Kontrola AI a rozhodnutí sporů podle metodiky, 122 údajů:**

| Oblast | Údajů | OK | OK s výhradou | Chyba | Nejistota |
|---|---|---|---|---|---|
| Profil investora (K1–K3, typ, sídlo, web, zaměření, ticket, AUM, hodnocení, aktivita) | 70 | 53 | 14 | 3 | 0 |
| Fondy | 8 | 6 | 2 | 0 | 0 |
| Investice (přiřazení a nástroj; datum a částky) | 36 | 29 | 3 | 3 | 1 |
| Sloučení právnických osob (E10) | 8 | 2 | 6 | 0 | 0 |
| **Celkem** | **122** | **90** | **25** | **6** | **1** |

„OK s výhradou“ znamená, že údaj odpovídá zdroji nebo metodice, ale má drobné omezení nebo nejistotu, která výsledek nemění. Jsou to například nepotvrzené právní struktury nebo přibližný převod do číselníku.

**Rozhodnutí sporů podle metodiky** (podrobně ve sloupci „Rozhodnutí sporu“ v `audit_pilot.csv`):

| Spor | Rozhodnutí | Co nejde spolehlivě určit |
|---|---|---|
| Q1 NRI, hodnocení | **B místo A**: obě publikace přebírají totéž prohlášení Hardwaria | jak metodika počítá více publikací téhož prohlášení (doplnit v kroku 8) |
| Q1 NRI, typ | VC, subtype public (menšinové podíly v rostoucích firmách, plan.md 4.1) | kotované firmy na trhu START, metodika nemá samostatný typ |
| Q2 Rockaway, K2 | doloženo na úrovni týmu, AMISTA spravuje jen feeder | formální GP a případný AIFM lucemburského fondu |
| Q3 Tilia a Orbit, K2 a E10 | doloženo na úrovni týmu, české společnosti týmů sloučené | registrace GP lucemburských fondů, role společností vůči fondům |
| Q4 StartupYard, Vistag | **nejistota**, doporučení do K3 nepočítat (zdroj je v budoucím čase) | zda investice proběhla |
| O1 Orbit, geografie | **chyba**: má být CEE a DACH (novější zdroj tier 2) | – |
| O2 Orbit, Mews a Preply | **chyba**: přiřazení k fondu bez zdroje | – |
| O3 StartupYard, sektory | **chyba**: zdroje si odporují a novější nejde určit, správně `conflicting` | – |
| O4 Rockaway, Spotawheel | **chyba**: dluh dodaly banky a úvěrové instituce, správně kapitálová investice bez uvedené formy | – |

**Dopad oprav:** po opravách by všech 5 investorů zůstalo zařazených. Změnilo by se:
- hodnocení NRI (A → B),
- počet doložených investic: StartupYard 3 → 2, Rockaway 3 → 4,
- údaje uvedené u chyb výše.

**Vzorek vyřazených při triáži:** Innova Capital, Abris Capital, CVI, Sandberg Capital, Thein.

- **Výsledek kontroly AI:** všech 5 je podle vlastního popisu nebo profilu v CVCA PE fond nebo poskytovatel dluhového financování. Vyřazení je správné.
- **Pilotní filtr:** 4 z 5 by ho nesplnily ani kvůli sídlu týmu (Varšava, Bratislava).

## Co osobně ověřil autor

Autor (člověk) ručně zkontroloval **10 údajů ze 122** (12 otázek) 2026-10-16. **Nic dalšího člověk neověřoval.**

- **Jak:** otevřel původní stránku a na faktickou otázku, co na ní stojí, odpověděl ANO, NE, nebo NEDOKÁŽU URČIT.
- **Co neověřoval:**
  - odborné závěry (K1–K3, typ, hodnocení, sloučení E10, rozhodnutí sporů),
  - zbylých 112 údajů,
  - vzorek vyřazených při triáži.

  To všechno ověřila jen AI.
- **Kde je to zapsané:**
  - odpovědi a poznámky autora jsou v [rucni_kontrola.csv](rucni_kontrola.csv),
  - v [audit_pilot.csv](audit_pilot.csv) má ruční výsledek 10 řádků (sloupec „Ruční ověření (člověk)“), ostatní mají „neověřeno“.
- **Výsledek u K1 a K2** vzniká použitím pravidel metodiky na odpovědi autora:
  - **K1:** zdroj fond neuvádí (K1b NE), takže přiřazení k fondu je bez zdroje.
  - **K2:** starší profil uvádí jen CEE (K2a ANO) a novější zdroj tier 2 i DACH (K2b ANO). Podle plan.md 9 platí novější zdroj. Hodnota v databázi odpovídá citovanému profilu, ale není aktuální.
- **Úplně naslepo kontrola nebyla.**
  - Soubor pro autora neobsahoval hodnotu z databáze ani očekávanou odpověď.
  - Otázky ale uváděly, jaký text na stránce hledat.
  - U K1 a K2 autor předem znal závěr kontroly AI: souhrn rozhodnutí sporů byl ve stejné zprávě jako otázky.
- **Otázky připravila AI.** Autor kontroloval jen odkázanou stránku a další zdroje nehledal. Chybu typu K2 by ruční kontrola bez odkazu na novější zdroj neodhalila.

## Výsledky ruční kontroly (člověk, 2026-10-16)

| ID | Investor | Kontrolovaný údaj | Odpovědi autora | Výsledek | Kontrola AI |
|---|---|---|---|---|---|
| K1 | Orbit Capital | Preply: investor a přiřazení k fondu | a) ANO, b) NE | **chyba:** investice doložená, fond Orbit Growth zdroj neuvádí | chyba (shoda) |
| K2 | Orbit Capital | investiční geografie | a) ANO, b) ANO | **chyba:** databáze má jen CEE podle staršího profilu, novější zdroj (tier 2, 2026) uvádí i DACH | chyba (shoda) |
| K3 | Rockaway Ventures | země (Praha) | ANO | odpovídá | OK s výhradou (shoda) |
| K4 | Rockaway Ventures | velikost 2. fondu (~55 mil. EUR) | ANO | odpovídá | OK s výhradou (shoda) |
| K5 | NRI | Hardwario: datum a investor | ANO | odpovídá | OK (shoda) |
| K6 | Tilia Impact Ventures | MIWA Technologies: datum a investor | ANO | odpovídá | OK (shoda) |
| K7 | Rockaway Ventures | Remix: datum a podíl | ANO | odpovídá | OK (shoda) |
| K8 | StartupYard | město (Praha) | ANO | odpovídá | OK (shoda) |
| K9 | NRI | Primoco UAV: nákup přes IPO fond | ANO | odpovídá | OK (shoda) |
| K10 | Orbit Capital | země týmu (Czech Republic) | ANO | odpovídá | OK (shoda) |

**Poznámky autora a jak se promítají:**

- **K1b:** autor poznamenal, že investice z fondu Orbit Growth jít mohla.
  - Chyba proto není v tom, že by šlo o jiný fond, ale v přiřazení, které zdroj nedokládá.
  - Oprava: fond se nechá prázdný (neznámý), nepřiřadí se jiný.
- **K4:** zdroj uvádí „necelých“ 55 mil. EUR, tedy přibližnou částku.
  - V databázi je 55 000 000 EUR bez příznaku přibližné hodnoty, protože model ho nemá. Kontrola AI to vedla jako výhradu.
- **K5:** 18. 10. 2022 je datum zveřejnění článku, ne nutně datum investice.
  - V databázi je datum vedené jako datum oznámení (`date_basis = announcement`), údaj tedy odpovídá.
  - Přehled `investori_prehled.csv` ale druh data neuvádí.

## Měření přesnosti

**Ověřeno ručně autorem:**

| Ukazatel | Počet | Podíl | 95% interval |
|---|---|---|---|
| **Údaj v databázi je podle ruční kontroly správný** | 8/10 | 80 % | 49–94 % |
| **Verdikt kontroly AI (OK / chyba) se shoduje s ruční kontrolou** | 10/10 | 100 % | 72–100 % |

**Ověřeno jen AI** (předběžné, není to přesnost ověřená člověkem):

| Ukazatel | Počet | Podíl | 95% interval | Ručně z toho |
|---|---|---|---|---|
| Údaje bez chyby a bez nejistoty | 115/122 | 94 % | 89–97 % | 10 údajů (výše) |
| Zařazení investoři splňují K1–K3 a typ | 5/5 | 100 % | 57–100 % | nic |
| Hodnocení spolehlivosti A/B správně | 4/5 | 80 % | 38–96 % | nic |
| Doložené investice (K3) se správným investorem, firmou, nástrojem a datem | 13/14 | 93 % | 69–99 % | 4 (Preply, Hardwario, MIWA, Remix), všechny správně |
| Přiřazení investice k fondu doloženo zdrojem | 3/5 | 60 % | 23–88 % | 2 (Preply chyba, Primoco UAV správně) |
| Vyřazení při triáži správné | 5/5 | 100 % | 57–100 % | nic |

**Jak číst ukazatele:**

- **Výpočet:** intervaly jsou 95% intervaly spolehlivosti podle Wilsona, podrobně v [presnost.csv](presnost.csv).
- **Kontrola metrik (2026-10-16):** všechny počty jsou nezávisle přepočítané přímo z `audit_pilot.csv`, `rucni_kontrola.csv` a z validátoru (doložené investice). Shodují se s `presnost.csv` i s touto stránkou.
- **Doložené investice:** jediná nevyhovující je Vistag (nejistota). Opačnou chybu ukazatel nezachytí: Spotawheel se do K3 nepočítal, i když měl.
- **Zařazení:** výsledek stojí na rozhodnutí sporů AI a na nejistotách k právním strukturám (kap. Souhrn).

## Co z výsledků plyne

1. **Citované údaje odpovídají zdrojům.**
   - Všech 8 ručně zkontrolovaných údajů, které kontrola AI hodnotila jako OK, autor potvrdil.
   - Automatická kontrola našla doslovně všech 142 citací.
2. **Chyby vznikají při vyvozování ze zdrojů, ne v citacích.** Všech 6 chyb je v rozhodnutích koordinátora zapsaných v `scripts/pilot/decisions.py`:
   - přiřazení k fondu bez zdroje (2×),
   - starší profil použitý místo novějšího zdroje (1×),
   - výběr jedné ze dvou rozporných hodnot (1×),
   - příliš opatrná klasifikace nástroje (1×),
   - dvě publikace téhož prohlášení počítané jako dva důkazy (1×).
3. **Ruční kontrola potvrdila nálezy AI.**
   - U obou chybných údajů chybu předtím našla i kontrola AI.
   - Žádný údaj, který AI hodnotila jako OK, se neukázal jako chybný.
   - Otázky ale připravila AI se znalostí svých nálezů. Shoda 10/10 proto ukazuje hlavně, že nálezy AI odpovídají stránkám, ne že AI najde všechny chyby (dolní mez 72 %).
4. **Ruční vzorek měl víc chyb (2 z 10) než celý audit podle AI (6 ze 122).**
   - Mezi 72 údaji ověřitelnými z jedné stránky je 5 chyb a výběr dva z nich zachytil.
   - Při 10 údajích to neznamená, že chyb je víc, ale nelze to ani vyloučit.

## Souhrn: chyby, nejistoty a doporučené opravy

### Doložené chyby (6)

| Řádek auditu | Investor | Chyba | Ručně ověřeno | Doporučená oprava | Dopad |
|---|---|---|---|---|---|
| INV-0011/geografie | Orbit Capital | jen CEE, novější zdroj tier 2 (2026) uvádí i DACH | ano (K2) | `geographies` CEE;DACH, citace Alternative Credit Investor (2026) | – |
| DEAL-0018 | Orbit Capital | Preply přiřazený k fondu Orbit Growth SCSp bez zdroje | ano (K1) | `fund_id` prázdné | – |
| DEAL-0017 | Orbit Capital | Mews přiřazený k fondu Orbit Growth SCSp bez zdroje | ne | `fund_id` prázdné | – |
| INV-0003/sektory | StartupYard | zapsaný jeden ze dvou rozporných vlastních zdrojů, FAQ nemá datum | ne | `sectors` prázdné, `sectors_status = conflicting`, citace obou zdrojů | – |
| DEAL-0009 | Rockaway Ventures | Spotawheel jako `unclear`, i když dluh dodaly banky a Rockaway je mezi investory kola | ne | `instrument = investment_unspecified` | Rockaway 3 → 4 doložené investice |
| INV-0004/hodnocení | NRI | hodnocení A, i když obě publikace přebírají totéž prohlášení Hardwaria | ne | hodnocení B (jeden původ důkazu) | – |

### Nejistoty (upozornění zůstávají, nic se nedomýšlí)

- **Vistag (DEAL-0012):** nelze určit, zda investice proběhla.
  - Citace je v budoucím čase („získají investici“), titulek v minulém.
  - Doporučení: do K3 nepočítat (citaci investice odebrat, záznam ponechat s poznámkou). StartupYardu pak zůstanou 2 doložené investice a hodnocení A trvá.
- **Právní struktury lucemburských fondů:**
  - Nejistý je formální GP a případný AIFM u Rockaway Ventures Fund SCSp, Tilia Impact Ventures II a Orbit Growth SCSp.
  - U Tilie není známý vehikl fondu I.
  - K2 je doložené na úrovni týmu.
- **Role sloučených právnických osob (E10) vůči fondům** u Tilie, Rockaway a Orbitu. Sloučení je podle bodu 3 ověřovacího postupu, přesná role doložená není.
- **StartupYard, vehikl 15. kola:** vlastní ho osobně ředitel. Nelze určit, zda jedná jen za StartupYard.
- **NRI, typ VC:** hraniční, protože jde o úpisy na trhu START a metodika pro ně samostatný typ nemá.
- **Přibližné nebo částečné hodnoty:**
  - Fond Rockaway má „necelých“ 55 mil. EUR, zapsáno je 55 000 000.
  - Kolo Mews (185 mil. USD) obsahuje i malou dluhovou část.
  - U Lifeyear je zapsaná jen kapitálová část kola.
  - U Remixu může jít zčásti o odkup podílu.
  - Datum fondu Orbit (2021-12) je odvozené z „last December“.
  - Ticket StartupYardu (25 000 EUR) je volitelná hotovostní část programu.
- **Přibližné převody do číselníku sektorů:**
  - Rockaway: defence → deeptech_hardware; tech.eu 2025 navíc uvádí nové zaměření.
  - Orbit: technology-enabled → software_saas.
  - Tilia: impact zaměření číselník nevyjádří.
- **Datum investice je datum oznámení** (`date_basis = announcement`), ne datum uskutečnění. Přehled `investori_prehled.csv` to zatím neuvádí.

### Stav oprav (krok 8, 2026-10-16)

Opravy jsou zapsané v oddílu „Opravy podle auditu“ v `scripts/pilot/decisions.py`. Data jsou znovu sestavená, validace a kontrola citací prošly (143/143) a přehled je znovu vygenerovaný.

| Řádek auditu | Stav |
|---|---|
| INV-0011/geografie | opraveno: CEE a DACH, nová citace Alternative Credit Investor |
| DEAL-0017, DEAL-0018 | opraveno: bez přiřazení k fondu |
| INV-0003/sektory | opraveno: `conflicting`, nová citace stránky o 15. kole |
| DEAL-0009 (Spotawheel) | opraveno: `investment_unspecified`, Rockaway 4 doložené investice |
| INV-0004/hodnocení | opraveno: ČTK jako převzetí jen v poznámce, NRI hodnocení B |
| DEAL-0012 (Vistag) | **nejisté:** záznam ponechán s poznámkou „NEJISTÉ“, mezi doložené investice se nepočítá (citace v budoucím čase dokládá jen datum oznámení). StartupYard má 2 doložené investice a hodnocení A |

**Upřesnění:** u nálezu INV-0003/sektory je jako zdroj „AI, cybersecurity, IoT“ uvedeno FAQ. Citace je ve skutečnosti z úvodní stránky startupyard.com. Výsledek nálezu se tím nemění.

**Podněty pro revizi plánu (krok 8):** pravidlo nezávislosti publikací je doplněné do plan.md 6.3, ostatní jsou zapsané jako omezení v plan.md, kap. 14.

- **Příznak přibližné hodnoty** u velikosti fondu a částek (K4).
- **Druh data v přehledu:** oznámení vs. uskutečnění investice (K5).
- **Pravidlo, kdy jsou dvě publikace nezávislé:** NRI.
- **Přiřazení k fondu jen se zdrojem:** pravidlo i kontrola ve validátoru.

## Omezení

- **Malý vzorek:** 5 investorů, 122 údajů, 14 doložených investic. Interval spolehlivosti je široký: například 5/5 dává 95% interval zhruba 57–100 %.
- **Kontrola AI není nezávislá.** 112 ze 122 údajů ověřila jen AI.
- **Ruční kontrolu udělal jeden člověk** (autor) na 10 údajích. Ověřoval jen fakta na odkázané stránce, ne odborné závěry (K1–K3, typ, hodnocení, sloučení E10).
- **Otázky připravila AI** a u K1 a K2 autor znal závěr AI předem (kap. Co osobně ověřil autor).
- **Odborná rozhodnutí sporů dělá AI.** Nejistoty jsou zapsané, nezávislé odborné posouzení neproběhlo.
- **Vzorek investorů je rozvrstvený podle zdrojů,** ne reprezentativní pro všechna česká VC.
- **Vzorek vyřazených pokrývá 5 ze 17** a ověřila ho jen AI, chybné vyřazení tedy nelze vyloučit.
- **Úplnost (recall) se neměří.** Pilot nemá nezávislý úplný seznam českých VC.
