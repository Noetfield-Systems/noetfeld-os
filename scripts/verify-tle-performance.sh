#!/usr/bin/env bash
# NF-PLAN-0105 — TLE API performance smoke (live when platform up, static otherwise).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
# shellcheck source=dev-ports.sh
source "${ROOT}/scripts/dev-ports.sh"

echo "=== verify-tle-performance ==="
python3 -m pytest tests/unit/test_tle_smoke_performance.py -q

health_code="$(curl -sS -o /dev/null -w "%{http_code}" --connect-timeout 2 \
  "http://127.0.0.1:${NF_DEV_PLATFORM_PORT}/health" 2>/dev/null || echo "000")"
if [[ "$health_code" == "200" ]]; then
  chmod +x scripts/tle-smoke.sh
  ./scripts/tle-smoke.sh --api --perf
  echo "live perf smoke: OK"
else
  echo "platform not up (${health_code}) — static perf script checks only"
fi

echo "verify-tle-performance: OK"
