#!/usr/bin/env python3
"""Render sprint-grade 10-step upgrade plan per plane (NOOS-AGENT-20260702-029)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLANES_PATH = ROOT / "data/noos-upgrade-planes-v1.json"

PLANE_ORDER = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "GOV"]


def load_planes_doc() -> dict:
    return json.loads(PLANES_PATH.read_text())


def plane_by_id(doc: dict, plane_id: str) -> dict | None:
    pid = plane_id.upper()
    for p in doc.get("planes", []):
        if p["id"].upper() == pid:
            return p
    return None


def first_open_step(steps: list[dict]) -> dict | None:
    for s in steps:
        if s.get("status") != "done":
            return s
    return None


def open_steps(steps: list[dict]) -> list[dict]:
    started = False
    out: list[dict] = []
    for s in steps:
        if s.get("status") != "done":
            started = True
        if started and s.get("status") != "done":
            out.append(s)
    return out


def kaizen_note(plane: dict, next_step: dict | None) -> str | None:
    if not next_step:
        return None
    pid = plane["id"]
    sid = next_step.get("id", "")
    if pid == "GOV" and sid in ("G9", "G10"):
        return f"Kaizen: {sid} — machine_safe determinism fix (governed-autorun L13 / D1–D8)."
    if pid == "H" and next_step.get("status") == "open":
        return "Kaizen: L11 ROI — one scaler/throttle change per cycle max."
    return None


def mermaid_ladder(plane: dict) -> str:
    steps = plane.get("steps", [])
    lines = ["```mermaid", "flowchart LR"]
    nodes = []
    for s in steps:
        sid = s["id"].replace("-", "_")
        label = f"{s['id']}"
        nodes.append((sid, label))
        lines.append(f"  {sid}[{label}]")
    for i in range(len(nodes) - 1):
        lines.append(f"  {nodes[i][0]} --> {nodes[i + 1][0]}")
    lines.append("```")
    return "\n".join(lines)


def step_table_markdown(plane: dict) -> str:
    rows = [
        "| Step | ID | Priority | Status | Action | Success check | Verify | Backlog |",
        "|------|-----|----------|--------|--------|---------------|--------|---------|",
    ]
    for s in plane.get("steps", []):
        backlog = ", ".join(s.get("backlog_ids", [])) or "—"
        verify = s.get("verify_cmd", "—")
        rows.append(
            f"| {s['step']} | {s['id']} | {s.get('priority', '—')} | {s.get('status', '—')} "
            f"| {s.get('action', '—')} | {s.get('success_check', '—')} | `{verify}` | {backlog} |"
        )
    return "\n".join(rows)


def build_plane_plan(plane: dict) -> dict:
    steps = plane.get("steps", [])
    done = sum(1 for s in steps if s.get("status") == "done")
    nxt = first_open_step(steps)
    remaining = open_steps(steps)
    return {
        "id": plane["id"],
        "name": plane["name"],
        "tier": plane.get("tier"),
        "win_condition": plane.get("win_condition"),
        "depends_on": plane.get("depends_on", []),
        "verify_cmd": plane.get("verify_cmd"),
        "key_files": plane.get("key_files", []),
        "progress": f"{done}/{len(steps)}",
        "current_step": plane.get("current_step"),
        "next_step": nxt,
        "start_order": [s["id"] for s in remaining],
        "kaizen_note": kaizen_note(plane, nxt),
        "steps": steps,
        "closeout": done == len(steps),
    }


def render_plane_human(plan: dict) -> str:
    lines = [
        f"# Plane {plan['id']} — {plan['name']}",
        "",
        f"**Tier:** {plan['tier']} · **Progress:** {plan['progress']}",
        f"**Win condition:** {plan['win_condition']}",
        f"**Verify:** `{plan['verify_cmd']}`",
    ]
    if plan["depends_on"]:
        lines.append(f"**Depends on:** {', '.join(plan['depends_on'])}")
    if plan["closeout"]:
        lines.append("")
        lines.append("**Status:** CLOSED — do not re-open unless L12 drift.")
    lines.extend(["", "## Step ladder", ""])
    if plan.get("next_step"):
        nxt = plan["next_step"]
        lines.append(f"**Next:** {nxt['id']} ({nxt['status']}) — {nxt.get('action', '')}")
    if plan.get("start_order"):
        lines.append(f"**Start order:** {' → '.join(plan['start_order'])}")
    if plan.get("kaizen_note"):
        lines.append(f"**{plan['kaizen_note']}**")
    lines.extend(["", step_table_markdown({"steps": plan["steps"]}), ""])
    if plan.get("key_files"):
        lines.append("**Key files:** " + ", ".join(f"`{f}`" for f in plan["key_files"]))
    return "\n".join(lines)


def render_plane_markdown_section(plane: dict) -> str:
    plan = build_plane_plan(plane)
    lines = [
        f"## Plane {plan['id']} — {plan['name']} (10 steps)",
        "",
        f"**Win condition:** {plan['win_condition']}",
        f"**Tier:** {plan['tier']} · **Progress:** {plan['progress']} · **Verify:** `{plan['verify_cmd']}`",
    ]
    if plan["depends_on"]:
        lines.append(f"**Depends on planes:** {', '.join(plan['depends_on'])}")
    if plan["closeout"]:
        lines.append("")
        lines.append("> CLOSED — evidence on disk. Do not re-open unless L12 drift.")
    lines.extend(["", mermaid_ladder(plane), ""])
    if plan.get("start_order"):
        lines.append(f"**Start order (open steps):** {' → '.join(plan['start_order'])}")
    if plan.get("kaizen_note"):
        lines.append(f"**{plan['kaizen_note']}**")
    lines.extend(["", "<!-- GENERATED: sync from plane_plan_v1.py -->", "", step_table_markdown(plane), ""])
    if plan.get("key_files"):
        lines.append("**Key files:** " + ", ".join(f"`{f}`" for f in plan["key_files"]))
    lines.append("")
    return "\n".join(lines)


def render_all_markdown(doc: dict) -> str:
    lines = ["<!-- GENERATED BODY: ten plane sections -->", ""]
    planes_map = {p["id"]: p for p in doc.get("planes", [])}
    for pid in PLANE_ORDER:
        if pid in planes_map:
            lines.append(render_plane_markdown_section(planes_map[pid]))
    return "\n".join(lines)


def render_list(doc: dict) -> str:
    lines = ["Plane  Progress  Tier   Next"]
    planes_map = {p["id"]: p for p in doc.get("planes", [])}
    for pid in PLANE_ORDER:
        p = planes_map.get(pid)
        if not p:
            continue
        plan = build_plane_plan(p)
        nxt = plan.get("next_step") or {}
        nxt_id = nxt.get("id", "COMPLETE")
        lines.append(f"{pid:4}   {plan['progress']:7}  {plan['tier']:4}   {nxt_id}")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="10-step upgrade plan renderer")
    parser.add_argument("--plane", help="Plane id (A, B, … GOV)")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--markdown", action="store_true", help="Markdown output")
    parser.add_argument("--all", action="store_true", help="All planes (with --markdown)")
    parser.add_argument("--list", action="store_true", help="List planes progress")
    args = parser.parse_args()

    doc = load_planes_doc()

    if args.list:
        print(render_list(doc))
        return 0

    if args.all and args.markdown:
        print(render_all_markdown(doc))
        return 0

    if not args.plane:
        parser.error("Specify --plane ID, --list, or --all --markdown")

    plane = plane_by_id(doc, args.plane)
    if not plane:
        print(f"Unknown plane: {args.plane}", file=sys.stderr)
        return 1

    plan = build_plane_plan(plane)

    if args.json:
        print(json.dumps(plan, indent=2))
    elif args.markdown:
        print(render_plane_markdown_section(plane))
    else:
        print(render_plane_human(plan))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
