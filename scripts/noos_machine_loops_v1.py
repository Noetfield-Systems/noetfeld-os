#!/usr/bin/env python3
"""NOOS Machine Loops v1 — worker, critic, repair, research, audit, autonomy E2E."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import noos_receipt_chain_v1 as chain  # noqa: E402
from noos_observability_semantics_v1 import summarize_pending  # noqa: E402

CONFIG_PATH = ROOT / "data/noos-machine-loops-config-v1.json"
LEDGER_PATH = ROOT / "data/founder-trigger-ledger-v1.json"
TEMPLATES_DIR = ROOT / ".agent-policy/dispatch-templates"
PROOF_DIR = ROOT / "receipts/proof"
RUNTIME_DIR = ROOT / ".noos-runtime/machine-loops"

VERIFIER_PATH_PREFIXES = (
    "scripts/verify_",
    "noetfield_gate/",
    "data/noos-parallel-agent-registry-v1.json",
    "data/trigger-registry-v1.json",
    "docs/GOVERNED_AUTORUN_LAWS",
    ".agent-policy/",
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")


def render_template(template: dict[str, Any], params: dict[str, Any]) -> dict[str, Any]:
    raw = json.dumps(template)

    def repl(match: re.Match[str]) -> str:
        key = match.group(1)
        val = params.get(key, "")
        if isinstance(val, (list, dict)):
            return json.dumps(val)
        return str(val)

    rendered = re.sub(r"\{\{(\w+)\}\}", repl, raw)
    out = json.loads(rendered)
    out["instantiated_at"] = utc_now()
    out["params"] = params
    return out


def git_changed_files(base: str = "HEAD~1") -> list[str]:
    try:
        out = subprocess.check_output(
            ["git", "diff", "--name-only", base, "HEAD"],
            cwd=ROOT,
            text=True,
            stderr=subprocess.DEVNULL,
        )
        return [line.strip() for line in out.splitlines() if line.strip()]
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []


def classify_merge_tier(files: list[str], config: dict[str, Any]) -> str:
    if any(p.startswith(VERIFIER_PATH_PREFIXES) or "GOVERNED_AUTORUN" in p for p in files):
        return "T3"
    if any(p.startswith(".github/") or p.endswith((".yml", ".yaml")) for p in files):
        return "T2"
    if any(p.startswith(("requirements", "pyproject", "package")) for p in files):
        return "T2"
    if all(
        p.startswith(("docs/", "tests/", "receipts/", "noetfield-org/"))
        or p.endswith((".md", ".json"))
        for p in files
    ):
        return "T0"
    return "T1"


def run_critic(*, receipt: dict[str, Any], diff_files: list[str] | None = None) -> dict[str, Any]:
    findings: list[dict[str, str]] = []
    report = str(receipt.get("report_line") or receipt.get("summary") or "")
    schema = receipt.get("schema")

    if report and not schema:
        findings.append({"check": "prose_as_proof", "detail": "report_line without schema"})

    if receipt.get("ok") is True and receipt.get("self_verified") is True:
        findings.append({"check": "self_verification", "detail": "receipt claims self_verified"})

    if isinstance(receipt.get("summary"), str) and isinstance(receipt.get("ok"), bool):
        if ("pass" in receipt["summary"].lower()) != receipt["ok"]:
            findings.append({"check": "report_vs_json", "detail": "summary contradicts ok flag"})

    prose_markers = ("should work", "config live", "expected lag", "looks good")
    blob = json.dumps(receipt).lower()
    for marker in prose_markers:
        if marker in blob:
            findings.append({"check": "prose_as_proof", "detail": marker})

    for fp in diff_files or []:
        if fp.startswith(VERIFIER_PATH_PREFIXES) or fp.startswith("scripts/verify_"):
            findings.append({"check": "verifier_edit", "detail": fp})

    started = receipt.get("started_at") or receipt.get("written_at")
    finished = receipt.get("finished_at") or receipt.get("written_at")
    if started and finished:
        try:
            s = datetime.fromisoformat(str(started).replace("Z", "+00:00"))
            f = datetime.fromisoformat(str(finished).replace("Z", "+00:00"))
            if (f - s).total_seconds() < 0:
                findings.append({"check": "timestamp_math", "detail": "finished before started"})
        except ValueError:
            findings.append({"check": "timestamp_math", "detail": "unparseable timestamps"})

    if receipt.get("cost") is None and receipt.get("tokens_in") is None and receipt.get("mode"):
        findings.append({"check": "cost_sanity", "detail": "work receipt missing cost metering"})

    verdict = "APPROVE"
    if any(f["check"] == "verifier_edit" for f in findings):
        verdict = "REJECT"
    elif findings:
        uncertain_checks = {"prose_as_proof", "cost_sanity", "self_verification"}
        if all(f["check"] in uncertain_checks for f in findings):
            verdict = "UNCERTAIN"
        else:
            verdict = "REJECT"

    return {
        "schema": "noos-machine-critic-receipt-v1",
        "version": "1.0.0",
        "at": utc_now(),
        "target_schema": schema,
        "verdict": verdict,
        "findings": findings,
        "diff_files": diff_files or [],
        "ok": verdict == "APPROVE",
        "report_line": f"critic_{verdict.lower()} · findings={len(findings)}",
    }


def derive_repair_paths(failure_receipt: dict[str, Any]) -> list[str]:
    paths: set[str] = set()
    for key in ("files_changed", "allowed_paths", "scope_files"):
        val = failure_receipt.get(key)
        if isinstance(val, list):
            paths.update(str(x) for x in val if x)
    result = failure_receipt.get("result")
    if isinstance(result, dict):
        for key in ("failing_tests", "paths"):
            val = result.get(key)
            if isinstance(val, list):
                paths.update(str(x) for x in val if x)
    err = str(failure_receipt.get("error") or failure_receipt.get("blocker_reason") or "")
    for match in re.findall(r"tests/[\w./_-]+\.py", err):
        paths.add(match)
    return sorted(paths)


def build_repair_dispatch(failure_receipt: dict[str, Any], *, attempt: int = 1) -> dict[str, Any]:
    template = load_json(TEMPLATES_DIR / "repair-lane-v1.json")
    task_id = str(failure_receipt.get("task_id") or failure_receipt.get("op_key") or "UNKNOWN")
    derived = derive_repair_paths(failure_receipt)
    return {
        **template,
        "schema": "noos-machine-repair-dispatch-v1",
        "instantiated_at": utc_now(),
        "params": {
            "task_id": task_id,
            "attempt": attempt,
            "failure_receipt": failure_receipt.get("receipt_path") or failure_receipt.get("schema"),
            "derived_paths": derived,
        },
        "allowed_paths": derived,
        "ok": True,
    }


def build_research_memo(*, question: str, source_receipt: dict[str, Any] | None = None) -> dict[str, Any]:
    findings: list[dict[str, str]] = []
    sources: list[str] = ["docs/GOVERNED_AUTORUN_LAWS_v3.md", "data/noos-machine-loops-config-v1.json"]
    if source_receipt:
        findings.append(
            {
                "point": "Source receipt schema and status",
                "detail": f"{source_receipt.get('schema')} ok={source_receipt.get('ok')}",
            }
        )
        if source_receipt.get("receipt_path"):
            sources.append(str(source_receipt["receipt_path"]))

    recommendation = "Route to repair lane with machine-narrowed scope; escalate to outside audit if second repair fails."
    confidence = 0.8 if source_receipt and source_receipt.get("schema") else 0.55
    blast = "T1" if confidence >= 0.75 else "T2"

    return {
        "schema": "noos-research-memo-v1",
        "version": "1.0.0",
        "at": utc_now(),
        "question": question,
        "findings": findings,
        "sources": sources,
        "options": [
            {"id": "A", "action": "repair_lane", "blast_radius": "T1"},
            {"id": "B", "action": "outside_audit", "blast_radius": "T1"},
            {"id": "C", "action": "founder_gated_with_memo", "blast_radius": "T3"},
        ],
        "recommendation": recommendation,
        "confidence": confidence,
        "blast_radius_class": blast,
        "machine_apply": confidence >= 0.75 and blast in {"T0", "T1"},
        "report_line": f"research_memo · confidence={confidence} blast={blast}",
    }


def consume_dispatch_queue(
    pending: list[dict[str, Any]],
    processed: list[dict[str, Any]],
    *,
    max_items: int = 1,
) -> dict[str, Any]:
    """Bridge actionable queue rows to Runway role intake (no local LLM execution)."""
    try:
        import noos_role_runway_dispatch_v1 as role_dispatch
        import noos_plan_completion_dispatch_v1 as plan_dispatch
    except ImportError as exc:
        return {"ok": False, "error": str(exc), "consumed": 0}

    consumed: list[dict[str, Any]] = []
    remaining: list[dict[str, Any]] = []
    for item in pending:
        if len(consumed) >= max_items:
            remaining.append(item)
            continue
        schema = str(item.get("schema") or "")
        role = None
        subject = str(item.get("task_id") or item.get("target_schema") or item.get("action") or "reconcile")
        if schema == "noos-machine-repair-dispatch-v1":
            role = "self_heal"
        elif schema == "noos-research-memo-v1":
            role = "research"
        elif schema == "noos-machine-reconcile-event-v1":
            role = "incident_diagnose"
        else:
            remaining.append(item)
            continue
        artifact = role_dispatch.dispatch_role(role, subject=subject, context={"source_schema": schema})
        processed.append(
            {
                "at": utc_now(),
                "schema": schema,
                "role": role,
                "subject": subject,
                "dispatch_ok": bool(artifact.get("ok")),
                "receipt_path": artifact.get("receipt_path"),
                "job_id": (artifact.get("ack") or {}).get("job_id"),
            }
        )
        consumed.append(artifact)

    plan = plan_dispatch.reconcile_and_dispatch(write=True)
    return {
        "ok": True,
        "consumed": len(consumed),
        "remaining": len(remaining),
        "artifacts": consumed,
        "plan_completion": {
            "ok": plan.get("ok"),
            "verdict": (plan.get("dispatch") or {}).get("verdict"),
            "report_line": plan.get("report_line"),
        },
        "pending_out": remaining,
    }


def reconcile_queue(*, write: bool = True, consume: bool = True) -> dict[str, Any]:
    config = load_json(CONFIG_PATH)
    queue_path = ROOT / config["dispatch_queue_path"]
    queue = load_json(queue_path) if queue_path.is_file() else {"pending": [], "processed": []}

    pending: list[dict[str, Any]] = list(queue.get("pending") or [])
    processed: list[dict[str, Any]] = list(queue.get("processed") or [])
    new_dispatches: list[dict[str, Any]] = []

    for fp in sorted(PROOF_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime)[-50:]:
        try:
            receipt = json.loads(fp.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        status = str(receipt.get("status") or "")
        schema = str(receipt.get("schema") or "")
        if receipt.get("ok") is False or status in {"FAILED_WITH_RECEIPT", "BLOCKED_WITH_REASON"}:
            dispatch = build_repair_dispatch(receipt)
            try:
                dispatch["source_receipt_path"] = str(fp.relative_to(ROOT))
            except ValueError:
                dispatch["source_receipt_path"] = str(fp)
            new_dispatches.append(dispatch)
        if schema == "noos-machine-critic-receipt-v1" and receipt.get("verdict") == "REJECT":
            src = receipt.get("target_schema")
            new_dispatches.append(
                {
                    "schema": "noos-machine-reconcile-event-v1",
                    "at": utc_now(),
                    "action": "file_repair_from_critic",
                    "target_schema": src,
                }
            )
        if schema == "noos-machine-critic-receipt-v1" and receipt.get("verdict") == "UNCERTAIN":
            memo = build_research_memo(question=f"Uncertain critic verdict on {receipt.get('target_schema')}", source_receipt=receipt)
            new_dispatches.append(memo)

    dedup_count = 0
    existing_keys = {json.dumps(x, sort_keys=True) for x in pending}
    for d in new_dispatches:
        key = json.dumps(d, sort_keys=True)
        if key not in existing_keys:
            pending.append(d)
            existing_keys.add(key)
        else:
            dedup_count += 1

    consumer: dict[str, Any] = {"ok": True, "consumed": 0, "skipped": True}
    if consume:
        consumer = consume_dispatch_queue(pending, processed, max_items=1)
        pending = list(consumer.get("pending_out") or pending)

    now_ts = datetime.now(timezone.utc).timestamp()
    orphan_days = float(config.get("orphan_backlog_age_days") or 3.0)
    breakdown = summarize_pending(
        pending,
        new_dispatches=len(new_dispatches),
        now_ts=now_ts,
        orphan_age_days=orphan_days,
        dedup_count=dedup_count,
    )
    counts = breakdown["counts"]

    row = {
        "schema": "noos-machine-dispatch-queue-v1",
        "updated_at": utc_now(),
        "pending": pending,
        "processed": processed[-200:],
        "new_this_run": len(new_dispatches),
        "consumer": {
            "consumed": consumer.get("consumed"),
            "plan_completion": consumer.get("plan_completion"),
            "ok": consumer.get("ok"),
        },
        # Explicit reconciler reporting: distinguish genuinely actionable work
        # from orphaned/historical backlog and other non-actionable buckets so
        # ``pending=N`` is never mistaken for N live items needing dispatch.
        "queue_breakdown": counts,
        "queue_items_classified": breakdown["items"],
        "ok": True,
        "report_line": (
            f"reconcile · pending={len(pending)} new={len(new_dispatches)} "
            f"consumed={consumer.get('consumed', 0)} "
            f"actionable={counts['actionable_pending']} orphaned={counts['orphaned_backlog']} "
            f"dedup={counts['deduplicated']} leases={counts['active_leases']} "
            f"backoff={counts['backoff_pending']} unknown={counts['unknown']}"
        ),
    }
    if write:
        save_json(queue_path, row)
    return row


def run_outside_audit(*, trailing_hours: int = 168) -> dict[str, Any]:
    config = load_json(CONFIG_PATH)
    hours = trailing_hours or int(config.get("audit_trailing_hours") or 168)
    cutoff = datetime.now(timezone.utc).timestamp() - hours * 3600

    scanned: list[dict[str, Any]] = []
    kaizen_candidates: list[dict[str, Any]] = []
    for fp in PROOF_DIR.glob("*.json"):
        try:
            if fp.stat().st_mtime < cutoff:
                continue
            row = json.loads(fp.read_text(encoding="utf-8"))
            scanned.append(row)
        except (OSError, json.JSONDecodeError):
            continue

    chain_row = chain.verify_chain_operational(scanned)
    if not chain_row["ok"]:
        kaizen_candidates.append(
            {
                "class": "machine_safe",
                "title": "Receipt chain integrity repair",
                "expected_roi": "risk_reduced",
                "source": "outside_audit",
            }
        )

    critic_failures = [
        r for r in scanned if r.get("schema") == "noos-machine-critic-receipt-v1" and r.get("verdict") != "APPROVE"
    ]
    for cf in critic_failures[:5]:
        kaizen_candidates.append(
            {
                "class": "machine_safe",
                "title": f"Address critic finding on {cf.get('target_schema')}",
                "expected_roi": "hygiene",
                "source": "outside_audit",
            }
        )

    spot_urls: list[str] = []
    for row in scanned:
        if isinstance(row.get("urls"), list):
            spot_urls.extend(str(u) for u in row["urls"][:1])
    spot_urls = spot_urls[: int(config.get("audit_spot_fetch_count") or 3)]

    fetched: list[dict[str, Any]] = []
    for url in spot_urls:
        if not url.startswith("https://"):
            continue
        try:
            proc = subprocess.run(
                ["curl", "-fsSIL", url],
                capture_output=True,
                text=True,
                timeout=15,
                check=False,
            )
            fetched.append({"url": url, "ok": proc.returncode == 0, "status_line": (proc.stdout or "").splitlines()[:1]})
        except (subprocess.TimeoutExpired, FileNotFoundError):
            fetched.append({"url": url, "ok": False, "status_line": ["timeout"]})

    receipt = {
        "schema": "noos-outside-audit-receipt-v1",
        "version": "1.0.0",
        "at": utc_now(),
        "trailing_hours": hours,
        "receipts_scanned": len(scanned),
        "chain": chain_row,
        "critic_non_approve": len(critic_failures),
        "spot_fetches": fetched,
        "kaizen_candidates": kaizen_candidates,
        "ok": chain_row["ok"],
        "report_line": f"outside_audit · scanned={len(scanned)} chain_ok={chain_row['ok']}",
    }
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = PROOF_DIR / f"noos-outside-audit-{ts}.json"
    PROOF_DIR.mkdir(parents=True, exist_ok=True)
    sealed = chain.seal_receipt(receipt, prev_hash=chain_row.get("tail_hash"))
    out.write_text(json.dumps(sealed, indent=2) + "\n", encoding="utf-8")
    sealed["receipt_path"] = str(out.relative_to(ROOT))
    return sealed


def validate_merge(*, base: str = "HEAD~1") -> dict[str, Any]:
    config = load_json(CONFIG_PATH)
    files = git_changed_files(base)
    tier = classify_merge_tier(files, config)
    tier_cfg = (config.get("merge_tiers") or {}).get(tier, {})

    ci_ok = True
    try:
        proc = subprocess.run([sys.executable, "-m", "pytest", "-q"], cwd=ROOT, capture_output=True, text=True, check=False)
        ci_ok = proc.returncode == 0
    except FileNotFoundError:
        ci_ok = False

    gov_ok = False
    try:
        proc = subprocess.run(
            [sys.executable, "scripts/verify_living_system_governance_v1.py", "--json"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        if proc.returncode == 0:
            row = json.loads(proc.stdout)
            gov_ok = bool(row.get("ok"))
    except (json.JSONDecodeError, FileNotFoundError):
        gov_ok = False

    critic = run_critic(receipt={"schema": "noos-merge-validation-v1", "ok": ci_ok and gov_ok, "files_changed": files}, diff_files=files)
    second_critic_ok = True
    if tier_cfg.get("requires_second_critic"):
        second = run_critic(receipt={"schema": "noos-merge-validation-v1", "ok": critic["ok"], "files_changed": files, "pass": "second"}, diff_files=files)
        second_critic_ok = second["verdict"] == "APPROVE"

    machine_merge_allowed = bool(tier_cfg.get("machine_merge")) and tier != "T3"
    all_ok = ci_ok and gov_ok and critic["verdict"] == "APPROVE" and second_critic_ok

    return {
        "schema": "noos-machine-merge-validation-v1",
        "version": "1.0.0",
        "at": utc_now(),
        "tier": tier,
        "files": files,
        "checks": {
            "ci_ok": ci_ok,
            "governance_ok": gov_ok,
            "critic_verdict": critic["verdict"],
            "second_critic_ok": second_critic_ok,
            "machine_merge_allowed": machine_merge_allowed,
        },
        "ok": all_ok and (machine_merge_allowed or tier == "T3"),
        "merge_authority": "machine" if all_ok and machine_merge_allowed else "founder",
        "report_line": f"merge_validation · tier={tier} authority={'machine' if all_ok and machine_merge_allowed else 'founder'}",
    }


def record_shadow_decision(*, trigger_id: str, machine_recommendation: str, founder_decision: str) -> dict[str, Any]:
    ledger = load_json(LEDGER_PATH)
    config = load_json(CONFIG_PATH)
    shadow_path = ROOT / config["shadow_decisions_path"]
    shadow = load_json(shadow_path) if shadow_path.is_file() else {"events": []}

    match = machine_recommendation.strip().lower() == founder_decision.strip().lower()
    event = {
        "at": utc_now(),
        "trigger_id": trigger_id,
        "machine_recommendation": machine_recommendation,
        "founder_decision": founder_decision,
        "match": match,
    }
    shadow.setdefault("events", []).append(event)
    save_json(shadow_path, shadow)

    proposals: list[dict[str, Any]] = []
    for trig in ledger.get("triggers") or []:
        if trig.get("trigger_id") != trigger_id:
            continue
        if match:
            trig["evidence_counter"] = int(trig.get("evidence_counter") or 0) + 1
        else:
            trig["evidence_counter"] = 0
            trig["status"] = trig.get("status") or "founder_gated"
        threshold = int(ledger.get("shadow_decision_threshold") or 10)
        if int(trig.get("evidence_counter") or 0) >= threshold and trig.get("target_status"):
            proposals.append(
                {
                    "trigger_id": trigger_id,
                    "proposal": "phase_unlock_autonomy_expand",
                    "target_status": trig["target_status"],
                    "evidence_counter": trig["evidence_counter"],
                    "note": "Founder one-click unlock; ratchet reverts on post-unlock violation",
                }
            )
        if isinstance(trig.get("bootstrap_cycles_remaining"), int) and trig["bootstrap_cycles_remaining"] > 0:
            trig["bootstrap_cycles_remaining"] -= 1
            if trig["bootstrap_cycles_remaining"] == 0:
                trig["status"] = "machine_autonomous_bootstrap_complete"

    ledger["updated_at"] = utc_now()[:10]
    save_json(LEDGER_PATH, ledger)

    return {
        "schema": "noos-shadow-decision-v1",
        "event": event,
        "proposals": proposals,
        "ok": True,
        "report_line": f"shadow_decision · match={match} counter_updated",
    }


def autonomy_status() -> dict[str, Any]:
    ledger = load_json(LEDGER_PATH)
    config = load_json(CONFIG_PATH)
    shadow_path = ROOT / config["shadow_decisions_path"]
    shadow = load_json(shadow_path) if shadow_path.is_file() else {"events": []}
    events = shadow.get("events") or []
    recent_matches = sum(1 for e in events[-20:] if e.get("match"))
    return {
        "schema": "noos-autonomy-status-v1",
        "at": utc_now(),
        "canon_version": config.get("canon_version"),
        "triggers": ledger.get("triggers"),
        "shadow_events": len(events),
        "recent_match_rate": recent_matches / max(len(events[-20:]), 1),
        "dispatch_queue": reconcile_queue(write=False),
        "ok": True,
        "report_line": "autonomy_status · ledger loaded",
    }


def verify_installation() -> dict[str, Any]:
    checks = {
        "config": CONFIG_PATH.is_file(),
        "ledger": LEDGER_PATH.is_file(),
        "templates": all(
            (TEMPLATES_DIR / name).is_file()
            for name in (
                "worker-execute-v1.json",
                "repair-lane-v1.json",
                "critic-pass-v1.json",
                "research-memo-v1.json",
            )
        ),
        "proof_dir": PROOF_DIR.is_dir(),
    }
    audit = run_outside_audit(trailing_hours=24)
    checks["outside_audit"] = audit.get("ok")
    row = {
        "schema": "noos-machine-loops-verify-v1",
        "at": utc_now(),
        "checks": checks,
        "ok": all(checks.values()),
        "report_line": "machine_loops_verify · all checks pass" if all(checks.values()) else "machine_loops_verify · drift",
    }
    return row


def cmd_critic(args: argparse.Namespace) -> dict[str, Any]:
    path = Path(args.receipt)
    if not path.is_absolute():
        path = ROOT / path
    return run_critic(receipt=load_json(path), diff_files=git_changed_files())


def cmd_repair_dispatch(args: argparse.Namespace) -> dict[str, Any]:
    path = Path(args.receipt)
    if not path.is_absolute():
        path = ROOT / path
    row = build_repair_dispatch(load_json(path), attempt=args.attempt)
    row["ok"] = True
    return row


def cmd_research_memo(args: argparse.Namespace) -> dict[str, Any]:
    src = None
    if args.receipt:
        path = Path(args.receipt)
        if not path.is_absolute():
            path = ROOT / path
        src = load_json(path)
    row = build_research_memo(question=args.question, source_receipt=src)
    row["ok"] = True
    return row


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--json", action="store_true")
    sub = p.add_subparsers(dest="command", required=True)

    sub.add_parser("status", help="Human/machine loops status digest").set_defaults(func=lambda a: autonomy_status())
    sub.add_parser("reconcile", help="Instantiate dispatches + consume into Runway intake").set_defaults(
        func=lambda a: reconcile_queue(consume=True)
    )
    sub.add_parser("reconcile-enqueue-only", help="Enqueue only (no Runway consume)").set_defaults(
        func=lambda a: reconcile_queue(consume=False)
    )
    sub.add_parser("audit", help="Outside audit over trailing receipts").set_defaults(func=lambda a: run_outside_audit())

    c = sub.add_parser("critic", help="Adversarial critic on receipt file")
    c.add_argument("--receipt", required=True)
    c.set_defaults(func=cmd_critic)

    r = sub.add_parser("repair-dispatch", help="Build repair dispatch from failure receipt")
    r.add_argument("--receipt", required=True)
    r.add_argument("--attempt", type=int, default=1)
    r.set_defaults(func=cmd_repair_dispatch)

    m = sub.add_parser("research-memo", help="Decision memo for uncertainty")
    m.add_argument("--question", required=True)
    m.add_argument("--receipt")
    m.set_defaults(func=cmd_research_memo)

    sub.add_parser("validate-merge", help="Machine merge validation T0–T3").set_defaults(func=lambda a: validate_merge())

    s = sub.add_parser("record-shadow", help="Record shadow decision vs founder")
    s.add_argument("--trigger-id", required=True)
    s.add_argument("--machine", required=True)
    s.add_argument("--founder", required=True)
    s.set_defaults(
        func=lambda a: record_shadow_decision(
            trigger_id=a.trigger_id,
            machine_recommendation=a.machine,
            founder_decision=a.founder,
        )
    )

    sub.add_parser("verify", help="Structural + audit installation verify").set_defaults(func=lambda a: verify_installation())
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    row = args.func(args)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("report_line") or json.dumps(row))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
