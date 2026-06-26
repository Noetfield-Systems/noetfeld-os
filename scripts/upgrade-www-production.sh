#!/usr/bin/env bash
# UPGRADE — verify competitive + SSOT content, bump cache v=43, deploy canonical www.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

log() { printf '[upgrade-www] %s\n' "$*"; }

log "=== Noetfield www UPGRADE ==="

# Bump public HTML cache bust v=40|41|42 → v=43
while IFS= read -r -d '' f; do
  if grep -qE 'v=(40|41|42)' "$f"; then
    sed -i '' -E 's/v=40/v=43/g; s/v=41/v=43/g; s/v=42/v=43/g' "$f"
    log "bumped cache: $f"
  fi
done < <(find . -path './copilot/*.html' -o -name 'index.html' -maxdepth 1 -print0 2>/dev/null)

# SSOT demo assets
for f in assets/noetfield-ssot-demo.css assets/noetfield-ssot-demo.js; do
  [[ -f "$f" ]] && sed -i '' 's/v=1/v=2/g' "$f" 2>/dev/null || true
done
for f in copilot/demo/index.html; do
  [[ -f "$f" ]] && sed -i '' 's/noetfield-ssot-demo\.css?v=[0-9]*/noetfield-ssot-demo.css?v=2/g; s/noetfield-ssot-demo\.js?v=[0-9]*/noetfield-ssot-demo.js?v=2/g' "$f"
done

log "verify competitive content…"
./scripts/verify-competitive-content.sh

if [[ -f scripts/verify-ssot-demo.sh ]]; then
  log "verify SSOT demo…"
  ./scripts/verify-ssot-demo.sh
fi

log "deploy canonical www…"
HEAL_SKIP_ENV=1 ./scripts/auto-heal-www.sh || {
  log "WARN: auto-heal exited non-zero — check DNS alias for www.noetfield.com"
}

BASE="https://project-gc7lm.vercel.app"
log "canonical smoke:"
for p in "/" "/copilot/proof-case/" "/copilot/governance-audit-trail/" "/copilot/procurement/" "/copilot/demo/" "/api/intake/health"; do
  code="$(curl -sS -o /tmp/nf-upgrade-body -w '%{http_code}' -L "${BASE}${p}" 2>/dev/null || echo 000)"
  log "  ${code} ${p}"
done
if grep -q buyer-faq /tmp/nf-upgrade-body 2>/dev/null; then
  log "  procurement buyer-faq: OK"
fi
curl -sS "${BASE}/api/intake/health" 2>/dev/null | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    print(f\"  intake delivery_mode={d.get('delivery_mode')} www_email={d.get('www_email_configured')}\")
except Exception as e:
    print('  intake health parse failed', e)
" || true

log ""
log "UPGRADE complete. Canonical: ${BASE}"
log "If www.noetfield.com lags: fix Cloudflare DNS on sina.kazemnezhad.ca account → d2e47b585a01bc61.vercel-dns-017.com"
