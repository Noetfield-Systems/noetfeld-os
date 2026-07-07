#!/usr/bin/env bash
# One-shot: push Noetfield Supabase keys from ~/.sourcea-secrets/ → GitHub Actions secrets.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO="${GITHUB_REPO:-Noetfield-Systems/Noetfield}"

# shellcheck source=scripts/load_noetfield_vault_env.sh
source "${ROOT}/scripts/load_noetfield_vault_env.sh"

log() { printf '[sync-noetfield-gh-secrets] %s\n' "$*"; }
die() { log "FAIL: $*"; exit 1; }

command -v gh >/dev/null 2>&1 || die "gh CLI required"

sync_secret() {
  local name="$1" value="$2"
  [[ -n "$value" ]] || { log "SKIP ${name} (empty in vault)"; return 0; }
  printf '%s' "$value" | gh secret set "$name" -R "$REPO"
  log "OK ${name}"
}

[[ -n "${NOETFIELD_SUPABASE_URL:-}" ]] || die "NOETFIELD_SUPABASE_URL missing — check ~/.noetfield-platform-secrets/noetfield.env"

sync_secret NOETFIELD_SUPABASE_URL "${NOETFIELD_SUPABASE_URL}"
sync_secret NOETFIELD_SUPABASE_SERVICE_ROLE_KEY "${NOETFIELD_SUPABASE_SERVICE_ROLE_KEY:-}"
sync_secret NOETFIELD_SUPABASE_ANON_KEY "${NOETFIELD_SUPABASE_ANON_KEY:-}"
sync_secret NOETFIELD_SUPABASE_DATABASE_URL "${NOETFIELD_SUPABASE_DATABASE_URL:-}"

log "done — repo ${REPO} (workflows: repo-health-daily, security-sweep-weekly, supabase-heartbeat)"
