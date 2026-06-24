#!/usr/bin/env bash
# UI end-to-end HTTP checks on unified dev proxy (:13080).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=dev-ports.sh
source "${ROOT}/scripts/dev-ports.sh"

PUBLIC="$NF_DEV_PUBLIC_PORT"
fail=0

check() {
  local url="$1"
  local label="$2"
  local expect="${3:-200}"
  local code
  code="$(curl -sS -o /dev/null -w "%{http_code}" --connect-timeout 5 "$url" 2>/dev/null || echo "000")"
  if [[ "$code" == "$expect" ]]; then
    echo "OK   $label ($code) $url"
  else
    echo "FAIL $label ($code, want $expect) $url" >&2
    fail=1
  fi
}

check_html() {
  local url="$1"
  local label="$2"
  local needle="$3"
  local body
  body="$(curl -sS --connect-timeout 5 -H "Accept: text/html" "$url" 2>/dev/null || true)"
  local code
  code="$(curl -sS -o /dev/null -w "%{http_code}" -H "Accept: text/html" "$url" 2>/dev/null || echo "000")"
  if [[ "$code" != "200" ]]; then
    echo "FAIL $label (HTTP $code) $url" >&2
    fail=1
    return
  fi
  if [[ -n "$needle" && "$body" != *"$needle"* ]]; then
    echo "FAIL $label missing content '$needle' $url" >&2
    fail=1
    return
  fi
  echo "OK   $label ($code) $url"
}

echo "=== verify-ui-endpoints ==="

# Governance console (Next via proxy)
check_html "http://127.0.0.1:${PUBLIC}/cognitive-dashboard" "dashboard" "Cognitive dashboard"
check_html "http://127.0.0.1:${PUBLIC}/evaluate" "evaluate" "Submit operational intent"
check_html "http://127.0.0.1:${PUBLIC}/audit" "audit page" "Audit log"
check_html "http://127.0.0.1:${PUBLIC}/audit" "audit export CTA" "Export bundle (JSON)"
check_html "http://127.0.0.1:${PUBLIC}/trust-ledger/" "trust-ledger list" "Open workspace"
check_html "http://127.0.0.1:${PUBLIC}/trust-ledger/new" "tle generator" "TLE Generator"
check_html "http://127.0.0.1:${PUBLIC}/workspace" "workspace list" "Trust Ledger Workspace"
check_html "http://127.0.0.1:${PUBLIC}/workspace/connectors" "workspace connectors" "M365 evidence connectors"

# Static www + docs (regression: /docs/api must not hit platform OpenAPI)
check "http://127.0.0.1:${PUBLIC}/docs/api/" "docs/api index" "200"
check "http://127.0.0.1:${PUBLIC}/docs/diligence/CONNECTORS_CONTROLS_v1.md" "diligence md" "200"
check "http://127.0.0.1:${PUBLIC}/docs/spec/examples/tle-v1-go.yaml" "tle example yaml" "200"
check "http://127.0.0.1:${PUBLIC}/trust-ledger/" "www trust-ledger" "200"

# Platform swagger still reachable
check "http://127.0.0.1:${PUBLIC}/docs" "platform openapi docs" "200"

# Evaluate → result flow (gov API via proxy)
eval_json="$(curl -sS --connect-timeout 5 -X POST "http://127.0.0.1:${PUBLIC}/evaluate" \
  -H "Content-Type: application/json" \
  -d '{"actor":"ui-verify","action":"smoke","context":"ui endpoint verify","metadata":{}}' 2>/dev/null || echo '{}')"
rid="$(python3 -c "import json,sys; print(json.loads(sys.argv[1]).get('rid',''))" "$eval_json" 2>/dev/null || true)"
if [[ -z "$rid" ]]; then
  echo "FAIL evaluate flow (no rid)" >&2
  fail=1
else
  check_html "http://127.0.0.1:${PUBLIC}/result/${rid}" "result page" "Governance decision"
  echo "OK   evaluate flow rid=${rid}"
fi

# Trust ledger API (platform) + gov workspace API (proxy → 18002)
tle_code="$(curl -sS -o /dev/null -w "%{http_code}" "http://127.0.0.1:${PUBLIC}/api/v1/tle?limit=5" 2>/dev/null || echo "000")"
if [[ "$tle_code" == "200" ]]; then
  echo "OK   trust-ledger API ($tle_code)"
else
  echo "FAIL trust-ledger API ($tle_code)" >&2
  fail=1
fi

gov_tle_code="$(curl -sS -o /dev/null -w "%{http_code}" "http://127.0.0.1:${PUBLIC}/tle?limit=5" 2>/dev/null || echo "000")"
if [[ "$gov_tle_code" == "200" ]]; then
  echo "OK   gov TLE list API ($gov_tle_code)"
else
  echo "FAIL gov TLE list API ($gov_tle_code)" >&2
  fail=1
fi

conn_code="$(curl -sS -o /dev/null -w "%{http_code}" "http://127.0.0.1:${PUBLIC}/connectors" 2>/dev/null || echo "000")"
if [[ "$conn_code" == "200" ]]; then
  echo "OK   gov connectors API ($conn_code)"
else
  echo "FAIL gov connectors API ($conn_code)" >&2
  fail=1
fi

if [[ "$fail" -eq 0 ]]; then
  echo ""
  echo "All UI endpoint checks passed."
  exit 0
fi
echo ""
echo "Fix proxy/UI then re-run: ./scripts/verify-ui-endpoints.sh" >&2
exit 1
