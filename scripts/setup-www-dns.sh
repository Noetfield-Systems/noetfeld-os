#!/usr/bin/env bash
# Attach www.noetfield.com to noetfield-systems/www via DNS (Cloudflare) + Vercel verify.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=scripts/www-vercel-canonical.sh
source "$ROOT/scripts/www-vercel-canonical.sh"

log() { printf '[setup-www-dns] %s\n' "$*"; }

CF_TOKEN="${CF_NOETFIELD_API_TOKEN:-${CF_API_TOKEN:-}}"
CF_ZONE="${CF_NOETFIELD_ZONE_ID:-}"
PROJECT_ID="prj_68m1LfXo1ElhjHzAJs3VCHz4rQ79"
VERCEL_TEAM="team_DXqqstsPtLv4TVnbadi34GCN"

vercel_token() {
  python3 -c "import json; print(json.load(open('$HOME/Library/Application Support/com.vercel.cli/auth.json'))['token'])"
}

ensure_project_domain() {
  local token body
  token="$(vercel_token)"
  body="$(curl -sS -X POST "https://api.vercel.com/v10/projects/${PROJECT_ID}/domains" \
    -H "Authorization: Bearer ${token}" \
    -H "Content-Type: application/json" \
    -d "{\"name\":\"${NF_WWW_LIVE_DOMAIN}\"}")"
  printf '%s' "$body"
}

resolve_zone_id() {
  if [[ -n "$CF_ZONE" ]]; then
    printf '%s' "$CF_ZONE"
    return 0
  fi
  curl -sS "https://api.cloudflare.com/client/v4/zones?name=noetfield.com" \
    -H "Authorization: Bearer ${CF_TOKEN}" \
    -H "Content-Type: application/json" \
    | python3 -c "import json,sys; d=json.load(sys.stdin); r=d.get('result') or []; print(r[0]['id'] if r else '')"
}

cf_upsert() {
  local type="$1" name="$2" content="$3" zone="$4"
  local existing id
  existing="$(curl -sS "https://api.cloudflare.com/client/v4/zones/${zone}/dns_records?type=${type}&name=${name}" \
    -H "Authorization: Bearer ${CF_TOKEN}" | python3 -c "
import json,sys
d=json.load(sys.stdin)
for r in d.get('result',[]):
    if r.get('name')=='''${name}''' or r.get('name','').endswith('''${name}'''):
        print(r['id']); break
" 2>/dev/null || true)"
  if [[ -n "$existing" ]]; then
    curl -sS -X PUT "https://api.cloudflare.com/client/v4/zones/${zone}/dns_records/${existing}" \
      -H "Authorization: Bearer ${CF_TOKEN}" -H "Content-Type: application/json" \
      -d "$(python3 -c "import json; print(json.dumps({'type':'${type}','name':'${name}','content':'${content}','ttl':1,'proxied':False}))")" >/dev/null
    log "updated ${type} ${name}"
  else
    curl -sS -X POST "https://api.cloudflare.com/client/v4/zones/${zone}/dns_records" \
      -H "Authorization: Bearer ${CF_TOKEN}" -H "Content-Type: application/json" \
      -d "$(python3 -c "import json; print(json.dumps({'type':'${type}','name':'${name}','content':'${content}','ttl':1,'proxied':False}))")" >/dev/null
    log "created ${type} ${name}"
  fi
}

main() {
  log "register ${NF_WWW_LIVE_DOMAIN} on Vercel project ${NF_VERCEL_PROJECT}…"
  local reg txt cname
  reg="$(ensure_project_domain)"
  txt="$(printf '%s' "$reg" | python3 -c "
import json,sys
d=json.load(sys.stdin)
for v in d.get('verification') or []:
    if v.get('type')=='TXT':
        print(v.get('value','')); break
" 2>/dev/null || true)"
  token="$(vercel_token)"
  cname="$(curl -sS "https://api.vercel.com/v6/domains/${NF_WWW_LIVE_DOMAIN}/config?teamId=${VERCEL_TEAM}" \
    -H "Authorization: Bearer ${token}" \
    | python3 -c "
import json,sys
d=json.load(sys.stdin)
recs=d.get('recommendedCNAME') or []
print(recs[0]['value'].rstrip('.') if recs else '')
" 2>/dev/null || true)"

  if [[ -z "$CF_TOKEN" ]]; then
    log "BLOCKED: set CF_NOETFIELD_API_TOKEN in ~/.sina/secrets.env (token must include noetfield.com zone)"
    log "Manual DNS:"
    [[ -n "$txt" ]] && log "  TXT _vercel.noetfield.com → ${txt}"
    [[ -n "$cname" ]] && log "  CNAME www → ${cname}"
    exit 2
  fi

  zone="$(resolve_zone_id)"
  if [[ -z "$zone" ]]; then
    log "BLOCKED: Cloudflare token cannot see noetfield.com zone"
    log "Create token at dash.cloudflare.com → noetfield.com → DNS Edit, add CF_NOETFIELD_API_TOKEN + CF_NOETFIELD_ZONE_ID to vault"
    exit 2
  fi

  if [[ -n "$txt" ]]; then
    cf_upsert TXT "_vercel.noetfield.com" "$txt" "$zone"
  fi
  if [[ -n "$cname" ]]; then
    cf_upsert CNAME "www.noetfield.com" "$cname" "$zone"
  fi

  log "waiting for Vercel domain verify…"
  sleep 8
  curl -sS "https://api.vercel.com/v9/projects/${PROJECT_ID}/domains/${NF_WWW_LIVE_DOMAIN}?teamId=${VERCEL_TEAM}" \
    -H "Authorization: Bearer ${token}" \
    | python3 -c "import json,sys; d=json.load(sys.stdin); print('verified=', d.get('verified'))"
}

main "$@"
