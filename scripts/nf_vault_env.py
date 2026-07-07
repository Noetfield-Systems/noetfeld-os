#!/usr/bin/env python3
"""Load Noetfield Supabase keys from ~/.noetfield-platform-secrets/ (canonical)."""

from __future__ import annotations

import os
from pathlib import Path

PLATFORM_SECRETS = Path.home() / ".noetfield-platform-secrets"
NOETFIELD_ENV = PLATFORM_SECRETS / "noetfield.env"
NOETFIELD_DB_ENV = PLATFORM_SECRETS / "noetfield-db.env"
LEGACY_NOETFIELD_ENV = Path.home() / ".sourcea-secrets" / "noetfield.env"
LEGACY_NOETFIELD_DB_ENV = Path.home() / ".sourcea-secrets" / "noetfield-db.env"
SINA_SECRETS = Path.home() / ".sina" / "secrets.env"

SUPABASE_KEYS = (
    "NOETFIELD_SUPABASE_URL",
    "NOETFIELD_SUPABASE_ANON_KEY",
    "NOETFIELD_SUPABASE_SERVICE_ROLE_KEY",
    "NOETFIELD_SUPABASE_DATABASE_URL",
    "NOETFIELD_SUPABASE_REF",
    "SUPABASE_URL",
    "SUPABASE_ANON_KEY",
    "SUPABASE_SERVICE_ROLE_KEY",
    "SUPABASE_DATABASE_URL",
)


def parse_env_file(path: Path) -> dict[str, str]:
    if not path.is_file():
        return {}
    out: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key = key.strip()
        if " " in key:
            continue
        val = val.strip()
        if len(val) >= 2 and val[0] == val[-1] and val[0] in "\"'":
            val = val[1:-1]
        out[key] = val
    return out


def load_noetfield_vault() -> dict[str, str]:
    merged: dict[str, str] = {}
    for path in (SINA_SECRETS, LEGACY_NOETFIELD_ENV, LEGACY_NOETFIELD_DB_ENV, NOETFIELD_ENV, NOETFIELD_DB_ENV):
        merged.update(parse_env_file(path))
    return merged


def ensure_noetfield_supabase_env() -> None:
    """Populate missing NOETFIELD_SUPABASE_* from vault without overriding explicit env."""
    vault = load_noetfield_vault()
    aliases = {
        "NOETFIELD_SUPABASE_URL": ("SUPABASE_URL",),
        "NOETFIELD_SUPABASE_ANON_KEY": ("SUPABASE_ANON_KEY",),
        "NOETFIELD_SUPABASE_SERVICE_ROLE_KEY": ("SUPABASE_SERVICE_ROLE_KEY",),
        "NOETFIELD_SUPABASE_DATABASE_URL": ("SUPABASE_DATABASE_URL",),
    }
    for canonical, fallbacks in aliases.items():
        if os.environ.get(canonical):
            continue
        for key in (canonical, *fallbacks):
            val = vault.get(key, "")
            if val:
                os.environ[canonical] = val
                break
    ref = os.environ.get("NOETFIELD_SUPABASE_REF") or vault.get("NOETFIELD_SUPABASE_REF", "")
    if ref and not os.environ.get("NOETFIELD_SUPABASE_URL"):
        os.environ["NOETFIELD_SUPABASE_URL"] = f"https://{ref}.supabase.co"


def vault_status() -> dict[str, bool]:
    vault = load_noetfield_vault()
    return {key: bool(vault.get(key)) for key in SUPABASE_KEYS}


if __name__ == "__main__":
    import json

    ensure_noetfield_supabase_env()
    print(
        json.dumps(
            {
                "paths": {
                    "platform_noetfield_env": NOETFIELD_ENV.is_file(),
                    "platform_noetfield_db_env": NOETFIELD_DB_ENV.is_file(),
                    "legacy_noetfield_env": LEGACY_NOETFIELD_ENV.is_file(),
                    "sina_secrets": SINA_SECRETS.is_file(),
                },
                "vault_keys": vault_status(),
                "resolved": {
                    "NOETFIELD_SUPABASE_URL": bool(os.environ.get("NOETFIELD_SUPABASE_URL")),
                    "NOETFIELD_SUPABASE_SERVICE_ROLE_KEY": bool(
                        os.environ.get("NOETFIELD_SUPABASE_SERVICE_ROLE_KEY")
                    ),
                    "NOETFIELD_SUPABASE_ANON_KEY": bool(
                        os.environ.get("NOETFIELD_SUPABASE_ANON_KEY")
                    ),
                    "NOETFIELD_SUPABASE_DATABASE_URL": bool(
                        os.environ.get("NOETFIELD_SUPABASE_DATABASE_URL")
                    ),
                },
            }
        )
    )
