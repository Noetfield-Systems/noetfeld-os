"""Agent run + tool call audit persistence (v1) — linked to RID."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Protocol
from uuid import UUID, uuid4

import asyncpg
from pydantic import BaseModel, ConfigDict, Field


class ToolCallRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tool_call_id: UUID = Field(default_factory=uuid4)
    tool_name: str
    arguments: dict[str, object] = Field(default_factory=dict)
    result_status: str = Field(description="ok | denied | error")
    recorded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AgentRun(BaseModel):
    model_config = ConfigDict(extra="forbid")

    run_id: UUID = Field(default_factory=uuid4)
    tenant_id: UUID
    organization_id: UUID
    agent_id: str
    rid: str | None = None
    workflow_id: UUID | None = None
    tool_calls: list[ToolCallRecord] = Field(default_factory=list)
    verification_status: str = Field(default="pending", description="pending | verified | rejected")
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: datetime | None = None


class AgentRunStore(Protocol):
    async def append_run(self, run: AgentRun) -> AgentRun:
        ...


@dataclass
class InMemoryAgentRunStore:
    runs: list[AgentRun] = field(default_factory=list)

    async def append_run(self, run: AgentRun) -> AgentRun:
        self.runs.append(run)
        return run


class PostgresAgentRunStore:
    """Persists agent runs and tool calls for copilot-governance demo replay."""

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

    async def append_run(self, run: AgentRun) -> AgentRun:
        await self.connect()
        assert self._pool is not None
        async with self._pool.acquire() as connection:
            await connection.execute(
                """
                insert into noetfield.copilot_agent_runs (
                  id, tenant_id, organization_id, agent_id, rid, workflow_id,
                  verification_status, tool_calls, started_at, completed_at
                )
                values ($1, $2, $3, $4, $5, $6, $7, $8::jsonb, $9, $10)
                """,
                run.run_id,
                run.tenant_id,
                run.organization_id,
                run.agent_id,
                run.rid,
                str(run.workflow_id) if run.workflow_id else None,
                run.verification_status,
                json.dumps([t.model_dump(mode="json") for t in run.tool_calls], default=str),
                run.started_at,
                run.completed_at,
            )
        return run


DENIED_TOOLS_DEFAULT = frozenset(
    {
        "payment_initiate",
        "transfer_funds",
        "ledger_post",
        "m365_write",
        "publish_without_verification",
    }
)


def guard_tool_call(tool_name: str, allowed_actions: list[str]) -> ToolCallRecord:
    """Deny-by-default unless tool is explicitly allowed."""
    if tool_name in DENIED_TOOLS_DEFAULT:
        return ToolCallRecord(
            tool_name=tool_name,
            result_status="denied",
            arguments={"reason": "deny_tools_default"},
        )
    if tool_name not in allowed_actions:
        return ToolCallRecord(
            tool_name=tool_name,
            result_status="denied",
            arguments={"reason": "not_in_allowed_actions"},
        )
    return ToolCallRecord(tool_name=tool_name, result_status="ok")
