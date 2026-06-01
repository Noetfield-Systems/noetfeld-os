#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BACKEND="$ROOT/governance-console/backend"
FRONTEND="$ROOT/governance-console/frontend"
DB_FILE="$BACKEND/.dev_governance.db"
ENV_FILE="$ROOT/.dev-cognitive-dashboard.env"
API_PID=""
REDIRECT_PID=""

export DATABASE_URL="${DATABASE_URL:-sqlite:///${DB_FILE}}"

free_port() {
  python3 - "$@" <<'PY'
import socket, sys
for p in sys.argv[1:]:
    p = int(p)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind(("127.0.0.1", p))
        print(p)
        sys.exit(0)
    except OSError:
        s.close()
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(("127.0.0.1", 0))
print(s.getsockname()[1])
s.close()
PY
}

cleanup() {
  [[ -n "${REDIRECT_PID:-}" ]] && kill "$REDIRECT_PID" 2>/dev/null || true
  [[ -n "$API_PID" ]] && kill "$API_PID" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

WEB_PORT="$(free_port "${COGNITIVE_DASHBOARD_PORT:-3010}" 3000 3100 3200)"
API_PORT="${COGNITIVE_DASHBOARD_API_PORT:-$(free_port 8000 8001 8002 8003)}"
export NEXT_PUBLIC_API_URL="${NEXT_PUBLIC_API_URL:-http://127.0.0.1:${API_PORT}}"

cat >"$ENV_FILE" <<EOF
export COGNITIVE_DASHBOARD_PORT=$WEB_PORT
export NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
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

DASH_URL="http://localhost:${WEB_PORT}/cognitive-dashboard"
if [[ "$WEB_PORT" != "3000" ]]; then
  if free_port 3000 | grep -q '^3000$'; then
    node -e "
const http=require('http');
const t='http://127.0.0.1:${WEB_PORT}';
http.createServer((q,s)=>{const u=new URL(q.url||'/','http://x');s.writeHead(302,{Location:t+u.pathname+u.search});s.end();}).listen(3000,'0.0.0.0');
" &
    REDIRECT_PID=$!
  fi
fi

echo "$DASH_URL"

exec env PORT="$WEB_PORT" COGNITIVE_DASHBOARD_PORT="$WEB_PORT" npm run dev
