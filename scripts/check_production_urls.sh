#!/usr/bin/env bash
# check_production_urls.sh — curl smoke for www + platform + GEL API (UPG-0018)
set -euo pipefail

fail=0
check() {
  local name="$1"
  local url="$2"
  local code
  code=$(curl -sS -o /dev/null -w '%{http_code}' --max-time 15 "$url" || echo "000")
  if [[ "$code" =~ ^2 ]]; then
    echo "OK   $name ($code) $url"
  else
    echo "FAIL $name ($code) $url" >&2
    fail=1
  fi
}

check "www home" "https://www.noetfield.com/"
check "www gel" "https://www.noetfield.com/gel/"
check "www ai-value-os" "https://www.noetfield.com/ai-value-governance-os/"
check "platform health" "https://platform.noetfield.com/health"
check "gel-api health" "https://api.noetfield.com/health"
check "gel-api readiness" "https://api.noetfield.com/readiness"

exit "$fail"
