#!/usr/bin/env bash
# One-way copy: Desktop SourceA → gitignored ops/private/sourceA/ (founder Mac only).
# Direction: SourceA → mirror ONLY. Never copy repo docs back to Desktop.
set -euo pipefail
SRC="${1:-/Users/sinakazemnezhad/Desktop/SourceA}"
DEST="$(cd "$(dirname "$0")/.." && pwd)/ops/private/sourceA"
if [[ ! -d "$SRC" ]]; then
  echo "SourceA not found: $SRC" >&2
  exit 1
fi
mkdir -p "$DEST" "$DEST/founder/repo-agent-notices"
cp -f "$SRC/SINA_OS_SSOT_LOCKED.md" "$SRC/PHASE1_UNIFIED_BLUEPRINT_v2_3.md" "$DEST/" 2>/dev/null || {
  echo "Copy failed — check filenames on Desktop" >&2
  exit 1
}
for f in AUTO_CONFLICT_ENGINE_V3_LOCKED.md NOETFIELD_REPO_ALIGNMENT.md; do
  [[ -f "$SRC/$f" ]] && cp -f "$SRC/$f" "$DEST/"
done
# Repo-agent notices (semi lane, link index canonical on Mac)
if [[ -d "$SRC/founder/repo-agent-notices" ]]; then
  cp -f "$SRC/founder/repo-agent-notices/"* "$DEST/founder/repo-agent-notices/" 2>/dev/null || true
fi
# Legacy flat paths on Desktop (optional)
for f in \
  SINAAI_AGENT_YAML_INGEST_LOCKED_v1.md \
  SINAAI_EXECUTION_TRUTH_LAYER_LOCKED_v1.md \
  SINA_SEMI_SEPARATE_AGENT_NOTICE_LOCKED_v1.md \
  SEMI_NOTICE_noetfield_cloud_v1.md; do
  if [[ -f "$SRC/$f" ]]; then
    cp -f "$SRC/$f" "$DEST/"
  fi
  if [[ -f "$SRC/founder/repo-agent-notices/$f" ]]; then
    cp -f "$SRC/founder/repo-agent-notices/$f" "$DEST/founder/repo-agent-notices/"
  fi
done
echo "Synced to $DEST (gitignored). SourceA → mirror only."
ls -la "$DEST" "$DEST/founder/repo-agent-notices" 2>/dev/null || ls -la "$DEST"
