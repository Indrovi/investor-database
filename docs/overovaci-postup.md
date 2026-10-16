# Ověřovací postup (checklist pro český pilot)

> **Stav:** schváleno 2026-10-16 (krok 4).
> **Navazuje na:** [plan.md](plan.md) (pravidla) · [datovy-model.md](datovy-model.md) (data a validátor) · [agenti.md](agenti.md) (agenti a skripty) · [zdroje-cr.md](zdroje-cr.md) a [data/sources/](../data/sources/) (zdroje)

Checklist propojuje postupy, které už máme. Nová pravidla nezavádí: o zařazení vždy rozhoduje `plan.md`. Prochází se pro každého kandidáta.

## A. Příjem kandidáta

1. **Zapsat nález** do `candidates.csv`: zdroj z katalogu (`source_key`), URL, datum, způsob nalezení ([data/sources/README.md](../data/sources/README.md)). Tabulka vznikne s pilotem.
   - Zdroje s omezujícími podmínkami (Czechia Dealroom, OpenVC, CEE Funding Map, CC+) jen ručně a interně. Nic se z nich nepřebírá ([zdroje-cr.md](zdroje-cr.md), kap. 8).
2. **Pilotní filtr:** investiční tým nebo správce doložitelně sídlí v ČR (plan.md 11.1). Jinak v `candidates.csv` poznámka „mimo pilot“ s důvodem.
3. **Párování** (plan.md K1, 3.1, E10). Automatické párování přijde s pilotem, do té doby ručně podle tohoto bodu.
   - **Stejné IČO = stejná právnická osoba:** pokud záznam s daným IČO už existuje, nový nevzniká a zjištění se přiřadí k existujícímu záznamu. Hledá se i mezi vyřazenými záznamy E10. U nich se zjištění přiřadí k záznamu v `merged_into`.
   - **Bez IČO** (fyzické osoby, zahraniční subjekty): párovat podle názvu, domény webu, země a klíčových osob.
   - **Jedna značka, více právnických osob:** stejná značka neznamená stejný subjekt. Rozhoduje, kdo má **skutečnou investiční pravomoc** (K2), proto se všechny právnické osoby značky automaticky neslučují.
     - Hlavní záznam v `investors.csv` patří subjektu, který o investicích rozhoduje (správce nebo investiční tým).
     - **Sloučí se** (E10, `merged_into` na hlavní záznam) jen právnické osoby bez vlastní investiční pravomoci, za které rozhoduje hlavní subjekt: fondová vehikula, feedery, SPV, GP. Zůstávají se svým IČO, aby se při dalším nálezu spárovaly. Vzor je v [ukázkových datech](../data/examples/valid/): INV-0005 (E10 → INV-0001).
     - **Samostatný záznam** má právnická osoba, která o investicích rozhoduje sama, i když nese stejnou nebo podobnou značku. Typicky jde o fond oddělený od původní skupiny s vlastním týmem ([agenti.md](agenti.md), kap. 5.4, Presto × Tech Horizons). Rozhoduje doklad K2 a časová osa.
     - Fondy jako takové (velikost, vintage) patří do `funds.csv` (vzor FND-0001).
   - **Nejde rozhodnout,** kdo má investiční pravomoc nebo která osoba je investor: záznam zůstává kandidátem a rozhodne autor (bod F).

## B. Sběr dokladů (průzkumník)

4. **Spustit průzkumníka** s úzkým zadáním: identita, fakta ke K2, doložené investice a popisné údaje. U investic hledat přednostně nejnovější (kvůli stavu aktivity), ale nevynechat starší: K3 časový limit nemá. Zdroje vybírat podle [uses.csv](../data/sources/uses.csv).

   ```bash
   python3 scripts/agents.py run investor-source-scout --prompt-file ZADANI.txt --out .cache/agents/BEH --max-budget-usd 4
   ```

5. **Ověřit citace průzkumníka.** Neúplné nebo nedoslovné záznamy se dál nepoužijí, případně se vrátí průzkumníkovi.

   ```bash
   python3 scripts/check_quotes.py --markdown .cache/agents/BEH/investor-source-scout.md
   ```

## C. Kritická kontrola (auditor)

6. **Předat tvrzení souborem a spustit auditora.**

   ```bash
   python3 scripts/agents.py handoff .cache/agents/BEH/investor-source-scout.md --investor "Název" --out .cache/agents/BEH/handoff.json
   python3 scripts/agents.py run investor-evidence-auditor --prompt-file ZADANI_AUDITOR.txt --out .cache/agents/BEH --max-budget-usd 6
   ```

7. **Ověřit citace nových důkazů** auditora stejně jako v bodě 5 (`check_quotes.py --markdown` na `investor-evidence-auditor.md`).

## D. Rozhodnutí koordinátora (pravidla z plan.md beze změny)

8. **K1, identita:** úroveň I1, I2, nebo I3 (plan.md 5) a kterou právnickou osobu evidovat (bod 3).
9. **K2, rozhodovací pravomoc:** citace `decision_authority` ze zdroje tier 1–3. U správců podle § 15 ZISIF dokládá ČNB jen fakt registrace ([zdroje-cr.md](zdroje-cr.md)).
10. **K3, investice:** aspoň jeden nezávislý doklad podle bodů 1–5 (plan.md 5).
    - Nepočítá se samotný zápis v obchodním rejstříku, nástroj `unclear`, `investment_unspecified` bez výslovné zmínky o investici, vlastní zdroj investora, investice do vlastní skupiny ani zakladatel ve vlastní firmě.
    - Stáří investice pro K3 nerozhoduje. Splní ho i starší doložená investice, hranice 24 měsíců určuje jen stav aktivity (bod 12).
    - Podrobnosti: datovy-model.md 3.3 a 6.
11. **Typ a subtype** (plan.md 4.1–4.3). Ticket 500 tis. EUR je jen vodítko.
12. **Data a aktivita:** datum jen s přesností zdroje. Datum zápisu do rejstříku není datum investice (plan.md 7.1). Stav `active` zakládá jen nezávisle doložená investice za posledních 24 měsíců, jinak `inactive` (plan.md 7). Starší investice se zapisují také.
13. **Popisné údaje:** hodnota s původem, nebo důvod, proč chybí. AUM není velikost fondu ani součet fondů (plan.md 10, 10.1).
14. **Rozpory mezi zdroji:** přednost má vyšší tier, při stejném tieru novější zdroj (plan.md 9).
    - Obě hodnoty zůstanou v `citations.csv` a v `note` se uvede, která platí a proč. To je log rozporů podle plan.md 9.
    - Když to nejde rozhodnout, stav `conflicting`.
15. **Vyřazení:** kód E1–E10 s citací `rejection`, E9 jen s výsledkem prověření (plan.md 8). Vyřazený záznam zůstává v `investors.csv`, což je log vyřazení podle plan.md 8.
16. **Osobní údaje a doslovnost citací** (plan.md 6.5, datovy-model.md, `citations.csv`):
    - Citace se nikdy neupravuje: žádné výpustky, začernění ani přepis. Jinak by neprošla kontrolou doslovnosti (bod 19).
    - Osobní údaje se chrání **výběrem úryvku**. Cituje se kratší souvislý úsek, který obsahuje jen potřebný profesní údaj (jméno, role, investice). Typicky jen řádek s rolí nebo podílem z výpisu rejstříku, bez data narození a adresy.
    - Když potřebný údaj nejde doložit bez soukromých údajů, použije se jiný úryvek nebo zdroj. Jinak rozhodne autor (bod F).
    - Soukromé údaje se nezapisují ani do hodnot a poznámek.

## E. Zápis a kontrola dat

17. **Zapsat data** do CSV v `data/sample/` (sources, investors, funds, investments, citations).
18. **Spustit validátor.** Chyby opravit, varování projít.

    ```bash
    python3 scripts/validate.py data/sample
    ```

19. **Ověřit doslovnost všech citací v datech.** Kontrola zachytí i znaky změněné při zápisu.

    ```bash
    python3 scripts/check_quotes.py --data data/sample
    ```

20. **Archivace je zatím odložená** a vrátíme se k ní při dokončování pilotu. U každého zdroje zůstává URL, citace a datum přístupu. Varování validátoru `MISSING_ARCHIVE` je do té doby očekávané.

## F. Kdy rozhoduje autor

- není jasné, která právnická osoba je investor, nebo hrozí záměna investorů,
- K2 nebo typ investora nejde z doložených podkladů rozhodnout,
- rozpor, který pravidla v plan.md 9 nerozhodnou,
- vyřazení E9,
- citlivé informace o fyzických osobách,
- zdroj s nejasnými podmínkami použití.

## G. Náklady a technika

- **Agenty spouštět za sebou.** Firecrawl v tarifu Free povoluje zhruba 10 požadavků za minutu.
- **Velká PDF číst jen jednou.** Firecrawl účtuje 1 kredit za stranu.
- **Rozpočet na investora** je podle testů Credo a Presto orientačně 7–8 USD (limit `--max-budget-usd` na každý běh).
- **Klíč a připojení Firecrawlu:** `python3 scripts/firecrawl_mcp.py --check` (klíč nevypisuje).

## Otevřené otázky

- **Archivace** (Wayback Machine nebo jiná): odložena do dokončení pilotu.
- **Automatické párování podle IČO:** zavede se v pilotu, do té doby ručně podle bodu 3. Ani automatické párování nesmí slučovat právnické osoby se samostatnou investiční pravomocí.
- **Sankční seznamy EU a OFAC** (plan.md 9): zatím otevřené, datový model pro ně nemá pole.
- **Otázky z mapy zdrojů:** pokrytí ČR v CEE Funding Map, komerční užití dat obchodního rejstříku, seznam správců podle § 15 ve WS JERRS ([zdroje-cr.md](zdroje-cr.md), kap. 8).
