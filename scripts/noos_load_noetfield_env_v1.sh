#!/usr/bin/env bash
# noos_load_noetfield_env_v1.sh — read KEY=value lines only (skip comments / malformed rows)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/noos_resolve_local_env_v1.sh"

noos_env_get() {
  local key="$1" file="$2"
  [[ -f "$file" ]] || return 1
  grep -E "^${key}=" "$file" 2>/dev/null | head -1 | cut -d= -f2- | sed -e 's/^"//' -e 's/"$//'
}

noos_load_noetfield_env() {
  local explicit="${1:-}"
  export CLOUDFLARE_API_TOKEN
  export CF_NOETFIELD_API_TOKEN
  export NOOS_LOOP_SECRET
  export NOETFIELD_SUPABASE_URL
  export NOETFIELD_SUPABASE_SERVICE_ROLE_KEY
  export SUPABASE_URL
  export SUPABASE_SERVICE_ROLE_KEY

  local -a files=()
  if [[ -n "$explicit" ]]; then
    files+=("$explicit")
  else
    [[ -f "$NOOS_LOCAL_ENV" ]] && files+=("$NOOS_LOCAL_ENV")
    [[ -f "$NOETFIELD_LOCAL_ENV" ]] && files+=("$NOETFIELD_LOCAL_ENV")
  fi

  for file in "${files[@]}"; do
    CLOUDFLARE_API_TOKEN="${CLOUDFLARE_API_TOKEN:-$(noos_env_get CLOUDFLARE_API_TOKEN "$file" || true)}"
    CF_NOETFIELD_API_TOKEN="${CF_NOETFIELD_API_TOKEN:-$(noos_env_get CF_NOETFIELD_API_TOKEN "$file" || true)}"
    NOOS_LOOP_SECRET="${NOOS_LOOP_SECRET:-$(noos_env_get NOOS_LOOP_SECRET "$file" || true)}"
    NOETFIELD_SUPABASE_URL="${NOETFIELD_SUPABASE_URL:-$(noos_env_get NOETFIELD_SUPABASE_URL "$file" || true)}"
    NOETFIELD_SUPABASE_SERVICE_ROLE_KEY="${NOETFIELD_SUPABASE_SERVICE_ROLE_KEY:-$(noos_env_get NOETFIELD_SUPABASE_SERVICE_ROLE_KEY "$file" || true)}"
    SUPABASE_URL="${SUPABASE_URL:-$(noos_env_get SUPABASE_URL "$file" || true)}"
    SUPABASE_SERVICE_ROLE_KEY="${SUPABASE_SERVICE_ROLE_KEY:-$(noos_env_get SUPABASE_SERVICE_ROLE_KEY "$file" || true)}"
  done

  CLOUDFLARE_API_TOKEN="${CF_NOETFIELD_API_TOKEN:-${CLOUDFLARE_API_TOKEN:-}}"
}
