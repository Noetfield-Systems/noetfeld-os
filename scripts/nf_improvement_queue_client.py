"""Read/update public.improvement_queue via Supabase REST."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

_SCRIPTS = Path(__file__).resolve().parent
import sys

if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from nf_vault_env import ensure_noetfield_supabase_env  # noqa: E402

ROI_RANK = (
    "policy_compliance",
    "repo_stability",
    "drift_alignment",
    "greeting_coupling",
    "security_hygiene",
    "regression_safety",
)


def _config() -> tuple[str, str]:
    ensure_noetfield_supabase_env()
    url = (
        os.environ.get("NOETFIELD_SUPABASE_URL") or os.environ.get("SUPABASE_URL") or ""
    ).rstrip("/")
    key = (
        os.environ.get("NOETFIELD_SUPABASE_SERVICE_ROLE_KEY")
        or os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        or ""
    )
    if not url or not key:
        raise RuntimeError("NOETFIELD_SUPABASE_URL and service role key required")
    return url, key


def _request(
    method: str,
    path: str,
    *,
    body: object | None = None,
    prefer: str | None = None,
) -> Any:
    base, key = _config()
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Accept": "application/json",
    }
    if body is not None:
        headers["Content-Type"] = "application/json"
    if prefer:
        headers["Prefer"] = prefer
    data = None if body is None else json.dumps(body).encode("utf-8")
    req = urllib.request.Request(f"{base}{path}", data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw) if raw else None
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:500]
        raise RuntimeError(f"supabase {method} {path} HTTP {exc.code}: {detail}") from exc


def fetch_open_machine_safe(*, limit: int = 50) -> list[dict[str, Any]]:
    query = urllib.parse.urlencode(
        {
            "select": "id,finding,source,expected_roi,machine_safe,status,metadata,created_at",
            "status": "eq.open",
            "machine_safe": "eq.true",
            "order": "created_at.asc",
            "limit": str(limit),
        }
    )
    rows = _request("GET", f"/rest/v1/improvement_queue?{query}")
    if not isinstance(rows, list):
        return []

    def rank(row: dict[str, Any]) -> tuple[int, str]:
        roi = str(row.get("expected_roi") or "")
        try:
            idx = ROI_RANK.index(roi)
        except ValueError:
            idx = len(ROI_RANK)
        return (idx, str(row.get("created_at") or ""))

    return sorted(rows, key=rank)


def patch_row(
    row_id: str,
    *,
    status: str,
    metadata_patch: dict[str, Any] | None = None,
) -> None:
    body: dict[str, Any] = {"status": status}
    if metadata_patch:
        body["metadata"] = metadata_patch
    q = urllib.parse.urlencode({"id": f"eq.{row_id}"})
    _request("PATCH", f"/rest/v1/improvement_queue?{q}", body=body, prefer="return=minimal")


def insert_probe_receipt(*, run_id: str, status: str, receipt: dict[str, Any]) -> None:
    _request(
        "POST",
        "/rest/v1/probe_cron_receipts",
        body={
            "run_id": run_id,
            "probe_name": "kaizen_nightly",
            "status": status,
            "receipt": receipt,
        },
        prefer="return=minimal",
    )
