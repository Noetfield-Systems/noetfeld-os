#!/usr/bin/env bash
# Noetfield — post-verify closeout: validate YAML, ingest, sync SourceA mirror.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
"${ROOT}/scripts/ingest-cursor-reply.sh"
"${ROOT}/scripts/sync-sourceA-desktop.sh"
