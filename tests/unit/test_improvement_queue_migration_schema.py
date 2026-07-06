"""Migration 0013 — improvement_queue + probe_cron_receipts schema."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MIGRATION = ROOT / "infrastructure" / "supabase" / "migrations" / "0013_improvement_queue_and_probe_receipts.sql"

REQUIRED_TABLES = (
    "improvement_queue",
    "probe_cron_receipts",
)

REQUIRED_COLUMNS = {
    "improvement_queue": (
        "finding",
        "source",
        "expected_roi",
        "machine_safe",
        "status",
    ),
}


def _sql() -> str:
    return MIGRATION.read_text(encoding="utf-8")


def test_improvement_queue_migration_file_exists() -> None:
    assert MIGRATION.is_file()


def test_improvement_queue_tables_defined() -> None:
    sql = _sql()
    for table in REQUIRED_TABLES:
        assert f"create table if not exists {table}" in sql


def test_improvement_queue_columns_defined() -> None:
    sql = _sql()
    for col in REQUIRED_COLUMNS["improvement_queue"]:
        assert col in sql


def test_probe_receipt_status_check() -> None:
    sql = _sql()
    assert "probe_cron_receipts" in sql
    assert "'pass'" in sql and "'fail'" in sql


def test_improvement_queue_migration_lexical_order() -> None:
    migrations = sorted((ROOT / "infrastructure" / "supabase" / "migrations").glob("*.sql"))
    names = [m.name for m in migrations]
    assert "0013_improvement_queue_and_probe_receipts.sql" in names
    idx = names.index("0013_improvement_queue_and_probe_receipts.sql")
    tail = names[idx:]
    assert tail[:3] == [
        "0013_improvement_queue_and_probe_receipts.sql",
        "0014_probe_tables_public_rest.sql",
        "0015_operations_signal_triage.sql",
    ]
