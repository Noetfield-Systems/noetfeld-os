#!/usr/bin/env bash
# Wait for unified dev proxy to serve canonical static www (not just /health).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=dev-ports.sh
source "${ROOT}/scripts/dev-ports.sh"

BASE="http://127.0.0.1:${NF_DEV_PUBLIC_PORT}"
MAX_WAIT="${NF_DEV_WWW_READY_SEC:-90}"
NEEDLES=(
  "audit trail your Copilot deployment"
  "Apply for pilot"
  "Start free sandbox"
  "data-live-proof-hero"
  "live-proof-hero"
)

health_ok() {
  local code
  code="$(curl -sS -o /dev/null -w "%{http_code}" --connect-timeout 3 "${BASE}/health" 2>/dev/null || echo "000")"
  [[ "$code" == "200" ]]
}

www_ok() {
  local html start_html
  html="$(curl -sS --connect-timeout 5 -H "Accept: text/html" "${BASE}/" 2>/dev/null || true)"
  [[ -n "$html" ]] || return 1
  local n
  for n in "${NEEDLES[@]}"; do
    echo "$html" | grep -qF "$n" || return 1
  done
  start_html="$(curl -sS --connect-timeout 5 -H "Accept: text/html" "${BASE}/start/" 2>/dev/null || true)"
  [[ -n "$start_html" ]] || return 1
  echo "$start_html" | grep -qF "data-trial-os-flow" || return 1
  echo "$start_html" | grep -qF "trial-os-flow" || return 1
  return 0
}

echo "=== wait-dev-www-ready ==="

deadline=$((SECONDS + MAX_WAIT))
while (( SECONDS < deadline )); do
  if health_ok && www_ok; then
    echo "OK   dev www ready (${BASE}/)"
    exit 0
  fi
  sleep 2
done

echo "FAIL dev www not ready after ${MAX_WAIT}s" >&2
echo "     health: $(curl -sS -o /dev/null -w '%{http_code}' --connect-timeout 2 "${BASE}/health" 2>/dev/null || echo 000)" >&2
echo "     Run: make dev-local" >&2
exit 1
