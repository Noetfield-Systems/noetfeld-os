#!/usr/bin/env bash
# Cut www.noetfield.com DNS from Vercel → Cloudflare Pages (verify preview first).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VAULT="${NF_SECRETS_VAULT:-$HOME/.sina/secrets.env}"
ZONE="${CF_NOETFIELD_ZONE_ID:-456aeba6b1a37d1fadbf6443cb929468}"
PROJECT="${CF_PAGES_PROJECT:-noetfield-www}"
HOST="${NF_WWW_LIVE_DOMAIN:-www.noetfield.com}"
CNAME_ID="${CF_WWW_CNAME_RECORD_ID:-1b24691ebe98d07087190b761d6ef024}"

log() { printf '[setup-www-dns-cloudflare] %s\n' "$*"; }

read_vault_token() {
  # shellcheck disable=SC1090
  [[ -f "$VAULT" ]] && source "$VAULT" 2>/dev/null || true
  printf '%s' "${CF_NOETFIELD_API_TOKEN:-${CF_API_TOKEN:-}}"
}

pages_target() {
  npx wrangler pages project get "$PROJECT" --json 2>/dev/null | python3 -c "
import json,sys
try:
    d=json.load(sys.stdin)
    sub=str(d.get('subdomain') or d.get('name') or '').strip()
    if sub:
        print(f'{sub}.pages.dev')
except Exception:
    pass
" || true
}

PREVIEW_URL="${CF_PAGES_PREVIEW_URL:-}"
if [[ -z "$PREVIEW_URL" ]]; then
  sub="$(pages_target)"
  [[ -n "$sub" ]] && PREVIEW_URL="https://${sub}"
fi

if [[ -z "$PREVIEW_URL" ]]; then
  log "FAIL: set CF_PAGES_PREVIEW_URL or ensure project ${PROJECT} exists"
  exit 2
fi

log "verify preview before DNS: ${PREVIEW_URL}"
python3 "$ROOT/scripts/nf_post_deploy_verify.py" --surface www --www-base "$PREVIEW_URL" || {
  log "FAIL: preview not green — aborting DNS cutover"
  exit 3
}

TARGET="${CF_PAGES_CNAME_TARGET:-$(pages_target)}"
if [[ -z "$TARGET" ]]; then
  log "FAIL: could not resolve Pages CNAME target"
  exit 4
fi

log "DNS cutover: ${HOST} CNAME → ${TARGET}"
token="$(read_vault_token)"
if [[ -z "$token" ]]; then
  log "FAIL: CF_NOETFIELD_API_TOKEN missing in ${VAULT}"
  exit 5
fi

body="$(python3 -c "import json; print(json.dumps({'type':'CNAME','name':'${HOST}','content':'${TARGET}','ttl':1,'proxied':True}))")"
resp="$(curl -sS -X PUT "https://api.cloudflare.com/client/v4/zones/${ZONE}/dns_records/${CNAME_ID}" \
  -H "Authorization: Bearer ${token}" \
  -H "Content-Type: application/json" \
  -d "$body")"
python3 -c "import json,sys; d=json.load(sys.stdin); print('dns',d.get('success')); sys.exit(0 if d.get('success') else 1)" <<<"$resp"

log "attach custom domain on Pages…"
npx wrangler pages domain add "$HOST" --project-name "$PROJECT" 2>/dev/null || log "domain may already be attached"

log "waiting for propagation…"
for _ in $(seq 1 24); do
  if dig +short CNAME "$HOST" | grep -q 'pages.dev'; then
    log "CNAME propagated"
    break
  fi
  sleep 5
done

CF_PAGES_DNS_READY=1 NF_WWW_CANONICAL_URL="https://${HOST}" bash "$ROOT/scripts/deploy-www-cloudflare.sh" || true

log "canonical verify…"
python3 "$ROOT/scripts/nf_post_deploy_verify.py" --surface www --www-base "https://${HOST}" || {
  log "FAIL: canonical verify failed after DNS"
  exit 6
}

log "PASS — ${HOST} on Cloudflare Pages"
