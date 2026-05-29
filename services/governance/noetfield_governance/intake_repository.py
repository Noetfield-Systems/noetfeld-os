"""Intake persistence facade — memory or PostgreSQL."""

from __future__ import annotations

import logging
from typing import Any, Literal, Protocol

from noetfield_config import Settings
from noetfield_governance.intake_store import IntakeRecord
from noetfield_governance.intake_store import list_recent as memory_list_recent
from noetfield_governance.intake_store import record_intake as memory_record_intake
from noetfield_governance.postgres_intake_store import PostgresIntakeStore

logger = logging.getLogger("noetfield.governance.intake")

IntakePersistence = Literal["auto", "memory", "postgres"]


class IntakeStoreBackend(Protocol):
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
    ) -> IntakeRecord: ...

    async def list_recent(self, *, limit: int = 50) -> list[dict[str, Any]]: ...

    async def close(self) -> None: ...


class _MemoryIntakeBackend:
    async def record(self, **kwargs: Any) -> IntakeRecord:
        return memory_record_intake(**kwargs)

    async def list_recent(self, *, limit: int = 50) -> list[dict[str, Any]]:
        return memory_list_recent(limit=limit)

    async def close(self) -> None:
        return None


_backend: IntakeStoreBackend | None = None
_backend_label: str = "memory"


def resolve_persistence(settings: Settings) -> IntakePersistence:
    pref = getattr(settings, "intake_persistence", "auto")
    if pref in ("memory", "postgres"):
        return pref
    if settings.runtime_event_store == "postgres":
        return "postgres"
    return "memory"


async def init_intake_repository(settings: Settings | None = None) -> str:
    global _backend, _backend_label
    if settings is None:
        from noetfield_config import get_settings

        settings = get_settings()
    mode = resolve_persistence(settings)
    if mode == "postgres":
        store = PostgresIntakeStore(settings.database_url)
        await store.connect()
        _backend = store
        _backend_label = "postgres"
        logger.info("intake_repository mode=postgres")
    else:
        _backend = _MemoryIntakeBackend()
        _backend_label = "memory"
        logger.info("intake_repository mode=memory")
    return _backend_label


async def close_intake_repository() -> None:
    global _backend
    if _backend is not None:
        await _backend.close()
    _backend = None


def storage_label() -> str:
    return _backend_label


async def record_intake(**kwargs: Any) -> IntakeRecord:
    if _backend is None:
        await init_intake_repository()
    assert _backend is not None
    return await _backend.record(**kwargs)


async def list_recent(*, limit: int = 50) -> list[dict[str, Any]]:
    if _backend is None:
        return memory_list_recent(limit=limit)
    return await _backend.list_recent(limit=limit)
