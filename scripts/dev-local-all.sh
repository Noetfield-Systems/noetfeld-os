#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=dev-ports.sh
source "${ROOT}/scripts/dev-ports.sh"

URLS_FILE="${ROOT}/.local-dev-urls.txt"
chmod +x "${ROOT}/scripts/ensure-platform-console.sh" \
  "${ROOT}/scripts/ensure-www.sh" \
  "${ROOT}/scripts/dev-cognitive-dashboard.sh" 2>/dev/null || true

echo "=== Noetfield local dev ==="
"${ROOT}/scripts/ensure-www.sh"
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
# Open in browser (Cursor: forward these ports first)
WEBSITE=http://localhost:${WWW_DEV_PORT}/
COGNITIVE_DASHBOARD=http://localhost:${COGNITIVE_DASHBOARD_PORT}/cognitive-dashboard
PLATFORM_CONSOLE=http://localhost:${PLATFORM_CONSOLE_PORT}/console
GOV_API=http://127.0.0.1:${COGNITIVE_DASHBOARD_API_PORT}
EOF

echo ""
cat "$URLS_FILE"
echo ""
curl -sf -o /dev/null "http://127.0.0.1:${WWW_DEV_PORT}/" && echo "OK  website (www)     :${WWW_DEV_PORT}"
curl -sf -o /dev/null "$WEB_URL" && echo "OK  cognitive dashboard :${COGNITIVE_DASHBOARD_PORT}"
curl -sf -o /dev/null "http://127.0.0.1:${PLATFORM_CONSOLE_PORT}/console" && echo "OK  platform console    :${PLATFORM_CONSOLE_PORT}"
