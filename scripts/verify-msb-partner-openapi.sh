#!/usr/bin/env bash
# NF-PLAN-0103 — committed public OpenAPI matches live app (msb partner routes).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
export PYTHONPATH="${PYTHONPATH:-}:${ROOT}/packages/types:${ROOT}/packages/config:${ROOT}/packages/sdk:${ROOT}/services/events:${ROOT}/services/ledger:${ROOT}/services/graph:${ROOT}/services/governance:${ROOT}/services/signals:${ROOT}/services/workflow:${ROOT}/services/ai-runtime:${ROOT}/services/inspectors:${ROOT}/services/identity:${ROOT}/services/copilot-governance"

echo "=== verify-msb-partner-openapi ==="
cp docs/api/openapi.json /tmp/nf-openapi-before.json
cp docs/api/openapi.yaml /tmp/nf-openapi-before.yaml
python3 scripts/generate_public_openapi.py >/dev/null

if ! diff -q /tmp/nf-openapi-before.json docs/api/openapi.json >/dev/null 2>&1; then
  echo "FAIL docs/api/openapi.json drift — run: make generate-openapi" >&2
  exit 1
fi
if ! diff -q /tmp/nf-openapi-before.yaml docs/api/openapi.yaml >/dev/null 2>&1; then
  echo "FAIL docs/api/openapi.yaml drift — run: make generate-openapi" >&2
  exit 1
fi

python3 -m pytest tests/unit/test_msb_partner_openapi_sync.py -q
echo "verify-msb-partner-openapi: OK"
