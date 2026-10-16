#!/usr/bin/env python3
"""Audit pilotu a měření přesnosti (krok 6, results/README.md).

Sestaví auditní tabulky z dat v data/sample a odděleně zapíše tři úrovně ověření:
- automatická kontrola: validátor a doslovnost citací (results/kontrola_citaci.txt),
- kontrola AI (koordinátor): verdikty v AI_REVIEW níže (není to nezávislý audit),
- rozhodnutí sporů AI podle metodiky: AI_DECISIONS (odborné otázky autor delegoval na AI),
- ruční ověření (člověk): results/rucni_kontrola.csv, odpovědi ANO / NE / NEDOKÁŽU URČIT.

Výstupy:
- results/audit_pilot.csv: jeden řádek = jeden kontrolovaný údaj zařazeného investora,
- results/audit_triaz.csv: vzorek kandidátů vyřazených při triáži,
- results/rucni_kontrola.csv: ruční kontrola vybraných údajů (odpovědi autora se zachovají),
- results/presnost.csv: počty a podíly; přesnost jen z ručně ověřených položek.

Použití: python3 scripts/pilot/audit.py [--online]   (--online ověří citace vzorku triáže přímým stažením)

Audit se vztahuje k datům z commitu c96c21e. Po opravách v kroku 8 se nad aktuálními daty znovu
nespouští (hodnoty i ID citací se změnily); pro reprodukci vraťte data/sample na commit c96c21e.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import math
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import export_overview as ov  # noqa: E402
import validate  # noqa: E402

DATA = ROOT / "data/sample"
OUT = ROOT / "results"
TODAY = date(2026, 10, 16)
SEED_TRIAGE = "audit-triaz-2026-10-16"
SEED_SPOT = "audit-rucni-2026-10-16"
TRIAGE_SAMPLE, SPOT_SAMPLE = 5, 12
OK_VERDICTS = {"OK", "OK s výhradou"}

# Kontrola AI (koordinátor), 2026-10-16: přečtení citace v kontextu původního zdroje.
# (verdikt, nalezená chyba či nejistota, navržená oprava). Verdikty: OK, OK s výhradou, chyba, nejistota.
Q1, Q2, Q3, Q4 = "otázka Q1", "otázka Q2", "otázka Q3", "otázka Q4"
AI_REVIEW = {
    # --- Tilia Impact Ventures ---
    "INV-0001/K1": ("OK", "I2: název, sídlo Drtinova 557/10 a osoby se shodují v rejstříku (tier 1), seznamu EIF (tier 2) a na webu.", ""),
    "INV-0001/K2": ("nejistota", f"Investice fondu II schvaluje investiční výbor (jen vlastní zdroj SFDR); tým kola vede (Vestbee, tier 2). GP fondu II doložen jen vlastním zdrojem, vehikl fondu I neznámý ({Q3}).", "Podle rozhodnutí Q3."),
    "INV-0001/K3": ("OK", "4 nezávisle doložené investice za 24 měsíců (Flox, FaceUp, Theorema, Lifeyear) a MIWA 2019.", ""),
    "INV-0001/typ": ("OK", "EIF: Venture Capital; doložené investice jsou menšinové účasti pre-seed až Series A.", ""),
    "INV-0001/zeme": ("OK", "", ""), "INV-0001/mesto": ("OK", "", ""),
    "INV-0001/web": ("OK", "Web tilia.vc; seznam EIF uvádí nefunkční adresu.", ""),
    "INV-0001/sektory": ("OK s výhradou", "„Sector-agnostic, Impact-driven“: impact zaměření číselník sektorů nevyjádří.", ""),
    "INV-0001/faze": ("OK", "Odvozeno z „Early stage“ a fází doložených investic, metoda v citaci.", ""),
    "INV-0001/geografie": ("OK", "„CEE+“ → CEE.", ""),
    "INV-0001/ticket": ("OK", "Deklarovaný počáteční ticket z webu; starší údaj AIN 2023 (do 1,5 mil. EUR) zapsán jako nepoužitý.", ""),
    "INV-0001/aum": ("OK", "Nedatovaný údaj CVCA „ve správě 62,7 mil. Kč“ odpovídá době fondu I; nejasné správně.", ""),
    "INV-0001/hodnoceni": ("OK", "Více nezávislých vydavatelů (Vestbee, JIC, CzechCrunch, Lupa, AIN).", ""),
    "INV-0001/aktivita": ("OK", "FaceUp 2026-05-19 je v okně 24 měsíců.", ""),
    # --- Rockaway Ventures ---
    "INV-0002/K1": ("OK", "I2: tech.eu (značka ve skupině Rockaway Capital), General Partner (tech.eu, Lupa), Praha.", ""),
    "INV-0002/K2": ("nejistota", f"Fond vedou General Partners a investiční výbor z lidí Rockaway (Unquote 2023, CzechCrunch 2021); AMISTA spravuje jen feeder. Auditor: sporné, chybí výpis z lucemburského registru a nevyloučen externí AIFM ({Q2}).", "Podle rozhodnutí Q2; při požadavku na výpis z registru → candidate."),
    "INV-0002/K3": ("OK", "Filuta AI, Remix, AdSpawn (2025–2026).", ""),
    "INV-0002/typ": ("OK", "Menšinové účasti seed až Series A.", ""),
    "INV-0002/zeme": ("OK s výhradou", "AIN přebírá oznámení investora („key locations in Prague and San Francisco“); české osoby značky sídlí v Praze.", ""),
    "INV-0002/mesto": ("OK s výhradou", "Tým i v San Franciscu, sídlo Praha.", ""),
    "INV-0002/web": ("OK", "", ""),
    "INV-0002/sektory": ("OK s výhradou", "Výčet z webu popisuje oblasti od roku 2014; tech.eu 2025 uvádí nové zaměření (energetika, obrana, dual-use). „defence“ → deeptech_hardware je přibližné.", ""),
    "INV-0002/faze": ("OK", "„late seed or Series A“.", ""),
    "INV-0002/geografie": ("OK", "„CEE and Western European countries“ (titulek webu: CEE a DACH).", ""),
    "INV-0002/ticket": ("OK", "Typický ticket nezveřejněn; CzechCrunch 2021 uvádí jen maximum 15 mil. EUR na firmu včetně navazujících investic.", ""),
    "INV-0002/aum": ("OK", "Hodnota portfolia 139 mil. EUR (2022) není AUM.", ""),
    "INV-0002/hodnoceni": ("OK", "Filuta (CzechCrunch, Silicon Canals) a AdSpawn (Vestbee, Startitup). U Remixu jsou Lupa a Euro.cz patrně téhož vydavatele.", ""),
    "INV-0002/aktivita": ("OK", "AdSpawn 2026-04-22.", ""),
    # --- StartupYard ---
    "INV-0003/K1": ("OK", "I2: provozovatel Startup Yard Limited (Companies House, Lupa), sídlo vehiklů Perlová 371/5 (rejstřík).", ""),
    "INV-0003/K2": ("OK s výhradou", f"Vehikla kol řídí ředitel StartupYardu (Lupa 2020, rejstřík). Vehikl Batch 15 vlastní ze 80 % osobně ředitel, Ltd v něm podíl nemá ({Q4}).", ""),
    "INV-0003/K3": ("OK", f"Fungies.io (2 vydavatelé) a Qoobus; Vistag viz {Q4}.", ""),
    "INV-0003/typ": ("OK", "Akcelerátor investuje vlastní hotovost (Lupa 2020: 40 000 USD do každé firmy).", ""),
    "INV-0003/zeme": ("OK", "", ""), "INV-0003/mesto": ("OK", "", ""), "INV-0003/web": ("OK", "", ""),
    "INV-0003/sektory": ("nejistota", "FAQ: „AI, cybersecurity, IoT“, stránka o 15. kole (2025-09): „We're industry-agnostic“. Podle plan.md 9 při stejném tieru platí novější zdroj; FAQ není datované.", "sectors_status conflicting (s citací obou), nebo generalist podle stránky o 15. kole."),
    "INV-0003/faze": ("OK", "", ""), "INV-0003/geografie": ("OK", "", ""),
    "INV-0003/ticket": ("OK s výhradou", "25 000 EUR hotovosti je volitelná součást programu (od 15. kola); in-kind část správně vynechána.", ""),
    "INV-0003/aum": ("OK", "„€105m“ je kapitál získaný absolventy, ne AUM.", ""),
    "INV-0003/hodnoceni": ("OK", "Fungies.io: Business Wire (firma) a tech.eu; dále Lupa 2020.", ""),
    "INV-0003/aktivita": ("OK", "Poslední doložená 2023-07-26; Ydoca 2025 jako unclear se nepočítá.", ""),
    # --- NRI ---
    "INV-0004/K1": ("OK", "I1: IČO 08465797 (rejstřík).", ""),
    "INV-0004/K2": ("OK", "Rejstřík: správa fondu fondů; MPO a Seznam Zprávy: NRI spravuje fond a nakupuje akcie.", ""),
    "INV-0004/K3": ("OK", "Hardwario 2022: NRI mezi novými akcionáři po IPO.", ""),
    "INV-0004/typ": ("nejistota", f"Menšinové úpisy na trhu START, část firem zavedená; úřední název „osoba rizikového kapitálu“ ({Q1}).", "Podle rozhodnutí Q1."),
    "INV-0004/zeme": ("OK", "", ""), "INV-0004/mesto": ("OK", "", ""), "INV-0004/web": ("OK", "", ""),
    "INV-0004/sektory": ("OK", "Zdroje odvětvové zaměření neuvádějí.", ""),
    "INV-0004/faze": ("OK", "Odvozeno z úpisu nových akcií při IPO/SPO.", ""),
    "INV-0004/geografie": ("OK", "Firmy působící v ČR.", ""),
    "INV-0004/ticket": ("OK", "80 mil. Kč je limit programu, správně není ticketem.", ""),
    "INV-0004/aum": ("OK", "500 mil. EUR je zákonný strop § 15.", ""),
    "INV-0004/hodnoceni": ("nejistota", f"Obě citace (Lupa, ČTK/Forbes) přebírají totéž prohlášení Hardwaria; Forbes s překryvem pro členy ({Q1}).", "Podle Q1: pokud nejde o 2 nezávislé důkazy, hodnocení B."),
    "INV-0004/aktivita": ("OK", "Nová přímá investice z IPO Fondu 2025+ nenalezena.", ""),
    # --- Orbit Capital ---
    "INV-0011/K1": ("OK", "I2: EIF (Praha a Varšava), Mews, CzechCrunch, Unquote; partneři.", ""),
    "INV-0011/K2": ("nejistota", f"Investiční výbor a partneři vedou fond (CzechCrunch); GP ani AIFM kapitálového fondu Orbit Growth SCSp neověřeny v registru ({Q3}).", "Podle rozhodnutí Q3."),
    "INV-0011/K3": ("OK", "Mews a Preply (Series C, 2022); dluhové financování správně nezapsáno.", ""),
    "INV-0011/typ": ("OK", "Typ jen podle kapitálových investic (plan.md 9).", ""),
    "INV-0011/zeme": ("OK", "", ""), "INV-0011/mesto": ("OK s výhradou", "Kanceláře v Praze a Varšavě.", ""),
    "INV-0011/web": ("OK", "", ""),
    "INV-0011/sektory": ("OK s výhradou", "„Technology and technology-enabled scale-ups“ → software_saas je přibližné.", ""),
    "INV-0011/faze": ("OK", "", ""),
    "INV-0011/geografie": ("chyba", "Alternative Credit Investor (2026, tier 2) uvádí „CEE region as well as Germany, Austria and Switzerland“; podle plan.md 9 má přednost před profilem CVCA (tier 3).", "geographies CEE;DACH s citací ze zdroje Alternative Credit Investor."),
    "INV-0011/ticket": ("OK", "Deklarované rozpětí pro growth equity (CVCA); dluhové tickety odděleny.", ""),
    "INV-0011/aum": ("OK", "Jen dolní mez „more than €200m“ za obě strategie.", ""),
    "INV-0011/hodnoceni": ("OK", "Mews (tisková zpráva firmy, Forbes) a Preply (PR Newswire, CzechCrunch, Unquote).", ""),
    "INV-0011/aktivita": ("OK", "Poslední kapitálová investice 2022-12; novější financování je dluh.", ""),
    # --- Fondy ---
    "FND-0001": ("OK", "CzechCrunch: cíl 32 mil. EUR, potvrzeno 26 mil. EUR = první uzavření.", ""),
    "FND-0002": ("OK", "Rozhovor 2018: první kolo 43 mil. Kč.", ""),
    "FND-0003": ("OK s výhradou", "Zdroje: „necelých / nearly 55 mil. EUR“; zapsáno 55 000 000 bez příznaku přibližné hodnoty (model ho nemá).", ""),
    "FND-0004": ("OK", "", ""), "FND-0005": ("OK", "306 vs. ~360 mil. Kč, správně zdroje si odporují.", ""),
    "FND-0006": ("OK s výhradou", "Datum 2021-12 odvozeno z „last December“ v článku z 2022-08-31.", ""),
    "FND-0007": ("OK", "Cíl 100 mil. EUR (EIF 2025); druhé uzavření 107 mil. EUR v poznámce.", ""),
    "FND-0008": ("OK", "40 vs. 35 mil. EUR, správně zdroje si odporují.", ""),
    # --- Investice: přiřazení a nástroj ---
    "DEAL-0001/prirazeni": ("OK", "Tilia kolo Seed+ vedla.", ""),
    "DEAL-0002/prirazeni": ("OK", "Tilia jako stávající investor (follow-on).", ""),
    "DEAL-0003/prirazeni": ("OK", "„Mezi investory nechybí … Tilia Impact Ventures“.", ""),
    "DEAL-0004/prirazeni": ("OK", "Tilia mezi VC fondy kapitálové části kola.", ""),
    "DEAL-0005/prirazeni": ("OK", "Konvertibilní půjčka, druhá investice fondu.", ""),
    "DEAL-0006/prirazeni": ("OK", "Rockaway Ventures kolo vedl.", ""),
    "DEAL-0007/prirazeni": ("OK s výhradou", "20% podíl „v rámci aktuálního investičního kola“; Lupa uvádí „částku za prodej“, část může být odkup podílu. Equity v obou případech.", ""),
    "DEAL-0008/prirazeni": ("OK", "", ""),
    "DEAL-0009/prirazeni": ("nejistota", "Podle tiskové zprávy Adevinta dodaly dluh banky a úvěrové instituce, Rockaway je mezi investory equity kola. Nástroj unclear je zřejmě příliš opatrný.", "instrument investment_unspecified (investice by se počítala; Rockaway 4 doložené investice)."),
    "DEAL-0010/prirazeni": ("OK", "", ""), "DEAL-0011/prirazeni": ("OK", "11. kolo, každá firma 40 000 USD.", ""),
    "DEAL-0012/prirazeni": ("nejistota", f"Citace v budoucím čase („získají investici“), titulek „investoval“ ({Q4}).", "Podle rozhodnutí Q4."),
    "DEAL-0013/prirazeni": ("OK", "Unclear správně (možná in-kind nóta, rozpor zdrojů).", ""),
    "DEAL-0014/prirazeni": ("OK", "Nový akcionář po IPO; IPO fond doložen výčtem firem (Seznam Zprávy).", ""),
    "DEAL-0015/prirazeni": ("OK", "Jen vlastní zdroj NRI, správně se nepočítá do K3.", ""),
    "DEAL-0016/prirazeni": ("OK", "Jen vlastní zdroj NRI, správně se nepočítá do K3.", ""),
    "DEAL-0017/prirazeni": ("chyba", "Přiřazení k fondu Orbit Growth SCSp (FND-0006) žádný zdroj neuvádí, byl to odhad koordinátora.", "fund_id prázdné."),
    "DEAL-0018/prirazeni": ("chyba", "Přiřazení k fondu Orbit Growth SCSp (FND-0006) žádný zdroj neuvádí, byl to odhad koordinátora.", "fund_id prázdné."),
    # --- Investice: datum a částky ---
    "DEAL-0001/datum_castky": ("OK", "", ""), "DEAL-0002/datum_castky": ("OK", "Celé kolo 5 mil. USD.", ""),
    "DEAL-0003/datum_castky": ("OK", "3,3 mil. USD (Lupa) = 70 mil. Kč (CzechCrunch).", ""),
    "DEAL-0004/datum_castky": ("OK s výhradou", "Zapsána kapitálová část 1,3 mil. EUR, celé kolo 2,8 mil. EUR včetně grantu.", ""),
    "DEAL-0005/datum_castky": ("OK", "Částka jen slovně, správně nezapsána.", ""),
    "DEAL-0006/datum_castky": ("OK", "", ""), "DEAL-0007/datum_castky": ("OK", "Částka nezveřejněna.", ""),
    "DEAL-0008/datum_castky": ("OK", "", ""), "DEAL-0009/datum_castky": ("OK", "Částka kola zahrnuje dluh, správně nezapsána.", ""),
    "DEAL-0010/datum_castky": ("OK", "", ""), "DEAL-0011/datum_castky": ("OK", "", ""),
    "DEAL-0012/datum_castky": ("OK", "Datum oznámení výběru do kola.", ""),
    "DEAL-0013/datum_castky": ("OK", "", ""), "DEAL-0014/datum_castky": ("OK", "", ""),
    "DEAL-0015/datum_castky": ("OK", "", ""), "DEAL-0016/datum_castky": ("OK", "", ""),
    "DEAL-0017/datum_castky": ("OK s výhradou", "185 mil. USD je celé kolo; podle TechCrunch obsahovalo i malou dluhovou část od jiného věřitele.", ""),
    "DEAL-0018/datum_castky": ("OK", "8 mil. USD z kola 50 mil. USD.", ""),
    # --- Sloučené právnické osoby (E10) ---
    "INV-0005/E10": ("nejistota", f"Jednatelé jsou partneři Tilie, stejné sídlo; role vůči fondům nedoložena ({Q3}).", ""),
    "INV-0006/E10": ("nejistota", f"Jednatel je partner Tilie; v EIF jako správce fondu II; role nedoložena ({Q3}).", ""),
    "INV-0007/E10": ("OK s výhradou", "Vehikl 15. kola, jednatel ředitel StartupYardu; podíly osobně ředitel.", ""),
    "INV-0008/E10": ("OK", "Odštěpný závod provozovatele.", ""),
    "INV-0009/E10": ("OK", "Feeder do lucemburského fondu (KID AMISTA, tisková zpráva).", ""),
    "INV-0010/E10": ("nejistota", f"Představenstvo z lidí Rockaway, role vůči fondu nedoložena ({Q2}).", ""),
    "INV-0012/E10": ("nejistota", f"Společníky jsou partneři Orbitu; EIF ji uvádí jako správce dluhového fondu II ({Q3}).", ""),
    "INV-0013/E10": ("nejistota", f"Jednatel je zakladatel Orbitu; ke kterému fondu je GP, nedoloženo ({Q3}).", ""),
}

# Vzorek vyřazených při triáži: doklady z vlastního webu nebo profilu CVCA (kontrola AI 2026-10-16).
TRIAGE_REVIEW = {
    "Innova Capital": ("https://www.innovacap.com/", "We are an independent private equity firm",
                       "PE (buyout, růstový kapitál, tickety 20–50 mil. EUR); tým ve Varšavě."),
    "Abris Capital": ("https://www.abris-capital.com/",
                      "Abris Capital Partners is the leading ESG transformation specialist private equity investor focused on Central Europe.",
                      "PE (buyout, MBO/MBI); tým ve Varšavě."),
    "CVI": ("https://cvca.cz/cvi/", "Direct Lending, Senior Debt, Mezzanine, Výjimečně minoritní ekvitní investice",
            "Dluhové financování, jen výjimečně menšinová equity; tým ve Varšavě."),
    "Sandberg Capital": ("https://www.sandbergcapital.com/", "zamerané na investovanie do private equity",
                         "PE (buy-and-build, growth, tickety 5–20 mil. EUR); tým v Bratislavě."),
    "Thein": ("https://cvca.cz/thein/", "LBO, Růstový kapitál",
              "PE (LBO, růstový kapitál, průmysl); tým v Praze. Vlastní web thein.eu se nenačetl."),
}

# Rozhodnutí sporů koordinátorem (AI) podle metodiky, 2026-10-16. Autor odborné otázky delegoval na AI;
# co nejde spolehlivě určit, je zapsané jako nejistota. Formát: řádek -> (konečný verdikt, rozhodnutí, oprava).
AI_DECISIONS = {
    "INV-0004/hodnoceni": ("chyba", "Q1: Lupa i ČTK (Forbes) přebírají totéž prohlášení Hardwaria, jde o jeden původ důkazu. "
                           "Pro A je potřeba ≥2 nezávislé důkazy (plan.md 6.3), proto konzervativně B. Metodika výslovně neříká, "
                           "jak počítat více publikací téhož prohlášení (doplnit v kroku 8).", "hodnocení B"),
    "INV-0004/typ": ("OK s výhradou", "Q1: Podle plan.md 4.1, krok 3 rozhoduje převažující charakter doložených investic: menšinové "
                     "(nekontrolní) podíly v rostoucích firmách odpovídají VC, PE vyžaduje kontrolní nebo významné podíly. Úřední název "
                     "„osoba rizikového kapitálu“. Nejistota: firmy jsou kotované na trhu START a část je zavedená; metodika pro "
                     "veřejné úpisy MSP samostatný typ nemá.", ""),
    "INV-0002/K2": ("OK s výhradou", "Q2: K2 doloženo (plan.md 5, K2): fond vedou General Partners z Rockaway a jeho investiční výbor "
                    "tvoří lidé z Rockaway (Unquote 2023, CzechCrunch 2021), tým kola vede (CzechCrunch 2025); AMISTA podle vlastního "
                    "KID obhospodařuje jen feeder. Nelze spolehlivě určit formálního GP a případného AIFM lucemburského fondu "
                    "(registr neověřen); externího AIFM žádný zdroj neuvádí.", ""),
    "INV-0001/K2": ("OK s výhradou", "Q3: K2 doloženo na úrovni týmu: investice fondu II schvaluje investiční výbor Tilie (vlastní "
                    "zdroj, tier 3 stačí podle plan.md 5, K2) a tým kola vede (Vestbee). Nelze spolehlivě určit registraci GP fondu "
                    "II ani vehikl fondu I.", ""),
    "INV-0011/K2": ("OK s výhradou", "Q3: K2 doloženo na úrovni týmu: hlavní partner je členem investičního výboru a partneři fond "
                    "vedou (CzechCrunch 2022 a 2023). Nelze spolehlivě určit GP ani AIFM kapitálového fondu Orbit Growth SCSp.", ""),
    "DEAL-0012/prirazeni": ("nejistota", "Q4: Článek oznamuje výběr do 10. kola, investice je v budoucím čase („získají investici“), "
                            "titulek v minulém. Že investice proběhla, nelze spolehlivě určit. Konzervativně se do K3 nepočítá "
                            "(plan.md 5, K3, bod 2: zdroj musí popisovat vložení kapitálu).",
                            "nepočítat do K3; StartupYard má 2 doložené investice, hodnocení A trvá"),
    "INV-0003/K3": ("OK s výhradou", "Q4: K3 splněno i bez Vistagu (Fungies.io, Qoobus).", "počet doložených investic 2"),
    "INV-0003/K2": ("OK s výhradou", "Q4: K2 doloženo: vehikla kol řídí ředitel StartupYardu (Lupa 2020, rejstřík). Vehikl 15. kola "
                    "vlastní osobně ředitel; nelze spolehlivě určit, zda jedná jen za StartupYard.", ""),
    "INV-0011/geografie": ("chyba", "O1: Novější zdroj tier 2 (Alternative Credit Investor, 2026) uvádí i Německo, Rakousko a "
                           "Švýcarsko; podle plan.md 9 má přednost před profilem CVCA (tier 3).", "geographies CEE;DACH"),
    "DEAL-0017/prirazeni": ("chyba", "O2: Přiřazení k fondu Orbit Growth SCSp žádný zdroj neuvádí.", "fund_id prázdné"),
    "DEAL-0018/prirazeni": ("chyba", "O2: Přiřazení k fondu Orbit Growth SCSp žádný zdroj neuvádí.", "fund_id prázdné"),
    "INV-0003/sektory": ("chyba", "O3: Dva vlastní zdroje si odporují (FAQ: „AI, cybersecurity, IoT“; stránka o 15. kole: "
                         "„We're industry-agnostic“) a FAQ nemá datum, novější zdroj tedy nejde určit. Podle plan.md 9 stav "
                         "conflicting.", "sectors prázdné, sectors_status conflicting, citace obou zdrojů"),
    "DEAL-0009/prirazeni": ("chyba", "O4: Podle tiskové zprávy dodaly dluh „credit and banking institutions“; Rockaway je jmenován "
                            "mezi investory kola vedeného VC fondem. Zdroj výslovně mluví o investorech a formu neuvádí, proto "
                            "investment_unspecified (plan.md 5, K3).", "instrument investment_unspecified; Rockaway 4 doložené investice"),
    "INV-0002/K3": ("OK s výhradou", "O4: K3 splněno; po opravě Spotawheel 4 doložené investice.", "počet doložených investic 4"),
}
for _row in ("INV-0005/E10", "INV-0006/E10", "INV-0010/E10", "INV-0012/E10", "INV-0013/E10"):
    AI_DECISIONS[_row] = ("OK s výhradou", "Q2/Q3: Sloučení podle ověřovacího postupu, bod 3: tytéž osoby a sídlo jako tým, samostatná "
                          "investiční pravomoc nedoložena. Nelze spolehlivě určit přesnou roli vůči fondům.", "")

# Ruční kontrola (člověk), 2026-10-16. Pravidlo: ze všech řádků auditu bez ohledu na verdikt AI, které jde ověřit
# přečtením jedné stránky (sídlo, zaměření, ticket, velikost fondu, investor u investice, datum a částka) a mají zdroj,
# prvních 5 podle SHA-256 z „audit-rucni-2026-10-16|ID řádku“. Otázky jsou faktické, bez odborného posouzení.
CHECKABLE = re.compile(r"/(zeme|mesto|sektory|faze|geografie|ticket|prirazeni|datum_castky)$|^FND-")
HUMAN_CHECK_COUNT = 5
# ID řádku -> [(odkaz, co najít na stránce, otázka, odpověď odpovídající hodnotě v databázi)]
HUMAN_CHECKS = {
    "DEAL-0018/prirazeni": [
        ("https://www.prnewswire.co.uk/news-releases/ukrainian-founded-preply-raises-50-million-usd-series-c-830797049.html",
         "Datum „13 Jul, 2022“ pod titulkem a větu „… as well as new investors such as Swisscom Ventures, and Orbit Capital.“",
         "a) Uvádí tisková zpráva Orbit Capital jako nového investora v kole Series C firmy Preply?", "ANO"),
        ("https://www.prnewswire.co.uk/news-releases/ukrainian-founded-preply-raises-50-million-usd-series-c-830797049.html",
         "Vyhledejte na stránce text „Orbit Growth“ (Ctrl+F).",
         "b) Uvádí stránka, že investice šla z fondu Orbit Growth (Orbit Growth SCSp)?", "ANO"),
    ],
    "INV-0011/geografie": [
        ("https://cvca.cz/orbit-capital/", "Řádek „Geografické zaměření“ v profilu.",
         "a) Uvádí profil jako geografické zaměření jen „CEE - Central and Eastern Europe“?", "ANO"),
        ("https://alternativecreditinvestor.com/2026/07/02/orbit-inks-more-than-e100m-for-venture-debt-fund/",
         "Datum „July 2 2026“ a větu „… across the CEE region as well as Germany, Austria and Switzerland.“",
         "b) Uvádí článek, že se Orbit Capital zaměřuje i na Německo, Rakousko a Švýcarsko?", "NE"),
    ],
    "INV-0002/zeme": [
        ("https://en.ain.ua/2025/03/21/culturepulse-raises-eur145m",
         "Odstavec o Rockaway Ventures s větou „… with key locations in Prague and San Francisco.“",
         "Je u Rockaway Ventures uvedena Praha jako jedna z klíčových lokalit?", "ANO"),
    ],
    "FND-0003": [
        ("https://cc.cz/rockaway-ventures-oznamilo-druhy-fond-na-startupy-ma-pripravene-14-miliardy-korun/",
         "Datum „14. 5. 2025“ nad titulkem a větu „… oznámilo uzavření svého druhého fondu o celkové výši „necelých“ 55 milionů eur …“",
         "Píše článek ze 14. 5. 2025, že Rockaway Ventures uzavřelo druhý fond ve výši zhruba 55 milionů eur?", "ANO"),
    ],
    "DEAL-0014/datum_castky": [
        ("https://www.lupa.cz/aktuality/liberecke-hardwario-upsalo-akcie-na-prazske-burze-oceneno-bylo-na-240-milionu/",
         "Datum „18. 10. 2022“ pod titulkem a větu „Mezi novými akcionáři je … také Národní rozvojová investiční, a.s.“",
         "Je článek z 18. 10. 2022 a jmenuje Národní rozvojovou investiční mezi novými akcionáři Hardwaria?", "ANO"),
    ],
}
# 2. kolo (2026-10-16, na pokyn autora: jedna kontrola pro každého z pěti investorů). Pravidlo: pro každého zařazeného
# investora první dosud nekontrolovaný řádek stejného typu (jedna stránka, se zdrojem) podle stejného SHA-256 pořadí.
HUMAN_CHECKS_2 = {
    "DEAL-0005/datum_castky": [
        ("https://cc.cz/silke-horakova-a-petr-vitek-posilaji-miliony-korun-do-startupu-miwa-ktery-z-obchodu-odstranuje-jednorazove-plasty/",
         "Datum „08. 10. 2019“ nad titulkem a větu „Druhou investicí v portfoliu Tilia Impact Ventures se nyní stává společnost MIWA Technologies …“",
         "Je článek z 8. 10. 2019 a píše, že MIWA Technologies se nyní stává investicí v portfoliu Tilia Impact Ventures?", "ANO"),
    ],
    "DEAL-0007/datum_castky": [
        ("https://www.lupa.cz/aktuality/rockaway-investuje-do-evropskeho-digitalniho-second-hand-giganta-tahne-ho-umela-inteligence/",
         "Datum „19. 12. 2025“ pod titulkem a větu „Rockaway Ventures získává 20% podíl v Remixu …“",
         "Je článek z 19. 12. 2025 a píše, že Rockaway Ventures získává 20% podíl v Remixu?", "ANO"),
    ],
    "INV-0003/mesto": [
        ("https://startupyard.com/faq", "Odpověď na otázku „What is StartupYard?“ s větou „StartupYard, based in beautiful Prague, …“",
         "Uvádí stránka, že StartupYard sídlí v Praze?", "ANO"),
    ],
    "DEAL-0015/prirazeni": [
        ("https://www.nrinvesticni.cz/skupina-cmzrb-nakoupila-podil-v-ceske-firme-vyrabejici-bezpilotni-letouny/",
         "Datum „21.05.2021“ a větu „Prostřednictvím programu Rizikový kapitál - IPO fond nakoupila 12,7% podíl z nově vydaných akcií "
         "společnosti Primoco UAV …“. Podmětem je „ČMZRB investiční“ (dřívější název NRI podle obchodního rejstříku).",
         "Píše stránka, že ČMZRB investiční nakoupila prostřednictvím programu „Rizikový kapitál - IPO fond“ podíl z nově vydaných akcií společnosti Primoco UAV?", "ANO"),
    ],
    "INV-0011/zeme": [
        ("https://www.eif.org/files/attachments/czechia-equity-fundmanagers.pdf",
         "V tabulce (PDF) řádek „Orbit Growth Debt II | OGD Advisory s.r.o. | Czech Republic“, sloupec „Team location“.",
         "Je u fondu Orbit Growth Debt II ve sloupci Team location uvedeno „Czech Republic“?", "ANO"),
    ],
}
ANSWERS = ("ANO", "NE", "NEDOKÁŽU URČIT")


def read(name):
    with (DATA / name).open(encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def order_key(seed, text):
    return hashlib.sha256(f"{seed}|{text}".encode("utf-8")).hexdigest()


def wilson(k, n, z=1.96):
    if n == 0:
        return ("–", "–")
    p = k / n
    centre = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return (f"{max(0, centre - half):.0%}", f"{min(1, centre + half):.0%}")


def quote_status():
    """citation_id -> stav doslovnosti z results/kontrola_citaci.txt."""
    status, path = {}, OUT / "kontrola_citaci.txt"
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            match = re.match(r"(CIT-\d+)\s+(\S+)", line)
            if match:
                status[match.group(1)] = match.group(2)
    return status


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--online", action="store_true")
    args = parser.parse_args()
    report = validate.validate(DATA, TODAY)
    summaries = {s.investor_id: s for s in report.investors}
    issues = {}
    for issue in report.errors:
        issues.setdefault(issue.entity_id, []).append(issue.code)
    investors = {r["investor_id"]: r for r in read("investors.csv")}
    funds = read("funds.csv")
    deals = {d["deal_id"]: d for d in read("investments.csv")}
    citations = read("citations.csv")
    urls = {s["source_id"]: s["url"] for s in read("sources.csv")}
    verbatim = quote_status()

    def cites(entity, fields):
        found = [c for c in citations if c["entity_id"] == entity
                 and set(validate.split_list(c["fields"])) & set(fields)]
        return found

    def src_text(found):
        return " | ".join(f"{urls[c['source_id']]} ({c['citation_id']})" for c in found) or "–"

    def auto_text(entity, found):
        bad = [c["citation_id"] for c in found if verbatim.get(c["citation_id"]) != "DOSLOVNĚ"]
        parts = [f"validátor: {', '.join(issues[entity])}" if entity in issues else "validátor: bez chyb"]
        if found:
            parts.append(f"doslovnost: {len(found) - len(bad)}/{len(found)}" + (f" (problém: {', '.join(bad)})" if bad else ""))
        return "; ".join(parts)

    rows = []
    found_by_row = {}

    def add(row_id, investor, label, value, entity, found):
        verdict, finding, fix = AI_REVIEW[row_id]
        decision = ""
        if row_id in AI_DECISIONS:
            verdict, decision, fix = AI_DECISIONS[row_id]
        found_by_row[row_id] = found
        rows.append({"ID řádku": row_id, "Investor": investor, "Kontrolovaný údaj": label, "Původní hodnota": value,
                     "Zdroj (URL a citace)": src_text(found), "Automatická kontrola": auto_text(entity, found),
                     "Kontrola AI (koordinátor)": verdict, "Nalezená chyba či nejistota": finding,
                     "Rozhodnutí sporu (AI podle metodiky)": decision,
                     "Navržená oprava": fix, "Ruční ověření (člověk)": "neověřeno"})

    included = [i for i, r in investors.items() if r["record_status"] == "included"]
    for iid in included:
        r, s, name = investors[iid], summaries[iid], investors[iid]["name"]
        own_deals = [d for d in deals.values() if d["investor_id"] == iid]
        add(f"{iid}/K1", name, "K1 identita", f"{r['identity_level']} {r['registry_type']} {r['registry_id']}".strip(), iid, cites(iid, ("identity",)))
        add(f"{iid}/K2", name, "K2 rozhodovací pravomoc", "doloženo" if s.k2_verified else "nedoloženo", iid, cites(iid, ("decision_authority",)))
        k3_cites = [c for d in s.documented_deal_ids for c in cites(d, ("deal",))]
        add(f"{iid}/K3", name, "K3 doložené investice", f"{s.documented_deals} ({', '.join(deals[d]['company_name'] for d in s.documented_deal_ids)})", iid, k3_cites)
        add(f"{iid}/typ", name, "typ / podtyp", f"{r['primary_type']} / {r['subtype'] or '–'}", iid, cites(iid, ("primary_type",)))
        add(f"{iid}/zeme", name, "země", r["country"], iid, cites(iid, ("country",)))
        add(f"{iid}/mesto", name, "město týmu", r["city"], iid, cites(iid, ("city",)))
        add(f"{iid}/web", name, "web", r["website"], iid, [])
        add(f"{iid}/sektory", name, "sektory", ov.with_status(ov.listed(r["sectors"], ov.SECTORS), r["sectors_status"]), iid, cites(iid, ("sectors",)))
        add(f"{iid}/faze", name, "fáze", ov.with_status(ov.listed(r["stages"], ov.STAGES), r["stages_status"]), iid, cites(iid, ("stages",)))
        add(f"{iid}/geografie", name, "investiční geografie", ov.with_status(ov.listed(r["geographies"], {**ov.COUNTRY_NAMES, **ov.REGIONS}), r["geographies_status"]), iid, cites(iid, ("geographies",)))
        add(f"{iid}/ticket", name, "typická investice (ticket)", ov.ticket(r), iid, cites(iid, ("ticket",)))
        add(f"{iid}/aum", name, "AUM", ov.aum(r), iid, cites(iid, ("aum",)))
        add(f"{iid}/hodnoceni", name, "hodnocení spolehlivosti", s.confidence_grade, iid, k3_cites)
        add(f"{iid}/aktivita", name, "aktivita a poslední doložená investice",
            f"{s.activity_status}, {deals[s.last_deal_id]['company_name'] if s.last_deal_id else '–'} ({s.last_investment_date or '–'})", iid, [])
        for f in (f for f in funds if f["investor_id"] == iid):
            add(f["fund_id"], name, f"fond: {f['name']}", ov.fund_text(f), f["fund_id"], cites(f["fund_id"], ("fund", "size")))
        for d in own_deals:
            fund = f", fond {d['fund_id']}" if d["fund_id"] else ""
            add(f"{d['deal_id']}/prirazeni", name, f"investice {d['company_name']}: přiřazení a nástroj",
                f"{d['instrument']}, {d['round_stage']}, follow-on {d['is_follow_on']}{fund}", d["deal_id"], cites(d["deal_id"], ("deal",)))
            amounts = ", ".join(x for x in (
                f"kolo {ov.money(d['round_amount'], d['round_currency'])}" if d["round_amount"] else "",
                f"investor {ov.money(d['investor_amount'], d['investor_currency'])}" if d["investor_amount"] else "") if x)
            add(f"{d['deal_id']}/datum_castky", name, f"investice {d['company_name']}: datum a částky",
                f"{d['investment_date'] or '–'} ({d['date_basis'] or '–'}){'; ' + amounts if amounts else ''}", d["deal_id"],
                cites(d["deal_id"], ("investment_date", "round_amount", "investor_amount")))
        for e in (e for e in investors.values() if e["merged_into"] == iid):
            add(f"{e['investor_id']}/E10", name, f"sloučení E10: {e['name']}", f"E10 → {iid}, {e['registry_id']}",
                e["investor_id"], cites(e["investor_id"], ("identity", "rejection")))
    missing = set(AI_REVIEW) - {r["ID řádku"] for r in rows}
    assert not missing, f"verdikty bez řádku: {missing}"

    # Ruční kontrola: výběr podle pravidla, odpovědi autora se při opakovaném spuštění zachovají.
    human_path = OUT / "rucni_kontrola.csv"
    previous = {}
    if human_path.exists():
        with human_path.open(encoding="utf-8") as handle:
            previous = {r["ID"]: r for r in csv.DictReader(handle)}
    by_id = {r["ID řádku"]: r for r in rows}
    eligible = [r for r in rows if CHECKABLE.search(r["ID řádku"]) and found_by_row[r["ID řádku"]]]
    chosen = sorted(eligible, key=lambda r: order_key(SEED_SPOT, r["ID řádku"]))[:HUMAN_CHECK_COUNT]
    assert [r["ID řádku"] for r in chosen] == list(HUMAN_CHECKS), "výběr neodpovídá připraveným kontrolám"
    human_rows, expected_by_id = [], {}
    round1 = {r["ID řádku"] for r in chosen}
    chosen2 = []
    for iid in included:
        own = [r for r in eligible if r["ID řádku"] not in round1
               and (r["ID řádku"].startswith(iid) or found_by_row[r["ID řádku"]] and r["Investor"] == investors[iid]["name"])]
        chosen2.append(sorted(own, key=lambda r: order_key(SEED_SPOT, r["ID řádku"]))[0])
    assert [r["ID řádku"] for r in chosen2] == list(HUMAN_CHECKS_2), "výběr 2. kola neodpovídá připraveným kontrolám"
    checks = {**HUMAN_CHECKS, **HUMAN_CHECKS_2}
    for number, r in enumerate(chosen + chosen2, 1):
        for part, (link, find, question, expected) in enumerate(checks[r["ID řádku"]]):
            cid = f"K{number}" + ("" if len(checks[r["ID řádku"]]) == 1 else "ab"[part])
            old = previous.get(cid, {})
            answer = old.get("Odpověď autora", "").strip().upper()
            assert answer in ("",) + ANSWERS, f"{cid}: neplatná odpověď {answer}"
            expected_by_id[cid] = expected  # očekávaná odpověď se do souboru pro autora nepíše
            human_rows.append({"ID": cid, "Řádek auditu": r["ID řádku"], "Investor": r["Investor"],
                               "Kontrolovaný údaj": r["Kontrolovaný údaj"],
                               "Odkaz": link, "Co najít na stránce": find, "Otázka": question, "Odpověď autora": answer,
                               "Poznámka autora": old.get("Poznámka autora", ""), "Datum": old.get("Datum", "")})
    for row_id in checks:
        parts = [h for h in human_rows if h["Řádek auditu"] == row_id]
        if all(h["Odpověď autora"] for h in parts):
            by_id[row_id]["Ruční ověření (člověk)"] = "; ".join(f"{h['ID']}: {h['Odpověď autora']}" for h in parts)
    write(human_path, human_rows)
    write(OUT / "audit_pilot.csv", rows)

    # Vzorek vyřazených při triáži
    candidates = {}
    for c in read("candidates_vyber.csv"):
        candidates.setdefault(c["candidate_id"], c)
    excluded = [c for c in candidates.values() if c["note"].startswith("mimo pilot: typ podle zdroje")]
    sample = sorted(excluded, key=lambda c: order_key(SEED_TRIAGE, c["name"]))[:TRIAGE_SAMPLE]
    triage_rows = []
    for c in sample:
        url, quote, finding = TRIAGE_REVIEW[c["name"]]
        check = "neověřeno (spusťte s --online)"
        if args.online:
            import check_quotes as cq
            page = cq.fetch_direct(url)
            check = ("DOSLOVNĚ" if page.status == 200 and cq.find_quote(page.text, quote)[0]
                     else f"NEDOSLOVNĚ / HTTP {page.status}")
        triage_rows.append({"Kandidát": f"{c['candidate_id']} {c['name']}", "Důvod vyřazení při triáži": c["note"],
                            "Zdroj (URL)": url, "Citace": quote, "Doslovnost (automaticky)": check,
                            "Kontrola AI (koordinátor)": "vyřazení správné", "Zjištění": finding,
                            "Ruční ověření (člověk)": "neověřeno"})
    write(OUT / "audit_triaz.csv", triage_rows)

    # Počty a přesnost
    def category(row_id):
        if row_id.startswith("FND"):
            return "fondy"
        if row_id.startswith("DEAL"):
            return "investice"
        if row_id.endswith("/E10"):
            return "sloučení E10"
        return "profil investora"
    metrics = []
    for cat in ("profil investora", "fondy", "investice", "sloučení E10", "celkem"):
        part = [r for r in rows if cat == "celkem" or category(r["ID řádku"]) == cat]
        counts = {v: sum(r["Kontrola AI (koordinátor)"] == v for r in part) for v in ("OK", "OK s výhradou", "chyba", "nejistota")}
        ok = counts["OK"] + counts["OK s výhradou"]
        low, high = wilson(ok, len(part))
        metrics.append({"Ukazatel": f"kontrola AI: bez nalezené chyby či nejistoty ({cat})", "Úroveň": "kontrola AI (předběžné, není přesnost)",
                        "Počet": f"{ok}/{len(part)}", "Podíl": f"{ok / len(part):.0%}" if part else "–", "95% interval": f"{low}–{high}",
                        "Poznámka": f"OK {counts['OK']}, OK s výhradou {counts['OK s výhradou']}, chyba {counts['chyba']}, nejistota {counts['nejistota']}"})
    answered = [row_id for row_id in checks
                if all(h["Odpověď autora"] for h in human_rows if h["Řádek auditu"] == row_id)]
    unknown = [row_id for row_id in answered
               if any(h["Odpověď autora"] == "NEDOKÁŽU URČIT" for h in human_rows if h["Řádek auditu"] == row_id)]
    decided = [row_id for row_id in answered if row_id not in unknown]
    correct = [row_id for row_id in decided if all(h["Odpověď autora"] == expected_by_id[h["ID"]]
                                                     for h in human_rows if h["Řádek auditu"] == row_id)]
    agree = [row_id for row_id in decided
             if (row_id in correct) == (by_id[row_id]["Kontrola AI (koordinátor)"] in OK_VERDICTS)]
    for label, k, n, note in (
            ("údaj v databázi je podle ruční kontroly správný", len(correct), len(decided),
             f"zodpovězeno {len(answered)} z {len(checks)}, nelze určit {len(unknown)}"),
            ("kontrola AI se shoduje s ruční kontrolou", len(agree), len(decided), "shoda verdiktu AI (OK / chyba) s výsledkem člověka")):
        low, high = wilson(k, n)
        metrics.append({"Ukazatel": label, "Úroveň": "ruční ověření", "Počet": f"{k}/{n}",
                        "Podíl": f"{k / n:.0%}" if n else "–", "95% interval": f"{low}–{high}", "Poznámka": note})
    # Ukazatele po rozhodnutí sporů (AI podle metodiky; ručně ověřené jsou jen řádky z ruční kontroly).
    verdict = {r["ID řádku"]: r["Kontrola AI (koordinátor)"] for r in rows}
    criteria = ("K1", "K2", "K3", "typ")
    inclusion_ok = [iid for iid in included if all(verdict[f"{iid}/{c}"] in OK_VERDICTS for c in criteria)]
    grade_ok = [iid for iid in included if verdict[f"{iid}/hodnoceni"] in OK_VERDICTS]
    documented = [d for iid in included for d in summaries[iid].documented_deal_ids]
    fund_only = {"DEAL-0017/prirazeni", "DEAL-0018/prirazeni"}  # chyba jen v přiřazení k fondu
    deals_ok = [d for d in documented
                if (verdict[f"{d}/prirazeni"] in OK_VERDICTS or f"{d}/prirazeni" in fund_only)
                and verdict[f"{d}/datum_castky"] in OK_VERDICTS]
    with_fund = [d for d in deals if deals[d]["fund_id"]]
    fund_ok = [d for d in with_fund if f"{d}/prirazeni" not in fund_only]
    for label, k, n, note in (
            ("zařazení investoři splňují K1–K3 a typ (po rozhodnutí sporů)", len(inclusion_ok), len(included),
             "rozhodnutí AI podle metodiky, s nejistotami k právním strukturám; člověk K1–K3 přímo neověřoval"),
            ("hodnocení spolehlivosti A/B správně", len(grade_ok), len(included), "NRI: A → B (jeden původ důkazu)"),
            ("doložené investice (K3) se správným investorem, firmou, nástrojem a datem", len(deals_ok), len(documented),
             "1 nejistá (Vistag, zdroj v budoucím čase); ručně ověřeny 4 z nich (Preply, Hardwario, MIWA, Remix), všechny správně"),
            ("přiřazení investice k fondu doloženo zdrojem", len(fund_ok), len(with_fund),
             "Mews a Preply přiřazeny k fondu bez zdroje; ručně ověřeno Preply (chyba, K1b) a Primoco UAV (správně, K9)")):
        low, high = wilson(k, n)
        metrics.append({"Ukazatel": label, "Úroveň": "kontrola AI a rozhodnutí sporů", "Počet": f"{k}/{n}",
                        "Podíl": f"{k / n:.0%}" if n else "–", "95% interval": f"{low}–{high}", "Poznámka": note})
    metrics.append({"Ukazatel": "vyřazení při triáži potvrzeno (vzorek)", "Úroveň": "kontrola AI (předběžné)",
                    "Počet": f"{len(triage_rows)}/{len(triage_rows)}", "Podíl": "100%", "95% interval": "%s–%s" % wilson(len(triage_rows), len(triage_rows)),
                    "Poznámka": "5 z 17 vyřazených podle typu; ruční ověření neproběhlo"})
    write(OUT / "presnost.csv", metrics)
    print(f"audit: {len(rows)} řádků, triáž: {len(triage_rows)}, ruční kontrola: {len(human_rows)} otázek ({len(answered)} z {len(checks)} údajů zodpovězeno)")
    for m in metrics:
        print(f"  {m['Ukazatel']}: {m['Počet']} = {m['Podíl']} (95% {m['95% interval']}); {m['Poznámka']}")


def write(path, rows):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
