#!/usr/bin/env bash
# Read-only T2 session boot — conflict + governance + integrator summary (no writes).
set -uo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

failures=0

run_check() {
  local label="$1"
  shift
  if "$@" >/dev/null 2>&1; then
    echo "[noos-local-boot] OK: ${label}"
  else
    echo "[noos-local-boot] WARN: ${label} failed (session continues)" >&2
    failures=$((failures + 1))
  fi
}

run_check "parallel_conflict" python3 scripts/noos_agent_conflict_check_v1.py --json
run_check "governance_verify" python3 scripts/verify_living_system_governance_v1.py --json
run_check "integrator_summary" python3 scripts/noos_integrator_sync_v1.py summary --json

# Fail open: never block session start (plan constraint).
exit 0
