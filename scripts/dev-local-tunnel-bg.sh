#!/usr/bin/env bash
# Start localtunnel in background; write public URL to .dev-tunnel-url.txt
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=dev-ports.sh
source "${ROOT}/scripts/dev-ports.sh"

PORT="$NF_DEV_PUBLIC_PORT"
LOG="${ROOT}/.dev-tunnel.log"
URL_FILE="${ROOT}/.dev-tunnel-url.txt"
PID_FILE="${ROOT}/.dev-tunnel.pid"

extract_url() {
  grep -oE 'https://[a-zA-Z0-9.-]+\.(loca\.lt|localtunnel\.me)' "$LOG" 2>/dev/null | head -1 \
    || sed -n 's/.*your url is: \(https:\/\/[^ ]*\).*/\1/p' "$LOG" 2>/dev/null | head -1
}

if [[ -f "$PID_FILE" ]] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
  url="$(extract_url)"
  [[ -n "$url" ]] && echo "$url" >"$URL_FILE"
  [[ -f "$URL_FILE" ]] && echo "Tunnel already running: $(cat "$URL_FILE")"
  exit 0
fi

if ! curl -sf -o /dev/null --connect-timeout 2 "http://127.0.0.1:${PORT}/" 2>/dev/null; then
  echo "dev-local-tunnel-bg: port ${PORT} not up" >&2
  exit 1
fi

: >"$LOG"
nohup npx --yes localtunnel --port "$PORT" >>"$LOG" 2>&1 &
echo $! >"$PID_FILE"

for _ in $(seq 1 45); do
  url="$(extract_url)"
  if [[ -n "$url" ]]; then
    echo "$url" >"$URL_FILE"
    echo "Tunnel: $url"
    exit 0
  fi
  sleep 1
done

echo "Tunnel started (PID $(cat "$PID_FILE")) — URL pending; see $LOG" >&2
exit 0
