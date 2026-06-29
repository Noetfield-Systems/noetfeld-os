#!/usr/bin/env bash
# Verify and write the Noetfield OS live sync receipt.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

SCOPE="${NOOS_LIVE_SYNC_SCOPE:-ecosystem}"
ARGS=(--write --refresh-website-nerve --scope "$SCOPE")

if [[ "${NOOS_LIVE_SYNC_FULL:-0}" == "1" ]]; then
  ARGS+=(--full)
fi

if [[ "${NOOS_LIVE_SYNC_STRICT:-0}" == "1" ]]; then
  ARGS+=(--strict)
fi

python3 scripts/noos_live_sync_gate.py "${ARGS[@]}"
python3 -m json.tool docs/_NOOS_AGENT/live_sync/NOOS_LIVE_SYNC_RECEIPT.json >/dev/null

echo "check_noos_live_sync_gate: PASS"
