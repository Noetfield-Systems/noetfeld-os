#!/usr/bin/env bash
# Load Noetfield Supabase keys: ~/.sourcea-secrets/noetfield.env (primary), sina fallback.
# Usage: source scripts/load_noetfield_vault_env.sh
set -euo pipefail

NOETFIELD_VAULT="${HOME}/.sourcea-secrets/noetfield.env"
NOETFIELD_DB_VAULT="${HOME}/.sourcea-secrets/noetfield-db.env"
SINA_VAULT="${NF_SECRETS_VAULT:-${HOME}/.sina/secrets.env}"

_nf_vault_read() {
  local file="$1" key="$2"
  [[ -f "$file" ]] || return 1
  grep -E "^${key}=" "$file" 2>/dev/null | tail -1 | cut -d= -f2- | tr -d '\r' | sed -e 's/^"//' -e 's/"$//'
}

_nf_vault_apply() {
  local canonical="$1"
  shift
  [[ -n "${!canonical:-}" ]] && return 0
  local key val
  for key in "$canonical" "$@"; do
    val="$(_nf_vault_read "$NOETFIELD_VAULT" "$key" || true)"
    [[ -z "$val" ]] && val="$(_nf_vault_read "$NOETFIELD_DB_VAULT" "$key" || true)"
    [[ -z "$val" ]] && val="$(_nf_vault_read "$SINA_VAULT" "$key" || true)"
    if [[ -n "$val" ]]; then
      export "${canonical}=${val}"
      return 0
    fi
  done
}

if [[ -f "$NOETFIELD_VAULT" ]]; then
  # shellcheck disable=SC1090
  set -a && source "$NOETFIELD_VAULT" && set +a
fi

ADMIN_VAULT="${HOME}/.sourcea-secrets/noetfield-admin-dashboard.env"
if [[ -f "$ADMIN_VAULT" ]]; then
  # shellcheck disable=SC1090
  set -a && source "$ADMIN_VAULT" && set +a
fi

_nf_vault_apply NOETFIELD_SUPABASE_URL SUPABASE_URL
_nf_vault_apply NOETFIELD_SUPABASE_ANON_KEY SUPABASE_ANON_KEY
_nf_vault_apply NOETFIELD_SUPABASE_SERVICE_ROLE_KEY SUPABASE_SERVICE_ROLE_KEY
_nf_vault_apply NOETFIELD_SUPABASE_DATABASE_URL SUPABASE_DATABASE_URL

if [[ -z "${NOETFIELD_SUPABASE_URL:-}" && -n "${NOETFIELD_SUPABASE_REF:-}" ]]; then
  export NOETFIELD_SUPABASE_URL="https://${NOETFIELD_SUPABASE_REF}.supabase.co"
fi

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  printf 'noetfield vault: URL=%s service=%s anon=%s db=%s\n' \
    "$( [[ -n "${NOETFIELD_SUPABASE_URL:-}" ]] && echo set || echo missing )" \
    "$( [[ -n "${NOETFIELD_SUPABASE_SERVICE_ROLE_KEY:-}" ]] && echo set || echo missing )" \
    "$( [[ -n "${NOETFIELD_SUPABASE_ANON_KEY:-}" ]] && echo set || echo missing )" \
    "$( [[ -n "${NOETFIELD_SUPABASE_DATABASE_URL:-}" ]] && echo set || echo missing )"
fi
