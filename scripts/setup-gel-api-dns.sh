#!/usr/bin/env bash
# Point api.noetfield.com → Railway gel-api (after deploy-gel-api-railway.sh).
set -euo pipefail

VAULT="${NF_SECRETS_VAULT:-$HOME/.sina/secrets.env}"
CF_TOKEN="${CF_NOETFIELD_API_TOKEN:-$(grep -E '^CF_NOETFIELD_API_TOKEN=' "$VAULT" 2>/dev/null | tail -1 | cut -d= -f2- | tr -d '\r\n' | sed -e 's/^"//' -e 's/"$//' || true)}"
CF_ZONE="${CF_NOETFIELD_ZONE_ID:-$(grep -E '^CF_NOETFIELD_ZONE_ID=' "$VAULT" 2>/dev/null | tail -1 | cut -d= -f2- | tr -d '\r\n' | sed -e 's/^"//' -e 's/"$//' || true)}"
CNAME_TARGET="${GEL_API_CNAME:-vgkvc5lo.up.railway.app}"
VERIFY_TXT="${GEL_RAILWAY_VERIFY_TXT:-railway-verify=eb5249af9da6489484b6d868238b6db4905835ce20fdbd2adea4ec195ddce2d9}"

log() { printf '[setup-gel-api-dns] %s\n' "$*"; }

upsert() {
  local type="$1" name="$2" content="$3"
  local existing
  existing="$(curl -sS "https://api.cloudflare.com/client/v4/zones/${CF_ZONE}/dns_records?type=${type}&name=${name}" \
    -H "Authorization: Bearer ${CF_TOKEN}" \
    | python3 -c "import json,sys; r=(json.load(sys.stdin).get('result') or []); print(r[0]['id'] if r else '')")"
  local payload
  payload="$(python3 -c "import json; print(json.dumps({'type':'${type}','name':'${name}','content':'${content}','ttl':1,'proxied':False}))")"
  if [[ -n "$existing" ]]; then
    curl -sS -X PUT "https://api.cloudflare.com/client/v4/zones/${CF_ZONE}/dns_records/${existing}" \
      -H "Authorization: Bearer ${CF_TOKEN}" -H "Content-Type: application/json" -d "$payload" >/dev/null
  else
    curl -sS -X POST "https://api.cloudflare.com/client/v4/zones/${CF_ZONE}/dns_records" \
      -H "Authorization: Bearer ${CF_TOKEN}" -H "Content-Type: application/json" -d "$payload" >/dev/null
  fi
  log "upsert ${type} ${name} → ${content}"
}

[[ -n "$CF_TOKEN" && -n "$CF_ZONE" ]] || { log "need CF_NOETFIELD_API_TOKEN + CF_NOETFIELD_ZONE_ID"; exit 2; }

upsert CNAME "api.noetfield.com" "$CNAME_TARGET"
upsert TXT "_railway-verify.api.noetfield.com" "$VERIFY_TXT"

log "waiting for DNS…"
for i in 1 2 3 4 5 6 7 8; do
  if curl -fsS "https://api.noetfield.com/health" >/dev/null 2>&1; then
    curl -sS "https://api.noetfield.com/health"
    echo
    log "PASS"
    exit 0
  fi
  sleep 10
done
log "WARN — DNS set; health not ready yet (Railway build may still be running)"
