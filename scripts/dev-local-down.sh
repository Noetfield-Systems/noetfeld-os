#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=dev-ports.sh
source "${ROOT}/scripts/dev-ports.sh"

kill_port() {
  local p="$1"
  if command -v lsof >/dev/null 2>&1; then
    lsof -tiTCP:"$p" -sTCP:LISTEN 2>/dev/null | xargs -r kill -9 2>/dev/null || true
  fi
}

for f in .platform-console.pid .cognitive-dashboard.pid .dev-proxy.pid .dev-redirect.pid .www-dev.pid; do
  if [[ -f "$ROOT/$f" ]]; then
    kill "$(cat "$ROOT/$f")" 2>/dev/null || true
    rm -f "$ROOT/$f"
  fi
done

kill_port "$NF_DEV_PUBLIC_PORT"
kill_port "$NF_DEV_PLATFORM_PORT"
kill_port "$NF_DEV_WEB_PORT"
kill_port "$NF_DEV_GOV_API_PORT"
kill_port 3000

pkill -f "dev-unified-proxy.py" 2>/dev/null || true
pkill -f "dev-port-redirects.py" 2>/dev/null || true
pkill -f "next dev --port" 2>/dev/null || true

echo "Stopped local dev processes."
