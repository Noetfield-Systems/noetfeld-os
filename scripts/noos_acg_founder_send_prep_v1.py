#!/usr/bin/env python3
"""Step 9 prep — ACG founder send gate (machine prepares; founder acts)."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PREP_RECEIPT = ROOT / "noetfield-org/receipts/NOOS_ACG_FOUNDER_SEND_PREP_2026-07-05.md"
SEND_TEMPLATE = ROOT / "noetfield-org/receipts/NOOS_ACG_FOUNDER_SEND_RECEIPT_TEMPLATE.md"
FOUNDER_RECEIPT = Path.home() / ".sina/nw1-outbound-send-receipt-v1.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def founder_send_exists() -> bool:
    if not FOUNDER_RECEIPT.is_file():
        return False
    try:
        row = json.loads(FOUNDER_RECEIPT.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return False
    status = str(row.get("nw1_status") or "").lower()
    if status in {"awaiting_founder_send_click", "draft", "pending"}:
        return False
    if row.get("founder_approved") and row.get("send_mode") == "mail_draft_opened":
        return False
    return bool(row.get("sent_at") or row.get("first_outreach_sent") or status == "sent")


def build_prep() -> dict[str, Any]:
    packet = {
        "sourcea_branch": "preserve/acg-2026-07-05",
        "packet_commit": "bfc05dbb2c7ff102dee6380e8a202dae493c11d1",
        "packet_path": "docs/commercial/ACG_FIRST_PROSPECT_PACKET_v1.md",
        "live_url": "https://www.noetfield.com/services/agentic-cost-governance",
        "noetfield_commit": "096428e2",
    }
    send_done = founder_send_exists()
    return {
        "schema": "noos-acg-founder-send-prep-v1",
        "prepared_at": utc_now(),
        "service_id": "svc-cost-audit-firewall-001",
        "current_lane_state": "PUBLIC_PAGE_LIVE + PROSPECT_PACKET_READY",
        "target_lane_state": "FIRST_OUTREACH_SENT",
        "packet": packet,
        "founder_gate": "FT-COMMERCIAL-SEND",
        "upg_id": "UPG-0001",
        "founder_send_receipt_exists": send_done,
        "founder_send_receipt_path": str(FOUNDER_RECEIPT),
        "machine_may_update_lane": send_done,
        "ok": True,
        "report_line": (
            f"acg_founder_send_prep · send_receipt={'yes' if send_done else 'pending_founder'}"
        ),
    }


def write_markdown(row: dict[str, Any]) -> None:
    PREP_RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    PREP_RECEIPT.write_text(
        "\n".join(
            [
                "# NOOS ACG Founder Send Prep",
                "",
                f"**Prepared:** {row['prepared_at']}",
                f"**Service:** {row['service_id']}",
                f"**Gate:** {row['founder_gate']} ({row['upg_id']})",
                "",
                "## Packet facts",
                f"- SourceA branch: `{row['packet']['sourcea_branch']}`",
                f"- Packet commit: `{row['packet']['packet_commit']}`",
                f"- Packet path: `{row['packet']['packet_path']}`",
                f"- Live URL: {row['packet']['live_url']}",
                "",
                "## Founder action required",
                "1. Review ACG_FIRST_PROSPECT_PACKET_v1.md on SourceA preserve branch",
                "2. Send first NW1 prospect outreach (founder authority only)",
                f"3. Write send receipt: `{row['founder_send_receipt_path']}`",
                "",
                f"**Send receipt on disk:** {'yes' if row['founder_send_receipt_exists'] else 'no — lane stays PROSPECT_PACKET_READY'}",
                "",
                "## Founder blocker (machine)",
                "NW1 draft receipt may exist at `~/.sina/nw1-outbound-send-receipt-v1.json` with "
                "`nw1_status: awaiting_founder_send_click` — that is **not** FIRST_OUTREACH_SENT.",
                "Machine will not advance lane until founder records a completed send receipt.",
                "",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    if not SEND_TEMPLATE.is_file():
        SEND_TEMPLATE.write_text(
            '{"schema":"nw1-outbound-send-receipt-v1","sent_at":"","prospect":"","channel":"email","packet_commit":"bfc05dbb"}\n',
            encoding="utf-8",
        )


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write-receipt", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    row = build_prep()
    if args.write_receipt:
        write_markdown(row)
        row["receipt_path"] = str(PREP_RECEIPT.relative_to(ROOT))

    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row["report_line"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
