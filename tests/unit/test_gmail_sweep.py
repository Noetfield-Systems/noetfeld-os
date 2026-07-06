"""Gmail / IMAP sweep worker tests."""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from noetfield_governance.inbox_message import GmailMessage, message_to_signal_payload
from noetfield_governance.gmail_sweep_worker import GmailSweepSettings, GmailSweepWorker


def test_message_to_signal_payload_shape() -> None:
    message = GmailMessage(
        message_id="imap:42",
        thread_id="imap-thread:42",
        subject="Subject",
        from_addr="lead@example.com",
        to_addrs=["operations@noetfield.com"],
        cc_addrs=[],
        received_at="Mon, 05 Jul 2026 12:00:00 +0000",
        snippet="snippet",
        body_text="body",
        headers={"message-id": "<abc@example.com>"},
    )
    payload = message_to_signal_payload(message, mailbox="operations@noetfield.com")
    assert payload["channel"] == "operations_inbox"
    assert payload["gmail_message_id"] == "imap:42"


def test_gmail_sweep_worker_skips_processed_messages() -> None:
    async def run() -> None:
        settings = GmailSweepSettings(
            enabled=True,
            mailbox="operations@noetfield.com",
            app_password="app-pass",
            processed_label="nf-processed",
            search_query="INBOX",
            tenant_id=uuid4(),
            organization_id=uuid4(),
            max_messages=5,
        )
        store = AsyncMock()
        store.start_run.return_value = uuid4()
        store.is_processed.side_effect = [True, False]
        store.mark_processed.return_value = None
        store.finish_run.return_value = None

        client = MagicMock()
        client.list_messages.return_value = [
            MagicMock(message_id="seen", thread_id="t1"),
            MagicMock(message_id="new", thread_id="t2"),
        ]
        client.fetch_message.return_value = GmailMessage(
            message_id="new",
            thread_id="t2",
            subject="Hi",
            from_addr="lead@example.com",
            to_addrs=["operations@noetfield.com"],
            cc_addrs=[],
            received_at="Mon, 05 Jul 2026 12:00:00 +0000",
            snippet="snippet",
            body_text="body",
            headers={},
        )

        pipeline = AsyncMock()
        pipeline.ingest.return_value = (
            MagicMock(signal_id=uuid4()),
            MagicMock(),
        )

        worker = GmailSweepWorker(
            sweep_settings=settings,
            signal_pipeline=pipeline,
            sweep_store=store,
            client=client,
        )

        result = await worker.run_once()
        assert result["ok"] is True
        assert result["messages_seen"] == 2
        assert result["messages_skipped"] == 1
        assert result["messages_ingested"] == 1
        pipeline.ingest.assert_awaited_once()
        client.mark_processed.assert_called_once()

    asyncio.run(run())


def test_settings_from_platform_requires_app_password() -> None:
    from types import SimpleNamespace

    from noetfield_governance.gmail_sweep_worker import settings_from_platform

    settings = SimpleNamespace(
        gmail_sweep_enabled=True,
        gmail_app_password="app-pass",
        gmail_mailbox="operations@noetfield.com",
        gmail_processed_label="nf-processed",
        gmail_sweep_query="INBOX",
        operations_inbox_tenant_id="00000000-0000-4000-8000-000000000001",
        operations_inbox_organization_id="00000000-0000-4000-8000-000000000002",
        gmail_sweep_max_messages=10,
    )
    parsed = settings_from_platform(settings)
    assert parsed is not None
    assert parsed.app_password == "app-pass"

    missing = SimpleNamespace(
        gmail_sweep_enabled=True,
        gmail_app_password=None,
        gmail_mailbox="operations@noetfield.com",
        gmail_processed_label="nf-processed",
        gmail_sweep_query="INBOX",
        operations_inbox_tenant_id="00000000-0000-4000-8000-000000000001",
        operations_inbox_organization_id="00000000-0000-4000-8000-000000000002",
        gmail_sweep_max_messages=10,
    )
    assert settings_from_platform(missing) is None
