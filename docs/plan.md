# Plán: Spolehlivá databáze investorů

> **Stav:** pracovní verze. Krok 2 ([datový model](datovy-model.md)) je hotový. U kroku 1 (pravidla zařazení a vyřazení) zbývá potvrdit hraniční případy (kap. 9) a GDPR (kap. 6.5).
> **Poslední úprava:** 2026-10-15
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
| 3 | Mapa veřejných zdrojů, odhad počtu investorů a spolehlivosti dat | kapitola plánu | plánováno |
| 4 | Ověřovací postup (verification protocol) | kapitola plánu a checklist | plánováno |
| 5 | Pilot: české VC | `data/sample/` | plánováno |
| 6 | Ruční ověření a měření přesnosti | `results/` | plánováno |
| 7 | Odhad nákladů na rozšíření na celý svět | kapitola plánu a `results/` | plánováno |
| 8 | Revize plánu podle pilotu a finalizace | finální `docs/plan.md` | plánováno |

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

Zda citace na uvedené stránce opravdu je, se zatím automaticky neověřuje. Řeší se v dalších krocích (ověřovací postup, krok 4).

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

**Závěr:** CVCA je **užitečný zdroj kandidátů**, hlavně pro PE, a doplňkový zdroj vlastních tvrzení (Tier 3). **Pro VC je výrazně neúplný** a **členství není důkazem investice** ani typu subjektu. V pilotu ho proto použijeme jako jeden z více zdrojů kandidátů. Úplnost bude zajištěna kombinací zdrojů, které se rozeberou v kroku 3:

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
| Automatická kontrola, že citace na uvedeném webu opravdu je | 6.2 | odloženo do dalších kroků (krok 4) |
| Úrovně zdrojů Tier 1–4 | 6.1 | rozhodnuto |
| Hodnocení spolehlivosti A/B/C | 6.3 | rozhodnuto |
| Pravidla vyřazení E1–E8 a E10 | 8 | rozhodnuto |
| E9 jen po prověření, samotné varovné signály nevyřazují | 8 | rozhodnuto |
| Chybějící údaje: prázdná hodnota + důvod | 10 | rozhodnuto (s datovým modelem) |
| Hraniční případy, GDPR | 9, 6.5 | **návrh bez připomínek, zatím výslovně neschválený** |

---

## Zdroje

| Zdroj | URL | Přístup |
|---|---|---|
| EBAN Statistics Compendium 2024 | https://www.eban.org/wp-content/uploads/2025/12/Stats-Compendium-2024.pdf | 2026-10-14 |
| Business Angels Europe: A. What is a Business Angel? | https://www.businessangelseurope.com/professionalstandards/a.-what-is-a-business-angel%3F-- | 2026-10-14 |
| CVCA: řádní členové | https://cvca.cz/clenstvi/radni-clenove/ | 2026-10-14 |
| CVCA: přidružení členové | https://cvca.cz/clenstvi/pridruzeni-clenove/ | 2026-10-14 |
