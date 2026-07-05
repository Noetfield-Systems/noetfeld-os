#!/usr/bin/env bash
# deploy_noos_loop_runner_railway_v1.sh — Railway HTTP loop execution plane
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

PROJECT="${RAILWAY_PROJECT_NAME:-noetfield-platform}"
SERVICE="${RAILWAY_LOOP_RUNNER_SERVICE:-noos-loop-runner}"
RAILWAY="${RAILWAY_BIN:-/Users/sinakazemnezhad/.railway/bin/railway}"
CONFIG="${ROOT}/ops/railway/noos-loop-runner/railway.toml"

log() { printf '[deploy-loop-runner] %s\n' "$*"; }

if ! "$RAILWAY" whoami >/dev/null 2>&1; then
  log "FAIL: railway not logged in — run: railway login"
  exit 1
fi

log "link project ${PROJECT} service ${SERVICE}"
"$RAILWAY" link --project "$PROJECT" --environment production --service "$SERVICE" 2>/dev/null || {
  "$RAILWAY" link --project "$PROJECT" --environment production 2>/dev/null || true
  "$RAILWAY" add --service "$SERVICE" 2>/dev/null || true
  "$RAILWAY" link --project "$PROJECT" --environment production --service "$SERVICE"
}

if [[ -z "${LOOP_RUNNER_SECRET:-}" ]]; then
  LOOP_RUNNER_SECRET="$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')"
  log "generated LOOP_RUNNER_SECRET (set in Railway dashboard + CF worker secret)"
fi

log "deploy from ${ROOT} using ${CONFIG}"
(cd "$ROOT" && RAILWAY_CONFIG_FILE="$CONFIG" "$RAILWAY" up --detach --service "$SERVICE")

log "set LOOP_RUNNER_SECRET on Railway (if not already)"
if [[ -n "${LOOP_RUNNER_SECRET:-}" ]]; then
  (cd "$ROOT" && RAILWAY_CONFIG_FILE="$CONFIG" "$RAILWAY" variables set LOOP_RUNNER_SECRET="$LOOP_RUNNER_SECRET" --service "$SERVICE") 2>/dev/null || true
fi

DOMAIN=""
for _ in 1 2 3 4 5 6; do
  DOMAIN="$(cd "$ROOT" && RAILWAY_CONFIG_FILE="$CONFIG" "$RAILWAY" domain --service "$SERVICE" 2>/dev/null | awk '/https:\/\//{print $2; exit}')"
  [[ -n "$DOMAIN" ]] && break
  sleep 5
done
if [[ -z "$DOMAIN" ]]; then
  log "WARN: no public domain yet — use Railway dashboard → noos-loop-runner → Settings → Generate Domain"
  log "Then set LOOP_RUNNER_URL=https://<domain> on CF worker"
  exit 0
fi

URL="https://${DOMAIN}"
log "health probe ${URL}/health"
for i in 1 2 3 4 5 6 8 10 12; do
  if curl -fsS "${URL}/health" >/dev/null 2>&1; then
    curl -sS "${URL}/health"
    echo
    log "PASS — LOOP_RUNNER_URL=${URL}"
    exit 0
  fi
  sleep 10
done
log "WARN — deploy submitted; health not ready yet"
