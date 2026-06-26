#!/usr/bin/env bash
# Verify a sending domain on Resend + Cloudflare DNS (default: notify.trustfield.ca).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VAULT="${NF_SECRETS_VAULT:-$HOME/.sina/secrets.env}"

log() { printf '[setup-resend-domain] %s\n' "$*"; }

read_vault() {
  grep -E "^${1}=" "$VAULT" 2>/dev/null | tail -1 | cut -d= -f2- | tr -d '\r\n' | sed -e 's/^"//' -e 's/"$//' || true
}

RESEND_DOMAIN="${RESEND_DOMAIN:-notify.trustfield.ca}"
RESEND_KEY="${RESEND_FULL_API_KEY:-$(read_vault RESEND_FULL_API_KEY)}"
if [[ -z "$RESEND_KEY" ]]; then
  RESEND_KEY="$(read_vault RESEND_API_KEY)"
fi

CF_TOKEN="${CF_API_TOKEN:-$(read_vault CF_API_TOKEN)}"
CF_ZONE="${CF_ZONE_ID:-$(read_vault CF_ZONE_ID)}"

if [[ -z "$RESEND_KEY" ]]; then
  log "FAIL: RESEND_FULL_API_KEY missing in vault (send-only keys cannot add domains)"
  log "Create full access key: https://resend.com/api-keys → add RESEND_FULL_API_KEY= to ~/.sina/secrets.env"
  exit 1
fi

if resend domains list --api-key "$RESEND_KEY" 2>/dev/null | grep -q "$RESEND_DOMAIN"; then
  log "domain already registered: $RESEND_DOMAIN"
else
  log "creating Resend domain ${RESEND_DOMAIN}..."
  resend domains create --name "$RESEND_DOMAIN" --region us-east-1 --api-key "$RESEND_KEY" >/tmp/resend-domain.json 2>&1 || {
    cat /tmp/resend-domain.json >&2
    exit 1
  }
fi

DOMAIN_ID="$(resend domains list --api-key "$RESEND_KEY" --json 2>/dev/null \
  | python3 -c "import json,sys; d=json.load(sys.stdin); 
data=d.get('data') or d.get('result') or []
for row in data:
  if row.get('name')=='${RESEND_DOMAIN}':
    print(row.get('id','')); break
" 2>/dev/null || true)"

if [[ -z "$DOMAIN_ID" ]]; then
  DOMAIN_ID="$(resend domains get "$RESEND_DOMAIN" --api-key "$RESEND_KEY" --json 2>/dev/null \
    | python3 -c "import json,sys; d=json.load(sys.stdin); print((d.get('data') or d).get('id',''))" 2>/dev/null || true)"
fi

[[ -n "$DOMAIN_ID" ]] || { log "FAIL: could not resolve Resend domain id"; exit 1; }

RECORDS_JSON="$(resend domains get "$DOMAIN_ID" --api-key "$RESEND_KEY" --json 2>/dev/null || resend domains get "$DOMAIN_ID" --api-key "$RESEND_KEY")"

if [[ -z "$CF_TOKEN" ]]; then
  log "BLOCKED: CF_API_TOKEN missing — paste DNS records manually:"
  printf '%s\n' "$RECORDS_JSON"
  exit 2
fi

if [[ -z "$CF_ZONE" ]]; then
  apex="${RESEND_DOMAIN#*.}"
  CF_ZONE="$(curl -sS "https://api.cloudflare.com/client/v4/zones?name=${apex}" \
    -H "Authorization: Bearer ${CF_TOKEN}" \
    | python3 -c "import json,sys; r=json.load(sys.stdin).get('result') or []; print(r[0]['id'] if r else '')")"
fi

[[ -n "$CF_ZONE" ]] || { log "FAIL: Cloudflare zone not found for $RESEND_DOMAIN"; exit 1; }

python3 - <<'PY' "$RECORDS_JSON" "$CF_TOKEN" "$CF_ZONE"
import json, sys, urllib.request

records_raw = sys.argv[1]
token, zone = sys.argv[2], sys.argv[3]
try:
    payload = json.loads(records_raw)
except json.JSONDecodeError:
    print("WARN: could not parse records JSON"); sys.exit(0)
data = payload.get("data") or payload
rows = data.get("records") or []

def cf(method, path, body=None):
    req = urllib.request.Request(
        f"https://api.cloudflare.com/client/v4/zones/{zone}{path}",
        data=json.dumps(body).encode() if body else None,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        method=method,
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())

for rec in rows:
    rtype = rec.get("type") or rec.get("record")
    name = rec.get("name", "")
    value = rec.get("value") or rec.get("content") or ""
    if not rtype or not name or not value:
        continue
    name = name.rstrip(".")
    existing = cf("GET", f"/dns_records?type={rtype}&name={name}")
    body = {"type": rtype, "name": name, "content": value, "ttl": 1, "proxied": False}
    if existing.get("result"):
        rid = existing["result"][0]["id"]
        cf("PUT", f"/dns_records/{rid}", body)
        print(f"updated {rtype} {name}")
    else:
        cf("POST", "/dns_records", body)
        print(f"created {rtype} {name}")
PY

log "trigger Resend verify..."
resend domains verify "$DOMAIN_ID" --api-key "$RESEND_KEY" >/dev/null 2>&1 || true
sleep 10
STATUS="$(resend domains get "$DOMAIN_ID" --api-key "$RESEND_KEY" --json 2>/dev/null \
  | python3 -c "import json,sys; d=json.load(sys.stdin); print((d.get('data') or d).get('status',''))" 2>/dev/null || echo pending)"
log "domain status: ${STATUS}"

FROM_ADDR="Noetfield Intake <intake@${RESEND_DOMAIN}>"
log "set Vercel INTAKE_EMAIL_FROM=${FROM_ADDR}"
npx vercel env add INTAKE_EMAIL_FROM production --scope noetfield-systems --force --yes --value "$FROM_ADDR" >/dev/null 2>&1 || true

if [[ "$STATUS" == "verified" ]]; then
  log "PASS - Resend domain verified"
  exit 0
fi
log "WARN - DNS propagating; re-run: ./scripts/setup-resend-domain.sh"
exit 2
