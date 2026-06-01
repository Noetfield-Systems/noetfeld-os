#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=dev-ports.sh
source "${ROOT}/scripts/dev-ports.sh"

PUBLIC="$NF_DEV_PUBLIC_PORT"
PLATFORM="$NF_DEV_PLATFORM_PORT"
LEGACY="${NF_DEV_LEGACY_NEXT_PORT:-3000}"

probe() {
  local url="$1"
  curl -sS -o /dev/null -w "%{http_code}" --connect-timeout 2 "$url" 2>/dev/null || echo "000"
}

echo "=== Noetfield local dev status ==="
echo ""
echo "Ports:"
for p in "$PUBLIC" "$PLATFORM" "$NF_DEV_WEB_PORT" "$NF_DEV_GOV_API_PORT" "$LEGACY"; do
  if python3 -c "import socket;s=socket.socket();s.settimeout(0.3);s.connect(('127.0.0.1',int('${p}')));s.close()" 2>/dev/null; then
    echo "  :${p}  listening"
  else
    echo "  :${p}  down"
  fi
done

echo ""
echo "HTTP:"
http_line() {
  local label="$1" url="$2"
  local code
  code="$(probe "$url")"
  echo "  ${label}: ${code}  ${url}"
}
http_line website "http://127.0.0.1:${PUBLIC}/"
http_line console "http://127.0.0.1:${PUBLIC}/console"
http_line dashboard "http://127.0.0.1:${PUBLIC}/cognitive-dashboard"
http_line console-direct "http://127.0.0.1:${PLATFORM}/console"

legacy_code="$(curl -sS -o /dev/null -w "%{http_code}" --max-redirs 0 --connect-timeout 2 "http://127.0.0.1:${LEGACY}/" 2>/dev/null || echo "000")"
echo "  legacy :${LEGACY}: ${legacy_code} (expect 302 → :${PUBLIC})"

if [[ -f "${ROOT}/.dev-tunnel-url.txt" ]]; then
  echo ""
  echo "Tunnel: $(cat "${ROOT}/.dev-tunnel-url.txt")"
fi

if [[ -f "${ROOT}/.local-dev-urls.txt" ]]; then
  echo ""
  echo "URLs (after Cursor Ports forward ${PUBLIC}):"
  sed 's/^/  /' "${ROOT}/.local-dev-urls.txt"
fi

echo ""
if "${ROOT}/scripts/verify-local-dev.sh" >/dev/null 2>&1; then
  echo "Health: ALL OK — forward port ${PUBLIC} in Cursor → globe icon."
else
  echo "Health: FAILED — run: make dev-local"
  exit 1
fi
