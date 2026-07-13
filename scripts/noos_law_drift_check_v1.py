#!/usr/bin/env python3
"""LSUP v0.1 — scan agent-facing docs for forbidden tokens outside FORBIDDEN_MARKERS.txt."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

ROOT = Path(__file__).resolve().parents[1]
MARKER_PATH = ROOT / "noetfield-org/FORBIDDEN_MARKERS.txt"
REGISTRY_PATH = ROOT / "noetfield-org/system-laws/SYSTEM_LAW_REGISTRY_v1.json"
RECEIPT_PATH = ROOT / "receipts/proof/noos-law-drift-check-v1.json"

SCAN_ROOTS = (
    ROOT / "noetfield-org",
    ROOT / "docs/_NOOS_AGENT",
    ROOT / "docs/ops",
)

SCAN_FILES = (
    ROOT / "AGENTS.md",
    ROOT / ".github/copilot-instructions.md",
    ROOT / ".noetfield/agent_manifest.yml",
)

SKIP_DIR_NAMES = frozenset(
    {
        ".git",
        "__pycache__",
        "node_modules",
        ".venv",
        "venv",
        "graph-out",
        "www-pages-dist",
        ".noos-runtime",
    }
)

SKIP_RELATIVE_FILES = frozenset(
    {
        "noetfield-org/FORBIDDEN_MARKERS.txt",
        "noetfield-org/system-laws/SYSTEM_LAW_REGISTRY_v1.json",
    }
)

TEXT_SUFFIXES = frozenset({".md", ".json", ".txt", ".yml", ".yaml", ".mdc"})


def _is_skipped_file(path: Path) -> bool:
    try:
        rel = path.relative_to(ROOT).as_posix()
    except ValueError:
        return False
    return rel in SKIP_RELATIVE_FILES


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_forbidden_markers(path: Path = MARKER_PATH) -> list[str]:
    if not path.is_file():
        raise FileNotFoundError(f"missing forbidden marker file: {path}")
    markers: list[str] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        markers.append(line)
    if not markers:
        raise ValueError(f"no forbidden markers defined in {path}")
    return markers


def _registry_ok(path: Path = REGISTRY_PATH) -> tuple[bool, dict[str, Any]]:
    if not path.is_file():
        return False, {"error": "missing", "path": str(path)}
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return False, {"error": f"invalid json: {exc}", "path": str(path)}
    ok = doc.get("schema") == "noos-system-law-v1" and isinstance(doc.get("laws"), list)
    return ok, {"path": str(path), "registry_version": doc.get("registry_version"), "law_count": len(doc.get("laws") or [])}


def iter_scan_files() -> Iterator[Path]:
    seen: set[Path] = set()

    def emit(path: Path) -> Iterator[Path]:
        resolved = path.resolve()
        if resolved in seen or not path.is_file():
            return
        if _is_skipped_file(path):
            return
        if path.suffix.lower() not in TEXT_SUFFIXES:
            return
        seen.add(resolved)
        yield path

    for explicit in SCAN_FILES:
        yield from emit(explicit)

    for root in SCAN_ROOTS:
        if not root.is_dir():
            continue
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            if any(part in SKIP_DIR_NAMES for part in path.parts):
                continue
            if path.name.startswith("."):
                continue
            yield from emit(path)


def find_violations(
    markers: list[str] | None = None,
    *,
    root: Path = ROOT,
) -> tuple[list[dict[str, Any]], int]:
    del root  # reserved for tests with patched paths
    tokens = markers if markers is not None else load_forbidden_markers()
    lowered = [(token, token.lower()) for token in tokens]
    violations: list[dict[str, Any]] = []
    files_scanned = 0

    for path in iter_scan_files():
        files_scanned += 1
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for line_no, line in enumerate(text.splitlines(), start=1):
            line_lower = line.lower()
            for token, token_lower in lowered:
                if token_lower in line_lower:
                    violations.append(
                        {
                            "path": str(path.relative_to(ROOT)),
                            "line": line_no,
                            "marker": token,
                            "snippet": line.strip()[:160],
                        }
                    )

    return violations, files_scanned


def run_check(*, markers: list[str] | None = None) -> dict[str, Any]:
    registry_ok, registry = _registry_ok()
    violations, files_scanned = find_violations(markers=markers)
    marker_list = markers if markers is not None else load_forbidden_markers()
    ok = registry_ok and not violations
    return {
        "schema": "noos-law-drift-check-v1",
        "at": utc_now(),
        "ok": ok,
        "markers": marker_list,
        "registry_ok": registry_ok,
        "registry": registry,
        "files_scanned": files_scanned,
        "violation_count": len(violations),
        "violations": violations[:50],
        "closure_token": "NOOS_LAW_DRIFT: green" if ok else "NOOS_LAW_DRIFT: fail",
        "fix": None
        if ok
        else "Purge forbidden tokens from listed paths; keep tokens only in noetfield-org/FORBIDDEN_MARKERS.txt",
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--write-receipt", action="store_true")
    args = ap.parse_args()

    try:
        row = run_check()
    except (FileNotFoundError, ValueError) as exc:
        row = {
            "schema": "noos-law-drift-check-v1",
            "at": utc_now(),
            "ok": False,
            "error": str(exc),
            "closure_token": "NOOS_LAW_DRIFT: fail",
        }

    if args.write_receipt:
        RECEIPT_PATH.parent.mkdir(parents=True, exist_ok=True)
        RECEIPT_PATH.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        row["receipt_path"] = str(RECEIPT_PATH)

    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row["closure_token"])
        if not row.get("ok"):
            for hit in row.get("violations") or []:
                print(f"  {hit['path']}:{hit['line']} marker={hit['marker']}")

    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
