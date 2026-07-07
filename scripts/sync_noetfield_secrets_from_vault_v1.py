#!/usr/bin/env python3
"""Merge Noetfield-related keys from ~/.sina/secrets.env into ~/.noetfield-platform-secrets/."""

from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import quote_plus

from noos_vault_paths_v1 import NOETFIELD_DB_ENV, NOETFIELD_LOCAL_ENV

VAULT = Path.home() / ".sina" / "secrets.env"
NOETFIELD_ENV = NOETFIELD_LOCAL_ENV
REF = "tkgpapowwplupyekpivy"

# secrets.env key -> noetfield.env key
TRANSFER_MAP = {
    "RESEND_NOETFIELD_API_KEY": "RESEND_API_KEY",
    "CF_NOETFIELD_API_TOKEN": "CF_NOETFIELD_API_TOKEN",
    "CF_NOETFIELD_ZONE_ID": "CF_NOETFIELD_ZONE_ID",
    "OPENROUTER_API_KEY": "OPENROUTER_API_KEY",
    "INTAKE_EMAIL_FROM": "INTAKE_EMAIL_FROM",
    "INTAKE_EMAIL_TO": "INTAKE_EMAIL_TO",
    "INTAKE_AUTO_ACK_ENABLED": "INTAKE_AUTO_ACK_ENABLED",
    "FBE_CLOUD_WORKER_URL": "FBE_CLOUD_WORKER_URL",
    "FBE_INTERNAL_SECRET": "FBE_INTERNAL_SECRET",
    "PYPI_API_TOKEN": "PYPI_API_TOKEN",
}

ALIAS_FROM_EXISTING = {
    "NOETFIELD_SUPABASE_URL": "SUPABASE_URL",
    "NOETFIELD_SUPABASE_ANON_KEY": "SUPABASE_ANON_KEY",
    "NOETFIELD_SUPABASE_SERVICE_ROLE_KEY": "SUPABASE_SERVICE_ROLE_KEY",
    "NOETFIELD_SUPABASE_REF": "SUPABASE_PROJECT_ID",
}


def parse_env(path: Path) -> dict[str, str]:
    if not path.is_file():
        return {}
    out: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key = key.strip()
        val = val.strip().strip('"').strip("'")
        out[key] = val
    return out


def render_env(rows: dict[str, str], header: list[str]) -> str:
    lines = header + [""]
    for key in sorted(rows):
        if key.startswith("_"):
            continue
        val = rows[key]
        if " " in val or val.startswith("<"):
            lines.append(f'{key}="{val}"')
        else:
            lines.append(f"{key}={val}")
    return "\n".join(lines) + "\n"


def main() -> int:
    vault = parse_env(VAULT)
    nf = parse_env(NOETFIELD_ENV)
    db = parse_env(NOETFIELD_DB_ENV)

    transferred: list[str] = []
    for src, dst in TRANSFER_MAP.items():
        if vault.get(src):
            nf[dst] = vault[src]
            transferred.append(f"{src}->{dst}")

    for alias, src in ALIAS_FROM_EXISTING.items():
        val = nf.get(src) or vault.get(src)
        if val:
            nf[alias] = val

    if not nf.get("SUPABASE_PROJECT_ID"):
        nf["SUPABASE_PROJECT_ID"] = REF
    if not nf.get("NOETFIELD_SUPABASE_REF"):
        nf["NOETFIELD_SUPABASE_REF"] = nf.get("SUPABASE_PROJECT_ID", REF)

    password = db.get("SUPABASE_DB_PASSWORD") or vault.get("SUPABASE_DB_PASSWORD") or vault.get(
        "NOETFIELD_SUPABASE_DB_PASSWORD"
    )
    if password:
        db["SUPABASE_DB_PASSWORD"] = password
        encoded = quote_plus(password)
        direct = f"postgresql://postgres:{encoded}@db.{REF}.supabase.co:5432/postgres"
        db["NOETFIELD_SUPABASE_DATABASE_URL"] = direct

    NOETFIELD_ENV.parent.mkdir(parents=True, exist_ok=True)
    NOETFIELD_ENV.write_text(
        render_env(
            nf,
            [
                "# Supabase — Noetfield (synced from ~/.sina/secrets.env + dashboard)",
                "# GitHub Actions: NOETFIELD_SUPABASE_URL, NOETFIELD_SUPABASE_ANON_KEY,",
                "#   NOETFIELD_SUPABASE_SERVICE_ROLE_KEY, SUPABASE_DB_PASSWORD (noetfield-db.env)",
            ],
        ),
        encoding="utf-8",
    )
    NOETFIELD_DB_ENV.write_text(
        render_env(
            db,
            [
                "# Noetfield — database password + direct DATABASE_URL for CI/migrations",
                "# GitHub secret SUPABASE_DB_PASSWORD = value only (no quotes)",
            ],
        ),
        encoding="utf-8",
    )

    print(f"Updated {NOETFIELD_ENV} ({len(nf)} keys)")
    print(f"Updated {NOETFIELD_DB_ENV} ({len(db)} keys)")
    if transferred:
        print("Transferred from vault:", ", ".join(transferred))
    else:
        print("No new vault keys transferred (aliases refreshed)")
    print("GitHub secrets to paste:")
    print("  NOETFIELD_SUPABASE_URL        <- noetfield.env NOETFIELD_SUPABASE_URL")
    print("  NOETFIELD_SUPABASE_ANON_KEY   <- noetfield.env NOETFIELD_SUPABASE_ANON_KEY")
    print("  NOETFIELD_SUPABASE_SERVICE_ROLE_KEY <- noetfield.env NOETFIELD_SUPABASE_SERVICE_ROLE_KEY")
    print("  SUPABASE_DB_PASSWORD          <- noetfield-db.env SUPABASE_DB_PASSWORD (value only)")
    print("  NOETFIELD_SUPABASE_DATABASE_URL <- noetfield-db.env NOETFIELD_SUPABASE_DATABASE_URL (optional)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
