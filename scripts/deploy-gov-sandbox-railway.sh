#!/usr/bin/env bash
# Deploy governance-console API + Next workspace to Railway; wire www proxy config.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

PROJECT_ID="${NF_RAILWAY_PROJECT_ID:-94ade24c-9b24-4d8d-a443-9ddc5bf6ef54}"
ENV_NAME="${NF_RAILWAY_ENV:-production}"
API_SERVICE="${NF_GOV_API_SERVICE:-gov-sandbox-api}"
WEB_SERVICE="${NF_GOV_WEB_SERVICE:-gov-sandbox-web}"
PROXY_CFG="${ROOT}/data/nf-www-gov-proxy-v1.json"
RAILWAY_CALLER="${RAILWAY_CALLER:-scripts/deploy-gov-sandbox-railway}"
SESSION="${RAILWAY_AGENT_SESSION:-gov-sandbox-$(date +%s)}"

log() { printf '[deploy-gov-sandbox-railway] %s\n' "$*"; }

railway_cmd() {
  env RAILWAY_CALLER="$RAILWAY_CALLER" RAILWAY_AGENT_SESSION="$SESSION" railway "$@"
}

link_service() {
  local name="$1"
  railway_cmd link -p "$PROJECT_ID" -e "$ENV_NAME" -s "$name" >/dev/null 2>&1 || true
}

# Railway service status JSON has no public URL — use domain list (same as deploy-platform-railway.sh).
railway_service_url() {
  local name="$1"
  link_service "$name"
  railway_cmd domain list --service "$name" --json 2>/dev/null | python3 -c "
import json, sys
try:
    d = json.load(sys.stdin)
    items = d if isinstance(d, list) else d.get('domains', d.get('result', []))
    for x in items or []:
        dom = x.get('domain') if isinstance(x, dict) else x
        if dom and 'railway.app' in str(dom):
            print('https://' + str(dom).replace('https://', '').rstrip('/'))
            break
except Exception:
    pass
" 2>/dev/null
}

wait_for_railway_url() {
  local name="$1"
  local url=""
  local attempt
  for attempt in $(seq 1 18); do
    url="$(railway_service_url "$name" || true)"
    if [[ -n "$url" ]]; then
      echo "$url"
      return 0
    fi
    log "waiting for ${name} domain (${attempt}/18)…"
    sleep 10
  done
  return 1
}

proxy_cfg_origin() {
  local key="$1"
  python3 -c "
import json, sys
from pathlib import Path
p = Path('${PROXY_CFG}')
if not p.is_file():
    sys.exit(0)
d = json.loads(p.read_text(encoding='utf-8'))
print((d.get('${key}') or '').rstrip('/'))
" 2>/dev/null || true
}

log "project=${PROJECT_ID} env=${ENV_NAME}"

link_service "$API_SERVICE"

log "pin Railway build config (gov-console images, not platform-api)…"
railway_cmd environment edit -e "$ENV_NAME" \
  --service-config "$API_SERVICE" build.builder DOCKERFILE \
  --service-config "$API_SERVICE" build.dockerfilePath "governance-console/backend/Dockerfile" \
  --service-config "$WEB_SERVICE" build.builder DOCKERFILE \
  --service-config "$WEB_SERVICE" build.dockerfilePath "governance-console/Dockerfile.www" \
  -m "gov-sandbox: governance-console dockerfiles" \
  >/dev/null 2>&1 || log "WARN: could not patch Railway build config"

log "set API CORS + SQLite sandbox DB…"
railway_cmd variable set \
  -s "$API_SERVICE" \
  --set "CORS_ORIGINS=https://www.noetfield.com,https://noetfield.com,http://localhost:13080" \
  --set "DATABASE_URL=sqlite:///./gov_sandbox.db" \
  --skip-deploys \
  >/dev/null 2>&1 || log "WARN: could not set API variables"

log "deploy API (${API_SERVICE})…"
link_service "$API_SERVICE"
(
  cd "${ROOT}"
  railway_cmd up "./governance-console/backend" --path-as-root -s "$API_SERVICE" -d -m "gov-sandbox-api: governance-console backend"
)

log "deploy Web (${WEB_SERVICE})…"
link_service "$WEB_SERVICE"
(
  cd "${ROOT}"
  if [[ -f railway.toml ]]; then
    cp railway.toml "${ROOT}/.railway.toml.platform.bak"
  fi
  cp governance-console/railway.web.toml railway.toml
  railway_cmd up -s "$WEB_SERVICE" -d -m "gov-sandbox-web: Next workspace /workspace"
  if [[ -f "${ROOT}/.railway.toml.platform.bak" ]]; then
    mv "${ROOT}/.railway.toml.platform.bak" railway.toml
  else
    rm -f railway.toml
  fi
)

log "resolve Railway service URLs (domain list + retry)…"
API_URL="$(wait_for_railway_url "$API_SERVICE" || true)"
WEB_URL="$(wait_for_railway_url "$WEB_SERVICE" || true)"

if [[ -z "$API_URL" ]]; then
  API_URL="$(proxy_cfg_origin gov_api_origin)"
  [[ -n "$API_URL" ]] && log "WARN: using cached gov_api_origin from ${PROXY_CFG}"
fi
if [[ -z "$WEB_URL" ]]; then
  WEB_URL="$(proxy_cfg_origin gov_web_origin)"
  [[ -n "$WEB_URL" ]] && log "WARN: using cached gov_web_origin from ${PROXY_CFG}"
fi

if [[ -z "$API_URL" || -z "$WEB_URL" ]]; then
  log "FAIL: could not resolve Railway service URLs"
  log "Check: railway domain list --service ${API_SERVICE} --json"
  exit 2
fi

log "API URL: ${API_URL}"
log "WEB URL: ${WEB_URL}"

python3 - <<PY
import json
from pathlib import Path
cfg = {
    "schema": "nf-www-gov-proxy-v1",
    "enabled": True,
    "gov_web_origin": "${WEB_URL}".rstrip("/"),
    "gov_api_origin": "${API_URL}".rstrip("/"),
}
path = Path("${PROXY_CFG}")
path.write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")
print(f"wrote {path}")
PY

python3 scripts/generate-cf-redirects.py
python3 scripts/generate-www-deny-middleware.py

log "smoke API…"
curl -sf "${API_URL}/health" | head -c 200
echo
log "smoke WEB workspace…"
curl -sf "${WEB_URL}/workspace" | grep -qE '_next|Trust Ledger Workspace' && log "OK workspace shell" || log "WARN: workspace shell missing on Railway URL"

log "done — run: bash scripts/deploy-www-cloudflare.sh to promote www proxy"
