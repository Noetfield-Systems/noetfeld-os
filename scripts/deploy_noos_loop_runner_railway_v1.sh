#!/usr/bin/env bash
# deploy_noos_loop_runner_railway_v1.sh — Railway HTTP loop execution plane
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

PROJECT="${RAILWAY_PROJECT_NAME:-noetfield-platform}"
SERVICE="${RAILWAY_LOOP_RUNNER_SERVICE:-noos-loop-runner}"
RAILWAY="${RAILWAY_BIN:-/Users/sinakazemnezhad/.railway/bin/railway}"
CONFIG="${ROOT}/ops/railway/noos-loop-runner/railway.toml"
DOCKERFILE="ops/railway/noos-loop-runner/Dockerfile"
BUILD_SHA_FILE="${ROOT}/ops/railway/noos-loop-runner/BUILD_SHA"
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

_vars_json="$("$RAILWAY" variables --service "$SERVICE" --json 2>/dev/null || echo '{}')"
_existing_loop_secret="$(echo "$_vars_json" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('LOOP_RUNNER_SECRET',''))" 2>/dev/null || true)"
_existing_noos_secret="$(echo "$_vars_json" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('NOOS_LOOP_SECRET',''))" 2>/dev/null || true)"

if [[ -z "${NOOS_LOOP_SECRET:-}" && -n "$_existing_noos_secret" ]]; then
  NOOS_LOOP_SECRET="$_existing_noos_secret"
  log "reusing NOOS_LOOP_SECRET from Railway"
elif [[ -z "${NOOS_LOOP_SECRET:-}" && -n "$_existing_loop_secret" ]]; then
  NOOS_LOOP_SECRET="$_existing_loop_secret"
  log "migrating LOOP_RUNNER_SECRET → NOOS_LOOP_SECRET (same value)"
elif [[ -z "${NOOS_LOOP_SECRET:-}" ]]; then
  NOOS_LOOP_SECRET="$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')"
  log "generated NEW NOOS_LOOP_SECRET"
fi
LOOP_RUNNER_SECRET="$NOOS_LOOP_SECRET"

GIT_SHA="$(git -C "$ROOT" rev-parse HEAD 2>/dev/null || echo unknown)"
printf '%s' "$GIT_SHA" > "$BUILD_SHA_FILE"
log "BUILD_SHA=${GIT_SHA:0:12}"

log "pin Dockerfile on service (prevents gel-api wrong-image deploy)"
(cd "$ROOT" && "$RAILWAY" variables set \
  "RAILWAY_DOCKERFILE_PATH=${DOCKERFILE}" \
  "NOOS_GIT_SHA=${GIT_SHA}" \
  --service "$SERVICE") 2>/dev/null || true

log "deploy from ${ROOT} using ${DOCKERFILE}"
_swap_railway_config
(cd "$ROOT" && "$RAILWAY" up --detach --service "$SERVICE")

log "set loop secrets on Railway"
(cd "$ROOT" && "$RAILWAY" variables set \
  "NOOS_LOOP_SECRET=${NOOS_LOOP_SECRET}" \
  "LOOP_RUNNER_SECRET=${LOOP_RUNNER_SECRET}" \
  --service "$SERVICE") 2>/dev/null || true

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
  exit 0
fi

URL="https://${DOMAIN}"
log "health probe ${URL}/health (must be noos-loop-runner + git_sha, not gel-api)"
for i in 1 2 3 4 5 6 8 10 12 15; do
  body="$(curl -fsS "${URL}/health" 2>/dev/null || true)"
  if echo "$body" | python3 -c '
import json,sys
d=json.load(sys.stdin)
sys.exit(0 if d.get("service")=="noos-loop-runner" and d.get("git_sha") not in (None,"","unknown") else 1)
' 2>/dev/null; then
    echo "$body"
    log "PASS — LOOP_RUNNER_URL=${URL}"
    if [[ -f "$HOME/.noetfield-platform-secrets/noetfield.env" && "${SYNC_RAILWAY_ENV:-1}" == "1" ]]; then
      bash "$ROOT/scripts/sync_railway_loop_runner_env_v1.sh" || log "WARN: Supabase env sync failed"
    fi
    log "verify: python3 scripts/verify_noos_loop_runner_railway_v1.py --url ${URL} --write-receipt"
    exit 0
  fi
  if echo "$body" | python3 -c 'import json,sys; d=json.load(sys.stdin); sys.exit(0 if d.get("service")=="noos-loop-runner" else 1)' 2>/dev/null; then
    log "WARN: service=noos-loop-runner but git_sha missing — waiting for new deploy..."
  else
    log "WARN: /health not loop-runner (likely gel-api wrong image) — waiting..."
  fi
  sleep 10
done
log "FAIL — deploy finished but /health did not return service=noos-loop-runner with git_sha"
exit 1
