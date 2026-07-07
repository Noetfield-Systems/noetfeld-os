#!/usr/bin/env bash
# phase_b_wire_cf_railway_motor_v1.sh — Railway executor green → CF motor (cron off) → E2E → cron on
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

# shellcheck disable=SC1091
source "$ROOT/scripts/noos_load_noetfield_env_v1.sh"
noos_load_noetfield_env

RAILWAY_URL="${RAILWAY_LOOP_RUNNER_URL:-${FLY_LOOP_EXECUTOR_URL:-https://noos-loop-runner-production.up.railway.app}}"
RAILWAY_URL="${RAILWAY_URL%/}"

echo "== Step 1: verify Railway loop runner =="
python3 scripts/verify_noos_loop_runner_railway_v1.py --json

echo "== Step 2: deploy CF motor → Railway (cron OFF) =="
FLY_LOOP_EXECUTOR_URL="$RAILWAY_URL" ENABLE_CF_CRON=0 bash scripts/deploy_noos_loop_fleet_tick_cf_v1.sh

echo "== Step 3: CF motor health =="
curl -fsS "https://noos-loop-fleet-tick-v1.sina-kazemnezhad-ca.workers.dev/health" | python3 -m json.tool

echo "== Step 4: E2E CF→Railway tick (wait=1) =="
FLY_LOOP_EXECUTOR_URL="$RAILWAY_URL" bash scripts/verify_noos_cloud_motor_e2e_v1.sh

echo "== Step 5: enable CF */5 cron =="
FLY_LOOP_EXECUTOR_URL="$RAILWAY_URL" ENABLE_CF_CRON=1 bash scripts/deploy_noos_loop_fleet_tick_cf_v1.sh

echo "OK phase B wire complete — CF cron → Railway executor"
