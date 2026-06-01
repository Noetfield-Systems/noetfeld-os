#!/usr/bin/env bash
# Copy Desktop SourceA into gitignored ops/private/sourceA/ (founder Mac only).
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
echo "Synced to $DEST (gitignored)."
ls -la "$DEST"
