"""Gmail API client for operations@ inbox sweep (Workspace domain delegation)."""

from __future__ import annotations

# Back-compat re-exports — IMAP ingest uses inbox_message.py; GCP service account path removed.
from noetfield_governance.inbox_message import (
    GmailMessage,
    GmailMessageRef,
    message_to_signal_payload,
)

__all__ = ["GmailMessage", "GmailMessageRef", "message_to_signal_payload"]
