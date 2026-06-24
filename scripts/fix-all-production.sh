#!/usr/bin/env bash
# One-shot: DNS + Resend + Vercel auto-heal for Noetfield production intake.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
chmod +x scripts/*.sh 2>/dev/null || true

echo "=== Noetfield production fix-all ==="

# Open Cloudflare DNS for noetfield (user may already be logged in)
open "https://dash.cloudflare.com/456aeba6b1a37d1fadbf6443cb929468/noetfield.com/dns/records" 2>/dev/null || true
open "https://dash.cloudflare.com/profile/api-tokens" 2>/dev/null || true
open "https://resend.com/api-keys" 2>/dev/null || true

python3 scripts/fix-dns-production.py || true

export PATH="$PATH:/Users/sinakazemnezhad/.npm-global/bin"
if [[ -z "${RESEND_FULL_API_KEY:-}" ]] && grep -q '^RESEND_FULL_API_KEY=' ~/.sina/secrets.env 2>/dev/null; then
  export RESEND_FULL_API_KEY="$(grep '^RESEND_FULL_API_KEY=' ~/.sina/secrets.env | cut -d= -f2- | tr -d '\r\n')"
fi
./scripts/setup-resend-domain.sh 2>/dev/null || true

HEAL_SKIP_ENV=1 ./scripts/auto-heal-www.sh || true

echo ""
echo "=== Health ==="
curl -sS "https://project-gc7lm.vercel.app/api/intake/health" 2>/dev/null; echo
curl -sS "https://www.noetfield.com/api/intake/health" 2>/dev/null; echo
