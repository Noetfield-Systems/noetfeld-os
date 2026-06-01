#!/usr/bin/env bash
# Start both local dev surfaces and print URLs (remote workspace → use Cursor Ports panel).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
URLS_FILE="${ROOT}/.local-dev-urls.txt"

chmod +x "${ROOT}/scripts/ensure-platform-console.sh" "${ROOT}/scripts/dev-cognitive-dashboard.sh" 2>/dev/null || true

echo "Starting platform console (8001)…"
"${ROOT}/scripts/ensure-platform-console.sh"

if ! curl -sf -o /dev/null --connect-timeout 2 http://127.0.0.1:3000/cognitive-dashboard 2>/dev/null; then
  echo "Starting cognitive dashboard (3000) in background…"
  nohup env COGNITIVE_DASHBOARD_PORT=3000 bash "${ROOT}/scripts/dev-cognitive-dashboard.sh" >>"${ROOT}/.cognitive-dashboard.log" 2>&1 &
  echo $! >"${ROOT}/.cognitive-dashboard.pid"
  for _ in $(seq 1 45); do
    curl -sf -o /dev/null --connect-timeout 2 http://127.0.0.1:3000/cognitive-dashboard 2>/dev/null && break
    sleep 1
  done
fi

cat >"$URLS_FILE" <<EOF
# Dev servers (inside this workspace / VM)
COGNITIVE_DASHBOARD=http://127.0.0.1:3000/cognitive-dashboard
PLATFORM_CONSOLE=http://127.0.0.1:8001/console

# If your browser is on your Mac but code runs in Cursor Cloud:
# 1. Open the Ports tab (bottom panel)
# 2. Forward ports 3000 and 8001
# 3. Click the globe icon or use the forwarded localhost links there
#
# Do NOT expect Mac localhost to work until Ports shows them as forwarded.
EOF

cat "$URLS_FILE"
echo ""
if curl -sf -o /dev/null --connect-timeout 2 http://127.0.0.1:3000/cognitive-dashboard; then
  echo "OK  cognitive dashboard :3000"
else
  echo "WARN cognitive dashboard not up — run: make cognitive-dashboard-dev"
fi
if curl -sf -o /dev/null --connect-timeout 2 http://127.0.0.1:8001/console; then
  echo "OK  platform console :8001"
else
  echo "WARN platform console not up — run: make platform-console-up"
fi
