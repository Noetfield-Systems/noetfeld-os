#!/usr/bin/env bash
# Verify Noetfield business strategy docs in agent vault (010/011/013).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VAULT="$ROOT/docs/_NOOS_AGENT"
fail=0

check_file() {
  local label="$1" file="$2"
  shift 2
  [[ -f "$file" ]] || { echo "FAIL missing $label: $file" >&2; fail=1; return; }
  local missing=0 needle
  for needle in "$@"; do
    if ! grep -qF "$needle" "$file"; then
      echo "FAIL $label missing: $needle" >&2
      missing=1
    fi
  done
  [[ "$missing" -eq 0 ]] && echo "OK   $label" || fail=1
}

echo "=== check_noetfield_business_strategy ==="

check_file "strategy doc (010)" "$VAULT/[NOOS-AGENT-20260615-010]_BUSINESS_STRATEGY_PROOF_DENSITY_v1.md" \
  "NOOS-AGENT-DOC" "Proof-density" "NW1" "SW1" "tamper-FAIL" "Buyer 1" "Fit scorecard"

check_file "NW1 one-pager (011)" "$VAULT/[NOOS-AGENT-20260615-011]_FOUNDING_PILOT_ONEPAGER_EXTERNAL_v1.md" \
  "NOOS-AGENT-DOC" "TLE v1" "Board PDF" "CAD \$2,000" "tamper-FAIL" "Copilot"

check_file "SW1 one-pager (013)" "$VAULT/[NOOS-AGENT-20260615-013]_FOUNDING_PILOT_ONEPAGER_AGENTS_v1.md" \
  "NOOS-AGENT-DOC" "Runtime governance for AI agents" "CAD \$2,000" "tamper-FAIL" "signed audit chain"

python3 -c "
import json
m=json.load(open('$VAULT/MANIFEST.json'))
ids={d['trace_id'] for d in m['documents']}
for tid in ('NOOS-AGENT-20260615-010','NOOS-AGENT-20260615-011','NOOS-AGENT-20260615-013'):
    assert tid in ids, tid
print('OK   MANIFEST.json entries')
" || fail=1

if [[ "$fail" -eq 0 ]]; then
  echo ""
  echo "check_noetfield_business_strategy: PASS"
  exit 0
fi
exit 1
