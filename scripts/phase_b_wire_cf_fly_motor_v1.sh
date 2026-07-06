#!/usr/bin/env bash
# phase_b_wire_cf_fly_motor_v1.sh — Fly executor green → CF motor (cron off) → E2E → cron on
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

ENV_FILE="${NOETFIELD_ENV:-$HOME/.sourcea-secrets/noetfield.env}"
FLY_URL="${FLY_LOOP_EXECUTOR_URL:-https://noos-loop-executor.fly.dev}"

if [[ -f "$ENV_FILE" ]]; then
  set -a
  # shellcheck disable=SC1090
  . "$ENV_FILE"
  set +a
fi

echo "== Step 1: verify Fly loop executor =="
python3 scripts/verify_noos_loop_executor_fly_v1.py --json

echo "== Step 2: redeploy Fly (factory handler + latest code) =="
bash scripts/deploy_noos_loop_executor_fly_v1.sh

echo "== Step 3: deploy CF motor → Fly (cron OFF) =="
FLY_LOOP_EXECUTOR_URL="$FLY_URL" ENABLE_CF_CRON=0 bash scripts/deploy_noos_loop_fleet_tick_cf_v1.sh

echo "== Step 4: CF motor health =="
curl -fsS "https://noos-loop-fleet-tick-v1.sina-kazemnezhad-ca.workers.dev/health" | python3 -m json.tool

echo "== Step 5: E2E CF→Fly tick (wait=1) =="
bash scripts/verify_noos_cloud_motor_e2e_v1.sh

echo "== Step 6: enable CF */5 cron =="
FLY_LOOP_EXECUTOR_URL="$FLY_URL" ENABLE_CF_CRON=1 bash scripts/deploy_noos_loop_fleet_tick_cf_v1.sh

echo "OK phase B wire complete — CF cron → Fly executor"
