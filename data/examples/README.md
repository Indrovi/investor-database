# Fiktivní ukázková data

**Všechna data v tomto adresáři jsou vymyšlená.** Slouží jen k ukázce datového modelu a k testům validátoru. Nejde o skutečné investory.

- `valid/`: správně zapsaná data včetně okrajových případů (neznámé datum, jen rok, nejasný kapitál, nejasný nástroj, zápis v rejstříku bez dalšího dokladu, cílová vs. konečná velikost fondu, kandidát, vyřazené subjekty).
- `invalid/`: stejná data se záměrně vloženými chybami. Každá je popsaná ve sloupci `notes` (začíná „CHYBA:“).

Názvy jsou smyšlené, URL vedou na rezervovanou doménu `.example`. Použitá IČO mají platný kontrolní součet, ale v ARES neexistují (ověřeno 2026-10-14).

```bash
python3 scripts/validate.py data/examples/valid --today 2026-10-14
python3 scripts/validate.py data/examples/invalid --today 2026-10-14
```

Popis modelu je v [docs/datovy-model.md](../../docs/datovy-model.md).
