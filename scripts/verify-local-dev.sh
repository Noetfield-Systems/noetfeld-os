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
  if grep -q '"tenant_id"' /tmp/nf-dash-eval.json 2>/dev/null; then
    echo "OK   evaluate response includes tenant_id"
  else
    echo "FAIL evaluate missing tenant_id" >&2
    fail=1
  fi
else
  echo "FAIL dashboard API via proxy ($dash_eval) — POST /evaluate must hit gov API, not Next HTML" >&2
  fail=1
fi

export_code="$(curl -sS -o /tmp/nf-audit-export.json -w "%{http_code}" --connect-timeout 5 \
  "http://127.0.0.1:${PUBLIC}/audit/export" \
  -H "X-Tenant-ID: copilot-pilot-01" \
  2>/dev/null || echo "000")"
if [[ "$export_code" == "200" ]] && grep -q '"event_count"' /tmp/nf-audit-export.json 2>/dev/null; then
  echo "OK   audit export (200 JSON)"
else
  echo "FAIL audit export ($export_code)" >&2
  fail=1
fi

# dashboard UI assets (production build serves stable /_next/static)
html="$(curl -sS --connect-timeout 5 "http://127.0.0.1:${PUBLIC}/cognitive-dashboard" 2>/dev/null || true)"
chunk="$(echo "$html" | grep -oE '/_next/static/[^"[:space:]]+\.js' | head -1)"
if [[ -n "$chunk" ]]; then
  chunk_code="$(curl -sS -o /dev/null -w "%{http_code}" --connect-timeout 5 "http://127.0.0.1:${PUBLIC}${chunk}" 2>/dev/null || echo "000")"
  if [[ "$chunk_code" == "200" ]]; then
    echo "OK   dashboard UI chunk (200) ${chunk}"
  else
    echo "FAIL dashboard UI chunk ($chunk_code) ${chunk} — run: NF_DEV_FORCE_DASHBOARD_BUILD=1 make dev-local" >&2
    fail=1
  fi
else
  echo "WARN dashboard UI chunk not found in HTML" >&2
fi

tle_code="$(curl -sS -o /tmp/nf-tle-list.json -w "%{http_code}" --connect-timeout 5 \
  "http://127.0.0.1:${PUBLIC}/tle" \
  -H "X-Tenant-ID: copilot-pilot-01" \
  2>/dev/null || echo "000")"
if [[ "$tle_code" == "200" ]]; then
  echo "OK   TLE list API (200)"
else
  echo "FAIL TLE list API ($tle_code)" >&2
  fail=1
fi

ws_code="$(curl -sS -o /dev/null -w "%{http_code}" --connect-timeout 5 \
  "http://127.0.0.1:${PUBLIC}/workspace" 2>/dev/null || echo "000")"
if [[ "$ws_code" == "200" ]]; then
  echo "OK   Trust Ledger workspace (200)"
else
  echo "FAIL Trust Ledger workspace ($ws_code) — rebuild dashboard" >&2
  fail=1
fi

check "http://127.0.0.1:${PUBLIC}/trust-ledger/sample-report/" "TLE sample report"
pilot_code="$(curl -sS -o /dev/null -w "%{http_code}" --connect-timeout 5 \
  "http://127.0.0.1:${PUBLIC}/copilot/pilot/" 2>/dev/null || echo "000")"
if [[ "$pilot_code" == "200" ]]; then
  echo "OK   Copilot pilot page (200)"
else
  echo "FAIL Copilot pilot page ($pilot_code)" >&2
  fail=1
fi
conn_html="$(curl -sS --connect-timeout 5 "http://127.0.0.1:${PUBLIC}/workspace/connectors" 2>/dev/null || true)"
if echo "$conn_html" | grep -qF "M365 evidence connectors"; then
  echo "OK   Workspace connectors (content)"
elif echo "$conn_html" | grep -qF 'tle_id","connectors"'; then
  echo "FAIL Workspace connectors — stale Next build routes /connectors as TLE id" >&2
  echo "     Run: NF_DEV_FORCE_DASHBOARD_BUILD=1 make dev-local" >&2
  fail=1
else
  conn_code="$(curl -sS -o /dev/null -w "%{http_code}" --connect-timeout 5 \
    "http://127.0.0.1:${PUBLIC}/workspace/connectors" 2>/dev/null || echo "000")"
  echo "FAIL Workspace connectors ($conn_code) — missing page content" >&2
  fail=1
fi
sample_yaml="$(curl -sS -o /dev/null -w "%{http_code}" --connect-timeout 3 \
  "http://127.0.0.1:${PUBLIC}/trust-ledger/sample-report/samples/tle-go-approved.yaml" 2>/dev/null || echo "000")"
if [[ "$sample_yaml" == "200" ]]; then
  echo "OK   TLE sample YAML download (200)"
else
  echo "FAIL TLE sample YAML ($sample_yaml)" >&2
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
