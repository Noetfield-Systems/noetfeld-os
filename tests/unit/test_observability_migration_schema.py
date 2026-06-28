"""NF-PLAN-0104 — observability migration schema + RLS guards."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MIGRATION = ROOT / "infrastructure" / "supabase" / "migrations" / "0008_observability_tables.sql"

REQUIRED_TABLES = (
    "observability_api_requests",
    "observability_health_checks",
    "observability_slo_windows",
)


def _sql() -> str:
    return MIGRATION.read_text(encoding="utf-8")


def test_observability_migration_file_exists() -> None:
    assert MIGRATION.is_file()


def test_observability_tables_defined() -> None:
    sql = _sql()
    for table in REQUIRED_TABLES:
        assert f"create table if not exists {table}" in sql


def test_observability_rls_enabled() -> None:
    sql = _sql()
    for table in REQUIRED_TABLES:
        assert f"alter table {table} enable row level security" in sql


def test_observability_tenant_policies_defined() -> None:
    sql = _sql()
    assert "noetfield.current_tenant_id()" in sql
    assert "observability_api_requests_tenant_access" in sql
    assert "observability_health_checks_tenant_access" in sql
    assert "observability_slo_windows_tenant_access" in sql


def test_observability_migration_lexical_order() -> None:
    migrations = sorted((ROOT / "infrastructure" / "supabase" / "migrations").glob("*.sql"))
    names = [m.name for m in migrations]
    assert "0008_observability_tables.sql" in names
    assert names.index("0008_observability_tables.sql") == 7
    assert names[names.index("0008_observability_tables.sql") + 1 :] == [
        "0009_public_analytics_events.sql",
        "0010_public_analytics_funnel_tables.sql",
    ]
