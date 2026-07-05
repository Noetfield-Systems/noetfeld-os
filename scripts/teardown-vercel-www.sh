#!/usr/bin/env bash
# Remove Vercel www project after Cloudflare Pages is live on canonical domain.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=scripts/www-vercel-canonical.sh
source "$ROOT/scripts/www-vercel-canonical.sh"

log() { printf '[teardown-vercel-www] %s\n' "$*"; }

CANONICAL="${NF_WWW_CANONICAL_URL:-https://www.noetfield.com}"

log "confirm canonical is Cloudflare Pages before teardown…"
if ! curl -sSI "$CANONICAL/health" | grep -qi 'server: cloudflare'; then
  log "FAIL: ${CANONICAL} does not look like Cloudflare yet — aborting"
  exit 2
fi

python3 "$ROOT/scripts/nf_post_deploy_verify.py" --surface www --www-base "$CANONICAL" || {
  log "FAIL: post-deploy verify failed — aborting Vercel teardown"
  exit 3
}

log "removing Vercel project ${NF_VERCEL_PROJECT} (scope ${NF_VERCEL_SCOPE})"
npx vercel project rm "$NF_VERCEL_PROJECT" --scope "$NF_VERCEL_SCOPE" --yes

log "disconnect GitHub integration (manual if CLI cannot):"
log "  https://vercel.com/${NF_VERCEL_SCOPE}/${NF_VERCEL_PROJECT}/settings/git"

rm -rf "$ROOT/.vercel"
log "removed local .vercel link"
log "PASS — Vercel www disconnected; canonical ${CANONICAL}"
