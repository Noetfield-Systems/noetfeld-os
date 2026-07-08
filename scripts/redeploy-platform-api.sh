#!/usr/bin/env bash
# Canonical platform-api redeploy — set GIT_SHA, build, wait for live match, verify, sync probe.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

API_SERVICE="${RAILWAY_API_SERVICE:-platform-api}"
PLATFORM_DOMAIN="${NF_PLATFORM_LIVE_DOMAIN:-platform.noetfield.com}"
PLATFORM_BASE="https://${PLATFORM_DOMAIN}"

log() { printf '[redeploy-platform-api] %s\n' "$*"; }

railway_cmd() {
  RAILWAY_CALLER="skill:use-railway" RAILWAY_AGENT_SESSION="${RAILWAY_AGENT_SESSION:-redeploy-platform-api-$$}" \
    railway "$@"
}

GIT_SHA="$(git -C "$ROOT" rev-parse HEAD 2>/dev/null || true)"
if [[ -z "$GIT_SHA" ]]; then
  log "FAIL: not a git repo"
  exit 1
fi

command -v railway >/dev/null || { log "FAIL: railway CLI missing"; exit 1; }
railway_cmd whoami >/dev/null

log "greeting SSOT coupling check…"
python3 "$ROOT/scripts/sync_chat_greeting_asset.py"
python3 "$ROOT/scripts/verify_chat_greeting_coupling.py"

log "set GIT_SHA=${GIT_SHA:0:12} on ${API_SERVICE} (skip intermediate deploy)…"
railway_cmd variable set --service "$API_SERVICE" --skip-deploys "GIT_SHA=${GIT_SHA}"

log "deploy ${API_SERVICE}…"
railway_cmd up --service "$API_SERVICE" -d -y

log "wait for live git_sha…"
PLATFORM_BASE="$PLATFORM_BASE" "$ROOT/scripts/wait-for-platform-sha.sh" --expected-sha "$GIT_SHA" --platform-base "$PLATFORM_BASE"

log "post-deploy verify (platform + www intake path)…"
python3 "$ROOT/scripts/nf_post_deploy_verify.py" --expected-sha "$GIT_SHA" --surface both \
  --platform-base "$PLATFORM_BASE" --www-base "${NF_WWW_LIVE_BASE:-https://www.noetfield.com}"

log "sync probe EXPECTED_GIT_SHA…"
"$ROOT/scripts/sync-probe-expected-sha.sh" "$GIT_SHA"

log "PASS — platform-api live at ${GIT_SHA:0:12}"
