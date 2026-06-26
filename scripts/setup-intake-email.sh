#!/usr/bin/env bash
# Full intake email go-live: Resend domain + www DNS + auto-heal.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
chmod +x scripts/setup-www-dns.sh scripts/setup-resend-domain.sh scripts/auto-heal-www.sh 2>/dev/null || true

echo "[setup-intake-email] 1/3 Resend sending domain…"
if ! ./scripts/setup-resend-domain.sh; then
  echo "[setup-intake-email] Resend setup incomplete (need RESEND_FULL_API_KEY or DNS wait)"
fi

echo "[setup-intake-email] 2/3 www DNS → canonical Vercel…"
if ! ./scripts/setup-www-dns.sh; then
  echo "[setup-intake-email] www DNS incomplete (need CF_NOETFIELD_API_TOKEN for noetfield.com zone)"
fi

echo "[setup-intake-email] 3/3 auto-heal deploy + health…"
HEAL_SKIP_ENV=1 ./scripts/auto-heal-www.sh || true

echo "[setup-intake-email] done — check:"
curl -sS "https://www.noetfield.com/api/intake/health" 2>/dev/null || true
echo
