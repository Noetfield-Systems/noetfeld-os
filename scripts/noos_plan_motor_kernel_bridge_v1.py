#!/usr/bin/env python3
"""Bridge plan-motor roles to the governed worker kernel (DeepSeek T1/T2 routing)."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from noos_worker_kernel_v1 import run_task  # noqa: E402


def kernel_classify(*, text: str, labels: list[str] | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {"text": text, "labels": labels or []}
    return run_task(task_kind="classify", payload=payload, dry_run=False)


def kernel_summarize(*, text: str) -> dict[str, Any]:
    return run_task(task_kind="summarize", payload={"text": text}, dry_run=False)


def kernel_patch_proposal(*, patch: dict[str, Any], title: str = "") -> dict[str, Any]:
    body = {"title": title, "patch": patch}
    return run_task(task_kind="patch_proposal", payload=body, dry_run=False)


def kernel_triage_finding(finding: dict[str, Any]) -> dict[str, Any]:
    text = json.dumps(
        {
            "finding_id": finding.get("id"),
            "severity": finding.get("severity"),
            "metadata": finding.get("metadata"),
        },
        sort_keys=True,
    )
    return kernel_classify(text=text, labels=["systematic", "integration", "unknown", "founder_gate"])


def kernel_proposal_review(proposal: dict[str, Any]) -> dict[str, Any]:
    return kernel_patch_proposal(
        patch={
            "files": [],
            "description": json.dumps(proposal.get("proposed_changes") or {}, sort_keys=True)[:4000],
            "risk_level": proposal.get("risk_level"),
            "fix_type": proposal.get("fix_type"),
        },
        title=str(proposal.get("proposal_id") or "specialist_proposal"),
    )
