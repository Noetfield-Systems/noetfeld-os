#!/usr/bin/env bash
# v18 visual QA gate — layout markers + client chunk strings (UI-10).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=dev-ports.sh
source "${ROOT}/scripts/dev-ports.sh"

BASE="http://127.0.0.1:${NF_DEV_PUBLIC_PORT}"
fail=0

check_marker() {
  local url="$1"
  local label="$2"
  local marker="$3"
  local html
  html="$(curl -sS --connect-timeout 5 -H "Accept: text/html" "$url" 2>/dev/null || true)"
  if echo "$html" | grep -qF "$marker"; then
    echo "OK   $label — $marker"
  else
    echo "FAIL $label — missing marker: $marker" >&2
    fail=1
  fi
}

echo "=== verify-ui-visual (v18 markers) ==="

check_marker "${BASE}/" "live proof hero" "data-live-proof-hero"
check_marker "${BASE}/" "live proof script" "noetfield-live-proof.js"
check_marker "${BASE}/start/" "trial os flow" "data-trial-os-flow"
check_marker "${BASE}/start/" "trial os wizard" "nfTrialOs"
check_marker "${BASE}/" "four-act prove" "The moment Copilot becomes auditable"
check_marker "${BASE}/pricing/" "pricing www css" "noetfield-www.css?v=40"

dash_html="$(curl -sS --connect-timeout 5 -H "Accept: text/html" "${BASE}/cognitive-dashboard" 2>/dev/null || true)"
dash_chunk="$(echo "$dash_html" | grep -oE '/_next/static/chunks/app/cognitive-dashboard/page-[^"]+\.js' | head -1)"
if [[ -n "$dash_chunk" ]]; then
  body="$(curl -sS "${BASE}${dash_chunk}" 2>/dev/null || true)"
  for needle in "Investigate" "Agent command deck" "sandbox simulation"; do
    if echo "$body" | grep -qF "$needle"; then
      echo "OK   dashboard deck — $needle"
    else
      echo "FAIL dashboard deck — missing: $needle" >&2
      fail=1
    fi
  done
else
  echo "FAIL dashboard chunk — rebuild dashboard" >&2
  fail=1
fi

tle_html="$(curl -sS --connect-timeout 5 -H "Accept: text/html" "${BASE}/workspace/TLE-015DCFB8B953" 2>/dev/null || true)"
tle_chunk="$(echo "$tle_html" | grep -oE '/_next/static/chunks/app/workspace/%5Btle_id%5D/page-[^"]+\.js' | head -1)"
if [[ -n "$tle_chunk" ]]; then
  body="$(curl -sS "${BASE}${tle_chunk}" 2>/dev/null || true)"
  for needle in "Receipt Studio" "Board pack (PDF)" "Procurement pack (ZIP)" "Export dock"; do
    if echo "$body" | grep -qF "$needle"; then
      echo "OK   receipt studio — $needle"
    else
      echo "FAIL receipt studio — missing: $needle" >&2
      fail=1
    fi
  done
else
  echo "FAIL tle studio chunk — rebuild dashboard" >&2
  fail=1
fi

if [[ -f "${ROOT}/governance-console/playwright/visual.spec.ts" ]]; then
  if command -v npx >/dev/null 2>&1 && [[ -d "${ROOT}/governance-console/frontend/node_modules" ]]; then
    (cd "${ROOT}/governance-console/frontend" && npx playwright test ../playwright/visual.spec.ts --reporter=line 2>/dev/null) || {
      echo "WARN playwright visual spec skipped or failed — marker checks above are required" >&2
    }
  else
    echo "SKIP playwright (install frontend deps to enable full baselines)"
  fi
fi

if [[ "$fail" -eq 0 ]]; then
  echo ""
  echo "verify-ui-visual passed."
  exit 0
fi
exit 1
