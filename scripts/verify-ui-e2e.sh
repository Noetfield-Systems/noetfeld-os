#!/usr/bin/env bash
# UI content checks beyond HTTP status — catches stale Next builds and route collisions.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=dev-ports.sh
source "${ROOT}/scripts/dev-ports.sh"

BASE="http://127.0.0.1:${NF_DEV_PUBLIC_PORT}"
fail=0

if [[ -f "${ROOT}/scripts/wait-dev-www-ready.sh" ]]; then
  chmod +x "${ROOT}/scripts/wait-dev-www-ready.sh"
  "${ROOT}/scripts/wait-dev-www-ready.sh"
fi

fetch_html() {
  local url="$1"
  local tries="${2:-3}"
  local html="" attempt
  for ((attempt = 1; attempt <= tries; attempt++)); do
    html="$(curl -sS --connect-timeout 5 -H "Accept: text/html" "$url" 2>/dev/null || true)"
    if [[ -n "$html" ]]; then
      echo "$html"
      return 0
    fi
    sleep 1
  done
  echo "$html"
}

check_html() {
  local url="$1"
  local label="$2"
  shift 2
  local html
  html="$(fetch_html "$url")"
  local missing=0
  for needle in "$@"; do
    if ! echo "$html" | grep -qF "$needle"; then
      echo "FAIL $label — missing: $needle" >&2
      missing=1
    fi
  done
  if [[ "$missing" -eq 0 ]]; then
    echo "OK   $label"
  else
    echo "     URL: $url" >&2
    echo "     Hint: NF_DEV_FORCE_DASHBOARD_BUILD=1 make dev-local" >&2
    fail=1
  fi
}

echo "=== verify-ui-e2e ==="

check_html "${BASE}/workspace" "workspace list" "Trust Ledger Workspace" "Create TLE draft"
check_html "${BASE}/workspace/connectors" "connectors page" "M365 evidence connectors" "Register + mock connect"
check_html "${BASE}/cognitive-dashboard" "cognitive dashboard" "Cognitive dashboard" "Submit operational intent"
check_html "${BASE}/evaluate" "evaluate page" "Submit operational intent"
check_html "${BASE}/audit" "audit page" "Audit log"
check_html "${BASE}/" "homepage pilot-first" "audit trail your Copilot deployment" 'Apply for pilot ($2k–10k)' "5-minute demo" "Start free sandbox"
check_html "${BASE}/" "homepage packaging" "Published tiers" "Developer access · free" "What regulated buyers receive"
check_html "${BASE}/" "homepage commercial path" "Commercial path" "Learn in sandbox" "Copilot Governance Pack"
check_html "${BASE}/copilot/pilot/" "pilot lane depth" "Digital trust lane" "Governance gaps" "Buyer voices" "Policy-bound workflows"
check_html "${BASE}/start/" "start sandbox" "Trial OS" "50 evaluate calls" "Apply for Governance Pack"
check_html "${BASE}/pricing/" "pricing tiers" "Sandbox + production" "14-day sandbox" "Apply for pilot"
check_html "${BASE}/docs/api/" "api sandbox CTA" "Start free sandbox" "Sandbox + production"
check_html "${BASE}/" "homepage v15 procurement rail" "Procurement" "Trust center" "Verify export" "Procurement pack"
check_html "${BASE}/" "homepage v15 ciso strip" "What legal and security reviewers need to see" "Fail-closed export"
check_html "${BASE}/" "homepage pain moment" "The moment AI execution becomes auditable" "One evaluate · four exports"
check_html "${BASE}/trust/" "trust center" "Trust center" "Metadata-only" "fail closed on tamper" "Shipped"
check_html "${BASE}/trust-ledger/verify/" "tle verify" "fail closed on tamper" "Verify export integrity"
check_html "${BASE}/copilot/" "copilot hub" "audit trail your Copilot deployment" "Phase 2" "Copilot Governance Pack"
check_html "${BASE}/copilot/pilot/" "copilot pilot" "Copilot Governance Pack" "GTM-locked pilot success signals" "nfPilotApplyForm"
check_html "${BASE}/copilot/demo/" "copilot demo" "Five-minute buyer story" "SSOT_CHANGED" "allow · 0.80" "Trust Ledger"
check_html "${BASE}/copilot/procurement/" "procurement buyer" "Procurement-grade export" "NIST AI RMF" "/trust/"
check_html "${BASE}/copilot/sme/" "copilot sme pack" "SME Governance Pack" "90-day Governance Pack" "confidence score"
check_html "${BASE}/trust-brief/" "trust brief" '$10,000' "Request Trust Brief"
check_html "${BASE}/federal/" "federal lane" "June 24, 2026" "Algorithmic Impact Assessment" "Copilot PIN" "canada.ca" "tbs-sct.canada.ca" "not a federal certifier"
check_html "${BASE}/msp/" "msp partner lane" "Readiness → Record" "Phase 1" "Phase 2" "Governance Pack"
check_html "${BASE}/" "homepage scope" "Available now" "Pre-execution evaluate" "Governance playground"
check_html "${BASE}/" "homepage receipt" "Trust Ledger Entry" "export_integrity" "fail closed"
check_html "${BASE}/" "homepage v18 live proof" "data-live-proof-hero" "live-proof-hero"
check_html "${BASE}/start/" "start trial os" "data-trial-os-flow" "trial-os-flow"
check_html "${BASE}/investors/" "investors success model" "Land → Expand → Channel" "Board PDF pilots open" "Company compliance automation"
check_html "${BASE}/trust-ledger/sample-report/" "tle samples" "Trust Ledger"
check_html "${BASE}/ai-automation/" "ai-automation operator" "Make your AI automation defensible" "Apply for pilot" "Scope (locked)"

ws_html="$(curl -sS --connect-timeout 5 -H "Accept: text/html" "${BASE}/workspace" 2>/dev/null || true)"
ws_chunk="$(echo "$ws_html" | grep -oE '/_next/static/chunks/app/workspace/page-[^"]+\.js' | head -1)"
if [[ -n "$ws_chunk" ]]; then
  ws_chunk_body="$(curl -sS "${BASE}${ws_chunk}" 2>/dev/null || true)"
  if echo "$ws_chunk_body" | grep -qF "5-minute demo script"; then
    echo "OK   workspace demo link"
  else
    echo "FAIL workspace demo link — rebuild dashboard" >&2
    fail=1
  fi
  if echo "$ws_chunk_body" | grep -qF "Mock OAuth connected" \
    && echo "$ws_chunk_body" | grep -qF "M365 evidence ingested"; then
    echo "OK   workspace oauth success banner"
  else
    echo "FAIL workspace oauth success banner — rebuild dashboard" >&2
    fail=1
  fi
else
  echo "FAIL workspace client chunk — rebuild dashboard" >&2
  fail=1
fi

tle_html="$(curl -sS --connect-timeout 5 -H "Accept: text/html" "${BASE}/workspace/TLE-015DCFB8B953" 2>/dev/null || true)"
tle_chunk="$(echo "$tle_html" | grep -oE '/_next/static/chunks/app/workspace/%5Btle_id%5D/page-[^"]+\.js' | head -1)"
if [[ -n "$tle_chunk" ]]; then
  chunk_body="$(curl -sS "${BASE}${tle_chunk}" 2>/dev/null || true)"
  if echo "$chunk_body" | grep -qF "Board pack (PDF)"; then
    echo "OK   tle detail PDF link"
  else
    echo "FAIL tle detail PDF link — rebuild dashboard" >&2
    fail=1
  fi
  if echo "$chunk_body" | grep -qF "Procurement pack (ZIP)"; then
    echo "OK   tle detail ZIP link"
  else
    echo "FAIL tle detail ZIP link — rebuild dashboard" >&2
    fail=1
  fi
  if echo "$chunk_body" | grep -qF "Confidence score"; then
    echo "OK   tle detail confidence badge"
  else
    echo "FAIL tle detail confidence badge — rebuild dashboard" >&2
    fail=1
  fi
else
  echo "FAIL tle detail export links — rebuild dashboard" >&2
  fail=1
fi

conn_html="$(curl -sS --connect-timeout 5 -H "Accept: text/html" "${BASE}/workspace/connectors" 2>/dev/null || true)"
if echo "$conn_html" | grep -qF 'params":{"tle_id":"connectors"'; then
  echo "FAIL /workspace/connectors hits [tle_id] dynamic route — run NF_DEV_FORCE_DASHBOARD_BUILD=1 make dev-local" >&2
  fail=1
else
  echo "OK   connectors not captured by [tle_id]"
fi

conn_chunk="$(echo "$conn_html" | grep -oE '/_next/static/chunks/app/workspace/connectors/page-[^"]+\.js' | head -1)"
if [[ -n "$conn_chunk" ]]; then
  conn_chunk_body="$(curl -sS "${BASE}${conn_chunk}" 2>/dev/null || true)"
  if echo "$conn_chunk_body" | grep -qF "Register + mock connect (M365)" \
    && echo "$conn_chunk_body" | grep -qF "m365-purview"; then
    echo "OK   connectors client chunk"
  else
    echo "FAIL connectors client chunk — rebuild dashboard" >&2
    fail=1
  fi
else
  echo "FAIL connectors client chunk — rebuild dashboard" >&2
  fail=1
fi

CONN_ID="verify-ui-$(date +%s)"
curl -sS -o /dev/null \
  -X POST "${BASE}/connectors" \
  -H "Content-Type: application/json" \
  -H "X-Tenant-ID: copilot-pilot-01" \
  -d "{\"connector_id\":\"${CONN_ID}\",\"connector_type\":\"m365_purview\",\"required_scopes\":[\"Purview.Read\"]}" \
  2>/dev/null || true
oauth_headers="$(curl -sS --max-redirs 0 -D - -o /dev/null \
  -H "Accept: text/html" \
  -H "X-Tenant-ID: copilot-pilot-01" \
  "${BASE}/connectors/${CONN_ID}/oauth/callback?code=dev-mock&state=verify-ui" 2>/dev/null || true)"
oauth_code="$(echo "$oauth_headers" | head -1 | awk '{print $2}')"
oauth_location="$(echo "$oauth_headers" | awk 'tolower($1)=="location:" {print $2}' | tr -d '\r')"
if [[ "$oauth_code" == "302" ]] && echo "$oauth_location" | grep -qF "/workspace?connected=${CONN_ID}"; then
  echo "OK   oauth html redirect to workspace"
else
  echo "FAIL oauth html redirect — expected 302 to /workspace?connected=${CONN_ID}" >&2
  echo "     code=${oauth_code} location=${oauth_location:-<empty>}" >&2
  fail=1
fi

eval_json="$(curl -sS --connect-timeout 5 -X POST "${BASE}/evaluate" \
  -H "Content-Type: application/json" \
  -d '{"actor":"ui-e2e","action":"smoke","context":"verify-ui-e2e confidence","metadata":{}}' 2>/dev/null || echo '{}')"
rid="$(python3 -c "import json,sys; print(json.loads(sys.argv[1]).get('rid',''))" "$eval_json" 2>/dev/null || true)"
if [[ -z "$rid" ]]; then
  echo "FAIL evaluate flow (no rid)" >&2
  fail=1
else
  result_url="${BASE}/result/${rid}"
  check_html "$result_url" "result page shell" "Governance decision"
  result_html="$(curl -sS --connect-timeout 5 -H "Accept: text/html" "$result_url" 2>/dev/null || true)"
  result_chunk="$(echo "$result_html" | grep -oE '/_next/static/chunks/app/result/%5Brid%5D/page-[^"]+\.js' | head -1)"
  if [[ -n "$result_chunk" ]]; then
    chunk_body="$(curl -sS "${BASE}${result_chunk}" 2>/dev/null || true)"
    if echo "$chunk_body" | grep -qF "Confidence score"; then
      echo "OK   result page confidence badge (rid=${rid})"
    else
      echo "FAIL result page confidence badge — rebuild dashboard" >&2
      fail=1
    fi
  else
    echo "FAIL result page chunk — rebuild dashboard (rid=${rid})" >&2
    fail=1
  fi
fi

VENDOR_PATTERN='Veridra|Vanta|Drata|OneTrust|Inforcer|Securiti|Credo AI|Holistic AI|Audital'
LEGACY_GTM_PATTERN='design.partner|Design.partner|Become a design partner|Apply to design partner|Purview-only trap|Accepting design partners'
for path in / /trust/ /copilot/ /copilot/pilot/ /msp/ /federal/ /investors/ /start/ /pricing/; do
  page_html="$(curl -sS --connect-timeout 5 -H "Accept: text/html" "${BASE}${path}" 2>/dev/null || true)"
  if echo "$page_html" | grep -Eiq "$VENDOR_PATTERN"; then
    echo "FAIL vendor name on ${path} — public www must use zone labels only" >&2
    fail=1
  else
    echo "OK   no vendor names on ${path}"
  fi
  if echo "$page_html" | grep -Eiq "$LEGACY_GTM_PATTERN"; then
    echo "FAIL legacy GTM copy on ${path} — use Copilot Governance Pack / Apply for pilot" >&2
    fail=1
  else
    echo "OK   no legacy design-partner copy on ${path}"
  fi
done

if [[ "$fail" -eq 0 ]]; then
  echo ""
  echo "verify-ui-e2e passed."
  exit 0
fi
exit 1
