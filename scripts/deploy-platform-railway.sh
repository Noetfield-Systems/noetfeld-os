#!/usr/bin/env bash
# UPG-WWW-001 — provision platform.noetfield.com on Railway + Cloudflare DNS.
# Idempotent bootstrap: project, Postgres, Redis, platform API, custom domain, DNS cutover.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

# shellcheck source=scripts/read_platform_vault.sh
source "${ROOT}/scripts/read_platform_vault.sh"

PROJECT_NAME="${RAILWAY_PROJECT_NAME:-noetfield-platform}"
API_SERVICE="${RAILWAY_API_SERVICE:-platform-api}"
PG_SERVICE="${RAILWAY_PG_SERVICE:-postgres}"
REDIS_SERVICE="${RAILWAY_REDIS_SERVICE:-redis}"
PLATFORM_DOMAIN="${NF_PLATFORM_LIVE_DOMAIN:-platform.noetfield.com}"
CF_ZONE="${CF_NOETFIELD_ZONE_ID:-456aeba6b1a37d1fadbf6443cb929468}"

log() { printf '[upg-www-001] %s\n' "$*"; }

railway_cmd() {
  RAILWAY_CALLER="skill:use-railway" RAILWAY_AGENT_SESSION="${RAILWAY_AGENT_SESSION:-upg-www-001-$$}" \
    railway "$@"
}

ensure_project() {
  if railway_cmd status --json >/dev/null 2>&1; then
    local linked
    linked="$(railway_cmd status --json 2>/dev/null | python3 -c "import json,sys; print(json.load(sys.stdin).get('name',''))" 2>/dev/null || true)"
    log "Railway project linked: ${linked:-unknown}"
    return 0
  fi
  log "Creating Railway project: ${PROJECT_NAME}"
  if ! railway_cmd init --name "$PROJECT_NAME" --json >/dev/null 2>&1; then
    log "FAIL: could not create Railway project (trial resource limit?)"
    log "  → See docs/ops/UPG_SUPABASE_001_ACTIVATION.md for Supabase Noetfield Systems (tkgpapowwplupyekpivy)"
    log "  → Or Unlock Hobby Plan, or deploy via render.yaml (see docs/ops/UPG_WWW_001_PLATFORM_SPINE.md)"
    exit 3
  fi
}

ensure_data_services() {
  log "Ensuring Postgres + Redis services (skip if already present)..."
  railway_cmd add --database postgres --service "$PG_SERVICE" 2>/dev/null || log "  postgres service exists or add skipped"
  railway_cmd add --database redis --service "$REDIS_SERVICE" 2>/dev/null || log "  redis service exists or add skipped"
}

set_platform_variables() {
  log "Setting platform API variables on service ${API_SERVICE}..."
  local or_key resend_key resend_webhook_secret event_secret
  or_key="$(read_platform_vault OPENROUTER_API_KEY || true)"
  resend_key="$(read_platform_vault RESEND_API_KEY || true)"
  resend_webhook_secret="$(read_platform_vault RESEND_WEBHOOK_SECRET || true)"
  event_secret="$(read_platform_vault EVENT_INTEGRITY_SECRET || true)"

  railway_cmd variable set --service "$API_SERVICE" --skip-deploys \
    NOETFIELD_ENV=prod \
    NOETFIELD_SERVICE_NAME=noetfield-platform \
    RUNTIME_EVENT_STORE=postgres \
    INTAKE_PERSISTENCE=auto \
    PUBLIC_CHAT_ENABLED=true \
    PUBLIC_INTAKE_ENABLED=true \
    PUBLIC_CHAT_PROVIDER=auto \
    REDIS_SESSIONS_ENABLED=false \
    "TELEGRAM_WEBHOOK_BASE_URL=https://${PLATFORM_DOMAIN}" \
    PUBLIC_STATUS_PAGE_URL=https://www.noetfield.com/status/ \
    "PUBLIC_CHAT_CORS_ORIGINS=https://www.noetfield.com,https://noetfield.com" \
    GOVERNANCE_PILOT_AUTH_REQUIRED=true \
    'DATABASE_URL=${{Postgres.DATABASE_URL}}'

  [[ -n "$or_key" ]] && railway_cmd variable set --service "$API_SERVICE" --skip-deploys OPENROUTER_API_KEY="$or_key"
  [[ -n "$resend_key" ]] && railway_cmd variable set --service "$API_SERVICE" --skip-deploys RESEND_API_KEY="$resend_key"
  [[ -n "$resend_webhook_secret" ]] && railway_cmd variable set --service "$API_SERVICE" --skip-deploys RESEND_WEBHOOK_SECRET="$resend_webhook_secret"
  local gmail_app_pw tg_token tg_chat sweep_enabled triage_enabled admin_secret
  gmail_app_pw="$(read_gmail_app_password 2>/dev/null || true)"
  tg_token="$(read_platform_vault TELEGRAM_NOETFIELD_OPS_BOT_TOKEN 2>/dev/null || read_platform_vault TELEGRAM_BOT_TOKEN 2>/dev/null || true)"
  tg_chat="$(read_platform_vault TELEGRAM_OPS_CHAT_ID 2>/dev/null || true)"
  admin_secret="$(read_platform_vault ADMIN_DASHBOARD_SECRET 2>/dev/null || true)"
  sweep_enabled="${GMAIL_SWEEP_ENABLED:-false}"
  triage_enabled="${SIGNAL_TRIAGE_ENABLED:-false}"
  if [[ -n "$gmail_app_pw" ]]; then
    sweep_enabled="${GMAIL_SWEEP_ENABLED:-true}"
    triage_enabled="${SIGNAL_TRIAGE_ENABLED:-true}"
    railway_cmd variable set --service "$API_SERVICE" --skip-deploys GMAIL_APP_PASSWORD="$gmail_app_pw"
    railway_cmd variable set --service "$API_SERVICE" --skip-deploys NF_OPERATIONS_GOOGLE_WORKSPACE_APP_PASSWORD="$gmail_app_pw"
  fi
  railway_cmd variable set --service "$API_SERVICE" --skip-deploys \
    GMAIL_SWEEP_ENABLED="$sweep_enabled" \
    GMAIL_MAILBOX="${GMAIL_MAILBOX:-operations@noetfield.com}" \
    OPERATIONS_INBOX_TENANT_ID="${OPERATIONS_INBOX_TENANT_ID:-00000000-0000-4000-8000-000000000001}" \
    OPERATIONS_INBOX_ORGANIZATION_ID="${OPERATIONS_INBOX_ORGANIZATION_ID:-00000000-0000-4000-8000-000000000002}" \
    SIGNAL_TRIAGE_ENABLED="$triage_enabled" \
    SIGNAL_TRIAGE_INTERVAL_SEC="${SIGNAL_TRIAGE_INTERVAL_SEC:-120}"
  [[ -n "$tg_token" ]] && railway_cmd variable set --service "$API_SERVICE" --skip-deploys TELEGRAM_NOETFIELD_OPS_BOT_TOKEN="$tg_token"
  [[ -n "$tg_token" ]] && railway_cmd variable set --service "$API_SERVICE" --skip-deploys TELEGRAM_BOT_TOKEN="$tg_token"
  [[ -n "$tg_chat" ]] && railway_cmd variable set --service "$API_SERVICE" --skip-deploys TELEGRAM_OPS_CHAT_ID="$tg_chat"
  [[ -n "$admin_secret" ]] && railway_cmd variable set --service "$API_SERVICE" --skip-deploys ADMIN_DASHBOARD_SECRET="$admin_secret"
  [[ -n "$event_secret" ]] && railway_cmd variable set --service "$API_SERVICE" --skip-deploys EVENT_INTEGRITY_SECRET="$event_secret"
}

deploy_api() {
  log "Verifying greeting SSOT coupling on disk…"
  python3 "$ROOT/scripts/sync_chat_greeting_asset.py"
  python3 "$ROOT/scripts/verify_chat_greeting_coupling.py"
  log "Deploying platform API (Dockerfile.api)..."
  local git_sha
  git_sha="$(git -C "$ROOT" rev-parse HEAD 2>/dev/null || true)"
  if [[ -n "$git_sha" ]]; then
    railway_cmd variable set --service "$API_SERVICE" --skip-deploys "GIT_SHA=${git_sha}"
  fi
  railway_cmd up --service "$API_SERVICE" -d -y
  if [[ -n "$git_sha" ]]; then
    log "Waiting for live platform git_sha to match ${git_sha:0:12}…"
    PLATFORM_BASE="https://${PLATFORM_DOMAIN}" \
      "$ROOT/scripts/wait-for-platform-sha.sh" --expected-sha "$git_sha" --platform-base "https://${PLATFORM_DOMAIN}"
    python3 "$ROOT/scripts/nf_post_deploy_verify.py" --expected-sha "$git_sha" --surface platform \
      --platform-base "https://${PLATFORM_DOMAIN}"
    "$ROOT/scripts/sync_nf_probe_expected_sha.sh" || log "WARN: probe EXPECTED_GIT_SHA sync skipped"
  fi
}

wait_for_railway_url() {
  local url=""
  for _ in $(seq 1 30); do
    url="$(railway_cmd domain --service "$API_SERVICE" --json 2>/dev/null | python3 -c "
import json,sys
try:
    d=json.load(sys.stdin)
    items=d if isinstance(d,list) else d.get('domains',d.get('result',[]))
    for x in items or []:
        dom=x.get('domain') if isinstance(x,dict) else x
        if dom and 'railway.app' in str(dom):
            print('https://'+str(dom).replace('https://',''))
            break
except Exception:
    pass
" 2>/dev/null || true)"
    if [[ -n "$url" ]]; then
      echo "$url"
      return 0
    fi
    sleep 10
  done
  railway_cmd status --json 2>/dev/null | python3 -c "
import json,sys
d=json.load(sys.stdin)
print(d.get('url',''))
" 2>/dev/null || true
}

register_custom_domain() {
  log "Registering custom domain ${PLATFORM_DOMAIN} on Railway..."
  railway_cmd domain add "$PLATFORM_DOMAIN" --service "$API_SERVICE" 2>/dev/null || \
    railway_cmd domain --service "$API_SERVICE" 2>/dev/null || true
}

apply_cloudflare_cname() {
  local target="${1:-}"
  if [[ -z "$target" ]]; then
    log "WARN: no Railway CNAME target — set manually in Cloudflare"
    return 1
  fi
  log "Cloudflare CNAME ${PLATFORM_DOMAIN} → ${target}"
  PLATFORM_API_CNAME="$target" "$ROOT/scripts/setup-platform-api-dns.sh"
}

smoke_platform() {
  local base="${1:-https://${PLATFORM_DOMAIN}}"
  log "Platform smoke: ${base}"
  PLATFORM_HEALTH_BASE="$base" python3 "$ROOT/scripts/verify_platform_health.py"
}

main() {
  log "=== UPG-WWW-001 platform spine ==="
  command -v railway >/dev/null || { log "FAIL: railway CLI not installed"; exit 1; }
  railway_cmd whoami >/dev/null

  ensure_project
  ensure_data_services
  set_platform_variables
  deploy_api

  register_custom_domain
  local railway_url
  railway_url="$(wait_for_railway_url || true)"
  log "Railway service URL: ${railway_url:-pending}"

  # Railway custom domain verification target (often same as *.up.railway.app)
  local cname_target="${RAILWAY_PLATFORM_CNAME:-}"
  if [[ -z "$cname_target" && -n "$railway_url" ]]; then
    cname_target="${railway_url#https://}"
  fi
  apply_cloudflare_cname "$cname_target" || true

  log "Waiting 90s for DNS + deploy propagation..."
  sleep 90

  if smoke_platform "https://${PLATFORM_DOMAIN}"; then
    log "UPG-WWW-001 PASS — platform spine live at https://${PLATFORM_DOMAIN}"
    python3 "$ROOT/scripts/verify_chat_greeting_coupling.py" --live \
      --platform-base "https://${PLATFORM_DOMAIN}" || \
      log "WARN: live greeting coupling not yet green on platform"
    python3 "$ROOT/scripts/nf_post_deploy_verify.py" --surface platform || true
    log "Next: www chat will auto-proxy when PLATFORM_API_BASE resolves (no vercel rewrite needed)"
    exit 0
  fi

  if [[ -n "$railway_url" ]] && smoke_platform "$railway_url"; then
    log "Platform API healthy on Railway URL; DNS cutover may still propagate"
    log "Re-run: PLATFORM_API_CNAME=<railway-target> ./scripts/setup-platform-api-dns.sh"
    exit 0
  fi

  log "WARN: smoke not yet green — check railway logs"
  railway_cmd logs --service "$API_SERVICE" 2>&1 | tail -40 || true
  exit 2
}

main "$@"
