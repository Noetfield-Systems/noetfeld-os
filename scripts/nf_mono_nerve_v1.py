#!/usr/bin/env python3
"""NF mono nerve — real-time wire to SourceA nerves, defer SSOT, founder cascade.

Law: data/nf_mono_nerve_wiring_v1.json
Receipt: reports/agent-auto/events/nf-mono-nerve-v1.json
         ~/.sina/nf-mono-nerve-v1.json

Skip = FAIL on nf-onboard. No LLM. Read-only on SourceA.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from nf_factory_lib_v1 import (
    agent_id,
    iso_now,
    load_json,
    load_sina,
    repo_root,
    write_event,
    write_sina,
)

SOURCEA_ROOT = Path.home() / "Desktop/SourceA"
DEFER_SSOT = SOURCEA_ROOT / "data/commercial-email-send-defer-v1.json"
DEFER_SCRIPT = SOURCEA_ROOT / "scripts/commercial_email_send_defer_v1.py"
SINA = Path.home() / ".sina"
NF_INBOX = SINA / "agent-workspaces/noetfield_cloud/INBOX.md"
OPERATIONS_RECEIPT = SINA / "noetfield-operations-inbox-active-v1.json"
COMMERCIAL_INBOX_DOC = "docs/ops/COMMERCIAL_INBOX_PACKAGING_LOCKED_v1.md"


def _parse_iso(ts: str | None) -> datetime | None:
    if not ts:
        return None
    raw = str(ts).strip()
    if not raw:
        return None
    try:
        if raw.endswith("Z"):
            dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        else:
            dt = datetime.fromisoformat(raw)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except ValueError:
        return None


def _mtime_iso(path: Path) -> str | None:
    if not path.is_file():
        return None
    return datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _latest_founder_cascade() -> dict | None:
    path = SINA / "founder-input-cascade-events.jsonl"
    if not path.is_file():
        return None
    last = None
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            last = json.loads(line)
        except json.JSONDecodeError:
            continue
    return last


def _cascade_requires_disk_patch(row: dict | None) -> bool:
    """Ignore governance auto-ticks; flag real founder pivots needing SHIP_NOW/INBOX."""
    if not row:
        return False
    preview = str(row.get("text_preview") or "").lower()
    source = str(row.get("source") or "").lower()
    if source == "validator_proof":
        return False
    if source in ("governance_center", "governance_specialist") and (
        "auto cycle" in preview or "self-govern" in preview
    ):
        return False
    verify = row.get("verify") or {}
    checks = verify.get("checks") or {}
    disk = checks.get("disk_truth") or {}
    if disk.get("ok") is False:
        return True
    if row.get("inbox_action") == "INBOX_STALE" and "proof test" not in preview:
        return True
    return False


def refresh_email_defer(*, write: bool = True) -> dict:
    """Run SourceA assess — refreshes ~/.sina/commercial-email-send-defer-receipt-v1.json."""
    if not DEFER_SCRIPT.is_file():
        return {"ok": False, "error": f"missing defer script {DEFER_SCRIPT}"}
    cmd = ["python3", str(DEFER_SCRIPT), "--json"]
    if not write:
        cmd.append("--no-write")
    try:
        out = subprocess.check_output(cmd, text=True, stderr=subprocess.STDOUT, timeout=120)
        row = json.loads(out)
        row["ok"] = row.get("ok", True)
        return row
    except subprocess.CalledProcessError as exc:
        try:
            row = json.loads(exc.output or "{}")
        except json.JSONDecodeError:
            row = {}
        row["ok"] = False
        row["error"] = (exc.output or str(exc))[:240]
        return row
    except (subprocess.TimeoutExpired, json.JSONDecodeError, OSError) as exc:
        return {"ok": False, "error": str(exc)[:240]}


def pulse_trustfield_fleet_wire() -> dict:
    """Sync TrustField tf-live-surfaces from fresh defer receipt (read-only on TF repo)."""
    tf_script = Path.home() / "Desktop/TrustField Technologies/scripts/tf_fleet_live_wire_v1.py"
    if not tf_script.is_file():
        return {"ok": False, "error": f"missing {tf_script}"}
    try:
        out = subprocess.check_output(
            [sys.executable, str(tf_script), "--json", "--no-refresh"],
            text=True,
            stderr=subprocess.STDOUT,
            timeout=90,
        )
        row = json.loads(out) if out.strip().startswith("{") else {}
        return {
            "ok": bool(row.get("email_send_defer_line")),
            "email_send_defer_line": row.get("email_send_defer_line"),
            "defer_active": row.get("defer_active"),
            "commercial_send_allowed": row.get("commercial_send_allowed"),
            "synced_at": row.get("synced_at"),
        }
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, json.JSONDecodeError, OSError) as exc:
        return {"ok": False, "error": str(exc)[:200]}


def write_ecosystem_nerve(nf_receipt: dict, tf_pulse: dict) -> dict:
    """Mono receipt linking Noetfield + TrustField + SourceA parent surfaces."""
    parent = load_sina("agent-live-surfaces-v1.json") or {}
    tf = load_sina("tf-live-surfaces-v1.json") or {}
    row = {
        "schema": "ecosystem-live-nerve-v1",
        "generated_at": iso_now(),
        "ok": bool(nf_receipt.get("ok")) and bool(nf_receipt.get("email_send_defer_line")),
        "email_send_defer_line": nf_receipt.get("email_send_defer_line"),
        "defer_active": nf_receipt.get("defer_active"),
        "planes": {
            "noetfield": {
                "receipt": "~/.sina/nf-mono-nerve-v1.json",
                "ok": nf_receipt.get("ok"),
                "operations_inbox": (nf_receipt.get("operations_inbox") or {}).get("gw_status"),
            },
            "trustfield": {
                "receipt": "~/.sina/tf-live-surfaces-v1.json",
                "ok": tf_pulse.get("ok"),
                "commercial_send_allowed": tf.get("commercial_send_allowed") or tf_pulse.get("commercial_send_allowed"),
            },
            "sourcea_parent": {
                "receipt": "~/.sina/agent-live-surfaces-v1.json",
                "synced_at": parent.get("synced_at"),
                "factory_now_line": parent.get("factory_now_line"),
            },
        },
        "sequencing_law": "GW inbox receive OPEN · Resend/W3 send DEFERRED until factory + sites + founder lift",
        "heal": "make nf-onboard",
    }
    write_sina("ecosystem-live-nerve-v1.json", row)
    return row


def sync_operations_inbox_receipt(root: Path) -> dict:
    """Machine receipt for operations@ GW active — synced from repo LOCK doc."""
    doc = root / COMMERCIAL_INBOX_DOC
    text = doc.read_text(encoding="utf-8", errors="replace") if doc.is_file() else ""
    gw_active = (
        "operations@noetfield.com" in text
        and "Google Workspace" in text
        and "ACTIVE" in text
    )
    resend_deferred = "DEFERRED" in text and "Resend" in text
    receipt = {
        "schema": "noetfield-operations-inbox-active-v1",
        "at": iso_now(),
        "ok": gw_active and resend_deferred,
        "inbox": "operations@noetfield.com",
        "gw_status": "ACTIVE" if gw_active else "UNKNOWN",
        "form_autonotify": "DEFERRED_POST_FACTORY" if resend_deferred else "UNKNOWN",
        "receive_lane": "OPEN" if gw_active else "BLOCKED",
        "send_lane": "DEFERRED_POST_FACTORY",
        "ssot_doc": COMMERCIAL_INBOX_DOC,
        "one_law": "GW inbox receive OPEN · Resend/form auto-send DEFERRED until after factory",
    }
    write_sina("noetfield-operations-inbox-active-v1.json", receipt)
    return receipt


def _inherit_defer_line() -> tuple[str, bool]:
    defer = load_sina("commercial-email-send-defer-receipt-v1.json") or {}
    parent = load_sina("agent-live-surfaces-v1.json") or {}
    nerve = load_sina("agent-nerve-system-receipt-v1.json") or {}
    tf = load_sina("tf-live-surfaces-v1.json") or {}
    ship = nerve.get("ship_gates") or {}

    line = (
        str(defer.get("email_send_defer_line") or "")
        or str(parent.get("email_send_defer_line") or "")
        or str(tf.get("email_send_defer_line") or "")
        or str(ship.get("email_send_defer_line") or "")
    )
    defer_active = defer.get("defer_active")
    if defer_active is None:
        defer_active = ship.get("w3_email_send_deferred", True)
    return line, bool(defer_active)


def run_mono_nerve(*, refresh: bool = True) -> dict:
    root = repo_root()
    wiring = load_json(root / "data/nf_mono_nerve_wiring_v1.json") or {}
    gates: list[dict] = []
    ok = True

    def gate(name: str, passed: bool, **extra) -> None:
        nonlocal ok
        row = {"gate": name, "ok": passed, **extra}
        gates.append(row)
        if not passed:
            ok = False

    gate("defer_ssot", DEFER_SSOT.is_file(), path=str(DEFER_SSOT))
    gate("defer_script", DEFER_SCRIPT.is_file(), path=str(DEFER_SCRIPT))
    gate("commercial_inbox_doc", (root / COMMERCIAL_INBOX_DOC).is_file(), path=COMMERCIAL_INBOX_DOC)
    gate("nf_inbox", NF_INBOX.is_file(), path=str(NF_INBOX))

    defer_row: dict = {}
    if refresh:
        defer_row = refresh_email_defer(write=True)
    else:
        defer_row = load_sina("commercial-email-send-defer-receipt-v1.json") or {}
    gate("defer_assess", bool(defer_row.get("email_send_defer_line")), detail=defer_row.get("error"))

    ops = sync_operations_inbox_receipt(root)
    gate("operations_inbox_receipt", ops.get("ok") is True, gw=ops.get("gw_status"))

    email_line, defer_active = _inherit_defer_line()
    gate("email_send_defer_line", bool(email_line), line=email_line or None)
    gate("defer_active_wired", defer_active is not None)

    parent = load_sina("agent-live-surfaces-v1.json") or {}
    gate(
        "agent_live_surfaces",
        (SINA / "agent-live-surfaces-v1.json").is_file(),
        synced_at=parent.get("synced_at"),
    )

    cascade = _latest_founder_cascade()
    cascade_at = (cascade or {}).get("at")
    ship_path = root / "os/SHIP_NOW.md"
    ship_mtime = _mtime_iso(ship_path)
    cascade_newer = False
    if _cascade_requires_disk_patch(cascade) and cascade_at and ship_mtime:
        c_dt = _parse_iso(cascade_at)
        s_dt = _parse_iso(ship_mtime)
        if c_dt and s_dt and c_dt > s_dt:
            cascade_newer = True
    gate("founder_cascade_readable", cascade is not None, latest_at=cascade_at)

    tf_pulse = pulse_trustfield_fleet_wire()
    gate("trustfield_fleet_wire", tf_pulse.get("ok") is True, detail=tf_pulse.get("error"))

    mono_at = parent.get("truth_bundle_at") or parent.get("synced_at")
    live_path = root / "reports/agent-auto/LIVE-STATUS.md"
    live_mtime = _mtime_iso(live_path)
    mono_newer = False
    if mono_at and live_mtime:
        m_dt = _parse_iso(str(mono_at).replace("+00:00", "Z") if "+00:00" in str(mono_at) else str(mono_at))
        l_dt = _parse_iso(live_mtime)
        if m_dt and l_dt and m_dt > l_dt:
            mono_newer = True

    receipt = {
        "schema_version": "nf-mono-nerve-v1",
        "generated_at": iso_now(),
        "ok": ok,
        "agent_id": agent_id(),
        "defer_active": defer_active,
        "email_send_defer_line": email_line,
        "operations_inbox": ops,
        "defer_receipt_at": defer_row.get("at"),
        "agent_live_surfaces_at": parent.get("synced_at") or parent.get("truth_bundle_at"),
        "founder_cascade_latest_at": cascade_at,
        "founder_cascade_newer_than_ship": cascade_newer,
        "mono_newer_than_live_status": mono_newer,
        "trustfield_pulse": tf_pulse,
        "gates": gates,
        "wiring_ssot": "data/nf_mono_nerve_wiring_v1.json",
        "heal": None if ok else "make nf-onboard",
        "quote_rule": "Quote product_now_line AND email_send_defer_line — not chat memory",
    }
    write_event("nf-mono-nerve-v1.json", receipt)
    write_sina("nf-mono-nerve-v1.json", receipt)
    write_ecosystem_nerve(receipt, tf_pulse)
    return receipt


def task_touches_email_lane(task: dict | None) -> bool:
    if not task:
        return False
    wiring = load_json(repo_root() / "data/nf_mono_nerve_wiring_v1.json") or {}
    patterns = wiring.get("email_task_denial_patterns") or [
        "resend", "auto-notify", "auto_notify", "w3_send", "outreach",
        "commercial_email", "send_w3", "mail_from", "form_autonotify", "email",
    ]
    blob = f"{task.get('id', '')} {task.get('title', '')}".lower()
    return any(p in blob for p in patterns)


def main() -> int:
    parser = argparse.ArgumentParser(description="NF mono nerve — SourceA + ~/.sina real-time wire")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--no-refresh", action="store_true", help="Skip SourceA defer assess refresh")
    args = parser.parse_args()

    receipt = run_mono_nerve(refresh=not args.no_refresh)
    if args.json:
        print(json.dumps(receipt, indent=2))
    else:
        status = "PASS" if receipt["ok"] else "FAIL"
        print(f"nf_mono_nerve: {status}")
        print(f"  {receipt.get('email_send_defer_line') or '(no defer line)'}")
        for g in receipt.get("gates") or []:
            if not g.get("ok"):
                print(f"  FAIL {g['gate']}")
    return 0 if receipt["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
