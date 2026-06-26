#!/usr/bin/env bash
# Noetfield — post-verify closeout: surfaces, language gate, ingest, SourceA mirror.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
REPLY="${ROOT}/reports/cursor-reply-latest.txt"

python3 scripts/nf_live_surfaces_v1.py --json >/dev/null
chmod +x scripts/verify-nf-agent-report-language.sh
./scripts/verify-nf-agent-report-language.sh

if [[ -f "$REPLY" ]]; then
  python3 scripts/nf_founder_reply_loop_v1.py --file "$REPLY" --write-receipt --json >/dev/null || {
    echo "FAIL closeout: cursor-reply blocked by founder reply loop — rewrite plain English" >&2
    exit 1
  }
fi

"${ROOT}/scripts/ingest-cursor-reply.sh"
"${ROOT}/scripts/sync-sourceA-desktop.sh"
