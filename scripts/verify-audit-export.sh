#!/usr/bin/env bash
# Audit export diligence bundle — GET /audit/export returns JSON with events.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=dev-ports.sh
source "${ROOT}/scripts/dev-ports.sh"

BASE="http://127.0.0.1:${NF_DEV_PUBLIC_PORT}"
TENANT="X-Tenant-ID: copilot-pilot-01"
fail=0

echo "=== verify-audit-export ==="

code="$(curl -sS -o /dev/null -w "%{http_code}" --connect-timeout 5 "${BASE}/audit/export" -H "${TENANT}" 2>/dev/null || echo "000")"
if [[ "$code" != "200" ]]; then
  echo "FAIL audit export HTTP ${code}" >&2
  exit 1
fi

body="$(curl -sS --connect-timeout 5 "${BASE}/audit/export" -H "${TENANT}" 2>/dev/null || echo '{}')"
if python3 -c "
import json, sys
b = json.loads(sys.argv[1])
assert b.get('tenant_id'), 'missing tenant_id'
assert isinstance(b.get('events'), list), 'missing events list'
assert b.get('event_count', 0) >= 0, 'invalid event_count'
assert b['event_count'] == len(b['events']), 'event_count mismatch'
if b['events']:
    e = b['events'][0]
    assert e.get('rid', '').startswith('RID-'), 'invalid rid'
    assert e.get('integrity_hash'), 'missing integrity_hash'
print('OK')
" "$body" 2>/dev/null; then
  count="$(python3 -c "import json,sys; print(json.loads(sys.argv[1])['event_count'])" "$body")"
  echo "OK   audit export bundle (${count} events)"
else
  echo "FAIL audit export JSON schema" >&2
  fail=1
fi

if [[ "$fail" -eq 0 ]]; then
  echo ""
  echo "verify-audit-export passed."
  exit 0
fi
exit 1
