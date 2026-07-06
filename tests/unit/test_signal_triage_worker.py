"""Signal triage worker tests."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, patch
from uuid import uuid4

from noetfield_governance.signal_factory_rubric import SignalFactoryVerdict
from noetfield_governance.signal_triage_store import UntriagedSignal, _payload_dict
from noetfield_governance.signal_triage_worker import SignalTriageSettings, SignalTriageWorker


def test_payload_dict_parses_json_string() -> None:
    raw = '{"subject": "Hi", "from": "a@b.com"}'
    payload = _payload_dict(raw)
    assert payload["subject"] == "Hi"
    assert payload["from"] == "a@b.com"


def test_signal_triage_worker_triages_and_notifies() -> None:
    async def run() -> None:
        settings = SignalTriageSettings(
            enabled=True,
            telegram_token="token",
            telegram_chat_id="123",
            max_signals=5,
        )
        store = AsyncMock()
        signal_id = uuid4()
        store.list_untriaged.return_value = [
            UntriagedSignal(
                signal_id=signal_id,
                signal_type="operations_inbox_email",
                subject="Trust Brief",
                from_addr="lead@example.com",
                payload={
                    "channel": "operations_inbox",
                    "subject": "Trust Brief",
                    "from_addr": "lead@example.com",
                    "body_text": "Trust Brief kickoff please",
                },
                received_at=None,
            )
        ]
        store.save_verdict.return_value = None
        store.latest_verdicts.return_value = []

        worker = SignalTriageWorker(triage_settings=settings, triage_store=store)
        with patch(
            "noetfield_governance.signal_triage_worker.send_triage_verdict_telegram",
            return_value={"ok": True, "message_id": 99},
        ):
            result = await worker.run_once()

        assert result["ok"] is True
        assert result["triaged"] == 1
        assert result["telegram_sent"] == 1
        store.save_verdict.assert_awaited_once()
        args = store.save_verdict.await_args.kwargs
        assert args["signal_id"] == signal_id
        assert args["verdict"] == "REQUIRE_HUMAN_REVIEW"
        assert args["telegram_message_id"] == 99

    asyncio.run(run())


def test_format_triage_telegram_shape() -> None:
    from noetfield_governance.operations_telegram import format_triage_telegram

    text = format_triage_telegram(
        signal_id="sig-1",
        subject="Subject",
        from_addr="a@b.com",
        verdict=SignalFactoryVerdict(
            verdict="PROCEED",
            route="sandbox_nurture",
            label="Sandbox nurture",
            sku=None,
            risk_score=20,
        ),
    )
    assert "Signal Factory triage" in text
    assert "verdict: PROCEED" in text
    assert "signal: sig-1" in text
