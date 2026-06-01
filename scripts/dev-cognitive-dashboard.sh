#!/usr/bin/env bash
# Start governance-console API + Next dev server for http://localhost:3000/cognitive-dashboard
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BACKEND="$ROOT/governance-console/backend"
FRONTEND="$ROOT/governance-console/frontend"
DB_FILE="$BACKEND/.dev_governance.db"
API_PID_FILE="/tmp/noetfield-cognitive-dashboard-api.pid"
WEB_PID_FILE="/tmp/noetfield-cognitive-dashboard-web.pid"

export DATABASE_URL="${DATABASE_URL:-sqlite:///${DB_FILE}}"
export NEXT_PUBLIC_API_URL="${NEXT_PUBLIC_API_URL:-http://127.0.0.1:8000}"

stop_existing() {
  for f in "$API_PID_FILE" "$WEB_PID_FILE"; do
    if [[ -f "$f" ]]; then
      pid="$(cat "$f")"
      kill "$pid" 2>/dev/null || true
      rm -f "$f"
    fi
  done
}

wait_http() {
  local url="$1"
  local label="$2"
  local deadline=$((SECONDS + 90))
  while (( SECONDS < deadline )); do
    if curl -sf -o /dev/null "$url" 2>/dev/null; then
      echo "OK  $label $url"
      return 0
    fi
    sleep 1
  done
  echo "FAIL timeout waiting for $label at $url" >&2
  return 1
}

stop_existing

cd "$BACKEND"
python3 -m pip install -q -r requirements.txt
python3 -m uvicorn main:app --host 127.0.0.1 --port 8000 &
echo $! >"$API_PID_FILE"

cd "$FRONTEND"
if [[ ! -d node_modules ]]; then
  npm install
fi
npm run dev &
echo $! >"$WEB_PID_FILE"

wait_http "http://127.0.0.1:8000/health" "api-health"
wait_http "http://127.0.0.1:3000/cognitive-dashboard" "cognitive-dashboard"

echo ""
echo "Cognitive dashboard ready:"
echo "  http://localhost:3000/cognitive-dashboard"
echo "  API http://localhost:8000/docs"
echo ""
echo "Stop: kill \$(cat $API_PID_FILE) \$(cat $WEB_PID_FILE)"
