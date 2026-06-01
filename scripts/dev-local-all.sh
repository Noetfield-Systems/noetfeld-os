#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=dev-ports.sh
source "${ROOT}/scripts/dev-ports.sh"

URLS_FILE="${ROOT}/.local-dev-urls.txt"
chmod +x "${ROOT}/scripts/ensure-platform-console.sh" "${ROOT}/scripts/dev-cognitive-dashboard.sh" 2>/dev/null || true

"${ROOT}/scripts/ensure-platform-console.sh"

WEB_URL="http://127.0.0.1:${COGNITIVE_DASHBOARD_PORT}/cognitive-dashboard"
if ! curl -sf -o /dev/null --connect-timeout 2 "$WEB_URL" 2>/dev/null; then
  nohup env COGNITIVE_DASHBOARD_PORT="$COGNITIVE_DASHBOARD_PORT" \
    COGNITIVE_DASHBOARD_API_PORT="$COGNITIVE_DASHBOARD_API_PORT" \
    bash "${ROOT}/scripts/dev-cognitive-dashboard.sh" >>"${ROOT}/.cognitive-dashboard.log" 2>&1 &
  echo $! >"${ROOT}/.cognitive-dashboard.pid"
  for _ in $(seq 1 45); do
    curl -sf -o /dev/null --connect-timeout 2 "$WEB_URL" 2>/dev/null && break
    sleep 1
  done
fi

cat >"$URLS_FILE" <<EOF
COGNITIVE_DASHBOARD=http://localhost:${COGNITIVE_DASHBOARD_PORT}/cognitive-dashboard
PLATFORM_CONSOLE=http://localhost:${PLATFORM_CONSOLE_PORT}/console
GOV_API=http://127.0.0.1:${COGNITIVE_DASHBOARD_API_PORT}
EOF

cat "$URLS_FILE"
curl -sf -o /dev/null "$WEB_URL" && echo "OK  dashboard :${COGNITIVE_DASHBOARD_PORT}"
curl -sf -o /dev/null "http://127.0.0.1:${PLATFORM_CONSOLE_PORT}/console" && echo "OK  console :${PLATFORM_CONSOLE_PORT}"
