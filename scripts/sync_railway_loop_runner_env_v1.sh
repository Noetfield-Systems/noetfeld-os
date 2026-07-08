#!/usr/bin/env bash
# sync_railway_loop_runner_env_v1.sh — Supabase + loop secrets on Railway noos-loop-runner
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
RAILWAY="${RAILWAY_BIN:-/Users/sinakazemnezhad/.railway/bin/railway}"
SERVICE="${RAILWAY_LOOP_RUNNER_SERVICE:-noos-loop-runner}"
# shellcheck disable=SC1091
source "$ROOT/scripts/noos_resolve_local_env_v1.sh"

log() { printf '[sync-loop-runner-env] %s\n' "$*"; }

# shellcheck disable=SC1091
source "$ROOT/scripts/noos_load_noetfield_env_v1.sh"
noos_load_noetfield_env

URL="${NOETFIELD_SUPABASE_URL:-${SUPABASE_URL:-}}"
KEY="${NOETFIELD_SUPABASE_SERVICE_ROLE_KEY:-${SUPABASE_SERVICE_ROLE_KEY:-}}"
LOOP_SECRET="${NOOS_LOOP_SECRET:-${LOOP_RUNNER_SECRET:-}}"
[[ -n "$URL" && -n "$KEY" ]] || { log "FAIL: Supabase URL/key not in $NOETFIELD_LOCAL_ENV"; exit 1; }
[[ -n "$LOOP_SECRET" ]] || { log "FAIL: NOOS_LOOP_SECRET missing in platform vault"; exit 1; }

"$RAILWAY" link --project "${RAILWAY_PROJECT_NAME:-noetfield-platform}" --environment production --service "$SERVICE" 2>/dev/null || true

"$RAILWAY" variables set \
  "NOETFIELD_SUPABASE_URL=$URL" \
  "NOETFIELD_SUPABASE_SERVICE_ROLE_KEY=$KEY" \
  "SUPABASE_URL=$URL" \
  "SUPABASE_SERVICE_ROLE_KEY=$KEY" \
  "NOOS_LOOP_SECRET=$LOOP_SECRET" \
  "LOOP_RUNNER_SECRET=$LOOP_SECRET" \
  --service "$SERVICE"

log "OK — Supabase + loop secret on $SERVICE (service will restart)"

PORTFOLIO_ENV="${PORTFOLIO_SPINE_ENV:-$HOME/.sourcea-secrets/portfolio-spine.env}"
if [[ -f "$PORTFOLIO_ENV" ]]; then
  # shellcheck disable=SC1090
  set -a
  source "$PORTFOLIO_ENV" 2>/dev/null || true
  set +a
  if [[ -n "${SUPABASE_URL:-}" && -n "${SUPABASE_SERVICE_ROLE_KEY:-}" ]]; then
    "$RAILWAY" variables set \
      "PORTFOLIO_SPINE_SUPABASE_URL=$SUPABASE_URL" \
      "PORTFOLIO_SPINE_SERVICE_ROLE_KEY=$SUPABASE_SERVICE_ROLE_KEY" \
      --service "$SERVICE"
    log "OK — portfolio-spine env on $SERVICE"
  fi
fi

log "OK — loop runner env sync complete"
