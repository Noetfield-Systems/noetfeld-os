#!/usr/bin/env bash
# SSOT: read Noetfield platform secrets from canonical vault files (not chat memory).
# Order: admin-dashboard → ~/.noetfield-platform-secrets → legacy symlinks → ~/.sina/secrets.env
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

PLATFORM_SECRETS="${NOETFIELD_PLATFORM_SECRETS:-$HOME/.noetfield-platform-secrets}"

PLATFORM_VAULT_FILES=(
  "${HOME}/.sourcea-secrets/noetfield-admin-dashboard.env"
  "${PLATFORM_SECRETS}/noetfield.env"
  "${PLATFORM_SECRETS}/noetfield-db.env"
  "${HOME}/.sourcea-secrets/noetfield.env"
  "${HOME}/.sourcea-secrets/noetfield-db.env"
  "${NF_SECRETS_VAULT:-${HOME}/.sina/secrets.env}"
)

read_platform_vault() {
  local key="$1"
  local file val
  for file in "${PLATFORM_VAULT_FILES[@]}"; do
    [[ -f "$file" ]] || continue
    val="$(grep -E "^${key}=" "$file" 2>/dev/null | tail -1 | cut -d= -f2- | tr -d '\r' | sed -e 's/^"//' -e 's/"$//')"
    if [[ -n "$val" ]]; then
      printf '%s' "$val"
      return 0
    fi
  done
  return 1
}

read_gmail_app_password() {
  for key in GMAIL_APP_PASSWORD NF_OPERATIONS_GOOGLE_WORKSPACE_APP_PASSWORD; do
    local val
    val="$(read_platform_vault "$key" 2>/dev/null || true)"
    if [[ -n "$val" ]]; then
      printf '%s' "$val"
      return 0
    fi
  done
  return 1
}

platform_vault_status() {
  python3 - <<'PY' "${PLATFORM_VAULT_FILES[@]}"
import json, os, sys
from pathlib import Path

keys = [
    "ADMIN_DASHBOARD_SECRET",
    "GMAIL_APP_PASSWORD",
    "NF_OPERATIONS_GOOGLE_WORKSPACE_APP_PASSWORD",
    "TELEGRAM_NOETFIELD_OPS_BOT_TOKEN",
    "TELEGRAM_BOT_TOKEN",
    "TELEGRAM_OPS_CHAT_ID",
    "NOETFIELD_SUPABASE_DATABASE_URL",
    "DATABASE_URL",
    "RESEND_API_KEY",
    "OPENROUTER_API_KEY",
]
files = sys.argv[1:]

def parse(path: Path) -> dict[str, str]:
    if not path.is_file():
        return {}
    out: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        out[k.strip()] = v.strip().strip('"').strip("'")
    return out

merged: dict[str, str] = {}
for f in files:
    merged.update(parse(Path(f)))

gmail_app = bool(
    merged.get("GMAIL_APP_PASSWORD") or merged.get("NF_OPERATIONS_GOOGLE_WORKSPACE_APP_PASSWORD")
)

tg = merged.get("TELEGRAM_NOETFIELD_OPS_BOT_TOKEN") or merged.get("TELEGRAM_BOT_TOKEN")
print(
    json.dumps(
        {
            "vault_files": {Path(f).name: Path(f).is_file() for f in files},
            "resolved": {
                "ADMIN_DASHBOARD_SECRET": bool(merged.get("ADMIN_DASHBOARD_SECRET")),
                "GMAIL_APP_PASSWORD": gmail_app,
                "TELEGRAM_OPS_BOT_TOKEN": bool(tg),
                "TELEGRAM_OPS_CHAT_ID": bool(merged.get("TELEGRAM_OPS_CHAT_ID")),
                "DATABASE_URL": bool(
                    merged.get("DATABASE_URL") or merged.get("NOETFIELD_SUPABASE_DATABASE_URL")
                ),
            },
        }
    )
)
PY
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  case "${1:-status}" in
    status) platform_vault_status ;;
    get)
      shift
      read_platform_vault "${1:?key required}"
      ;;
    gmail-app-password) read_gmail_app_password ;;
    *)
      echo "usage: $0 [status|get KEY|gmail-app-password]" >&2
      exit 2
      ;;
  esac
fi
