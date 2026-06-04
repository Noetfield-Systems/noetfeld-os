#!/usr/bin/env bash
# E2E: signal → evaluate → RID → audit export (governance-console API via :13080)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=dev-ports.sh
source "${ROOT}/scripts/dev-ports.sh"

BASE="http://127.0.0.1:${NF_DEV_PUBLIC_PORT}"
TENANT_HEADER="X-Tenant-ID: copilot-pilot-01"

echo "=== copilot-quickscan-e2e ==="

eval_json="$(curl -sS -X POST "${BASE}/evaluate" \
  -H "Content-Type: application/json" \
  -H "${TENANT_HEADER}" \
  -d '{"actor":"e2e-pilot","action":"copilot_quickscan","context":"M365 copilot oversharing check","metadata":{"pii_exposure":false}}')"

echo "$eval_json" | grep -q '"rid"'
echo "$eval_json" | grep -q '"tenant_id"'
RID="$(echo "$eval_json" | python3 -c "import sys,json; print(json.load(sys.stdin)['rid'])")"
echo "OK  evaluate rid=${RID}"

curl -sS "${BASE}/audit/${RID}" -H "${TENANT_HEADER}" | grep -q '"integrity_hash"'
echo "OK  audit by rid"

export_json="$(curl -sS "${BASE}/audit/export" -H "${TENANT_HEADER}")"
echo "$export_json" | grep -q '"event_count"'
echo "OK  audit export"
echo "E2E complete."
