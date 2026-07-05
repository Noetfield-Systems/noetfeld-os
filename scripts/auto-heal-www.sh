#!/usr/bin/env bash
# Auto-heal Noetfield www: one Vercel project, synced intake env, production deploy, health gate.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
# shellcheck source=scripts/www-vercel-canonical.sh
source "$ROOT/scripts/www-vercel-canonical.sh"

log() { printf '[auto-heal-www] %s\n' "$*"; }
fail() { log "FAIL: $*"; exit 1; }

HEAL_DRY_RUN="${HEAL_DRY_RUN:-0}"
HEAL_SKIP_DEPLOY="${HEAL_SKIP_DEPLOY:-0}"
HEAL_SKIP_DEDUP="${HEAL_SKIP_DEDUP:-0}"

vercel_cmd() {
  npx vercel "$@" --scope "$NF_VERCEL_SCOPE" --yes 2>&1
}

project_exists() {
  local name="$1"
  npx vercel project inspect "$name" --scope "$NF_VERCEL_SCOPE" >/dev/null 2>&1
}

dedupe_projects() {
  [[ "$HEAL_SKIP_DEDUP" == "1" ]] && { log "skip dedupe (HEAL_SKIP_DEDUP=1)"; return 0; }
  local dup
  for dup in web project-j43wr; do
    if project_exists "$dup"; then
      log "removing duplicate project: $dup"
      if [[ "$HEAL_DRY_RUN" == "1" ]]; then
        log "dry-run: would remove $dup"
      else
        printf 'y\n' | npx vercel project remove "$dup" --scope "$NF_VERCEL_SCOPE" --non-interactive 2>&1 || log "warn: could not remove $dup"
      fi
    fi
  done
}

ensure_canonical_link() {
  if [[ "$HEAL_DRY_RUN" == "1" ]]; then
    log "dry-run: would link to $NF_VERCEL_PROJECT"
    return 0
  fi
  rm -rf .vercel
  vercel_cmd link --project "$NF_VERCEL_PROJECT" >/dev/null
  log "linked repo → $NF_VERCEL_SCOPE/$NF_VERCEL_PROJECT"
}

read_vault() {
  local key="$1"
  if [[ ! -f "$NF_SECRETS_VAULT" ]]; then
    return 1
  fi
  local line
  line="$(grep -E "^${key}=" "$NF_SECRETS_VAULT" | tail -1 || true)"
  [[ -n "$line" ]] || return 1
  printf '%s' "${line#*=}" | tr -d '\r\n' | sed -e 's/^"//' -e 's/"$//'
}

env_complete() {
  local key list
  list="$(npx vercel env ls production --scope "$NF_VERCEL_SCOPE" 2>/dev/null || true)"
  for key in $NF_INTAKE_ENV_KEYS; do
    echo "$list" | grep -q "$key" || return 1
  done
  return 0
}

sync_intake_env() {
  [[ "${HEAL_SKIP_ENV:-0}" == "1" ]] && { log "skip env (HEAL_SKIP_ENV=1)"; return 0; }
  if env_complete; then
    log "intake env complete on production — skip sync"
    return 0
  fi
  local key val
  for key in $NF_INTAKE_ENV_KEYS; do
    val="$(read_vault "$key" 2>/dev/null || true)"
    if [[ -z "$val" ]]; then
      if [[ "$key" == "INTAKE_AUTO_ACK_ENABLED" ]]; then
        val="true"
      elif [[ "$key" == "INTAKE_EMAIL_TO" ]]; then
        val="operations@noetfield.com"
      elif [[ "$key" == "INTAKE_EMAIL_FROM" ]]; then
        val="Noetfield Intake <notifications@noetfield.com>"
      elif [[ "$key" == "TELEGRAM_OPS_CHAT_ID" ]]; then
        val="8635650894"
      else
        log "warn: $key missing in $NF_SECRETS_VAULT — skip"
        continue
      fi
    fi
    if [[ "$HEAL_DRY_RUN" == "1" ]]; then
      log "dry-run: would set $key on production"
      continue
    fi
    log "sync env: $key"
    npx vercel env add "$key" production \
      --scope "$NF_VERCEL_SCOPE" \
      --force --yes --value "$val" >/dev/null 2>&1 || log "warn: env sync $key (may already match)"
  done
}

deploy_production() {
  [[ "$HEAL_SKIP_DEPLOY" == "1" ]] && { log "skip deploy (HEAL_SKIP_DEPLOY=1)"; return 0; }
  [[ "$HEAL_DRY_RUN" == "1" ]] && { log "dry-run: would deploy production"; return 0; }
  log "deploying production…"
  vercel_cmd --prod
}

canonical_deploy_url() {
  local url
  url="$(npx vercel project ls --scope "$NF_VERCEL_SCOPE" 2>&1 \
    | grep 'https://' \
    | awk -v p="$NF_VERCEL_PROJECT" '$1==p {print $2; exit}')"
  # Prefer stable alias with intake env; team default URL may sit behind Vercel auth.
  if [[ -z "$url" ]] || [[ "$url" == *"-noetfield-systems.vercel.app" ]]; then
    url="${NF_WWW_DEPLOY_URL:-https://www.noetfield.com}"
  fi
  printf '%s' "$url"
}

check_health() {
  local base="$1"
  local label="$2"
  local url="${base%/}/api/intake/health"
  log "health: $label ($url)"
  local body ok
  body="$(curl -sS --max-time 20 "$url" || echo '{}')"
  ok="$(printf '%s' "$body" | python3 -c "
import json, sys
try:
    h = json.load(sys.stdin)
except Exception:
    print('0'); sys.exit(0)
www = h.get('www_email_configured') is True
mode = h.get('delivery_mode') == 'resend'
print('1' if www and mode else '0')
" 2>/dev/null || echo "0")"
  printf '%s' "$body" | python3 -m json.tool 2>/dev/null || printf '%s\n' "$body"
  [[ "$ok" == "1" ]]
}

alias_live_domain() {
  [[ "$HEAL_DRY_RUN" == "1" ]] && return 0
  local deploy_url
  deploy_url="$(canonical_deploy_url)"
  log "attempt alias $NF_WWW_LIVE_DOMAIN → $deploy_url"
  if npx vercel alias set "$deploy_url" "$NF_WWW_LIVE_DOMAIN" --scope "$NF_VERCEL_SCOPE" 2>&1; then
    log "alias ok: $NF_WWW_LIVE_DOMAIN"
    return 0
  fi
  log "alias blocked — domain not under $NF_VERCEL_SCOPE (attach in Vercel dashboard → Domains)"
  return 1
}

main() {
  log "start — canonical $NF_VERCEL_SCOPE/$NF_VERCEL_PROJECT"

  if ! project_exists "$NF_VERCEL_PROJECT" && project_exists "project-gc7lm"; then
    log "renaming project-gc7lm → $NF_VERCEL_PROJECT"
    [[ "$HEAL_DRY_RUN" != "1" ]] && npx vercel project rename project-gc7lm "$NF_VERCEL_PROJECT" --scope "$NF_VERCEL_SCOPE" 2>&1
  fi

  dedupe_projects

  if ! project_exists "$NF_VERCEL_PROJECT"; then
    fail "canonical project $NF_VERCEL_PROJECT missing — deploy once: npx vercel link --project $NF_VERCEL_PROJECT"
  fi

  ensure_canonical_link
  sync_intake_env
  deploy_production

  local canon_url ok_canon ok_live=1
  canon_url="$(canonical_deploy_url)"
  check_health "$canon_url" "canonical" || fail "canonical deploy intake not configured ($canon_url)"

  alias_live_domain || true

  if check_health "$NF_WWW_CANONICAL_URL" "live www"; then
    log "PASS — $NF_WWW_CANONICAL_URL intake healthy"
  else
    log "WARN — live domain still fragmented (different Vercel owner or missing alias)"
    log "FIX — Vercel dashboard: move $NF_WWW_LIVE_DOMAIN to $NF_VERCEL_SCOPE/$NF_VERCEL_PROJECT"
    ok_live=0
  fi

  [[ "$ok_live" == "1" ]] && log "auto-heal complete" || exit 2
}

main "$@"
