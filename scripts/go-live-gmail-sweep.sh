#!/usr/bin/env bash
# Go-live Gmail sweep + Signal Factory triage on Railway platform API.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

# shellcheck source=scripts/read_platform_vault.sh
source "${ROOT}/scripts/read_platform_vault.sh"
# shellcheck source=scripts/load_noetfield_vault_env.sh
source "${ROOT}/scripts/load_noetfield_vault_env.sh"

API_SERVICE="${RAILWAY_API_SERVICE:-platform-api}"

log() { printf '[go-live-gmail-sweep] %s\n' "$*"; }

railway_cmd() {
  RAILWAY_CALLER="skill:use-railway" RAILWAY_AGENT_SESSION="${RAILWAY_AGENT_SESSION:-go-live-gmail-$$}" \
    railway "$@"
}

apply_migrations() {
  local db_url="${DATABASE_URL:-${NOETFIELD_SUPABASE_DATABASE_URL:-}}"
  if [[ -z "$db_url" ]]; then
    db_url="$(read_platform_vault DATABASE_URL 2>/dev/null || read_platform_vault NOETFIELD_SUPABASE_DATABASE_URL 2>/dev/null || true)"
  fi
  if [[ -z "$db_url" ]]; then
    log "WARN: no DATABASE_URL — skip migration apply"
    return 0
  fi
  log "Applying Postgres migrations…"
  DATABASE_URL="$db_url" python3 scripts/apply_postgres_migrations.py
}

sync_railway_env() {
  log "Vault status:"
  platform_vault_status | python3 -m json.tool

  log "Syncing Railway env on service ${API_SERVICE}…"
  local gmail_app_pw tg_token tg_chat admin_secret
  gmail_app_pw="$(read_gmail_app_password 2>/dev/null || true)"
  tg_token="$(read_platform_vault TELEGRAM_NOETFIELD_OPS_BOT_TOKEN 2>/dev/null || read_platform_vault TELEGRAM_BOT_TOKEN 2>/dev/null || true)"
  tg_chat="$(read_platform_vault TELEGRAM_OPS_CHAT_ID 2>/dev/null || true)"
  admin_secret="$(read_platform_vault ADMIN_DASHBOARD_SECRET 2>/dev/null || true)"

  local sweep_enabled="false" triage_enabled="false"
  if [[ -n "$gmail_app_pw" ]]; then
    sweep_enabled="true"
    triage_enabled="true"
    railway_cmd variable set --service "$API_SERVICE" --skip-deploys GMAIL_APP_PASSWORD="$gmail_app_pw"
    railway_cmd variable set --service "$API_SERVICE" --skip-deploys NF_OPERATIONS_GOOGLE_WORKSPACE_APP_PASSWORD="$gmail_app_pw"
    log "OK GMAIL_APP_PASSWORD (IMAP)"
  else
    log "WARN: NF_OPERATIONS_GOOGLE_WORKSPACE_APP_PASSWORD missing — sweep stays disabled"
  fi

  if [[ -n "$tg_token" && -n "$tg_chat" ]]; then
    triage_enabled="true"
    railway_cmd variable set --service "$API_SERVICE" --skip-deploys TELEGRAM_NOETFIELD_OPS_BOT_TOKEN="$tg_token"
    railway_cmd variable set --service "$API_SERVICE" --skip-deploys TELEGRAM_BOT_TOKEN="$tg_token"
    railway_cmd variable set --service "$API_SERVICE" --skip-deploys TELEGRAM_OPS_CHAT_ID="$tg_chat"
    log "OK Telegram ops bot + chat"
  else
    log "WARN: TELEGRAM_NOETFIELD_OPS_BOT_TOKEN or TELEGRAM_OPS_CHAT_ID missing"
  fi

  railway_cmd variable set --service "$API_SERVICE" --skip-deploys \
    GMAIL_SWEEP_ENABLED="$sweep_enabled" \
    GMAIL_MAILBOX="${GMAIL_MAILBOX:-operations@noetfield.com}" \
    GMAIL_PROCESSED_LABEL="${GMAIL_PROCESSED_LABEL:-nf-processed}" \
    OPERATIONS_INBOX_TENANT_ID="${OPERATIONS_INBOX_TENANT_ID:-00000000-0000-4000-8000-000000000001}" \
    OPERATIONS_INBOX_ORGANIZATION_ID="${OPERATIONS_INBOX_ORGANIZATION_ID:-00000000-0000-4000-8000-000000000002}" \
    SIGNAL_TRIAGE_ENABLED="$triage_enabled" \
    SIGNAL_TRIAGE_INTERVAL_SEC="${SIGNAL_TRIAGE_INTERVAL_SEC:-120}"

  [[ -n "$admin_secret" ]] && railway_cmd variable set --service "$API_SERVICE" --skip-deploys ADMIN_DASHBOARD_SECRET="$admin_secret"

  log "GMAIL_SWEEP_ENABLED=$sweep_enabled SIGNAL_TRIAGE_ENABLED=$triage_enabled"
}

smoke_live() {
  local base="${PLATFORM_API_BASE:-https://platform.noetfield.com}"
  log "Health: ${base}/api/operations/gmail/sweep/health"
  curl -fsS "${base}/api/operations/gmail/sweep/health" | python3 -m json.tool || true
  log "Health: ${base}/api/operations/signal-triage/health"
  curl -fsS "${base}/api/operations/signal-triage/health" | python3 -m json.tool || true
}

main() {
  apply_migrations
  sync_railway_env
  if [[ "${DEPLOY_AFTER_SYNC:-1}" == "1" ]]; then
    log "Redeploying platform API…"
    railway_cmd up --service "$API_SERVICE" -d -y
    log "Waiting 90s for deploy…"
    sleep 90
  fi
  smoke_live
  log "Manual sweep: python3 scripts/run_gmail_sweep.py"
  log "Manual triage: python3 scripts/run_signal_triage.py"
}

main "$@"
