#!/usr/bin/env bash
# Optional smoke against ASF-provided staging URL (no secrets in repo).
set -euo pipefail

BASE="${NF_STAGING_URL:-}"
if [[ -z "$BASE" ]]; then
  echo "Set NF_STAGING_URL (e.g. https://staging.example.com) and re-run." >&2
  exit 1
fi
BASE="${BASE%/}"

echo "=== staging-smoke ==="
for path in /health / /workspace/ /copilot/pilot/; do
  code="$(curl -sS -o /dev/null -w "%{http_code}" --connect-timeout 10 "${BASE}${path}" 2>/dev/null || echo "000")"
  echo "${path} -> ${code}"
  [[ "$code" =~ ^[23] ]] || { echo "FAIL ${path}" >&2; exit 1; }
done
echo "staging-smoke passed."
