#!/usr/bin/env bash
# NF-PLAN-0110 — workspace UI pilot scopes + rate limits.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
export PYTHONPATH="${PYTHONPATH:-}:${ROOT}/packages/types:${ROOT}/packages/config:${ROOT}/packages/sdk:${ROOT}/services/events:${ROOT}/services/ledger:${ROOT}/services/graph:${ROOT}/services/governance:${ROOT}/services/signals:${ROOT}/services/workflow:${ROOT}/services/ai-runtime:${ROOT}/services/inspectors:${ROOT}/services/identity:${ROOT}/services/copilot-governance"

echo "=== verify-workspace-ui-auth ==="
python3 -m pytest tests/unit/test_workspace_ui_pilot_scopes.py -q
grep -q "require_workspace_read_scope" services/governance/noetfield_governance/trust_ledger.py
grep -q "check_workspace_ui_rate_limit" services/governance/noetfield_governance/trust_ledger.py
grep -q "NEXT_PUBLIC_PILOT_API_KEY" governance-console/frontend/lib/trustLedger.ts
echo "verify-workspace-ui-auth: OK"
