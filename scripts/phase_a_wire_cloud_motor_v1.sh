#!/usr/bin/env bash
# phase_a_wire_cloud_motor_v1.sh — run from repo root; wires Railway loop-runner + CF motor
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

echo "== Step 2: deploy CF loop motor with Railway URL + secret =="
LOOP_RUNNER_URL="$URL" LOOP_RUNNER_SECRET="$SECRET" bash "$ROOT/scripts/deploy_noos_loop_fleet_tick_cf_v1.sh"

echo "== Step 3: verify =="
curl -fsS "https://noos-loop-fleet-tick-v1.sina-kazemnezhad-ca.workers.dev/health" | python3 -m json.tool
echo
curl -fsS "${URL}/health" | python3 -m json.tool
