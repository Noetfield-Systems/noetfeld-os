#!/usr/bin/env bash
# Opens Cloudflare + prints exact noetfield.com DNS fixes for canonical Vercel www.
set -euo pipefail

VERCEL_CNAME="d2e47b585a01bc61.vercel-dns-017.com"
VERCEL_TXT="vc-domain-verify=www.noetfield.com,80da2e8e34431bb25d15"
ZONE_ID="456aeba6b1a37d1fadbf6443cb929468"

echo "=== noetfield.com DNS (required for www fix) ==="
echo ""
echo "1) Edit CNAME www.noetfield.com"
echo "   FROM: 210ae8d5e3588265.vercel-dns-017.com  (old project)"
echo "   TO:   ${VERCEL_CNAME}"
echo "   Proxy: DNS only (grey cloud)"
echo ""
echo "2) Edit TXT _vercel.noetfield.com"
echo "   ADD or REPLACE with:"
echo "   ${VERCEL_TXT}"
echo ""
echo "Opening Cloudflare DNS editor…"
open "https://dash.cloudflare.com/${ZONE_ID}/noetfield.com/dns/records" 2>/dev/null || true
open "https://dash.cloudflare.com/profile/api-tokens" 2>/dev/null || true

echo ""
echo "After saving DNS, run:"
echo "  cd $(cd "$(dirname "$0")/.." && pwd) && ./scripts/setup-www-dns.sh"
echo "  HEAL_SKIP_ENV=1 ./scripts/auto-heal-www.sh"
