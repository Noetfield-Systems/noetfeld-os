#!/usr/bin/env bash
# Expose the unified dev server (13080) via a public HTTPS URL when Cursor port
# forwarding is unavailable. Requires: make dev-local (or equivalent) already running.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=dev-ports.sh
source "${ROOT}/scripts/dev-ports.sh"

PORT="$NF_DEV_PUBLIC_PORT"
URL="http://127.0.0.1:${PORT}/"

if ! curl -sf -o /dev/null --connect-timeout 2 "$URL" 2>/dev/null; then
  echo "Nothing listening on ${URL}" >&2
  echo "Run: make dev-local" >&2
  exit 1
fi

echo "Tunneling ${URL} (Ctrl+C to stop)…"
echo "Share the URL printed below — it is NOT localhost on your Mac."
exec npx --yes localtunnel --port "$PORT"
