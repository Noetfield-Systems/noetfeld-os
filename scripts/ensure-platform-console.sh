#!/usr/bin/env bash
# Start platform API on 8001 if /console is not reachable.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PORT="${PLATFORM_CONSOLE_PORT:-8001}"
URL="http://127.0.0.1:${PORT}/console"
PID_FILE="${ROOT}/.platform-console.pid"
LOG_FILE="${ROOT}/.platform-console.log"

if curl -sf -o /dev/null --connect-timeout 2 "$URL" 2>/dev/null; then
  echo "OK  $URL"
  exit 0
fi

if [[ -f "$PID_FILE" ]]; then
  old="$(cat "$PID_FILE")"
  if kill -0 "$old" 2>/dev/null; then
    echo "Waiting for $URL (pid $old)…"
    for _ in $(seq 1 30); do
      curl -sf -o /dev/null --connect-timeout 2 "$URL" && echo "OK  $URL" && exit 0
      sleep 1
    done
  fi
fi

echo "Starting platform console on port ${PORT}…"
nohup env PLATFORM_CONSOLE_PORT="$PORT" bash "${ROOT}/scripts/dev-platform-console.sh" >>"$LOG_FILE" 2>&1 &
echo $! >"$PID_FILE"

for _ in $(seq 1 45); do
  if curl -sf -o /dev/null --connect-timeout 2 "$URL" 2>/dev/null; then
    echo "OK  $URL"
    echo "Log: $LOG_FILE"
    exit 0
  fi
  sleep 1
done

echo "FAIL  $URL not reachable. See $LOG_FILE" >&2
exit 1
