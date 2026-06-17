#!/usr/bin/env bash
# Noetfield cloud agent — session-start (NF-GAOS gate first; SourceA audit optional).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
AGENT="${NOETFIELD_AGENT_ID:-noetfield_cloud}"
AUDIT="${HOME}/Desktop/SourceA/scripts/cursor_agent_self_audit.py"

cd "$ROOT"
chmod +x scripts/nf-onboard.sh scripts/nf-live-orient-v1.sh 2>/dev/null || true

echo "=== agent-session-start (NF-GAOS) ==="
if ! ./scripts/nf-onboard.sh cloud; then
  echo "WARN: nf-onboard reported gate issues — read reports/agent-auto/LIVE-STATUS.md" >&2
fi

if [[ -f "$AUDIT" ]]; then
  python3 "$AUDIT" session-start --agent "$AGENT" || true
else
  echo "SKIP SourceA cursor_agent_self_audit (not on founder Mac)"
fi
