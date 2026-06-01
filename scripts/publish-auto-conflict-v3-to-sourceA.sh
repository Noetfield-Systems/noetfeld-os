#!/usr/bin/env bash
# INTERNAL — Founder Mac only. Copies gitignored doctrine → Desktop SourceA.
# Not public; do not commit ops/private/sourceA/*.md to GitHub.
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC="$REPO_ROOT/ops/private/sourceA/AUTO_CONFLICT_ENGINE_V3_LOCKED.md"
DEST="${1:-/Users/sinakazemnezhad/Desktop/SourceA}"
if [[ ! -f "$SRC" ]]; then
  echo "Missing: $SRC" >&2
  echo "Ensure ops/private/sourceA/ exists (bootstrap or agent draft)." >&2
  exit 1
fi
if [[ ! -d "$DEST" ]]; then
  echo "SourceA folder not found: $DEST" >&2
  exit 1
fi
cp -f "$SRC" "$DEST/AUTO_CONFLICT_ENGINE_V3_LOCKED.md"
echo "Published locked doctrine to: $DEST/AUTO_CONFLICT_ENGINE_V3_LOCKED.md"
ls -la "$DEST/AUTO_CONFLICT_ENGINE_V3_LOCKED.md"
