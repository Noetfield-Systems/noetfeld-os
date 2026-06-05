#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=dev-ports.sh
source "${ROOT}/scripts/dev-ports.sh"

PUBLIC="$NF_DEV_PUBLIC_PORT"
PLATFORM="$NF_DEV_PLATFORM_PORT"
fail=0

check() {
  local url="$1"
  local label="$2"
  local code
  code="$(curl -sS -o /dev/null -w "%{http_code}" --connect-timeout 3 "$url" 2>/dev/null || echo "000")"
  if [[ "$code" =~ ^(200|301|302|307)$ ]]; then
    echo "OK   $label ($code) $url"
  else
    echo "FAIL $label ($code) $url" >&2
    fail=1
  fi
}

echo "=== verify-local-dev ==="

check "http://127.0.0.1:${PUBLIC}/" "website"
check "http://127.0.0.1:${PUBLIC}/console" "console (proxy)"
check "http://127.0.0.1:${PUBLIC}/cognitive-dashboard" "dashboard (proxy)"
check "http://127.0.0.1:${PUBLIC}/trust-ledger" "trust-ledger (proxy)"
check "http://127.0.0.1:${PUBLIC}/docs/api/" "docs/api (static)"
check "http://127.0.0.1:${PLATFORM}/console" "console (direct)"
check "http://127.0.0.1:${PUBLIC}/assets/noetfield-tokens.css" "www assets"

LEGACY="${NF_DEV_LEGACY_NEXT_PORT:-3000}"
legacy_code="$(curl -sS -o /dev/null -w "%{http_code}" --max-redirs 0 --connect-timeout 2 \
  "http://127.0.0.1:${LEGACY}/" 2>/dev/null || echo "000")"
if [[ "$legacy_code" == "302" ]]; then
  echo "OK   legacy :${LEGACY} redirect (302)"
elif [[ "$legacy_code" == "000" ]]; then
  echo "OK   legacy :${LEGACY} (not in use)"
else
  echo "WARN legacy :${LEGACY} ($legacy_code) — use http://localhost:${PUBLIC}/" >&2
fi

# governance evaluate via proxy
eval_code="$(curl -sS -o /dev/null -w "%{http_code}" --connect-timeout 5 \
  -X POST "http://127.0.0.1:${PUBLIC}/api/v1/governance/evaluate" \
  -H "Content-Type: application/json" \
  -d '{"tenant_id":"00000000-0000-4000-8000-000000000001","organization_id":"00000000-0000-4000-8000-000000000002","action":"publish_board_report","resource_type":"governance_artifact","resource_id":"verify-local","mode":"shadow"}' \
  2>/dev/null || echo "000")"
if [[ "$eval_code" == "200" ]]; then
  echo "OK   governance evaluate (200)"
else
  echo "FAIL governance evaluate ($eval_code)" >&2
  fail=1
fi

dash_eval="$(curl -sS -o /tmp/nf-dash-eval.json -w "%{http_code}" --connect-timeout 5 \
  -X POST "http://127.0.0.1:${PUBLIC}/evaluate" \
  -H "Content-Type: application/json" \
  -d '{"actor":"verify","action":"smoke","context":"local dev","metadata":{}}' \
  2>/dev/null || echo "000")"
if [[ "$dash_eval" == "200" ]] && grep -q '"decision"' /tmp/nf-dash-eval.json 2>/dev/null; then
  echo "OK   dashboard API via proxy (200 JSON)"
else
  echo "FAIL dashboard API via proxy ($dash_eval) — POST /evaluate must hit gov API, not Next HTML" >&2
  fail=1
fi

if [[ "$fail" -eq 0 ]]; then
  echo ""
  echo "All checks passed."
  echo "Open: http://localhost:${PUBLIC}/"
  exit 0
fi
echo ""
echo "Run: make dev-local" >&2
exit 1
