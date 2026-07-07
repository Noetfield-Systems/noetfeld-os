"""Canonical local vault paths — NOOS + Noetfield platform (not SourceA)."""
from __future__ import annotations

from pathlib import Path

NOETFIELD_PLATFORM_SECRETS = Path.home() / ".noetfield-platform-secrets"
NOOS_LOCAL_ENV = NOETFIELD_PLATFORM_SECRETS / "noos-local.env"
NOETFIELD_LOCAL_ENV = NOETFIELD_PLATFORM_SECRETS / "noetfield.env"
NOETFIELD_DB_ENV = NOETFIELD_PLATFORM_SECRETS / "noetfield-db.env"

# Legacy fallback only — symlink target after `make cloud-vault-cleanup`.
LEGACY_SOURCEA_NOETFIELD_ENV = Path.home() / ".sourcea-secrets" / "noetfield.env"

NOOS_ONLY_KEYS = frozenset(
    {
        "CLOUDFLARE_API_TOKEN",
        "CF_NOETFIELD_API_TOKEN",
        "CF_NOETFIELD_ZONE_ID",
        "NOOS_LOOP_SECRET",
    }
)


def parse_env_file(path: Path) -> dict[str, str]:
    if not path.is_file():
        return {}
    out: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        if " " in key:
            continue
        out[key] = value.strip().strip('"')
    return out


def noos_loop_secret() -> str:
    env = load_platform_env()
    return env.get("NOOS_LOOP_SECRET") or env.get("LOOP_RUNNER_SECRET") or ""


def resolve_env_paths() -> list[Path]:
    paths: list[Path] = []
    for candidate in (NOOS_LOCAL_ENV, NOETFIELD_LOCAL_ENV):
        if candidate.is_file() and candidate not in paths:
            paths.append(candidate)
    return paths


def workers_api_token(env: dict[str, str] | None = None) -> str:
    """Wrangler deploy token — prefer CF_NOETFIELD_API_TOKEN (Workers Edit) over generic CF token."""
    row = env if env is not None else load_platform_env()
    return row.get("CF_NOETFIELD_API_TOKEN") or row.get("CLOUDFLARE_API_TOKEN") or ""


def load_platform_env() -> dict[str, str]:
    merged: dict[str, str] = {}
    for path in resolve_env_paths():
        merged.update(parse_env_file(path))
    token = workers_api_token(merged)
    if token:
        merged["CLOUDFLARE_API_TOKEN"] = token
    return merged


def supabase_creds() -> tuple[str, str]:
    env = load_platform_env()
    url = env.get("NOETFIELD_SUPABASE_URL") or env.get("SUPABASE_URL", "")
    key = env.get("NOETFIELD_SUPABASE_SERVICE_ROLE_KEY") or env.get(
        "SUPABASE_SERVICE_ROLE_KEY", ""
    )
    return url, key
