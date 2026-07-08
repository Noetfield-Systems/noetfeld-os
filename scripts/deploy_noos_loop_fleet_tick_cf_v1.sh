#!/usr/bin/env bash
# deploy_noos_loop_fleet_tick_cf_v1.sh — CF motor → Railway loop executor (Option A)
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck disable=SC1091
source "$ROOT/scripts/noos_load_noetfield_env_v1.sh"
noos_load_noetfield_env
WORKER_DIR="$ROOT/cloud/workers/noos-loop-fleet-tick-v1"
CF_ACCOUNT_ID="${CLOUDFLARE_ACCOUNT_ID:-0d0b967b77e2e5535455d39ff3dae72c}"
TABLE_SRC="$ROOT/data/noos-cf-dispatch-table-v1.json"
TABLE_DST="$WORKER_DIR/src/dispatch-table.json"
WRANGLER="$WORKER_DIR/wrangler.toml"
WRANGLER_BAK="$WORKER_DIR/wrangler.toml.bak-deploy"
RAILWAY="${RAILWAY_BIN:-$HOME/.railway/bin/railway}"
RAILWAY_SERVICE="${RAILWAY_LOOP_RUNNER_SERVICE:-noos-loop-runner}"

cp "$TABLE_SRC" "$TABLE_DST"

EXECUTOR_URL="${FLY_LOOP_EXECUTOR_URL:-${RAILWAY_LOOP_EXECUTOR_URL:-https://noos-loop-runner-production.up.railway.app}}"
EXECUTOR_URL="${EXECUTOR_URL%/}"

if [[ -z "${NOOS_LOOP_SECRET:-}" && -x "$RAILWAY" ]]; then
  NOOS_LOOP_SECRET="$("$RAILWAY" variables --service "$RAILWAY_SERVICE" --json 2>/dev/null | python3 -c "
import json,sys
try:
    d=json.load(sys.stdin)
except Exception:
    sys.exit(0)
print(d.get('NOOS_LOOP_SECRET') or d.get('LOOP_RUNNER_SECRET') or '')
" 2>/dev/null || true)"
  [[ -n "${NOOS_LOOP_SECRET:-}" ]] && echo "using NOOS_LOOP_SECRET from Railway ${RAILWAY_SERVICE}"
fi

if [[ -z "${NOOS_LOOP_SECRET:-}" ]]; then
  noos_load_noetfield_env
fi

if [[ -z "${NOOS_LOOP_SECRET:-}" ]]; then
  echo "FAIL: set NOOS_LOOP_SECRET or ensure Railway ${RAILWAY_SERVICE} has it" >&2
  exit 1
fi

ENABLE_CF_CRON="${ENABLE_CF_CRON:-1}"
cp "$WRANGLER" "$WRANGLER_BAK"
if [[ "$ENABLE_CF_CRON" == "1" ]]; then
  cat > "$WRANGLER" <<EOF
name = "noos-loop-fleet-tick-v1"
main = "src/index.js"
compatibility_date = "2024-06-01"
account_id = "$CF_ACCOUNT_ID"

[triggers]
crons = ["*/5 * * * *"]
EOF
  echo "CF cron ENABLED (*/5)"
else
  cat > "$WRANGLER" <<EOF
name = "noos-loop-fleet-tick-v1"
main = "src/index.js"
compatibility_date = "2024-06-01"
account_id = "$CF_ACCOUNT_ID"
EOF
  echo "CF cron DISABLED"
fi

cd "$WORKER_DIR"
if [[ -n "${GITHUB_ACTIONS:-}" && "${NOOS_WRANGLER_SKIP_SECRET_PUT:-1}" != "0" ]]; then
  wrangler deploy
else
  printf '%s' "$EXECUTOR_URL" | wrangler secret put FLY_LOOP_EXECUTOR_URL
  printf '%s' "$NOOS_LOOP_SECRET" | wrangler secret put NOOS_LOOP_SECRET
  wrangler deploy
fi
mv "$WRANGLER_BAK" "$WRANGLER"

for dead in GITHUB_REPO GITHUB_TOKEN LOOP_RUNNER_SECRET LOOP_RUNNER_URL; do
  wrangler secret delete "$dead" 2>/dev/null && echo "deleted secret $dead" || echo "skip delete $dead (not set)"
done

echo "OK deployed noos-loop-fleet-tick-v1 → Railway ($EXECUTOR_URL) cron=${ENABLE_CF_CRON}"
echo "Health: curl -fsS https://noos-loop-fleet-tick-v1.sina-kazemnezhad-ca.workers.dev/health"
echo "Verify: curl -X POST 'https://noos-loop-fleet-tick-v1.sina-kazemnezhad-ca.workers.dev/tick?event_type=noos_inbox_loop_tick&wait=1'"
