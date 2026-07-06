#!/usr/bin/env bash
# verify_noos_cloud_motor_e2e_v1.sh — CF motor → Railway → liveness → deadman
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
RAILWAY="${RAILWAY_BIN:-/Users/sinakazemnezhad/.railway/bin/railway}"

fail() { printf '[e2e] FAIL: %s\n' "$*" >&2; exit 1; }
ok() { printf '[e2e] OK: %s\n' "$*"; }

URL="${LOOP_RUNNER_URL:-https://noos-loop-runner-production.up.railway.app}"
CF_MOTOR="https://noos-loop-fleet-tick-v1.sina-kazemnezhad-ca.workers.dev"
DEADMAN="https://noos-deadman-v1.sina-kazemnezhad-ca.workers.dev"

body="$(curl -fsS "${URL}/health")"
echo "$body" | python3 -c 'import json,sys; d=json.load(sys.stdin); sys.exit(0 if d.get("service")=="noos-loop-runner" else 1)' || fail "Railway /health not noos-loop-runner"
ok "Railway loop-runner health"

tick="$(curl -fsS -X POST "${CF_MOTOR}/tick?event_type=noos_inbox_loop_tick")"
echo "$tick" | python3 -c 'import json,sys; d=json.load(sys.stdin); r=(d.get("results") or [{}])[0]; sys.exit(0 if r.get("status")==200 else 1)' || fail "CF→Railway tick failed (401=resync secrets; check Railway logs)"
ok "CF motor dispatched inbox loop (HTTP 200)"

sleep 3
if [[ -f "$HOME/.sourcea-secrets/noetfield.env" ]]; then
  set -a; . "$HOME/.sourcea-secrets/noetfield.env"; set +a
fi
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

deadman="$(curl -fsS -X POST "${DEADMAN}/check")"
echo "$deadman" | python3 -c 'import json,sys; d=json.load(sys.stdin); sys.exit(0 if d.get("alert_sent") is not None else 1)' || fail "deadman /check failed"
stale="$(echo "$deadman" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("stale_count",999))')"
if [[ "$stale" -gt 1 ]]; then
  printf '[e2e] WARN: stale_count=%s (target <=1 until all loops seeded)\n' "$stale" >&2
else
  ok "deadman stale_count<=${stale}"
fi
alert="$(echo "$deadman" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("alert_sent"))')"
tg="$(curl -fsS "${DEADMAN}/health" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("telegram_ready"))')"
ok "deadman alert_sent=${alert} telegram_ready=${tg}"
echo "$deadman" | python3 -m json.tool | head -20
