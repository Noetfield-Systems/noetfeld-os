#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=dev-ports.sh
source "${ROOT}/scripts/dev-ports.sh"

PORT="$PLATFORM_CONSOLE_PORT"
export PYTHONPATH="${ROOT}/packages/types:${ROOT}/packages/config:${ROOT}/packages/sdk:${ROOT}/services/events:${ROOT}/services/ledger:${ROOT}/services/graph:${ROOT}/services/governance:${ROOT}/services/signals:${ROOT}/services/workflow:${ROOT}/services/ai-runtime:${ROOT}/services/inspectors:${ROOT}/services/identity:${ROOT}/services/copilot-governance"
export RUNTIME_EVENT_STORE="${RUNTIME_EVENT_STORE:-memory}"

if command -v lsof >/dev/null 2>&1; then
  lsof -tiTCP:"$PORT" -sTCP:LISTEN 2>/dev/null | xargs -r kill -9 2>/dev/null || true
fi
sleep 1

echo ">>> http://127.0.0.1:${PORT}/console"
echo ">>> http://localhost:${PORT}/console"

exec bash "${ROOT}/scripts/dev-python.sh" -m uvicorn noetfield_governance.api:app --reload --host 0.0.0.0 --port "$PORT" --app-dir "${ROOT}/services/governance"
