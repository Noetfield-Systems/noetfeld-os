#!/usr/bin/env bash
# Deploy nf-probe-cron worker — 15-min uptime/greeting/drift/intake probes → Supabase + Telegram.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VAULT="${NF_SECRETS_VAULT:-$HOME/.sina/secrets.env}"
WORKER_DIR="$ROOT/infra/nf-probe-cron"

read_vault() {
  local key="$1"
  [[ -f "$VAULT" ]] || return 1
  grep -E "^${key}=" "$VAULT" | tail -1 | cut -d= -f2- | tr -d '\r\n' | sed -e 's/^"//' -e 's/"$//'
}

log() { printf '[deploy-nf-probe-cron] %s\n' "$*"; }

sync_secret() {
  local key="$1"
  local val="$2"
  [[ -n "$val" ]] || { log "WARN: ${key} missing — skip"; return 0; }
  log "secret ${key}"
  cd "$WORKER_DIR"
  printf '%s' "$val" | wrangler secret put "$key" >/dev/null
}

GIT_SHA="$(git -C "$ROOT" rev-parse HEAD 2>/dev/null || true)"
LIVE_PLATFORM_SHA="$(curl -sS "${PLATFORM_BASE:-https://platform.noetfield.com}/api/public/chat/health" 2>/dev/null | python3 -c "import json,sys; print(json.load(sys.stdin).get('git_sha',''))" 2>/dev/null || true)"
if [[ -n "$GIT_SHA" && -n "$LIVE_PLATFORM_SHA" && "$LIVE_PLATFORM_SHA" != "$GIT_SHA" && "${LIVE_PLATFORM_SHA:0:12}" != "${GIT_SHA:0:12}" ]]; then
  log "NOTE: platform git_sha=${LIVE_PLATFORM_SHA:0:12} may lag repo HEAD=${GIT_SHA:0:12} — drift probe uses live platform pin, not HEAD"
fi

# shellcheck source=scripts/load_noetfield_vault_env.sh
source "${ROOT}/scripts/load_noetfield_vault_env.sh"
# shellcheck source=scripts/read_platform_vault.sh
source "${ROOT}/scripts/read_platform_vault.sh"

bash "$ROOT/scripts/sync_nf_probe_expected_sha.sh" || log "WARN: probe expected SHA sync skipped"
EXPECTED_SHA="$(python3 "$ROOT/scripts/read_nf_platform_expected_sha.py" 2>/dev/null || true)"

SUPABASE_URL="${NOETFIELD_SUPABASE_URL:-}"
SUPABASE_SERVICE="${NOETFIELD_SUPABASE_SERVICE_ROLE_KEY:-}"
TELEGRAM_TOKEN="$(read_platform_vault TELEGRAM_NOETFIELD_OPS_BOT_TOKEN 2>/dev/null || read_platform_vault TELEGRAM_BOT_TOKEN 2>/dev/null || true)"
TELEGRAM_CHAT="$(read_platform_vault TELEGRAM_OPS_CHAT_ID 2>/dev/null || true)"
[[ -n "$TELEGRAM_CHAT" ]] || TELEGRAM_CHAT="8635650894"

log "deploy nf-probe-cron from ${WORKER_DIR}"
cd "$WORKER_DIR"

if [[ "${NF_PROBE_CRON_FORCE_TOKEN:-0}" == "1" ]]; then
  :
else
  unset CLOUDFLARE_API_TOKEN CF_API_TOKEN
fi

wrangler deploy

sync_secret "SUPABASE_URL" "$SUPABASE_URL"
sync_secret "SUPABASE_SERVICE_ROLE_KEY" "$SUPABASE_SERVICE"
sync_secret "TELEGRAM_NOETFIELD_OPS_BOT_TOKEN" "$TELEGRAM_TOKEN"
sync_secret "TELEGRAM_OPS_CHAT_ID" "$TELEGRAM_CHAT"
# sync_nf_probe_expected_sha.sh already updated wrangler.toml + secret when token present.

log "bootstrap recovery telegram on next green probe run"
cd "$WORKER_DIR"
printf '1' | wrangler secret put PROBE_BOOTSTRAP_RECOVERY >/dev/null 2>&1 || true
if curl -fsS -X POST "https://nf-probe-cron.sina-kazemnezhad-ca.workers.dev/run" >/tmp/nf-probe-run.json 2>/dev/null; then
  python3 -c "import json; d=json.load(open('/tmp/nf-probe-run.json')); print('probe_run ok=', d.get('ok'))"
fi
printf '0' | wrangler secret put PROBE_BOOTSTRAP_RECOVERY >/dev/null 2>&1 || true

log "PASS — nf-probe-cron deployed (expected platform sha=${EXPECTED_SHA:0:12})"
log "manual smoke: wrangler tail nf-probe-cron — or POST /run on workers.dev URL after deploy"
