#!/bin/bash
# Celý řetězec agentů pro jednoho kandidáta pilotu, vždy za sebou (docs/overovaci-postup.md, body 4–7):
# průzkumník → uložené kopie stránek → kontrola citací → předání souborem → auditor → kontrola citací.
#
# Použití: scripts/pilot/run_one.sh CAN-ID "NÁZEV" [auditor-only]
# Zadání musí být připravené v .cache/agents/pilot/CAN-ID/ (scripts/pilot/prompt.py).
set -u
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
B=.cache/agents/pilot/$1
if [ "${3:-}" != "auditor-only" ]; then
  python3 scripts/agents.py run investor-source-scout --prompt-file $B/scout.txt --out $B --max-budget-usd 4 > $B/scout.log 2>&1
  echo "scout exit $?" >> $B/scout.log
fi
python3 scripts/pilot/pages.py > /dev/null
python3 scripts/pilot/verify_quotes.py --markdown $B/investor-source-scout.md > $B/quotes_scout.txt 2>&1
python3 scripts/agents.py handoff $B/investor-source-scout.md --investor "$2" --out $B/handoff.json > $B/handoff.log 2>&1 \
  || { echo "Předání odmítnuto:"; cat $B/handoff.log; exit 1; }
python3 scripts/agents.py run investor-evidence-auditor --prompt-file $B/auditor.txt --out $B --max-budget-usd 6 > $B/auditor.log 2>&1
echo "auditor exit $?" >> $B/auditor.log
python3 scripts/pilot/pages.py > /dev/null
python3 scripts/pilot/verify_quotes.py --markdown $B/investor-evidence-auditor.md > $B/quotes_auditor.txt 2>&1
python3 scripts/pilot/credits.py > $B/credits_after.txt 2>&1
head -2 $B/scout.log; tail -1 $B/quotes_scout.txt; head -2 $B/auditor.log; tail -1 $B/quotes_auditor.txt; cat $B/credits_after.txt
