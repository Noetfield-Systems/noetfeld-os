#!/usr/bin/env bash
# Live www sandbox gate — /workspace must serve real governance-console UI when proxy enabled.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

BASE="${NOETFIELD_E2E_BASE:-https://www.noetfield.com}"
PROXY_CFG="${ROOT}/data/nf-www-gov-proxy-v1.json"
fail=0

echo "=== verify-www-live-sandbox ==="

if [[ -f "$PROXY_CFG" ]]; then
  enabled="$(python3 -c "import json; print(json.load(open('$PROXY_CFG')).get('enabled', False))")"
else
  enabled="False"
fi

if [[ "$enabled" != "True" ]]; then
  echo "SKIP proxy disabled — set data/nf-www-gov-proxy-v1.json enabled=true after deploy-gov-sandbox-railway"
  exit 0
fi

html="$(curl -sSL --connect-timeout 15 -H "Accept: text/html" "${BASE}/workspace/" 2>/dev/null || true)"
if grep -qF "_next" <<< "$html"; then
  echo "OK   ${BASE}/workspace/ serves Next.js app shell (_next)"
else
  echo "FAIL ${BASE}/workspace/ missing Next.js _next assets" >&2
  fail=1
fi
for needle in "Trust Ledger Workspace" "Create TLE draft"; do
  if grep -qF "$needle" <<< "$html"; then
    echo "OK   ${BASE}/workspace/ has: ${needle}"
  else
    echo "NOTE ${BASE}/workspace/ SSR may omit: ${needle} (client-rendered)"
  fi
done

if grep -qF 'nf-workspace-mock' <<< "$html"; then
  echo "FAIL ${BASE}/workspace/ still serves static mock" >&2
  fail=1
else
  echo "OK   workspace is not static mock"
fi

api_code="$(curl -sS -o /dev/null -w "%{http_code}" --connect-timeout 10 -H "Accept: application/json" "${BASE}/tle" 2>/dev/null || echo 000)"
if [[ "$api_code" =~ ^2 ]]; then
  echo "OK   ${BASE}/tle returns ${api_code}"
else
  echo "FAIL ${BASE}/tle returns ${api_code} (expected 2xx)" >&2
  fail=1
fi

if [[ "$fail" -eq 0 ]]; then
  echo ""
  echo "verify-www-live-sandbox passed."
  exit 0
fi
echo ""
echo "verify-www-live-sandbox failed." >&2
exit 1
