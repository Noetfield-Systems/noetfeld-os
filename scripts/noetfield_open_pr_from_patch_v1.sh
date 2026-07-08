#!/usr/bin/env bash
# Apply Noetfield patch bundle and open PR (requires token with push to Noetfield-Systems/Noetfield).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PATCH_DIR="${PATCH_DIR:-$ROOT/receipts/proof/noetfield-semantic-drift-closeout}"
TARGET_REPO="${TARGET_REPO:-Noetfield-Systems/Noetfield}"
BRANCH="${BRANCH:-cursor/nf-semantic-drift-closeout-72f6}"
BASE="${BASE:-main}"
WORKDIR="${WORKDIR:-/tmp/noetfield-pr-push}"

TOKEN="${NOETFIELD_GITHUB_TOKEN:-${GH_TOKEN:-${GITHUB_TOKEN:-}}}"

log() { printf '[noetfield-open-pr] %s\n' "$*"; }
die() { log "FAIL: $*"; exit 1; }

[[ -n "$TOKEN" ]] || die "NOETFIELD_GITHUB_TOKEN/GH_TOKEN/GITHUB_TOKEN required"
[[ -d "$PATCH_DIR" ]] || die "patch dir missing: $PATCH_DIR"

rm -rf "$WORKDIR"
git clone "https://x-access-token:${TOKEN}@github.com/${TARGET_REPO}.git" "$WORKDIR"
cd "$WORKDIR"
git config user.email "noos-handoff-bot@noetfield.com"
git config user.name "NOOS Noetfield Handoff"
git fetch origin "$BASE"
git checkout -B "$BRANCH" "origin/$BASE"

shopt -s nullglob
patches=("$PATCH_DIR"/*.patch)
[[ ${#patches[@]} -gt 0 ]] || die "no patches in $PATCH_DIR"
log "applying ${#patches[@]} patch(es) from $PATCH_DIR"
git am "${patches[@]}"

if ! git push -u origin "$BRANCH" --force-with-lease 2>&1; then
  log "WARN: direct push denied — publishing mirror branch on noetfeld-os"
  MIRROR_BRANCH="noetfield-mirror/${BRANCH}"
  NOOS_REMOTE="https://x-access-token:${TOKEN}@github.com/Noetfield-Systems/noetfeld-os.git"
  if git push "$NOOS_REMOTE" "HEAD:refs/heads/${MIRROR_BRANCH}" 2>&1; then
    log "mirror pushed: noetfeld-os@${MIRROR_BRANCH}"
    log "FAIL: set NOETFIELD_GITHUB_TOKEN org PAT with push to ${TARGET_REPO} — see Noetfield issue #98"
  else
    die "push denied — set NOETFIELD_GITHUB_TOKEN org secret with push to Noetfield-Systems/Noetfield"
  fi
  exit 1
fi

PR_URL="$(gh pr create \
  --repo "$TARGET_REPO" \
  --base "$BASE" \
  --head "$BRANCH" \
  --title "feat(L8): semantic drift anchors + hybrid chatbot retrieval" \
  --body "## Summary

Applies cloud-agent patch bundle for SourceA Voyage anti-drift in Noetfield:

- \`nf_semantic_drift_v1.py\` — PRODUCT_TRUTH anchor alignment via Voyage embeddings
- \`semantic_anchors_v1.json\` — SSOT ↔ chatbot knowledge pairs
- Hybrid scoring in chatbot retrieval when Voyage active
- L8 + semantic_drift gates in \`nf_voyage_integrity_v1.py\`
- BAVT + \`make nf-semantic-drift\` targets

Built on main (\`nf_embedding_provider_v1\` + voyage live wire already merged).

## Verify

\`\`\`bash
make nf-voyage-ai-wire
make nf-semantic-drift
make nf-voyage-integrity
\`\`\`
" 2>&1)" || true

log "branch pushed: $BRANCH"
log "pr: ${PR_URL:-see https://github.com/${TARGET_REPO}/compare/${BASE}...${BRANCH}}"
