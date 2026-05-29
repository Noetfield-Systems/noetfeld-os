#!/usr/bin/env bash
# Restore ops/private trackers from a prior git commit (one-time), or init empty folder.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PRIVATE="${ROOT}/ops/private"
mkdir -p "${PRIVATE}"

if [[ -f "${PRIVATE}/todolist/NEXT_MOVES.md" ]]; then
  echo "ops/private/todolist already exists — nothing to do."
  exit 0
fi

for rev in HEAD~1 HEAD~3 HEAD~8 HEAD~15 HEAD~30 HEAD~50; do
  if git -C "${ROOT}" cat-file -e "${rev}:todolist/NEXT_MOVES.md" 2>/dev/null; then
    echo "Restoring todolist/ from ${rev} into ops/private/"
    git -C "${ROOT}" archive "${rev}" todolist | tar -x -C "${PRIVATE}"
    if git -C "${ROOT}" cat-file -e "${rev}:docs/GO_LIVE_CHECKLIST.md" 2>/dev/null; then
      mkdir -p "${PRIVATE}/docs"
      git -C "${ROOT}" show "${rev}:docs/GO_LIVE_CHECKLIST.md" > "${PRIVATE}/docs/GO_LIVE_CHECKLIST.md"
    fi
    echo "Done. ops/private/ is gitignored — stays on your machine only."
    exit 0
  fi
done

echo "No prior todolist/ found in recent history."
echo "Use GitHub Issues (.github/ISSUE_TEMPLATE/) or create ops/private/todolist manually."
exit 0
