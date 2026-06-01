#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=dev-ports.sh
source "${ROOT}/scripts/dev-ports.sh"

PORT="$WWW_DEV_PORT"
URL="http://127.0.0.1:${PORT}/"
PID_FILE="${ROOT}/.www-dev.pid"
LOG_FILE="${ROOT}/.www-dev.log"

if curl -sf -o /dev/null --connect-timeout 2 "$URL" 2>/dev/null; then
  body="$(curl -sf --connect-timeout 2 "$URL" | head -c 5000)"
  if echo "$body" | grep -qi noetfield; then
    echo "OK  $URL"
    exit 0
  fi
fi

if [[ -f "$PID_FILE" ]]; then
  kill "$(cat "$PID_FILE")" 2>/dev/null || true
  rm -f "$PID_FILE"
fi
if command -v lsof >/dev/null 2>&1; then
  lsof -tiTCP:"$PORT" -sTCP:LISTEN 2>/dev/null | xargs -r kill -9 2>/dev/null || true
fi
sleep 1

cd "$ROOT"
nohup python3 -m http.server "$PORT" --bind 0.0.0.0 >>"$LOG_FILE" 2>&1 &
echo $! >"$PID_FILE"

for _ in $(seq 1 20); do
  if curl -sf -o /dev/null --connect-timeout 2 "$URL" 2>/dev/null; then
    echo "OK  $URL"
    exit 0
  fi
  sleep 1
done
echo "FAIL  $URL — see $LOG_FILE" >&2
exit 1
