#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if ! command -v docker >/dev/null 2>&1; then
  echo "Docker not found — starting local API (SQLite) only."
  echo "Run: cd backend && DATABASE_URL=sqlite:///./governance_console.db uvicorn main:app --reload"
  echo "Run: cd frontend && npm run dev"
  exit 1
fi
docker compose up -d --build --wait postgres api web
echo ""
echo "Governance Console ready:"
echo "  Web   http://localhost:3000"
echo "  API   http://localhost:8000"
echo "  Docs  http://localhost:8000/docs"
echo ""
echo "E2E:  make e2e"
