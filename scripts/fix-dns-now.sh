#!/usr/bin/env bash
# Fix noetfield.com www DNS → canonical Vercel (free Cloudflare DNS only).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VAULT="${NF_SECRETS_VAULT:-$HOME/.sina/secrets.env}"
ZONE="456aeba6b1a37d1fadbf6443cb929468"
CNAME_ID="1b24691ebe98d07087190b761d6ef024"
TXT_ID="6e6c4c155772beb1618a521d8e03d4d3"
CNAME="d2e47b585a01bc61.vercel-dns-017.com"
TXT="vc-domain-verify=www.noetfield.com,80da2e8e34431bb25d15"
TOKEN_EDIT="https://dash.cloudflare.com/profile/api-tokens/7c2589dc89e41fc71b6f0f8fd01ec426"
DNS_URL="https://dash.cloudflare.com/${ZONE}/noetfield.com/dns/records"

log() { printf '[fix-dns-now] %s\n' "$*"; }

read_vault_token() {
  # shellcheck disable=SC1090
  [[ -f "$VAULT" ]] && source "$VAULT" 2>/dev/null || true
  printf '%s' "${CF_NOETFIELD_API_TOKEN:-${CF_API_TOKEN:-}}"
}

cf_put() {
  local token="$1" id="$2" body="$3"
  curl -sS -X PUT "https://api.cloudflare.com/client/v4/zones/${ZONE}/dns_records/${id}" \
    -H "Authorization: Bearer ${token}" \
    -H "Content-Type: application/json" \
    -d "$body"
}

apply_dns() {
  local token="$1"
  local c1 c2
  c1="$(cf_put "$token" "$CNAME_ID" "{\"type\":\"CNAME\",\"name\":\"www.noetfield.com\",\"content\":\"${CNAME}\",\"ttl\":1,\"proxied\":false}")"
  c2="$(cf_put "$token" "$TXT_ID" "{\"type\":\"TXT\",\"name\":\"_vercel.noetfield.com\",\"content\":\"${TXT}\",\"ttl\":1,\"proxied\":false}")"
  python3 -c "import json,sys; c1=json.loads(sys.argv[1]); c2=json.loads(sys.argv[2]); print('cname',c1.get('success'),'txt',c2.get('success')); sys.exit(0 if c1.get('success') and c2.get('success') else 1)" "$c1" "$c2"
}

log "Attempting DNS apply via API…"
token="$(read_vault_token)"
if [[ -n "$token" ]] && apply_dns "$token" 2>/dev/null; then
  log "DNS applied via API"
else
  log "API blocked — expand existing token OR edit DNS manually"
  log "Token edit (add zone noetfield.com → DNS Edit): $TOKEN_EDIT"
  log "DNS records: $DNS_URL"
  open "$TOKEN_EDIT" 2>/dev/null || true
  open "$DNS_URL" 2>/dev/null || true
  printf '%s' "$CNAME" | pbcopy 2>/dev/null || true
  log "CNAME target copied to clipboard"
  log "Polling API every 5s (add noetfield.com to token, then wait)…"
  for i in $(seq 1 36); do
    token="$(read_vault_token)"
    if apply_dns "$token" 2>/dev/null; then
      log "DNS applied on poll $i"
      break
    fi
    sleep 5
  done || {
    log "Still blocked. Manual edits on $DNS_URL :"
    log "  CNAME www → $CNAME"
    log "  TXT _vercel (www line) → $TXT"
    exit 2
  }
fi

log "Waiting for propagation…"
for i in $(seq 1 18); do
  if dig +short CNAME www.noetfield.com | grep -q 'd2e47b585a01bc61'; then
    log "CNAME propagated"
    break
  fi
  sleep 5
done

log "Auto-heal…"
HEAL_SKIP_ENV=1 "$ROOT/scripts/auto-heal-www.sh" || true

log "Health:"
curl -sS "https://www.noetfield.com/api/intake/health" || true
echo
