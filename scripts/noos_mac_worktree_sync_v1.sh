#!/usr/bin/env bash
# Sync with origin/main when main is checked out in another worktree.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "[noos-mac-worktree-sync] fetching origin/main"
git fetch origin main

LOCAL="$(git rev-parse HEAD)"
REMOTE="$(git rev-parse origin/main)"

if [ "$LOCAL" = "$REMOTE" ]; then
  echo "[noos-mac-worktree-sync] already at origin/main"
elif git merge-base --is-ancestor "$LOCAL" "$REMOTE" 2>/dev/null; then
  echo "[noos-mac-worktree-sync] fast-forward merge"
  git merge --ff-only origin/main
else
  echo "[noos-mac-worktree-sync] merge origin/main into current branch"
  git merge origin/main
fi

git log -1 --oneline origin/main
make local-boot
