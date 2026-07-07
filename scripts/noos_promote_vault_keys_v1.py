#!/usr/bin/env python3
"""Promote NOOS keys from noetfield.env (incl. ~/.sourcea-secrets symlink) → noos-local.env."""

from __future__ import annotations

import re
from pathlib import Path

from noos_vault_paths_v1 import (
    NOOS_LOCAL_ENV,
    NOOS_ONLY_KEYS,
    NOETFIELD_LOCAL_ENV,
    NOETFIELD_PLATFORM_SECRETS,
    parse_env_file,
    workers_api_token,
)

CF_BARE = re.compile(r"^(cfat_|cfut_)[A-Za-z0-9_-]+$")


def scan_raw_lines(path: Path) -> tuple[dict[str, str], list[str]]:
    found: dict[str, str] = {}
    orphans: list[str] = []
    if not path.is_file():
        return found, orphans
    for line in path.read_text(encoding="utf-8").splitlines():
        raw = line.strip()
        if not raw or raw.startswith("#"):
            continue
        if "=" in raw:
            key, _, val = raw.partition("=")
            key = key.strip()
            val = val.strip().strip('"')
            if " " in key:
                continue
            if key in NOOS_ONLY_KEYS or key.startswith("NOOS_") or key.startswith("CLNOOS"):
                found[key] = val
            continue
        if CF_BARE.match(raw):
            orphans.append(raw)
    return found, orphans


def render_env(rows: dict[str, str], header: list[str]) -> str:
    lines = header + [""]
    for key in sorted(rows):
        lines.append(f"{key}={rows[key]}")
    return "\n".join(lines) + "\n"


def promote() -> dict[str, object]:
    NOETFIELD_PLATFORM_SECRETS.mkdir(parents=True, exist_ok=True)
    product = parse_env_file(NOETFIELD_LOCAL_ENV)
    noos = parse_env_file(NOOS_LOCAL_ENV)
    raw_keys, orphans = scan_raw_lines(NOETFIELD_LOCAL_ENV)

    for key, val in raw_keys.items():
        if key == "CLNOOS_" and val and not noos.get("NOOS_LOOP_SECRET"):
            noos["NOOS_LOOP_SECRET"] = val
        elif key in NOOS_ONLY_KEYS and val:
            noos[key] = val

    for orphan in orphans:
        if orphan.startswith("cfat_"):
            noos["CLOUDFLARE_API_TOKEN"] = orphan
        elif orphan.startswith("cfut_") and not noos.get("CF_NOETFIELD_API_TOKEN"):
            noos["CF_NOETFIELD_API_TOKEN"] = orphan

    token = workers_api_token(noos)
    if token:
        noos["CLOUDFLARE_API_TOKEN"] = token

    for key in list(product):
        if key in NOOS_ONLY_KEYS or key.startswith("NOOS_") or key.startswith("CLNOOS"):
            product.pop(key, None)

    NOOS_LOCAL_ENV.write_text(
        render_env(
            noos,
            [
                "# NOOS runtime — Cloudflare Workers motor, GHA deploy, loop secret",
                "# Edit here OR add to ~/.sourcea-secrets/noetfield.env then: make cloud-vault-promote",
            ],
        ),
        encoding="utf-8",
    )
    NOETFIELD_LOCAL_ENV.write_text(
        render_env(
            product,
            [
                "# Noetfield product — Supabase, intake, deploy keys (not NOOS CF motor)",
                "# ~/.sourcea-secrets/noetfield.env symlinks here",
            ],
        ),
        encoding="utf-8",
    )
    return {
        "noos_keys": len(noos),
        "product_keys": len(product),
        "orphan_tokens": len(orphans),
        "cloudflare_set": bool(noos.get("CLOUDFLARE_API_TOKEN")),
    }


def main() -> int:
    row = promote()
    print(f"[promote-vault] noos-local={row['noos_keys']} keys cloudflare={row['cloudflare_set']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
