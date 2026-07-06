"""Scheduled operations@ IMAP sweep → signals (Signal Factory triage follows)."""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Any
from uuid import UUID

from noetfield_signals import IngestSignalCommand, SignalIngestionPipeline

from noetfield_governance.gmail_imap_client import GmailImapClient
from noetfield_governance.gmail_sweep_store import GmailSweepStore
from noetfield_governance.inbox_message import message_to_signal_payload

logger = logging.getLogger("noetfield.governance.gmail_sweep")

SIGNAL_TYPE = "operations_inbox_email"


@dataclass(frozen=True)
class GmailSweepSettings:
    enabled: bool
    mailbox: str
    app_password: str
    processed_label: str
    search_query: str
    tenant_id: UUID
    organization_id: UUID
    max_messages: int = 25


def _secret(value: object | None) -> str:
    if value is None:
        return ""
    getter = getattr(value, "get_secret_value", None)
    if callable(getter):
        return str(getter() or "").strip()
    return str(value).strip()


def settings_from_platform(settings: object) -> GmailSweepSettings | None:
    if not bool(getattr(settings, "gmail_sweep_enabled", False)):
        return None
    app_password = _secret(getattr(settings, "gmail_app_password", None)) or None
    if not app_password:
        return None
    tenant_raw = str(getattr(settings, "operations_inbox_tenant_id", "") or "").strip()
    org_raw = str(getattr(settings, "operations_inbox_organization_id", "") or "").strip()
    if not tenant_raw or not org_raw:
        return None
    return GmailSweepSettings(
        enabled=True,
        mailbox=str(getattr(settings, "gmail_mailbox", "operations@noetfield.com") or "").strip(),
        app_password=app_password,
        processed_label=str(getattr(settings, "gmail_processed_label", "nf-processed") or "nf-processed"),
        search_query=str(
            getattr(settings, "gmail_sweep_query", "label:INBOX -label:nf-processed") or ""
        ).strip(),
        tenant_id=UUID(tenant_raw),
        organization_id=UUID(org_raw),
        max_messages=int(getattr(settings, "gmail_sweep_max_messages", 25) or 25),
    )


def _parse_observed_at(received_header: str) -> datetime:
    if not received_header:
        return datetime.now(timezone.utc)
    try:
        parsed = parsedate_to_datetime(received_header)
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)
    except (TypeError, ValueError, IndexError):
        return datetime.now(timezone.utc)


class GmailSweepWorker:
    def __init__(
        self,
        *,
        sweep_settings: GmailSweepSettings,
        signal_pipeline: SignalIngestionPipeline,
        sweep_store: GmailSweepStore,
        client: GmailImapClient | None = None,
    ) -> None:
        self._settings = sweep_settings
        self._signal_pipeline = signal_pipeline
        self._store = sweep_store
        self._client = client or GmailImapClient(
            mailbox=sweep_settings.mailbox,
            app_password=sweep_settings.app_password,
            processed_label=sweep_settings.processed_label,
        )
        self._lock = asyncio.Lock()

    async def run_once(self) -> dict[str, Any]:
        async with self._lock:
            return await self._run_once_unlocked()

    async def _run_once_unlocked(self) -> dict[str, Any]:
        run_id = await self._store.start_run()
        seen = 0
        ingested = 0
        skipped = 0
        ingested_ids: list[str] = []
        try:
            refs = await asyncio.to_thread(
                self._client.list_messages,
                query=self._settings.search_query,
                max_results=self._settings.max_messages,
            )
            for ref in refs:
                seen += 1
                if await self._store.is_processed(ref.message_id):
                    skipped += 1
                    continue
                message = await asyncio.to_thread(self._client.fetch_message, ref.message_id)
                payload = message_to_signal_payload(message, mailbox=self._settings.mailbox)
                command = IngestSignalCommand(
                    tenant_id=self._settings.tenant_id,
                    organization_id=self._settings.organization_id,
                    signal_type=SIGNAL_TYPE,
                    source_event_id=message.message_id,
                    observed_at=_parse_observed_at(message.received_at),
                    payload=payload,
                    provenance={
                        "ingestion": "imap_sweep",
                        "mailbox": self._settings.mailbox,
                        "gmail_thread_id": message.thread_id,
                    },
                    actor_id="imap-sweep-worker",
                )
                signal, _trace = await self._signal_pipeline.ingest(command)
                await self._store.mark_processed(
                    gmail_message_id=message.message_id,
                    gmail_thread_id=message.thread_id,
                    signal_id=signal.signal_id,
                    subject=message.subject,
                    from_addr=message.from_addr,
                    metadata={"run_id": str(run_id)},
                )
                await asyncio.to_thread(
                    self._client.mark_processed,
                    message_id=message.message_id,
                    processed_label=self._settings.processed_label,
                )
                ingested += 1
                ingested_ids.append(message.message_id)
            result = {
                "ok": True,
                "status": "completed",
                "run_id": str(run_id),
                "messages_seen": seen,
                "messages_ingested": ingested,
                "messages_skipped": skipped,
                "ingested_message_ids": ingested_ids,
            }
            await self._store.finish_run(
                run_id,
                status="completed",
                messages_seen=seen,
                messages_ingested=ingested,
                messages_skipped=skipped,
                metadata=result,
            )
            logger.info(
                "imap_sweep_completed seen=%s ingested=%s skipped=%s",
                seen,
                ingested,
                skipped,
            )
            return result
        except Exception as exc:
            err = str(exc)[:500]
            logger.exception("imap_sweep_failed %s", err)
            await self._store.finish_run(
                run_id,
                status="failed",
                messages_seen=seen,
                messages_ingested=ingested,
                messages_skipped=skipped,
                error=err,
            )
            return {
                "ok": False,
                "status": "failed",
                "run_id": str(run_id),
                "error": err,
                "messages_seen": seen,
                "messages_ingested": ingested,
                "messages_skipped": skipped,
            }

    async def health(self) -> dict[str, Any]:
        latest = await self._store.latest_run()
        return {
            "enabled": True,
            "transport": "imap",
            "mailbox": self._settings.mailbox,
            "search_query": self._settings.search_query,
            "processed_label": self._settings.processed_label,
            "latest_run": latest,
        }


_gmail_sweep_worker: GmailSweepWorker | None = None
_gmail_sweep_task: asyncio.Task[None] | None = None


def get_gmail_sweep_worker() -> GmailSweepWorker | None:
    return _gmail_sweep_worker


async def init_gmail_sweep_worker(
    *,
    settings: object,
    signal_pipeline: SignalIngestionPipeline,
    database_url: str,
) -> GmailSweepWorker | None:
    global _gmail_sweep_worker
    sweep_settings = settings_from_platform(settings)
    if sweep_settings is None:
        _gmail_sweep_worker = None
        return None
    store = GmailSweepStore(database_url)
    await store.connect()
    _gmail_sweep_worker = GmailSweepWorker(
        sweep_settings=sweep_settings,
        signal_pipeline=signal_pipeline,
        sweep_store=store,
    )
    return _gmail_sweep_worker


async def start_gmail_sweep_scheduler(settings: object) -> None:
    global _gmail_sweep_task
    worker = get_gmail_sweep_worker()
    if worker is None or not bool(getattr(settings, "gmail_sweep_enabled", False)):
        return
    interval = max(60, int(getattr(settings, "gmail_sweep_interval_sec", 300) or 300))

    async def _loop() -> None:
        while True:
            try:
                await worker.run_once()
            except Exception:
                logger.exception("imap_sweep_scheduler_tick_failed")
            await asyncio.sleep(interval)

    if _gmail_sweep_task is None or _gmail_sweep_task.done():
        _gmail_sweep_task = asyncio.create_task(_loop())


async def stop_gmail_sweep_scheduler() -> None:
    global _gmail_sweep_task
    if _gmail_sweep_task is not None:
        _gmail_sweep_task.cancel()
        try:
            await _gmail_sweep_task
        except asyncio.CancelledError:
            pass
        _gmail_sweep_task = None
