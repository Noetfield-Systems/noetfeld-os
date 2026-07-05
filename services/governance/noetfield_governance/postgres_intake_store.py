"""PostgreSQL-backed public intake store."""

from __future__ import annotations

import json
import uuid
from datetime import UTC, datetime
from typing import Any

import asyncpg

from noetfield_governance.intake_store import IntakeRecord


class PostgresIntakeStore:
    def __init__(self, database_url: str) -> None:
        self._database_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
        self._pool: asyncpg.Pool | None = None

    async def connect(self) -> None:
        if self._pool is None:
            self._pool = await asyncpg.create_pool(self._database_url)

    async def close(self) -> None:
        if self._pool is not None:
            await self._pool.close()
            self._pool = None

    async def record(
        self,
        *,
        organization: str,
        contact_email: str,
        message: str,
        request_id: str | None = None,
        contact_name: str | None = None,
        sku: str = "trust_brief",
        vector: str = "web-intake",
        source: str = "api",
        metadata: dict[str, Any] | None = None,
    ) -> IntakeRecord:
        await self.connect()
        assert self._pool is not None

        if request_id:
            existing = await self.get_by_request_id(request_id)
            if existing is not None:
                return existing

        rec = IntakeRecord(
            intake_id="INT-" + uuid.uuid4().hex[:12].upper(),
            created_at=datetime.now(UTC).isoformat(),
            request_id=request_id,
            organization=organization.strip(),
            contact_name=(contact_name or "").strip() or None,
            contact_email=contact_email.strip().lower(),
            sku=sku,
            vector=vector,
            source=source,
            message=message.strip(),
            metadata=metadata or {},
        )

        async with self._pool.acquire() as connection:
            await connection.execute(
                """
                insert into noetfield.public_intakes (
                  intake_id, request_id, organization, contact_name,
                  contact_email, sku, vector, source, message, metadata
                )
                values ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10::jsonb)
                """,
                rec.intake_id,
                rec.request_id,
                rec.organization,
                rec.contact_name,
                rec.contact_email,
                rec.sku,
                rec.vector,
                rec.source,
                rec.message,
                json.dumps(rec.metadata, default=str),
            )
        return rec

    async def get_by_request_id(self, request_id: str) -> IntakeRecord | None:
        await self.connect()
        assert self._pool is not None
        async with self._pool.acquire() as connection:
            row = await connection.fetchrow(
                """
                select intake_id, created_at, request_id, organization, contact_name,
                       contact_email, sku, vector, source, message, metadata,
                       email_archive_status, email_archive_updated_at, email_archive_detail
                from noetfield.public_intakes
                where request_id = $1
                limit 1
                """,
                request_id.upper(),
            )
        if row is None:
            return None
        return _row_to_record(row)

    async def update_email_archive_status(
        self,
        *,
        request_id: str,
        status: str,
        detail: str | None = None,
    ) -> dict[str, Any] | None:
        await self.connect()
        assert self._pool is not None
        rid = request_id.strip().upper()
        async with self._pool.acquire() as connection:
            row = await connection.fetchrow(
                """
                update noetfield.public_intakes
                set email_archive_status = $2,
                    email_archive_updated_at = now(),
                    email_archive_detail = $3
                where request_id = $1
                returning intake_id, created_at, request_id, organization, contact_name,
                          contact_email, sku, vector, source, message, metadata,
                          email_archive_status, email_archive_updated_at, email_archive_detail
                """,
                rid,
                status,
                detail,
            )
        if row is None:
            return None
        return _row_to_dict(row)

    async def list_recent(self, *, limit: int = 50) -> list[dict[str, Any]]:
        await self.connect()
        assert self._pool is not None
        cap = max(1, min(limit, 100))
        async with self._pool.acquire() as connection:
            rows = await connection.fetch(
                """
                select intake_id, created_at, request_id, organization, contact_name,
                       contact_email, sku, vector, source, message, metadata,
                       email_archive_status, email_archive_updated_at, email_archive_detail
                from noetfield.public_intakes
                order by created_at desc
                limit $1
                """,
                cap,
            )
        return [_row_to_dict(row) for row in rows]

    async def count(self) -> int:
        await self.connect()
        assert self._pool is not None
        async with self._pool.acquire() as connection:
            val = await connection.fetchval("select count(*)::int from noetfield.public_intakes")
        return int(val or 0)


def _row_to_record(row: asyncpg.Record) -> IntakeRecord:
    meta = row["metadata"]
    if isinstance(meta, str):
        meta = json.loads(meta)
    created = row["created_at"]
    if hasattr(created, "isoformat"):
        created = created.isoformat()
    archive_updated = row["email_archive_updated_at"] if "email_archive_updated_at" in row else None
    if archive_updated is not None and hasattr(archive_updated, "isoformat"):
        archive_updated = archive_updated.isoformat()
    return IntakeRecord(
        intake_id=row["intake_id"],
        created_at=str(created),
        request_id=row["request_id"],
        organization=row["organization"],
        contact_name=row["contact_name"],
        contact_email=row["contact_email"],
        sku=row["sku"],
        vector=row["vector"],
        source=row["source"],
        message=row["message"],
        metadata=dict(meta or {}),
        email_archive_status=row["email_archive_status"] if "email_archive_status" in row else None,
        email_archive_updated_at=str(archive_updated) if archive_updated else None,
        email_archive_detail=row["email_archive_detail"] if "email_archive_detail" in row else None,
    )


def _row_to_dict(row: asyncpg.Record) -> dict[str, Any]:
    rec = _row_to_record(row)
    from dataclasses import asdict

    return asdict(rec)
