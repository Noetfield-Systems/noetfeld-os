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

for path in "/copilot/pilot/" "/copilot/demo/"; do
  html="$(curl -sS --connect-timeout 5 -H "Accept: text/html" "${BASE}${path}" 2>/dev/null || true)"
  if echo "$html" | grep -qF "Design partner pipeline"; then
    echo "OK   ${path} pipeline link text"
  else
    echo "FAIL ${path} missing Design partner pipeline" >&2
    fail=1
  fi
  if echo "$html" | grep -qF "demo rehearsal"; then
    echo "OK   ${path} rehearsal link text"
  else
    echo "FAIL ${path} missing demo rehearsal" >&2
    fail=1
  fi
done

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
