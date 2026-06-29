#!/usr/bin/env python3
"""Fail closed when generated public output exposes internal Noetfield truth."""

from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / ".vercel" / "output" / "static"
DENYLIST = ROOT / "governance" / "PUBLIC_OUTPUT_DENYLIST.json"

def public_denylist() -> dict[str, list[str]]:
    return json.loads(DENYLIST.read_text(encoding="utf-8"))


def forbidden_prefixes() -> tuple[str, ...]:
    denylist = public_denylist()
    prefixes = [prefix.lstrip("/") for prefix in denylist.get("prefix_paths", [])]
    return tuple(dict.fromkeys(prefixes + ["prompts/"]))


def forbidden_exact() -> set[str]:
    denylist = public_denylist()
    exact = {path.lstrip("/") for path in denylist.get("exact_paths", [])}
    exact.update({"Makefile", "railway.json", "package-lock.json"})
    return exact

FORBIDDEN_ROOT_PATTERNS = (
    re.compile(r"^[A-Z0-9_./-]*LOCKED(?:_[A-Za-z0-9.-]+)?\.md$"),
    re.compile(r"^[A-Z0-9_./-]*SSOT(?:_[A-Za-z0-9.-]+)?\.md$"),
)

TEXT_SUFFIXES = {
    ".html",
    ".htm",
    ".js",
    ".json",
    ".md",
    ".txt",
    ".css",
    ".xml",
}

FORBIDDEN_CONTENT_PATTERNS = (
    re.compile(r"/docs/ops/", re.I),
    re.compile(r"docs/ops/", re.I),
    re.compile(r"/services/", re.I),
    re.compile(r"services/governance", re.I),
    re.compile(r"AGENT_SELF_AUDIT", re.I),
    re.compile(r"plan-with-no-asf", re.I),
    re.compile(r"make nf-prove", re.I),
    re.compile(r"Hub approve", re.I),
    re.compile(r"founder never", re.I),
    re.compile(r"SourceA", re.I),
    re.compile(r"/Users/sinakazemnezhad/", re.I),
    re.compile(r"ops/private", re.I),
    re.compile(r"\.jsonl\b", re.I),
)

PUBLIC_MARKDOWN_PREFIXES = (
    "docs/api/",
    "docs/copilot/",
    "docs/diligence/",
    "docs/federal/",
    "docs/msp/",
    "docs/runtime/",
    "docs/templates/",
    "docs/trust-brief/",
)


def rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def is_forbidden(rel_path: str) -> str | None:
    if rel_path in forbidden_exact():
        return "forbidden exact file"
    if any(rel_path.startswith(prefix) for prefix in forbidden_prefixes()):
        return "forbidden internal prefix"
    if "/" not in rel_path:
        if any(pattern.search(rel_path) for pattern in FORBIDDEN_ROOT_PATTERNS):
            return "forbidden root truth doc"
    if rel_path.endswith(".md") and not rel_path.startswith(PUBLIC_MARKDOWN_PREFIXES):
        return "markdown is not in public-doc allowlist"
    if rel_path.endswith(".jsonl"):
        return "jsonl telemetry/log file"
    return None


def content_findings(path: Path, rel_path: str) -> list[dict[str, str]]:
    if path.suffix not in TEXT_SUFFIXES:
        return []
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return []
    findings: list[dict[str, str]] = []
    for pattern in FORBIDDEN_CONTENT_PATTERNS:
        if pattern.search(text):
            findings.append(
                {
                    "path": rel_path,
                    "reason": f"forbidden internal content: {pattern.pattern}",
                }
            )
    return findings


def scan(output: Path) -> list[dict[str, str]]:
    if not output.exists():
        return []
    findings: list[dict[str, str]] = []
    for path in output.rglob("*"):
        if not path.is_file():
            continue
        rel_path = rel(path, output)
        reason = is_forbidden(rel_path)
        if reason:
            findings.append({"path": rel_path, "reason": reason})
            continue
        findings.extend(content_findings(path, rel_path))
    return findings


def clean(output: Path, findings: list[dict[str, str]]) -> None:
    for finding in findings:
        target = output / finding["path"]
        if target.is_file():
            target.unlink()
    for directory in sorted((p for p in output.rglob("*") if p.is_dir()), reverse=True):
        try:
            directory.rmdir()
        except OSError:
            pass
    for prefix in forbidden_prefixes():
        top = output / prefix.split("/", 1)[0]
        if top.exists() and top.is_dir() and not any(top.iterdir()):
            shutil.rmtree(top)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--clean", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    output = Path(args.output)
    findings = scan(output)
    if args.clean and findings:
        clean(output, findings)
        findings = scan(output)

    payload = {
        "ok": not findings,
        "output": str(output),
        "blocked_count": len(findings),
        "findings": findings[:100],
    }
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    elif findings:
        for finding in findings[:100]:
            print(
                f"FAIL public-output-allowlist: {finding['path']} ({finding['reason']})"
            )
        if len(findings) > 100:
            print(f"FAIL public-output-allowlist: {len(findings) - 100} more findings")
    else:
        print("OK   public-output-allowlist: generated output contains no internal truth surfaces")
    return 0 if not findings else 1


if __name__ == "__main__":
    raise SystemExit(main())
