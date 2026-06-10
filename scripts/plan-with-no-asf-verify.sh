#!/usr/bin/env bash
# PLAN WITH NO ASF — single verify bundle (Noetfield only).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=dev-ports.sh
source "${ROOT}/scripts/dev-ports.sh"
cd "$ROOT"

echo "=== plan-with-no-asf-verify ==="

chmod +x scripts/verify-agent-scope.sh
./scripts/verify-agent-scope.sh

health="$(curl -sS -o /dev/null -w "%{http_code}" --connect-timeout 3 "http://127.0.0.1:${NF_DEV_PUBLIC_PORT}/health" 2>/dev/null || echo "000")"
if [[ "$health" != "200" ]]; then
  echo "Dev stack not up (health ${health}); starting NF_DASHBOARD_MODE=production make dev-local-pro …"
  NF_DASHBOARD_MODE=production make dev-local-pro
fi

chmod +x scripts/verify-ui-endpoints.sh scripts/verify-ui-e2e.sh scripts/verify-copilot-demo-links.sh
chmod +x scripts/verify-audit-export.sh scripts/copilot-pilot-e2e.sh scripts/procurement-pack-e2e.sh
chmod +x scripts/verify-gtm-ops-docs.sh scripts/verify-tier-gate.sh
chmod +x scripts/verify-quick-pick-fresh.sh scripts/verify-boundary-matrix.sh
./scripts/verify-ui-endpoints.sh
./scripts/verify-ui-e2e.sh
./scripts/verify-copilot-demo-links.sh
./scripts/verify-gtm-ops-docs.sh
chmod +x scripts/verify-demo-url.sh
./scripts/verify-demo-url.sh
./scripts/verify-tier-gate.sh
./scripts/verify-quick-pick-fresh.sh
./scripts/verify-boundary-matrix.sh
./scripts/verify-audit-export.sh
./scripts/copilot-pilot-e2e.sh
./scripts/procurement-pack-e2e.sh

cd governance-console/backend
PYTHONPATH=. python3 -m pytest tests/test_audit_events.py -q
cd "$ROOT"

python3 scripts/smoke_bank_grade_html.py

chmod +x scripts/verify-no-asf-coherence.sh
./scripts/verify-no-asf-coherence.sh

if [[ -n "${NF_STAGING_URL:-}" ]]; then
  echo "NF_STAGING_URL set — running optional staging-smoke …"
  chmod +x scripts/staging-smoke.sh
  ./scripts/staging-smoke.sh
else
  echo "SKIP staging-smoke (NF_STAGING_URL not set)"
fi

echo ""
echo "plan-with-no-asf-verify passed."
