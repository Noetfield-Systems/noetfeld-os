#!/usr/bin/env python3
"""Compile governed NOOS/Runway/Sentinel plans into one deduplicated backlog.

D1: op_key = sha256(source_id + item_id + source_revision + content_hash)
D3: IDs from source actuals, never inference
D7: no LLM in this compiler — pure deterministic fold of source adapters
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "data/noos-unified-plan-completion-v1.json"
TERMINAL_SOURCE = {"done", "complete", "closed", "complete_closed"}
FOUNDER_SOURCE = {"founder_blocked", "founder", "awaiting_founder", "blocked_founder"}
BLOCKED_SOURCE = {"blocked", "blocked_with_reason", "deferred", "cancelled"}


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")


def content_hash(obj: Any) -> str:
    raw = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def op_key(*, source_id: str, item_id: str, source_revision: str, payload_hash: str) -> str:
    material = f"{source_id}|{item_id}|{source_revision}|{payload_hash}"
    return hashlib.sha256(material.encode("utf-8")).hexdigest()


def normalize_status(raw: Any, *, tier: str = "") -> str:
    s = str(raw or "open").strip().lower()
    if s in TERMINAL_SOURCE:
        return "COMPLETE"
    if s in FOUNDER_SOURCE or tier.upper() == "FOUNDER":
        return "FOUNDER_BLOCKED"
    if s in BLOCKED_SOURCE:
        return "BLOCKED_WITH_REASON"
    if s in {"ready", "open", "pending", "todo", "active"}:
        return "READY"
    if s in {"dispatched", "running", "in_progress"}:
        return "DISPATCHED"
    return "READY"


def map_role(item: dict[str, Any]) -> str:
    if item.get("role"):
        return str(item["role"])
    track = str(item.get("track") or item.get("lane") or "").lower()
    title = str(item.get("title") or item.get("name") or "").lower()
    if "research" in title or track in {"gov", "com"}:
        return "research"
    if "repair" in title or "self_heal" in title or "heal" in title:
        return "self_heal"
    if "specialist" in title or "patch" in title or "ci" in title:
        return "specialist"
    if "orchestr" in title or "cross-repo" in title:
        return "orchestrator"
    if "sentinel" in track or "observe" in title:
        return "incident_diagnose"
    return "research"


def map_value_class(item: dict[str, Any]) -> str:
    vc = str(item.get("value_class") or "").strip()
    if vc in {"revenue_path", "proof_asset", "risk_reduction", "hygiene"}:
        return vc
    priority = str(item.get("priority") or "").upper()
    if priority == "P0":
        return "risk_reduction"
    if "commercial" in str(item.get("title") or "").lower():
        return "revenue_path"
    return "hygiene"


def extract_items(doc: dict[str, Any], items_key: str) -> list[dict[str, Any]]:
    val = doc.get(items_key)
    if isinstance(val, list):
        return [x for x in val if isinstance(x, dict)]
    # nested common shapes
    for nest in ("unified_next_plan", "plans", "registry"):
        nested = doc.get(nest)
        if isinstance(nested, dict) and isinstance(nested.get(items_key), list):
            return [x for x in nested[items_key] if isinstance(x, dict)]
    return []


def normalize_item(
    *,
    source_id: str,
    source_revision: str,
    raw: dict[str, Any],
    index: int,
) -> dict[str, Any]:
    item_id = str(raw.get("id") or raw.get("task_id") or raw.get("plan_id") or f"{source_id}-{index}")
    payload = {
        "title": raw.get("title") or raw.get("name") or item_id,
        "status_raw": raw.get("status"),
        "tier": raw.get("tier"),
        "track": raw.get("track") or raw.get("lane"),
        "depends_on": raw.get("depends_on") or raw.get("deps") or [],
        "acceptance": raw.get("acceptance") or raw.get("success_check") or raw.get("evidence"),
        "runway_id": raw.get("runway_id"),
        "recipe_id": raw.get("recipe_id"),
        "recipe_version": raw.get("recipe_version"),
        "owner": raw.get("owner"),
        "priority": raw.get("priority"),
    }
    ph = content_hash(payload)
    status = normalize_status(raw.get("status"), tier=str(raw.get("tier") or ""))
    depends = payload["depends_on"]
    if isinstance(depends, str):
        depends = [depends]
    if not isinstance(depends, list):
        depends = []
    acceptance = payload["acceptance"]
    if isinstance(acceptance, str):
        acceptance = [acceptance]
    if not isinstance(acceptance, list):
        acceptance = []

    return {
        "schema": "noos-unified-backlog-item-v1",
        "plan_id": source_id,
        "item_id": item_id,
        "source_revision": source_revision,
        "title": str(payload["title"]),
        "status": status,
        "lane": str(raw.get("lane") or raw.get("track") or source_id),
        "role": map_role(raw),
        "repository": str(raw.get("repository") or "Noetfield-Systems/noetfeld-os"),
        "authority_class": "FOUNDER" if status == "FOUNDER_BLOCKED" else str(raw.get("tier") or "T2"),
        "acceptance_checks": [str(x) for x in acceptance],
        "budget_usd": float(raw.get("budget_usd") or 0.25),
        "value_class": map_value_class(raw),
        "depends_on": [str(x) for x in depends],
        "runway_id": raw.get("runway_id"),
        "recipe_id": raw.get("recipe_id"),
        "recipe_version": raw.get("recipe_version"),
        "content_hash": ph,
        "op_key": op_key(
            source_id=source_id,
            item_id=item_id,
            source_revision=source_revision,
            payload_hash=ph,
        ),
        "source_ref": {
            "source_id": source_id,
            "raw_id": item_id,
            "priority": raw.get("priority"),
            "owner": raw.get("owner"),
        },
    }


def compile_backlog(*, write: bool = True) -> dict[str, Any]:
    config = load_json(CONFIG)
    items: list[dict[str, Any]] = []
    sources_read: list[dict[str, Any]] = []
    for adapter in config.get("source_adapters") or []:
        path = ROOT / str(adapter["path"])
        optional = bool(adapter.get("optional"))
        if not path.is_file():
            sources_read.append({"source_id": adapter["source_id"], "ok": False, "missing": True, "optional": optional})
            if optional:
                continue
            sources_read[-1]["error"] = "required_source_missing"
            continue
        doc = load_json(path)
        revision = str(doc.get("version") or doc.get("updated_at") or content_hash(doc)[:12])
        raw_items = extract_items(doc, str(adapter.get("items_key") or "items"))
        for i, raw in enumerate(raw_items):
            items.append(
                normalize_item(
                    source_id=str(adapter["source_id"]),
                    source_revision=revision,
                    raw=raw,
                    index=i,
                )
            )
        sources_read.append(
            {
                "source_id": adapter["source_id"],
                "ok": True,
                "path": str(adapter["path"]),
                "count": len(raw_items),
                "source_revision": revision,
            }
        )

    # Deduplicate by (source_id, item_id) preferring higher content_hash stability / first wins
    by_identity: dict[str, dict[str, Any]] = {}
    aliases_collapsed = 0
    for item in items:
        key = f"{item['plan_id']}::{item['item_id']}"
        if key in by_identity:
            aliases_collapsed += 1
            continue
        by_identity[key] = item
    # Cross-source content-hash alias collapse
    by_hash: dict[str, str] = {}
    unified: list[dict[str, Any]] = []
    for item in by_identity.values():
        ch = item["content_hash"]
        if ch in by_hash:
            aliases_collapsed += 1
            item = {**item, "alias_of": by_hash[ch], "status": "COMPLETE" if item["status"] == "COMPLETE" else item["status"]}
            # keep as pointer only when not terminal
            if item["status"] != "COMPLETE":
                continue
        else:
            by_hash[ch] = item["op_key"]
        unified.append(item)

    # Preserve runtime CAS state (DISPATCHED/COMPLETE/job_id) across recompiles.
    out_path = ROOT / str(config.get("runtime_queue_path") or ".noos-runtime/plan-completion/backlog-v1.json")
    prior_by_op: dict[str, dict[str, Any]] = {}
    if out_path.is_file():
        try:
            prior = load_json(out_path)
            for pitem in prior.get("items") or []:
                if isinstance(pitem, dict) and pitem.get("op_key"):
                    prior_by_op[str(pitem["op_key"])] = pitem
        except (OSError, json.JSONDecodeError, TypeError):
            prior_by_op = {}
    for item in unified:
        prior = prior_by_op.get(item["op_key"])
        if not prior:
            continue
        prior_status = str(prior.get("status") or "")
        # Never revive COMPLETE; never drop in-flight DISPATCHED back to READY.
        if prior_status == "COMPLETE":
            item["status"] = "COMPLETE"
            item["job_id"] = prior.get("job_id")
            item["completed_at"] = prior.get("completed_at")
            item["dispatched_at"] = prior.get("dispatched_at")
            item["fencing_token"] = prior.get("fencing_token") or item.get("fencing_token") or 1
        elif prior_status == "DISPATCHED" and item["status"] == "READY":
            item["status"] = "DISPATCHED"
            item["job_id"] = prior.get("job_id")
            item["dispatched_at"] = prior.get("dispatched_at")
            item["concurrency_key"] = prior.get("concurrency_key")
            item["fencing_token"] = prior.get("fencing_token") or item.get("fencing_token") or 1

    # Dependency readiness: FOUNDER_BLOCKED never READY for dispatch
    id_to_status = {i["item_id"]: i["status"] for i in unified}
    for item in unified:
        if item["status"] != "READY":
            continue
        deps = item.get("depends_on") or []
        # deps that exist and are not COMPLETE block readiness
        blocking = [d for d in deps if d in id_to_status and id_to_status[d] not in {"COMPLETE", "FOUNDER_BLOCKED"}]
        if blocking:
            item["status"] = "BLOCKED_WITH_REASON"
            item["blocker_reason"] = f"unmet_deps:{','.join(blocking)}"

    counts = {
        "READY": 0,
        "DISPATCHED": 0,
        "COMPLETE": 0,
        "BLOCKED_WITH_REASON": 0,
        "FOUNDER_BLOCKED": 0,
    }
    for item in unified:
        counts[item["status"]] = counts.get(item["status"], 0) + 1

    idle = counts.get("READY", 0) == 0 and counts.get("DISPATCHED", 0) == 0
    row = {
        "schema": "noos-unified-backlog-v1",
        "version": "1.0.0",
        "compiled_at": utc_now(),
        "canon_version": config.get("canon_version"),
        "sources": sources_read,
        "items": sorted(unified, key=lambda x: (x["plan_id"], x["item_id"])),
        "counts": counts,
        "aliases_collapsed": aliases_collapsed,
        "idle_no_work": idle,
        "ok": all(s.get("ok") or s.get("optional") for s in sources_read),
        "report_line": (
            f"unified_backlog · total={len(unified)} ready={counts.get('READY', 0)} "
            f"complete={counts.get('COMPLETE', 0)} founder_blocked={counts.get('FOUNDER_BLOCKED', 0)} "
            f"blocked={counts.get('BLOCKED_WITH_REASON', 0)} aliases={aliases_collapsed} "
            f"idle={idle}"
        ),
    }
    if write:
        save_json(out_path, row)
        row["receipt_path"] = str(out_path.relative_to(ROOT))
        proof = ROOT / "receipts/proof" / f"noos-unified-backlog-compile-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
        proof.parent.mkdir(parents=True, exist_ok=True)
        proof.write_text(json.dumps({k: v for k, v in row.items() if k != "items"}, indent=2) + "\n", encoding="utf-8")
        # also write compact items sidecar
        (proof.parent / proof.name.replace(".json", "-items.json")).write_text(
            json.dumps({"schema": "noos-unified-backlog-items-v1", "items": row["items"]}, indent=2) + "\n",
            encoding="utf-8",
        )
        row["proof_path"] = str(proof.relative_to(ROOT))
        try:
            import noos_plan_completion_supabase_sink_v1 as sink  # noqa: PLC0415

            row["supabase_sink"] = sink.sync_compile(row["items"])
        except Exception as exc:  # noqa: BLE001 — sink must never fail compile
            row["supabase_sink"] = {"ok": False, "error": str(exc)[:240]}
    return row


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--json", action="store_true")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args(argv)
    row = compile_backlog(write=not args.dry_run)
    print(json.dumps(row if args.json else {"report_line": row["report_line"], "counts": row["counts"], "ok": row["ok"]}, indent=2))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
