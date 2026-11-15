"""Canonical pair selection for the already-active Supabase project.

This is an env adapter ONLY, not a database migration, backup restore, or
new queue. Never combine a URL from one project with another project's key.
The old, paused Supabase URL can remain in Railway env for legacy audits,
but all ordinary child loops must receive one canonical active pair.
"""
from __future__ import annotations

import re
from urllib.parse import urlparse


def canonical_env(source: dict[str, str]) -> dict[str, str]:
    """Select active URL/key together, preserving unrelated process variables.

    Partial or malformed active configuration fails closed with fixed codes.
    The existing task/data schemas still have to be verified by normal probes.
    """
    out=dict(source)
    url=(out.get("NOETFIELD_ACTIVE_SUPABASE_URL") or "").strip().rstrip("/")
    key=(out.get("NOETFIELD_ACTIVE_SUPABASE_SERVICE_ROLE_KEY") or "").strip()
    if not url and not key:
        out["NOOS_SUPABASE_SOURCE"]="LEGACY_UNCHANGED"
        return out
    if not url or not key:
        raise RuntimeError("NOOS_ACTIVE_SUPABASE_PAIR_INCOMPLETE")
    parsed=urlparse(url)
    if (parsed.scheme!="https" or not parsed.hostname
            or not re.fullmatch(r"[a-z0-9]{12,32}\.supabase\.co",parsed.hostname)
            or parsed.username or parsed.password or parsed.port not in (None,443)
            or parsed.path not in ("","/") or parsed.query or parsed.fragment
            or len(key)<24):
        raise RuntimeError("NOOS_ACTIVE_SUPABASE_PAIR_INVALID")
    out["NOETFIELD_SUPABASE_URL"]=url
    out["NOETFIELD_SUPABASE_SERVICE_ROLE_KEY"]=key
    out["SUPABASE_URL"]=url
    out["SUPABASE_SERVICE_ROLE_KEY"]=key
    out["NOOS_SUPABASE_SOURCE"]="ACTIVE_PAIR"
    return out
