#!/usr/bin/env bash
# verify_noos_cloud_motor_e2e_v1.sh — CF motor → Railway executor → liveness → deadman
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

fail() { printf '[e2e] FAIL: %s\n' "$*" >&2; exit 1; }
ok() { printf '[e2e] OK: %s\n' "$*"; }

RAILWAY_URL="${RAILWAY_LOOP_RUNNER_URL:-${FLY_LOOP_EXECUTOR_URL:-https://noos-loop-runner-production.up.railway.app}}"
RAILWAY_URL="${RAILWAY_URL%/}"
CF_MOTOR="https://noos-loop-fleet-tick-v1.sina-kazemnezhad-ca.workers.dev"
DEADMAN="https://noos-deadman-v1.sina-kazemnezhad-ca.workers.dev"

body="$(curl -fsS "${RAILWAY_URL}/health")"
echo "$body" | python3 -c '
import json, sys
d = json.load(sys.stdin)
svc = str(d.get("service") or "")
ok = svc == "noos-loop-runner" or "loop-runner" in svc or d.get("execution_mode") == "railway"
sys.exit(0 if ok else 1)
' || fail "Railway /health not noos-loop-runner"
ok "Railway loop-runner health"

motor="$(curl -fsS "${CF_MOTOR}/health")"
echo "$motor" | python3 -c 'import json,sys; d=json.load(sys.stdin); sys.exit(0 if str(d.get("execution_plane","")).startswith("railway:") else 1)' || fail "CF motor not on railway execution plane"
ok "CF motor execution_plane=railway"

tick="$(curl -fsS -X POST "${CF_MOTOR}/tick?event_type=noos_inbox_loop_tick&wait=1")"
echo "$tick" | python3 -c 'import json,sys; d=json.load(sys.stdin); r=(d.get("results") or [{}])[0]; sys.exit(0 if r.get("status")==200 and r.get("ok") else 1)' || fail "CF→Railway tick failed (check NOOS_LOOP_SECRET sync)"
ok "CF motor dispatched inbox loop via Railway (HTTP 200)"

sleep 3
# shellcheck disable=SC1091
source "$ROOT/scripts/noos_load_noetfield_env_v1.sh"
noos_load_noetfield_env
export NOETFIELD_SUPABASE_URL SUPABASE_URL NOETFIELD_SUPABASE_SERVICE_ROLE_KEY SUPABASE_SERVICE_ROLE_KEY
rows="$(python3 - <<'PY'
import json, os, urllib.request
url = (os.environ.get("NOETFIELD_SUPABASE_URL") or os.environ.get("SUPABASE_URL") or "").rstrip("/")
key = os.environ.get("NOETFIELD_SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or ""
if not url or not key:
    print("skip")
    raise SystemExit(0)
req = urllib.request.Request(
    f"{url}/rest/v1/noos_loop_registry?select=loop_id,last_fired_at&loop_id=eq.inbox",
    headers={"apikey": key, "Authorization": f"Bearer {key}"},
)
with urllib.request.urlopen(req, timeout=20) as resp:
    rows = json.load(resp)
print(json.dumps(rows))
PY
)"
if [[ "$rows" != "skip" ]]; then
  echo "$rows" | python3 -c 'import json,sys; r=json.load(sys.stdin); sys.exit(0 if r and r[0].get("last_fired_at") else 1)' && ok "Supabase liveness row for inbox" || fail "inbox not in noos_loop_registry yet (loop may still be running)"
fi

deadman="$(curl -fsS -X POST "${DEADMAN}/check?telegram=0")"
echo "$deadman" | python3 -c 'import json,sys; d=json.load(sys.stdin); sys.exit(0 if "stale_count" in d else 1)' || fail "deadman /check failed"
stale="$(echo "$deadman" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("stale_count",999))')"
if [[ "$stale" -gt 1 ]]; then
  printf '[e2e] WARN: stale_count=%s (target <=1 until all loops seeded)\n' "$stale" >&2
else
  ok "deadman stale_count<=${stale}"
fi
alert="$(echo "$deadman" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("alert",{}).get("reason","suppressed"))')"
tg="$(curl -fsS "${DEADMAN}/health" | python3 -c 'import json,sys; d=json.load(sys.stdin); print(d.get("telegram_send_alerts",False))')"
ok "deadman telegram lane suppressed=${tg} alert=${alert}"
echo "$deadman" | python3 -m json.tool | head -20
