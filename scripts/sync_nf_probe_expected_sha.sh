#!/usr/bin/env bash
# Sync nf-probe-cron EXPECTED_GIT_SHA to live platform.noetfield.com git_sha.
# Prevents drift false-alarms when www/main advances without a platform Railway deploy.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORKER_DIR="$ROOT/infra/nf-probe-cron"
PIN_FILE="$ROOT/data/nf-platform-deploy-pin-v1.json"
PLATFORM_BASE="${PLATFORM_BASE:-https://platform.noetfield.com}"
WRANGLER_TOML="$WORKER_DIR/wrangler.toml"

log() { printf '[sync-nf-probe-expected-sha] %s\n' "$*"; }

fetch_live_platform_sha() {
  curl -sS "${PLATFORM_BASE%/}/api/public/chat/health" \
    | python3 -c "import json,sys; print(json.load(sys.stdin).get('git_sha','').strip())"
}

write_pin_file() {
  local sha="$1"
  local now
  now="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  python3 - "$PIN_FILE" "$sha" "$now" "$PLATFORM_BASE" <<'PY'
import json, sys
from pathlib import Path

path, sha, pinned_at, platform_base = sys.argv[1:5]
doc = {
    "schema": "nf-platform-deploy-pin-v1",
    "git_sha": sha,
    "pinned_at": pinned_at,
    "source": "live_platform_health",
    "platform_base": platform_base,
    "note": "Updated when platform Railway deploy succeeds or sync_nf_probe_expected_sha.sh runs. Drift probe compares live /api/public/chat/health git_sha to this pin — not repo main HEAD.",
}
Path(path).write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
PY
}

update_wrangler_var() {
  local sha="$1"
  python3 - "$WRANGLER_TOML" "$sha" <<'PY'
import re, sys
from pathlib import Path

path, sha = sys.argv[1], sys.argv[2]
text = Path(path).read_text(encoding="utf-8")
line = f'EXPECTED_GIT_SHA = "{sha}"'
if "EXPECTED_GIT_SHA" in text:
    text = re.sub(r'^EXPECTED_GIT_SHA\s*=.*$', line, text, count=1, flags=re.M)
else:
    text = text.replace("[vars]\n", f"[vars]\n{line}\n", 1)
Path(path).write_text(text, encoding="utf-8")
PY
}

sync_wrangler_secret() {
  local sha="$1"
  if [[ -z "${CLOUDFLARE_API_TOKEN:-}${CF_API_TOKEN:-}" ]]; then
    log "WARN: no Cloudflare token — skip wrangler secret put (run from Mac vault or GHA with CLOUDFLARE_API_TOKEN)"
    return 0
  fi
  log "wrangler secret put EXPECTED_GIT_SHA"
  cd "$WORKER_DIR"
  printf '%s' "$sha" | wrangler secret put EXPECTED_GIT_SHA >/dev/null
}

main() {
  local live_sha
  live_sha="$(fetch_live_platform_sha)"
  if [[ -z "$live_sha" ]]; then
    log "FAIL: could not read git_sha from ${PLATFORM_BASE}/api/public/chat/health"
    exit 1
  fi

  log "live platform git_sha=${live_sha:0:12}"
  write_pin_file "$live_sha"
  update_wrangler_var "$live_sha"
  sync_wrangler_secret "$live_sha"

  if [[ "${NF_PROBE_CRON_DEPLOY:-0}" == "1" ]]; then
    log "NF_PROBE_CRON_DEPLOY=1 — wrangler deploy"
    cd "$WORKER_DIR"
    wrangler deploy
  fi

  log "PASS — EXPECTED_GIT_SHA synced to ${live_sha:0:12}"
}

main "$@"
