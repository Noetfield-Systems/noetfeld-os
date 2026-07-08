#!/usr/bin/env bash
# Claim a T2 local lane before editing (L-P5).
# Usage: bash scripts/noos_local_claim_lane_v1.sh NOOS-LANE-001 path1 path2 ...
set -euo pipefail

if [ "$#" -lt 2 ]; then
  echo "Usage: bash scripts/noos_local_claim_lane_v1.sh <task-id> <scope-file> [scope-file ...]" >&2
  exit 1
fi

TASK_ID="$1"
shift
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

SCOPE_ARGS=()
for path in "$@"; do
  SCOPE_ARGS+=(--scope-file "$path")
done

AGENT_ID="${AGENT_ID:-cursor-local-mac}"
IDE="${IDE:-cursor}"

exec python3 scripts/noos_integrator_sync_v1.py claim \
  --agent-id "$AGENT_ID" \
  --ide "$IDE" \
  --task-id "$TASK_ID" \
  --title "$TASK_ID" \
  "${SCOPE_ARGS[@]}"
