#!/bin/sh
set -eu

# Railway / Render often provide postgresql:// — normalize for asyncpg consumers.
case "${DATABASE_URL:-}" in
  postgresql://*)
    export DATABASE_URL="postgresql+asyncpg://${DATABASE_URL#postgresql://}"
    ;;
  postgres://*)
    export DATABASE_URL="postgresql+asyncpg://${DATABASE_URL#postgres://}"
    ;;
esac

export RUNTIME_EVENT_STORE="${RUNTIME_EVENT_STORE:-postgres}"
export INTAKE_PERSISTENCE="${INTAKE_PERSISTENCE:-auto}"
export NOETFIELD_ENV="${NOETFIELD_ENV:-prod}"
export PUBLIC_CHAT_ENABLED="${PUBLIC_CHAT_ENABLED:-true}"
export PUBLIC_INTAKE_ENABLED="${PUBLIC_INTAKE_ENABLED:-true}"
export TELEGRAM_WEBHOOK_BASE_URL="${TELEGRAM_WEBHOOK_BASE_URL:-https://platform.noetfield.com}"

PORT="${PORT:-8001}"

if [ -n "${DATABASE_URL:-}" ]; then
  python3 scripts/apply_postgres_migrations.py || {
    echo "WARN: migrations failed — continuing for health probe" >&2
  }
fi

exec uvicorn noetfield_governance.api:app \
  --host 0.0.0.0 \
  --port "$PORT" \
  --app-dir services/governance
