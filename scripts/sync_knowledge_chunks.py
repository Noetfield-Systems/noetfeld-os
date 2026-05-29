#!/usr/bin/env python3
"""Sync markdown knowledge into noetfield.knowledge_chunks (Postgres)."""

from __future__ import annotations

import asyncio
import hashlib
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


async def main() -> int:
    db_url = os.environ.get("DATABASE_URL", "").strip()
    if not db_url:
        print("DATABASE_URL required", file=sys.stderr)
        return 1

    import asyncpg

    dsn = db_url.replace("postgresql+asyncpg://", "postgresql://")
    paths: list[Path] = []
    kdir = ROOT / "data" / "chatbot" / "knowledge"
    if kdir.is_dir():
        paths.extend(sorted(kdir.glob("*.md")))
    for name in ("PRODUCT_BRIEF.md", "OFFERINGS_LOCKED.md"):
        p = ROOT / name
        if p.is_file():
            paths.append(p)

    pool = await asyncpg.create_pool(dsn)
    count = 0
    async with pool.acquire() as conn:
        for path in paths:
            text = path.read_text(encoding="utf-8").strip()
            if not text:
                continue
            h = _hash(text)
            sections = text.split("\n## ")
            for i, section in enumerate(sections):
                body = section if i == 0 else "## " + section
                title = body.split("\n", 1)[0][:200]
                sh = _hash(body)
                await conn.execute(
                    """
                    insert into noetfield.knowledge_chunks
                      (source_path, section_title, content, content_hash)
                    values ($1, $2, $3, $4)
                    on conflict (content_hash) do update set
                      content = excluded.content,
                      section_title = excluded.section_title,
                      updated_at = now()
                    """,
                    str(path.relative_to(ROOT)),
                    title,
                    body[:50000],
                    sh,
                )
                count += 1
    await pool.close()
    print(f"Synced {count} knowledge chunk(s)")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
