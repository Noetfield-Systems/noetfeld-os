#!/usr/bin/env bash
# Add status.noetfield.com to Vercel noetfield project + DNS CNAME.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "$ROOT/scripts/www-vercel-canonical.sh"

HOST="${NF_STATUS_LIVE_DOMAIN:-status.noetfield.com}"
VAULT="${NF_SECRETS_VAULT:-$HOME/.sina/secrets.env}"
CF_TOKEN="${CF_NOETFIELD_API_TOKEN:-$(grep -E '^CF_NOETFIELD_API_TOKEN=' "$VAULT" 2>/dev/null | tail -1 | cut -d= -f2- | tr -d '\r\n' | sed -e 's/^"//' -e 's/"$//' || true)}"
CF_ZONE="${CF_NOETFIELD_ZONE_ID:-$(grep -E '^CF_NOETFIELD_ZONE_ID=' "$VAULT" 2>/dev/null | tail -1 | cut -d= -f2- | tr -d '\r\n' | sed -e 's/^"//' -e 's/"$//' || true)}"

log() { printf '[setup-status-dns] %s\n' "$*"; }

log "add domain ${HOST} to Vercel project ${NF_VERCEL_PROJECT}"
npx vercel domains add "$HOST" --scope "$NF_VERCEL_SCOPE" 2>&1 || log "domain may already exist on project"

vercel_token() {
  python3 -c "import json; print(json.load(open('$HOME/Library/Application Support/com.vercel.cli/auth.json'))['token'])"
}

token="$(vercel_token)"
cname="$(curl -sS "https://api.vercel.com/v6/domains/${HOST}/config?teamId=team_AKduEfXc59NTMgSd7MzgujVw" \
  -H "Authorization: Bearer ${token}" \
  | python3 -c "import json,sys; d=json.load(sys.stdin); r=d.get('recommendedCNAME') or []; print(r[0]['value'].rstrip('.') if r else '')" 2>/dev/null || true)"

if [[ -z "$CF_TOKEN" || -z "$CF_ZONE" || -z "$cname" ]]; then
  log "Manual: CNAME ${HOST} → ${cname:-<vercel-dns>}"
  exit 0
fi

existing="$(curl -sS "https://api.cloudflare.com/client/v4/zones/${CF_ZONE}/dns_records?type=CNAME&name=${HOST}" \
  -H "Authorization: Bearer ${CF_TOKEN}" \
  | python3 -c "import json,sys; r=(json.load(sys.stdin).get('result') or []); print(r[0]['id'] if r else '')")"

payload="$(python3 -c "import json; print(json.dumps({'type':'CNAME','name':'${HOST}','content':'${cname}','ttl':1,'proxied':False}))")"

if [[ -n "$existing" ]]; then
  curl -sS -X PUT "https://api.cloudflare.com/client/v4/zones/${CF_ZONE}/dns_records/${existing}" \
    -H "Authorization: Bearer ${CF_TOKEN}" -H "Content-Type: application/json" -d "$payload" >/dev/null
else
  curl -sS -X POST "https://api.cloudflare.com/client/v4/zones/${CF_ZONE}/dns_records" \
    -H "Authorization: Bearer ${CF_TOKEN}" -H "Content-Type: application/json" -d "$payload" >/dev/null
fi

log "DNS CNAME ${HOST} → ${cname}"
log "redirect rule in vercel.json sends status host → www.noetfield.com/status/"
