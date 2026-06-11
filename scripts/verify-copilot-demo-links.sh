#!/usr/bin/env bash
# Verify copilot/demo CTA hrefs return 200 on unified dev proxy.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=dev-ports.sh
source "${ROOT}/scripts/dev-ports.sh"

BASE="http://127.0.0.1:${NF_DEV_PUBLIC_PORT}"
DEMO_HTML="${ROOT}/copilot/demo/index.html"
fail=0

echo "=== verify-copilot-demo-links ==="

if [[ ! -f "$DEMO_HTML" ]]; then
  echo "FAIL copilot demo page missing: $DEMO_HTML" >&2
  exit 1
fi

# Paths required by GTM demo script (with or without trailing slash)
paths=(
  "/cognitive-dashboard"
  "/evaluate"
  "/workspace"
  "/workspace/connectors"
)

for path in "${paths[@]}"; do
  code="$(curl -sS -o /dev/null -w "%{http_code}" --connect-timeout 5 "${BASE}${path}" 2>/dev/null || echo "000")"
  if [[ "$code" == "200" ]]; then
    echo "OK   CTA ${path} (${code})"
  else
    # Retry with trailing slash (demo HTML uses trailing slashes)
    code_slash="$(curl -sS -o /dev/null -w "%{http_code}" --connect-timeout 5 "${BASE}${path}/" 2>/dev/null || echo "000")"
    if [[ "$code_slash" == "200" ]]; then
      echo "OK   CTA ${path}/ (${code_slash})"
    else
      echo "FAIL CTA ${path} (${code}, slash ${code_slash})" >&2
      fail=1
    fi
  fi
done

# Confirm hrefs exist in demo HTML
for path in "${paths[@]}"; do
  if ! grep -qF "href=\"${path}/\"" "$DEMO_HTML" && ! grep -qF "href=\"${path}\"" "$DEMO_HTML"; then
    echo "FAIL copilot/demo missing href for ${path}" >&2
    fail=1
  fi
done
if [[ "$fail" -eq 0 ]]; then
  echo "OK   demo HTML contains required CTA hrefs"
fi

if [[ "$fail" -eq 0 ]]; then
  echo ""
  echo "verify-copilot-demo-links passed."
  exit 0
fi
exit 1
