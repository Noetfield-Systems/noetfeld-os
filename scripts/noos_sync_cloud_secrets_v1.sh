#!/usr/bin/env bash
# noos_sync_cloud_secrets_v1.sh — ~/.noetfield-platform-secrets → GHA + Railway
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck disable=SC1091
source "$ROOT/scripts/noos_resolve_local_env_v1.sh"
REPO="${GITHUB_REPO:-Noetfield-Systems/noetfeld-os}"

log() { printf '[noos-sync-cloud] %s\n' "$*"; }

python3 "$ROOT/scripts/canonicalize_noos_vault_v1.py" >/dev/null
python3 "$ROOT/scripts/noos_promote_vault_keys_v1.py"

if ! python3 "$ROOT/scripts/verify_noos_cf_deploy_token_v1.py" >/dev/null; then
  log "FAIL: CF token verify failed — fix CF_NOETFIELD_API_TOKEN before GHA sync"
  python3 "$ROOT/scripts/verify_noos_cf_deploy_token_v1.py" || true
  exit 1
fi

# shellcheck disable=SC1091
source "$ROOT/scripts/noos_load_noetfield_env_v1.sh"
noos_load_noetfield_env
[[ -n "${CLOUDFLARE_API_TOKEN:-}" ]] || { log "FAIL: set CF_NOETFIELD_API_TOKEN in $NOOS_LOCAL_ENV"; exit 1; }
[[ -n "${NOETFIELD_SUPABASE_URL:-${SUPABASE_URL:-}}" ]] || {
  log "FAIL: set NOETFIELD_SUPABASE_URL in $NOETFIELD_LOCAL_ENV"; exit 1;
}

if command -v gh >/dev/null 2>&1; then
  log "GHA secret CLOUDFLARE_API_TOKEN → $REPO"
  printf '%s' "$CLOUDFLARE_API_TOKEN" | gh secret set CLOUDFLARE_API_TOKEN --repo "$REPO"
  if [[ -n "${NOOS_LOOP_SECRET:-}" ]]; then
    log "GHA secret NOOS_LOOP_SECRET → $REPO"
    printf '%s' "$NOOS_LOOP_SECRET" | gh secret set NOOS_LOOP_SECRET --repo "$REPO"
  fi
  if [[ -n "${NOETFIELD_SUPABASE_URL:-}" ]]; then
    printf '%s' "$NOETFIELD_SUPABASE_URL" | gh secret set NOETFIELD_SUPABASE_URL --repo "$REPO" 2>/dev/null || true
  fi
  if [[ -n "${NOETFIELD_SUPABASE_SERVICE_ROLE_KEY:-}" ]]; then
    printf '%s' "$NOETFIELD_SUPABASE_SERVICE_ROLE_KEY" | gh secret set NOETFIELD_SUPABASE_SERVICE_ROLE_KEY --repo "$REPO" 2>/dev/null || true
  fi
  PORTFOLIO_ENV="${PORTFOLIO_SPINE_ENV:-$HOME/.sourcea-secrets/portfolio-spine.env}"
  if [[ -f "$PORTFOLIO_ENV" ]]; then
    # shellcheck disable=SC1090
    source "$PORTFOLIO_ENV"
    PS_URL="${PORTFOLIO_SPINE_SUPABASE_URL:-${SUPABASE_URL:-}}"
    PS_KEY="${PORTFOLIO_SPINE_SERVICE_ROLE_KEY:-${SUPABASE_SERVICE_ROLE_KEY:-${SUPABASE_SERVICE_KEY:-}}}"
    if [[ -n "$PS_URL" ]]; then
      log "GHA secret PORTFOLIO_SPINE_SUPABASE_URL → $REPO (dedicated — not SUPABASE_URL)"
      printf '%s' "$PS_URL" | gh secret set PORTFOLIO_SPINE_SUPABASE_URL --repo "$REPO"
    fi
    if [[ -n "$PS_KEY" ]]; then
      log "GHA secret PORTFOLIO_SPINE_SERVICE_ROLE_KEY → $REPO (dedicated — not shared generic key)"
      printf '%s' "$PS_KEY" | gh secret set PORTFOLIO_SPINE_SERVICE_ROLE_KEY --repo "$REPO"
    fi
  else
    log "WARN: portfolio spine env missing — $PORTFOLIO_ENV (spine witness stays yellow on GHA)"
  fi
  TF_REPO="${TRUSTFIELD_GITHUB_REPO:-Noetfield-Systems/TrustField-Technologies}"
  if [[ -n "${NOETFIELD_SUPABASE_URL:-}" ]]; then
    log "GHA secret NOETFIELD_SUPABASE_URL → $TF_REPO"
    printf '%s' "$NOETFIELD_SUPABASE_URL" | gh secret set NOETFIELD_SUPABASE_URL --repo "$TF_REPO" 2>/dev/null || true
    printf '%s' "$NOETFIELD_SUPABASE_URL" | gh secret set SUPABASE_URL --repo "$TF_REPO" 2>/dev/null || true
  fi
  if [[ -n "${NOETFIELD_SUPABASE_SERVICE_ROLE_KEY:-}" ]]; then
    log "GHA secret NOETFIELD_SUPABASE_SERVICE_ROLE_KEY → $TF_REPO"
    printf '%s' "$NOETFIELD_SUPABASE_SERVICE_ROLE_KEY" | gh secret set NOETFIELD_SUPABASE_SERVICE_ROLE_KEY --repo "$TF_REPO" 2>/dev/null || true
    printf '%s' "$NOETFIELD_SUPABASE_SERVICE_ROLE_KEY" | gh secret set SUPABASE_SERVICE_ROLE_KEY --repo "$TF_REPO" 2>/dev/null || true
  fi
  log "GHA secrets synced"
else
  log "WARN: gh CLI missing — skip GHA secret sync"
fi

if [[ -x "${RAILWAY_BIN:-$HOME/.railway/bin/railway}" || -x "$(command -v railway 2>/dev/null || true)" ]]; then
  bash "$ROOT/scripts/sync_railway_loop_runner_env_v1.sh"
else
  log "WARN: railway CLI missing — skip Railway env sync"
fi

log "OK cloud secrets bootstrap complete"
