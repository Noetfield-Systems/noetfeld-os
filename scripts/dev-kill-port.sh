#!/usr/bin/env bash
# Kill any process listening on TCP port $1 (best-effort).
set -euo pipefail
port="${1:?port required}"
if command -v lsof >/dev/null 2>&1; then
  lsof -tiTCP:"$port" -sTCP:LISTEN 2>/dev/null | xargs -r kill -9 2>/dev/null || true
fi
if command -v fuser >/dev/null 2>&1; then
  fuser -k "${port}/tcp" 2>/dev/null || true
fi
