#!/usr/bin/env bash
# deploy_noos_loop_fleet_tick_cf_v1.sh — CF */5 cron → parallel domain loop dispatches
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WORKER_DIR="$ROOT/cloud/workers/noos-loop-fleet-tick-v1"
REPO="${GITHUB_REPO:-Noetfield-Systems/noetfeld-os}"

token() {
  if [[ -n "${GITHUB_TOKEN:-}" ]]; then printf '%s' "$GITHUB_TOKEN"; return 0; fi
  if [[ -n "${GH_TOKEN:-}" ]]; then printf '%s' "$GH_TOKEN"; return 0; fi
  git credential fill <<EOF 2>/dev/null | awk -F= '$1=="password"{print $2; exit}'
protocol=https
host=github.com

EOF
}

GITHUB_TOKEN_VAL="$(token || true)"
if [[ -z "$GITHUB_TOKEN_VAL" ]]; then
  echo "FAIL: set GITHUB_TOKEN or configure git credential for github.com" >&2
  exit 1
fi

echo "== L12 schedule gate (registry home) =="
python3 "$ROOT/scripts/verify_noos_loop_schedule_registry_v1.py" --skip-missing || {
  echo "FAIL: loop schedule drift — fix data/noos-24-7-loops-v1.json vs .github/workflows before deploy" >&2
  exit 1
}

cd "$WORKER_DIR"
printf '%s' "$GITHUB_TOKEN_VAL" | wrangler secret put GITHUB_TOKEN
printf '%s' "$REPO" | wrangler secret put GITHUB_REPO
wrangler deploy

echo "OK deployed noos-loop-fleet-tick-v1 cron */5 → 6 domain loops ($REPO)"
echo "Health: curl -fsS https://noos-loop-fleet-tick-v1.sina-kazemnezhad-ca.workers.dev/health"
