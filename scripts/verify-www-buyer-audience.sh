#!/usr/bin/env bash
# Buyer-audience copy gate — www must speak to ICP (CISO, procurement, legal, investors),
# not founders, agents, or internal repo language. Adapted for platform-blueprint branch.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
fail=0

echo "=== verify-www-buyer-audience ==="

PAGES=(
  index.html
  trust-brief/index.html
  trust-brief/intake/index.html
  copilot/index.html
  copilot/demo/index.html
  copilot/trial/index.html
  gate/intake/index.html
  gate/diligence/index.html
  gate/procurement/index.html
  gate/procurement/procurement-pack/index.html
  trust-ledger/index.html
  trust-ledger/sample-report/index.html
  faq/index.html
  status/index.html
  privacy/index.html
  contact/index.html
)

PARTIALS=(
  assets/partials/footer.html
)

FORBIDDEN=(
  'GCIP'
  'internal tracking'
  'founder sign-off'
  'founder attest'
  'this repo'
  'docs/ops/'
  'plan-with-no-asf'
  'AGENT_SELF_AUDIT'
  'NF-CLOUD'
  'Founder / solutions'
  'TrustField execution'
  'docs/strategy/PACKAGING'
  'Ship verify'
  'ship verification'
  'internal release gate'
  'Buyer surface coherence'
  'outreach copy'
  'STAGING_DEMO'
  'Internal runbook'
  'until founder sign-off'
  'Revenue grows from'
  'local dev:'
  'PRODUCT_TRUTH'
  'repo-native'
  'agent self-audit'
  'packages/sdk'
  'Noetfield-Systems'
  'Repository docs'
)

CAPITAL_RAISE_ON_INDEXED=(
  'raising our seed'
  'Noetfield is raising'
  'invest in Noetfield'
)

scan_file() {
  local rel="$1"
  local label="$2"
  if [[ ! -f "$rel" ]]; then
    echo "FAIL missing required page: $rel" >&2
    fail=1
    return 0
  fi
  local text page_fail=0
  text="$(cat "$rel")"
  for phrase in "${FORBIDDEN[@]}"; do
    if grep -qF "$phrase" <<< "$text"; then
      echo "FAIL $label — internal phrase: $phrase" >&2
      page_fail=1
      fail=1
    fi
  done
  if [[ "$rel" != gate/partners/investors/index.html ]]; then
    for phrase in "${CAPITAL_RAISE_ON_INDEXED[@]}"; do
      if grep -qiF "$phrase" <<< "$text"; then
        echo "FAIL $label — capital-raise phrase on indexed page: $phrase" >&2
        page_fail=1
        fail=1
      fi
    done
  fi
  if [[ "$page_fail" -eq 0 ]]; then
    echo "OK   $label buyer-audience clean"
  fi
}

for rel in "${PAGES[@]}"; do
  label="${rel%/index.html}"
  label="${label:-homepage}"
  scan_file "$rel" "$label"
done

for rel in "${PARTIALS[@]}"; do
  scan_file "$rel" "partial:${rel}"
done

if grep -q 'gate/partners/investors' assets/partials/footer.html 2>/dev/null; then
  echo "FAIL footer links to capital-raise investors lane" >&2
  fail=1
else
  echo "OK   footer does not link capital-raise investors lane"
fi

if [[ "$fail" -eq 0 ]]; then
  echo ""
  echo "verify-www-buyer-audience passed (${#PAGES[@]} pages + partials)."
  exit 0
fi
echo ""
echo "Remove founder/agent/internal copy from www. Buyers only." >&2
exit 1
