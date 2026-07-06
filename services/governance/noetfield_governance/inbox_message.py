"""Operations inbox message model + signal payload (IMAP ingest)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GmailMessageRef:
    message_id: str
    thread_id: str


@dataclass(frozen=True)
class GmailMessage:
    message_id: str
    thread_id: str
    subject: str
    from_addr: str
    to_addrs: list[str]
    cc_addrs: list[str]
    received_at: str
    snippet: str
    body_text: str
    headers: dict[str, str]


def message_to_signal_payload(message: GmailMessage, *, mailbox: str) -> dict[str, object]:
    return {
        "channel": "operations_inbox",
        "mailbox": mailbox,
        "gmail_message_id": message.message_id,
        "gmail_thread_id": message.thread_id,
        "subject": message.subject,
        "from": message.from_addr,
        "to": message.to_addrs,
        "cc": message.cc_addrs,
        "received_at": message.received_at,
        "snippet": message.snippet,
        "body_text": message.body_text,
        "headers": {
            "message-id": message.headers.get("message-id", ""),
            "reply-to": message.headers.get("reply-to", ""),
        },
    }
