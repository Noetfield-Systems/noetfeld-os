#!/usr/bin/env bash
# TLE v1 smoke: YAML examples + optional live API (draft → approve) + perf budgets.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=dev-ports.sh
source "${ROOT}/scripts/dev-ports.sh"
SCHEMA="$ROOT/docs/spec/schemas/tle-v1.schema.yaml"
EXAMPLES="$ROOT/docs/spec/examples"
fail() { echo "tle-smoke: $*" >&2; exit 1; }

API_BASE=""
CONNECTORS_SYNC=0
PERF=0
PERF_TOTAL_MS=0
TLE_SMOKE_MAX_MS_PER_STEP="${TLE_SMOKE_MAX_MS_PER_STEP:-5000}"
TLE_SMOKE_MAX_TOTAL_MS="${TLE_SMOKE_MAX_TOTAL_MS:-20000}"

for arg in "$@"; do
  case "$arg" in
    --api=*) API_BASE="${arg#--api=}" ;;
    --api) API_BASE="${TLE_SMOKE_API_BASE:-http://127.0.0.1:${NF_DEV_PLATFORM_PORT}/api/v1}" ;;
    --connectors-sync) CONNECTORS_SYNC=1 ;;
    --perf) PERF=1 ;;
  esac
done
if [[ "${1:-}" == "--api" && -z "$API_BASE" ]]; then
  API_BASE="${TLE_SMOKE_API_BASE:-http://127.0.0.1:${NF_DEV_PLATFORM_PORT}/api/v1}"
fi

record_perf() {
  local label="$1"
  local seconds="$2"
  [[ "$PERF" -eq 1 ]] || return 0
  local ms
  ms="$(python3 -c "print(int(float('${seconds}') * 1000))")"
  PERF_TOTAL_MS=$((PERF_TOTAL_MS + ms))
  echo "tle-smoke: perf ${label} ${ms}ms" >&2
  if [[ "$ms" -gt "$TLE_SMOKE_MAX_MS_PER_STEP" ]]; then
    fail "${label} exceeded budget ${ms}ms > ${TLE_SMOKE_MAX_MS_PER_STEP}ms"
  fi
}

CURL_TIMED_LAST_CODE="000"

curl_timed() {
  local label="$1"
  local out="$2"
  shift 2
  local meta
  meta="$(curl -sS -o "$out" -w "%{http_code} %{time_total}" "$@" 2>/dev/null || echo "000 99")"
  local code seconds
  code="${meta%% *}"
  seconds="${meta#* }"
  record_perf "$label" "$seconds"
  CURL_TIMED_LAST_CODE="$code"
}

[[ -f "$SCHEMA" ]] || fail "missing $SCHEMA"
shopt -s nullglob
yaml_files=("$EXAMPLES"/tle-v1-*.yaml)
[[ ${#yaml_files[@]} -gt 0 ]] || fail "no tle-v1-*.yaml under $EXAMPLES"

if command -v python3 >/dev/null 2>&1; then
  python3 - "$SCHEMA" "${yaml_files[@]}" <<'PY'
import sys
from pathlib import Path
try:
    import yaml
except ImportError:
    print("tle-smoke: PyYAML not installed — checking files exist only")
    for p in sys.argv[2:]:
        Path(p).read_text(encoding="utf-8")
    sys.exit(0)
schema_path = Path(sys.argv[1])
schema_path.read_text(encoding="utf-8")
for p in sys.argv[2:]:
    data = yaml.safe_load(Path(p).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit(f"not a mapping: {p}")
    for key in ("tle_id", "status"):
        if key not in data:
            raise SystemExit(f"missing {key} in {p}")
    if "drift_class" in data:
        print(f"  drift_class={data.get('drift_class')} (optional field OK)")
print(f"tle-smoke: OK ({len(sys.argv) - 2} example(s))")
PY
else
  for f in "${yaml_files[@]}"; do [[ -s "$f" ]] || fail "empty $f"; done
  echo "tle-smoke: OK (${#yaml_files[@]} example(s), python3 unavailable — size check only)"
fi

if [[ -n "$API_BASE" ]]; then
  EV_ID="ev-smoke-$(date +%s)"
  curl_timed "evidence/ingest" /tmp/tle-smoke-ingest.json \
    -X POST "${API_BASE}/evidence/ingest" \
    -H "Content-Type: application/json" \
    -d "{\"evidence_id\":\"${EV_ID}\",\"source\":\"Purview\",\"title\":\"TLE smoke evidence\",\"hash\":\"sha256:smoke0000000000000000000000000000000000000000000000000000000001\",\"ingest_mode\":\"metadata_only\"}"
  code="$CURL_TIMED_LAST_CODE"
  [[ "$code" == "201" ]] || fail "API ingest failed ($code) at ${API_BASE}/evidence/ingest"

  curl_timed "tle/draft" /tmp/tle-smoke-draft.json \
    -X POST "${API_BASE}/tle/draft" \
    -H "Content-Type: application/json" \
    -d "{\"template_id\":\"copilot-go-no-go-v1\",\"evidence_ids\":[\"${EV_ID}\"],\"owner_id\":\"usr-smoke\",\"decision\":\"Smoke test\"}"
  draft_code="$CURL_TIMED_LAST_CODE"
  [[ "$draft_code" == "201" ]] || fail "API draft failed ($draft_code)"

  python3 -c "import json; d=json.load(open('/tmp/tle-smoke-draft.json')); assert 'confidence_score' in d, 'missing confidence_score'; assert 0 <= d['confidence_score'] <= 1"
  tle_id="$(python3 -c "import json; print(json.load(open('/tmp/tle-smoke-draft.json'))['tle_id'])")"

  for approver in usr-smoke-1 usr-smoke-2; do
    curl_timed "tle/approve/${approver}" /tmp/tle-smoke-approve.json \
      -X POST "${API_BASE}/tle/${tle_id}/approve" \
      -H "Content-Type: application/json" \
      -d "{\"approver_id\":\"${approver}\",\"status\":\"Approved\",\"signature_hash\":\"sig:smoke0000000000000000000000000000000000000000000000000000000001\",\"key_id\":\"kms-smoke-01\"}"
    appr_code="$CURL_TIMED_LAST_CODE"
    [[ "$appr_code" == "200" ]] || fail "API approve failed ($appr_code) for ${approver}"
  done

  curl_timed "tle/export" /tmp/tle-smoke-export.pdf \
    "${API_BASE}/tle/${tle_id}/export"
  exp_code="$CURL_TIMED_LAST_CODE"
  [[ "$exp_code" == "200" ]] || fail "API export failed ($exp_code)"
  head -c 4 /tmp/tle-smoke-export.pdf | grep -q '%PDF' || fail "export is not PDF"

  curl_timed "tle/list" /tmp/tle-smoke-list.json \
    "${API_BASE}/tle?limit=5"
  list_code="$CURL_TIMED_LAST_CODE"
  [[ "$list_code" == "200" ]] || fail "API list failed ($list_code)"

  curl_timed "connectors/register" /tmp/tle-smoke-conn.json \
    -X POST "${API_BASE}/connectors" \
    -H "Content-Type: application/json" \
    -d '{"connector_id":"smoke-purview","type":"Purview","required_scopes":["Audit.Read"],"ingest_mode":"metadata_only"}'
  conn_code="$CURL_TIMED_LAST_CODE"
  [[ "$conn_code" == "201" ]] || fail "API connector register failed ($conn_code)"

  if [[ "$CONNECTORS_SYNC" -eq 1 ]]; then
    curl_timed "connectors/sync" /tmp/tle-smoke-sync.json \
      -X POST "${API_BASE}/connectors/smoke-purview/sync" \
      -H "Content-Type: application/json" \
      -d '{"status":"active","records_synced":1}'
    sync_code="$CURL_TIMED_LAST_CODE"
    [[ "$sync_code" == "200" ]] || fail "API connector sync failed ($sync_code)"
    python3 -c "import json; d=json.load(open('/tmp/tle-smoke-sync.json')); assert d.get('status')=='active' and d.get('last_sync')"
    echo "tle-smoke: connector sync OK"
  fi

  if [[ "$PERF" -eq 1 ]]; then
    echo "tle-smoke: perf total ${PERF_TOTAL_MS}ms (budget ${TLE_SMOKE_MAX_TOTAL_MS}ms)" >&2
    if [[ "$PERF_TOTAL_MS" -gt "$TLE_SMOKE_MAX_TOTAL_MS" ]]; then
      fail "total flow exceeded budget ${PERF_TOTAL_MS}ms > ${TLE_SMOKE_MAX_TOTAL_MS}ms"
    fi
  fi
  echo "tle-smoke: API OK (${API_BASE}) tle_id=${tle_id}"
fi
