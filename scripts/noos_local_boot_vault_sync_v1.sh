#!/usr/bin/env bash
# local-boot vault sync — canonicalize + promote + conditional GHA/Railway push (ICL-P1-01 / UPG-PLAN-04)
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PLATFORM="${NOETFIELD_PLATFORM_SECRETS:-$HOME/.noetfield-platform-secrets}"
NOOS_ENV="${NOOS_LOCAL_ENV:-$PLATFORM/noos-local.env}"
MARKER="${PLATFORM}/.last-cloud-sync"
SYNC="${NOOS_BOOT_VAULT_SYNC:-auto}"

log() { printf '[local-boot-vault] %s\n' "$*"; }

[[ "$SYNC" == "0" || "$SYNC" == "skip" ]] && { log "SKIP (NOOS_BOOT_VAULT_SYNC=$SYNC)"; exit 0; }

python3 "$ROOT/scripts/canonicalize_noos_vault_v1.py" >/dev/null || log "WARN: vault canonicalize failed"
python3 "$ROOT/scripts/noos_promote_vault_keys_v1.py" >/dev/null || log "WARN: vault promote failed"

if ! command -v gh >/dev/null 2>&1; then
  log "SKIP cloud-secrets-sync — gh missing"
  exit 0
fi

if [[ ! -f "$NOOS_ENV" ]] || ! grep -qE '^CF_NOETFIELD_API_TOKEN=.+' "$NOOS_ENV" 2>/dev/null; then
  log "SKIP cloud-secrets-sync — no CF_NOETFIELD_API_TOKEN in $NOOS_ENV"
  exit 0
fi

need_sync=0
for f in "$NOOS_ENV" "${PLATFORM}/noetfield.env"; do
  [[ -f "$f" ]] || continue
  if [[ ! -f "$MARKER" ]] || [[ "$f" -nt "$MARKER" ]]; then
    need_sync=1
    break
  fi
done

if [[ "$SYNC" == "force" ]]; then
  need_sync=1
fi

if [[ "$need_sync" == "1" ]]; then
  log "vault dirty — cloud-secrets-sync"
  bash "$ROOT/scripts/noos_sync_cloud_secrets_v1.sh"
  mkdir -p "$PLATFORM"
  touch "$MARKER"
  log "OK — marked $MARKER"
else
  log "vault unchanged — skip cloud-secrets-sync"
fi
