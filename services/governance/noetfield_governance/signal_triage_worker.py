"""Signal Factory triage worker — rubric on unprocessed inbox signals → Telegram verdict."""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from typing import Any
from uuid import UUID

from noetfield_governance.operations_telegram import send_triage_verdict_telegram
from noetfield_governance.signal_factory_rubric import classify_operations_inbox_payload
from noetfield_governance.signal_triage_store import SignalTriageStore

logger = logging.getLogger("noetfield.governance.signal_triage")

SIGNAL_TYPE = "operations_inbox_email"


@dataclass(frozen=True)
class SignalTriageSettings:
    enabled: bool
    telegram_token: str
    telegram_chat_id: str
    max_signals: int = 25


def _secret(value: object | None) -> str:
    if value is None:
        return ""
    getter = getattr(value, "get_secret_value", None)
    if callable(getter):
        return str(getter() or "").strip()
    return str(value).strip()


def settings_from_platform(settings: object) -> SignalTriageSettings | None:
    if not bool(getattr(settings, "signal_triage_enabled", False)):
        return None
    token = _secret(getattr(settings, "telegram_ops_bot_token", None)) or _secret(
        getattr(settings, "telegram_bot_token", None)
    )
    chat_id = str(getattr(settings, "telegram_ops_chat_id", "") or "").strip()
    if not token or not chat_id:
        return None
    return SignalTriageSettings(
        enabled=True,
        telegram_token=token,
        telegram_chat_id=chat_id,
        max_signals=int(getattr(settings, "signal_triage_max_signals", 25) or 25),
    )


class SignalTriageWorker:
    def __init__(
        self,
        *,
        triage_settings: SignalTriageSettings,
        triage_store: SignalTriageStore,
    ) -> None:
        self._settings = triage_settings
        self._store = triage_store
        self._lock = asyncio.Lock()

    async def run_once(self) -> dict[str, Any]:
        async with self._lock:
            return await self._run_once_unlocked()

    async def _run_once_unlocked(self) -> dict[str, Any]:
        pending = await self._store.list_untriaged(
            signal_type=SIGNAL_TYPE,
            limit=self._settings.max_signals,
        )
        triaged = 0
        telegram_sent = 0
        verdicts: list[dict[str, Any]] = []
        for item in pending:
            factory_verdict = classify_operations_inbox_payload(item.payload)
            rubric = factory_verdict.to_rubric_json()
            telegram_message_id: int | None = None
            tg = await asyncio.to_thread(
                send_triage_verdict_telegram,
                token=self._settings.telegram_token,
                chat_id=self._settings.telegram_chat_id,
                signal_id=str(item.signal_id),
                subject=item.subject,
                from_addr=item.from_addr,
                verdict=factory_verdict,
            )
            if tg.get("ok"):
                telegram_sent += 1
                mid = tg.get("message_id")
                if isinstance(mid, int):
                    telegram_message_id = mid
            await self._store.save_verdict(
                signal_id=item.signal_id,
                verdict=factory_verdict.verdict,
                route=factory_verdict.route,
                label=factory_verdict.label,
                risk_score=factory_verdict.risk_score,
                rubric=rubric,
                telegram_message_id=telegram_message_id,
            )
            triaged += 1
            verdicts.append(
                {
                    "signal_id": str(item.signal_id),
                    "verdict": factory_verdict.verdict,
                    "route": factory_verdict.route,
                    "telegram_delivered": bool(tg.get("ok")),
                }
            )
        result = {
            "ok": True,
            "status": "completed",
            "pending_seen": len(pending),
            "triaged": triaged,
            "telegram_sent": telegram_sent,
            "verdicts": verdicts,
        }
        if triaged:
            logger.info(
                "signal_triage_completed triaged=%s telegram_sent=%s",
                triaged,
                telegram_sent,
            )
        return result

    async def health(self) -> dict[str, Any]:
        latest = await self._store.latest_verdicts(limit=3)
        return {
            "enabled": True,
            "signal_type": SIGNAL_TYPE,
            "latest_verdicts": latest,
        }


_signal_triage_worker: SignalTriageWorker | None = None
_signal_triage_task: asyncio.Task[None] | None = None


def get_signal_triage_worker() -> SignalTriageWorker | None:
    return _signal_triage_worker


async def init_signal_triage_worker(*, settings: object, database_url: str) -> SignalTriageWorker | None:
    global _signal_triage_worker
    triage_settings = settings_from_platform(settings)
    if triage_settings is None:
        _signal_triage_worker = None
        return None
    store = SignalTriageStore(database_url)
    await store.connect()
    _signal_triage_worker = SignalTriageWorker(
        triage_settings=triage_settings,
        triage_store=store,
    )
    return _signal_triage_worker


async def start_signal_triage_scheduler(settings: object) -> None:
    global _signal_triage_task
    worker = get_signal_triage_worker()
    if worker is None or not bool(getattr(settings, "signal_triage_enabled", False)):
        return
    interval = max(30, int(getattr(settings, "signal_triage_interval_sec", 120) or 120))

    async def _loop() -> None:
        while True:
            try:
                await worker.run_once()
            except Exception:
                logger.exception("signal_triage_scheduler_tick_failed")
            await asyncio.sleep(interval)

    if _signal_triage_task is None or _signal_triage_task.done():
        _signal_triage_task = asyncio.create_task(_loop())


async def stop_signal_triage_scheduler() -> None:
    global _signal_triage_task
    if _signal_triage_task is not None:
        _signal_triage_task.cancel()
        try:
            await _signal_triage_task
        except asyncio.CancelledError:
            pass
        _signal_triage_task = None
