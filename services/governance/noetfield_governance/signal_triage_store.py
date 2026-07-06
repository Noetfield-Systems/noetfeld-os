"""Persistence for Signal Factory triage verdicts."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any
from uuid import UUID

import asyncpg


@dataclass(frozen=True)
class UntriagedSignal:
    signal_id: UUID
    signal_type: str
    subject: str
    from_addr: str
    payload: dict[str, Any]
    received_at: object


def _payload_dict(raw: object) -> dict[str, Any]:
    if raw is None:
        return {}
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, str):
        try:
            parsed = json.loads(raw)
            return parsed if isinstance(parsed, dict) else {}
        except json.JSONDecodeError:
            return {}
    return dict(raw)  # type: ignore[arg-type]


class SignalTriageStore:
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

    async def list_untriaged(
        self,
        *,
        signal_type: str = "operations_inbox_email",
        limit: int = 25,
    ) -> list[UntriagedSignal]:
        await self.connect()
        assert self._pool is not None
        async with self._pool.acquire() as connection:
            rows = await connection.fetch(
                """
                select s.id, s.signal_type, s.payload, s.received_at
                from noetfield.signals s
                left join noetfield.operations_signal_triage t on t.signal_id = s.id
                where s.signal_type = $1
                  and t.signal_id is null
                order by s.received_at asc
                limit $2
                """,
                signal_type,
                limit,
            )
        out: list[UntriagedSignal] = []
        for row in rows:
            payload = _payload_dict(row["payload"])
            out.append(
                UntriagedSignal(
                    signal_id=UUID(str(row["id"])),
                    signal_type=str(row["signal_type"]),
                    subject=str(payload.get("subject") or ""),
                    from_addr=str(payload.get("from_addr") or payload.get("from") or ""),
                    payload=payload,
                    received_at=row["received_at"],
                )
            )
        return out

    async def save_verdict(
        self,
        *,
        signal_id: UUID,
        verdict: str,
        route: str,
        label: str,
        risk_score: int,
        rubric: dict[str, Any],
        telegram_message_id: int | None = None,
    ) -> None:
        await self.connect()
        assert self._pool is not None
        async with self._pool.acquire() as connection:
            await connection.execute(
                """
                insert into noetfield.operations_signal_triage (
                  signal_id, verdict, route, label, risk_score, rubric, telegram_message_id
                )
                values ($1, $2, $3, $4, $5, $6::jsonb, $7)
                on conflict (signal_id) do update
                set verdict = excluded.verdict,
                    route = excluded.route,
                    label = excluded.label,
                    risk_score = excluded.risk_score,
                    rubric = excluded.rubric,
                    telegram_message_id = coalesce(excluded.telegram_message_id, operations_signal_triage.telegram_message_id),
                    triaged_at = now()
                """,
                signal_id,
                verdict,
                route,
                label[:200],
                risk_score,
                json.dumps(rubric, default=str),
                telegram_message_id,
            )

    async def latest_verdicts(self, *, limit: int = 5) -> list[dict[str, Any]]:
        await self.connect()
        assert self._pool is not None
        async with self._pool.acquire() as connection:
            rows = await connection.fetch(
                """
                select signal_id, verdict, route, label, risk_score, triaged_at, telegram_message_id
                from noetfield.operations_signal_triage
                order by triaged_at desc
                limit $1
                """,
                limit,
            )
        return [dict(row) for row in rows]
