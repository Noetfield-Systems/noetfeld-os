"""Gmail IMAP client — Workspace app-password path (no GCP service account key)."""

from __future__ import annotations

import email
import imaplib
import logging
from email.header import decode_header, make_header
from email.utils import parseaddr
from typing import Any

from noetfield_governance.inbox_message import GmailMessage, GmailMessageRef

logger = logging.getLogger("noetfield.governance.gmail_imap")

IMAP_HOST = "imap.gmail.com"
IMAP_PORT = 993


def _decode_header_value(value: str) -> str:
    if not value:
        return ""
    try:
        return str(make_header(decode_header(value)))
    except (email.errors.HeaderParseError, TypeError, ValueError):
        return value


def _body_text_from_message(msg: email.message.Message) -> str:
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_maintype() == "multipart":
                continue
            if part.get_content_type() == "text/plain":
                payload = part.get_payload(decode=True)
                if payload:
                    charset = part.get_content_charset() or "utf-8"
                    return payload.decode(charset, errors="replace")[:8000]
        for part in msg.walk():
            if part.get_content_type() == "text/html":
                payload = part.get_payload(decode=True)
                if payload:
                    charset = part.get_content_charset() or "utf-8"
                    return payload.decode(charset, errors="replace")[:8000]
        return ""
    payload = msg.get_payload(decode=True)
    if not payload:
        return ""
    charset = msg.get_content_charset() or "utf-8"
    return payload.decode(charset, errors="replace")[:8000]


class GmailImapClient:
    def __init__(self, *, mailbox: str, app_password: str, processed_label: str = "nf-processed") -> None:
        self._mailbox = mailbox
        self._app_password = app_password
        self._processed_label = processed_label

    def _connect(self) -> imaplib.IMAP4_SSL:
        client = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT)
        client.login(self._mailbox, self._app_password)
        return client

    def _with_imap(self, fn: Any) -> Any:
        imap = self._connect()
        try:
            return fn(imap)
        finally:
            try:
                imap.logout()
            except Exception:
                pass

    def list_messages(self, *, query: str, max_results: int = 25) -> list[GmailMessageRef]:
        del query  # IMAP path relies on DB dedupe; sweep INBOX only.

        def _list(imap: imaplib.IMAP4_SSL) -> list[GmailMessageRef]:
            refs: list[GmailMessageRef] = []
            imap.select("INBOX", readonly=True)
            _status, data = imap.uid("SEARCH", None, "UNSEEN")
            uids = (data[0] or b"").split()
            if not uids:
                _status, data = imap.uid("SEARCH", None, "ALL")
                uids = (data[0] or b"").split()
            for raw_uid in uids[-max_results:]:
                uid = raw_uid.decode("ascii", errors="ignore")
                if uid:
                    refs.append(GmailMessageRef(message_id=f"imap:{uid}", thread_id=f"imap-thread:{uid}"))
            return refs

        return self._with_imap(_list)

    def fetch_message(self, message_id: str) -> GmailMessage:
        uid = message_id.removeprefix("imap:")

        def _fetch(imap: imaplib.IMAP4_SSL) -> GmailMessage:
            imap.select("INBOX", readonly=True)
            _status, data = imap.uid("FETCH", uid, "(RFC822)")
            if not data or not data[0]:
                raise RuntimeError(f"imap_fetch_failed:{message_id}")
            raw = data[0][1] if isinstance(data[0], tuple) else b""
            msg = email.message_from_bytes(raw)
            headers = {k.lower(): v for k, v in msg.items()}
            subject = _decode_header_value(headers.get("subject", ""))
            from_addr = _decode_header_value(headers.get("from", ""))
            to_addrs = [
                parseaddr(item)[1]
                for item in _decode_header_value(headers.get("to", "")).split(",")
                if item.strip()
            ]
            cc_addrs = [
                parseaddr(item)[1]
                for item in _decode_header_value(headers.get("cc", "")).split(",")
                if item.strip()
            ]
            body_text = _body_text_from_message(msg)
            snippet = (body_text or subject)[:200]
            return GmailMessage(
                message_id=message_id,
                thread_id=f"imap-thread:{uid}",
                subject=subject,
                from_addr=from_addr,
                to_addrs=to_addrs,
                cc_addrs=cc_addrs,
                received_at=headers.get("date", ""),
                snippet=snippet,
                body_text=body_text,
                headers=headers,
            )

        return self._with_imap(_fetch)

    def mark_processed(self, *, message_id: str, processed_label: str) -> None:
        uid = message_id.removeprefix("imap:")
        label = processed_label or self._processed_label

        def _mark(imap: imaplib.IMAP4_SSL) -> None:
            imap.select("INBOX", readonly=False)
            imap.uid("STORE", uid, "+FLAGS", "\\Seen")
            try:
                imap.uid("STORE", uid, "+X-GM-LABELS", f"({label})")
            except imaplib.IMAP4.error as exc:
                logger.warning("imap_label_apply_failed uid=%s err=%s", uid, exc)

        self._with_imap(_mark)
