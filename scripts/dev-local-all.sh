#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=dev-ports.sh
source "${ROOT}/scripts/dev-ports.sh"

PUBLIC_PORT="$NF_DEV_PUBLIC_PORT"
URLS_FILE="${ROOT}/.local-dev-urls.txt"
PROXY_PID_FILE="${ROOT}/.dev-proxy.pid"
PROXY_LOG="${ROOT}/.dev-proxy.log"
REDIRECT_PID_FILE="${ROOT}/.dev-redirect.pid"
REDIRECT_LOG="${ROOT}/.dev-redirect.log"

chmod +x "${ROOT}/scripts/ensure-platform-console.sh" \
  "${ROOT}/scripts/dev-cognitive-dashboard.sh" \
  "${ROOT}/scripts/dev-kill-port.sh" \
  "${ROOT}/scripts/dev-local-tunnel-bg.sh" \
  "${ROOT}/scripts/dev-unified-proxy.py" \
  "${ROOT}/scripts/dev-port-redirects.py" \
  "${ROOT}/scripts/verify-local-dev.sh" \
  "${ROOT}/scripts/dev-local-down.sh" 2>/dev/null || true

kill_stale() {
  if [[ -f "${ROOT}/scripts/dev-local-down.sh" ]]; then
    bash "${ROOT}/scripts/dev-local-down.sh" >/dev/null 2>&1 || true
  fi
  sleep 1
}

echo "=== Noetfield local dev ==="
kill_stale

kill_port() {
  bash "${ROOT}/scripts/dev-kill-port.sh" "$1" 2>/dev/null || true
}
LEGACY_PORT="${NF_DEV_LEGACY_NEXT_PORT:-3000}"
# Free legacy port (apps/web default, orphan next-server) so redirect → 13080 works.
kill_port "$LEGACY_PORT"
pkill -9 -f "next-server \\(v" 2>/dev/null || true
sleep 1

export PLATFORM_CONSOLE_PORT="$NF_DEV_PLATFORM_PORT"
export COGNITIVE_DASHBOARD_PORT="$NF_DEV_WEB_PORT"
export COGNITIVE_DASHBOARD_API_PORT="$NF_DEV_GOV_API_PORT"
export NF_DEV_PLATFORM_INTERNAL="http://127.0.0.1:${NF_DEV_PLATFORM_PORT}"
export NF_DEV_NEXT_INTERNAL="http://127.0.0.1:${NF_DEV_WEB_PORT}"

"${ROOT}/scripts/ensure-platform-console.sh"

WEB_URL="http://127.0.0.1:${COGNITIVE_DASHBOARD_PORT}/cognitive-dashboard"
if ! curl -sf -o /dev/null --connect-timeout 2 "$WEB_URL" 2>/dev/null; then
  echo "Starting cognitive dashboard on ${COGNITIVE_DASHBOARD_PORT}…"
  nohup env COGNITIVE_DASHBOARD_PORT="$COGNITIVE_DASHBOARD_PORT" \
    COGNITIVE_DASHBOARD_API_PORT="$COGNITIVE_DASHBOARD_API_PORT" \
    bash "${ROOT}/scripts/dev-cognitive-dashboard.sh" >>"${ROOT}/.cognitive-dashboard.log" 2>&1 &
  echo $! >"${ROOT}/.cognitive-dashboard.pid"
  for _ in $(seq 1 60); do
    curl -sf -o /dev/null --connect-timeout 2 "$WEB_URL" 2>/dev/null && break
    sleep 1
  done
fi

nohup env NF_DEV_PUBLIC_PORT="$PUBLIC_PORT" \
  NF_DEV_PLATFORM_PORT="$NF_DEV_PLATFORM_PORT" \
  python3 "${ROOT}/scripts/dev-unified-proxy.py" >>"$PROXY_LOG" 2>&1 &
echo $! >"$PROXY_PID_FILE"

nohup env NF_DEV_PUBLIC_PORT="$PUBLIC_PORT" NF_DEV_LEGACY_NEXT_PORT="$LEGACY_PORT" \
  python3 "${ROOT}/scripts/dev-port-redirects.py" >>"$REDIRECT_LOG" 2>&1 &
echo $! >"$REDIRECT_PID_FILE"

sleep 2
legacy_code="$(curl -sS -o /dev/null -w "%{http_code}" --max-redirs 0 --connect-timeout 2 \
  "http://127.0.0.1:${LEGACY_PORT}/" 2>/dev/null || echo "000")"
if [[ "$legacy_code" != "302" ]]; then
  echo "WARN: :${LEGACY_PORT} redirect not active (${legacy_code}) — use http://localhost:${PUBLIC_PORT}/ only" >&2
fi

if [[ "${NF_DEV_AUTO_TUNNEL:-0}" == "1" ]]; then
  bash "${ROOT}/scripts/dev-local-tunnel-bg.sh" || true
fi

cat >"$URLS_FILE" <<EOF
WEBSITE=http://localhost:${PUBLIC_PORT}/
CONSOLE=http://localhost:${PUBLIC_PORT}/console
CONSOLE_DIRECT=http://localhost:${NF_DEV_PLATFORM_PORT}/console
DASHBOARD=http://localhost:${PUBLIC_PORT}/cognitive-dashboard
EOF

echo ""
cat "$URLS_FILE"
echo ""

if "${ROOT}/scripts/verify-local-dev.sh"; then
  echo ""
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "  Servers are UP in this workspace (verified)."
  echo "  Your Mac browser will NOT see them until you:"
  echo "    • Cursor → Ports → forward ${PUBLIC_PORT} (+ ${NF_DEV_PLATFORM_PORT}) → globe"
  echo "    • OR run make dev-local on your Mac"
  echo "    • OR make dev-local-tunnel for a shareable HTTPS link"
  echo "  Open: http://localhost:${PUBLIC_PORT}/  (after forwarding)"
  if [[ -f "${ROOT}/.dev-tunnel-url.txt" ]]; then
    echo "  Public tunnel: $(cat "${ROOT}/.dev-tunnel-url.txt")"
  fi
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
else
  echo "Some checks failed — see logs:" >&2
  echo "  $PROXY_LOG" >&2
  echo "  ${ROOT}/.platform-console.log" >&2
  exit 1
fi
