#!/usr/bin/env bash
# Regression guard for make demo-url when dev stack is up (iter 12 ship-demo-url-verify-038).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=dev-ports.sh
source "${ROOT}/scripts/dev-ports.sh"
cd "$ROOT"

health="$(curl -sS -o /dev/null -w "%{http_code}" --connect-timeout 3 "http://127.0.0.1:${NF_DEV_PUBLIC_PORT}/health" 2>/dev/null || echo "000")"
if [[ "$health" != "200" ]]; then
  echo "SKIP verify-demo-url (dev stack health ${health})"
  exit 0
fi

chmod +x scripts/print-demo-url.sh
out="$(./scripts/print-demo-url.sh 2>&1 || true)"

if echo "$out" | grep -qE 'https?://[^[:space:]]+'; then
  if echo "$out" | grep -qE 'trycloudflare\.com|localhost|127\.0\.0\.1'; then
    echo "OK   demo-url prints shareable URL (tunnel/local)"
  elif [[ -n "${NF_STAGING_URL:-}" ]] && echo "$out" | grep -qF "${NF_STAGING_URL%/}"; then
    echo "OK   demo-url prints shareable URL (staging)"
  else
    echo "OK   demo-url prints URL output"
  fi
elif echo "$out" | grep -q 'No public demo URL configured yet'; then
  echo "SKIP verify-demo-url (stack up; no tunnel or NF_STAGING_URL configured)"
else
  echo "FAIL verify-demo-url unexpected output:" >&2
  echo "$out" >&2
  exit 1
fi
