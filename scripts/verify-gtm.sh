#!/usr/bin/env bash
# GTM pre-demo verify — run before sharing tunnel/staging URL with a design partner.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=dev-ports.sh
source "${ROOT}/scripts/dev-ports.sh"
cd "$ROOT"

echo "=== verify-gtm (pre-demo bundle) ==="

if [[ -f scripts/verify-no-competitor-names.sh ]]; then
  chmod +x scripts/verify-no-competitor-names.sh
  ./scripts/verify-no-competitor-names.sh
fi

if [[ -f scripts/verify-static-www.sh ]]; then
  chmod +x scripts/verify-static-www.sh
  ./scripts/verify-static-www.sh
fi

if [[ -f scripts/validate-noetfield-1000-sources.py ]]; then
  python3 scripts/validate-noetfield-1000-sources.py
fi

if [[ -f scripts/smoke-pick-no-asf-plan.sh ]]; then
  ./scripts/smoke-pick-no-asf-plan.sh
fi

if [[ -f scripts/verify-lane-fences.sh ]]; then
  ./scripts/verify-lane-fences.sh
fi

code="$(curl -sS -o /dev/null -w "%{http_code}" --connect-timeout 3 "http://127.0.0.1:${NF_DEV_PUBLIC_PORT}/health" 2>/dev/null || echo "000")"
if [[ "$code" != "200" ]]; then
  echo "FAIL: dev stack not up (health ${code}). Run: make dev-local" >&2
  exit 1
fi

if [[ -f scripts/smoke-seed-m365-evidence-stub.sh ]]; then
  chmod +x scripts/smoke-seed-m365-evidence-stub.sh
  ./scripts/smoke-seed-m365-evidence-stub.sh
fi

cd governance-console/backend
PYTHONPATH=. python3 -m pytest tests/test_tle_flow.py tests/test_audit_events.py -q
cd "$ROOT"

if [[ -f scripts/tle-smoke.sh ]]; then
  ./scripts/tle-smoke.sh
fi

make verify-local-dev
make verify-ui-e2e
make verify-ui-visual
make copilot-pilot-e2e
make procurement-pack-e2e

echo ""
echo "Optional: make demo-url  (after make dev-local-tunnel-bg or NF_STAGING_URL)"
echo ""
echo "verify-gtm passed — safe to run external demo."
