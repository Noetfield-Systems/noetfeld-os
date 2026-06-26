#!/usr/bin/env bash
# GTM buyer proof docs — served on :13080; public pages link buyer-facing docs only.
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

# Docs remain on disk for ops/diligence — not required on public copilot hero copy
check_url "${BASE}/docs/copilot/BUYER_DEBRIEF_TEMPLATE_v1.md" "buyer debrief doc"
check_url "${BASE}/docs/diligence/rpaa-positioning-onepager.md" "rpaa diligence one-pager"
check_url "${BASE}/docs/copilot/PROCUREMENT_ONE_PAGER.md" "procurement one-pager doc"
check_url "${BASE}/docs/references/GOVERNANCE_SOURCES_BOOK_v1.md" "governance sources book doc"
check_url "${BASE}/docs/references/GOVERNANCE_SOURCES_HANDBOOK_LOCKED_v1.md" "governance sources handbook doc"
check_url "${BASE}/docs/references/GOVERNANCE_DRIFT_DETECTION_SOURCES_LOCKED_v1.md" "drift detection sources locked doc"

# Public copilot pages — client proof section, no founder runbooks
FOUNDER_LINK_PATTERN='STAGING_DEMO|DEMO_REHEARSAL_CHECKLIST|gtm-ops-runbooks|COPILOT_GOVERNANCE_PIPELINE_v1'
proof_ok=0
for path in "/copilot/" "/copilot/pilot/" "/copilot/demo/"; do
  html="$(curl -sS --connect-timeout 5 -H "Accept: text/html" "${BASE}${path}" 2>/dev/null || true)"
  if echo "$html" | grep -qF 'buyer-proof-links' \
    && echo "$html" | grep -qF 'Proof and diligence' \
    && echo "$html" | grep -qF '/copilot/procurement/' \
    && ! echo "$html" | grep -qE "$FOUNDER_LINK_PATTERN"; then
    echo "OK   ${path} buyer-proof section (no founder runbooks)"
    proof_ok=$((proof_ok + 1))
  else
    echo "FAIL ${path} missing buyer-proof or has founder runbook links" >&2
    fail=1
  fi
done
[[ "$proof_ok" -eq 3 ]] && echo "OK   buyer-proof parity (3/3 copilot pages)"

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
if echo "$proc_html" | grep -qF "/openapi.json"; then
  echo "OK   /copilot/procurement/ public OpenAPI link"
else
  echo "FAIL /copilot/procurement/ missing public OpenAPI link" >&2
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

check_url "${BASE}/openapi.json" "public OpenAPI schema (procurement path)"

if [[ "$fail" -eq 0 ]]; then
  echo ""
  echo "verify-gtm-ops-docs passed."
  exit 0
fi
exit 1
