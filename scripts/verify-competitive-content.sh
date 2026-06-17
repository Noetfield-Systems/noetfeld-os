#!/usr/bin/env bash
# Verify competitive / procurement content on disk.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
fail=0
ok() { echo "OK   $*"; }
bad() { echo "FAIL $*" >&2; fail=1; }

echo "=== verify-competitive-content ==="

for f in \
  docs/diligence/COMPETITIVE_LANDSCAPE_LOCKED_v1.md \
  docs/diligence/battlecards/BATTLECARD_VS_PURVIEW_LOCKED_v1.md \
  docs/diligence/battlecards/BATTLECARD_VS_CREDO_LOCKED_v1.md \
  docs/diligence/battlecards/BATTLECARD_VS_SECURITI_LOCKED_v1.md \
  docs/diligence/CANADIAN_OSFI_E23_COPILOT_ORIENTATION_v1.md \
  docs/diligence/PROOF_CASE_COPILOT_EVALUATE_TLE_v1.md \
  docs/copilot/PROCUREMENT_COMPETITIVE_FAQ_v1.md; do
  [[ -f "$f" ]] && ok "$f" || bad "missing $f"
done

for f in copilot/procurement/index.html copilot/proof-case/index.html copilot/governance-audit-trail/index.html; do
  [[ -f "$f" ]] && ok "$f" || bad "missing $f"
done

grep -q 'buyer-faq' copilot/procurement/index.html && ok 'procurement buyer FAQ' || bad 'procurement FAQ section'
grep -q 'governance-audit-trail' copilot/governance-audit-trail/index.html && ok 'SEO audit trail page' || bad 'audit trail page'
grep -q 'TLE-015DCFB8B953' copilot/proof-case/index.html && ok 'proof case TLE' || bad 'proof case content'

# Banned comparison phrases must not appear on index.html (verify-static-www rule)
COMP_PATTERN='not another|They configure|Complement, not compete|six-figure GRC'
if grep -E -i -q "$COMP_PATTERN" index.html 2>/dev/null; then
  bad "banned comparison phrase on index.html"
else
  ok "index.html comparison-safe"
fi

if [[ "$fail" -eq 0 ]]; then
  echo ""
  echo "verify-competitive-content passed."
  exit 0
fi
exit 1
