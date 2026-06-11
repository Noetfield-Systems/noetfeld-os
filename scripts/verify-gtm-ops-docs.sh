#!/usr/bin/env bash
# GTM ops docs — served on :13080 and linked from copilot pilot/demo pages.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=dev-ports.sh
source "${ROOT}/scripts/dev-ports.sh"

BASE="http://127.0.0.1:${NF_DEV_PUBLIC_PORT}"
fail=0

echo "=== verify-gtm-ops-docs ==="

check_url() {
  local url="$1"
  local label="$2"
  local code
  code="$(curl -sS -o /dev/null -w "%{http_code}" --connect-timeout 5 "$url" 2>/dev/null || echo "000")"
  if [[ "$code" == "200" ]]; then
    echo "OK   $label ($code)"
  else
    echo "FAIL $label ($code) $url" >&2
    fail=1
  fi
}

check_url "${BASE}/docs/copilot/DESIGN_PARTNER_PIPELINE_v1.md" "pipeline doc"
check_url "${BASE}/docs/ops/DEMO_REHEARSAL_CHECKLIST_v1.md" "demo rehearsal doc"
check_url "${BASE}/docs/copilot/BUYER_DEBRIEF_TEMPLATE_v1.md" "buyer debrief doc"
check_url "${BASE}/docs/strategy/channel-outreach/bc-ai-for-all-2026.md" "bc-ai outreach doc"
check_url "${BASE}/docs/diligence/rpaa-positioning-onepager.md" "rpaa diligence one-pager"
check_url "${BASE}/docs/ops/STAGING_DEMO.md" "staging demo runbook"
check_url "${BASE}/docs/copilot/PROCUREMENT_ONE_PAGER.md" "procurement one-pager doc"
check_url "${BASE}/docs/references/GOVERNANCE_SOURCES_BOOK_v1.md" "governance sources book doc"
check_url "${BASE}/docs/references/GOVERNANCE_SOURCES_HANDBOOK_LOCKED_v1.md" "governance sources handbook doc"

pipeline_body="$(curl -sS --connect-timeout 5 "${BASE}/docs/copilot/DESIGN_PARTNER_PIPELINE_v1.md" 2>/dev/null || true)"
if echo "$pipeline_body" | grep -qF "bc-ai-for-all-2026"; then
  echo "OK   pipeline doc bc-ai channel reference"
else
  echo "FAIL pipeline doc missing bc-ai-for-all-2026 reference" >&2
  fail=1
fi
if echo "$pipeline_body" | grep -qF "STAGING_DEMO"; then
  echo "OK   pipeline doc staging demo reference"
else
  echo "FAIL pipeline doc missing STAGING_DEMO reference" >&2
  fail=1
fi

for path in "/copilot/pilot/" "/copilot/demo/"; do
  html="$(curl -sS --connect-timeout 5 -H "Accept: text/html" "${BASE}${path}" 2>/dev/null || true)"
  if echo "$html" | grep -qF "Design partner pipeline"; then
    echo "OK   ${path} pipeline link text"
  else
    echo "FAIL ${path} missing Design partner pipeline" >&2
    fail=1
  fi
  if echo "$html" | grep -qF "bc-ai-for-all-2026.md"; then
    echo "OK   ${path} bc-ai outreach link"
  else
    echo "FAIL ${path} missing bc-ai-for-all-2026.md link" >&2
    fail=1
  fi
  if echo "$html" | grep -qF "rpaa-positioning-onepager"; then
    echo "OK   ${path} rpaa diligence link"
  else
    echo "FAIL ${path} missing rpaa-positioning-onepager link" >&2
    fail=1
  fi
  if echo "$html" | grep -qF "STAGING_DEMO"; then
    echo "OK   ${path} staging demo link"
  else
    echo "FAIL ${path} missing STAGING_DEMO link" >&2
    fail=1
  fi
done

tle_www="$(curl -sS --connect-timeout 5 -H "Accept: text/html" "${BASE}/trust-ledger/" 2>/dev/null || true)"
if echo "$tle_www" | grep -qF "security buyer"; then
  echo "OK   /trust-ledger/ security buyer copy"
else
  echo "FAIL /trust-ledger/ missing security buyer copy" >&2
  fail=1
fi
if echo "$tle_www" | grep -qF "rpaa-positioning-onepager"; then
  echo "OK   /trust-ledger/ rpaa diligence link"
else
  echo "FAIL /trust-ledger/ missing rpaa-positioning-onepager link" >&2
  fail=1
fi

proc_html="$(curl -sS --connect-timeout 5 -H "Accept: text/html" "${BASE}/copilot/procurement/" 2>/dev/null || true)"
if echo "$proc_html" | grep -qF "rpaa-positioning-onepager"; then
  echo "OK   /copilot/procurement/ rpaa diligence link"
else
  echo "FAIL /copilot/procurement/ missing rpaa-positioning-onepager link" >&2
  fail=1
fi
if echo "$proc_html" | grep -qF "PROCUREMENT_ONE_PAGER"; then
  echo "OK   /copilot/procurement/ procurement one-pager link"
else
  echo "FAIL /copilot/procurement/ missing PROCUREMENT_ONE_PAGER link" >&2
  fail=1
fi
if echo "$proc_html" | grep -qF "GOVERNANCE_SOURCES_BOOK_v1.md"; then
  echo "OK   /copilot/procurement/ governance sources book link"
else
  echo "FAIL /copilot/procurement/ missing GOVERNANCE_SOURCES_BOOK link" >&2
  fail=1
fi
if echo "$proc_html" | grep -qF "GOVERNANCE_SOURCES_HANDBOOK_LOCKED_v1.md"; then
  echo "OK   /copilot/procurement/ governance sources handbook link"
else
  echo "FAIL /copilot/procurement/ missing GOVERNANCE_SOURCES_HANDBOOK link" >&2
  fail=1
fi
if echo "$proc_html" | grep -qF "control checkpoint"; then
  echo "OK   /copilot/procurement/ eval+enforce checkpoint copy"
else
  echo "FAIL /copilot/procurement/ missing control checkpoint copy" >&2
  fail=1
fi
if echo "$proc_html" | grep -qF "Governance control checkpoints"; then
  echo "OK   /copilot/procurement/ checkpoint section heading"
else
  echo "FAIL /copilot/procurement/ missing checkpoint section heading" >&2
  fail=1
fi
if echo "$proc_html" | grep -qF "plan-with-no-asf-verify.sh"; then
  echo "OK   /copilot/procurement/ evaluate checkpoint cites verify script"
else
  echo "FAIL /copilot/procurement/ missing verify script in checkpoint copy" >&2
  fail=1
fi
if echo "$proc_html" | grep -qF "AGENT_SELF_AUDIT_LOOP_LOCKED_v1.md"; then
  echo "OK   /copilot/procurement/ checkpoint links audit loop doc"
else
  echo "FAIL /copilot/procurement/ missing audit loop link in checkpoint copy" >&2
  fail=1
fi
if echo "$proc_html" | grep -qF "/openapi.json"; then
  echo "OK   /copilot/procurement/ public OpenAPI link"
else
  echo "FAIL /copilot/procurement/ missing public OpenAPI link" >&2
  fail=1
fi
if echo "$proc_html" | grep -qF "services/governance/README.md"; then
  echo "OK   /copilot/procurement/ services/governance README link"
else
  echo "FAIL /copilot/procurement/ missing services/governance README link" >&2
  fail=1
fi

hub_html="$(curl -sS --connect-timeout 5 -H "Accept: text/html" "${BASE}/copilot/" 2>/dev/null || true)"
if echo "$hub_html" | grep -qF "PROCUREMENT_ONE_PAGER"; then
  echo "OK   /copilot/ procurement one-pager link"
else
  echo "FAIL /copilot/ missing PROCUREMENT_ONE_PAGER link" >&2
  fail=1
fi
if echo "$hub_html" | grep -qF "GOVERNANCE_SOURCES_BOOK_v1.md"; then
  echo "OK   /copilot/ governance sources book link"
else
  echo "FAIL /copilot/ missing GOVERNANCE_SOURCES_BOOK link" >&2
  fail=1
fi
check_url "${BASE}/docs/references/GOVERNANCE_DRIFT_DETECTION_SOURCES_LOCKED_v1.md" "drift detection sources locked doc"

if echo "$proc_html" | grep -qF "GOVERNANCE_DRIFT_DETECTION_SOURCES_LOCKED_v1.md"; then
  echo "OK   /copilot/procurement/ drift detection sources link"
else
  echo "FAIL /copilot/procurement/ missing drift detection sources link" >&2
  fail=1
fi
if echo "$proc_html" | grep -qF "GOVERNANCE_DRIFT_BLUEPRINTS_INDEX_LOCKED_v1.md"; then
  echo "OK   /copilot/procurement/ drift blueprints index link"
else
  echo "FAIL /copilot/procurement/ missing drift blueprints index link" >&2
  fail=1
fi
pilot_html="$(curl -sS --connect-timeout 5 -H "Accept: text/html" "${BASE}/copilot/pilot/" 2>/dev/null || true)"
demo_html="$(curl -sS --connect-timeout 5 -H "Accept: text/html" "${BASE}/copilot/demo/" 2>/dev/null || true)"

# ship-trust-brief-parity-audit-045: single fail-closed loop (4 buyer pages)
trust_brief_ok=0
for entry in "hub_html|/copilot/" "pilot_html|/copilot/pilot/" "demo_html|/copilot/demo/" "proc_html|/copilot/procurement/"; do
  var="${entry%%|*}"
  path="${entry#*|}"
  html="${!var}"
  if echo "$html" | grep -qF "/trust-brief/intake/"; then
    echo "OK   ${path} trust-brief intake CTA"
    trust_brief_ok=$((trust_brief_ok + 1))
  else
    echo "FAIL ${path} missing trust-brief intake CTA" >&2
    fail=1
  fi
done
if [[ "$trust_brief_ok" -eq 4 ]]; then
  echo "OK   trust-brief parity (4/4 buyer pages)"
fi

# ship-rehearsal-parity-all-pages-049: single fail-closed loop (hub prose + pilot ol + demo ol)
rehearsal_ok=0
for entry in "hub_html|/copilot/" "pilot_html|/copilot/pilot/" "demo_html|/copilot/demo/"; do
  var="${entry%%|*}"
  path="${entry#*|}"
  html="${!var}"
  if echo "$html" | grep -qF "DEMO_REHEARSAL_CHECKLIST_v1.md"; then
    echo "OK   ${path} rehearsal checklist"
    rehearsal_ok=$((rehearsal_ok + 1))
  else
    echo "FAIL ${path} missing DEMO_REHEARSAL_CHECKLIST" >&2
    fail=1
  fi
done
if [[ "$rehearsal_ok" -eq 3 ]]; then
  echo "OK   rehearsal parity (3/3 buyer runbooks)"
fi

home_html="$(curl -sS --connect-timeout 5 -H "Accept: text/html" "${BASE}/" 2>/dev/null || true)"
if echo "$home_html" | grep -qF 'href="/copilot/procurement/"'; then
  echo "OK   / homepage procurement hero CTA"
else
  echo "FAIL / homepage missing procurement hero CTA" >&2
  fail=1
fi

debrief_body="$(curl -sS --connect-timeout 5 "${BASE}/docs/copilot/BUYER_DEBRIEF_TEMPLATE_v1.md" 2>/dev/null || true)"
for needle in "Board PDF used in governance meeting" "Persona" "Next step"; do
  if echo "$debrief_body" | grep -qF "$needle"; then
    echo "OK   debrief template field: $needle"
  else
    echo "FAIL debrief template missing: $needle" >&2
    fail=1
  fi
done

if [[ "$fail" -eq 0 ]]; then
  echo ""
  echo "verify-gtm-ops-docs passed."
  exit 0
fi
exit 1
