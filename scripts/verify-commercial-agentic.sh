#!/usr/bin/env bash
# Commercial agentic polish gate — demo, trial, reference doc, buyer copy.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
fail=0

echo "=== verify-commercial-agentic ==="

require_file() {
  local rel="$1"
  local min="${2:-800}"
  if [[ ! -f "$rel" ]]; then
    echo "FAIL missing: $rel" >&2
    fail=1
    return
  fi
  local size
  size="$(wc -c < "$rel" | tr -d ' ')"
  if [[ "$size" -lt "$min" ]]; then
    echo "FAIL $rel too small ($size)" >&2
    fail=1
    return
  fi
  echo "OK   $rel ($size bytes)"
}

require_file docs/strategy/COMMERCIAL_AGENTIC_UI_REFERENCE_v1.md 3000
require_file copilot/demo/index.html 5000
require_file copilot/trial/index.html 4000

demo="$(cat copilot/demo/index.html)"
trial="$(cat copilot/trial/index.html)"
header="$(cat assets/partials/header.html)"

for phrase in "nf26-demoStepper" "nf26-eventTrace" "nf26-progressRing" "Human-in-the-loop" "evaluate"; do
  if ! grep -qiF "$phrase" <<< "$demo"; then
    echo "FAIL copilot/demo missing: $phrase" >&2
    fail=1
  fi
done
echo "OK   copilot/demo has agentic demo patterns"

for phrase in "sandbox" "three contract" "Copilot Readiness" "mock M365" "/start/"; do
  if ! grep -qiF "$phrase" <<< "$trial"; then
    echo "FAIL copilot/trial missing: $phrase" >&2
    fail=1
  fi
done
echo "OK   copilot/trial has commercial sandbox copy"

if grep -qiF "QuickScan" <<< "$trial"; then
  echo "FAIL copilot/trial must not list QuickScan as ladder step" >&2
  fail=1
else
  echo "OK   trial ladder free of QuickScan retail step"
fi

for bad in "payment rails" "Start sending payments" "Treasury" "corridor"; do
  if grep -qiF "$bad" <<< "$trial" || grep -qiF "$bad" <<< "$demo"; then
    echo "FAIL demo/trial must not mention fintech bleed: $bad" >&2
    fail=1
  fi
done
echo "OK   demo/trial free of fintech sandbox bleed"

for link in "/copilot/demo/" "/copilot/trial/"; do
  if ! grep -qF "$link" <<< "$header"; then
    echo "FAIL header missing $link" >&2
    fail=1
  fi
done
echo "OK   header links demo + trial"

index="$(cat index.html)"
if ! grep -qF '/copilot/demo/' <<< "$index" || ! grep -qF '/copilot/trial/' <<< "$index"; then
  echo "FAIL homepage must link demo and trial" >&2
  fail=1
else
  echo "OK   homepage links demo + trial"
fi

if grep -qiF "fourth SKU" <<< "$trial" || grep -qiF "fourth product" <<< "$demo"; then
  echo "FAIL must not introduce fourth SKU language" >&2
  fail=1
else
  echo "OK   three-SKU boundary preserved"
fi

footer="$(cat assets/partials/footer.html)"
if ! grep -qF '/copilot/demo/' <<< "$footer" || ! grep -qF '/copilot/trial/' <<< "$footer"; then
  echo "FAIL footer must link demo and trial" >&2
  fail=1
else
  echo "OK   footer links demo + trial"
fi

if [[ "$fail" -eq 0 ]]; then
  if [[ -x ./scripts/verify-www-buyer-audience.sh ]]; then
    echo ""
    echo "Running buyer-audience gate (extended pages)..."
    PAGES_EXTRA=(copilot/demo/index.html copilot/trial/index.html)
    for rel in "${PAGES_EXTRA[@]}"; do
      text="$(cat "$rel")"
      for phrase in GCIP "internal tracking" "founder sign-off" "this repo"; do
        if grep -qF "$phrase" <<< "$text"; then
          echo "FAIL $rel — $phrase" >&2
          fail=1
        fi
      done
      if [[ "$fail" -eq 0 ]]; then
        echo "OK   $rel buyer-audience clean"
      fi
    done
  fi
  echo ""
  echo "verify-commercial-agentic passed."
  exit 0
fi
echo ""
echo "Commercial agentic verification failed." >&2
exit 1
