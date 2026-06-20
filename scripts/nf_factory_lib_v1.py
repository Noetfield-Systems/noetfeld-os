#!/usr/bin/env python3
"""Shared helpers for NF-GAOS factory spine (W3)."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path


def iso_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def events_dir(root: Path | None = None) -> Path:
    d = (root or repo_root()) / "reports/agent-auto/events"
    d.mkdir(parents=True, exist_ok=True)
    return d


def sina_dir() -> Path:
    d = Path.home() / ".sina"
    d.mkdir(parents=True, exist_ok=True)
    return d


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def write_event(name: str, data: dict, root: Path | None = None) -> Path:
    path = events_dir(root) / name
    write_json(path, data)
    return path


def write_sina(name: str, data: dict) -> Path | None:
    try:
        path = sina_dir() / name
        write_json(path, data)
        return path
    except OSError:
        return None


def load_json(path: Path) -> dict | None:
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def load_event(name: str, root: Path | None = None) -> dict | None:
    return load_json(events_dir(root) / name)


def load_sina(name: str) -> dict | None:
    return load_json(sina_dir() / name)


def first_pending_task(plan: dict) -> dict | None:
    for row in plan.get("next_tasks") or []:
        if str(row.get("status", "")).lower() == "pending":
            return row
    return None


def agent_id() -> str:
    return os.environ.get("NOETFIELD_AGENT_ID", "noetfield_cloud")


def load_lock() -> dict | None:
    return load_sina("nf-executor-lock-v1.json") or load_event("nf-executor-lock-v1.json")


def write_lock(data: dict, root: Path | None = None) -> None:
    write_event("nf-executor-lock-v1.json", data, root)
    write_sina("nf-executor-lock-v1.json", data)


def write_ops_live_witness(surfaces: dict, root: Path | None = None) -> Path:
    """Git-tracked witness — both agents read git main; never www."""
    root = root or repo_root()
    gov = root / "governance"
    gov.mkdir(parents=True, exist_ok=True)
    charter = root / "docs/platform/NF_LIVING_SYSTEM_CHARTER_DRAFT_v3.md"
    witness = {
        "schema_version": "ops-live-status-locked-v1",
        "visibility": "internal-agent-only",
        "not_www": True,
        "audience": ["NF-LOCAL-REPO-AGENT", "NF-CLOUD-AGENT"],
        "witnessed_at": surfaces.get("generated_at") or iso_now(),
        "git_sha": surfaces.get("git_sha"),
        "product_now_line": surfaces.get("product_now_line"),
        "portfolio_now_line": surfaces.get("portfolio_now_line"),
        "email_send_defer_line": surfaces.get("email_send_defer_line"),
        "defer_active": surfaces.get("defer_active"),
        "gate_ok": surfaces.get("gate_ok"),
        "context_stale": surfaces.get("context_stale"),
        "mono_nerve_ok": surfaces.get("mono_nerve_ok"),
        "surfaces_ok": surfaces.get("surfaces_ok"),
        "internal_agent_docs": {
            "living_system_charter_v3": "docs/platform/NF_LIVING_SYSTEM_CHARTER_DRAFT_v3.md",
            "live_status": "reports/agent-auto/LIVE-STATUS.md",
            "routing_card": "ROUTING_CARD.md",
        },
        "charter_present": charter.is_file(),
        "quote_rule": surfaces.get("quote_rule"),
        "sync_law": "Mac nf-onboard writes this file; cloud reads git main — not www",
    }
    path = gov / "OPS_LIVE_STATUS_LOCKED.json"
    write_json(path, witness)
    return path


def sourcea_root() -> Path:
    return Path.home() / "Desktop/SourceA"


def load_wiring() -> dict | None:
    return load_json(repo_root() / "data/nf_mono_nerve_wiring_v1.json")


def portfolio_progress() -> dict | None:
    reg = Path.home() / "Desktop/1 PAGER/portfolio-300-locked/REGISTRY.json"
    if not reg.is_file():
        reg = Path("/Users/sinakazemnezhad/Desktop/1 PAGER/portfolio-300-locked/REGISTRY.json")
    if not reg.is_file():
        return None
    data = load_json(reg)
    if not data:
        return None
    plans = data.get("plans") or []
    done = sum(1 for p in plans if p.get("status") == "done")
    return {"total": len(plans), "done": done, "backlog": len(plans) - done, "registry": str(reg)}


def parse_iso(ts: str | None) -> datetime | None:
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


def mtime_iso(path: Path) -> str | None:
    if not path.is_file():
        return None
    return datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def latest_founder_cascade() -> tuple[str | None, dict | None]:
    path = sina_dir() / "founder-input-cascade-events.jsonl"
    if not path.is_file():
        return None, None
    last = None
    last_at = None
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            last = json.loads(line)
            last_at = last.get("at") or last_at
        except json.JSONDecodeError:
            continue
    return last_at, last


def cascade_requires_disk_patch(row: dict | None) -> bool:
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


def nf_inbox_path() -> Path:
    return sina_dir() / "agent-workspaces/noetfield_cloud/INBOX.md"
