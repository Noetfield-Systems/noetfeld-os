#!/usr/bin/env bash
# Apply noetfield.com Vercel DNS (free Cloudflare DNS only — no Workers).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VAULT="${NF_SECRETS_VAULT:-$HOME/.sina/secrets.env}"
ZONE_ID="456aeba6b1a37d1fadbf6443cb929468"

log() { printf '[apply-noetfield-dns] %s\n' "$*"; }

if [[ -n "${CF_NOETFIELD_API_TOKEN:-}" ]]; then
  if grep -q '^CF_NOETFIELD_API_TOKEN=' "$VAULT" 2>/dev/null; then
    sed -i '' "s|^#*CF_NOETFIELD_API_TOKEN=.*|CF_NOETFIELD_API_TOKEN=${CF_NOETFIELD_API_TOKEN}|" "$VAULT"
  else
    printf '\nCF_NOETFIELD_API_TOKEN=%s\nCF_NOETFIELD_ZONE_ID=%s\n' "$CF_NOETFIELD_API_TOKEN" "$ZONE_ID" >>"$VAULT"
  fi
  log "saved CF_NOETFIELD_API_TOKEN to vault"
fi

export CF_NOETFIELD_API_TOKEN="${CF_NOETFIELD_API_TOKEN:-}"
if [[ -z "$CF_NOETFIELD_API_TOKEN" ]] && [[ -f "$VAULT" ]]; then
  # shellcheck disable=SC1090
  source "$VAULT" 2>/dev/null || true
fi

python3 "$ROOT/scripts/fix-dns-production.py" || exit $?

log "waiting for DNS propagation…"
for i in $(seq 1 24); do
  cname="$(dig +short CNAME www.noetfield.com | tr -d '.')"
  if [[ "$cname" == *d2e47b585a01bc61* ]]; then
    log "CNAME propagated (attempt $i)"
    break
  fi
  sleep 5
done

log "auto-heal deploy + health gate…"
HEAL_SKIP_ENV=1 "$ROOT/scripts/auto-heal-www.sh" || true

log "intake health:"
curl -sS "https://www.noetfield.com/api/intake/health" || true
echo
