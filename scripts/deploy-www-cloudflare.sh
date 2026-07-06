#!/usr/bin/env bash
# Production deploy www.noetfield.com → Cloudflare Pages (noetfield-www).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

PROJECT="${CF_PAGES_PROJECT:-noetfield-www}"
BRANCH="${CF_PAGES_BRANCH:-main}"
CANONICAL="${NF_WWW_CANONICAL_URL:-https://www.noetfield.com}"
VAULT="${NF_SECRETS_VAULT:-$HOME/.sina/secrets.env}"

log() { printf '[deploy-www-cloudflare] %s\n' "$*"; }

read_vault() {
  local key="$1"
  if [[ ! -f "$VAULT" ]]; then return 1; fi
  grep -E "^${key}=" "$VAULT" | tail -1 | cut -d= -f2- | tr -d '"' || true
}

sync_pages_secrets() {
  local key value
  for key in RESEND_API_KEY INTAKE_EMAIL_FROM INTAKE_EMAIL_TO OPENROUTER_API_KEY TELEGRAM_NOETFIELD_OPS_BOT_TOKEN TELEGRAM_OPS_CHAT_ID; do
    value="$(read_vault "$key" || true)"
    if [[ -n "$value" ]]; then
      log "pages secret ${key}"
      printf '%s' "$value" | npx wrangler pages secret put "$key" --project-name "$PROJECT" 2>/dev/null || \
        log "WARN: could not set secret ${key}"
    fi
  done
}

ensure_project() {
  if npx wrangler pages project list 2>/dev/null | grep -q "$PROJECT"; then
    log "project exists: ${PROJECT}"
    return 0
  fi
  log "creating Pages project ${PROJECT} (production branch=${BRANCH})"
  npx wrangler pages project create "$PROJECT" --production-branch "$BRANCH" --compatibility-flags nodejs_compat
}

bash scripts/build-www-pages-dist.sh
python3 scripts/verify_chat_greeting_coupling.py

ensure_project
sync_pages_secrets

EXPECTED_SHA="$(git rev-parse HEAD)"
log "deploy branch=${BRANCH} sha=${EXPECTED_SHA:0:12}"
DEPLOY_OUT="$(npx wrangler pages deploy www-pages-dist --project-name "$PROJECT" --branch "$BRANCH" --commit-dirty=true 2>&1)"
printf '%s\n' "$DEPLOY_OUT"

PREVIEW_URL="$(printf '%s\n' "$DEPLOY_OUT" | grep -Eo 'https://[a-z0-9.-]+\.pages\.dev' | tail -1 || true)"
if [[ -z "$PREVIEW_URL" ]]; then
  PREVIEW_URL="$(npx wrangler pages deployment list --project-name "$PROJECT" --environment production 2>/dev/null | grep -Eo 'https://[a-z0-9.-]+\.pages\.dev' | head -1 || true)"
fi

if [[ -z "$PREVIEW_URL" ]]; then
  log "FAIL: could not determine Pages preview URL"
  python3 scripts/nf_post_deploy_verify.py --deploy-failed "cloudflare pages deploy missing preview url" --surface www || true
  exit 2
fi

log "preview URL: ${PREVIEW_URL}"

wait_for_preview_health() {
  local base="$1"
  local attempt code
  for attempt in $(seq 1 24); do
    code="$(curl -sS -o /dev/null -w '%{http_code}' "${base%/}/api/health" 2>/dev/null || echo 000)"
    if [[ "$code" == "200" ]]; then
      log "preview /api/health ready (${attempt})"
      return 0
    fi
    log "preview /api/health ${code} — retry ${attempt}/24…"
    sleep 5
  done
  return 1
}

wait_for_preview_health "$PREVIEW_URL" || log "WARN: preview health still not 200 — verify may fail"

log "smoke preview…"
curl -sS "${PREVIEW_URL}/health" | head -c 400
echo
curl -sS "${PREVIEW_URL}/api/intake/health" | python3 -m json.tool 2>/dev/null | head -20 || true

python3 scripts/nf_post_deploy_verify.py --expected-sha "$EXPECTED_SHA" --surface www --www-base "$PREVIEW_URL" || {
  log "FAIL: preview verify failed — do not cut DNS yet"
  exit 3
}

if [[ "${CF_PAGES_PROMOTE_PRODUCTION:-}" == "1" ]]; then
  log "production promotion requested — custom domain should serve latest deployment"
fi

if [[ "${CF_PAGES_DNS_READY:-}" == "1" ]]; then
  python3 scripts/nf_post_deploy_verify.py --expected-sha "$EXPECTED_SHA" --surface www --www-base "$CANONICAL" || {
    log "FAIL: canonical domain verify failed"
    exit 4
  }
fi

log "done — preview ${PREVIEW_URL} (canonical ${CANONICAL} when DNS cut over)"
