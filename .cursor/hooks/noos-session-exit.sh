#!/usr/bin/env bash
# LOCAL SESSION EXIT RULE: refresh integrator mirrors before session stop (fail-open).
set -uo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

AGENT_ID="${NOOS_INTEGRATOR_AGENT_ID:-cursor-local-mac}"

if python3 scripts/noos_integrator_sync_v1.py session-exit --agent-id "$AGENT_ID" >/dev/null 2>&1; then
  echo "[noos-session-exit] OK: integrator mirrors refreshed"
else
  echo "[noos-session-exit] WARN: session-exit sync failed (session continues)" >&2
fi

exit 0
