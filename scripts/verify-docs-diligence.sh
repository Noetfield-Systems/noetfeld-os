#!/usr/bin/env bash
# NF-PLAN-0102 — docs diligence integration tests (happy path + 409 guards).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
export PYTHONPATH="${PYTHONPATH:-}:${ROOT}/packages/types:${ROOT}/packages/config:${ROOT}/packages/sdk:${ROOT}/services/events:${ROOT}/services/ledger:${ROOT}/services/graph:${ROOT}/services/governance:${ROOT}/services/signals:${ROOT}/services/workflow:${ROOT}/services/ai-runtime:${ROOT}/services/inspectors:${ROOT}/services/identity:${ROOT}/services/copilot-governance"

echo "=== verify-docs-diligence ==="
python3 -m pytest tests/integration/test_docs_diligence_integration.py -q
echo "verify-docs-diligence: OK"
