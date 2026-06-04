#!/usr/bin/env bash
# E2E: TLE draft → approve (3 signers) → export via unified dev proxy
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=dev-ports.sh
source "${ROOT}/scripts/dev-ports.sh"

BASE="http://127.0.0.1:${NF_DEV_PUBLIC_PORT}"
TENANT="X-Tenant-ID: copilot-pilot-01"
HDR=(-H "Content-Type: application/json" -H "${TENANT}")

code="$(curl -sS -o /dev/null -w "%{http_code}" --connect-timeout 3 "${BASE}/health" 2>/dev/null || echo "000")"
if [[ "$code" != "200" ]]; then
  echo "FAIL: dev stack not up (${BASE}/health → ${code}). Run: make dev-local" >&2
  exit 1
fi

echo "=== tle-smoke ==="

# Ensure pilot evidence exists (seed on API boot; optional extra M365 stub)
for eid in EV-PURVIEW-001 EV-ENTRA-001 EV-AUDIT-001; do
  curl -sS -o /dev/null -w "" "${BASE}/evidence/ingest" "${HDR[@]}" \
    -d "{\"evidence_id\":\"${eid}\",\"source\":\"Manual\",\"title\":\"smoke\",\"content_hash\":\"sha256:smoke\"}" \
    2>/dev/null || true
done

DRAFT="$(curl -sS "${BASE}/tle/draft" "${HDR[@]}" \
  -d '{"evidence_ids":["EV-PURVIEW-001","EV-ENTRA-001","EV-AUDIT-001"]}')"
TLE_ID="$(echo "$DRAFT" | python3 -c "import sys,json; print(json.load(sys.stdin)['tle_id'])")"
echo "OK   draft ${TLE_ID}"

for approver in cio-001 legal-001 sec-001; do
  curl -sS "${BASE}/tle/${TLE_ID}/approve" "${HDR[@]}" \
    -d "{\"approver_id\":\"${approver}\",\"decision\":\"Approved\"}" >/dev/null
done
echo "OK   approvals"

DETAIL="$(curl -sS "${BASE}/tle/${TLE_ID}" -H "${TENANT}")"
echo "$DETAIL" | python3 -c "import sys,json; d=json.load(sys.stdin); assert d.get('audit_digest','').startswith('sha256:'), d"
echo "OK   audit_digest present"

EXPORT="$(curl -sS "${BASE}/tle/${TLE_ID}/export" -H "${TENANT}")"
echo "$EXPORT" | python3 -c "import sys,json; d=json.load(sys.stdin); assert d.get('export_type')=='board_pack_v1', d"
echo "OK   board pack export"

echo ""
echo "tle-smoke passed."
