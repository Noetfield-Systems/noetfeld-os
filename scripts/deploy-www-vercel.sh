#!/usr/bin/env bash
# Production deploy www.noetfield.com → Vercel project the-777-foundation/noetfield
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
# shellcheck source=scripts/www-vercel-canonical.sh
source "$ROOT/scripts/www-vercel-canonical.sh"

log() { printf '[deploy-www-vercel] %s\n' "$*"; }

log "scope=$NF_VERCEL_SCOPE project=$NF_VERCEL_PROJECT"

log "sync chat greeting SSOT asset…"
python3 scripts/sync_chat_greeting_asset.py
python3 scripts/verify_chat_greeting_coupling.py

if [[ ! -d .vercel ]] || ! grep -q '"projectName": "noetfield"' .vercel/project.json 2>/dev/null; then
  rm -rf .vercel
  npx vercel link --project "$NF_VERCEL_PROJECT" --scope "$NF_VERCEL_SCOPE" --yes
fi

npx vercel deploy --prod --scope "$NF_VERCEL_SCOPE" --yes

log "health check…"
curl -sS "${NF_WWW_CANONICAL_URL}/health"
echo
curl -sS "${NF_WWW_CANONICAL_URL}/api/intake/health" | python3 -m json.tool 2>/dev/null || true
python3 scripts/verify_chat_greeting_coupling.py --live || {
  log "WARN: live greeting coupling not yet green — platform deploy may still be propagating"
}
log "done — ${NF_WWW_CANONICAL_URL}"
