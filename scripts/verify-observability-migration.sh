#!/usr/bin/env bash
# NF-PLAN-0104 — observability migration schema + RLS (static + optional live apply).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "=== verify-observability-migration ==="
test -f infrastructure/supabase/migrations/0008_observability_tables.sql
python3 -m pytest tests/unit/test_observability_migration_schema.py -q

if [[ -n "${DATABASE_URL:-}" && ( "${DATABASE_URL}" == postgresql://* || "${DATABASE_URL}" == postgres://* || "${DATABASE_URL}" == postgresql+asyncpg://* ) ]]; then
  PYTHONPATH="${PYTHONPATH:-}:${ROOT}/packages/types:${ROOT}/packages/config" \
    python3 scripts/apply_postgres_migrations.py --migrations-dir infrastructure/supabase/migrations
  echo "live migration apply: OK"
else
  echo "no postgres DATABASE_URL — static schema checks only"
fi

echo "verify-observability-migration: OK"
