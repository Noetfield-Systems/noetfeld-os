#!/usr/bin/env bash
# Deploy noetfeld-os GEL to Railway (api.noetfield.com lane).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

PROJECT="${RAILWAY_PROJECT_NAME:-noetfield-platform}"
SERVICE="${RAILWAY_GEL_SERVICE:-gel-api}"
DOMAIN="${NF_GEL_LIVE_DOMAIN:-api.noetfield.com}"
RAILWAY="/Users/sinakazemnezhad/.railway/bin/railway"

log() { printf '[deploy-gel-api] %s\n' "$*"; }

if ! $RAILWAY whoami >/dev/null 2>&1; then
  log "FAIL: railway not logged in — run: railway login"
  exit 1
fi

log "link project ${PROJECT} (service ${SERVICE})"
$RAILWAY link --project "$PROJECT" --environment production --service "$SERVICE" 2>/dev/null || {
  log "creating service ${SERVICE}…"
  $RAILWAY link --project "$PROJECT" --environment production 2>/dev/null || true
  $RAILWAY add --service "$SERVICE" 2>/dev/null || true
  $RAILWAY link --project "$PROJECT" --environment production --service "$SERVICE"
}

log "deploy GEL from ${ROOT}"
$RAILWAY up --detach

log "ensure custom domain ${DOMAIN}"
$RAILWAY domain --service "$SERVICE" "$DOMAIN" 2>/dev/null || \
  $RAILWAY domain add "$DOMAIN" --service "$SERVICE" 2>/dev/null || \
  log "warn: set ${DOMAIN} in Railway dashboard if CLI domain add fails"

log "health probe (may take ~60s on cold start)…"
for i in 1 2 3 4 5 6; do
  if curl -fsS "https://${DOMAIN}/health" >/dev/null 2>&1; then
    curl -sS "https://${DOMAIN}/health"
    echo
    log "PASS — https://${DOMAIN}/health"
    exit 0
  fi
  sleep 10
done

log "WARN — deploy submitted; https://${DOMAIN}/health not ready yet (check Railway logs)"
