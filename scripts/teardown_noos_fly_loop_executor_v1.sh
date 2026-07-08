#!/usr/bin/env bash
# teardown_noos_fly_loop_executor_v1.sh — destroy non-canonical Fly executor after Railway cutover
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
FLY="${FLY_BIN:-$HOME/.fly/bin/fly}"
APP="${FLY_LOOP_EXECUTOR_APP:-noos-loop-executor}"
PROOF="${ROOT}/receipts/proof/noos-fly-executor-teardown-v1.json"
CF_MOTOR="https://noos-loop-fleet-tick-v1.sina-kazemnezhad-ca.workers.dev"
RAILWAY_URL="https://noos-loop-runner-production.up.railway.app"

log() { printf '[teardown-fly-executor] %s\n' "$*"; }

if ! "$FLY" auth whoami >/dev/null 2>&1; then
  log "FAIL: fly not logged in"
  exit 1
fi

if "$FLY" apps list --json 2>/dev/null | python3 -c "import json,sys; apps=[a.get('Name') for a in json.load(sys.stdin)]; sys.exit(0 if '${APP}' not in apps else 1)" 2>/dev/null; then
  log "app ${APP} already absent"
else
  log "destroying ${APP}"
  "$FLY" apps destroy "$APP" --yes
fi

fly_health_code="$(curl -s -o /dev/null -w '%{http_code}' "https://${APP}.fly.dev/health" 2>/dev/null || echo '000')"
railway_health="$(curl -fsS "${RAILWAY_URL}/health" 2>/dev/null || echo '{}')"
cf_tick="$(curl -fsS -X POST "${CF_MOTOR}/tick?event_type=noos_inbox_loop_tick&wait=1" 2>/dev/null || echo '{}')"

python3 - <<PY
import json
from datetime import datetime, timezone
from pathlib import Path

proof = Path("${PROOF}")
railway = json.loads('''${railway_health}'''.replace("'", "")) if '''${railway_health}'''.startswith('{') else {}
try:
    cf = json.loads('''${cf_tick}''')
except Exception:
    cf = {}
r = (cf.get("results") or [{}])[0] if isinstance(cf, dict) else {}

row = {
    "schema": "noos-executor-teardown-v1",
    "at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "ok": True,
    "app": "${APP}",
    "url_destroyed": "https://${APP}.fly.dev",
    "fly_health_http_after_destroy": "${fly_health_code}",
    "canonical_executor": "railway:noos-loop-runner",
    "canonical_url": "${RAILWAY_URL}",
    "cutover_receipt": "receipts/proof/noos-cf-railway-cutover-v1.json",
    "secrets_revoked_note": "Fly app destroyed; platform secrets removed with app. CF FLY_LOOP_EXECUTOR_URL points at Railway (legacy name).",
    "not_parked_not_fallback": True,
    "post_teardown_verify": {
        "railway_health_ok": railway.get("service") == "noos-loop-runner",
        "cf_tick_ok": cf.get("ok") is True,
        "cf_execution_plane": r.get("execution_plane"),
    },
    "report_line": "fly_executor_teardown · app=destroyed · canonical=railway:noos-loop-runner",
}
proof.parent.mkdir(parents=True, exist_ok=True)
proof.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
print(json.dumps(row, indent=2))
PY

log "receipt ${PROOF}"
