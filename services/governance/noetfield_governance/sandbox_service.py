"""Server-backed developer sandbox — provision, evaluate caps, observe-only freemium."""

from __future__ import annotations

import hashlib
import re
import secrets
import time
from dataclasses import dataclass
from typing import Literal

from fastapi import HTTPException

from noetfield_config import get_settings
from noetfield_governance import redis_runtime
from noetfield_governance.governance_rid import generate_rid
from noetfield_governance.trust_ledger_pdf import minimal_pdf

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_FREE_EMAIL_DOMAINS = frozenset(
    {
        "gmail.com",
        "googlemail.com",
        "yahoo.com",
        "yahoo.ca",
        "hotmail.com",
        "outlook.com",
        "live.com",
        "icloud.com",
        "me.com",
        "aol.com",
        "proton.me",
        "protonmail.com",
        "mail.com",
        "gmx.com",
        "yandex.com",
    }
)

SANDBOX_MODE: Literal["observe"] = "observe"
_FACTORY_DEMO_IDS = (
    "copilot_governance_readiness_v1",
    "trust_brief_diligence_v1",
    "legal_review_v1",
)

_memory_sessions: dict[str, dict[str, object]] = {}
_memory_provision_buckets: dict[str, list[float]] = {}


@dataclass(frozen=True)
class SandboxSession:
    session_token: str
    tenant_id: str
    email: str
    org: str
    api_key_preview: str
    mode: Literal["observe"]
    evaluates_used: int
    evaluates_limit: int
    created_at: str
    expires_at: str
    trial_step: int
    m365_connected: bool
    last_rid: str | None
    factory_demos_run: list[str]

    def to_dict(self) -> dict[str, object]:
        return {
            "session_token": self.session_token,
            "tenant_id": self.tenant_id,
            "email": self.email,
            "org": self.org,
            "api_key_preview": self.api_key_preview,
            "mode": self.mode,
            "evaluates_used": self.evaluates_used,
            "evaluates_limit": self.evaluates_limit,
            "created_at": self.created_at,
            "expires_at": self.expires_at,
            "trial_step": self.trial_step,
            "m365_connected": self.m365_connected,
            "last_rid": self.last_rid,
            "factory_demos_run": list(self.factory_demos_run),
        }

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> SandboxSession:
        demos = data.get("factory_demos_run") or []
        if not isinstance(demos, list):
            demos = []
        return cls(
            session_token=str(data["session_token"]),
            tenant_id=str(data["tenant_id"]),
            email=str(data["email"]),
            org=str(data.get("org") or "Sandbox org"),
            api_key_preview=str(data.get("api_key_preview") or ""),
            mode="observe",
            evaluates_used=int(data.get("evaluates_used") or 0),
            evaluates_limit=int(data.get("evaluates_limit") or 50),
            created_at=str(data.get("created_at") or ""),
            expires_at=str(data.get("expires_at") or ""),
            trial_step=int(data.get("trial_step") or 0),
            m365_connected=bool(data.get("m365_connected")),
            last_rid=str(data["last_rid"]) if data.get("last_rid") else None,
            factory_demos_run=[str(x) for x in demos],
        )


def _ttl_sec() -> int:
    return get_settings().sandbox_trial_days * 86400


def _session_key(token: str) -> str:
    return f"nf:sbx:session:{token}"


def _new_tenant_id() -> str:
    return "sandbox-" + secrets.token_hex(4)


def _new_session_token() -> str:
    return secrets.token_urlsafe(24)


def validate_work_email(email: str) -> str:
    normalized = (email or "").strip().lower()
    if not normalized or len(normalized) > 254 or not _EMAIL_RE.match(normalized):
        raise ValueError("email must be a valid work email address")
    domain = normalized.rsplit("@", 1)[-1]
    settings = get_settings()
    if settings.sandbox_block_free_email and domain in _FREE_EMAIL_DOMAINS:
        raise ValueError("use a work email address — consumer domains are not accepted in sandbox")
    return normalized


async def _check_provision_rate_limit(client_key: str) -> None:
    settings = get_settings()
    limit = settings.sandbox_provision_rate_limit_per_hour
    if limit <= 0:
        return
    key = f"sandbox:provision:{client_key}"
    if redis_runtime.is_enabled():
        try:
            await redis_runtime.check_rate_limit(key, max_calls=limit, window_sec=3600)
        except PermissionError as exc:
            raise HTTPException(status_code=429, detail=str(exc)) from exc
        return
    now = time.time()
    bucket = _memory_provision_buckets.setdefault(key, [])
    cutoff = now - 3600
    _memory_provision_buckets[key] = [t for t in bucket if t > cutoff]
    if len(_memory_provision_buckets[key]) >= limit:
        raise HTTPException(status_code=429, detail="Sandbox provision rate limit exceeded")
    _memory_provision_buckets[key].append(now)


async def _load_session(token: str) -> SandboxSession | None:
    token = (token or "").strip()
    if not token:
        return None
    if redis_runtime.is_enabled():
        data = await redis_runtime.get_json(_session_key(token))
        if not data:
            return None
        return SandboxSession.from_dict(data)
    data = _memory_sessions.get(token)
    if not data:
        return None
    return SandboxSession.from_dict(data)


async def _save_session(session: SandboxSession) -> None:
    payload = session.to_dict()
    if redis_runtime.is_enabled():
        await redis_runtime.set_json(_session_key(session.session_token), payload, ttl_sec=_ttl_sec())
        return
    _memory_sessions[session.session_token] = payload


def reset_sandbox_memory_for_tests() -> None:
    _memory_sessions.clear()
    _memory_provision_buckets.clear()


async def provision_sandbox(*, email: str, org: str | None, client_key: str) -> SandboxSession:
    settings = get_settings()
    if not settings.sandbox_enabled:
        raise HTTPException(status_code=503, detail="Sandbox provisioning is disabled")
    await _check_provision_rate_limit(client_key or "anonymous")
    work_email = validate_work_email(email)
    now = time.time()
    expires = now + settings.sandbox_trial_days * 86400
    token = _new_session_token()
    session = SandboxSession(
        session_token=token,
        tenant_id=_new_tenant_id(),
        email=work_email,
        org=(org or "").strip() or "Sandbox org",
        api_key_preview="nf_sbx_" + secrets.token_hex(4),
        mode=SANDBOX_MODE,
        evaluates_used=0,
        evaluates_limit=settings.sandbox_evaluate_limit,
        created_at=_iso(now),
        expires_at=_iso(expires),
        trial_step=0,
        m365_connected=False,
        last_rid=None,
        factory_demos_run=[],
    )
    await _save_session(session)
    return session


async def get_sandbox_session(token: str) -> SandboxSession:
    session = await _load_session(token)
    if session is None:
        raise HTTPException(status_code=404, detail="Sandbox session not found or expired")
    if _is_expired(session):
        raise HTTPException(status_code=410, detail="Sandbox session expired")
    return session


async def update_sandbox_session(
    token: str,
    *,
    trial_step: int | None = None,
    m365_connected: bool | None = None,
) -> SandboxSession:
    session = await get_sandbox_session(token)
    if trial_step is not None:
        session = _replace(session, trial_step=max(session.trial_step, trial_step))
    if m365_connected is not None:
        session = _replace(session, m365_connected=m365_connected)
    await _save_session(session)
    return session


async def sandbox_evaluate(token: str) -> dict[str, object]:
    session = await get_sandbox_session(token)
    if session.evaluates_used >= session.evaluates_limit:
        raise HTTPException(
            status_code=429,
            detail=f"Sandbox evaluate cap reached ({session.evaluates_limit}). Upgrade via Copilot Readiness Pack.",
        )
    rid = generate_rid()
    used = session.evaluates_used + 1
    step = max(session.trial_step, 4)
    session = _replace(
        session,
        evaluates_used=used,
        trial_step=step,
        last_rid=rid,
    )
    await _save_session(session)
    warn_threshold = max(1, int(session.evaluates_limit * 0.8))
    return {
        "rid": rid,
        "tenant_id": session.tenant_id,
        "mode": session.mode,
        "decision": "allow",
        "allowed": True,
        "reason": "Sandbox observe-mode evaluate — metadata-only mock M365 signals.",
        "evaluates_used": used,
        "evaluates_limit": session.evaluates_limit,
        "evaluates_remaining": session.evaluates_limit - used,
        "usage_warning": used >= warn_threshold,
        "upgrade_url": get_settings().sandbox_copilot_pack_intake_url,
    }


async def sandbox_factory_demo(token: str, factory_id: str) -> dict[str, object]:
    if factory_id not in _FACTORY_DEMO_IDS:
        raise HTTPException(status_code=400, detail=f"Unknown sandbox factory demo: {factory_id}")
    session = await get_sandbox_session(token)
    if factory_id in session.factory_demos_run:
        return {
            "factory_id": factory_id,
            "status": "already_run",
            "mode": session.mode,
            "tenant_id": session.tenant_id,
        }
    demos = list(session.factory_demos_run) + [factory_id]
    session = _replace(session, factory_demos_run=demos, trial_step=max(session.trial_step, 3))
    await _save_session(session)
    return {
        "factory_id": factory_id,
        "status": "demo_complete",
        "mode": session.mode,
        "tenant_id": session.tenant_id,
        "observe_only": True,
        "message": f"Sandbox observe-mode orientation for {factory_id} — production enforce/HITL requires paid pack.",
    }


def build_board_export_pdf(session: SandboxSession) -> bytes:
    rid = session.last_rid or "RID-SANDBOX-PENDING"
    lines = [
        "SANDBOX ORIENTATION — NOT FOR BOARD FILING",
        f"Tenant: {session.tenant_id}",
        f"Organization: {session.org}",
        f"Request ID: {rid}",
        f"Mode: {session.mode} (free sandbox — enforce requires Copilot Readiness Pack)",
        f"Evaluates: {session.evaluates_used}/{session.evaluates_limit}",
        "Decision: allow (mock M365 metadata · observe-only)",
        "Upgrade: Copilot Readiness Pack or Trust Brief for production board PDF.",
        f"Generated: {session.expires_at}",
    ]
    return minimal_pdf(lines, title="Noetfield Board Pack — Sandbox Watermark")


def sandbox_health() -> dict[str, object]:
    settings = get_settings()
    return {
        "enabled": settings.sandbox_enabled,
        "mode": SANDBOX_MODE,
        "evaluate_limit": settings.sandbox_evaluate_limit,
        "trial_days": settings.sandbox_trial_days,
        "redis_backed": redis_runtime.is_enabled(),
        "factory_demo_ids": list(_FACTORY_DEMO_IDS),
        "upgrade_url": settings.sandbox_copilot_pack_intake_url,
    }


def _iso(ts: float) -> str:
    from datetime import datetime, timezone

    return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()


def _is_expired(session: SandboxSession) -> bool:
    try:
        from datetime import datetime

        exp = datetime.fromisoformat(session.expires_at.replace("Z", "+00:00"))
        return exp.timestamp() < time.time()
    except ValueError:
        return False


def _replace(session: SandboxSession, **kwargs: object) -> SandboxSession:
    data = session.to_dict()
    data.update(kwargs)
    return SandboxSession.from_dict(data)


def email_hash(email: str) -> str:
    return hashlib.sha256(email.encode()).hexdigest()[:16]
