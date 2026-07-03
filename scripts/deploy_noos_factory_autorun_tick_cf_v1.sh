#!/usr/bin/env bash
# deploy_noos_factory_autorun_tick_cf_v1.sh — deploy CF cron → GitHub repository_dispatch
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WORKER_DIR="$ROOT/cloud/workers/noos-factory-autorun-tick-v1"
REPO="${GITHUB_REPO:-Noetfield-Systems/noetfeld-os}"

token() {
  if [[ -n "${GITHUB_TOKEN:-}" ]]; then
    printf '%s' "$GITHUB_TOKEN"
    return 0
  fi
  if [[ -n "${GH_TOKEN:-}" ]]; then
    printf '%s' "$GH_TOKEN"
    return 0
  fi
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

cd "$WORKER_DIR"
printf '%s' "$GITHUB_TOKEN_VAL" | wrangler secret put GITHUB_TOKEN
printf '%s' "$REPO" | wrangler secret put GITHUB_REPO
wrangler deploy

echo "OK deployed noos-factory-autorun-tick-v1 cron */10 → repository_dispatch ($REPO)"
echo "Health: curl -fsS https://noos-factory-autorun-tick-v1.sina-kazemnezhad-ca.workers.dev/health"
