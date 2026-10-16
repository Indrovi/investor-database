"""Rozhodnutí koordinátora pro data pilotu (podle plan.md, datovy-model.md a ověřovacího postupu).

Soubor je zároveň záznam rozhodnutí v pořadí, jak vznikala: první vyhodnocení, přehodnocení K1–K3,
oprava duplicity ve výběru, pátý kandidát a doplnění přehledu. Pozdější oddíly upravují dřívější.

Odkaz na tvrzení: "CAN-ID:S:číslo" (průzkumník) nebo "CAN-ID:A:číslo" (nový důkaz auditora).
"""

# --- Tier zdrojů (plan.md 6.1), určuje koordinátor ---
TIER = {
    # Tilia Impact Ventures (CAN-0025)
    "https://or.justice.cz/ias/ui/rejstrik-firma.vysledky?subjektId=1189360&typ=PLATNY": "1",
    "https://or.justice.cz/ias/ui/rejstrik-firma.vysledky?subjektId=1182186&typ=PLATNY": "1",
    "https://or.justice.cz/ias/ui/rejstrik-$firma?nazev=Tila+Impact&jenPlatne=VSECHNY&polozek=50": "1",
    "https://tilia.vc/": "3",
    "https://tilia.vc/sfdr/": "3",
    "https://cvca.cz/tilia-impact-ventures/": "3",
    "https://www.eif.org/files/attachments/czechia-equity-fundmanagers.pdf": "2",
    "https://cc.cz/cesky-fond-urceny-na-investice-se-spolecenskymi-dopady-ma-dalsich-600-milionu-podporili-ho-winkler-ci-barta/": "2",
    "https://cc.cz/silke-horakova-a-petr-vitek-z-noveho-tilia-impact-ventures-chybel-nam-rizikovy-kapital-pro-socialni-inovace/": "3",
    "https://cc.cz/silke-horakova-a-petr-vitek-posilaji-miliony-korun-do-startupu-miwa-ktery-z-obchodu-odstranuje-jednorazove-plasty/": "2",
    "https://cc.cz/prvni-startup-prodali-za-stamiliony-ted-stavi-dalsi-diky-ai-jsme-30krat-rychlejsi-na-nic-necekame/": "2",
    "https://www.lupa.cz/aktuality/ai-agenti-noveho-ceskeho-startupu-maji-desitky-milionu-aby-urychlily-vedecky-vyzkum-a-vyvoj/": "2",
    "https://www.jic.cz/en/about-us/pro-media/prvni-investice-noveho-fondu-jic-ventures-miri-do": "2",
    "https://vestbee.com/insights/articles/flox-intelligence-raises-3-m": "2",
    "https://en.ain.ua/2025/07/01/lifeyear-raises-eur28m/": "2",
    "https://en.ain.ua/2023/09/21/czech-tilia-impact-ventures-launches-32m-second-fund": "2",
    "https://www.newstream.cz/trhy/podarilo-se-novy-fond-silke-horakove-a-spol-upsal-stamiliony": "2",
}
SOURCE_OVERRIDES = {
    "https://www.eif.org/files/attachments/czechia-equity-fundmanagers.pdf": {
        "title": "Czechia equity fund managers", "accessed_date": "2026-10-15"},
}

T = "CAN-0025"
INVESTORS = [
    {
        "investor_id": "INV-0001", "record_status": "candidate", "name": "Tilia Impact Ventures",
        "primary_type": "vc", "country": "CZ", "website": "https://www.tilia.vc/",
        "sectors": "generalist", "sectors_original": "Sector-agnostic", "sectors_status": "reported",
        "stages": "pre_seed;seed;series_a", "stages_status": "derived",
        "geographies": "CEE", "geographies_status": "reported",
        "ticket_min": "300000", "ticket_max": "1200000", "ticket_currency": "EUR", "ticket_status": "reported",
        "aum_status": "ambiguous",
        "notes": ("Kandidát: K1 nerozhodnuto. Značka je jednoznačná (web, sídlo Drtinova 557/10, osoby), "
                  "ale není doloženo, která právnická osoba je investor: Tilia Impact Ventures, osoba rizikového "
                  "kapitálu, s.r.o. (IČO 17848911, předmět § 15 ZISIF), Tilia Impact Partners s.r.o. (IČO 17621615, "
                  "poradenství; v seznamu EIF jako správce „Tila Impact Partners“), nebo Tilia Impact Ventures II "
                  "GP S.à r.l. (GP fondu II podle SFDR, neověřeno v registru). Rozhodne autor (overovaci-postup.md, "
                  "bod 3 a F). K2 doloženo na úrovni týmu (investiční výbor), K3 splněno (5 investic, poslední "
                  "2026-05-19). Kandidát CAN-0028 je tentýž subjekt."),
        "cites": [
            (f"{T}:S:A1", "identity", "Jedna z právnických osob značky (§ 15 ZISIF). Zda je investorem, nerozhodnuto (K1)."),
            (f"{T}:S:A5", "identity", "Druhá právnická osoba značky (poradenství). Zda je investorem, nerozhodnuto (K1)."),
            (f"{T}:S:A8", "identity", "Párování CAN-0028: subjekt „Tila Impact“ v rejstříku neexistuje, „Tila“ v seznamu EIF je překlep."),
            (f"{T}:S:A11", "primary_type", "VC podle klasifikace EIF a charakteru doložených investic: minoritní účasti v kolech pre-seed až Series A (DEAL-0001 až 0005)."),
            (f"{T}:S:B1", "decision_authority", "K2 na úrovni týmu: investice fondu II schvaluje investiční výbor. Kterou právnickou osobou výbor jedná, nedoloženo."),
            (f"{T}:S:A9", "decision_authority", "Formálním správcem fondu II je podle vlastního zdroje lucemburský GP (neověřeno v registru)."),
            (f"{T}:S:B4", "country", ""),
            (f"{T}:S:A10", "country", "Team location: Czech Republic (pilotní podmínka plan.md 11.1)."),
            (f"{T}:S:D1", "sectors;stages;geographies;ticket",
             "Fáze odvozeny: „Early stage“ převedeno na pre_seed;seed;series_a podle fází doložených investic. "
             "„CEE+“ zapsáno jako CEE. Ticket je počáteční investice."),
            (f"{T}:A:A19", "ticket", "Starší údaj (2023, tvrzení fondu převzaté médiem): do 1,5 mil. EUR. Nepoužito, platí novější údaj z webu (plan.md 9)."),
            (f"{T}:S:D3", "ticket", "Zastaralý nedatovaný profil CVCA (1–5 mil. Kč). Nepoužito."),
            (f"{T}:S:D2", "aum", "Nedatovaný údaj „ve správě“ z profilu CVCA, zřejmě z doby fondu I. Nejasné, co představuje, AUM nezapsáno."),
        ],
    },
]

FUNDS = [
    {"fund_id": "FND-0001", "investor_id": "INV-0001", "name": "Tilia Impact Ventures Fund II",
     "vintage_year": "2023", "size_amount": "26000000", "size_currency": "EUR", "size_type": "first_close",
     "size_as_of": "2023-09-21", "size_status": "reported",
     "notes": ("Cíl 32 mil. EUR. Názvy ve zdrojích: „Tila Impact Ventures Fund II“ (EIF), „Impact Seed Fund“ "
               "(CzechCrunch). Správce podle SFDR Tilia Impact Ventures II GP S.à r.l. LP: EIF a Česká spořitelna. "
               "Domicil a konečná velikost nedoloženy."),
     "cites": [
         (f"{T}:S:A9", "fund", ""),
         (f"{T}:S:A10", "fund", "Seznam EIF (LP fondu); název s překlepem „Tila“."),
         (f"{T}:A:A17", "fund", "LP fondu: EIF a Česká spořitelna."),
         (f"{T}:S:D4", "size", "26 mil. EUR potvrzeno = first_close; 32 mil. EUR je cíl."),
     ]},
    {"fund_id": "FND-0002", "investor_id": "INV-0001", "name": "Tilia Impact Ventures – první fond (název neuveden)",
     "vintage_year": "2018", "size_amount": "43000000", "size_currency": "CZK", "size_type": "first_close",
     "size_as_of": "2018-11-28", "size_status": "reported",
     "notes": "Výrok investora v rozhovoru. Cíl „necelých 60 mil. Kč“, konečná velikost a právnická osoba fondu nedoloženy.",
     "cites": [(f"{T}:S:D6", "fund;size", "")]},
]

DEALS = [
    {"deal_id": "DEAL-0001", "investor_id": "INV-0001", "company_name": "Flox Intelligence",
     "investment_date": "2026-02-25", "date_basis": "announcement", "instrument": "investment_unspecified",
     "round_stage": "seed", "is_follow_on": "unknown", "round_amount": "3000000", "round_currency": "USD",
     "notes": "Kolo Seed+, Tilia ho vedla. TechCrunch (2026-10-13) zmiňuje zpětně i dřívější seed kolo; nepoužito.",
     "cites": [(f"{T}:A:A12", "deal", ""), (f"{T}:A:A13", "round_amount;investment_date", "")]},
    {"deal_id": "DEAL-0002", "investor_id": "INV-0001", "company_name": "FaceUp",
     "investment_date": "2026-05-19", "date_basis": "announcement", "instrument": "investment_unspecified",
     "round_stage": "series_a", "is_follow_on": "true", "round_amount": "5000000", "round_currency": "USD",
     "notes": "Tilia jako stávající investor. Článek Forbes (2026-05-19) to potvrzuje, ale může být jen pro členy, proto se necituje.",
     "cites": [(f"{T}:S:C2", "deal;investment_date", "Oznámení JIC, zakladatele spoluinvestora JIC Ventures."),
               (f"{T}:S:C3", "round_amount", "Celé kolo, částka Tilie neuvedena.")]},
    {"deal_id": "DEAL-0003", "investor_id": "INV-0001", "company_name": "Theorema",
     "investment_date": "2026-03-27", "date_basis": "announcement", "instrument": "investment_unspecified",
     "round_stage": "pre_seed", "is_follow_on": "unknown", "round_amount": "3300000", "round_currency": "USD",
     "notes": "CzechCrunch uvádí 70 mil. Kč (přepočet téhož kola).",
     "cites": [(f"{T}:A:A16", "deal", ""), (f"{T}:S:C5", "round_amount;investment_date", "Celé kolo.")]},
    {"deal_id": "DEAL-0004", "investor_id": "INV-0001", "company_name": "Lifeyear",
     "investment_date": "2025-07-01", "date_basis": "announcement", "instrument": "investment_unspecified",
     "round_stage": "unknown", "is_follow_on": "unknown", "round_amount": "1300000", "round_currency": "EUR",
     "notes": "Kolo 2,8 mil. EUR zahrnuje grant 1,5 mil. EUR (není investice); kapitálová část 1,3 mil. EUR.",
     "cites": [(f"{T}:A:A14", "deal;round_amount;investment_date", "")]},
    {"deal_id": "DEAL-0005", "investor_id": "INV-0001", "company_name": "MIWA Technologies",
     "investment_date": "2019-10-08", "date_basis": "announcement", "instrument": "convertible_loan",
     "round_stage": "unknown", "is_follow_on": "false",
     "notes": "Starší investice z doby fondu I (K3 nemá časový limit). Částka jen slovně („nižší jednotky milionů korun“).",
     "cites": [(f"{T}:S:C8", "deal;investment_date", ""),
               (f"{T}:S:C9", "deal", "Nástroj: konvertibilní půjčka.")]},
]

CANDIDATES = {
    "CAN-0025": {"investor_id": "INV-0001"},
    "CAN-0028": {"investor_id": "INV-0001", "note": (
        "Spárováno s CAN-0025 (tentýž subjekt): „Tila“ je překlep v seznamu EIF. V rejstříku žádná „Tila Impact“ "
        "není, Tilia Impact Partners s.r.o. má stejné sídlo jako Tilia, fond II i LP EIF se shodují. Samostatně "
        "se neověřoval.")},
}

# Oprava párování zjištěná při ověření: nález se odděluje jako nový kandidát.
SPLITS = {
    ("CAN-0055", "Rockaway Capital Partners"): ("CAN-0075", (
        "Odděleno od CAN-0055 při ověření: odkaz vede na skupinu Rockaway Capital, která investuje sama "
        "(jiný investor než Rockaway Ventures, plan.md 3.1 a overovaci-postup.md bod 3). Neověřováno.")),
}

# --- Rockaway Ventures (CAN-0055) ---
R = "CAN-0055"
TIER.update({
    "https://rockawayventures.com/": "3",
    "https://rockawayventures.com/team/": "3",
    "https://en.ain.ua/2025/03/21/culturepulse-raises-eur145m": "2",
    "https://tech.eu/2025/05/16/rockaway-ventures-closes-55m-fund-to-back-transformative-tech-in-cee-and-beyond/": "2",
    "https://cc.cz/rockaway-ventures-oznamilo-druhy-fond-na-startupy-ma-pripravene-14-miliardy-korun/": "2",
    "https://cc.cz/budeme-jeden-z-nejsilnejsich-tymu-pro-vyvoj-umele-inteligence-v-cesku-veri-ziskal-na-to-sto-milionu/": "2",
    "https://siliconcanals.com/pragues-filuta-ai-secures-3-6m/": "2",
    "https://www.lupa.cz/aktuality/rockaway-investuje-do-evropskeho-digitalniho-second-hand-giganta-tahne-ho-umela-inteligence/": "2",
    "https://www.euro.cz/aktuality/rockaway-ventures-kupuji-petinovy-podil-v-bulharskem-remixu-ktery-se-specializuje-na-second-hand-modu-a-recommerce/": "2",
    "https://www.vestbee.com/insights/articles/ad-spawn-raises-500k": "2",
    "https://www.startitup.sk/bratislavski-inovatori-postavili-stroj-na-vyrobu-pozornosti-idu-dobyt-trh-v-usa-investori-im-posielaju-pol-miliona-eur/": "2",
    "https://adevinta.com/press-releases/adevinta-ventures-announces-investment-in-spotawheels-series-b-e110m-funding-round/": "2",
    "https://globalventuring.com/corporate/spotawheel-drives-to-105m-round/": "2",
    "https://or.justice.cz/ias/ui/rejstrik-firma.vysledky?subjektId=1149228&typ=PLATNY": "1",
    "https://or.justice.cz/ias/ui/rejstrik-firma.vysledky?subjektId=1149228&typ=UPLNY": "1",
    "https://or.justice.cz/ias/ui/rejstrik-firma.vysledky?subjektId=985293&typ=PLATNY": "1",
    "https://or.justice.cz/ias/ui/rejstrik-firma.vysledky?subjektId=1145747&typ=PLATNY": "1",
})
SOURCE_OVERRIDES.update({
    "https://or.justice.cz/ias/ui/rejstrik-firma.vysledky?subjektId=1149228&typ=UPLNY": {
        "title": "Úplný výpis z OR: Rockaway Ventures Fund SICAV a.s.", "accessed_date": "2026-10-16"},
})
INVESTORS.append({
    "investor_id": "INV-0002", "record_status": "candidate", "name": "Rockaway Ventures",
    "primary_type": "vc", "country": "CZ", "website": "https://rockawayventures.com/",
    "sectors": "ecommerce_retail;consumer;logistics;media_gaming;cybersecurity;deeptech_hardware;cleantech_energy;proptech_construction",
    "sectors_original": "retail and e-commerce;travel & hospitality;digital logistics;digital media;cybersecurity;defence;CleanTech;PropTech",
    "sectors_status": "reported",
    "stages": "seed;series_a", "stages_status": "reported",
    "geographies": "CEE;EUROPE", "geographies_status": "reported",
    "ticket_status": "not_public", "aum_status": "not_public",
    "notes": ("Kandidát: K1 a K2 nerozhodnuto. Značka má nejméně 8 právnických osob se sídlem Generála Píky 430/26 "
              "(mj. Rockaway Ventures a.s., Rockaway Ventures Advisors a.s., Rockaway Ventures Fund Holding a.s., "
              "Rockaway GP a.s.). Fond Rockaway Ventures Fund SICAV a.s. (IČO 14235781) je vehikl (E10) a formálně ho "
              "obhospodařuje externí AMISTA investiční společnost; lucemburský GP Rockaway Venture Partners (GP) S.à r.l. "
              "je jen vlastní tvrzení. Dealy vede tým (General Partners). Která osoba je investor, rozhodne autor "
              "(overovaci-postup.md, bod 3 a F). Rockaway Capital SE investuje i sama a je LP fondu: samostatný investor, "
              "neslučovat. K3 splněno (Filuta AI, Remix, AdSpawn). Apptronik a CulturePulse nezapsány: účast doložena "
              "jen oznámením investora nebo bez výslovné investice. AUM nezveřejněno; hodnota portfolia 139 mil. EUR "
              "(2022) není AUM."),
    "cites": [
        (f"{R}:S:C9", "identity", "Rockaway Ventures a.s. (IČO 06387136), jediný akcionář Rockaway Capital SE. Investiční činnost v rejstříku nedoložena."),
        (f"{R}:S:C10", "identity", "Rockaway Ventures Advisors a.s. (IČO 14125129). Role vůči fondu nedoložena."),
        (f"{R}:S:C21", "primary_type;stages;geographies",
         "VC: minoritní účasti v kolech seed až Series A (DEAL-0006 až 0008). „late seed“ zapsáno jako seed, "
         "„Western European countries“ jako EUROPE."),
        (f"{R}:S:C13", "decision_authority", "Tým: General Partner spoluvede Rockaway Ventures. Mandát vůči fondu nedoložen."),
        (f"{R}:A:A19", "decision_authority", "Formálně: statutárním orgánem fondu (SICAV) je od 2022 externí AMISTA investiční společnost."),
        (f"{R}:S:C15", "country", "Text vychází z oznámení investora (tier 3 obsah). Všechny české osoby značky sídlí v Praze."),
        (f"{R}:S:C20", "sectors", "„defence“ zařazeno pod deeptech_hardware, „travel & hospitality“ pod consumer. Tech.eu (2025) uvádí nové zaměření na energetiku, obranu a dual-use."),
    ],
})
FUNDS.append(
    {"fund_id": "FND-0003", "investor_id": "INV-0002", "name": "Rockaway Ventures Fund (Rockaway Ventures II)",
     "vintage_year": "2022", "domicile_country": "CZ", "size_amount": "55000000", "size_currency": "EUR",
     "size_type": "final_close", "size_as_of": "2025-05-14", "size_status": "reported",
     "notes": ("Zdroje uvádějí „necelých“ / „nearly“ 55 mil. EUR. Cíl byl 100 mil. EUR (2022). Vehikl Rockaway Ventures "
               "Fund SICAV a.s. (IČO 14235781). Asi čtvrtina kapitálu od Rockaway Capital (LP). Investice před rokem "
               "2022 šly bez formálního fondu."),
     "cites": [(f"{R}:S:C6", "fund", "Vehikl: fond kvalifikovaných investorů (SICAV)."),
               (f"{R}:A:A9", "fund;size", ""),
               (f"{R}:S:C17", "fund;size", "")]})
DEALS.extend([
    {"deal_id": "DEAL-0006", "investor_id": "INV-0002", "company_name": "Filuta AI",
     "investment_date": "2025-06-24", "date_basis": "announcement", "instrument": "investment_unspecified",
     "round_stage": "seed", "is_follow_on": "unknown", "round_amount": "4200000", "round_currency": "USD",
     "notes": "Rockaway Ventures kolo vedl.",
     "cites": [(f"{R}:A:A7", "deal", ""), (f"{R}:A:A8", "round_amount;investment_date", ""),
               (f"{R}:S:C27", "deal;round_amount", "Druhý vydavatel (2025-06-25).")]},
    {"deal_id": "DEAL-0007", "investor_id": "INV-0002", "company_name": "Remix",
     "investment_date": "2025-12-19", "date_basis": "announcement", "instrument": "equity",
     "round_stage": "unknown", "is_follow_on": "unknown",
     "notes": "20% podíl, částka nezveřejněna. Euro.cz: v rámci aktuálního investičního kola.",
     "cites": [(f"{R}:S:C24", "deal;investment_date", ""), (f"{R}:A:A12", "deal", "")]},
    {"deal_id": "DEAL-0008", "investor_id": "INV-0002", "company_name": "AdSpawn",
     "investment_date": "2026-04-22", "date_basis": "announcement", "instrument": "investment_unspecified",
     "round_stage": "unknown", "is_follow_on": "unknown", "round_amount": "500000", "round_currency": "EUR",
     "notes": "Kolo s Czech Founders VC, částka Rockaway nezveřejněna.",
     "cites": [(f"{R}:A:A14", "deal", ""), (f"{R}:A:A13", "round_amount;investment_date", ""),
               (f"{R}:S:C29", "deal", "Zpětný profil firmy (2026-04-27).")]},
    {"deal_id": "DEAL-0009", "investor_id": "INV-0002", "company_name": "Spotawheel",
     "investment_date": "2022-04-26", "date_basis": "announcement", "instrument": "unclear",
     "round_stage": "series_b", "is_follow_on": "unknown",
     "notes": ("Kolo kombinovalo equity a asset-backed dluh (100–110 mil. EUR podle zdroje); forma účasti Rockaway "
               "neuvedena, proto unclear a jako doklad se nepočítá."),
     "cites": [(f"{R}:A:A2", "deal", "Global Venturing 2022-05-03."), (f"{R}:A:A4", "deal", "Tisková zpráva co-investora."),
               (f"{R}:A:A6", "investment_date", "Datum tiskové zprávy co-investora.")]},
])
CANDIDATES["CAN-0055"] = {"investor_id": "INV-0002", "note": "Nález ze StartupYardu („Rockaway Capital Partners“) oddělen jako CAN-0075: jiný investor téže skupiny."}

# --- StartupYard (CAN-0074) ---
Y = "CAN-0074"
TIER.update({
    "https://or.justice.cz/ias/ui/rejstrik-firma.vysledky?subjektId=1256888&typ=PLATNY": "1",
    "https://or.justice.cz/ias/ui/rejstrik-firma.vysledky?subjektId=889866&typ=PLATNY": "1",
    "https://find-and-update.company-information.service.gov.uk/company/07757587": "1",
    "https://startupyard.com/faq": "3",
    "https://startupyard.com/": "3",
    "https://startupyard.com/startupyard-team/": "3",
    "https://startupyard.com/the-next-wave-begins-startupyard-announces-batch-15/": "3",
    "https://www.lupa.cz/clanky/proc-a-jak-zakladatele-startupyardu-o-svuj-podnik-prisli-a-stali-se-jeho-konkurenty/": "2",
    "https://www.lupa.cz/aktuality/cesky-startupyard-spousti-rekordni-11-kolo-jeho-firmy-loni-ziskaly-415-milionu/": "2",
    "https://cc.cz/startupyard-v-novem-akceleracnim-kole-investoval-do-7-startupu-jeden-je-z-ceska-hned-tri-resi-kryptomeny/": "2",
    "https://cc.cz/live/petkrat-rychlejsi-vyberova-rizeni-do-cesko-slovenske-ai-platformy-ydoca-investovali-depo-ventures-a-startupyard/": "2",
    "https://tech.eu/2023/08/01/poland-fungies-io-no-code-gaming-industry": "2",
    "https://venturebeat.com/business/fungies-io-will-empower-the-rapid-commercialization-of-indie-game-studios/": "2",
})
SOURCE_OVERRIDES.update({
    "https://find-and-update.company-information.service.gov.uk/company/07757587": {
        "publisher": "Companies House", "title": "Company Overview for STARTUP YARD LIMITED (07757587)"},
    "https://venturebeat.com/business/fungies-io-will-empower-the-rapid-commercialization-of-indie-game-studios/": {
        "publisher": "Fungies.io (tisková zpráva přes Business Wire na VentureBeat)"},
})
INVESTORS.append({
    "investor_id": "INV-0003", "record_status": "candidate", "name": "StartupYard",
    "primary_type": "vc", "subtype": "accelerator", "country": "CZ", "website": "https://startupyard.com/",
    "sectors": "ai_data;cybersecurity;deeptech_hardware", "sectors_original": "AI;cybersecurity;IoT",
    "sectors_status": "reported", "stages": "pre_seed;seed", "stages_status": "reported",
    "geographies": "CEE", "geographies_status": "reported",
    "ticket_min": "25000", "ticket_max": "25000", "ticket_currency": "EUR", "ticket_status": "reported",
    "aum_status": "not_public",
    "notes": ("Kandidát: K1 a K2 nerozhodnuto. Značku od roku 2011 provozuje Startup Yard Limited (Companies House "
              "07757587, odštěpný závod IČO 03764931). Investuje přes vehikla jednotlivých kol (např. StartupYard "
              "Batch 15 s.r.o., IČO 22266852), nejnovější vehikla ale vlastní osobně ředitel, ne Ltd. Kterou osobu "
              "evidovat, rozhodne autor (overovaci-postup.md, bod 3 a F). O follow-on fondu rozhoduje DEPO Ventures. "
              "K3 splněno staršími investicemi (Fungies.io 2023, 11. kolo 2020, 10. kolo 2018). Ydoca (2025) je sporná "
              "(hotovost, nebo in-kind nóta za program; jiný zdroj investici připisuje jen DEPO), zapsána jako unclear. "
              "Stav inactive. Částky „€105m“ na webu jsou kapitál získaný absolventy, ne AUM."),
    "cites": [
        (f"{Y}:A:A1", "identity", "Provozovatel značky Startup Yard Limited (Anglie a Wales)."),
        (f"{Y}:S:T9", "identity", "Odštěpný závod Startup Yard Limited v ČR."),
        (f"{Y}:S:T2", "identity", "Vehikl 15. kola (StartupYard Batch 15 s.r.o.); vlastní ho osobně ředitel, ne Ltd."),
        (f"{Y}:S:T17", "primary_type;country;stages",
         "VC s formou akcelerátoru: vlastní hotovostní investice do pre-seed firem (DEAL-0010 až 0012), plan.md 4.2."),
        (f"{Y}:A:A7", "decision_authority", "Ředitelem Ltd je od 2012 tatáž osoba, která je jednatelem všech vehiklů kol."),
        (f"{Y}:S:T13", "decision_authority", "O follow-on investicích rozhoduje partner DEPO Ventures, ne StartupYard."),
        (f"{Y}:S:T23", "sectors", "Článek o 15. kole (2025-09) uvádí „industry-agnostic“; platí aktuální web."),
        (f"{Y}:S:T24", "geographies", ""),
        (f"{Y}:S:T20", "ticket", "Jen hotovostní část 25 000 EUR. Část 45 000 EUR je in-kind (služby programu), není to investice (plan.md 3)."),
    ],
})
DEALS.extend([
    {"deal_id": "DEAL-0010", "investor_id": "INV-0003", "company_name": "Fungies.io", "company_country": "US",
     "investment_date": "2023-07-26", "date_basis": "announcement", "instrument": "investment_unspecified",
     "round_stage": "pre_seed", "is_follow_on": "unknown", "round_amount": "850000", "round_currency": "USD",
     "notes": "Tým v Polsku, firma založená v USA. Kterým vehiklem StartupYard investoval, nedoloženo.",
     "cites": [(f"{Y}:A:A12", "deal;investment_date", "Tisková zpráva portfoliové firmy."),
               (f"{Y}:S:T28", "deal;round_amount", "Druhý vydavatel (2023-08-01).")]},
    {"deal_id": "DEAL-0011", "investor_id": "INV-0003", "company_name": "Qoobus",
     "investment_date": "2020-01-22", "date_basis": "announcement", "instrument": "investment_unspecified",
     "round_stage": "unknown", "is_follow_on": "false", "investor_amount": "40000", "investor_currency": "USD",
     "notes": "11. kolo akcelerátoru (6 firem, každá 40 000 USD); zapsána jen Qoobus, kterou citace jmenuje.",
     "cites": [(f"{Y}:A:A9", "deal", "Firma 11. kola."), (f"{Y}:A:A8", "deal;investor_amount;investment_date", "")]},
    {"deal_id": "DEAL-0012", "investor_id": "INV-0003", "company_name": "Vistag", "company_country": "CZ",
     "investment_date": "2018-10-30", "date_basis": "announcement", "instrument": "investment_unspecified",
     "round_stage": "unknown", "is_follow_on": "false",
     "notes": "10. kolo akcelerátoru (7 firem). Citace v budoucím čase („získají investici“).",
     "cites": [(f"{Y}:S:T29", "deal;investment_date", ""), (f"{Y}:S:T30", "deal", "Vistag je jediný český startup 10. kola.")]},
    {"deal_id": "DEAL-0013", "investor_id": "INV-0003", "company_name": "Ydoca",
     "investment_date": "2025-02-14", "date_basis": "announcement", "instrument": "unclear",
     "round_stage": "pre_seed", "is_follow_on": "false", "round_amount": "2300000", "round_currency": "CZK",
     "investor_amount": "500000", "investor_currency": "CZK",
     "notes": ("Sporné: částka může být in-kind konvertibilní nóta za program (služba, ne investice) a Startitup "
               "(2025-03-24) připisuje investici jen DEPO Ventures. Proto unclear, jako doklad se nepočítá."),
     "cites": [(f"{Y}:S:T26", "deal;investment_date", ""), (f"{Y}:S:T27", "round_amount;investor_amount", "")]},
])
CANDIDATES["CAN-0074"] = {"investor_id": "INV-0003"}

# --- Národní rozvojová investiční (CAN-0030) ---
N = "CAN-0030"
TIER.update({
    "https://or.justice.cz/ias/ui/rejstrik-firma.vysledky?subjektId=1061033&typ=PLATNY": "1",
    "https://or.justice.cz/ias/ui/rejstrik-firma.vysledky?subjektId=1061033&typ=UPLNY": "1",
    "https://www.nrinvesticni.cz/investicni-programy/ipo-fond-2025/": "3",
    "https://www.nrinvesticni.cz/skupina-cmzrb-nakoupila-podil-v-ceske-firme-vyrabejici-bezpilotni-letouny/": "3",
    "https://www.nrinvesticni.cz/narodni-rozvojova-investicni-nakoupila-podil-v-ceske-firme-zpracovavajici-kuze/": "3",
    "https://www.lupa.cz/aktuality/liberecke-hardwario-upsalo-akcie-na-prazske-burze-oceneno-bylo-na-240-milionu/": "2",
    "https://forbes.cz/hardwario-vstoupilo-na-burzu-a-upsalo-vsechny-nabizene-akcie-ziska-tak-48-milionu-korun/": "2",
    "https://zpravy.kurzy.cz/818066-mpo-spousti-ipo-fond-2025-na-podporu-rustu-malych-a-strednich-firem-a-rozvoje-kapitaloveho-trhu/": "2",
    "https://www.seznamzpravy.cz/clanek/ekonomika-finance-akcie-fondy-stat-chce-rozhybat-domaci-burzu-pomoci-ma-nove-spusteny-fond-292507": "2",
})
SOURCE_OVERRIDES.update({
    "https://or.justice.cz/ias/ui/rejstrik-firma.vysledky?subjektId=1061033&typ=UPLNY": {
        "title": "Úplný výpis z OR: Národní rozvojová investiční, a.s., osoba rizikového kapitálu"},
    "https://zpravy.kurzy.cz/818066-mpo-spousti-ipo-fond-2025-na-podporu-rustu-malych-a-strednich-firem-a-rozvoje-kapitaloveho-trhu/": {
        "publisher": "Ministerstvo průmyslu a obchodu (tisková zpráva na Kurzy.cz)"},
})
INVESTORS.append({
    "investor_id": "INV-0004", "record_status": "candidate",
    "name": "Národní rozvojová investiční, a.s., osoba rizikového kapitálu",
    "aliases": "NRI;ČMZRB investiční, a.s.;Národní rozvojová investiční, a.s.",
    "country": "CZ", "website": "https://www.nrinvesticni.cz/",
    "registry_type": "cz_ico", "registry_id": "08465797", "identity_level": "I1",
    "stages": "growth", "stages_status": "derived", "geographies": "CZ", "geographies_status": "reported",
    "ticket_max": "80000000", "ticket_currency": "CZK", "ticket_status": "reported",
    "aum_status": "not_public",
    "notes": ("Kandidát: K1 (I1), K2 a K3 splněno, typ investora nerozhodnut (plan.md 4.1, overovaci-postup.md bod F). "
              "Přímé investice jsou menšinové úpisy nových akcií zavedených i rostoucích MSP na trhu START "
              "(Hardwario, Primoco UAV, KARO Leather, mmcité). Neodpovídají čistě definici VC (mladé rychle rostoucí "
              "firmy) ani PE (kontrolní podíly); vlastní prezentace uvádí VC, PE i urban development. Návrh: subtype "
              "public; zda VC, rozhodne autor. Vedle toho je LP ve fondech (3SI Innovation Fund 20 mil. EUR, DEPO "
              "Ventures One SCSp 94 mil. Kč); tato část se do investic nepočítá (E7 jen pro tuto činnost). Mateřská "
              "Národní rozvojová banka investuje přes NRI, samostatný investor to není. Stav inactive: poslední "
              "nezávisle doložená přímá investice je 2022-10. AUM nezveřejněno; „až 500 mil. EUR“ je zákonný strop."),
    "cites": [
        (f"{N}:S:C1", "identity", ""), (f"{N}:S:C2", "identity", ""),
        (f"{N}:S:C4", "identity", "Dřívější název (alias)."),
        (f"{N}:S:C3", "country", ""),
        (f"{N}:S:C7", "decision_authority", "Zapsaná činnost: správa fondu fondů."),
        (f"{N}:A:A4", "decision_authority", "NRI spravuje fond a sama nakupuje akcie cílových firem."),
        (f"{N}:S:C18", "stages", "Odvozeno: úpis nových akcií při IPO/SPO zapsán jako growth."),
        (f"{N}:S:C19", "geographies", ""),
        (f"{N}:S:C17", "ticket", "Horní limit programu IPO Fond 2025+ (navíc nejvýš 30 % emise), ne typická investice."),
    ],
})
FUNDS.extend([
    {"fund_id": "FND-0004", "investor_id": "INV-0004", "name": "IPO fond (OP PIK)",
     "notes": "Program, ne samostatná právnická osoba. Z něj investice do Primoco UAV, KARO Leather, Hardwario a mmcité.",
     "cites": [(f"{N}:A:A3", "fund", ""), (f"{N}:A:A9", "fund", "Příklady podpořených firem.")]},
    {"fund_id": "FND-0005", "investor_id": "INV-0004", "name": "IPO Fond 2025+", "size_status": "conflicting",
     "notes": "Program do roku 2030. Velikost: 306 mil. Kč (web NRI, „investiční alokace“) vs. „zhruba 360 mil. Kč“ (Seznam Zprávy).",
     "cites": [(f"{N}:S:C15", "fund", ""), (f"{N}:S:C16", "size", ""), (f"{N}:A:A7", "size", "")]},
])
DEALS.extend([
    {"deal_id": "DEAL-0014", "investor_id": "INV-0004", "fund_id": "FND-0004", "company_name": "Hardwario",
     "company_country": "CZ", "investment_date": "2022-10-18", "date_basis": "announcement", "instrument": "equity",
     "round_stage": "unknown", "is_follow_on": "false",
     "notes": "Úpis nových akcií při IPO na trhu START. Obě citace mají společný původ (prohlášení firmy).",
     "cites": [(f"{N}:S:C24", "deal;investment_date", ""), (f"{N}:A:A1", "deal", "Text ČTK.")]},
    {"deal_id": "DEAL-0015", "investor_id": "INV-0004", "fund_id": "FND-0004", "company_name": "Primoco UAV",
     "company_country": "CZ", "investment_date": "2021-05-21", "date_basis": "announcement", "instrument": "equity",
     "round_stage": "unknown", "is_follow_on": "false", "investor_amount": "12000000", "investor_currency": "CZK",
     "notes": "SPO na trhu START. Jen vlastní zdroj NRI (tier 3), K3 nezakládá.",
     "cites": [(f"{N}:S:C21", "deal;investment_date", ""), (f"{N}:S:C22", "investor_amount", "")]},
    {"deal_id": "DEAL-0016", "investor_id": "INV-0004", "fund_id": "FND-0004", "company_name": "KARO Leather",
     "company_country": "CZ", "investment_date": "2022-10-21", "date_basis": "announcement", "instrument": "equity",
     "round_stage": "unknown", "is_follow_on": "false", "investor_amount": "38850000", "investor_currency": "CZK",
     "notes": "Druhé kolo úpisu na trhu START (úpis skončil 2022-09-26). Jen vlastní zdroj NRI (tier 3), K3 nezakládá.",
     "cites": [(f"{N}:S:C23", "deal;investor_amount;investment_date", "")]},
])
CANDIDATES["CAN-0030"] = {"investor_id": "INV-0004"}

# =====================================================================================
# Přehodnocení 2026-10-16 (pokyn autora): K1 připouští I2 z nezávislých zdrojů bez IČO,
# K2 musí jednoznačně doložit rozhodovací pravomoc investičního subjektu.
# Další právnické osoby téhož týmu se slučují jako E10 se svým IČO (overovaci-postup.md, bod 3).
# =====================================================================================
TIER["https://www.eif.org/press/all/central-and-eastern-europes-growth-stage-companies-get-boost-as-polish-and-czech-promotional-institutions-become-first-contributors-to-eif-led-three-seas-initiative-innovation-fund"] = "3"
by_id = {row["investor_id"]: row for row in INVESTORS}

# --- Tilia Impact Ventures: zařazen ---
by_id["INV-0001"].update({
    "record_status": "included", "identity_level": "I2",
    "notes": ("Zařazen. K1 (I2): investorem je tým a značka Tilia Impact Ventures. Název, sídlo Drtinova 557/10 "
              "a klíčové osoby se shodují v obchodním rejstříku, v seznamu EIF a na webu. IČO se neeviduje, protože "
              "investorem není jedna z právnických osob týmu. K2: investice fondu II schvaluje investiční výbor Tilie "
              "a tým kola vede (Flox). Mimo tým o investicích nikdo nerozhoduje; formálním správcem fondu II je GP Tilie "
              "(Tilia Impact Ventures II GP S.à r.l., registrační číslo neověřeno). Právnické osoby týmu jsou sloučené "
              "jako E10 (INV-0005, INV-0006). K3: 5 investic, z toho 4 nezávisle doložené za posledních 24 měsíců. "
              "Kandidát CAN-0028 („Tila Impact Partners“, překlep v seznamu EIF) je tentýž subjekt."),
    "cites": [
        (f"{T}:S:A1", "identity", "Právnická osoba týmu; název a sídlo (Drtinova 557/10) se shodují s webem (S:B4)."),
        (f"{T}:S:A3", "identity", "Jednatelka je spoluzakladatelka a partnerka týmu (S:B3)."),
        (f"{T}:S:A10", "identity", "Nezávislý zdroj (EIF): správce fondu II s týmem v ČR; „Tila“ je překlep (S:A8)."),
        (f"{T}:S:B3", "identity", "Partneři týmu na webu."),
        (f"{T}:S:A8", "identity", "Párování CAN-0028: subjekt „Tila Impact“ v rejstříku neexistuje."),
        (f"{T}:S:A11", "primary_type", "VC podle klasifikace EIF a charakteru doložených investic: minoritní účasti v kolech pre-seed až Series A (DEAL-0001 až 0005)."),
        (f"{T}:S:B1", "decision_authority", "Investice fondu II schvaluje investiční výbor Tilie."),
        (f"{T}:A:A12", "decision_authority", "Nezávislý zdroj: Tilia kolo vedla, o investici tedy rozhodla sama."),
        (f"{T}:S:A9", "decision_authority", "Formálním správcem fondu II je GP téhož týmu, ne externí subjekt."),
        (f"{T}:S:B4", "country", ""),
        (f"{T}:S:A10", "country", "Team location: Czech Republic (pilotní podmínka plan.md 11.1)."),
        (f"{T}:S:D1", "sectors;stages;geographies;ticket",
         "Fáze odvozeny: „Early stage“ převedeno na pre_seed;seed;series_a podle fází doložených investic. "
         "„CEE+“ zapsáno jako CEE. Ticket je počáteční investice."),
        (f"{T}:A:A19", "ticket", "Starší údaj (2023, tvrzení fondu převzaté médiem): do 1,5 mil. EUR. Nepoužito, platí novější údaj z webu (plan.md 9)."),
        (f"{T}:S:D3", "ticket", "Zastaralý nedatovaný profil CVCA (1–5 mil. Kč). Nepoužito."),
        (f"{T}:S:D2", "aum", "Nedatovaný údaj „ve správě“ z profilu CVCA, zřejmě z doby fondu I. Nejasné, co představuje, AUM nezapsáno."),
    ],
})
INVESTORS.extend([
    {"investor_id": "INV-0005", "record_status": "rejected", "rejection_code": "E10", "merged_into": "INV-0001",
     "name": "Tilia Impact Ventures, osoba rizikového kapitálu, s.r.o.", "registry_type": "cz_ico", "registry_id": "17848911",
     "notes": "Právnická osoba týmu Tilia (správa majetku podle § 15 ZISIF). Eviduje se kvůli párování podle IČO.",
     "cites": [(f"{T}:S:A1", "identity", ""),
               (f"{T}:S:A3", "rejection", "E10: jednatelé jsou partneři týmu Tilia, samostatná investiční pravomoc mimo tým nedoložena; sloučeno pod INV-0001.")]},
    {"investor_id": "INV-0006", "record_status": "rejected", "rejection_code": "E10", "merged_into": "INV-0001",
     "name": "Tilia Impact Partners s.r.o.", "registry_type": "cz_ico", "registry_id": "17621615",
     "notes": "Poradenská společnost týmu Tilia; v seznamu EIF jako správce „Tila Impact Partners“. Eviduje se kvůli párování podle IČO.",
     "cites": [(f"{T}:S:A5", "identity", ""),
               (f"{T}:S:A7", "rejection", "E10: jednatel je partner týmu Tilia (S:B3), stejné sídlo; samostatná investiční pravomoc nedoložena; sloučeno pod INV-0001.")]},
])

# --- StartupYard: zařazen ---
by_id["INV-0003"].update({
    "record_status": "included", "identity_level": "I2",
    "notes": ("Zařazen. K1 (I2): investorem je značka a tým StartupYard. Provozovatelem je Startup Yard Limited "
              "(Anglie a Wales 07757587, Companies House a Lupa), sídlo týmu a vehiklů je Perlová 371/5, Praha, "
              "ředitelem N. Rafaj. K2: investice jdou přes vehikla jednotlivých kol, jejichž jediným jednatelem je "
              "ředitel StartupYardu (Lupa 2020, obchodní rejstřík). O follow-on investicích rozhoduje DEPO Ventures; "
              "ty se StartupYardu nepřipisují. Vehikl Batch 15 (INV-0007, ze 80 % ho osobně vlastní ředitel) a "
              "odštěpný závod (INV-0008) jsou sloučené jako E10. K3: Fungies.io 2023, 11. kolo 2020, 10. kolo 2018. "
              "Ydoca 2025 je unclear (možná in-kind nóta za program). Stav inactive."),
    "cites": [
        (f"{Y}:A:A1", "identity", "Provozovatel značky Startup Yard Limited (Anglie a Wales)."),
        (f"{Y}:A:A6", "identity", "Nezávislý zdroj: značku provozuje Startup Yard Limited."),
        (f"{Y}:S:T3", "identity", "Sídlo týmu a vehiklů kol (všech 17 subjektů značky)."),
        (f"{Y}:S:T17", "primary_type;country;stages",
         "VC s formou akcelerátoru: pre-seed a seed (plan.md 4.2)."),
        (f"{Y}:A:A8", "primary_type", "Akcelerátor investuje vlastní kapitál v hotovosti (40 000 USD do každé firmy 11. kola), nejen program."),
        (f"{Y}:A:A10", "decision_authority", "Investice kola jdou přes vehikl, jehož jednatelem je ředitel StartupYardu."),
        (f"{Y}:S:T5", "decision_authority", "Vehikl 15. kola má jediného jednatele, ředitele StartupYardu (S:T16)."),
        (f"{Y}:A:A7", "decision_authority", "Ředitelem provozovatele Startup Yard Limited je od 2012 tatáž osoba."),
        (f"{Y}:S:T13", "decision_authority", "Omezení: o follow-on investicích rozhoduje partner DEPO Ventures, ne StartupYard."),
        (f"{Y}:S:T23", "sectors", "Článek o 15. kole (2025-09) uvádí „industry-agnostic“; platí aktuální web."),
        (f"{Y}:S:T24", "geographies", ""),
        (f"{Y}:S:T20", "ticket", "Jen hotovostní část 25 000 EUR. Část 45 000 EUR je in-kind (služby programu), není to investice (plan.md 3)."),
    ],
})
INVESTORS.extend([
    {"investor_id": "INV-0007", "record_status": "rejected", "rejection_code": "E10", "merged_into": "INV-0003",
     "name": "StartupYard Batch 15 s.r.o.", "registry_type": "cz_ico", "registry_id": "22266852",
     "notes": "Vehikl 15. kola akcelerátoru. Eviduje se kvůli párování podle IČO.",
     "cites": [(f"{Y}:S:T2", "identity", ""),
               (f"{Y}:S:T5", "rejection", "E10: investiční vehikl kola, jediným jednatelem je ředitel StartupYardu; sloučeno pod INV-0003.")]},
    {"investor_id": "INV-0008", "record_status": "rejected", "rejection_code": "E10", "merged_into": "INV-0003",
     "name": "Startup Yard Limited, odštěpný závod", "registry_type": "cz_ico", "registry_id": "03764931",
     "notes": "Odštěpný závod provozovatele značky v ČR. Eviduje se kvůli párování podle IČO.",
     "cites": [(f"{Y}:S:T9", "identity", ""),
               (f"{Y}:S:T10", "rejection", "E10: odštěpný závod společnosti Startup Yard Limited (07757587), není samostatný investor; sloučeno pod INV-0003.")]},
])

# --- NRI: zařazen jako VC (subtype public) ---
by_id["INV-0004"].update({
    "record_status": "included", "primary_type": "vc", "subtype": "public", "sectors_status": "not_public",
    "notes": ("Zařazen. K1 (I1): IČO 08465797. K2: zapsaná správa fondu fondů; NRI spravuje IPO fond a sama "
              "vybírá a kupuje akcie (MPO, Seznam Zprávy). K3: Hardwario 2022 (Lupa, ČTK; obě citace mají původ "
              "v prohlášení firmy). Typ VC (subtype public): úřední název „osoba rizikového kapitálu“ a doložené "
              "investice jsou menšinové podíly v rostoucích firmách při úpisu nových akcií na trhu START (plan.md 4.1, "
              "krok 3). Hraniční: část firem je zavedená a kotovaná na trhu START. Vedle toho je NRI LP ve fondech "
              "(3SI Innovation Fund, DEPO Ventures One SCSp), tato činnost se do investic nepočítá. Odvětvové "
              "zaměření zdroje neuvádějí. Mateřská Národní rozvojová banka investuje přes NRI. Stav inactive: "
              "poslední nezávisle doložená přímá investice je z 2022-10."),
})
by_id["INV-0004"]["cites"].extend([
    (f"{N}:S:C1", "primary_type", "Úřední název „osoba rizikového kapitálu“. Doložené investice: menšinové podíly v rostoucích firmách při úpisu nových akcií (DEAL-0014 až 0016), tedy VC (plan.md 4.1, krok 3), subtype public (4.2)."),
    (f"{N}:S:C20", "primary_type", "Vlastní prezentace (text NRI v tiskové zprávě EIF): venture capital, private equity a urban development."),
])

# --- Rockaway Ventures: zařazen po doplňujícím ověření K2 (CAN-0055-K2) ---
K = "CAN-0055-K2"
TIER.update({
    "https://www.amista.cz/files/investovani/cz0008048311-factsheet-cze-cs.pdf": "3",
    "https://www.amista.cz/files/rocway/2022-05-10-sdeleni-klicovych-informaci-rockaway-ventures-fund-sicav-podfond-i-iaa.pdf": "3",
    "https://rockawayventures.com/rockaway-ventures-completes-first-investment-round-with-almost-a-quarter-of-the-target-amount-of-eur-100-million-and-completes-another-investment/": "3",
    "https://www.unquote.com/cee/news/3028705/rockaway-plans-third-closing-for-rockaway-ventures-fund-this-autumn": "2",
    "https://api.gleif.org/api/v1/lei-records?filter[fulltext]=Rockaway%20Ventures&page[size]=50": "1",
    "https://cc.cz/jakub-havrlant-prichazi-s-novym-investicnim-fondem-rockaway-s-nim-chce-do-startupu-poslat-25-miliardy-korun/": "2",
    "https://www.lupa.cz/aktuality/cesti-investori-z-rockaway-investovali-do-americkych-humanoidu-a-to-po-boku-googlu-nebo-mercedes-benz/": "2",
})
SOURCE_OVERRIDES.update({
    "https://api.gleif.org/api/v1/lei-records?filter[fulltext]=Rockaway%20Ventures&page[size]=50": {
        "publisher": "GLEIF", "title": "LEI záznamy, hledání „Rockaway Ventures“"},
})
by_id["INV-0002"].update({
    "record_status": "included", "identity_level": "I2",
    "notes": ("Zařazen. K1 (I2): investorem je tým a značka Rockaway Ventures (skupina Rockaway Capital, Praha, "
              "General Partners podle tech.eu a Lupy). K2: o investicích fondu rozhoduje tým. Fond Rockaway Ventures "
              "Fund SCSp (Lucembursko) vedou General Partners z Rockaway a jeho investiční výbor tvoří lidé z Rockaway "
              "(Unquote 2023, CzechCrunch 2021). Externí AMISTA IS obhospodařuje jen český feeder Rockaway Ventures Fund "
              "SICAV a.s., který investuje výhradně do lucemburského fondu (KID AMISTA), o portfoliových firmách tedy "
              "nerozhoduje. Auditor K2 označil za sporné: chybí výpis z lucemburského registru (GP Rockaway Venture "
              "Partners (GP) S.à r.l., fond B263215) a nevyloučil externího AIFM; žádný zdroj ho ale neuvádí. Feeder a "
              "Rockaway Ventures Advisors a.s. jsou sloučené jako E10 (INV-0009, INV-0010). Rockaway Ventures a.s. "
              "(IČO 06387136, akcionář Rockaway Capital SE, předmět pronájem nemovitostí) se nesloučila, protože její "
              "role nedoložena. Rockaway Capital SE investuje i sama a je LP fondu: samostatný investor, neslučovat. "
              "K3: Filuta AI, Remix, AdSpawn (2025–2026). Apptronik a CulturePulse nezapsány (jen oznámení investora "
              "nebo bez výslovné investice). AUM nezveřejněno; hodnota portfolia 139 mil. EUR (2022) není AUM."),
    "cites": [
        (f"{R}:S:C17", "identity", "Nezávislý zdroj: značka Rockaway Ventures ve skupině Rockaway Capital."),
        (f"{K}:A:A4", "identity", "Klíčová osoba: General Partner Rockaway Ventures."),
        (f"{R}:S:C14", "identity", "Klíčová osoba (Lupa 2026)."),
        (f"{R}:S:C9", "identity", "Rockaway Ventures a.s. (IČO 06387136) sídlí v Praze; její role vůči fondu nedoložena, nesloučena."),
        (f"{R}:S:C21", "primary_type;stages;geographies",
         "VC: minoritní účasti v kolech seed až Series A (DEAL-0006 až 0008). „late seed“ zapsáno jako seed, "
         "„Western European countries“ jako EUROPE."),
        (f"{K}:S:T6", "decision_authority", "Fond má dva General Partners z Rockaway a investiční výbor z lidí Rockaway (stav 2023)."),
        (f"{K}:A:A1", "decision_authority", "V čele fondu stojí investiční partneři Rockaway (2021)."),
        (f"{K}:S:T3", "decision_authority", "Český feeder spravovaný AMISTA investuje jen do lucemburského fondu; o portfoliových firmách AMISTA nerozhoduje."),
        (f"{R}:A:A7", "decision_authority", "Charakter investic: fond Rockaway Ventures kolo vedl (nezávislý zdroj)."),
        (f"{R}:S:C15", "country", "Text vychází z oznámení investora (tier 3 obsah). Všechny české osoby značky sídlí v Praze."),
        (f"{R}:S:C20", "sectors", "„defence“ zařazeno pod deeptech_hardware, „travel & hospitality“ pod consumer. Tech.eu (2025) uvádí nové zaměření na energetiku, obranu a dual-use."),
    ],
})
INVESTORS.extend([
    {"investor_id": "INV-0009", "record_status": "rejected", "rejection_code": "E10", "merged_into": "INV-0002",
     "name": "Rockaway Ventures Fund SICAV a.s.", "registry_type": "cz_ico", "registry_id": "14235781",
     "notes": "Český feeder fondu Rockaway Ventures Fund SCSp; obhospodařovatel AMISTA investiční společnost, a.s.; LEI 315700BOU2P8YSSK8F03.",
     "cites": [(f"{K}:S:T7", "identity", "Záznam GLEIF uvádí registeredAs 14235781."),
               (f"{K}:S:T5", "rejection", "E10: feeder vytvořený jen pro investici do fondu Rockaway Ventures Fund; sloučeno pod INV-0002.")]},
    {"investor_id": "INV-0010", "record_status": "rejected", "rejection_code": "E10", "merged_into": "INV-0002",
     "name": "Rockaway Ventures Advisors a.s.", "registry_type": "cz_ico", "registry_id": "14125129",
     "notes": "Právnická osoba týmu (představenstvo z lidí Rockaway). Zda je poradcem fondu, nedoloženo.",
     "cites": [(f"{K}:A:A11", "identity", ""),
               (f"{R}:S:C10", "rejection", "E10: společnost téhož týmu, samostatná investiční pravomoc nedoložena; sloučeno pod INV-0002.")]},
])
fund_rv = next(f for f in FUNDS if f["fund_id"] == "FND-0003")
fund_rv.update({
    "domicile_country": "LU",
    "notes": ("Lucemburský fond Rockaway Ventures Fund SCSp (tech.eu: „Rockaway Ventures II“). Český feeder Rockaway "
              "Ventures Fund SICAV a.s. (INV-0009) do něj investuje. Zdroje uvádějí „necelých“ / „nearly“ 55 mil. EUR, "
              "cíl byl 100 mil. EUR. Asi čtvrtina kapitálu od Rockaway Capital (LP)."),
    "cites": [(f"{K}:A:A2", "fund", "Oficiální sídlo fondu je v Lucembursku."),
              (f"{K}:S:T3", "fund", "Feeder investuje do lucemburského fondu."),
              (f"{R}:A:A9", "fund;size", ""),
              (f"{R}:S:C17", "fund;size", "")],
})

# --- Doplnění vyplněnosti z už získaných citací ---
deal_by_id = {d["deal_id"]: d for d in DEALS}
deal_by_id["DEAL-0006"]["company_country"] = "CZ"          # „Prague-based Filuta AI“ (C27)
deal_by_id["DEAL-0011"]["company_country"] = "RO"          # „Qoobus (Rumunsko)“ (A9)
deal_by_id["DEAL-0007"]["company_country"] = "BG"
deal_by_id["DEAL-0007"]["cites"].append((f"{R}:S:C25", "deal", "Zpětný přehled CzechCrunch za rok 2025; země Bulharsko."))
deal_by_id["DEAL-0004"]["company_country"] = "EE"
deal_by_id["DEAL-0004"]["cites"].append((f"{T}:S:C7", "deal", "Přehled CzechCrunch (zahraniční dealy českých VC); země Estonsko, částka včetně grantu."))
fund_ipo = next(f for f in FUNDS if f["fund_id"] == "FND-0004")
fund_ipo["size_status"] = "not_public"
by_id["INV-0003"]["notes"] += " Fondy se nezapisují: velikost vehiklů kol ani follow-on fondu (o něm rozhoduje DEPO) zveřejněná není."
TIER.update({
    "https://cc.cz/startupy-letos-nabiraji-mene-penez-bez-umele-inteligence-by-bylo-jen-malo-prilezitosti-pro-investice/": "2",
    "https://cc.cz/zmapovali-jsme-vsechny-investice-ktere-loni-oznamily-ceske-startupy-neseme-tri-dobre-a-tri-spatne-zpravy/": "2",
})

# --- Město sídla investičního týmu (nové pole city, doložené citací) a oprava ticketu NRI ---
def add_field(investor_id, ref, field):
    cites = by_id[investor_id]["cites"]
    for i, (r, fields, note) in enumerate(cites):
        if r == ref:
            cites[i] = (r, fields + ";" + field, note)
            return
    raise KeyError(f"{investor_id}: citace {ref} není")

by_id["INV-0001"]["city"] = "Praha"
add_field("INV-0001", f"{T}:S:B4", "city")          # Contact us Drtinova 557/10, 150 00 Prague
add_field("INV-0001", f"{T}:S:A1", "city")          # Sídlo: Drtinova 557/10, ... Praha 5
by_id["INV-0002"]["city"] = "Praha"
add_field("INV-0002", f"{R}:S:C15", "city")         # key locations in Prague and San Francisco
by_id["INV-0003"]["city"] = "Praha"
add_field("INV-0003", f"{Y}:S:T17", "city")         # based in beautiful Prague
add_field("INV-0003", f"{Y}:S:T3", "city")          # Sídlo: Perlová 371/5, ... Praha 1
by_id["INV-0004"]["city"] = "Praha"
add_field("INV-0004", f"{N}:S:C3", "city")          # Přemyslovská 2845/43, Žižkov, 130 00 Praha 3

by_id["INV-0004"].update({"ticket_min": "", "ticket_max": "", "ticket_currency": "", "ticket_status": "not_public"})
by_id["INV-0004"]["cites"] = [
    (r, f, "Jen horní limit programu IPO Fond 2025+ (navíc nejvýš 30 % emise), ne typická investice. Typická investice nezveřejněna.")
    if r == f"{N}:S:C17" else (r, f, n) for r, f, n in by_id["INV-0004"]["cites"]]
by_id["INV-0004"]["notes"] += " Typická investice nezveřejněna; 80 mil. Kč je jen limit programu IPO Fond 2025+."
by_id["INV-0002"]["notes"] += " Tým působí v Praze a San Francisku, město sídla je Praha."

# --- Oprava duplicity ve výběru (2026-10-16): CAN-0028 je tentýž kandidát jako CAN-0025 ---
CANDIDATES["CAN-0028"] = {"investor_id": "INV-0001", "note": (
    "Oprava duplicity: tentýž subjekt jako CAN-0025 („Tila“ je překlep v seznamu EIF; v rejstříku žádná „Tila "
    "Impact“ není, Tilia Impact Partners s.r.o. má stejné sídlo, fond II i LP EIF se shodují). Ve výběru proto "
    "doplněn další unikátní kandidát ze stejného zdroje (CAN-0019, candidates_vyber_oprava.csv).")}

# --- Orbit Capital (CAN-0019): pátý unikátní kandidát po opravě duplicity ---
O = "CAN-0019"
TIER.update({
    "https://or.justice.cz/ias/ui/rejstrik-$firma?ico=22269720": "1",
    "https://or.justice.cz/ias/ui/rejstrik-firma.vysledky?subjektId=1257014&typ=PLATNY": "1",
    "https://or.justice.cz/ias/ui/rejstrik-$firma?nazev=Orbit+Capital&jenPlatne=VSECHNY&polozek=50": "1",
    "https://or.justice.cz/ias/ui/rejstrik-firma.vysledky?subjektId=1056199&typ=PLATNY": "1",
    "https://www.eif.org/press/all/eif-pledges-eur20-million-to-fuel-expansion-of-cee-based-innovative-smes-via-orbit-growth-debt-ii-fund": "2",
    "https://orbitcapital.com/equity/": "3",
    "https://cvca.cz/orbit-capital/": "3",
    "https://www.mews.com/en/press/series-c": "2",
    "https://forbes.cz/vesele-vanoce-v-mews-technologicka-firma-ziskava-od-investoru-43-miliardy-korun/": "2",
    "https://www.prnewswire.co.uk/news-releases/ukrainian-founded-preply-raises-50-million-usd-series-c-830797049.html": "2",
    "https://cc.cz/jazyky-jako-zajimavy-byznys-startup-na-online-vyuku-ziskal-i-diky-ceskym-investorum-pres-miliardu/": "2",
    "https://www.unquote.com/cee/news/3027699/orbit-capital-aims-for-eur-200m-with-new-scaleup-fund": "2",
    "https://cc.cz/byvaly-sef-polskeho-mckinsey-jde-pomahat-ridit-obri-cesky-fond-bude-hledat-prijemce-miliard/": "2",
    "https://alternativecreditinvestor.com/2026/07/02/orbit-inks-more-than-e100m-for-venture-debt-fund/": "2",
})
SOURCE_OVERRIDES.update({
    "https://www.mews.com/en/press/series-c": {"publisher": "Mews (portfoliová firma)"},
    "https://www.prnewswire.co.uk/news-releases/ukrainian-founded-preply-raises-50-million-usd-series-c-830797049.html": {
        "publisher": "Preply (tisková zpráva přes PR Newswire)"},
})
INVESTORS.append({
    "investor_id": "INV-0011", "record_status": "included", "name": "Orbit Capital",
    "primary_type": "vc", "country": "CZ", "city": "Praha", "website": "https://orbitcapital.com/",
    "identity_level": "I2",
    "sectors": "software_saas", "sectors_original": "Technology and technology-enabled scale-ups",
    "sectors_status": "reported", "stages": "growth", "stages_status": "reported",
    "geographies": "CEE", "geographies_status": "reported",
    "ticket_min": "6000000", "ticket_max": "15000000", "ticket_currency": "EUR", "ticket_status": "reported",
    "aum_status": "ambiguous",
    "notes": ("Zařazen. K1 (I2): tým a značka Orbit Capital (Praha a Varšava; partneři R. Nesrsta a W. Namysł) podle "
              "EIF, Mews, CzechCrunch a Unquote. K2: tým má investiční výbor a partneři fond vedou (CzechCrunch 2022 "
              "a 2023). Kapitálové investice jdou přes vlastní lucemburský fond Orbit Growth SCSp; jeho GP ani AIFM "
              "nejsou ověřené v registru (stejná výhrada jako u Rockaway). Orbit kombinuje growth equity a venture "
              "debt: typ a K3 se určují jen podle doložených kapitálových investic (plan.md 9). Ty jsou dvě (Mews a "
              "Preply, 2022), proto se nevyřazuje jako věřitel (E3). Novější financování (Jutro Medical 2025, Talkin' "
              "Things a Sloneek 2026) je dluh a do investic se nezapisuje. Stav inactive. Právnické osoby týmu OGD "
              "Advisory s.r.o. a ORBIT Capital GP s.r.o. jsou sloučené jako E10 (INV-0012, INV-0013). Conseq-Orbit "
              "SICAV, a.s. (IČO 08223467, dluhový fond I) obhospodařuje Conseq Funds IS jiné skupiny, proto se "
              "neslučuje. AUM: zdroj uvádí jen dolní mez „more than €200m“ za dluhovou i kapitálovou strategii. "
              "Pátý kandidát pilotu doplněný po opravě duplicity CAN-0028."),
    "cites": [
        (f"{O}:S:C11", "identity;city", "Nezávislý zdroj (EIF): Orbit Capital se sídlem v Praze a Varšavě."),
        (f"{O}:A:A15", "identity", "Zakladatel a partneři týmu (CzechCrunch)."),
        (f"{O}:S:C10", "country", "Team location: Czech Republic (pilotní podmínka plan.md 11.1)."),
        (f"{O}:A:A1", "primary_type",
         "VC: doložené kapitálové investice jsou menšinové účasti v kolech Series C rostoucích technologických "
         "firem (DEAL-0017, DEAL-0018). Dluhové financování se pro typ nepočítá (plan.md 9)."),
        (f"{O}:A:A8", "decision_authority", "Tým má investiční výbor; hlavní partner je jeho členem."),
        (f"{O}:A:A15", "decision_authority", "Partneři týmu fond vedou."),
        (f"{O}:A:A10", "decision_authority", "Kapitálový fond je vlastní fond týmu (Orbit Growth SCSp, Lucembursko); GP neověřen v registru."),
        (f"{O}:S:C23", "sectors;geographies",
         "„Technology and technology-enabled scale-ups“ zařazeno jako software_saas; „CEE“ jako CEE."),
        (f"{O}:S:C21", "stages", "„Scaling / expansion“ zapsáno jako growth (kapitálová strategie)."),
        (f"{O}:S:C22", "ticket", "Profil CVCA (upraven 2023): Growth Equity 6–15 mil. EUR; částky venture debt se netýkají kapitálových investic."),
        (f"{O}:A:A13", "ticket", "Starší údaj (2022, výrok partnera): počáteční ticket 5–10 mil. EUR. Nepoužito, platí novější profil."),
        (f"{O}:A:A20", "aum", "Jen dolní mez („more than €200m“) za dluhovou i kapitálovou strategii; přesná hodnota nezveřejněna, AUM nezapsáno."),
    ],
})
INVESTORS.extend([
    {"investor_id": "INV-0012", "record_status": "rejected", "rejection_code": "E10", "merged_into": "INV-0011",
     "name": "OGD Advisory s.r.o.", "registry_type": "cz_ico", "registry_id": "22269720",
     "notes": "Společnost týmu Orbit; v seznamu EIF správce dluhového fondu Orbit Growth Debt II. Eviduje se kvůli párování podle IČO.",
     "cites": [(f"{O}:S:C1", "identity", ""),
               (f"{O}:S:C4", "rejection", "E10: společníky jsou partneři týmu Orbit; samostatná investiční pravomoc mimo tým nedoložena; sloučeno pod INV-0011.")]},
    {"investor_id": "INV-0013", "record_status": "rejected", "rejection_code": "E10", "merged_into": "INV-0011",
     "name": "ORBIT Capital GP s.r.o.", "registry_type": "cz_ico", "registry_id": "08319961",
     "notes": "Společnost zakladatele týmu Orbit; ke kterému fondu je GP, nedoloženo. Eviduje se kvůli párování podle IČO.",
     "cites": [(f"{O}:S:C5", "identity", ""),
               (f"{O}:S:C6", "rejection", "E10: jednatelem je zakladatel a partner týmu Orbit; samostatná investiční pravomoc nedoložena; sloučeno pod INV-0011.")]},
])
FUNDS.extend([
    {"fund_id": "FND-0006", "investor_id": "INV-0011", "name": "Orbit Growth SCSp (kapitálový fond)",
     "domicile_country": "LU", "size_amount": "42000000", "size_currency": "EUR", "size_type": "first_close",
     "size_as_of": "2021-12", "size_status": "reported",
     "notes": "Datum podle „last December“ v článku z 2022-08-31. Cíl 200 mil. EUR; k 2023-03 upsána zhruba čtvrtina. Konečná velikost nedoložena.",
     "cites": [(f"{O}:A:A10", "fund;size", ""), (f"{O}:A:A11", "size", "Cíl 200 mil. EUR."),
               (f"{O}:A:A14", "size", "K 2023-03 upsána zhruba čtvrtina cíle.")]},
    {"fund_id": "FND-0007", "investor_id": "INV-0011", "name": "Orbit Growth Debt II (dluhový fond)",
     "size_amount": "100000000", "size_currency": "EUR", "size_type": "target", "size_as_of": "2025-06-17",
     "size_status": "reported",
     "notes": "Dluhový fond (venture debt); jeho financování se do investic nepočítá. Druhé uzavření 107 mil. EUR (2026-07), konečná velikost nedoložena. LP mj. EIF.",
     "cites": [(f"{O}:S:C11", "fund", ""), (f"{O}:S:C12", "size", "Cíl 100 mil. EUR."),
               (f"{O}:A:A21", "size", "Druhé uzavření 107 mil. EUR.")]},
    {"fund_id": "FND-0008", "investor_id": "INV-0011", "name": "Orbit Growth Debt I (dluhový fond)",
     "vintage_year": "2019", "size_status": "conflicting",
     "notes": "Dluhový fond (venture debt), od 2019; vehikl Orbit Capital Venture Debt Fund SICAV (dnes Conseq-Orbit SICAV). Velikost 40 mil. EUR (EIF 2025) vs. 35 mil. EUR (Unquote 2022).",
     "cites": [(f"{O}:S:C13", "fund;size", ""), (f"{O}:A:A12", "size", "")]},
])
DEALS.extend([
    {"deal_id": "DEAL-0017", "investor_id": "INV-0011", "fund_id": "FND-0006", "company_name": "Mews",
     "investment_date": "2022-12-15", "date_basis": "announcement", "instrument": "equity",
     "round_stage": "series_c_plus", "is_follow_on": "false", "round_amount": "185000000", "round_currency": "USD",
     "notes": "Series C; dluhovou část kola poskytl jiný věřitel. Fond podle doby a strategie (kapitálový fond).",
     "cites": [(f"{O}:A:A1", "deal", "Tisková zpráva portfoliové firmy: kapitálová investice."),
               (f"{O}:A:A2", "investment_date;round_amount", ""),
               (f"{O}:A:A3", "deal", "Druhý vydavatel: Orbit jako první český investor v Mews.")]},
    {"deal_id": "DEAL-0018", "investor_id": "INV-0011", "fund_id": "FND-0006", "company_name": "Preply",
     "investment_date": "2022-07-13", "date_basis": "announcement", "instrument": "equity",
     "round_stage": "series_c_plus", "is_follow_on": "false", "round_amount": "50000000", "round_currency": "USD",
     "investor_amount": "8000000", "investor_currency": "USD",
     "notes": "Series C, Orbit jako nový investor; pořídil podíl.",
     "cites": [(f"{O}:A:A4", "deal", "Tisková zpráva portfoliové firmy."),
               (f"{O}:A:A5", "investment_date", ""),
               (f"{O}:A:A7", "deal", "Fond si pořídil podíl (equity)."),
               (f"{O}:A:A6", "investor_amount", ""),
               (f"{O}:A:A9", "round_amount;investor_amount", "")]},
])
CANDIDATES["CAN-0019"] = {"investor_id": "INV-0011"}

# --- Rozsah deklarovaného ticketu (ticket_scope): ke které strategii nebo programu se vztahuje ---
by_id["INV-0001"]["ticket_scope"] = "počáteční investici"                          # „initial ticket“ (tilia.vc)
by_id["INV-0003"]["ticket_scope"] = "hotovostní investici v programu akcelerátoru"  # €25,000 in cash (FAQ)
next(r for r in INVESTORS if r["investor_id"] == "INV-0011")["ticket_scope"] = "growth equity"  # CVCA: Growth Equity

# =====================================================================================
# Opravy podle auditu kroku 6 (results/README.md, kap. Souhrn), zapracované v kroku 8, 2026-10-16.
# Audit a měření přesnosti se vztahují k datům před opravami (commit c96c21e).
# Citace „KOORD“ převzal koordinátor při auditu přímo ze stránky; doslovnost ověřuje verify_quotes.py.
# =====================================================================================
ACI = "https://alternativecreditinvestor.com/2026/07/02/orbit-inks-more-than-e100m-for-venture-debt-fund/"
SY15 = "https://startupyard.com/the-next-wave-begins-startupyard-announces-batch-15/"
KOORD_CLAIMS = {
    "G1": {"_url": ACI, "_quote": "Founded in 2019, Orbit Capital is a growth-stage investor focused on supporting "
                                  "technology scale-ups across the CEE region as well as Germany, Austria and Switzerland."},
    "S1": {"_url": SY15, "_quote": "We're industry-agnostic, but we look for solutions that are hard to replicate."},
}
TIER[SY15] = "3"
SOURCE_OVERRIDES[SY15] = {"publisher": "StartupYard", "title": "The Next Wave Begins: StartupYard Announces Batch 15",
                          "accessed_date": "2026-10-16"}
inv = {row["investor_id"]: row for row in INVESTORS}
deal_by_id = {d["deal_id"]: d for d in DEALS}

# INV-0011/geografie: novější zdroj tier 2 (2026) uvádí vedle CEE i DACH, má přednost před CVCA (plan.md 9).
inv["INV-0011"]["geographies"] = "CEE;DACH"
inv["INV-0011"]["cites"].append(("KOORD:G1", "geographies",
    "Novější zdroj tier 2 (2026) uvádí vedle CEE i Německo, Rakousko a Švýcarsko; má přednost před profilem CVCA "
    "(plan.md 9). Oprava podle auditu kroku 6."))

# DEAL-0017, DEAL-0018: přiřazení k fondu Orbit Growth SCSp žádný zdroj neuvádí.
for deal_id in ("DEAL-0017", "DEAL-0018"):
    deal_by_id[deal_id]["fund_id"] = ""
deal_by_id["DEAL-0017"]["notes"] = ("Series C; dluhovou část kola poskytl jiný věřitel. Fond zdroj neuvádí, proto není "
                                    "přiřazen (oprava podle auditu kroku 6).")
deal_by_id["DEAL-0018"]["notes"] = ("Series C, Orbit jako nový investor; pořídil podíl. Fond zdroj neuvádí, proto není "
                                    "přiřazen (oprava podle auditu kroku 6).")

# INV-0003/sektory: dva vlastní zdroje si odporují a novější nejde určit (úvodní stránka bez data) → conflicting.
inv["INV-0003"].update({"sectors": "", "sectors_original": "", "sectors_status": "conflicting"})
inv["INV-0003"]["cites"].append(("KOORD:S1", "sectors",
    "Stránka o 15. kole (2025) uvádí „industry-agnostic“, úvodní stránka (bez data) deep tech: AI, kyberbezpečnost, IoT. "
    "Novější zdroj nejde určit (plan.md 9). Oprava podle auditu kroku 6."))

# DEAL-0009 Spotawheel: dluh dodaly banky a úvěrové instituce, Rockaway je jmenován mezi investory kola.
deal_by_id["DEAL-0009"]["instrument"] = "investment_unspecified"
deal_by_id["DEAL-0009"]["notes"] = ("Kolo kombinovalo equity a asset-backed dluh (100–110 mil. EUR podle zdroje). Zdroje "
                                    "jmenují Rockaway mezi investory kola a formu neuvádějí; dluh podle tiskové zprávy dodaly "
                                    "banky a úvěrové instituce. Proto investment_unspecified (oprava podle auditu kroku 6, "
                                    "dříve unclear).")

# DEAL-0014 Hardwario: Forbes (ČTK) přebírá totéž prohlášení jako Lupa, jako samostatný důkaz se nepočítá (plan.md 6.3).
deal_by_id["DEAL-0014"]["cites"] = [c for c in deal_by_id["DEAL-0014"]["cites"] if c[0] != f"{N}:A:A1"]
deal_by_id["DEAL-0014"]["notes"] = ("Úpis nových akcií při IPO na trhu START. Totéž prohlášení Hardwaria přebírá i ČTK "
                                    "(https://forbes.cz/hardwario-vstoupilo-na-burzu-a-upsalo-vsechny-nabizene-akcie-ziska-tak-48-milionu-korun/); "
                                    "jako samostatný důkaz se nepočítá (plan.md 6.3, oprava podle auditu kroku 6).")

# DEAL-0012 Vistag: nejisté, ponecháno jako záznam, ale ne jako doložená investice (plan.md 5, K3, bod 2:
# zdroj musí popisovat vložení kapitálu). Citace v budoucím čase („získají investici“) proto dokládá jen datum
# oznámení, ne transakci; jako „deal“ zůstává jen citace o účasti v 10. kole, která investici nezmiňuje.
deal_by_id["DEAL-0012"]["cites"] = [
    (f"{Y}:S:T29", "investment_date", "Oznámení výběru do 10. kola; investice je v budoucím čase, vložení kapitálu "
                                      "nedokládá (K3, bod 2)."),
    (f"{Y}:S:T30", "deal", "Účast v 10. kole akcelerátoru; investici nezmiňuje, jako doklad K3 se nepočítá."),
]
deal_by_id["DEAL-0012"]["notes"] = ("10. kolo akcelerátoru (7 firem). NEJISTÉ: nelze spolehlivě určit, zda investice "
                                    "proběhla (citace v budoucím čase, titulek v minulém), proto se nepočítá mezi doložené "
                                    "investice (audit kroku 6, oprava v kroku 8).")
