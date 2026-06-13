#!/usr/bin/env bash
# Noetfield cloud agent — session-close self-audit (disk closeout beats chat).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
AUDIT="${HOME}/Desktop/SourceA/scripts/cursor_agent_self_audit.py"
AGENT="${NOETFIELD_AGENT_ID:-noetfield_cloud}"

if [[ ! -f "$AUDIT" ]]; then
  echo "WARN: cursor_agent_self_audit.py not found at $AUDIT" >&2
  exit 1
fi

cd "$ROOT"
python3 "$AUDIT" session-close --agent "$AGENT"
