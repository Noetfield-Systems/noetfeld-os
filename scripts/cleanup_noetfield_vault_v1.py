#!/usr/bin/env python3
"""Consolidate Noetfield/NOOS local vaults under ~/.noetfield-platform-secrets/."""

from __future__ import annotations

import shutil
from datetime import datetime, timezone
from pathlib import Path

from noos_vault_paths_v1 import (
    NOETFIELD_DB_ENV,
    NOETFIELD_LOCAL_ENV,
    NOETFIELD_PLATFORM_SECRETS,
    NOOS_LOCAL_ENV,
    NOOS_ONLY_KEYS,
    LEGACY_SOURCEA_NOETFIELD_ENV,
    parse_env_file,
)

LEGACY_DB = Path.home() / ".sourcea-secrets" / "noetfield-db.env"
STAMP = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def render_env(rows: dict[str, str], header: list[str]) -> str:
    lines = header + [""]
    for key in sorted(rows):
        if key.startswith("_"):
            continue
        val = rows[key]
        if " " in val and not (val.startswith('"') and val.endswith('"')):
            lines.append(f'{key}="{val}"')
        else:
            lines.append(f"{key}={val}")
    return "\n".join(lines) + "\n"


def merge_product_env() -> int:
    legacy = parse_env_file(LEGACY_SOURCEA_NOETFIELD_ENV)
    product = parse_env_file(NOETFIELD_LOCAL_ENV)
    for key, val in legacy.items():
        if key in NOOS_ONLY_KEYS:
            continue
        product.setdefault(key, val)
    NOETFIELD_PLATFORM_SECRETS.mkdir(parents=True, exist_ok=True)
    NOETFIELD_LOCAL_ENV.write_text(
        render_env(
            product,
            [
                "# Noetfield product — Supabase, intake, CF zone, deploy keys",
                "# Canonical path (not SourceA): ~/.noetfield-platform-secrets/noetfield.env",
            ],
        ),
        encoding="utf-8",
    )
    return len(product)


def merge_noos_env() -> int:
    from canonicalize_noos_vault_v1 import canonicalize

    canonicalize(NOOS_LOCAL_ENV, write=True, strict=True)
    noos = parse_env_file(NOOS_LOCAL_ENV)
    token = noos.get("CF_NOETFIELD_API_TOKEN") or noos.get("CLOUDFLARE_API_TOKEN")
    if token:
        noos["CF_NOETFIELD_API_TOKEN"] = token
    noos.pop("CLOUDFLARE_API_TOKEN", None)
    NOETFIELD_PLATFORM_SECRETS.mkdir(parents=True, exist_ok=True)
    NOOS_LOCAL_ENV.write_text(
        render_env(
            noos,
            [
                "# NOOS runtime — Cloudflare Workers motor, GHA deploy, loop secret",
                "# Canonical path: ~/.noetfield-platform-secrets/noos-local.env",
            ],
        ),
        encoding="utf-8",
    )
    return len(noos)


def sync_db_env() -> bool:
    if not LEGACY_DB.is_file():
        return False
    if not NOETFIELD_DB_ENV.is_file():
        shutil.copy2(LEGACY_DB, NOETFIELD_DB_ENV)
        return True
    return False


def backup_and_symlink(src: Path, target: Path) -> None:
    if not src.exists() and not src.is_symlink():
        return
    if src.is_symlink() and src.resolve() == target.resolve():
        return
    bak = src.with_suffix(src.suffix + f".bak-{STAMP}")
    if src.is_file() and not src.is_symlink():
        shutil.copy2(src, bak)
        src.unlink()
    elif src.is_symlink():
        src.unlink()
    src.symlink_to(target)


def sweep_legacy_backups() -> int:
    removed = 0
    for parent in (NOETFIELD_PLATFORM_SECRETS, Path.home() / ".sourcea-secrets"):
        if not parent.is_dir():
            continue
        for bak in parent.glob("*.bak-*"):
            try:
                bak.unlink()
                removed += 1
            except OSError:
                pass
    return removed


def write_readme() -> None:
    readme = NOETFIELD_PLATFORM_SECRETS / "README.txt"
    readme.write_text(
        "\n".join(
            [
                "Noetfield platform local secrets (not SourceA)",
                "",
                "  noos-local.env   — CF_NOETFIELD_API_TOKEN only (Workers Edit)",
                "  noetfield.env    — Noetfield product Supabase, intake, Resend",
                "  noetfield-db.env — DB password / DATABASE_URL for migrations",
                "",
                "Bootstrap:",
                "  make cloud-vault-canonicalize",
                "  make cloud-vault-promote",
                "  make cloud-secrets-sync",
                "",
                "Verify: python3 scripts/verify_noos_cf_deploy_token_v1.py",
                "",
            ]
        ),
        encoding="utf-8",
    )


def main() -> int:
    product_n = merge_product_env()
    noos_n = merge_noos_env()
    db_copied = sync_db_env()
    removed = sweep_legacy_backups()
    backup_and_symlink(LEGACY_SOURCEA_NOETFIELD_ENV, NOETFIELD_LOCAL_ENV)
    backup_and_symlink(LEGACY_DB, NOETFIELD_DB_ENV)
    write_readme()
    print(f"[cleanup-vault] product keys: {product_n} → {NOETFIELD_LOCAL_ENV}")
    print(f"[cleanup-vault] NOOS keys: {noos_n} → {NOOS_LOCAL_ENV}")
    print(f"[cleanup-vault] db env copied: {db_copied}")
    print(f"[cleanup-vault] legacy symlinks → {NOETFIELD_PLATFORM_SECRETS}")
    print(f"[cleanup-vault] removed .bak files: {removed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
