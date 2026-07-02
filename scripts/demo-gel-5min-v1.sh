#!/usr/bin/env bash
# demo-gel-5min-v1.sh — W1 GEL proof chain (UPG-0021–0025)
# gate → decide APPROVE → decide DECLINE → TLE export → tamper FAIL → replay
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
DEMO_DIR="${NOETFIELD_DEMO_DIR:-$ROOT/.demo-gel-run}"
mkdir -p "$DEMO_DIR"

API_URL="${NOETFIELD_API_URL:-https://api.noetfield.com}"
START_TS=$(date +%s)

pause() { sleep "${1:-1}"; }

require_key() {
  if [[ -z "${NOETFIELD_API_KEY:-}" ]]; then
    echo "NOETFIELD_API_KEY required for decide/export beats." >&2
    echo "  export NOETFIELD_API_KEY=\$(python3 scripts/mint_api_key.py 2>&1 | awk '/X-API-Key:/ {print \$2}')" >&2
    exit 1
  fi
}

echo "=============================================="
echo " NOETFIELD GEL — 5-MIN DEMO (W1)"
echo " Policy before execution. Receipt after."
echo " API: $API_URL"
echo "=============================================="
echo ""

echo "[0:30] BEAT 1 — noetfield gate (local PASS/BLOCK before dispatch)"
pause 1
noetfield gate --out "$DEMO_DIR/gate-report-v1.json"
python3 -c "
import json, pathlib
r=json.loads(pathlib.Path('$DEMO_DIR/gate-report-v1.json').read_text())
print('  outcome:', r['outcome'])
print('  checks:', len(r.get('checks', [])))
"
pause 1
echo ""

require_key

echo "[1:15] BEAT 2 — noetfield decide --sample (APPROVE path + receipt)"
pause 1
APPROVE_RECEIPT="$DEMO_DIR/approve-receipt.json"
noetfield decide --sample --api-url "$API_URL" --out "$APPROVE_RECEIPT"
python3 -c "
import json, pathlib
r=json.loads(pathlib.Path('$APPROVE_RECEIPT').read_text())
print('  decision:', r.get('decision'))
print('  audit_id:', r.get('audit_id'))
print('  request_id:', r.get('request_id'))
"
pause 1
echo ""

echo "[2:00] BEAT 3 — noetfield decide --sample-block (DECLINE corridor)"
pause 1
DECLINE_RECEIPT="$DEMO_DIR/decline-receipt.json"
noetfield decide --sample-block --api-url "$API_URL" --out "$DECLINE_RECEIPT"
python3 -c "
import json, pathlib
r=json.loads(pathlib.Path('$DECLINE_RECEIPT').read_text())
print('  decision:', r.get('decision'))
breaches=(r.get('api_response') or {}).get('corridor_breaches') or []
print('  corridor_breaches:', breaches)
"
pause 1
echo ""

echo "[2:45] BEAT 4 — portal TLE export bundle"
pause 1
AUDIT_ID=$(python3 -c "import json; print(json.load(open('$APPROVE_RECEIPT'))['audit_id'])")
EXPORT_PATH="$DEMO_DIR/export-${AUDIT_ID}.json"
HTTP=$(curl -sS -o "$EXPORT_PATH" -w '%{http_code}' \
  -H "X-API-Key: ${NOETFIELD_API_KEY}" \
  "${API_URL}/portal/audits/${AUDIT_ID}/export")
if [[ "$HTTP" != "200" ]]; then
  echo "  portal export HTTP $HTTP — building bundle locally from receipt" >&2
  python3 - <<PY
import json, sys
from pathlib import Path
sys.path.insert(0, "$ROOT")
from export.tle_mapper import build_export_bundle
receipt = json.loads(Path("$APPROVE_RECEIPT").read_text())
api = receipt["api_response"]
hashes = api.get("policy_hashes") or {}
record = {
    "id": api["audit_id"],
    "request_id": api["request_id"],
    "tenant_id": api.get("tenant_id", "unknown"),
    "applicant_id": api.get("applicant_id"),
    "decision": api["decision"],
    "composite_score": api["composite_score"],
    "created_at": receipt.get("checked_at") or "2026-01-01T00:00:00Z",
    "input_payload": receipt.get("intent"),
    "corridor_breaches": api.get("corridor_breaches") or [],
    "rule_set_id": api.get("rule_set_id"),
    "rule_set_version": api.get("rule_set_version"),
    "policy_base_hash": hashes.get("base"),
    "policy_corridor_hash": hashes.get("corridor"),
    "policy_decision": api.get("policy_decision"),
    "corridor_decision": api.get("corridor_decision"),
    "score_breakdown": api.get("score_breakdown"),
}
Path("$EXPORT_PATH").write_text(json.dumps(build_export_bundle(record), indent=2) + "\\n")
PY
fi
python3 -c "
import json, pathlib
b=json.loads(pathlib.Path('$EXPORT_PATH').read_text())
print('  export_type:', b.get('export_type'))
print('  tle_id:', (b.get('tle_v1') or {}).get('tle_id'))
print('  audit_digest:', (b.get('tle_v1') or {}).get('audit_digest'))
"
pause 1
echo ""

echo "[3:30] BEAT 5 — tamper FAIL (mutated export digest)"
pause 1
python3 scripts/verify-tle-digest-v1.py "$EXPORT_PATH"
python3 scripts/verify-tle-digest-v1.py "$EXPORT_PATH" --mutate && echo "  unexpected PASS" && exit 1 || echo "  tamper detected (expected FAIL)"
pause 1
echo ""

echo "[4:15] BEAT 6 — replay idempotency (same request_id)"
pause 1
REQ_ID="demo-replay-$(date +%s)"
REPLAY_A="$DEMO_DIR/replay-a.json"
REPLAY_B="$DEMO_DIR/replay-b.json"
noetfield decide --sample --request-id "$REQ_ID" --api-url "$API_URL" --out "$REPLAY_A"
noetfield decide --sample --request-id "$REQ_ID" --api-url "$API_URL" --out "$REPLAY_B"
python3 -c "
import json
a=json.load(open('$REPLAY_A'))
b=json.load(open('$REPLAY_B'))
print('  request_id match:', a.get('request_id') == b.get('request_id') == '$REQ_ID')
print('  decision match:', a.get('decision') == b.get('decision'))
print('  audit_id match:', a.get('audit_id') == b.get('audit_id'))
"
pause 1
echo ""

ELAPSED=$(( $(date +%s) - START_TS ))
echo "=============================================="
echo " DEMO COMPLETE — ${ELAPSED}s elapsed"
echo " Artifacts: $DEMO_DIR"
if [[ "$ELAPSED" -gt 300 ]]; then
  echo " WARN: exceeded 300s target (UPG-0025)" >&2
  exit 1
fi
echo " PASS — under 300s cold demo target"
echo " Next: Phase C — first Trust Brief / AI Value OS briefing"
echo "=============================================="
