#!/usr/bin/env bash
# Lane fences: Noetfield repo must not commit TrustField implementation tasks or competitor names on www.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
fail=0

_search() {
  grep -r -l -i -E "$1" docs os .cursor 2>/dev/null \
    | grep -v -E 'plan-library|nf-future|reject|grep|conflict-matrix|noetfield-scope|NOETFIELD_AGENT_TEAM|AGENT_SELF_AUDIT|\.cursor/skills|\.cursor/incidents|\.cursor/agent-memory|\.cursor/reports' || true
}

hits="$(_search 'implement.*trustfield|trustfield.*implement')"
if [[ -n "$hits" ]]; then
  echo "FAIL: TrustField implementation language in Noetfield docs" >&2
  echo "$hits" | head -5 >&2
  fail=1
fi

for name in Stripe Adyen Wise Revolut Monzo Chime; do
  if grep -r -q -i "\\b${name}\\b" index.html www 2>/dev/null; then
    echo "FAIL: competitor name '${name}' in www copy" >&2
    fail=1
  fi
done

# Lane C — TLE/evaluate schemas must not ship payment/custody fields (PRODUCT_TRUTH)
if grep -E 'payment_rail|custody_account|wire_transfer_id' governance-console/backend/schemas.py 2>/dev/null \
  | grep -v -E '# lane-c-forbidden|Lane C'; then
  echo "FAIL: Lane C payment fields in TLE/evaluate schemas" >&2
  fail=1
fi

if [[ "$fail" -ne 0 ]]; then
  exit 1
fi
echo "verify-lane-fences PASS"
