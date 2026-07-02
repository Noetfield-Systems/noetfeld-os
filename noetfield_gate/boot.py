"""Local pre-execution gate — 4 disk/runtime checks, PASS or BLOCK."""

from __future__ import annotations

import json
import os
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

def dated_receipt_dir(kind: str) -> Path:
    """UPG-0157 — ~/.noetfield/receipts/YYYY-MM-DD/{kind}/"""
    day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return Path.home() / ".noetfield" / "receipts" / day / kind


DEFAULT_RECEIPT = dated_receipt_dir("gate") / "gate-report-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def resolve_root() -> Path:
    env = os.environ.get("NOETFIELD_ROOT", "").strip()
    if env:
        return Path(env).expanduser().resolve()
    here = Path.cwd().resolve()
    for candidate in (here, *here.parents):
        if (candidate / "base_policy.json").is_file() and (candidate / "run.py").is_file():
            return candidate
    return here


def bundled_policy_dir() -> Path:
    return Path(__file__).resolve().parent / "policies"


def resolve_policy_paths(root: Path, *, use_bundled_fallback: bool) -> tuple[Path, Path, str]:
    base = root / "base_policy.json"
    corridor = root / "corridor_policy.json"
    if base.is_file() and corridor.is_file():
        return base, corridor, "repo"
    if use_bundled_fallback:
        bundled = bundled_policy_dir()
        bundled_base = bundled / "base_policy.json"
        bundled_corridor = bundled / "corridor_policy.json"
        if bundled_base.is_file() and bundled_corridor.is_file():
            return bundled_base, bundled_corridor, "bundled"
    return base, corridor, "missing"


def resolve_db_path(root: Path) -> Path:
    if (root / "run.py").is_file():
        return root / "noetfeld.db"
    return Path.home() / ".noetfield" / "noetfeld.db"


def _check(name: str, cid: str, ok: bool, reason: str, **extra: Any) -> dict[str, Any]:
    row: dict[str, Any] = {"id": cid, "name": name, "ok": ok, "reason": reason}
    row.update(extra)
    return row


def run_gate_checks(
    *,
    root: Path | None = None,
    api_url: str | None = None,
    strict: bool = False,
    include_pytest: bool = False,
) -> dict[str, Any]:
    explicit_root = root is not None
    root = (root or resolve_root()).resolve()
    checks: list[dict[str, Any]] = []

    base_path, corridor_path, policy_source = resolve_policy_paths(
        root,
        use_bundled_fallback=not explicit_root,
    )
    if policy_source == "missing":
        checks.append(
            _check(
                "policy_pack_present",
                "G1",
                False,
                "missing base_policy.json or corridor_policy.json",
                root=str(root),
            )
        )
    elif policy_source == "bundled":
        checks.append(
            _check(
                "policy_pack_present",
                "G1",
                True,
                "bundled default policy pack (pip install)",
                policy_source=policy_source,
            )
        )
    else:
        checks.append(_check("policy_pack_present", "G1", True, "base + corridor policy files found"))

    rule_set_id = ""
    rule_set_version = ""
    try:
        base = json.loads(base_path.read_text(encoding="utf-8"))
        corridor = json.loads(corridor_path.read_text(encoding="utf-8"))
        rule_set_id = str(base.get("rule_set_id") or corridor.get("rule_set_id") or "")
        rule_set_version = str(
            base.get("policy_pack_version") or base.get("rule_set_version") or ""
        )
        valid = bool(rule_set_id) and rule_set_version.count(".") >= 1
        checks.append(
            _check(
                "policy_pack_valid",
                "G2",
                valid,
                "rule_set_id and semver rule_set_version required" if not valid else "policy JSON valid",
                rule_set_id=rule_set_id,
                rule_set_version=rule_set_version,
            )
        )
    except (OSError, json.JSONDecodeError) as exc:
        checks.append(_check("policy_pack_valid", "G2", False, f"policy parse error: {exc}"))

    db_path = resolve_db_path(root)
    try:
        db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(db_path))
        conn.execute("SELECT 1")
        conn.close()
        checks.append(_check("database_writable", "G3", True, f"sqlite ok ({db_path.name})"))
    except sqlite3.Error as exc:
        checks.append(_check("database_writable", "G3", False, f"sqlite error: {exc}"))

    api = (api_url or os.environ.get("NOETFIELD_API_URL", "")).strip().rstrip("/")
    if api:
        try:
            import urllib.error
            import urllib.request

            req = urllib.request.Request(f"{api}/readiness", method="GET")
            with urllib.request.urlopen(req, timeout=10) as resp:
                ok = 200 <= resp.status < 300
            checks.append(
                _check("api_readiness", "G4", ok, f"GET {api}/readiness -> {resp.status}", api_url=api)
            )
        except Exception as exc:
            checks.append(_check("api_readiness", "G4", False, str(exc), api_url=api))
    else:
        checks.append(
            _check(
                "api_readiness",
                "G4",
                True,
                "skipped — set NOETFIELD_API_URL or --api-url to probe remote runtime",
                skipped=True,
            )
        )

    if policy_source == "bundled" or not (root / "run.py").is_file():
        checks.append(
            _check(
                "policy_registry",
                "G5",
                True,
                "skipped — portable gate (full PolicyRegistry requires noetfeld-os checkout)",
                skipped=True,
            )
        )
    else:
        if str(root) not in sys.path:
            sys.path.insert(0, str(root))
        try:
            from policy_meta import build_policy_meta

            meta = build_policy_meta(base_path=base_path, corridor_path=corridor_path)
            checks.append(
                _check(
                    "policy_registry",
                    "G5",
                    True,
                    "PolicyRegistry loaded",
                    combined_hash=meta.combined_hash,
                )
            )
        except Exception as exc:
            checks.append(_check("policy_registry", "G5", False, f"PolicyRegistry: {exc}"))

    if include_pytest and (root / "run.py").is_file():
        import subprocess

        try:
            proc = subprocess.run(
                [sys.executable, "-m", "pytest", "-q", "--tb=no"],
                cwd=str(root),
                capture_output=True,
                text=True,
                timeout=180,
            )
            ok = proc.returncode == 0
            tail = (proc.stdout or proc.stderr or "").strip().splitlines()[-1:] or [""]
            checks.append(
                _check(
                    "pytest_suite",
                    "G6",
                    ok,
                    tail[0] if ok else (proc.stderr or proc.stdout or "pytest failed")[:200],
                )
            )
        except subprocess.TimeoutExpired:
            checks.append(_check("pytest_suite", "G6", False, "pytest timed out (180s)"))
        except Exception as exc:
            checks.append(_check("pytest_suite", "G6", False, str(exc)))
    else:
        checks.append(
            _check(
                "pytest_suite",
                "G6",
                True,
                "skipped — pass include_pytest=True or use noetfield gate --pytest",
                skipped=True,
            )
        )

    truth_path = root / "docs/_NOOS_AGENT/PRODUCT_TRUTH.md"
    manifest_path = root / "docs/_NOOS_AGENT/UPGRADE_MANIFEST.json"
    if truth_path.is_file() and manifest_path.is_file():
        try:
            import re

            text = truth_path.read_text(encoding="utf-8")
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            phase_match = re.search(r"Phase:\s*(\d+)", text)
            truth_phase = int(phase_match.group(1)) if phase_match else None
            manifest_phase = int(manifest.get("current_phase") or 0)
            ok = truth_phase is not None and truth_phase == manifest_phase
            checks.append(
                _check(
                    "product_truth_phase",
                    "G7",
                    ok,
                    f"PRODUCT_TRUTH phase {truth_phase} vs manifest {manifest_phase}",
                    truth_phase=truth_phase,
                    manifest_phase=manifest_phase,
                )
            )
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            checks.append(_check("product_truth_phase", "G7", False, str(exc)))
    else:
        checks.append(
            _check(
                "product_truth_phase",
                "G7",
                True,
                "skipped — PRODUCT_TRUTH or UPGRADE_MANIFEST missing",
                skipped=True,
            )
        )

    if strict:
        for check in checks:
            if check.get("skipped"):
                check["ok"] = False
                check["reason"] = f"strict mode: skipped check not allowed ({check.get('reason', '')})"

    failed = [c for c in checks if not c.get("ok")]
    outcome = "PASS" if not failed else "BLOCK"
    return {
        "schema": "noetfield-gate-report-v1",
        "tool": "noetfield-gate",
        "outcome": outcome,
        "checked_at": _now(),
        "root": str(root),
        "checks": checks,
        "block_reasons": [c["reason"] for c in failed],
    }


def write_gate_report(report: dict[str, Any], path: Path | None = None) -> Path:
    out = path or DEFAULT_RECEIPT
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    md_path = out.with_suffix(".md")
    lines = [
        "# Noetfield Gate Report",
        "",
        f"**Outcome:** {report['outcome']}",
        f"**Checked:** {report['checked_at']}",
        "",
        "| ID | Check | OK | Reason |",
        "|----|-------|----|--------|",
    ]
    for c in report.get("checks", []):
        lines.append(
            f"| {c.get('id','')} | {c.get('name','')} | {c.get('ok')} | {c.get('reason','')} |"
        )
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out


__all__ = ["run_gate_checks", "write_gate_report", "resolve_root", "DEFAULT_RECEIPT", "dated_receipt_dir"]
