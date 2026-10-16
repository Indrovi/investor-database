# Plán: Spolehlivá databáze investorů

> **Stav:** pracovní verze. Krok 2 ([datový model](datovy-model.md)), krok 3 ([mapa zdrojů ČR](zdroje-cr.md)) a krok 4 ([ověřovací postup](overovaci-postup.md)) jsou hotové, stejně jako pilot (krok 5), měření přesnosti (krok 6) a odhad pro celý svět (krok 7, kap. 13). U kroku 1 (pravidla zařazení a vyřazení) zbývá potvrdit hraniční případy (kap. 9) a GDPR (kap. 6.5).
> **Poslední úprava:** 2026-10-16
> **Zadání:** [docs/zadani.md](zadani.md)

## 1. Účel databáze

Databáze slouží k tomu, aby šlo k investičnímu projektu rychle najít investory, kteří do podobných projektů **skutečně investují**. U každého investora proto musí být doloženo:

1. že jde o **skutečného investora**,
2. **do čeho** investuje (sektory, fáze, typ investic, geografie),
3. **kolik** investuje (ticket size) a jaký má **celkový investiční kapitál** (AUM). Ten se nezaměňuje s velikostí jednotlivých fondů (viz 10.1),
4. zda **stále investuje** (activity status),
5. **odkud** každá informace pochází (zdroj a datum).

Metodika je navržená tak, aby šla použít **celosvětově**. Pilotně se ověří na **českých VC investorech**. Používají se **výhradně veřejně dostupná data**.

## 2. Postup realizace

| Krok | Obsah | Výstup | Stav |
|---|---|---|---|
| 0 | Struktura repozitáře a konvence | README, `.gitignore`, adresáře | hotovo |
| 1 | Kdo je a kdo není investor | kapitoly 3–11 tohoto dokumentu | **téměř hotovo**, zbývá potvrdit kap. 9 a 6.5 (viz kap. 12) |
| 2 | Datový model s doložením původu každého údaje (data provenance) | [datovy-model.md](datovy-model.md), `scripts/validate.py`, testy a fiktivní příklady | **hotovo** |
| 3 | Mapa veřejných zdrojů a spolehlivosti dat (pro ČR) | [zdroje-cr.md](zdroje-cr.md), katalog `data/sources/` | **hotovo** (celosvětový odhad počtu investorů přesunut do kroku 7) |
| 4 | Ověřovací postup (verification protocol) | kap. 6.6 a [checklist](overovaci-postup.md) | **hotovo** |
| 5 | Pilot: české VC | `data/sample/`, přehled `investori_prehled.csv`, skripty `scripts/pilot/` | **hotovo**: 5 unikátních investorů, všichni zařazení; otevřené otázky pro krok 6 v [data/sample/README.md](../data/sample/README.md) |
| 6 | Ruční ověření a měření přesnosti | [results/](../results/README.md) | **hotovo**: autor ručně zkontroloval 10 údajů (8/10 správně, kontrola AI se shoduje 10/10); 6 chyb a 1 nejistota, opravy dat odložené do kroku 8 |
| 7 | Závěrečná analýza: odhad počtu investorů a nákladů na rozšíření na celý svět | kap. 13 a [results/odhad_svet.csv](../results/odhad_svet.csv) | **hotovo** (revidováno): ověřitelných asi 14 600 organizací (8 600–20 500) a 29 500 fyzických osob (velmi nejisté); prvotní ověření asi 0,41 mil. USD za organizace, 1,7 mil. USD za vše |
| 8 | Revize plánu podle pilotu a finalizace | finální `docs/plan.md` | plánováno; zapracovat opravy dat a podněty z auditu ([results/](../results/README.md#souhrn-chyby-nejistoty-a-doporučené-opravy)) |

---

## 3. Definice investora

**Investor je firma nebo člověk, který sám rozhoduje, do čeho investuje, a o kterém lze veřejně doložit, že do nějaké firmy skutečně investoval.**

Upřesnění:

- **Investice** znamená vložení kapitálu do firmy výměnou za equity nebo quasi-equity: obchodní podíl, akcie, convertible loan nebo SAFE. Smyslem je finanční výnos. Za investici se nepovažuje úvěr bez možnosti konverze na podíl, grant, dotace, sponzoring ani služba.
- **Firma** je obchodní společnost, zpravidla nekótovaná. Investice do nemovitostí, infrastruktury nebo komodit se nepočítají.
- **„Sám rozhoduje“** znamená, že záznam patří subjektu, který má o investicích **rozhodovací pravomoc**. U fondů je to správce (management company, GP, investiční výbor), u člověka on sám. Investorem tedy **nejsou**:
  - samotná investiční vehikula (fond, SPV, feeder),
  - LP, kteří do fondu jen vkládají peníze a o jednotlivých firmách nerozhodují,
  - platformy a poradci.

### 3.1 Jednotka záznamu

Jeden záznam představuje **jeden investiční subjekt**, ne každý jeho fond zvlášť. *(Rozhodnuto.)*

- Fondy (Fund I, II, SPV, feeder) jsou **atributy záznamu**. Eviduje se u nich jejich vlastní velikost (fund size) a slouží k doložení investic. AUM investora se z nich automaticky nepočítá (viz 10.1).
- Přejmenované nebo sloučené subjekty mají jeden záznam se seznamem dřívějších názvů (aliasy).
- Osobní holding fyzické osoby bez investičního týmu je součástí záznamu této osoby.
- Partner VC fondu, který investuje i soukromě, může mít vedle záznamu fondu ještě vlastní záznam jako business angel nebo large private investor (podle 4.3).

---

## 4. Typy investorů

Základní typy (primary types) vycházejí ze zadání. *(Rozhodnuto.)*

| Typ | Definice |
|---|---|
| **VC** | Profesionální investiční subjekt. Kupuje převážně **minoritní podíly v mladých, rychle rostoucích firmách** (pre-seed až late stage, growth). |
| **Private Equity (PE)** | Profesionální investiční subjekt. Kupuje převážně **většinové (kontrolní) nebo významné podíly v zavedených firmách** (buyout, MBO/MBI, konsolidace, growth s kontrolou). |
| **Family Office (FO)** | **Organizace s vlastním investičním týmem**, která spravuje majetek jedné osoby či rodiny (single) nebo více rodin (multi) a investuje **přímo do firem**. |
| **Business Angel** | **Fyzická osoba**, která investuje vlastní peníze převážně do **startupů v rané fázi**, s menšími tickety a minoritními podíly. |
| **Large Private Investor** | **Fyzická osoba** (přímo nebo přes vlastní holding bez investičního týmu), která investuje vlastní peníze ve **výrazně větším objemu** nebo do **zavedených firem**. |

### 4.1 Jak určit typ investora

Kroky se procházejí v tomto pořadí. Rozhoduje první, který sedí.

1. **Je to fyzická osoba** (přímo, nebo přes vlastní holding bez investičního týmu)? → Business Angel, nebo Large Private Investor (viz 4.3).
2. **Je to organizace s investičním týmem, která spravuje majetek jedné osoby, rodiny nebo více rodin?** → Family Office. Rozhoduje, jak subjekt funguje, ne jak se jmenuje.
3. **Ostatní profesionální investiční subjekty** → VC, nebo PE podle charakteru **všech doložených investic** (definice v tabulce výše):
   - rozhoduje převažující charakter investic,
   - při shodě rozhodují novější investice,
   - pokud ani to nerozhodne, rozhoduje, jak se subjekt sám prezentuje.

**Žádný typ se nepřiřazuje automaticky.** Pokud typ z doložených podkladů určit nejde, záznam se nezařadí a zůstává v seznamu kandidátů (candidate queue). Viz kapitola 10.

### 4.2 Subjekty mimo pět základních typů (subtype)

Atribut `subtype` popisuje **formu subjektu** (korporátní, veřejný, akcelerátor…). Uživatel podle něj může filtrovat a nevznikají nové základní typy.

**Subtype nikdy neurčuje základní typ.** Ten se u všech subjektů určuje stejnými pravidly podle 4.1, tedy podle doložených investic. Žádná forma subjektu se tak automaticky nezařazuje pod VC. *(Rozhodnuto.)*

| Subjekt | `subtype` | Základní typ | Podmínka zařazení |
|---|---|---|---|
| **Corporate VC (CVC)**, korporátní fond velké firmy, např. Inven Capital ve skupině ČEZ | `corporate` | **VC** *(rozhodnuto)* | Investuje finančně do **minoritních podílů ve firmách mimo vlastní skupinu**, má samostatnou jednotku nebo deklarovaný investiční program. Akvizice firem do vlastní skupiny se nepočítají (E6). |
| Accelerator, venture studio | `accelerator` | podle 4.1, krok 3 | Investuje **vlastní kapitál** do equity, nejen služby a program. |
| Státní nebo veřejný investor (státní fondy, development banks) | `public` | podle 4.1, krok 3 | Investuje **přímo do firem**. Pokud funguje jen jako LP ve fondech → E7. |
| Instituce investující přímo (pension fund, pojišťovna, státní investiční fond SWF, crossover fund) | `institutional` | podle 4.1, krok 3 | Má doložené přímé investice do firem. |
| Angel fund (fond s centrálním rozhodováním) | `angel_fund` | podle 4.1, krok 3 | O investicích rozhoduje manažer nebo výbor fondu. |
| Multi-family office | `multi_family` | FO (4.1, krok 2) | Má doložené **přímé** investice do firem. Jinak E4 nebo E7. |
| Angel club, angel network | – | **není investor** | Členové rozhodují každý sám. Zařadit lze jednotlivé členy jako business angels, pokud mají vlastní doložené investice. |

**Korporátní fondy:** CVC se chovají jako VC. Rozhodují o investicích do startupů a kupují minoritní podíly. Hranici tvoří účel transakce: finanční investice ano, strategická akvizice do vlastní skupiny ne.

### 4.3 Hranice mezi Business Angel a Large Private Investor

Typ popisuje **investiční chování**, ne velikost majetku. Osoba je **Large Private Investor**, pokud z jejích doložených investic plyne, že investuje spíš jako institucionální investor než jako angel. Typicky:

- kupuje **většinové nebo kontrolní podíly**,
- investuje do **zavedených firem**, ne do startupů,
- sama pokrývá **celá kola** nebo jejich velkou část.

Jinak jde o **Business Angel**. Pokud osoba investuje přes holding s vlastním investičním týmem, nejde o fyzickou osobu, ale o Family Office (4.1, krok 2).

**Ticket kolem 500 000 EUR je jen orientační vodítko, ne automatické rozhodovací pravidlo.** *(Rozhodnuto.)*

- Typický ticket (medián doložených vlastních investic) zhruba od 500 000 EUR je **signál k posouzení**, ne rozhodnutí. Typ se nikdy neurčuje jen podle částky (4.1: žádný typ se nepřiřazuje automaticky).
- O typu rozhoduje člověk podle celkového obrazu doložených investic.
- Validátor typ podle ticketu neurčuje ani nekontroluje.

**Proč zrovna 500 000 EUR:** hranice vznikla jako odhad řádu. Následně se porovnala s veřejnými statistikami evropských angel asociací:

| Ukazatel | Hodnota | Zdroj |
|---|---|---|
| Běžná investice business angela do jedné firmy | **10 000–250 000 EUR** | [Business Angels Europe: A. What is a Business Angel?](https://www.businessangelseurope.com/professionalstandards/a.-what-is-a-business-angel%3F--), část „Investment strategy and Ticket size“ |
| Průměrný ticket jednoho angela v jednom kole (2024) | 25 600 EUR | [EBAN Statistics Compendium 2024](https://www.eban.org/wp-content/uploads/2025/12/Stats-Compendium-2024.pdf), s. 6 a 19 (Figure 11) |
| Průměrná investice angelů do jedné firmy, souhrnně za kolo (2024) | 204 900 EUR | EBAN 2024, s. 6 a 19 (Figure 11) |
| Průměrné kolo v kategorii angel rounds do 1 mil. EUR (2024) | ~410 000 EUR | EBAN 2024, s. 10 |
| Česko: 3 angel networks, 340 angelů, 70 investic, 15 mil. EUR (2024) | – | EBAN 2024, s. 16 |

Ticket 500 000 EUR od **jediné osoby** je:

- **dvojnásobek horní hranice** běžného rozpětí podle BAE,
- přibližně **20× průměrný ticket angela** podle EBAN,
- **2,4× víc, než všichni angelové v průměru dají do jedné firmy** (EBAN).

Taková osoba tedy sama pokryje celé typické angel kolo a chová se spíš jako institucionální investor.

**Omezení:**

- EBAN pracuje jen s viditelnou částí trhu (visible market) a sám uvádí, že data nejsou reprezentativní (s. 2–3). Stránka BAE neuvádí datum aktualizace (v patičce je jen © 2013). Hranici lze proto po pilotu upravit podle skutečně doložených ticketů.
- Pokud ticket není známý, rozhoduje se jen podle charakteru investic (podíly, fáze firem).
- Pro účel databáze je hranice méně důležitá, než se zdá. **Ticket size je samostatný údaj** a uživatel podle něj filtruje bez ohledu na typ.

---

## 5. Kritéria zařazení

Subjekt se zařadí, pokud splní **všechna tři kritéria**. Kritéria platí celosvětově, liší se jen konkrétní zdroje v jednotlivých zemích.

### K1: Jednoznačná identita

Cílem je, aby šel subjekt jednoznačně určit a nedošlo k záměně, například se subjektem stejného jména. **Úřední registr je nejsilnější doklad, ale není podmínkou**, protože u některých typů investorů nemusí existovat nebo být dostupný.

| Druh subjektu | Preferovaná identifikace | Náhradní cesta |
|---|---|---|
| Právnická osoba v ČR | IČO z ARES nebo obchodního rejstříku | – |
| Zahraniční právnická osoba | národní registr (Companies House, Handelsregister…), LEI z GLEIF, ID regulátora (např. SEC CRD) | shodná identifikace ve ≥1 nezávislém zdroji (název + web + sídlo + klíčové osoby) |
| Fondové struktury (SICAV, LP, fondy v Lucembursku apod.) | registr správce nebo regulátora (seznamy ČNB, ESMA, SEC) | identita správce přes nezávislé zdroje |
| Fyzická osoba (angel, large private investor) | **registr se nevyžaduje**. Stačí celé jméno a ≥2 další identifikační údaje z veřejných profesních zdrojů (role, firma, země, web). | Pokud osoba investuje přes vlastní holding, eviduje se i jeho IČO. |
| Značka bez dohledatelné právnické osoby (např. menší FO) | – | shodná identifikace ve ≥1 nezávislém zdroji |

**Úroveň identity** (atribut `identity_level`):

- **I1**: ověřeno v úředním registru,
- **I2**: ověřeno nezávislým zdrojem, protože registr neexistuje nebo pro daný subjekt nedává smysl,
- **I3**: jen vlastní tvrzení subjektu → **nestačí**.

Záznamy se **párují podle registračního čísla**, pokud existuje. Jinak podle kombinace název + doména webu + země + klíčové osoby.

### K2: Vlastní rozhodování o investicích

Subjekt sám rozhoduje, do čeho investuje (viz kapitola 3). Typicky to dokládá vlastní prezentace subjektu, úřední registr (subjekt je zapsaný jako správce či obhospodařovatel) nebo charakter doložených investic.

**K2 je povinná a eviduje se.** *(Rozhodnuto.)*

- Posouzení K2 se zapisuje jako citace `decision_authority`: zdroj (tier 1–3) a úryvek, ze kterého rozhodovací pravomoc plyne. U posouzení podle charakteru investic se postup popíše v poznámce citace.
- Dokud K2 posouzená není, investor se **nezařadí** a zůstává kandidátem. Validátor to kontroluje.
- Pokud posouzení ukáže, že subjekt sám nerozhoduje (LP, platforma, poradce), vyřadí se podle kapitoly 8.

### K3: Alespoň jeden kvalitní nezávislý důkaz investice

*(Rozhodnuto: stačí jeden kvalitní nezávislý důkaz. Počet investic není podmínkou zařazení.)*

**Nezávislý** zdroj je zdroj, který investor nemá pod kontrolou: úřední registr, portfoliová firma, co-investor, LP nebo médium s redakční prací. **Kvalitní** je, pokud splňuje vše z následujícího:

1. jednoznačně jmenuje **investora** i **firmu**, do které investoval,
2. popisuje **vložení kapitálu**, tedy ne partnerství, službu, úvěr ani grant. Pokud zdroj neuvádí formu investice, musí **výslovně** mluvit o investici, investorovi nebo podílu. Obecná zmínka o „poskytnutí financování“ nestačí *(rozhodnuto)*,
3. má **datum** (datum dealu nebo publikace),
4. má **dohledatelného vydavatele**,
5. je **veřejně dostupný bez přihlášení** a dá se archivovat.

**Investice, které se nepočítají:**

- **zakladatel investuje do vlastní firmy** (to je založení, ne investice),
- investice do firem **vlastní skupiny**,
- čistě **dluhové** financování,
- investice, u které **není jasné, zda jde o kapitálovou investici, nebo o půjčku** (např. zdroj píše jen „poskytl finance“). Eviduje se, ale jako důkaz investování se nepočítá. *(Rozhodnuto.)*
- investice doložená **jen zápisem společníka v obchodním rejstříku**. Zápis dokazuje vlastnictví podílu, ne investiční transakci (podíl mohl vzniknout třeba založením firmy nebo darem). Potřebný je další doklad transakce: související listina ze sbírky listin, nebo důvěryhodné oznámení (viz 6.4). *(Rozhodnuto.)*

**Vlastní zdroje investora** (web, portfolio stránka, tisková zpráva, rozhovor) jsou **doplňkové**. Slouží k popisu sektorů, fází, ticketu a AUM, ale **samy k zařazení nestačí**.

Riziko „náhodné firmy“ nehlídá požadavek na více investic, ale tři věci:

- kvalitativní podmínky na důkaz (body 1–5),
- výčet investic, které se nepočítají,
- pravidla vyřazení (kapitola 8).

Počet doložených investic se ukládá do atributu `documented_deals_count`. Uživatel tak hned vidí, zda jde o jednorázového, nebo opakovaného investora.

---

## 6. Důkazy a zdroje

### 6.1 Úrovně zdrojů (evidence tiers)

| Tier | Druh zdroje | Příklady | Použití |
|---|---|---|---|
| **Tier 1: úřední** | rejstříky, regulátoři, úřední listiny | obchodní rejstřík a sbírka listin (justice.cz), ARES, seznamy ČNB, Companies House, Handelsregister, SEC Form ADV a Form D, ESMA, GLEIF | identita, rozhodovací pravomoc, **důkaz investice** (samotný zápis společníka ale nestačí, viz 6.4) |
| **Tier 2: nezávislé** | strana dealu jiná než investor, redakční média | tisková zpráva portfoliové firmy, oznámení co-investora nebo LP (např. EIF), CzechCrunch, Hospodářské noviny, Forbes, TechCrunch, FT | **důkaz investice**, ticket, velikost fondů, AUM |
| **Tier 3: vlastní tvrzení** | zdroje kontrolované investorem | web, portfolio, investment thesis, výroční zpráva, rozhovor | sektory, fáze, ticket, velikost fondů, AUM (doplňkově) |
| **Tier 4: agregátory** | databáze a seznamy | Crunchbase, Dealroom, OpenVC, Wikipedia, **členské seznamy asociací (např. CVCA)**. Samotné členství má váhu Tier 4, profil dodaný členem má váhu Tier 3. | **jen pro hledání kandidátů**, nikdy jako důkaz |

### 6.2 Co se u každého důkazu zaznamenává

URL, vydavatel, tier, datum publikace, datum dealu (pokud se liší), datum přístupu, doslovná citace podporující údaj a archivní kopie (Wayback Machine). Podrobné schéma je v [datovy-model.md](datovy-model.md).

Že citace na uvedené stránce opravdu je, ověřuje skript `scripts/check_quotes.py` ([agenti.md](agenti.md), kap. 3). Archivní kopie zatím nevznikají: archivace je odložena do dokončení pilotu a validátor na chybějící kopii upozorňuje.

### 6.3 Hodnocení spolehlivosti záznamu (confidence grade)

| Hodnocení | Podmínka | Výsledek |
|---|---|---|
| **A** | K1 + K2 + **≥2** kvalitní nezávislé důkazy investice | zařazen |
| **B** | K1 + K2 + **1** kvalitní nezávislý důkaz | zařazen (minimum) |
| **C** | nesplní některé z K1–K3, typicky existují jen vlastní tvrzení nebo agregátory | **nezařazen**, zůstává v seznamu kandidátů (candidate queue) |

### 6.4 Specifika zemí

- **ČR:**
  - Obchodní rejstřík ukazuje **společníky s.r.o. včetně data zápisu**, a to i u fyzických osob. Zápis ale dokazuje **vlastnictví podílu, ne samotnou investici**. *(Rozhodnuto.)*
    - K3 vyžaduje **další doklad investiční transakce**, například související listinu ze sbírky listin (rozhodnutí o zvýšení základního kapitálu, smlouva o převodu podílu) nebo důvěryhodné oznámení (Tier 2).
    - Samotný zápis nezakládá ani stav `active` (7.1).
    - Rejstřík tak slouží hlavně k hledání kandidátů, k identitě (K1) a jako doplňkový doklad k investici, kterou dokládá jiný zdroj.
  - Akcionáři a.s. veřejní nejsou (kromě jediného akcionáře).
  - Investice přes convertible loan nebo SAFE se v rejstříku objeví až po konverzi.
  - Startupy se zahraničním holdingem (Delaware, UK) vyžadují Tier 2 zdroj nebo zahraniční registr.
- **Svět:** dostupnost veřejných seznamů společníků se liší. UK a Německo je zveřejňují, Delaware ne. Kde chybí, roste význam Tier 2 zdrojů.

### 6.5 Fyzické osoby a GDPR

U business angels a large private investors se ukládají **jen profesní údaje**: jméno, role, investiční aktivita. **Žádná data narození, adresy ani soukromé kontakty**, a to ani tehdy, když jsou viditelné v obchodním rejstříku. Právním základem je oprávněný zájem (legitimate interest, čl. 6 odst. 1 písm. f GDPR) s minimalizací dat. Pro ostrý provoz je třeba vyřešit informační povinnost podle čl. 14 GDPR.

---

### 6.6 Ověřovací postup

Jak se u každého kandidáta postupuje od nálezu po zápis do dat, popisuje [checklist ověřovacího postupu](overovaci-postup.md). Propojuje pravidla tohoto plánu, datový model, agenty a skripty. Nová pravidla nezavádí.

---

## 7. Aktivita: investuje subjekt stále?

Aktivita **není podmínkou zařazení**, ale **stavovým atributem** záznamu. Investor, který delší dobu neinvestoval, zůstává v databázi. *(Rozhodnuto.)*

| Stav (`activity_status`) | Podmínka |
|---|---|
| `active` | Doložená investice za **posledních 24 měsíců**. Počítá se i **follow-on**, tedy další investice do firmy, ve které už investor podíl má. |
| `inactive` | Nejnovější doložená investice je **starší než 24 měsíců**, nebo její datum neznáme |

- **`inactive` neznamená, že investor přestal investovat.** Znamená jen, že **nemáme doloženou novější investici**.
- Stav se **počítá z data poslední doložené investice** (`last_investment_date`) k aktuálnímu dni, takže je vždy aktuální. Záznam se nikdy automaticky nemaže a nový důkaz ho vrátí do stavu `active`.
- **Doložená investice** je stejná jako v K3: kapitálová investice doložená **nezávislým zdrojem** (tier 1 nebo 2). Investice doložená jen vlastním zdrojem investora (tier 3) stav `active` nezakládá. *(Rozhodnuto.)*
- Oznámení nového fondu stav nemění. Eviduje se jen jako nový fond s jeho velikostí (viz 10.1).

### 7.1 Datum investice a jeho přesnost

- **Datum investice** je datum oznámení dealu (announcement), nebo datum investice, které zdroj výslovně uvádí.
- **Datum zápisu společníka do obchodního rejstříku není datum investice** a **zapsaný vklad není výše investice**. *(Rozhodnuto.)*
  - Zápis bývá až po investici.
  - Vklad do základního kapitálu bývá jen zlomek skutečné investice, zbytek tvoří ážio. Například vklad 20 000 Kč při investici v řádu milionů.
  - Oba údaje se proto ukládají zvlášť (`registry_entry_date`, `registry_contribution`) a do data a výše investice se nepřebírají.
  - **Samotný zápis nestačí pro K3 ani pro stav `active`** (6.4). *(Rozhodnuto.)*
- Datum se ukládá **jen s takovou přesností, jakou zdroj skutečně uvádí** (ISO 8601): `YYYY-MM-DD`, `YYYY-MM` nebo `YYYY`.
- **Neznámé části data se nedoplňují.** Například investice známá jen rokem 2024 se uloží jako `2024`, nikdy ne jako `2024-01-01`.
- Datum publikace zdroje, který se o investici zmiňuje jen zpětně (např. rozhovor nebo přehled portfolia), **není datem investice**.
- Pokud zdroj neuvádí ani rok, datum zůstane **prázdné**. Taková investice nemůže zakládat stav `active`, ale jako důkaz pro K3 platí, pokud má datum publikace.
- Při porovnání neúplného data s hranicí 24 měsíců se postupuje **konzervativně**: `active` vzniká jen tehdy, když investice **s jistotou** spadá do posledních 24 měsíců.
  - Rozhoduje nejstarší možný den, který z neúplného data plyne.
  - Příklad: k 2026-10-14 je hranice 2024-10-14. Investice s datem `2024` proto stav `active` nezakládá, s datem `2025` ano.

---

## 8. Pravidla vyřazení

| Kód | Kategorie | Pravidlo |
|---|---|---|
| E1 | Zprostředkovatelé a poradci | Poradci, M&A boutiques, advokátní kanceláře, Big4, placement agents, brokeři. Neinvestují vlastní kapitál a nerozhodují o něm. |
| E2 | Platformy | Crowdfundingové a investiční platformy jsou zprostředkovatelé. Zařadit lze jen vlastní fond platformy, pokud splní K1–K3. |
| E3 | Věřitelé | Banky, leasing, factoring, private credit a venture debt **bez doložené equity investice**. |
| E4 | Jen veřejné trhy | Podílové fondy, ETF, hedge funds a asset manageři bez přímých investic do firem. |
| E5 | Reálná aktiva | Realitní, infrastrukturní, energetické a komoditní fondy, které investují do aktiv, ne do firem. *V ČR jich je v seznamech ČNB mnoho, takže ČNB je jako zdroj kandidátů hodně „zašuměná“.* |
| E6 | Strategické a vnitroskupinové transakce | Firma kupuje podíly kvůli začlenění do vlastní skupiny nebo investuje do vlastních dceřiných společností. |
| E7 | Jen LP / fund of funds | Investuje jen do fondů a o investicích do firem nerozhoduje. Lze ho ale použít jako zdroj při hledání kandidátů. |
| E8 | Nefinanční podpora | Granty, dotační agentury, soutěže, inkubátory bez vlastního kapitálu. |
| E9 | Podezřelé subjekty (až po prověření) | Vyřadí se teprve tehdy, když **prověření potvrdí**, že subjekt nejedná jako investor. Například vybírá od zakladatelů poplatky místo investování, nebo jeho tvrzené investice vyvracejí nezávislé zdroje. **Samotné varovné signály** (poplatky, nedoložené investice, anonymní tým) k vyřazení **nestačí**: záznam zůstává kandidátem, dokud se neprověří. Výsledek prověření se zapíše k citaci důvodu vyřazení. *(Rozhodnuto.)* |
| E10 | Investiční vehikula a duplicity | Fondy, SPV, feedery a přejmenované subjekty se **sloučí** pod nadřazený záznam, nejsou samostatné. |

Pravidla vyřazení se týkají jen toho, **čím subjekt je** (E1–E8, E10), nebo **prověřeného podezření** (E9). **Neaktivita, chybějící údaje ani neprověřené varovné signály nejsou důvodem k vyřazení:**

- subjekt bez novější investice zůstává se stavem `inactive` (kapitola 7),
- subjekt, který zatím nesplňuje K1–K3, zůstává v seznamu kandidátů (kapitola 10).

Každé vyřazení se **zapíše do logu** (kód důvodu + zdroj), aby šlo v kroku 6 změřit i chybně vyřazené subjekty (false negatives).

---

## 9. Hraniční případy

| Případ | Pravidlo |
|---|---|
| Kombinovaný fond dluh + equity (např. growth equity + venture debt) | Typ se určí jen podle doložených **equity** investic. Dluhové deally se jako důkaz nepočítají. |
| Fond mezi dvěma generacemi (Fund I vyinvestovaný, Fund II ve fundraisingu) | Stav určuje jen doložená investice (kapitola 7). Oznámený nový fond se eviduje jako fond s cílovou nebo uzavřenou velikostí (viz 10.1). |
| Investiční skupina bohatého jednotlivce | Má vlastní investiční tým → FO (4.1, krok 2). Osoba s holdingem bez investičního týmu → Business Angel nebo Large Private Investor (4.3). Provozní holding bez investic do cizích firem → E6. |
| Partner VC fondu investující soukromě | Samostatný záznam jako business angel nebo large private investor (4.3), ale jen s vlastními doloženými investicemi. |
| Sankcionované subjekty | Nevyřazovat automaticky. Označit příznakem podle sankčních seznamů EU a OFAC. |
| Země investora | Země **HQ** = sídlo investičního týmu nebo správce. Domicil fondu (Lucembursko, SK, NL…) se eviduje zvlášť. |
| Rozpor mezi zdroji | Tier 1 má přednost před Tier 2 a Tier 2 před Tier 3. Při stejné úrovni platí novější zdroj. Každý rozpor se zapíše do logu. |

---

## 10. Chybějící informace

Zadání říká, že u každého investora „musí být uvedeno“, v jakém sektoru působí, do čeho a kolik investuje a jaký má celkový kapitál. **Výklad:** každý z těchto údajů musí mít buď **doloženou hodnotu**, nebo **výslovnou informaci, že veřejně dostupný není, a proč**. Údaj se nesmí vymýšlet. U FO a fyzických osob se AUM často nezveřejňuje.

| Skupina polí | Pole | Když chybí |
|---|---|---|
| **Pole nutná pro zařazení** (inclusion fields) | identita, primary type, země (u subjektů sídlo HQ, u fyzických osob země působení), ≥1 nezávislý důkaz investice | záznam **se nezařadí** a zůstává v seznamu kandidátů |
| **Popisná pole** (descriptive fields) | sektory, fáze a typ investic, geografie, ticket size, AUM, velikost fondů | záznam **zůstává**, hodnota je `null` a v `missing_reason` je důvod: `not_public`, `conflicting`, `not_applicable` nebo `ambiguous` |

**Důvod `ambiguous`** se použije, když zdroj údaj uvádí, ale **není jasné, co představuje**. Typicky jde o větu „disponuje kapitálem X“, ze které neplyne, zda jde o AUM, velikost fondu, nebo vlastní kapitál. Nejasný údaj se nezapisuje jako hodnota, ale zůstane dohledatelný v citaci. *(Rozhodnuto.)*

**Původ hodnoty** (atribut `value_origin`, podle spolehlivosti):

1. `reported`: hodnotu zveřejnil zdroj,
2. `derived`: hodnota je odvozená z doložených investic s popsanou metodou. Například sektory podle portfolia nebo ticket podle velikosti kol, ve kterých investor byl.
3. `estimate`: odhad, jen s výslovným označením a zdůvodněním. Jeho přesnost se měří zvlášť.

U hodnot `derived` a `estimate` **nestačí popis výpočtu**. Musí být dohledatelné i **původní zdroje**, ze kterých výpočet vychází (URL, datum, citace). *(Rozhodnuto.)*

**Sektory** se zařazují do číselníku 18 kategorií ([datovy-model.md](datovy-model.md), kap. 7). Vedle toho se **doslovně uchovává původní označení ze zdroje**. *(Rozhodnuto.)*

**Stárnutí:** každá hodnota má datum `as_of`. Údaj o AUM starší než 3 roky dostane příznak `stale`.

### 10.1 Velikost fondu vs. AUM investora

Velikost jednotlivého fondu a celkové AUM investora jsou **dva samostatné údaje** a **automaticky se nezaměňují**. *(Rozhodnuto.)* „Celkový investiční kapitál“ ze zadání odpovídá **AUM investora**.

| Údaj | Úroveň | Význam |
|---|---|---|
| **Velikost fondu** (`fund_size`) | jeden konkrétní fond | Kapitál, který investoři do fondu upsali (committed capital). Eviduje se s názvem fondu, vintage, měnou, datem a typem velikosti: `target` (cílová), `first_close` (první uzavření) nebo `final_close` (konečné uzavření). |
| **AUM investora** (`aum`) | celý investiční subjekt | Celkový kapitál, který investor spravuje napříč všemi fondy a vehikuly, **jak ho uvádí zdroj**, k datu `as_of`. Ukládá se i druh údaje: AUM výslovně uvedené zdrojem, nebo regulatorní AUM (např. Form ADV). |

**Pravidla:**

- Velikost jednoho fondu se **nikdy nezapisuje jako AUM** a naopak. Typická chyba médií je zaměnit „fond o velikosti X“ a „spravuje X“, proto se vždy čte přesná formulace ve zdroji.
- **Celkový upsaný kapitál fondů (committed capital) není AUM** a do AUM se nezapisuje, ani když ho zdroj uvede jako jedno číslo. Zapisují se jednotlivé fondy. *(Rozhodnuto.)* Validátor varuje, když se AUM shoduje s velikostí některého fondu nebo se součtem fondů.
- **AUM se z velikostí fondů automaticky nedopočítává.** Součet fondů se od AUM liší kvůli vráceným prostředkům, změnám hodnoty portfolia, neznámým fondům a co-investment vehiklům.
- Pokud AUM není zveřejněné, zůstane `null` s důvodem `not_public`, **i když známe velikosti fondů**.
- Cílová velikost (`target`) a první uzavření (`first_close`) se nikdy neprezentují jako konečná velikost fondu.
- U fyzických osob a FO se **osobní majetek** (net worth, např. žebříčky bohatých) nezapisuje jako AUM ani jako investiční kapitál.
- Součet velikostí fondů se **nepočítá ani jako samostatný odvozený údaj**. Evidují se jen velikosti jednotlivých fondů. *(Rozhodnuto.)*
- V měření přesnosti (krok 6) se velikost fondu a AUM ověřují jako **dvě samostatná pole**.

---

## 11. Pilot: české VC a rozbor zdroje CVCA

### 11.1 Kdo je pro pilot „český VC investor“

Investiční tým nebo správce **doložitelně sídlí v ČR**, bez ohledu na domicil fondu. *(Rozhodnuto.)* Zahraniční VC s pobočkou v ČR se zapíše do logu, ale do pilotu nespadá.

### 11.2 Rozbor zdroje: CVCA

[Czech Private Equity & Venture Capital Association](https://www.cvca.cz/) (CVCA) zastupuje firmy působící v PE a VC v ČR. Stav k 2026-10-14:

| Zjištění | Detail |
|---|---|
| **Řádní členové: 27** | Podle popisů dodaných samotnými členy jde převážně o **PE** (buyouts, MBO/MBI, growth). VC a early-stage investorů je jen asi 8: Credo Ventures, Depo Ventures, KAYA VC, Nation1, Tensor Ventures, Tilia Impact Ventures (čestný člen), i&i Biotech Investments a Inven Capital (CVC). Zbytek tvoří PE a smíšené fondy s dluhem (CVI, Orbit Capital). |
| **Přidružení členové: 57** | Převážně **nejsou investoři**: advokátní kanceláře, Big4 a poradci, banky, pojišťovny, burza. Jsou mezi nimi ale i investoři (např. Pale Fire Capital). **Kategorie členství tedy neodpovídá typu subjektu.** |
| **Pokrytí VC je nízké** | Česká VC, která se běžně objevují v médiích (např. Rockaway Ventures, Reflex Capital, Presto Ventures, Lighthouse Ventures, Day One Capital), mezi řádnými členy **chybí** (textové vyhledávání na stránce 2026-10-14; jejich status se ověří v pilotu). Tvrzení CVCA, že sdružuje „téměř všechny PE & VC fondy“, tak pro VC neplatí. |
| **Aktuálnost** | Stránka řádných členů byla podle metadat naposledy upravena 2024-05-22. Kritéria členství nejsou zveřejněná. |
| **Kvalita údajů** | Popisy a případné údaje o AUM dodávají členové sami, jde tedy o Tier 3. Ze seznamu nejde vyčíst, kdy subjekt naposledy investoval. |

**Závěr:** CVCA je **užitečný zdroj kandidátů**, hlavně pro PE, a doplňkový zdroj vlastních tvrzení (Tier 3). **Pro VC je výrazně neúplný** a **členství není důkazem investice** ani typu subjektu. V pilotu ho proto použijeme jako jeden z více zdrojů kandidátů. Úplnost bude zajištěna kombinací zdrojů, které rozebírá [mapa zdrojů](zdroje-cr.md) (krok 3):

- seznamy ČNB, včetně podlimitních správců podle § 15 ZISIF, ale s filtrem E5,
- obchodní rejstřík,
- portfolia LP (např. EIF),
- média,
- veřejné profily na agregátorech.

---

## 12. Přehled rozhodnutí a otevřené otázky

| Téma | Kapitola | Stav |
|---|---|---|
| Účel databáze: rychle najít skutečné a aktivní investory pro projekt | 1 | rozhodnuto |
| Metodika použitelná celosvětově, pilot na českých VC, jen veřejná data | 1 | rozhodnuto |
| Definice investora: sám rozhoduje + veřejně doložená investice | 3 | rozhodnuto |
| Jednotka záznamu = investiční subjekt, ne jednotlivý fond | 3.1 | rozhodnuto |
| Pět základních typů podle zadání | 4 | rozhodnuto |
| Základní typ se nikdy nepřiřazuje automaticky. Když ho nejde doložit, záznam zůstává v seznamu kandidátů. | 4.1 | rozhodnuto |
| Ostatní subjekty přes `subtype` (accelerator, public, institutional, angel fund, multi-family). Subtype neurčuje základní typ, ten se určuje podle 4.1. | 4.2 | rozhodnuto |
| Corporate VC → VC / `corporate` | 4.2 | rozhodnuto |
| Business Angel / Large Private Investor: rozhoduje investiční chování. 500 000 EUR je jen orientační vodítko (EBAN + BAE), ne automatické pravidlo. | 4.3 | rozhodnuto (lze upravit po pilotu) |
| Úřední registr není povinný, úrovně identity I1/I2/I3 | 5 (K1) | rozhodnuto |
| K2 je povinná, posouzení se eviduje citací `decision_authority`. Bez posouzení se investor nezařadí. | 5 (K2) | rozhodnuto |
| K zařazení stačí 1 kvalitní nezávislý důkaz, bez požadavku na počet investic | 5 (K3) | rozhodnuto |
| Investice bez uvedené formy (`investment_unspecified`) se počítá jen při výslovném oznámení investice, obecné „financování“ nestačí | 5 (K3) | rozhodnuto |
| Samotný zápis společníka v rejstříku nesplní K3 ani nezakládá `active`. Potřebný je další doklad transakce (listina, oznámení). | 5 (K3), 6.4, 7.1 | rozhodnuto |
| Aktivita jako stav `active` / `inactive` (24 měsíců, včetně follow-on), bez automatického vyřazení | 7 | rozhodnuto |
| Datum investice jen se známou přesností, nic se nedomýšlí | 7.1 | rozhodnuto |
| Konzervativní vyhodnocení neúplného data vůči hranici 24 měsíců | 7.1 | rozhodnuto |
| Velikost fondu a AUM investora jako dva samostatné údaje, bez automatické záměny | 10.1 | rozhodnuto |
| Součet velikostí fondů se nepočítá, evidují se jen jednotlivé fondy | 10.1 | rozhodnuto |
| Neaktivita ani chybějící údaje nejsou důvodem k vyřazení | 7, 8, 10 | rozhodnuto |
| Definice „českého VC“ pro pilot: investiční tým nebo správce sídlí v ČR | 11.1 | rozhodnuto |
| Investice s nejasným nástrojem (kapitálová investice, nebo půjčka?) se nepočítá jako důkaz investování | 5 (K3) | rozhodnuto |
| Aktivita se počítá jen z investic doložených nezávislým zdrojem (tier 1 nebo 2) | 7 | rozhodnuto |
| Datum zápisu a vklad v obchodním rejstříku nejsou datum a výše investice | 7.1 | rozhodnuto |
| Důvod chybějící hodnoty `ambiguous` | 10 | rozhodnuto |
| Odvozené a odhadnuté hodnoty musí mít dohledatelné původní zdroje, ne jen popis výpočtu | 10 | rozhodnuto |
| Číselník 18 sektorů + doslovné původní označení ze zdroje | 10 | rozhodnuto |
| Celkový upsaný kapitál fondů není AUM | 10.1 | rozhodnuto |
| Fáze a regiony podle návrhu v datovém modelu | [datovy-model.md](datovy-model.md), kap. 7 | rozhodnuto |
| Přepočet měn se zatím neřeší | [datovy-model.md](datovy-model.md), kap. 5 | rozhodnuto (zatím) |
| Kontrola, že citace na uvedeném webu opravdu je: skript `scripts/check_quotes.py` | 6.2 | rozhodnuto (hotovo) |
| Úrovně zdrojů Tier 1–4 | 6.1 | rozhodnuto |
| Hodnocení spolehlivosti A/B/C | 6.3 | rozhodnuto |
| Pravidla vyřazení E1–E8 a E10 | 8 | rozhodnuto |
| E9 jen po prověření, samotné varovné signály nevyřazují | 8 | rozhodnuto |
| Chybějící údaje: prázdná hodnota + důvod | 10 | rozhodnuto (s datovým modelem) |
| Hraniční případy, GDPR | 9, 6.5 | **návrh bez připomínek, zatím výslovně neschválený** |
| Krok 3 jen pro ČR, celosvětový odhad počtu investorů až v závěrečné analýze (krok 7) | 2 | rozhodnuto |
| Katalog zdrojů ve třech tabulkách: zdroje, použití se spolehlivostí, důkazy | [zdroje-cr.md](zdroje-cr.md) | rozhodnuto |
| Zdroje s omezujícími podmínkami (Dealroom, OpenVC, CEE Funding Map, CC+) jen ručně a interně, data se nepřebírají v rozporu s podmínkami | [zdroje-cr.md](zdroje-cr.md) | rozhodnuto |
| Evidence původu kandidátů (`candidates.csv`) se zavede v pilotu (krok 5) | [data/sources/README.md](../data/sources/README.md) | rozhodnuto |
| Pokrytí ČR v CEE Funding Map; komerční užití dat obchodního rejstříku; seznam správců podle § 15 ve WS JERRS | [zdroje-cr.md](zdroje-cr.md), kap. 8 | otevřené |
| Archivace zdrojů (např. Wayback Machine) odložena do dokončení pilotu; do té doby URL, citace, datum přístupu a varování validátoru | 6.2, [ověřovací postup](overovaci-postup.md) | odloženo |
| Stejné IČO = stejný subjekt (žádný nový záznam). U značky s více právnickými osobami rozhoduje skutečná investiční pravomoc: jako E10 se slučují jen osoby bez ní (vehikula, feedery, SPV, GP). Duplicitní IČO hlásí validátor, párování dělá koordinátor ručně. | 3.1, K1, 8 (E10), [ověřovací postup](overovaci-postup.md) | rozhodnuto (automatizace v pilotu) |
| Sankční seznamy EU a OFAC | 9 | otevřené |
| Ruční audit pilotu (krok 6): nezávislost důkazů a hodnocení A u NRI, K2 u Rockaway, právnické struktury Tilie a Orbitu, zda Vistag je skutečně uskutečněná investice StartupYardu | [results/README.md](../results/README.md) | rozhodnuto v kroku 6 (AI podle metodiky), nejistoty zapsané |
| Město sídla investičního týmu jako samostatný doložený údaj; přehled zařazených investorů pro čtení generovaný z dat | [datovy-model.md](datovy-model.md), kap. 3.1 a 9.1 | rozhodnuto |
| Pilot nejdřív na 5 různorodých českých VC, rozšíření až po osvědčení postupu. Kandidáti jen ze zmapovaných zdrojů, zdroje s omezeným přístupem vynechány, současný tarif Firecrawl. | 11, [data/sample/README.md](../data/sample/README.md) | rozhodnuto |
| Původ kandidátů v `candidates.csv`, `investor_id` až po ověření | [datovy-model.md](datovy-model.md), kap. 3.6 | rozhodnuto |
| Odhad počtu investorů a nákladů pro celý svět: rozlišit celkový počet a počet ověřitelný z veřejných zdrojů, každý typ zvlášť | 13 | odhad hotový (krok 7) |
| Před rozšířením na PE, FO, angely a LPI a na další jazyky malý pilot (5 investorů), který změří úspěšnost ověření, náklady a přesnost | 13.8 | doporučeno, otevřené |

---

## 13. Odhad pro celý svět (krok 7)

> **Stav:** hotovo 2026-10-16, revidováno týž den (kap. 13.9). Jde o **podložený odhad**, ne o databázi. Žádná data o investorech se pro něj nesbírala.
> **Vstupy:** každé číslo má zdroj s doslovnou citací (Z), měření z pilotu (M), nebo je výslovně označené jako předpoklad (P): [results/odhad_svet.csv](../results/odhad_svet.csv).

Zadání chce vědět čtyři věci: jaké typy investorů lze z veřejných zdrojů získat, kolik jich bude, jak spolehlivá budou data a kolik bude stát rozšíření na celý svět.

### 13.1 Výsledek v kostce

| Typ | Celkem ve světě | Reálně najdeme a ověříme (střed) | Jistota odhadu | Prvotní ověření, střed (rozpětí) |
|---|---|---|---|---|
| **VC** (včetně korporátních) | 9 800–13 600 | 4 900–9 700 (**~7 300**) | střední: pilot + oborové ročenky | 150 000 USD (59 000–326 000) |
| **PE** | 8 600–14 500 | 3 000–8 500 (**~5 800**) | nízká až střední | 125 000 USD (40 000–287 000) |
| **Family offices** s přímými investicemi | 4 500–6 600 | 700–2 300 (**~1 500**) | nízká | 53 000 USD (13 000–151 000) |
| **Organizace celkem** | **23 000–35 000** | **8 600–20 500 (~14 600)** | | **328 000 USD** (113 000–763 000) |
| **Business angels** | 0,6–1,2 milionu | 5 900–47 000 (**~26 500**) | velmi nízká | 1,18 mil. USD (0,14–4,5 mil.) |
| **Large private investors** | 26 000–77 000 | 800–5 400 (**~3 100**) | velmi nízká | 137 000 USD (18 000–510 000) |
| **Fyzické osoby celkem** | **0,6–1,25 milionu** | **6 700–52 400 (~29 500)** | | **1,32 mil. USD** (0,16–5,0 mil.) |

**Jaké typy lze získat:**
- **Organizace (VC, PE, family offices) ano.** Mají weby, jejich investice se oznamují a dají se doložit nezávislým zdrojem. U VC a PE v USA a Evropě lze najít a ověřit většinu, ve zbytku světa menšinu. U family offices jen menšinu, protože se veřejnosti vyhýbají.
- **Fyzické osoby (angelové, LPI) jen v malé, viditelné části**, asi 1–7 %. Ostatní nejsou veřejně doložitelní.

**Kolik to bude stát:**

| Položka | Organizace | Všechny typy |
|---|---|---|
| Prvotní ověření: AI, nástroje a ruční kontrola | ~0,33 mil. USD | ~1,65 mil. USD (0,27–5,7 mil.) |
| Lidská práce (řízení, vývoj, právní posouzení) | ~0,08 mil. USD | ~0,08 mil. USD (0,04–0,14 mil.) |
| **Prvotní ověření celkem** | **~0,41 mil. USD** | **~1,7 mil. USD** |
| Aktualizace ročně (AI, nástroje, ruční kontrola) | ~66 000 USD | ~200 000 USD (46 000–440 000) |
| Lidská práce ročně | ~27 000 USD | ~27 000 USD (12 000–48 000) |

- **Spolehlivost dat** je změřená jen u VC: ručně 8 z 10 údajů správně, podle kontroly AI 94 % údajů bez chyby (kap. 13.5).
- **Aktivní je jen část ověřených investorů:** v pilotu 2 z 5, viz kap. 13.5.

### 13.2 Jak jsem k odhadu došel

Každý typ investora jsem počítal zvlášť ve třech krocích:

1. **Celkový počet** z veřejných studií. Kde studie pokrývá jen region, sečetl jsem regiony. Mezery bez zdroje jsem doplnil předpokladem a označil ho.
2. **Podíl, který lze najít a ověřit.** Ptal jsem se, zda u typického subjektu existuje veřejný nezávislý doklad konkrétní investice (K3), doložitelná rozhodovací pravomoc (K2) a identita (K1).
   - U VC to kalibruje pilot.
   - U ostatních typů je to úvaha podle povahy veřejných zdrojů, ne měření.
3. **Náklady** z měření v pilotu, přepočtené úspěšností ověření. Typy, kde neprojde každý kandidát, platí i za ověřování těch, kdo neprojdou.

**Jak číst rozpětí:**
- „nízko–vysoko“ kombinuje všechny nízké nebo všechny vysoké vstupy, a je proto záměrně široké,
- střed počítá se středy všech vstupů,
- výpočet je prosté násobení vstupů z CSV (celkem × podíl, kandidáti = ověření ÷ úspěšnost).

**Co z pilotu platí a co ne** (pilot ověřil jen 5 českých VC):

| Zjištění z pilotu | VC jinde | PE | FO | Angelové a LPI |
|---|---|---|---|---|
| Cena jednoho ověření (průzkumník + auditor) | platí, mimo angličtinu a češtinu může být vyšší | pravděpodobně podobná, struktury bývají složitější | podobná nebo vyšší | jiná: méně údajů, ale těžší identita |
| 5/5 vylosovaných kandidátů splnilo K1–K3 | jen v zemích s dobrými médii a rejstříky | **nevyzkoušeno** | **nevyzkoušeno** | **nevyzkoušeno** |
| Přesnost údajů (ručně 8/10, AI 115/122) | přibližně | **nevyzkoušeno** | **nevyzkoušeno** | **nevyzkoušeno** |
| Kandidáti ze seznamů asociací, LP a médií za 0,04 USD | platí | platí (asociace, oznámení akvizic) | ne, veřejné seznamy nejsou | ne, kandidáti jen z oznámení investic |

### 13.3 Celkový počet podle typu

ID v závorce odkazuje na řádek v [results/odhad_svet.csv](../results/odhad_svet.csv).

- **VC: 9 800–13 600.**
  - **USA:** 2 984 VC firem, které za posledních 8 let uzavřely fond (Z01).
  - **Evropa:** 3 095 aktivních firem PE a VC dohromady (Z03, řád potvrzuje i druhý zdroj), VC z nich 40–60 % (P01).
  - **Korporátní VC:** 2 344 korporací aktivních v kolech v roce 2024 (Z04). Dříve aktivní nejsou započtené.
  - **Čína:** 11 523 registrovaných správců PE a VC (Z05), aktivních VC z nich 15–30 % (P02).
  - **Zbytek světa:** 1 500–3 000, předpoklad (P03).
- **PE: 8 600–14 500.**
  - **USA:** 3 000–5 000. Ověřitelný veřejný údaj se nenašel, je to předpoklad (P04).
  - **Evropa:** zbytek z 3 095 firem.
  - **Čína:** 25–40 % registrovaných správců (P02).
  - **Zbytek světa:** 1 500–3 000 (P03).
- **Kontrola řádu:** Preqin v roce 2018 evidoval 15 986 firem PE včetně VC (Z06). Náš součet VC + PE je 18 400–28 100, tedy 1,2–1,8× víc. Rozdíl odpovídá růstu od roku 2018, čínským registracím a korporátním VC. Vyšší konec rozpětí je spíš nadsazený.
- **Family offices: 4 500–6 600 v rozsahu databáze.**
  - Deloitte odhaduje 8 030 single family offices (Z07). Jde o modelový odhad, ne o seznam.
  - Do databáze patří jen ty, které investují přímo do firem (plan.md 4). Podle průzkumu Citi se přímým investicím věnuje 70 % dotázaných (Z08). Respondenti jsou ale klienti velké banky a „direct investments“ může zahrnovat i nemovitosti, proto počítám s 50–70 %.
  - Počet multi-family offices se ověřit nepodařilo, započteno 500–1 000 s přímými investicemi (P05).
- **Business angels: 0,6–1,2 milionu.**
  - **USA:** 445 535 aktivních angelů v roce 2024 (Z09). Je to odhad výzkumného centra UNH, metodika ve zprávě uvedená není.
  - **Evropa:** 47 600 jen v sítích a asociacích (Z10). EBAN sám uvádí, že jde jen o viditelný trh. Horní mez 330 000 je předpoklad odvozený z dřívějšího násobku 10, který EBAN už nepoužívá (P06).
  - **Zbytek světa:** 100 000–400 000, předpoklad (P07).
- **Large private investors: 26 000–77 000.**
  - Na světě je 510 810 lidí s majetkem nad 30 mil. USD (Altrata, Z12). To je zásoba bohatých lidí, ne investorů.
  - Do databáze patří jen ti, kdo **sami jako jednotlivci** investují do cizích firem ve velkém (plan.md 4.3). Ti, kdo investují přes family office s vlastním týmem, se počítají jako FO.
  - Takových je podle předpokladu 5–15 % (P09). Studie, která by to měřila, se nenašla.

### 13.4 Kolik dokážeme najít a ověřit

Rozhoduje, zda pro subjekt existuje **veřejný nezávislý doklad konkrétní investice** (K3) a zda lze doložit, kdo rozhoduje (K2).

| Typ | Podíl (P08) | Proč |
|---|---|---|
| **VC** v USA, Evropě a korporátní | 65–90 % | Kola se veřejně oznamují a fondy mají weby a portfolia. Pilot: 5/5, ale 95% interval je 57–100 %. Zbytek tvoří malé nebo neaktivní fondy bez nezávislého dokladu. |
| **VC** v Číně a zbytku světa | 20–50 % | Jiné jazyky, méně médií a mnoho registrovaných, ale neaktivních správců. Samotný zápis v rejstříku K3 nesplní (6.4). Postup v těchto jazycích není vyzkoušený. |
| **PE** v USA a Evropě | 50–80 % | Akvizice se obvykle oznamují a firmy mají weby s portfoliem. Menší PE a holdingy ale často mlčí. **V pilotu nevyzkoušeno.** |
| **PE** v Číně a zbytku světa | 20–40 % | Stejné důvody jako u VC. |
| **Family offices** | 15–35 % | Mnohé se veřejnosti záměrně vyhýbají, investují bez uvedení jména nebo přes holdingy. Obtížné je i odlišit FO od správce majetku (K2, typ). |
| **Business angels** | 1–4 % | K3 vyžaduje, aby nezávislý zdroj jmenoval konkrétního člověka u konkrétní investice. To se stává hlavně u známých angelů a ve větších kolech. V pilotu zdroje jmenovaly u investic jen 7 fyzických osob. Hrají roli i GDPR a minimalizace dat (6.5). |
| **Large private investors** | 3–7 % | Velké přímé investice známých lidí se v médiích objevují. U většiny bohatých lidí ale veřejně doložené nejsou, nebo jdou přes FO. |

**Úspěšnost ověření kandidáta (P10):**

| Typ | Úspěšnost | Odkud |
|---|---|---|
| VC | 60–100 % | pilot 5/5, dolní mez podle intervalu spolehlivosti |
| PE | 60–90 % | předpoklad |
| FO | 30–60 % | předpoklad |
| Angelové, LPI | 20–50 % | předpoklad |

Úspěšnost ovlivňuje jen náklady (kap. 13.6), ne počet.

### 13.5 Jak spolehlivá budou data

**Změřeno v pilotu** (5 českých VC, kroky 5 a 6, [results/README.md](../results/README.md)):

| Ukazatel | Výsledek |
|---|---|
| Údaje podle ruční kontroly | 8/10 správně (95% interval 49–94 %) |
| Údaje podle kontroly AI | 115/122 bez chyby a nejistoty (89–97 %) |
| Citace doslovně ve zdroji | 142/142 |
| Zařazení (K1–K3, typ) | 5/5 podle AI, člověk K1–K3 neověřoval |
| Hodnocení A/B | 4/5 správně |

- **Chyby vznikají při vyvozování ze zdrojů:** přiřazení k fondu bez zdroje, výběr mezi rozpornými zdroji, počítání důkazů.
- **Vyplněnost údajů** (M10):
  - geografie 5/5,
  - fáze 5/5, z toho 2 odvozené,
  - sektory 4/5, po opravě 3/5,
  - ticket 3/5,
  - **AUM 0/5**, celkový kapitál se veřejně uvádí jen výjimečně.
- **Aktivita:** investici za posledních 24 měsíců mají doloženou jen 2 z 5 (95% interval 12–77 %). Ročenka NVCA uvádí, že téměř polovina investorů aktivních v roce 2021 z trhu odešla (Z02).
  - Počty v kap. 13.1 zahrnují i neaktivní investory, protože K3 nemá časový limit.
  - Aktivních bude zhruba polovina, ale tato hodnota je nejistá.

**Očekávání u dalších typů** (neměřeno):

| Typ | Identita a investice | Ticket a AUM | Hlavní riziko |
|---|---|---|---|
| VC | spolehlivé (měřeno) | ticket asi u poloviny, AUM výjimečně | přiřazení k fondu, zastaralé profily |
| PE | spolehlivé, akvizice se oznamují | velikost fondů se často uvádí, ticket jako rozpětí hodnoty firmy | složité struktury (GP, AIFM), záměna s věřiteli |
| FO | méně spolehlivé, část investic bez jména | téměř nikdy | záměna s poradcem nebo správcem majetku |
| Angelové | jen u jmenovaných osob | téměř nikdy | záměna osob se stejným jménem |
| LPI | jen u známých osob | majetek ze žebříčků není investiční kapitál | investice přes holdingy, hranice mezi LPI a FO |

### 13.6 Náklady

**Co pilot změřil** (5 českých VC, agenti na modelu Opus):

| Položka | Hodnota | Vstup |
|---|---|---|
| Agenti na jednoho investora (průzkumník + auditor) | 7,53 USD; 8,57 USD včetně doplňujícího ověření | M01 |
| Audit AI (krok 6) na jednoho investora | asi 2,45 USD | M04 |
| Práce koordinátora v kroku 5 | asi 35,6 USD, z velké části jednorázová stavba skriptů | M04 |
| Firecrawl | 23–26 kreditů na investora (0,02–0,03 USD při placeném tarifu) | M02, Z13 |
| Hledání kandidátů | 0,04 USD na kandidáta | M03 |
| Doba běhu agentů | asi 22 minut na investora | M08 |

**Cena za jednoho zařazeného investora:**
- **Ověření jednoho kandidáta:** 11–18 USD (P11), vyděleno úspěšností ověření (P10).
- **Ruční kontrola, hledání a Firecrawl (P12):**
  - VC a PE 1,1–3,6 USD,
  - FO a fyzické osoby 1,5–5 USD, protože pro ně nejsou veřejné seznamy kandidátů.

| Typ | USD na zařazeného investora |
|---|---|
| VC | 12–34 |
| PE | 13–34 |
| FO | 20–65 |
| Angelové, LPI | 24–95 |

**Celkem:**
- **Prvotní ověření (AI, nástroje, ruční kontrola):** asi 1,65 mil. USD (0,27–5,7 mil.).
  - **Angelové tvoří 72 %**, protože jich je hodně a většina kandidátů neprojde.
  - Organizace stojí asi 0,33 mil. USD, tedy pětinu nákladů, a dávají třetinu výsledku.
- **Lidská práce** (P14), předpoklad 6 000–12 000 USD za člověkoměsíc:
  - prvotně 6–12 člověkoměsíců, asi 81 000 USD (36 000–144 000),
  - ročně 2–4 člověkoměsíce, asi 27 000 USD.
- **Aktualizace:** 3–6 USD na investora za rok (P13), tedy asi 200 000 USD ročně (46 000–440 000). Organizace z toho asi 66 000 USD.
  - Aktivní investoři se kontrolují ročně, neaktivní jednou za dva roky.
  - Odhad vychází z doplňujícího ověření K2 v pilotu (5,19 USD).
- **Kapacita:** asi 105 000 kandidátů a 38 000 hodin běhu agentů. Při 50 souběžných bězích je to asi 32 dní.
- **Firecrawl:** asi 2,8 milionu kreditů, tedy 3 měsíce tarifu Scale (1 milion kreditů měsíčně za 599–749 USD). Je to **asi 2 000 USD, zhruba 0,1 % nákladů**.
- **Nezapočteno:** externí právní stanovisko ke GDPR a infrastruktura (úložiště, servery).

**Co nejvíc rozhoduje o ceně:**
- cena jazykového modelu (agenti běželi na nejdražším modelu),
- úspěšnost ověření,
- rozsah ruční kontroly.

Levnější model by mohl cenu výrazně snížit, ale jeho přesnost je potřeba nejdřív změřit stejně jako v kroku 6.

### 13.7 Osvědčil se Firecrawl?

**Ano, jako nástroj pro čtení stránek agenty.** Hlavní náklad to není.

**Hlavní přínos:** agentům vrací skutečný text stránky bez přeformulování jazykovým modelem. WebFetch text přepisuje (docs/agenti.md, kap. 4). Díky tomu jsou citace doslovné: 142 ze 142.

**Co ukázal pilot:**
- **116 citací** šlo ověřit i proti přímo stažené stránce.
- **26 citací šlo ověřit jen proti kopii Firecrawlu**, přestože všechny ty stránky šly stáhnout i přímo. Citace pocházely z textu, který Firecrawl převedl z PDF, tabulek nebo obchodního rejstříku (například IČO bez mezer). Přímo stažený text ho doslovně neobsahoval (M07).
- **Ochrana proti robotům** se v pilotu projevila jen jednou: Unquote vracel chybu 429.
- **Hook vynutil bezpečné parametry:** 20 nepovolených volání zablokoval bez spotřeby kreditů.
- **Cena** je proti jazykovému modelu zanedbatelná.

**Co je potřeba hlídat:**
- **PDF stojí kredit za každou stranu.** V kroku 3 jedno PDF spotřebovalo 81 kreditů na jedno přečtení.
- **Tarif Free** (1 000 kreditů měsíčně) stačí asi na 38 investorů. Pro celý svět je potřeba placený tarif.
- **Kopie stránek je potřeba uchovávat** (`.cache/pages`), jinak část citací nepůjde později ověřit.
- **Omezený přístup** Firecrawl nevyřeší: databáze s omezujícími podmínkami ani obsah za paywallem.

**Doporučení:**
- Firecrawl ponechat pro agenty a uchovávat jeho kopie.
- Pro kontrolu citací nejdřív přímé stažení, kopie Firecrawlu až potom.
- Tarif volit podle objemu: Standard pro tisíce investorů, Scale pro desítky tisíc.

### 13.8 Omezení odhadu a doporučený postup

**Omezení:**

- **Nejjistější je VC:** počty pro USA a Evropu jsou z oborových ročenek a pilot ověřil celý postup. I tak jen na 5 českých investorech.
- **PE, FO, angelové a LPI nejsou vyzkoušené.** Podíly v kap. 13.4 jsou úvaha, ne měření, a mohou se lišit i několikanásobně.
- **Největší nejistota jsou angelové.** Celkový počet mimo USA ani podíl veřejně doložených angelů žádná studie nemá. Přitom tvoří 60 % odhadovaného výsledku a 72 % nákladů.
- **Počty pro Čínu a zbytek světa** stojí na předpokladech. Kontrola řádu proti Preqin 2018 naznačuje, že vyšší konec je nadsazený.
- **PE v USA** nemá ověřitelný veřejný zdroj počtu (P04).
- **Náklady stojí na ceně modelu Opus v říjnu 2026** a na pilotu v češtině a angličtině.

**Doporučený postup:**

1. **Organizace dřív než fyzické osoby:** VC v USA a Evropě, potom PE, potom FO. Je to třetina odhadovaného výsledku za pětinu nákladů a s nejlépe změřenou spolehlivostí.
2. **Před každým novým typem a jazykem malý pilot** (5 investorů, jako kroky 5 a 6). Změří úspěšnost ověření, cenu a přesnost a nahradí předpoklady z kap. 13.4 a 13.6.
3. **Vyzkoušet levnější model agentů** na stejném vzorku a porovnat přesnost s Opusem.
4. **Angely a LPI hledat jako vedlejší produkt** ověřování firem a fondů, tedy v oznámeních kol, kde jsou jmenovaní. Nejdřív ale vyřešit GDPR (informační povinnost, 6.5).

### 13.9 Revize odhadu (2026-10-16)

Při kontrole proti zadání a zdrojům jsem opravil:

| Co | Původně | Opraveno | Proč |
|---|---|---|---|
| Důvod, proč 26 citací ověřuje jen Firecrawl | ochrana proti robotům, chyba 429, JavaScript | převod PDF, tabulek a rejstříku; 429 jen jednou | záznam kontroly ukazuje u všech HTTP 200 |
| Korporátní VC | 2 344–4 000 | 2 344 | horní mez neměla zdroj |
| Aktivní správci v Číně | VC 20–40 %, PE 30–50 % | VC 15–30 %, PE 25–40 % | registrace zahrnují fondy fondů a neaktivní správce |
| Zbytek světa | VC 2 500–5 000, PE 2 000–4 000 | VC i PE 1 500–3 000 | součet VC + PE byl až 2,2× nad Preqin 2018 |
| Ověřitelný podíl | VC 75–90 % a 30–60 %; PE 60–85 % a 25–50 %; LPI 5–10 % | VC 65–90 % a 20–50 %; PE 50–80 % a 20–40 %; LPI 3–7 % | příliš optimistické vůči intervalu pilotu a nevyzkoušeným jazykům |
| Úspěšnost ověření VC | 70–100 % | 60–100 % | interval spolehlivosti pilotu 57–100 % |
| Hledání kandidátů FO a osob | jako u VC | 0,5–2 USD na zařazeného | pro FO a osoby neexistují veřejné seznamy |
| Lidská práce | nezapočtena | 6–12 člověkoměsíců prvotně, 2–4 ročně | bez ní byl odhad nákladů neúplný |
| Spolehlivost dat | jen jedna věta | samostatná kap. 13.5 | zadání ji výslovně požaduje |
| Hlavní výsledek | jedno číslo za všechny typy (~50 000) | organizace a fyzické osoby zvlášť | angelové mají velmi nízkou jistotu a přebíjeli součet |

Ověřený výsledek se tím snížil z asi 50 000 na asi 44 000 investorů, z toho organizace z 19 000 na 14 600. Náklady na AI a nástroje klesly z 1,76 na 1,65 mil. USD, ale přibyla lidská práce.

---

## Zdroje

| Zdroj | URL | Přístup |
|---|---|---|
| EBAN Statistics Compendium 2024 | https://www.eban.org/wp-content/uploads/2025/12/Stats-Compendium-2024.pdf | 2026-10-14 |
| Business Angels Europe: A. What is a Business Angel? | https://www.businessangelseurope.com/professionalstandards/a.-what-is-a-business-angel%3F-- | 2026-10-14 |
| CVCA: řádní členové | https://cvca.cz/clenstvi/radni-clenove/ | 2026-10-14 |
| CVCA: přidružení členové | https://cvca.cz/clenstvi/pridruzeni-clenove/ | 2026-10-14 |
| Zdroje odhadu pro celý svět (kap. 13), s doslovnými citacemi | [results/odhad_svet.csv](../results/odhad_svet.csv) | 2026-10-16 |
