"""Persistence for operations@ Gmail sweep ledger."""

from __future__ import annotations

import json
from typing import Any
from uuid import UUID

import asyncpg


class GmailSweepStore:
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

    async def is_processed(self, gmail_message_id: str) -> bool:
        await self.connect()
        assert self._pool is not None
        async with self._pool.acquire() as connection:
            val = await connection.fetchval(
                """
                select 1
                from noetfield.operations_gmail_processed
                where gmail_message_id = $1
                limit 1
                """,
                gmail_message_id,
            )
        return val is not None

    async def mark_processed(
        self,
        *,
        gmail_message_id: str,
        gmail_thread_id: str,
        signal_id: UUID,
        subject: str,
        from_addr: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        await self.connect()
        assert self._pool is not None
        async with self._pool.acquire() as connection:
            await connection.execute(
                """
                insert into noetfield.operations_gmail_processed (
                  gmail_message_id, gmail_thread_id, signal_id, subject, from_addr, metadata
                )
                values ($1, $2, $3, $4, $5, $6::jsonb)
                on conflict (gmail_message_id) do nothing
                """,
                gmail_message_id,
                gmail_thread_id,
                signal_id,
                subject[:500],
                from_addr[:500],
                json.dumps(metadata or {}, default=str),
            )

    async def start_run(self) -> UUID:
        await self.connect()
        assert self._pool is not None
        async with self._pool.acquire() as connection:
            run_id = await connection.fetchval(
                """
                insert into noetfield.operations_gmail_sweep_runs (status)
                values ('running')
                returning id
                """
            )
        return UUID(str(run_id))

    async def finish_run(
        self,
        run_id: UUID,
        *,
        status: str,
        messages_seen: int,
        messages_ingested: int,
        messages_skipped: int,
        error: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        await self.connect()
        assert self._pool is not None
        async with self._pool.acquire() as connection:
            await connection.execute(
                """
                update noetfield.operations_gmail_sweep_runs
                set completed_at = now(),
                    status = $2,
                    messages_seen = $3,
                    messages_ingested = $4,
                    messages_skipped = $5,
                    error = $6,
                    metadata = coalesce(metadata, '{}'::jsonb) || $7::jsonb
                where id = $1
                """,
                run_id,
                status,
                messages_seen,
                messages_ingested,
                messages_skipped,
                error,
                json.dumps(metadata or {}, default=str),
            )

    async def latest_run(self) -> dict[str, Any] | None:
        await self.connect()
        assert self._pool is not None
        async with self._pool.acquire() as connection:
            row = await connection.fetchrow(
                """
                select id, started_at, completed_at, messages_seen, messages_ingested,
                       messages_skipped, status, error, metadata
                from noetfield.operations_gmail_sweep_runs
                order by started_at desc
                limit 1
                """
            )
        if row is None:
            return None
        return dict(row)
