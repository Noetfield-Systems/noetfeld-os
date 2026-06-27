#!/usr/bin/env bash
# UPG-SUPABASE-001 — apply migrations, heartbeat, optional Railway wire-up.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

VAULT="${HOME}/.sina/secrets.env"
SOURCEA_SECRETS="${HOME}/.sourcea-secrets/noetfield.env"
SOURCEA_DB_SECRETS="${HOME}/.sourcea-secrets/noetfield-db.env"
SOURCEA_ROOT="${SOURCEA_ROOT:-${HOME}/Desktop/sourceA}"
SOURCEA_NOETFIELD_INFRA="${SOURCEA_ROOT}/infra/supabase/noetfield"
REF="${NOETFIELD_SUPABASE_REF:-tkgpapowwplupyekpivy}"
RAILWAY_SERVICE="${RAILWAY_API_SERVICE:-platform-api}"

log() { printf '[supabase-001] %s\n' "$*"; }
die() { log "FAIL: $*"; exit 1; }

read_vault() {
  local key="$1"
  [[ -f "$VAULT" ]] || return 1
  grep -E "^${key}=" "$VAULT" | tail -1 | cut -d= -f2- | tr -d '"' || true
}

load_env() {
  # SourceA lane: live keys in ~/.sourcea-secrets/ (scaffolded from Desktop/sourceA/infra/supabase/noetfield/)
  if [[ -f "$SOURCEA_SECRETS" ]]; then
    # shellcheck disable=SC1090
    set -a && source "$SOURCEA_SECRETS" && set +a
  elif [[ -f "${SOURCEA_NOETFIELD_INFRA}/config.env" ]]; then
    set -a && source "${SOURCEA_NOETFIELD_INFRA}/config.env" && set +a
  fi
  if [[ -f "$SOURCEA_DB_SECRETS" ]]; then
    # shellcheck disable=SC1090
    set -a && source "$SOURCEA_DB_SECRETS" && set +a
  elif [[ -f "${SOURCEA_NOETFIELD_INFRA}/config.db.env" ]]; then
    set -a && source "${SOURCEA_NOETFIELD_INFRA}/config.db.env" && set +a
  fi
  SUPABASE_URL="${NOETFIELD_SUPABASE_URL:-${SUPABASE_URL:-$(read_vault NOETFIELD_SUPABASE_URL || true)}}"
  SUPABASE_ANON="${NOETFIELD_SUPABASE_ANON_KEY:-${SUPABASE_ANON_KEY:-$(read_vault NOETFIELD_SUPABASE_ANON_KEY || true)}}"
  SUPABASE_SERVICE="${NOETFIELD_SUPABASE_SERVICE_ROLE_KEY:-${SUPABASE_SERVICE_ROLE_KEY:-$(read_vault NOETFIELD_SUPABASE_SERVICE_ROLE_KEY || true)}}"
  DATABASE_URL="${NOETFIELD_SUPABASE_DATABASE_URL:-${SUPABASE_DATABASE_URL:-$(read_vault NOETFIELD_SUPABASE_DATABASE_URL || true)}}"
  DB_PASSWORD="${SUPABASE_DB_PASSWORD:-$(read_vault SUPABASE_DB_PASSWORD || true)}"

  if [[ -z "$DATABASE_URL" && -n "$DB_PASSWORD" && -n "$REF" ]]; then
    DATABASE_URL="postgresql://postgres.${REF}:${DB_PASSWORD}@aws-0-us-west-1.pooler.supabase.com:6543/postgres"
  fi

  if [[ -z "$SUPABASE_URL" && -n "$REF" ]]; then
    SUPABASE_URL="https://${REF}.supabase.co"
  fi
}

require_db() {
  [[ -n "$DATABASE_URL" ]] || die "NOETFIELD_SUPABASE_DATABASE_URL missing — add to ${VAULT} (see docs/ops/UPG_SUPABASE_001_ACTIVATION.md)"
}

require_api() {
  [[ -n "$SUPABASE_URL" && -n "$SUPABASE_ANON" ]] || die "NOETFIELD_SUPABASE_URL + NOETFIELD_SUPABASE_ANON_KEY required for heartbeat"
}

run_migrations() {
  if [[ -z "$DATABASE_URL" ]]; then
    log "SKIP migrations — add SUPABASE_DB_PASSWORD to ${SOURCEA_DB_SECRETS} (copy from ${SOURCEA_NOETFIELD_INFRA}/config.db.example.env)"
    return 0
  fi
  log "Applying migrations to Supabase Postgres…"
  python3 scripts/apply_postgres_migrations.py --database-url "$DATABASE_URL"
}

run_heartbeat() {
  [[ -n "$SUPABASE_URL" ]] || die "SUPABASE_URL missing (expected in ${SOURCEA_SECRETS})"
  log "REST heartbeat → ${SUPABASE_URL}"

  local anon_code svc_code storage_code
  if [[ -n "$SUPABASE_ANON" ]]; then
    anon_code="$(curl -sS -o /dev/null -w '%{http_code}' \
      "${SUPABASE_URL}/rest/v1/" \
      -H "apikey: ${SUPABASE_ANON}" \
      -H "Authorization: Bearer ${SUPABASE_ANON}" || echo 000)"
    log "REST anon ping HTTP ${anon_code}"
  fi

  if [[ -n "$SUPABASE_SERVICE" ]]; then
    svc_code="$(curl -sS -o /dev/null -w '%{http_code}' \
      "${SUPABASE_URL}/rest/v1/" \
      -H "apikey: ${SUPABASE_SERVICE}" \
      -H "Authorization: Bearer ${SUPABASE_SERVICE}" || echo 000)"
    storage_code="$(curl -sS -o /dev/null -w '%{http_code}' \
      "${SUPABASE_URL}/storage/v1/bucket" \
      -H "apikey: ${SUPABASE_SERVICE}" \
      -H "Authorization: Bearer ${SUPABASE_SERVICE}" || echo 000)"
    log "REST service_role ping HTTP ${svc_code}; storage HTTP ${storage_code}"
    if [[ "$svc_code" != "200" && "$svc_code" != "401" && "$svc_code" != "406" ]]; then
      die "service_role REST ping failed HTTP ${svc_code}"
    fi
  else
    [[ -n "$SUPABASE_ANON" ]] || die "SUPABASE_ANON_KEY or SUPABASE_SERVICE_ROLE_KEY required"
    if [[ "$anon_code" != "200" && "$anon_code" != "401" ]]; then
      die "REST ping returned HTTP ${anon_code}"
    fi
  fi

  if [[ -n "$DATABASE_URL" ]]; then
    log "SQL heartbeat SELECT 1…"
    python3 - <<'PY'
import asyncio, os, asyncpg

async def main() -> None:
    url = os.environ["DATABASE_URL"].replace("postgresql+asyncpg://", "postgresql://")
    conn = await asyncpg.connect(url)
    try:
        val = await conn.fetchval("select 1")
        assert val == 1
        applied = await conn.fetchval(
            "select count(*) from noetfield.schema_migrations"
        )
        print(f"schema_migrations rows: {applied}")
    finally:
        await conn.close()

asyncio.run(main())
PY
    log "SQL heartbeat OK"
  fi
}

wire_railway() {
  command -v railway >/dev/null || die "railway CLI not installed"
  [[ -n "$SUPABASE_URL" && -n "$SUPABASE_SERVICE" ]] || die "SUPABASE_URL + service role key required"

  log "Setting Railway ${RAILWAY_SERVICE} Supabase env vars…"
  RAILWAY_CALLER="skill:use-railway" railway variable set --service "$RAILWAY_SERVICE" \
    "SUPABASE_URL=${SUPABASE_URL}" \
    "SUPABASE_ANON_KEY=${SUPABASE_ANON}" \
    "SUPABASE_SERVICE_ROLE_KEY=${SUPABASE_SERVICE}"

  if [[ -n "$DATABASE_URL" ]]; then
    log "Setting Railway DATABASE_URL → Supabase pooler…"
    RAILWAY_CALLER="skill:use-railway" railway variable set --service "$RAILWAY_SERVICE" \
      "DATABASE_URL=${DATABASE_URL}"
  else
    log "SKIP DATABASE_URL (add SUPABASE_DB_PASSWORD to ${SOURCEA_DB_SECRETS})"
  fi

  log "Redeploying ${RAILWAY_SERVICE}…"
  RAILWAY_CALLER="skill:use-railway" railway up --service "$RAILWAY_SERVICE" -d -y
  log "Railway wire-up submitted — verify platform /health after ~2 min"
}

usage() {
  cat <<EOF
Usage: $0 [--migrations] [--heartbeat] [--wire-railway] [--all]

  --migrations    Apply infrastructure/supabase/migrations to NOETFIELD_SUPABASE_DATABASE_URL
  --heartbeat     REST + SQL ping (registers activity)
  --wire-railway  Set SUPABASE_* on platform-api (+ DATABASE_URL if password set) and redeploy
  --all           migrations + heartbeat + wire-railway

Env / vault keys: NOETFIELD_SUPABASE_URL, NOETFIELD_SUPABASE_ANON_KEY,
  NOETFIELD_SUPABASE_SERVICE_ROLE_KEY, NOETFIELD_SUPABASE_DATABASE_URL

Docs: docs/ops/UPG_SUPABASE_001_ACTIVATION.md
EOF
}

main() {
  load_env
  export DATABASE_URL SUPABASE_URL SUPABASE_ANON SUPABASE_SERVICE

  local do_mig=0 do_hb=0 do_wire=0
  if [[ $# -eq 0 ]]; then
    do_hb=1
  fi
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --migrations) do_mig=1 ;;
      --heartbeat) do_hb=1 ;;
      --wire-railway) do_wire=1 ;;
      --all) do_mig=1; do_hb=1; do_wire=1 ;;
      -h|--help) usage; exit 0 ;;
      *) die "Unknown option: $1" ;;
    esac
    shift
  done

  log "Noetfield Supabase ref=${REF} (SourceA secrets: ${SOURCEA_SECRETS})"
  [[ "$do_mig" -eq 1 ]] && run_migrations
  [[ "$do_hb" -eq 1 ]] && run_heartbeat
  [[ "$do_wire" -eq 1 ]] && wire_railway
  log "Done."
}

main "$@"
