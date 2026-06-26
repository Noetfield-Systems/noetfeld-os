#!/usr/bin/env bash
# Verify 300-step upgrade plan doc + manifest (NOOS-AGENT-20260615-014).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VAULT="$ROOT/docs/_NOOS_AGENT"
PLAN="$VAULT/[NOOS-AGENT-20260615-014]_UPGRADE_PLAN_300_STEPS_v1.md"
MANIFEST="$VAULT/UPGRADE_MANIFEST.json"
fail=0

echo "=== check_upgrade_plan_300 ==="

[[ -f "$PLAN" ]] || { echo "FAIL missing plan: $PLAN" >&2; fail=1; }
[[ -f "$MANIFEST" ]] || { echo "FAIL missing manifest: $MANIFEST" >&2; fail=1; }

if [[ -f "$PLAN" ]]; then
  for needle in "NOOS-AGENT-DOC" "UPG-0001" "UPG-0300" "Phase 1" "Phase 6" "api.noetfield.com" "noetfield-gate"; do
    grep -qF "$needle" "$PLAN" || { echo "FAIL plan missing: $needle" >&2; fail=1; }
  done
  count=$(grep -cE '\*\*UPG-[0-9]{4}:\*\*' "$PLAN" || true)
  if [[ "$count" -ne 300 ]]; then
    echo "FAIL expected 300 UPG steps, found $count" >&2
    fail=1
  else
    echo "OK   300 UPG steps present"
  fi
fi

if [[ -f "$MANIFEST" ]]; then
  python3 -c "
import json
m=json.load(open('$MANIFEST'))
assert m['total_steps']==300, m['total_steps']
assert m['plan_trace_id']=='NOOS-AGENT-20260615-014'
print('OK   UPGRADE_MANIFEST.json valid')
" || fail=1
fi

grep -qF "NOOS-AGENT-20260615-014" "$VAULT/MANIFEST.json" || {
  echo "FAIL MANIFEST.json missing 014 entry" >&2
  fail=1
}

if [[ "$fail" -eq 0 ]]; then
  echo ""
  echo "check_upgrade_plan_300: PASS"
  exit 0
fi
exit 1
