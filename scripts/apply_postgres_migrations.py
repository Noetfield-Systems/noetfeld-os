"""Apply Noetfield PostgreSQL migrations in lexical order."""

from __future__ import annotations

import argparse
import asyncio
import os
from pathlib import Path

import asyncpg


def normalize_database_url(database_url: str) -> str:
    return database_url.replace("postgresql+asyncpg://", "postgresql://")


async def apply_migrations(database_url: str, migrations_dir: Path) -> None:
    connection = await asyncpg.connect(normalize_database_url(database_url))
    try:
        for migration in sorted(migrations_dir.glob("*.sql")):
            sql = migration.read_text(encoding="utf-8")
            await connection.execute(sql)
            print(f"applied {migration.name}")
    finally:
        await connection.close()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--database-url",
        default=os.environ.get("DATABASE_URL"),
        help="PostgreSQL URL. Defaults to DATABASE_URL.",
    )
    parser.add_argument(
        "--migrations-dir",
        default="infrastructure/supabase/migrations",
        help="Directory containing SQL migrations.",
    )
    args = parser.parse_args()
    if not args.database_url:
        raise SystemExit("DATABASE_URL is required")
    asyncio.run(apply_migrations(args.database_url, Path(args.migrations_dir)))


if __name__ == "__main__":
    main()
