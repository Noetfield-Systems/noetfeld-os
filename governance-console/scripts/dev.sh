#!/usr/bin/env bash
# Start postgres (docker), backend, and frontend for local dev.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

docker compose up -d postgres
echo "Waiting for Postgres…"
sleep 3

export DATABASE_URL="${DATABASE_URL:-postgresql+psycopg://postgres:postgres@localhost:5433/governance_console}"

(
  cd "$ROOT/backend"
  if [[ ! -d .venv ]]; then python3 -m venv .venv; fi
  source .venv/bin/activate
  pip install -q -r requirements.txt
  exec uvicorn main:app --reload --port 8000
) &
BACK_PID=$!

(
  cd "$ROOT/frontend"
  npm install --silent
  export NEXT_PUBLIC_API_URL=http://localhost:8000
  exec npm run dev
) &
FRONT_PID=$!

trap 'kill $BACK_PID $FRONT_PID 2>/dev/null' EXIT
echo "Use: make dev-local  →  http://localhost:13080/"
wait
