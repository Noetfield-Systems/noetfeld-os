#!/usr/bin/env bash
# Print shareable public demo URL (tunnel or staging) — no secrets in repo.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TUNNEL_FILE="${ROOT}/.dev-tunnel-url.txt"
DEMO_PATH="/copilot/demo/"

base=""
source=""

if [[ -f "$TUNNEL_FILE" ]]; then
  base="$(tr -d '[:space:]' <"$TUNNEL_FILE")"
  if [[ -n "$base" ]]; then
    source="tunnel (.dev-tunnel-url.txt)"
  fi
fi

if [[ -z "$base" && -n "${NF_STAGING_URL:-}" ]]; then
  base="${NF_STAGING_URL%/}"
  source="NF_STAGING_URL"
fi

if [[ -n "$base" ]]; then
  echo "Noetfield public demo (source: ${source})"
  echo "  Homepage:    ${base}/"
  echo "  5-min demo:  ${base}${DEMO_PATH}"
  echo "  Workspace:   ${base}/workspace/"
  echo "  Connectors:  ${base}/workspace/connectors/"
  exit 0
fi

echo "No public demo URL configured yet."
echo ""
echo "Option A — local tunnel (design partner on your Mac):"
echo "  make dev-local"
echo "  make dev-local-tunnel-bg"
echo "  make demo-url"
echo ""
echo "Option B — staging smoke:"
echo "  export NF_STAGING_URL=https://your-staging-host"
echo "  make staging-smoke"
echo "  make demo-url"
exit 0
