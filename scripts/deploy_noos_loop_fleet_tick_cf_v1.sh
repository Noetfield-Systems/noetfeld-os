#!/usr/bin/env bash
# deploy_noos_loop_fleet_tick_cf_v1.sh — CF */5 cron → Railway loop runner (no GHA)
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WORKER_DIR="$ROOT/cloud/workers/noos-loop-fleet-tick-v1"
TABLE_SRC="$ROOT/data/noos-cf-dispatch-table-v1.json"
TABLE_DST="$WORKER_DIR/src/dispatch-table.json"

cp "$TABLE_SRC" "$TABLE_DST"

if [[ -z "${LOOP_RUNNER_URL:-}" ]]; then
  echo "FAIL: set LOOP_RUNNER_URL (Railway noos-loop-runner public URL)" >&2
  exit 1
fi
if [[ -z "${LOOP_RUNNER_SECRET:-}" ]]; then
  echo "FAIL: set LOOP_RUNNER_SECRET (must match Railway service)" >&2
  exit 1
fi

cd "$WORKER_DIR"
printf '%s' "$LOOP_RUNNER_URL" | wrangler secret put LOOP_RUNNER_URL
printf '%s' "$LOOP_RUNNER_SECRET" | wrangler secret put LOOP_RUNNER_SECRET
wrangler deploy

echo "OK deployed noos-loop-fleet-tick-v1 → Railway ($LOOP_RUNNER_URL)"
echo "Health: curl -fsS https://noos-loop-fleet-tick-v1.sina-kazemnezhad-ca.workers.dev/health"
echo "Verify: curl -X POST 'https://noos-loop-fleet-tick-v1.sina-kazemnezhad-ca.workers.dev/tick?all=1'"
