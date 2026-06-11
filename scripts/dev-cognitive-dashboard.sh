#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=dev-ports.sh
source "${ROOT}/scripts/dev-ports.sh"

BACKEND="$ROOT/governance-console/backend"
FRONTEND="$ROOT/governance-console/frontend"
DB_FILE="$BACKEND/.dev_governance.db"
ENV_FILE="$ROOT/.dev-cognitive-dashboard.env"
API_PID=""

export DATABASE_URL="${DATABASE_URL:-sqlite:///${DB_FILE}}"

WEB_PORT="$COGNITIVE_DASHBOARD_PORT"
API_PORT="$COGNITIVE_DASHBOARD_API_PORT"
# production = next build + next start (stable assets via :13080). dev = next dev (hot reload).
DASHBOARD_MODE="${NF_DASHBOARD_MODE:-production}"

kill_port() {
  local p="$1"
  if command -v lsof >/dev/null 2>&1; then
    lsof -tiTCP:"$p" -sTCP:LISTEN 2>/dev/null | xargs -r kill -9 2>/dev/null || true
  fi
}

cleanup() { [[ -n "$API_PID" ]] && kill "$API_PID" 2>/dev/null || true; }
trap cleanup EXIT INT TERM

kill_port "$WEB_PORT"
kill_port "$API_PORT"
sleep 1

export NEXT_PUBLIC_API_URL="${NEXT_PUBLIC_API_URL:-}"
export NEXT_PUBLIC_WEB_PORT="$WEB_PORT"
export NEXT_PUBLIC_PLATFORM_CONSOLE_PORT="$PLATFORM_CONSOLE_PORT"
export NEXT_PUBLIC_PLATFORM_CONSOLE_URL="http://127.0.0.1:${PLATFORM_CONSOLE_PORT}/console"

cat >"$ENV_FILE" <<EOF
export COGNITIVE_DASHBOARD_PORT=$WEB_PORT
export NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
export NEXT_PUBLIC_WEB_PORT=$WEB_PORT
export PLATFORM_CONSOLE_PORT=$PLATFORM_CONSOLE_PORT
COGNITIVE_DASHBOARD_URL=http://localhost:${WEB_PORT}/cognitive-dashboard
PLATFORM_CONSOLE_URL=http://localhost:${PLATFORM_CONSOLE_PORT}/console
UNIFIED_URL=http://localhost:${NF_DEV_PUBLIC_PORT}/cognitive-dashboard
EOF

cd "$BACKEND"
bash "${ROOT}/scripts/dev-python.sh" -m pip install -q -r requirements.txt
bash "${ROOT}/scripts/dev-python.sh" -m uvicorn main:app --host 0.0.0.0 --port "$API_PORT" &
API_PID=$!

deadline=$((SECONDS + 60))
until curl -sf "http://127.0.0.1:${API_PORT}/health" >/dev/null 2>&1; do
  kill -0 "$API_PID" 2>/dev/null || exit 1
  (( SECONDS >= deadline )) && exit 1
  sleep 1
done

cd "$FRONTEND"
[[ -d node_modules ]] || npm install

echo ">>> Unified: http://localhost:${NF_DEV_PUBLIC_PORT}/cognitive-dashboard"
echo ">>> Direct:  http://localhost:${WEB_PORT}/cognitive-dashboard"
echo ">>> Console: http://localhost:${NF_DEV_PUBLIC_PORT}/console"
echo ">>> Mode:    ${DASHBOARD_MODE}"

if [[ "$DASHBOARD_MODE" == "production" ]]; then
  if [[ ! -f .next/BUILD_ID ]] || [[ "${NF_DEV_FORCE_DASHBOARD_BUILD:-0}" == "1" ]]; then
    echo "Building governance console UI (production)…"
    npm run build
  fi
  exec env NF_DASHBOARD_MODE=production PORT="$WEB_PORT" COGNITIVE_DASHBOARD_PORT="$WEB_PORT" \
    NEXT_PUBLIC_WEB_PORT="$WEB_PORT" npm run dev
fi

echo ">>> Dev mode (next dev) — set NF_DASHBOARD_MODE=production for pro performance"
exec env NF_DASHBOARD_MODE=dev PORT="$WEB_PORT" COGNITIVE_DASHBOARD_PORT="$WEB_PORT" \
  NEXT_PUBLIC_WEB_PORT="$WEB_PORT" npm run dev
