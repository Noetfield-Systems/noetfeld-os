#!/usr/bin/env bash
# Quick intake health check — www production or local override.
set -euo pipefail

BASE="${INTAKE_HEALTH_BASE:-https://www.noetfield.com}"
URL="${BASE%/}/api/intake/health"

echo "Checking ${URL} ..."
BODY="$(curl -sS "$URL")"
echo "$BODY" | python3 -c "
import json, sys
h = json.load(sys.stdin)
mode = h.get('delivery_mode', '?')
enabled = h.get('enabled')
www = h.get('www_email_configured')
print(f\"  enabled={enabled}  www_email={www}  delivery_mode={mode}\")
if not www and mode == 'unconfigured':
    print('  NEXT: Run ./scripts/auto-heal-www.sh — see docs/ops/VERCEL_INTAKE_SETUP.md')
    sys.exit(1)
print('  OK')
"
