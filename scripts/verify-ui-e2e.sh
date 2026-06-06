#!/usr/bin/env bash
# UI content checks beyond HTTP status — catches stale Next builds and route collisions.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=dev-ports.sh
source "${ROOT}/scripts/dev-ports.sh"

BASE="http://127.0.0.1:${NF_DEV_PUBLIC_PORT}"
fail=0

check_html() {
  local url="$1"
  local label="$2"
  shift 2
  local html
  html="$(curl -sS --connect-timeout 5 -H "Accept: text/html" "$url" 2>/dev/null || true)"
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
check_html "${BASE}/" "homepage" "audit trail your Copilot deployment" "Become a design partner"
check_html "${BASE}/copilot/" "copilot hub" "audit trail your Copilot deployment" "5-minute demo"
check_html "${BASE}/copilot/pilot/" "copilot pilot" "Design-partner Go/No-Go" "Design partner program"
check_html "${BASE}/copilot/demo/" "copilot demo" "5-minute demo" "Demo script (locked narrative)" "confidence score"
check_html "${BASE}/copilot/procurement/" "procurement buyer" "buyer pack" "Procurement pack (ZIP)" "NIST AI RMF"
check_html "${BASE}/trust-ledger/sample-report/" "tle samples" "Trust Ledger"

ws_html="$(curl -sS --connect-timeout 5 -H "Accept: text/html" "${BASE}/workspace" 2>/dev/null || true)"
ws_chunk="$(echo "$ws_html" | grep -oE '/_next/static/chunks/app/workspace/page-[^"]+\.js' | head -1)"
if [[ -n "$ws_chunk" ]] && curl -sS "${BASE}${ws_chunk}" 2>/dev/null | grep -qF "5-minute demo script"; then
  echo "OK   workspace demo link"
else
  echo "FAIL workspace demo link — rebuild dashboard" >&2
  fail=1
fi

# TLE detail must expose PDF export in client chunk (CSR page)
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

if [[ "$fail" -eq 0 ]]; then
  echo ""
  echo "verify-ui-e2e passed."
  exit 0
fi
exit 1
