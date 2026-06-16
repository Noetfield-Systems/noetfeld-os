#!/usr/bin/env bash
# Investor governance diligence lane — docs, public page, intake vectors, buyer-audience gate.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
fail=0

echo "=== verify-investor-diligence-lane ==="

require_file() {
  local rel="$1"
  local min_bytes="${2:-500}"
  if [[ ! -f "$rel" ]]; then
    echo "FAIL missing: $rel" >&2
    fail=1
    return
  fi
  local size
  size="$(wc -c < "$rel" | tr -d ' ')"
  if [[ "$size" -lt "$min_bytes" ]]; then
    echo "FAIL $rel too small ($size bytes)" >&2
    fail=1
    return
  fi
  echo "OK   $rel ($size bytes)"
}

require_file docs/strategy/INVESTOR_GOVERNANCE_LANE_LOCKED_v1.md 1500
require_file docs/diligence/INVESTOR_GOVERNANCE_CHECKLIST_MAP_v1.md 2000
require_file docs/diligence/IC_GOVERNANCE_APPENDIX_TEMPLATE_v1.md 1500
require_file gate/diligence/index.html 3000

checklist="$(cat docs/diligence/INVESTOR_GOVERNANCE_CHECKLIST_MAP_v1.md)"
for group in "Group 1" "Group 2" "Group 3" "Group 4"; do
  if ! grep -qF "$group" <<< "$checklist"; then
    echo "FAIL checklist map missing $group" >&2
    fail=1
  else
    echo "OK   checklist map has $group"
  fi
done

diligence="$(cat gate/diligence/index.html)"
for phrase in "decision-evidence" "Trust Brief"; do
  if ! grep -qiF "$phrase" <<< "$diligence"; then
    echo "FAIL gate/diligence missing: $phrase" >&2
    fail=1
  else
    echo "OK   gate/diligence contains: $phrase"
  fi
done

for bad in "fourth SKU" "Kenaz" "Intor" "Falkovia" "Big Four"; do
  if grep -qiF "$bad" <<< "$diligence"; then
    echo "FAIL gate/diligence must not mention: $bad" >&2
    fail=1
  fi
done
echo "OK   gate/diligence has no vendor/fourth-SKU bleed"

for intake in gate/intake/index.html trust-brief/intake/index.html; do
  if ! grep -qF "investor-diligence" "$intake"; then
    echo "FAIL $intake missing investor-diligence vector" >&2
    fail=1
  else
    echo "OK   $intake has investor-diligence vector"
  fi
done

investors="$(cat gate/partners/investors/index.html)"
if ! grep -q 'noindex' <<< "$investors"; then
  echo "FAIL gate/partners/investors must remain noindex" >&2
  fail=1
else
  echo "OK   gate/partners/investors is noindex"
fi

home="$(cat index.html)"
if grep -qiF "GCIP" <<< "$home" || grep -qF "(internal)" <<< "$home"; then
  echo "FAIL index.html trust strip still has internal bleed" >&2
  fail=1
else
  echo "OK   index.html has no GCIP / (internal) bleed"
fi

if ! grep -qF '/gate/diligence/' assets/partials/footer.html; then
  echo "FAIL footer missing Gate → Diligence link" >&2
  fail=1
else
  echo "OK   footer links to /gate/diligence/"
fi

if ! grep -qF 'instTopbar' assets/partials/header.html; then
  echo "FAIL header missing institutional topbar" >&2
  fail=1
else
  echo "OK   header has institutional topbar"
fi

if ! grep -qF 'navGroup' assets/partials/header.html; then
  echo "FAIL header missing grouped nav" >&2
  fail=1
else
  echo "OK   header has grouped institutional nav"
fi

if ! grep -qF 'Canada' assets/partials/header.html; then
  echo "FAIL header missing Canada institutional badge" >&2
  fail=1
else
  echo "OK   header tuned for Canada"
fi

if [[ "$fail" -eq 0 ]]; then
  echo ""
  echo "Running nested buyer-audience gate..."
  ./scripts/verify-www-buyer-audience.sh
  echo ""
  echo "verify-investor-diligence-lane passed."
  exit 0
fi
echo ""
echo "Investor diligence lane verification failed." >&2
exit 1
