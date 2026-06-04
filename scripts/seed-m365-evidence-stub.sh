#!/usr/bin/env bash
# POST M365-shaped metadata-only evidence into Evidence Index (local dev)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=dev-ports.sh
source "${ROOT}/scripts/dev-ports.sh"

BASE="http://127.0.0.1:${NF_DEV_PUBLIC_PORT}"
TENANT="X-Tenant-ID: copilot-pilot-01"

ingest() {
  local body="$1"
  local code
  code="$(curl -sS -o /tmp/nf-m365-ingest.json -w "%{http_code}" \
    -X POST "${BASE}/evidence/ingest" \
    -H "Content-Type: application/json" \
    -H "${TENANT}" \
    -d "${body}" 2>/dev/null || echo "000")"
  if [[ "$code" != "201" && "$code" != "409" ]]; then
    echo "FAIL ingest ($code): ${body}" >&2
    return 1
  fi
  echo "OK   ingest ($code)"
}

echo "=== seed-m365-evidence-stub ==="

ingest '{"evidence_id":"EV-PURVIEW-COPILOT-LABELS","source":"Purview","title":"Copilot sensitivity label coverage (M365 stub)","content_hash":"sha256:m365-purview-stub-001","sensitivity":"confidential","storage_ref":"m365-stub/purview/metadata","ingest_mode":"metadata_only"}'

ingest '{"evidence_id":"EV-ENTRA-CA-COPILOT","source":"EntraID","title":"Conditional Access — Copilot licensed users (M365 stub)","content_hash":"sha256:m365-entra-stub-002","sensitivity":"internal","storage_ref":"m365-stub/entra/metadata","ingest_mode":"metadata_only"}'

ingest '{"evidence_id":"EV-SPO-SITE-POLICY","source":"SharePoint","title":"SharePoint site policy export — Copilot-eligible sites (M365 stub)","content_hash":"sha256:m365-spo-stub-003","sensitivity":"internal","storage_ref":"m365-stub/sharepoint/metadata","ingest_mode":"metadata_only"}'

echo "Done. Use evidence_ids in POST /tle/draft."
