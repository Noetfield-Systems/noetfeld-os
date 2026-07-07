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
[[ -n "$URL" && -n "$KEY" ]] || { log "FAIL: Supabase URL/key not in $NOETFIELD_LOCAL_ENV"; exit 1; }

"$RAILWAY" link --project "${RAILWAY_PROJECT_NAME:-noetfield-platform}" --environment production --service "$SERVICE" 2>/dev/null || true

"$RAILWAY" variables set \
  "NOETFIELD_SUPABASE_URL=$URL" \
  "NOETFIELD_SUPABASE_SERVICE_ROLE_KEY=$KEY" \
  "SUPABASE_URL=$URL" \
  "SUPABASE_SERVICE_ROLE_KEY=$KEY" \
  --service "$SERVICE"

log "OK — Supabase env on $SERVICE (service will restart)"
