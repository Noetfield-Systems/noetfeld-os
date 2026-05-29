#!/usr/bin/env bash
# Seed gitignored ops/private for founders and local agents (never committed).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PRIVATE="${ROOT}/ops/private"
mkdir -p "${PRIVATE}/todolist" "${PRIVATE}/docs"

write_readme() {
  cat > "${PRIVATE}/README.md" << 'EOF'
# ops/private (local only — gitignored)

Founder and **local agent** detailed tracking. Cloud agents use GitHub Issues instead.

- `todolist/NEXT_MOVES.md` — P0/P1/P2
- `todolist/noetfield-platform.md` — platform
- `todolist/noetfield-public-site.md` — www
- `docs/GO_LIVE_CHECKLIST.md` — deploy
- `docs/LEGAL_REVIEW_CHECKLIST.md` — legal

Agents: [.cursor/AGENT_TRACKING.md](../.cursor/AGENT_TRACKING.md)
EOF
}

if [[ -f "${PRIVATE}/todolist/NEXT_MOVES.md" ]]; then
  write_readme
  echo "ops/private already seeded."
  exit 0
fi

for rev in HEAD HEAD~1 HEAD~5 HEAD~15 HEAD~30 HEAD~50; do
  if git -C "${ROOT}" cat-file -e "${rev}:todolist/NEXT_MOVES.md" 2>/dev/null; then
    echo "Restoring trackers from ${rev} → ops/private/"
    git -C "${ROOT}" archive "${rev}" todolist | tar -x -C "${PRIVATE}"
    if git -C "${ROOT}" cat-file -e "${rev}:docs/GO_LIVE_CHECKLIST.md" 2>/dev/null; then
      git -C "${ROOT}" show "${rev}:docs/GO_LIVE_CHECKLIST.md" > "${PRIVATE}/docs/GO_LIVE_CHECKLIST.md"
    fi
    if git -C "${ROOT}" cat-file -e "${rev}:docs/LEGAL_REVIEW_CHECKLIST.md" 2>/dev/null; then
      git -C "${ROOT}" show "${rev}:docs/LEGAL_REVIEW_CHECKLIST.md" > "${PRIVATE}/docs/LEGAL_REVIEW_CHECKLIST.md"
    elif [[ -f "${ROOT}/docs/LEGAL_REVIEW_CHECKLIST.md" ]]; then
      cp "${ROOT}/docs/LEGAL_REVIEW_CHECKLIST.md" "${PRIVATE}/docs/LEGAL_REVIEW_CHECKLIST.md"
    fi
    # Fix broken links in restored NEXT_MOVES
    if [[ -f "${PRIVATE}/todolist/NEXT_MOVES.md" ]]; then
      sed -i 's|docs/GO_LIVE_CHECKLIST.md|../docs/GO_LIVE_CHECKLIST.md|g' "${PRIVATE}/todolist/NEXT_MOVES.md" 2>/dev/null || \
        sed -i '' 's|docs/GO_LIVE_CHECKLIST.md|../docs/GO_LIVE_CHECKLIST.md|g' "${PRIVATE}/todolist/NEXT_MOVES.md" 2>/dev/null || true
      sed -i 's|../docs/strategy/|../../docs/strategy/|g' "${PRIVATE}/todolist/NEXT_MOVES.md" 2>/dev/null || \
        sed -i '' 's|../docs/strategy/|../../docs/strategy/|g' "${PRIVATE}/todolist/NEXT_MOVES.md" 2>/dev/null || true
      sed -i 's|../PROJECT_BOUNDARIES|../../PROJECT_BOUNDARIES|g' "${PRIVATE}/todolist/NEXT_MOVES.md" 2>/dev/null || \
        sed -i '' 's|../PROJECT_BOUNDARIES|../../PROJECT_BOUNDARIES|g' "${PRIVATE}/todolist/NEXT_MOVES.md" 2>/dev/null || true
    fi
    write_readme
    echo "Done. ops/private/ is gitignored."
    exit 0
  fi
done

write_readme
echo "No history to restore — created ops/private/README.md"
echo "Add Issues from .github/ISSUE_TEMPLATE/ or copy trackers manually."
