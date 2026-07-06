#!/usr/bin/env bash
# deploy_noos_loop_runner_railway_v1.sh — Railway HTTP loop execution plane
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

PROJECT="${RAILWAY_PROJECT_NAME:-noetfield-platform}"
SERVICE="${RAILWAY_LOOP_RUNNER_SERVICE:-noos-loop-runner}"
RAILWAY="${RAILWAY_BIN:-/Users/sinakazemnezhad/.railway/bin/railway}"
CONFIG="${ROOT}/ops/railway/noos-loop-runner/railway.toml"
ROOT_RAILWAY="${ROOT}/railway.toml"
ROOT_RAILWAY_BAK="${ROOT}/.railway.toml.gel-api.bak"

log() { printf '[deploy-loop-runner] %s\n' "$*"; }

_swap_railway_config() {
  if [[ -f "$ROOT_RAILWAY" ]]; then
    cp "$ROOT_RAILWAY" "$ROOT_RAILWAY_BAK"
  fi
  cp "$CONFIG" "$ROOT_RAILWAY"
  log "using loop-runner railway.toml (root gel-api config backed up)"
}

_restore_railway_config() {
  if [[ -f "$ROOT_RAILWAY_BAK" ]]; then
    mv "$ROOT_RAILWAY_BAK" "$ROOT_RAILWAY"
    log "restored root railway.toml"
  fi
}
trap _restore_railway_config EXIT

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

log "deploy from ${ROOT} using loop-runner Dockerfile"
_swap_railway_config
(cd "$ROOT" && "$RAILWAY" up --detach --service "$SERVICE")

log "set LOOP_RUNNER_SECRET on Railway (if not already)"
if [[ -n "${LOOP_RUNNER_SECRET:-}" ]]; then
  (cd "$ROOT" && "$RAILWAY" variables set LOOP_RUNNER_SECRET="$LOOP_RUNNER_SECRET" --service "$SERVICE") 2>/dev/null || true
fi

DOMAIN=""
for _ in 1 2 3 4 5 6; do
  DOMAIN="$(cd "$ROOT" && "$RAILWAY" domain --service "$SERVICE" 2>/dev/null | awk '/https:\/\//{print $2; exit}')"
  DOMAIN="${DOMAIN#https://}"
  DOMAIN="${DOMAIN#http://}"
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
  body="$(curl -fsS "${URL}/health" 2>/dev/null || true)"
  if echo "$body" | python3 -c 'import json,sys; d=json.load(sys.stdin); sys.exit(0 if d.get("service")=="noos-loop-runner" else 1)' 2>/dev/null; then
    echo "$body"
    log "PASS — LOOP_RUNNER_URL=${URL}"
    exit 0
  fi
  sleep 10
done
log "WARN — deploy submitted; /health did not return service=noos-loop-runner (domain may point at gel-api)"
