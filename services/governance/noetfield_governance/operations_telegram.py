"""Operations Telegram notify — Signal Factory triage verdicts to founder ops chat."""

from __future__ import annotations

import logging
from typing import Any

from noetfield_governance.signal_factory_rubric import SignalFactoryVerdict
from noetfield_governance.telegram_client import TelegramConfigurationError, send_message

logger = logging.getLogger("noetfield.governance.operations.telegram")


def format_triage_telegram(
    *,
    signal_id: str,
    subject: str,
    from_addr: str,
    verdict: SignalFactoryVerdict,
) -> str:
    lines = [
        "Signal Factory triage",
        f"verdict: {verdict.verdict}",
        f"route: {verdict.route}",
        f"label: {verdict.label}",
        f"from: {(from_addr or '—')[:120]}",
        f"subject: {(subject or '—')[:200]}",
        f"signal: {signal_id}",
        f"risk: {verdict.risk_score}",
    ]
    if verdict.sku:
        lines.append(f"sku: {verdict.sku}")
    if verdict.agent_may:
        lines.append(f"agent_may: {' · '.join(verdict.agent_may[:3])}")
    if verdict.agent_must_not:
        lines.append(f"agent_must_not: {' · '.join(verdict.agent_must_not[:2])}")
    return "\n".join(lines)


def send_triage_verdict_telegram(
    *,
    token: str,
    chat_id: str,
    signal_id: str,
    subject: str,
    from_addr: str,
    verdict: SignalFactoryVerdict,
) -> dict[str, Any]:
    if not token.strip() or not str(chat_id).strip():
        return {"ok": False, "configured": False, "error": "missing_telegram_config"}
    text = format_triage_telegram(
        signal_id=signal_id,
        subject=subject,
        from_addr=from_addr,
        verdict=verdict,
    )
    try:
        data = send_message(token=token, chat_id=chat_id, text=text, parse_mode=None)
    except TelegramConfigurationError as exc:
        return {"ok": False, "configured": False, "error": str(exc)}
    except Exception as exc:
        logger.warning("triage_telegram_failed %s", exc)
        return {"ok": False, "configured": True, "error": str(exc)[:200]}
    result = data.get("result") if isinstance(data.get("result"), dict) else {}
    message_id = result.get("message_id")
    return {
        "ok": True,
        "configured": True,
        "message_id": message_id,
    }
