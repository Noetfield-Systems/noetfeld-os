"""Shared inbox status constants for cloud worker + Supabase sink."""

from __future__ import annotations

FOUNDER_BLOCKED_STATUS = "founder_blocked"
FOUNDER_BLOCKED_REASON = "founder_decision_required"

# Re-enqueue must never downgrade these back to pending.
PRESERVED_INBOX_STATUSES = frozenset(
    {
        "dispatched",
        "completed",
        "cancelled",
        FOUNDER_BLOCKED_STATUS,
    }
)

# cancelled = explicitly never-run; not used for founder gates.
NEVER_RUN_STATUS = "cancelled"
