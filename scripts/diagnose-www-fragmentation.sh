#!/usr/bin/env bash
# Diagnose www.noetfield.com vs canonical noetfield-systems/www deploy.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=scripts/www-vercel-canonical.sh
source "$ROOT/scripts/www-vercel-canonical.sh"

CANON="${NF_WWW_DEPLOY_URL:-https://project-gc7lm.vercel.app}"
LIVE="https://www.noetfield.com"
TARGET_CNAME="d2e47b585a01bc61.vercel-dns-017.com"

echo "=== noetfield.com fragmentation diagnose ==="
echo "canonical deploy: $CANON"
echo "live www:         $LIVE"
echo ""

current="$(dig +short CNAME www.noetfield.com 2>/dev/null | tr -d '.' || true)"
echo "DNS CNAME www → ${current:-<missing>}"
echo "expected CNAME  → ${TARGET_CNAME}."
if [[ "$current" == *"d2e47b585a01bc61"* ]]; then
  echo "OK   DNS points at canonical Vercel project"
else
  echo "FAIL DNS still points at legacy host (${current:-none})"
  echo "FIX  Cloudflare → noetfield.com → DNS:"
  echo "     CNAME www → $TARGET_CNAME (DNS only / grey cloud)"
  echo "     TXT _vercel → vc-domain-verify=www.noetfield.com,80da2e8e34431bb25d15"
  echo "     Add platform CNAME → $TARGET_CNAME (optional bridge)"
  echo "Vault: add CF_NOETFIELD_API_TOKEN with noetfield.com zone Edit, then:"
  echo "     ./scripts/fix-dns-now.sh"
fi

echo ""
for base in "$CANON" "$LIVE"; do
  code="$(curl -sS -o /dev/null -w "%{http_code}" "${base}/api/intake/health" 2>/dev/null || echo 000)"
  mode="$(curl -sS "${base}/api/intake/health" 2>/dev/null | python3 -c "import json,sys; print(json.load(sys.stdin).get('delivery_mode','?'))" 2>/dev/null || echo "?")"
  echo "$base intake health: HTTP $code delivery_mode=$mode"
done
