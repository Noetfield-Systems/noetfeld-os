#!/usr/bin/env bash
# POST M365-shaped metadata-only evidence into Evidence Index (local dev)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=dev-ports.sh
source "${ROOT}/scripts/dev-ports.sh"

BASE="http://127.0.0.1:${NF_DEV_PUBLIC_PORT}"
TENANT="X-Tenant-ID: copilot-pilot-01"

hash_for() {
  python3 -c "import sys; sys.path.insert(0, '${ROOT}/governance-console/backend'); from services.evidence_hash import content_hash_for_metadata; print(content_hash_for_metadata(evidence_id=sys.argv[1], source=sys.argv[2], title=sys.argv[3], storage_ref=sys.argv[4]))" "$@"
}

ingest() {
  local eid="$1"
  local body="$2"
  local code
  code="$(curl -sS -o /tmp/nf-m365-ingest.json -w "%{http_code}" \
    -X POST "${BASE}/evidence/ingest" \
    -H "Content-Type: application/json" \
    -H "${TENANT}" \
    -d "${body}" 2>/dev/null || echo "000")"
  case "$code" in
    201) echo "OK   created ${eid}" ;;
    409) echo "OK   already present ${eid}" ;;
    *)
      echo "FAIL ingest ${eid} (${code})" >&2
      if [[ -f /tmp/nf-m365-ingest.json ]]; then
        head -c 200 /tmp/nf-m365-ingest.json >&2 || true
        echo "" >&2
      fi
      return 1
      ;;
  esac
}

echo "=== seed-m365-evidence-stub ==="

health_code="$(curl -sS -o /dev/null -w "%{http_code}" --connect-timeout 3 "${BASE}/health" 2>/dev/null || echo "000")"
if [[ "$health_code" != "200" ]]; then
  echo "FAIL: dev stack not up (health ${health_code}). Run: make dev-local" >&2
  exit 1
fi

H1="$(hash_for EV-PURVIEW-COPILOT-LABELS Purview "Copilot sensitivity label coverage (M365 stub)" m365-stub/purview/metadata)"
H2="$(hash_for EV-ENTRA-CA-COPILOT EntraID "Conditional Access — Copilot licensed users (M365 stub)" m365-stub/entra/metadata)"
H3="$(hash_for EV-SPO-SITE-POLICY SharePoint "SharePoint site policy export — Copilot-eligible sites (M365 stub)" m365-stub/sharepoint/metadata)"

ingest "EV-PURVIEW-COPILOT-LABELS" "{\"evidence_id\":\"EV-PURVIEW-COPILOT-LABELS\",\"source\":\"Purview\",\"title\":\"Copilot sensitivity label coverage (M365 stub)\",\"content_hash\":\"${H1}\",\"sensitivity\":\"confidential\",\"storage_ref\":\"m365-stub/purview/metadata\",\"ingest_mode\":\"metadata_only\"}"

ingest "EV-ENTRA-CA-COPILOT" "{\"evidence_id\":\"EV-ENTRA-CA-COPILOT\",\"source\":\"EntraID\",\"title\":\"Conditional Access — Copilot licensed users (M365 stub)\",\"content_hash\":\"${H2}\",\"sensitivity\":\"internal\",\"storage_ref\":\"m365-stub/entra/metadata\",\"ingest_mode\":\"metadata_only\"}"

ingest "EV-SPO-SITE-POLICY" "{\"evidence_id\":\"EV-SPO-SITE-POLICY\",\"source\":\"SharePoint\",\"title\":\"SharePoint site policy export — Copilot-eligible sites (M365 stub)\",\"content_hash\":\"${H3}\",\"sensitivity\":\"internal\",\"storage_ref\":\"m365-stub/sharepoint/metadata\",\"ingest_mode\":\"metadata_only\"}"

echo "seed-m365-evidence-stub passed (3/3)"
echo "Use evidence_ids in POST /tle/draft."
