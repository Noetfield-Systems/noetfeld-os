#!/usr/bin/env bash
# One-way copy: Desktop SourceA → gitignored ops/private/sourceA/ (founder Mac only).
# Agents have READ ONLY on Desktop SSOT files — do not run this to "update" Desktop from repo.
set -euo pipefail
SRC="${1:-/Users/sinakazemnezhad/Desktop/SourceA}"
DEST="$(cd "$(dirname "$0")/.." && pwd)/ops/private/sourceA"
if [[ ! -d "$SRC" ]]; then
  echo "SourceA not found: $SRC" >&2
  exit 1
fi
mkdir -p "$DEST"
cp -f "$SRC/SINA_OS_SSOT_LOCKED.md" "$SRC/PHASE1_UNIFIED_BLUEPRINT_v2_3.md" "$DEST/" 2>/dev/null || {
  echo "Copy failed — check filenames on Desktop" >&2
  exit 1
}
for f in \
  AUTO_CONFLICT_ENGINE_V3_LOCKED.md \
  SINAAI_FAST_TRACK_FORCE_MAJEURE_LOCKED_v1.md \
  SINAAI_AGENT_YAML_INGEST_LOCKED_v1.md \
  AGENT_OUTPUT_CONTRACT_v1.yaml \
  ECOSYSTEM_STATUS.md \
  EXECUTION_TRUTH.json \
  GLOBAL_PRIORITY.json \
  AGENT_GOVERNANCE_INDEX_LOCKED_v1.md \
  FEEDBACK_AGGREGATE.json; do
  if [[ -f "$SRC/$f" ]]; then
    cp -f "$SRC/$f" "$DEST/"
  fi
done
echo "Synced to $DEST (gitignored)."
NOTICE_DEST="${DEST}/founder/repo-agent-notices"
mkdir -p "$NOTICE_DEST"
if [[ -d "$SRC/founder/repo-agent-notices" ]]; then
  cp -f "$SRC/founder/repo-agent-notices/"*.md "$NOTICE_DEST/" 2>/dev/null || true
  cp -f "$SRC/founder/repo-agent-notices/"*.json "$NOTICE_DEST/" 2>/dev/null || true
fi
for f in \
  SINA_COMMAND_SYSTEM_UPDATE_NOTICE_LOCKED_v1.md \
  SINA_SEMI_SEPARATE_AGENT_NOTICE_LOCKED_v1.md \
  SINA_HUB_ESSENTIALS_LOCKED_v1.md \
  SINA_PERSONAL_DATABASE_LAYER_A_LOCKED_v1.md \
  SINA_MAC_HEALTH_GUARD_LOCKED_v1.md \
  ASF_PROGRAM_THREADS_REGISTRY_LOCKED_v1.md \
  ECOSYSTEM_INCIDENTS_INDEX_LOCKED_v1.md \
  AGENT_DESK_START_HERE.md \
  README_SOURCE_A.md \
  GLOBAL_BLOCKERS.json; do
  if [[ -f "$SRC/$f" ]]; then
    cp -f "$SRC/$f" "$DEST/"
  fi
done
echo "Synced to $DEST (gitignored)."
ls -la "$DEST"
ls -la "$NOTICE_DEST" 2>/dev/null | head -20
