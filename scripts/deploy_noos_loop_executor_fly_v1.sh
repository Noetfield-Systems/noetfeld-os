#!/usr/bin/env bash
# deploy_noos_loop_executor_fly_v1.sh — Option B Fly HTTP loop executor
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

FLY="${FLY_BIN:-$HOME/.fly/bin/fly}"
APP="${FLY_LOOP_EXECUTOR_APP:-noos-loop-executor}"
ORG="${FLY_ORG:-personal}"
CONFIG="${ROOT}/ops/fly/noos-loop-executor/fly.toml"
DOCKERFILE="${ROOT}/ops/fly/noos-loop-executor/Dockerfile"
ENV_FILE="${NOETFIELD_ENV:-$HOME/.sourcea-secrets/noetfield.env}"

log() { printf '[deploy-fly-loop-executor] %s\n' "$*"; }

_fly_auth_ok() {
  "$FLY" auth whoami >/dev/null 2>&1
}

_ensure_fly_auth() {
  if _fly_auth_ok; then
    return 0
  fi
  if [[ -z "${FLY_ACCESS_TOKEN:-}" && -f "$HOME/.fly/config.yml" ]]; then
    FLY_ACCESS_TOKEN="$(
      python3 -c 'import pathlib; p=pathlib.Path.home()/".fly/config.yml"; t=""; 
for line in p.read_text().splitlines():
    if line.startswith("access_token:"):
        t=line.split(":",1)[1].strip(); break
print(t)' 2>/dev/null || true
    )"
    export FLY_ACCESS_TOKEN
  fi
  _fly_auth_ok
}

if ! _ensure_fly_auth; then
  log "FAIL: fly not logged in — run: fly auth login"
  exit 1
fi

if ! "$FLY" apps list --json 2>/dev/null | python3 -c "import json,sys; apps=[a.get('Name') for a in json.load(sys.stdin)]; sys.exit(0 if '${APP}' in apps else 1)" 2>/dev/null; then
  log "creating Fly app ${APP} (org=${ORG})"
  "$FLY" apps create "$APP" --org "$ORG" 2>/dev/null || "$FLY" apps create "$APP" 2>/dev/null || true
fi

if [[ -z "${NOOS_LOOP_SECRET:-}" ]]; then
  if [[ -f "$ENV_FILE" ]]; then
    NOOS_LOOP_SECRET="$(grep -E '^NOOS_LOOP_SECRET=' "$ENV_FILE" 2>/dev/null | head -1 | cut -d= -f2- || true)"
  fi
fi
if [[ -z "${NOOS_LOOP_SECRET:-}" ]]; then
  NOOS_LOOP_SECRET="$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')"
  log "generated NEW NOOS_LOOP_SECRET"
else
  log "using NOOS_LOOP_SECRET from env/file"
fi

SECRET_ARGS=("NOOS_LOOP_SECRET=$NOOS_LOOP_SECRET")
if [[ -f "$ENV_FILE" ]]; then
  set -a
  # shellcheck disable=SC1090
  . "$ENV_FILE"
  set +a
  URL="${NOETFIELD_SUPABASE_URL:-${SUPABASE_URL:-}}"
  KEY="${NOETFIELD_SUPABASE_SERVICE_ROLE_KEY:-${SUPABASE_SERVICE_ROLE_KEY:-}}"
  if [[ -n "$URL" && -n "$KEY" ]]; then
    SECRET_ARGS+=(
      "NOETFIELD_SUPABASE_URL=$URL"
      "NOETFIELD_SUPABASE_SERVICE_ROLE_KEY=$KEY"
      "SUPABASE_URL=$URL"
      "SUPABASE_SERVICE_ROLE_KEY=$KEY"
    )
    log "syncing Supabase env to Fly"
  fi
fi

log "deploy ${APP} from ${ROOT}"
(cd "$ROOT" && "$FLY" deploy "$ROOT" --config "$CONFIG" --dockerfile "$DOCKERFILE" --app "$APP" --yes)

log "set Fly secrets"
"$FLY" secrets set "${SECRET_ARGS[@]}" --app "$APP"

URL="https://${APP}.fly.dev"
log "health probe ${URL}/health"
for i in 1 2 3 4 5 6 8 10; do
  if curl -fsS "${URL}/health" 2>/dev/null | python3 -c 'import json,sys; d=json.load(sys.stdin); sys.exit(0 if d.get("service")=="noos-loop-executor" else 1)' 2>/dev/null; then
    log "PASS — FLY_LOOP_EXECUTOR_URL=${URL}"
    log "Run: NOOS_LOOP_SECRET='***' python3 scripts/verify_noos_loop_executor_fly_v1.py --write-receipt"
    exit 0
  fi
  sleep 10
done
log "WARN: deploy submitted; /health not green yet"
exit 0
