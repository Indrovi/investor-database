# Investor Database

Spolehlivá databáze investorů do soukromých firem: VC fondů, PE fondů, family offices, angel investorů a velkých soukromých investorů. Hlavním požadavkem je spolehlivost dat. Každý záznam musí odpovídat skutečnému, aktivnímu investorovi a u každého údaje musí být doložený zdroj (data provenance).

Projekt vychází ze [zadání](docs/zadani.md) a pracuje výhradně s veřejně dostupnými daty.

## Výstupy (deliverables)

| Výstup | Umístění | Stav |
|---|---|---|
| Výsledný plán: inclusion/exclusion criteria, verification, odhad rozsahu a spolehlivosti, odhad nákladů | [docs/plan.md](docs/plan.md) | rozpracováno: krok 2 hotový, u kroku 1 zbývá potvrdit hraniční případy a GDPR |
| Datový model a validátor | [docs/datovy-model.md](docs/datovy-model.md), `scripts/validate.py` | hotovo |
| Data ze vzorku (sample) se zdrojem u každého údaje | `data/sample/` | připravuje se (krok 5) |
| Výsledky měření přesnosti (accuracy) | `results/` | připravuje se (krok 6) |

## Struktura repozitáře

```
docs/            zadání, plán, datový model
data/sample/     data z pilotního vzorku včetně zdrojů
data/examples/   fiktivní ukázková data pro datový model a testy
results/         měření přesnosti, odhad nákladů
scripts/         skripty (validate.py: validace dat)
tests/           testy skriptů
ai-log/          exporty konverzací s AI
```

Validace dat a testy (jen standardní knihovna Pythonu, vyzkoušeno na verzích 3.12.13 a 3.14.4):

```bash
python3 scripts/validate.py data/examples/valid --today 2026-10-14
python3 -m unittest discover -s tests -v
```

## Práce s AI

Projekt vzniká ve spolupráci s AI asistentem. Tato část dokumentuje, k čemu se AI používala, jak se kontrolovaly její výstupy, jaké chyby se našly a jaká padla rozhodnutí.

- **Nástroj:** Claude Code (model Claude Opus 5.5)
- **Workflow:** postupuje se po krocích. Každý krok se nejdřív naplánuje a prodiskutuje, implementuje se až po odsouhlasení.
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
| 2026-10-15 | AI v souhrnu kroku 2 uvedla jako zbývající ke schválení jen tiers, A/B/C a E1–E10. Vynechala hraniční případy (kap. 9) a GDPR (kap. 6.5), které plán vedl jako neschválené. | Neúplná informace o stavu schválení | Doplněno do plánu (kap. 12) a do souhrnu pro autora |

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
