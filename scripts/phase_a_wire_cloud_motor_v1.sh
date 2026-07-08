#!/usr/bin/env bash
# phase_a_wire_cloud_motor_v1.sh — one-lane cloud motor ops runbook (UPG-LS-02)
# Run from repo root. Chains: Railway deploy → Supabase env sync → CF motor deploy → E2E gate.
# On 401/resync: `make cloud-motor-resync` (same script). Never rotate LOOP_RUNNER_SECRET manually.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

RAILWAY="${RAILWAY_BIN:-/Users/sinakazemnezhad/.railway/bin/railway}"

echo "== Step 1: deploy Railway noos-loop-runner (must return service=noos-loop-runner) =="
bash "$ROOT/scripts/deploy_noos_loop_runner_railway_v1.sh"

URL="https://noos-loop-runner-production.up.railway.app"
SECRET="$("$RAILWAY" variables --service noos-loop-runner --json 2>/dev/null | python3 -c "
import json,sys
d=json.load(sys.stdin)
print(d.get('LOOP_RUNNER_SECRET',''))
" 2>/dev/null || true)"

if [[ -z "$SECRET" ]]; then
  echo "FAIL: LOOP_RUNNER_SECRET not found on Railway noos-loop-runner service" >&2
  exit 1
fi

echo "== Step 2: sync Supabase env on Railway loop-runner =="
bash "$ROOT/scripts/sync_railway_loop_runner_env_v1.sh"

echo "== Step 3: deploy CF loop motor with Railway URL + secret =="
LOOP_RUNNER_URL="$URL" LOOP_RUNNER_SECRET="$SECRET" bash "$ROOT/scripts/deploy_noos_loop_fleet_tick_cf_v1.sh"

echo "== Step 4: verify health =="
curl -fsS "https://noos-loop-fleet-tick-v1.sina-kazemnezhad-ca.workers.dev/health" | python3 -m json.tool
echo
curl -fsS "${URL}/health" | python3 -m json.tool
echo
echo "== Step 5: E2E gate =="
bash "$ROOT/scripts/verify_noos_cloud_motor_e2e_v1.sh"
