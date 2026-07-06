#!/usr/bin/env bash
# sync_railway_loop_runner_env_v1.sh — Supabase + loop secrets on Railway noos-loop-runner
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
RAILWAY="${RAILWAY_BIN:-/Users/sinakazemnezhad/.railway/bin/railway}"
SERVICE="${RAILWAY_LOOP_RUNNER_SERVICE:-noos-loop-runner}"
ENV_FILE="${NOETFIELD_ENV:-$HOME/.sourcea-secrets/noetfield.env}"

log() { printf '[sync-loop-runner-env] %s\n' "$*"; }

[[ -f "$ENV_FILE" ]] || { log "FAIL: missing $ENV_FILE"; exit 1; }
set -a; # shellcheck disable=SC1090
. "$ENV_FILE"
set +a

URL="${NOETFIELD_SUPABASE_URL:-${SUPABASE_URL:-}}"
KEY="${NOETFIELD_SUPABASE_SERVICE_ROLE_KEY:-${SUPABASE_SERVICE_ROLE_KEY:-}}"
[[ -n "$URL" && -n "$KEY" ]] || { log "FAIL: Supabase URL/key not in $ENV_FILE"; exit 1; }

"$RAILWAY" link --project "${RAILWAY_PROJECT_NAME:-noetfield-platform}" --environment production --service "$SERVICE" 2>/dev/null || true

"$RAILWAY" variables set \
  "NOETFIELD_SUPABASE_URL=$URL" \
  "NOETFIELD_SUPABASE_SERVICE_ROLE_KEY=$KEY" \
  "SUPABASE_URL=$URL" \
  "SUPABASE_SERVICE_ROLE_KEY=$KEY" \
  --service "$SERVICE"

log "OK — Supabase env on $SERVICE (service will restart)"
