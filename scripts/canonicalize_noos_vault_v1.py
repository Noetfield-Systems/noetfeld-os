#!/usr/bin/env python3
"""Dedupe and canonicalize ~/.noetfield-platform-secrets/noos-local.env."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

from noos_vault_paths_v1 import NOOS_LOCAL_ENV, NOOS_ONLY_KEYS, parse_env_file

CF_BARE = re.compile(r"^(cfat_|cfut_)[A-Za-z0-9_-]+$")
TOKEN_KEYS = ("CF_NOETFIELD_API_TOKEN", "CLOUDFLARE_API_TOKEN")
KEEP_KEYS = frozenset(
    {
        "CF_NOETFIELD_API_TOKEN",
        "CF_NOETFIELD_ZONE_ID",
        "CLOUDFLARE_ACCOUNT_ID",
        "NOOS_LOOP_SECRET",
    }
)


def _parse_raw(path: Path, *, strict: bool = True) -> tuple[dict[str, str], list[str], list[str]]:
    """Parse key=value; strict mode fails on duplicate keys with conflicting values."""
    rows: dict[str, str] = {}
    warnings: list[str] = []
    orphans: list[str] = []
    errors: list[str] = []
    if not path.is_file():
        return rows, warnings, orphans
    for lineno, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, _, val = line.partition("=")
            key = key.strip()
            val = val.strip().strip('"')
            if " " in key:
                warnings.append(f"line {lineno}: skipped malformed key {key!r}")
                continue
            if key in rows and rows[key] != val:
                msg = f"line {lineno}: duplicate {key} with conflicting value"
                if strict:
                    errors.append(msg)
                else:
                    warnings.append(f"{msg} (last wins)")
            rows[key] = val
            continue
        if CF_BARE.match(line):
            orphans.append(line)
    if errors:
        raise SystemExit("canonicalize FAIL:\n  " + "\n  ".join(errors))
    return rows, warnings, orphans


def _token_candidates(rows: dict[str, str], orphans: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for key in TOKEN_KEYS:
        val = rows.get(key, "")
        if val and val not in seen:
            seen.add(val)
            ordered.append(val)
    for orphan in orphans:
        if orphan not in seen:
            seen.add(orphan)
            ordered.append(orphan)
    return ordered


def _pick_workers_token(candidates: list[str]) -> str:
    if not candidates:
        return ""
    try:
        from verify_noos_cf_deploy_token_v1 import verify
    except ImportError:
        verify = None

    if verify:
        for tok in reversed(candidates):
            row = verify(tok)
            if row.get("ok"):
                return tok

    # Last explicit CLOUDFLARE_API_TOKEN / CF_NOETFIELD wins when none verify.
    return candidates[-1]


def canonicalize(path: Path = NOOS_LOCAL_ENV, write: bool = True, *, strict: bool = True) -> dict[str, object]:
    rows, warnings, orphans = _parse_raw(path, strict=strict)
    candidates = _token_candidates(rows, orphans)
    workers = _pick_workers_token(candidates)

    clean: dict[str, str] = {}
    if workers:
        clean["CF_NOETFIELD_API_TOKEN"] = workers
    zone = rows.get("CF_NOETFIELD_ZONE_ID", "")
    if zone:
        clean["CF_NOETFIELD_ZONE_ID"] = zone
    account = rows.get("CLOUDFLARE_ACCOUNT_ID", "0d0b967b77e2e5535455d39ff3dae72c")
    if account:
        clean["CLOUDFLARE_ACCOUNT_ID"] = account
    loop = rows.get("NOOS_LOOP_SECRET", "")
    if loop:
        clean["NOOS_LOOP_SECRET"] = loop

    stripped = [k for k in rows if k in NOOS_ONLY_KEYS and k not in KEEP_KEYS]
    if "CLOUDFLARE_API_TOKEN" in rows and workers:
        stripped.append("CLOUDFLARE_API_TOKEN")

    header = [
        "# NOOS runtime — Cloudflare Workers motor, GHA deploy, loop secret",
        "# Canonical: CF_NOETFIELD_API_TOKEN only (Workers Edit). Do NOT duplicate CLOUDFLARE_API_TOKEN here.",
        "# GHA sync derives CLOUDFLARE_API_TOKEN from CF_NOETFIELD_API_TOKEN via make cloud-vault-promote",
    ]
    body = "\n".join(header + [""] + [f"{k}={clean[k]}" for k in sorted(clean)]) + "\n"

    if write and path.parent.exists():
        path.write_text(body, encoding="utf-8")

    return {
        "path": str(path),
        "written": write,
        "warnings": warnings,
        "stripped_keys": sorted(set(stripped)),
        "orphans_merged": len(orphans),
        "workers_token_sha8": hashlib.sha256(workers.encode()).hexdigest()[:8] if workers else "",
        "keys": sorted(clean.keys()),
    }


def main() -> int:
    write = "--dry-run" not in sys.argv
    strict = "--lenient" not in sys.argv
    row = canonicalize(write=write, strict=strict)
    print(json.dumps(row, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
