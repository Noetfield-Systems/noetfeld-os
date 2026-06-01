#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BACKEND="$ROOT/governance-console/backend"
FRONTEND="$ROOT/governance-console/frontend"
DB_FILE="$BACKEND/.dev_governance.db"
ENV_FILE="$ROOT/.dev-cognitive-dashboard.env"
API_PID=""

export DATABASE_URL="${DATABASE_URL:-sqlite:///${DB_FILE}}"

WEB_PORT="${COGNITIVE_DASHBOARD_PORT:-3000}"
API_PORT="${COGNITIVE_DASHBOARD_API_PORT:-8000}"

free_port() {
  python3 - "$1" <<'PY'
import socket, sys
p = int(sys.argv[1])
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    s.bind(("0.0.0.0", p))
    print(p)
except OSError:
    print("")
s.close()
PY
}

stop_port() {
  local p="$1"
  if command -v lsof >/dev/null 2>&1; then
    lsof -tiTCP:"$p" -sTCP:LISTEN 2>/dev/null | xargs -r kill -9 2>/dev/null || true
  fi
}

cleanup() {
  [[ -n "$API_PID" ]] && kill "$API_PID" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

if [[ -z "$(free_port "$WEB_PORT")" ]]; then
  stop_port "$WEB_PORT"
  sleep 1
fi
if [[ -z "$(free_port "$WEB_PORT")" ]]; then
  WEB_PORT="$(python3 -c 'import socket;s=socket.socket();s.bind(("0.0.0.0",0));print(s.getsockname()[1]);s.close()')"
fi

if [[ -z "$(free_port "$API_PORT")" ]]; then
  stop_port "$API_PORT"
  sleep 1
fi
if [[ -z "$(free_port "$API_PORT")" ]]; then
  API_PORT="$(python3 -c 'import socket;s=socket.socket();s.bind(("0.0.0.0",0));print(s.getsockname()[1]);s.close()')"
fi

export NEXT_PUBLIC_API_URL="${NEXT_PUBLIC_API_URL:-http://127.0.0.1:${API_PORT}}"
export NEXT_PUBLIC_WEB_PORT="$WEB_PORT"

cat >"$ENV_FILE" <<EOF
export COGNITIVE_DASHBOARD_PORT=$WEB_PORT
export NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
export NEXT_PUBLIC_WEB_PORT=$WEB_PORT
COGNITIVE_DASHBOARD_URL=http://localhost:${WEB_PORT}/cognitive-dashboard
EOF

cd "$BACKEND"
python3 -m pip install -q -r requirements.txt
python3 -m uvicorn main:app --host 0.0.0.0 --port "$API_PORT" &
API_PID=$!

deadline=$((SECONDS + 60))
until curl -sf "http://127.0.0.1:${API_PORT}/health" >/dev/null 2>&1; do
  kill -0 "$API_PID" 2>/dev/null || exit 1
  (( SECONDS >= deadline )) && exit 1
  sleep 1
done

cd "$FRONTEND"
[[ -d node_modules ]] || npm install

echo "COGNITIVE_DASHBOARD_URL=http://localhost:${WEB_PORT}/cognitive-dashboard"
echo "Ports → web:${WEB_PORT} api:${API_PORT}"

exec env PORT="$WEB_PORT" COGNITIVE_DASHBOARD_PORT="$WEB_PORT" NEXT_PUBLIC_WEB_PORT="$WEB_PORT" npm run dev
