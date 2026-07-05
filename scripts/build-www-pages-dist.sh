#!/usr/bin/env bash
# Build static output directory for Cloudflare Pages (mirrors .vercelignore exclusions).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
DIST="${ROOT}/www-pages-dist"

log() { printf '[build-www-pages-dist] %s\n' "$*"; }

log "sync greeting SSOT…"
python3 scripts/sync_chat_greeting_asset.py
python3 scripts/generate-cf-redirects.py

log "clean ${DIST}"
rm -rf "$DIST"
mkdir -p "$DIST"

log "copy static files (respecting .vercelignore)…"
if command -v rsync >/dev/null 2>&1; then
  rsync -a \
    --exclude-from="${ROOT}/.vercelignore" \
    --exclude 'www-pages-dist/' \
    --exclude 'vercel.json' \
    --exclude '.vercel/' \
    --exclude '.vscode/' \
    --exclude '.git/' \
    --exclude '.venv/' \
    --exclude 'venv/' \
    --exclude 'node_modules/' \
    --exclude 'package-lock.json' \
    --exclude 'package.json' \
    --exclude '__pycache__/' \
    --exclude 'api/' \
    --exclude 'functions/' \
    --exclude 'wrangler.toml' \
    "${ROOT}/" "${DIST}/"
else
  log "FAIL: rsync required"
  exit 1
fi

cp "${ROOT}/_redirects" "${DIST}/_redirects"
node scripts/bundle-pages-functions.mjs
log "done — ${DIST} ($(find "$DIST" -type f | wc -l | tr -d ' ') files) + functions/"
