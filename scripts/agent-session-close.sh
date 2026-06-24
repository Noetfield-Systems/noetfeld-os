#!/usr/bin/env bash
# Noetfield cloud agent — session-close (BAVT fast + optional SourceA audit).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
AGENT="${NOETFIELD_AGENT_ID:-noetfield_cloud}"
AUDIT="${HOME}/Desktop/SourceA/scripts/cursor_agent_self_audit.py"

cd "$ROOT"
chmod +x scripts/nf-bavt-run.sh 2>/dev/null || true

echo "=== agent-session-close (NF-GAOS) ==="
bash scripts/nf-bavt-run.sh --fast --json || true

if [[ -f "$AUDIT" ]]; then
  python3 "$AUDIT" session-close --agent "$AGENT" || true
else
  echo "SKIP SourceA cursor_agent_self_audit close (not on founder Mac)"
fi

echo "Closeout: ingest YAML + ASK founder next move (R-008)"
