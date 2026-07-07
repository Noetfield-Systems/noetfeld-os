#!/usr/bin/env bash
# One-shot: move NOOS keys out of ~/.sourcea-secrets into ~/.noetfield-platform-secrets/
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck disable=SC1091
source "$ROOT/scripts/noos_resolve_local_env_v1.sh"
# shellcheck disable=SC1091
source "$ROOT/scripts/noos_load_noetfield_env_v1.sh"

LEGACY="${MIGRATE_FROM:-$HOME/.sourcea-secrets/noetfield.env}"
log() { printf '[migrate-noos-vault] %s\n' "$*"; }

[[ -f "$LEGACY" ]] || { log "SKIP: no legacy file at $LEGACY"; exit 0; }

mkdir -p "$NOETFIELD_PLATFORM_SECRETS"
touch "$NOOS_LOCAL_ENV" "$NOETFIELD_LOCAL_ENV"

upsert_key() {
  local file="$1" key="$2" value="$3"
  [[ -n "$value" ]] || return 0
  local tmp
  tmp="$(mktemp)"
  if [[ -f "$file" ]]; then
    grep -v -E "^${key}=" "$file" >"$tmp" || true
  else
    : >"$tmp"
  fi
  printf '%s=%s\n' "$key" "$value" >>"$tmp"
  mv "$tmp" "$file"
}

noos_keys=(CLOUDFLARE_API_TOKEN CF_NOETFIELD_API_TOKEN CF_NOETFIELD_ZONE_ID NOOS_LOOP_SECRET)
product_keys=(NOETFIELD_SUPABASE_URL NOETFIELD_SUPABASE_ANON_KEY NOETFIELD_SUPABASE_SERVICE_ROLE_KEY
  NOETFIELD_SUPABASE_REF SUPABASE_URL SUPABASE_ANON_KEY SUPABASE_SERVICE_ROLE_KEY SUPABASE_PROJECT_ID
  INTAKE_AUTO_ACK_ENABLED INTAKE_EMAIL_FROM INTAKE_EMAIL_TO RESEND_API_KEY)

for key in "${noos_keys[@]}"; do
  val="$(noos_env_get "$key" "$LEGACY" || true)"
  upsert_key "$NOOS_LOCAL_ENV" "$key" "$val"
done

for key in "${product_keys[@]}"; do
  val="$(noos_env_get "$key" "$LEGACY" || true)"
  upsert_key "$NOETFIELD_LOCAL_ENV" "$key" "$val"
done

log "OK — NOOS keys → $NOOS_LOCAL_ENV"
log "OK — Noetfield product keys → $NOETFIELD_LOCAL_ENV"
log "Legacy $LEGACY left untouched (remove NOOS keys manually when ready)"
