#!/usr/bin/env bash
# deploy_noos_loop_github_events_cf_v1.sh — GitHub App webhook receiver (Event Phase 1)
# Modeled on deploy_noos_loop_fleet_tick_cf_v1.sh. This worker is fetch-only
# (no cron) and forwards to the SAME Railway executor the fleet-tick worker
# already targets, reusing the same FLY_LOOP_EXECUTOR_URL / NOOS_LOOP_SECRET.
# One additional secret: MOTOR_APP_WEBHOOK_SECRET (founder-provisioned — see
# Event Phase 1a in docs/_NOOS_AGENT/ motor-repair plan; this script does not
# generate or choose that value).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck disable=SC1091
source "$ROOT/scripts/noos_load_noetfield_env_v1.sh"
noos_load_noetfield_env
WORKER_DIR="$ROOT/cloud/workers/noos-loop-github-events-v1"

EXECUTOR_URL="${FLY_LOOP_EXECUTOR_URL:-${RAILWAY_LOOP_EXECUTOR_URL:-https://noos-loop-runner-production.up.railway.app}}"
EXECUTOR_URL="${EXECUTOR_URL%/}"

if [[ -z "${NOOS_LOOP_SECRET:-}" ]]; then
  noos_load_noetfield_env
fi
if [[ -z "${NOOS_LOOP_SECRET:-}" ]]; then
  echo "FAIL: set NOOS_LOOP_SECRET (same value the fleet-tick worker already uses)" >&2
  exit 1
fi
if [[ -z "${MOTOR_APP_WEBHOOK_SECRET:-}" ]]; then
  echo "FAIL: set MOTOR_APP_WEBHOOK_SECRET — founder-provisioned GitHub App webhook secret (Event Phase 1a)" >&2
  exit 1
fi

cd "$WORKER_DIR"
if [[ -n "${GITHUB_ACTIONS:-}" && "${NOOS_WRANGLER_SKIP_SECRET_PUT:-1}" != "0" ]]; then
  wrangler deploy
else
  printf '%s' "$EXECUTOR_URL" | wrangler secret put FLY_LOOP_EXECUTOR_URL
  printf '%s' "$NOOS_LOOP_SECRET" | wrangler secret put NOOS_LOOP_SECRET
  printf '%s' "$MOTOR_APP_WEBHOOK_SECRET" | wrangler secret put MOTOR_APP_WEBHOOK_SECRET
  wrangler deploy
fi

echo "OK deployed noos-loop-github-events-v1 -> Railway ($EXECUTOR_URL)"
echo "Health: curl -fsS https://noos-loop-github-events-v1.sina-kazemnezhad-ca.workers.dev/health"
echo "Next: set this worker's URL as the GitHub App webhook URL (Event Phase 1a, founder-gated)."
