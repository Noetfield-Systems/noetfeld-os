#!/usr/bin/env bash
# GTM pre-demo verify — run before sharing tunnel/staging URL with a design partner.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=dev-ports.sh
source "${ROOT}/scripts/dev-ports.sh"
cd "$ROOT"

echo "=== verify-gtm (pre-demo bundle) ==="

code="$(curl -sS -o /dev/null -w "%{http_code}" --connect-timeout 3 "http://127.0.0.1:${NF_DEV_PUBLIC_PORT}/health" 2>/dev/null || echo "000")"
if [[ "$code" != "200" ]]; then
  echo "FAIL: dev stack not up (health ${code}). Run: make dev-local" >&2
  exit 1
fi

cd governance-console/backend
PYTHONPATH=. python3 -m pytest tests/test_tle_flow.py -q
cd "$ROOT"

make verify-local-dev
make verify-ui-e2e
make copilot-pilot-e2e
make procurement-pack-e2e

echo ""
echo "Optional: make demo-url  (after make dev-local-tunnel-bg or NF_STAGING_URL)"
echo ""
echo "verify-gtm passed — safe to run external demo."
