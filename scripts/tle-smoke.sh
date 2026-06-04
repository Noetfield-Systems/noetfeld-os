#!/usr/bin/env bash
# TLE v1 smoke: YAML examples + optional live API (draft → approve).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=dev-ports.sh
source "${ROOT}/scripts/dev-ports.sh"
SCHEMA="$ROOT/docs/spec/schemas/tle-v1.schema.yaml"
EXAMPLES="$ROOT/docs/spec/examples"
fail() { echo "tle-smoke: $*" >&2; exit 1; }

API_BASE=""
for arg in "$@"; do
  case "$arg" in
    --api=*) API_BASE="${arg#--api=}" ;;
    --api) API_BASE="${TLE_SMOKE_API_BASE:-http://127.0.0.1:${NF_DEV_PLATFORM_PORT}/api/v1}" ;;
  esac
done
if [[ "${1:-}" == "--api" && -z "$API_BASE" ]]; then
  API_BASE="${TLE_SMOKE_API_BASE:-http://127.0.0.1:${NF_DEV_PLATFORM_PORT}/api/v1}"
fi

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
print(f"tle-smoke: OK ({len(sys.argv) - 2} example(s))")
PY
else
  for f in "${yaml_files[@]}"; do [[ -s "$f" ]] || fail "empty $f"; done
  echo "tle-smoke: OK (${#yaml_files[@]} example(s), python3 unavailable — size check only)"
fi

if [[ -n "$API_BASE" ]]; then
  EV_ID="ev-smoke-$(date +%s)"
  code="$(curl -sS -o /tmp/tle-smoke-ingest.json -w "%{http_code}" \
    -X POST "${API_BASE}/evidence/ingest" \
    -H "Content-Type: application/json" \
    -d "{\"evidence_id\":\"${EV_ID}\",\"source\":\"Smoke\",\"title\":\"TLE smoke evidence\",\"hash\":\"sha256:smoke0000000000000000000000000000000000000000000000000000000001\",\"ingest_mode\":\"metadata_only\"}" \
    2>/dev/null || echo "000")"
  [[ "$code" == "201" ]] || fail "API ingest failed ($code) at ${API_BASE}/evidence/ingest"

  draft_code="$(curl -sS -o /tmp/tle-smoke-draft.json -w "%{http_code}" \
    -X POST "${API_BASE}/tle/draft" \
    -H "Content-Type: application/json" \
    -d "{\"template_id\":\"copilot-go-no-go-v1\",\"evidence_ids\":[\"${EV_ID}\"],\"owner_id\":\"usr-smoke\",\"decision\":\"Smoke test\"}" \
    2>/dev/null || echo "000")"
  [[ "$draft_code" == "201" ]] || fail "API draft failed ($draft_code)"

  tle_id="$(python3 -c "import json; print(json.load(open('/tmp/tle-smoke-draft.json'))['tle_id'])")"
  appr_code="$(curl -sS -o /tmp/tle-smoke-approve.json -w "%{http_code}" \
    -X POST "${API_BASE}/tle/${tle_id}/approve" \
    -H "Content-Type: application/json" \
    -d '{"approver_id":"usr-smoke","status":"Approved","signature_hash":"sig:smoke0000000000000000000000000000000000000000000000000000000001","key_id":"kms-smoke-01"}' \
    2>/dev/null || echo "000")"
  [[ "$appr_code" == "200" ]] || fail "API approve failed ($appr_code)"
  echo "tle-smoke: API OK (${API_BASE}) tle_id=${tle_id}"
fi
