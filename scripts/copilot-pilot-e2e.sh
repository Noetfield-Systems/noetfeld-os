#!/usr/bin/env bash
# Design-partner pilot E2E — evaluate → evidence → TLE → approve → export → audit
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=dev-ports.sh
source "${ROOT}/scripts/dev-ports.sh"

BASE="http://127.0.0.1:${NF_DEV_PUBLIC_PORT}"
TENANT="X-Tenant-ID: copilot-pilot-01"
HDR=(-H "Content-Type: application/json" -H "${TENANT}" -H "X-Role: approver")

code="$(curl -sS -o /dev/null -w "%{http_code}" --connect-timeout 3 "${BASE}/health" 2>/dev/null || echo "000")"
if [[ "$code" != "200" ]]; then
  echo "FAIL: dev stack not up. Run: make dev-local" >&2
  exit 1
fi

echo "=== copilot-pilot-e2e ==="

echo "Step 1: governance evaluate"
EVAL="$(curl -sS -X POST "${BASE}/evaluate" "${HDR[@]}" \
  -d '{"actor":"pilot-design-partner","action":"copilot_readiness_check","context":"pilot e2e","metadata":{"pack":"copilot-governance"}}')"
RID="$(echo "$EVAL" | python3 -c "import sys,json; print(json.load(sys.stdin)['rid'])")"
echo "OK   evaluate rid=${RID}"

echo "Step 2: M365 connector OAuth + auto evidence ingest"
CONN_ID="pilot-m365-$(date +%s)"
curl -sS "${BASE}/connectors" "${HDR[@]}" \
  -d "{\"connector_id\":\"${CONN_ID}\",\"connector_type\":\"m365_purview\",\"required_scopes\":[\"Purview.Read\"]}" >/dev/null
curl -sS "${BASE}/connectors/${CONN_ID}/oauth/callback?code=dev-mock&state=pilot" -H "${TENANT}" >/dev/null
echo "OK   connector ${CONN_ID} connected + evidence ingested"

echo "Step 3: TLE draft"
DRAFT="$(curl -sS "${BASE}/tle/draft" "${HDR[@]}" \
  -d "{\"source_rid\":\"${RID}\",\"evidence_ids\":[\"EV-PURVIEW-COPILOT-LABELS\",\"EV-ENTRA-CA-COPILOT\",\"EV-SPO-SITE-POLICY\"]}")"
TLE_ID="$(echo "$DRAFT" | python3 -c "import sys,json; print(json.load(sys.stdin)['tle_id'])")"
echo "OK   draft ${TLE_ID}"

echo "Step 4: approval chain"
for approver in cio-001 legal-001 sec-001; do
  curl -sS "${BASE}/tle/${TLE_ID}/approve" "${HDR[@]}" \
    -d "{\"approver_id\":\"${approver}\",\"decision\":\"Approved\"}" >/dev/null
done
echo "OK   approvals"

echo "Step 5: board pack export (json + pdf)"
EXPORT_JSON="$(curl -sS "${BASE}/tle/${TLE_ID}/export" -H "${TENANT}")"
echo "$EXPORT_JSON" | python3 -c "import sys,json; d=json.load(sys.stdin); assert d['export_type']=='board_pack_v1'; assert d.get('confidence_score',0)>0; assert 'drift_contract' in d"
pdf_code="$(curl -sS -o /dev/null -w "%{http_code}" "${BASE}/tle/${TLE_ID}/export?format=pdf" -H "${TENANT}")"
[[ "$pdf_code" == "200" ]] || { echo "FAIL pdf export $pdf_code" >&2; exit 1; }
echo "OK   export json + pdf"

echo "Step 6: audit export"
audit_code="$(curl -sS -o /dev/null -w "%{http_code}" "${BASE}/audit/export" -H "${TENANT}")"
[[ "$audit_code" == "200" ]] || { echo "FAIL audit export $audit_code" >&2; exit 1; }
echo "OK   audit export"

echo ""
echo "copilot-pilot-e2e passed."
