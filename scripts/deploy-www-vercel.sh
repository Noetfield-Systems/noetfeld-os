#!/usr/bin/env bash
# Production deploy www.noetfield.com → Vercel project the-777-foundation/noetfield
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
# shellcheck source=scripts/www-vercel-canonical.sh
source "$ROOT/scripts/www-vercel-canonical.sh"

log() { printf '[deploy-www-vercel] %s\n' "$*"; }

log "scope=$NF_VERCEL_SCOPE project=$NF_VERCEL_PROJECT"

log "sync chat greeting SSOT asset…"
python3 scripts/sync_chat_greeting_asset.py
python3 scripts/verify_chat_greeting_coupling.py

sync_telegram_env() {
  local key val
  for key in TELEGRAM_NOETFIELD_OPS_BOT_TOKEN TELEGRAM_OPS_CHAT_ID; do
    val="$(grep -E "^${key}=" "$NF_SECRETS_VAULT" 2>/dev/null | tail -1 | cut -d= -f2- | tr -d '"' || true)"
    if [[ -z "$val" && "$key" == "TELEGRAM_OPS_CHAT_ID" ]]; then
      val="8635650894"
    fi
    [[ -n "$val" ]] || { log "WARN: ${key} missing in vault — skip"; continue; }
    log "sync env: ${key}"
    npx vercel env add "$key" production --scope "$NF_VERCEL_SCOPE" --force --yes --value "$val" >/dev/null 2>&1 || \
      log "WARN: env sync ${key} (may already match)"
  done
}

if [[ ! -d .vercel ]] || ! grep -q '"projectName": "noetfield"' .vercel/project.json 2>/dev/null; then
  rm -rf .vercel
  npx vercel link --project "$NF_VERCEL_PROJECT" --scope "$NF_VERCEL_SCOPE" --yes
fi

sync_telegram_env

npx vercel deploy --prod --scope "$NF_VERCEL_SCOPE" --yes

log "health check…"
curl -sS "${NF_WWW_CANONICAL_URL}/health"
echo
curl -sS "${NF_WWW_CANONICAL_URL}/api/intake/health" | python3 -m json.tool 2>/dev/null || true
python3 scripts/nf_post_deploy_verify.py --surface www || true
log "done — ${NF_WWW_CANONICAL_URL}"
