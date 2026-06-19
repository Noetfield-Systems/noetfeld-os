#!/usr/bin/env bash
# verify-freemium-policy.sh — Sandbox v2 observe/enforce + commercial ladder gate
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

fail=0
echo "=== verify-freemium-policy ==="

require_file() {
  local rel="$1"
  if [[ ! -f "$rel" ]]; then
    echo "FAIL missing: $rel" >&2
    fail=1
    return
  fi
  echo "OK   $rel"
}

require_file governance/FREEMIUM_POLICY_LOCKED_v1.md
require_file assets/noetfield-sandbox.js
require_file services/governance/noetfield_governance/sandbox_service.py

require_file docs/ops/UI_BUILD_CHECKLIST_LOCKED_v1.md
require_file .cursor/skills/SKILL-009-ui-build-checklist-mandatory.md

api="$(cat services/governance/noetfield_governance/api.py)"
for route in \
  "/api/sandbox/provision" \
  "/api/sandbox/session" \
  "/api/sandbox/evaluate" \
  "/api/sandbox/export/board.pdf" \
  "/api/sandbox/health"; do
  if ! grep -qF "$route" <<< "$api"; then
    echo "FAIL api.py missing route: $route" >&2
    fail=1
  else
    echo "OK   api route $route"
  fi
done

sandbox_js="$(cat assets/noetfield-sandbox.js)"
for phrase in "/api/sandbox/provision" "/api/sandbox/evaluate" "observe" "nf_sandbox_v2"; do
  if ! grep -qF "$phrase" <<< "$sandbox_js"; then
    echo "FAIL noetfield-sandbox.js missing: $phrase" >&2
    fail=1
  fi
done
echo "OK   noetfield-sandbox.js v2 API wired"

start="$(cat start/index.html)"
for phrase in "watermarked board PDF" "data-sandbox-upgrade" "data-factory-demo" "observe"; do
  if ! grep -qF "$phrase" <<< "$start"; then
    echo "FAIL start/index.html missing: $phrase" >&2
    fail=1
  fi
done
echo "OK   start export moment present"

trial="$(cat copilot/trial/index.html)"
if grep -qiF "QuickScan" <<< "$trial"; then
  echo "FAIL copilot/trial must not list QuickScan as ladder step" >&2
  fail=1
else
  echo "OK   trial ladder free of QuickScan retail step"
fi

for phrase in "/start/" "Copilot Readiness" "Trust Brief" "Bank Pilot"; do
  if ! grep -qiF "$phrase" <<< "$trial"; then
    echo "FAIL copilot/trial missing: $phrase" >&2
    fail=1
  fi
done
echo "OK   trial commercial ladder aligned"

policy="$(cat governance/FREEMIUM_POLICY_LOCKED_v1.md)"
for phrase in "observe" "enforce" "50" "14 days" "watermarked"; do
  if ! grep -qiF "$phrase" <<< "$policy"; then
    echo "FAIL FREEMIUM_POLICY missing: $phrase" >&2
    fail=1
  fi
done
echo "OK   freemium policy doc complete"

if [[ -x scripts/verify-ui-build-checklist.sh ]]; then
  echo ""
  echo "Running UI build checklist (subset)..."
  ./scripts/verify-ui-build-checklist.sh || fail=1
fi

if [[ "$fail" -eq 0 ]]; then
  echo ""
  echo "verify-freemium-policy passed."
  exit 0
fi
echo ""
echo "Freemium policy verification failed." >&2
exit 1
