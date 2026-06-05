"""Trust Ledger v1 pilot API — evidence, connectors, TLE lifecycle."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from typing import Literal, Protocol
from uuid import uuid4

import asyncpg
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import Response
from pydantic import BaseModel, ConfigDict, Field

from noetfield_governance.governance_pilot_limits import check_governance_pilot_rate_limit
from noetfield_governance.pilot_auth import PilotAuthContext, require_pilot_auth
from noetfield_governance.trust_ledger_pdf import minimal_pdf

router = APIRouter(prefix="/api/v1", tags=["trust-ledger-v1"])

TerminalStatus = Literal["Approved", "Rejected", "Conditional"]
ACTIVE_TLE_STATUSES = ("Draft", "PendingApproval")
TRUSTED_EVIDENCE_SOURCES = frozenset({"Purview", "EntraID", "AuditLog", "SharePoint"})
KNOWN_TEMPLATE_BONUS = {"copilot-go-no-go-v1": 0.10}
CONFIDENCE_METHOD = "deterministic-v0"


def compute_confidence_score(
    evidence_rows: list[dict[str, object]],
    template_id: str,
) -> tuple[float, list[dict[str, object]]]:
    """Deterministic v0 score from evidence refs and template (auditable factors)."""
    count = len(evidence_rows)
    sources = {str(row.get("source", "")) for row in evidence_rows}
    trusted = sources & TRUSTED_EVIDENCE_SOURCES
    hashes_ok = count > 0 and all(
        isinstance(row.get("metadata"), dict) and bool((row["metadata"] or {}).get("hash"))
        for row in evidence_rows
    )

    factors: list[dict[str, object]] = []
    score = 0.40

    evidence_contrib = min(0.30, count * 0.10)
    factors.append(
        {
            "factor": "evidence_coverage",
            "contribution": round(evidence_contrib, 4),
            "detail": f"{count} evidence ref(s)",
        }
    )
    score += evidence_contrib

    diversity_contrib = min(0.15, len(trusted) * 0.05)
    factors.append(
        {
            "factor": "source_diversity",
            "contribution": round(diversity_contrib, 4),
            "detail": ", ".join(sorted(trusted)) if trusted else "no trusted M365 sources",
        }
    )
    score += diversity_contrib

    template_contrib = KNOWN_TEMPLATE_BONUS.get(template_id, 0.0)
    if template_contrib:
        factors.append(
            {
                "factor": "template_match",
                "contribution": template_contrib,
                "detail": template_id,
            }
        )
        score += template_contrib

    hash_contrib = 0.05 if hashes_ok else 0.0
    factors.append(
        {
            "factor": "hash_integrity",
            "contribution": hash_contrib,
            "detail": "all evidence hashes present" if hash_contrib else "missing hash metadata",
        }
    )
    score += hash_contrib

    return round(min(1.0, max(0.0, score)), 2), factors


def _attach_confidence(body: dict[str, object]) -> dict[str, object]:
    evidence = body.get("evidence") or []
    rows = [row for row in evidence if isinstance(row, dict)] if isinstance(evidence, list) else []
    template_id = str(body.get("template_id") or "")
    score, factors = compute_confidence_score(rows, template_id)
    body["confidence_score"] = score
    body["confidence_factors"] = factors
    body["confidence_method"] = CONFIDENCE_METHOD
    return body


def required_approvals() -> int:
    raw = os.environ.get("TLE_REQUIRED_APPROVALS", "2")
    try:
        return max(1, int(raw))
    except ValueError:
        return 2


class EvidenceIngestRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    evidence_id: str = Field(min_length=1, max_length=128)
    source: str = Field(min_length=1, max_length=64)
    title: str = Field(min_length=1, max_length=512)
    hash: str = Field(min_length=8, max_length=256)
    link: str | None = None
    sensitivity: str | None = None
    ingest_mode: Literal["metadata_only", "full_capture"] = "metadata_only"


class EvidenceObject(BaseModel):
    model_config = ConfigDict(extra="forbid")

    evidence_id: str
    source: str
    title: str
    hash: str
    ingested_at: datetime
    link: str | None = None
    sensitivity: str | None = None
    ingest_mode: str = "metadata_only"


class ConnectorRegisterRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    connector_id: str = Field(min_length=1, max_length=128)
    type: str = Field(min_length=1, max_length=64)
    required_scopes: list[str] = Field(default_factory=list)
    ingest_mode: Literal["metadata_only", "full_capture"] = "metadata_only"


class ConnectorObject(BaseModel):
    model_config = ConfigDict(extra="forbid")

    connector_id: str
    type: str
    required_scopes: list[str]
    ingest_mode: str
    status: str
    registered_at: datetime
    last_sync: datetime | None = None


class ConnectorSyncRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["active", "error"] = "active"
    records_synced: int = Field(default=0, ge=0)


class TleDraftRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    template_id: str = Field(min_length=1, max_length=64)
    evidence_ids: list[str] = Field(min_length=1)
    owner_id: str | None = None
    decision: str | None = None
    date: str | None = None


class TleApproveRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    approver_id: str = Field(min_length=1, max_length=128)
    status: TerminalStatus
    signature_hash: str = Field(min_length=8, max_length=256)
    key_id: str = Field(min_length=1, max_length=128)


class TrustLedgerEntry(BaseModel):
    model_config = ConfigDict(extra="allow")

    tle_id: str
    status: str
    decision: str | None = None
    date: str | None = None
    owner: dict[str, object] | None = None
    evidence: list[dict[str, object]] = Field(default_factory=list)
    template_id: str | None = None
    approval_chain: list[dict[str, object]] = Field(default_factory=list)
    signatures: list[dict[str, object]] = Field(default_factory=list)


class TleListResponse(BaseModel):
    items: list[TrustLedgerEntry]
    count: int


class EvidenceListResponse(BaseModel):
    items: list[EvidenceObject]
    count: int


@dataclass
class TleRecord:
    tle_id: str
    status: str
    body: dict[str, object]
    immutable: bool = False
    approved_at: datetime | None = None
    created_at: datetime | None = None


def _initial_tle_status() -> str:
    return "PendingApproval" if required_approvals() > 1 else "Draft"


def _apply_approval(record: TleRecord, request: TleApproveRequest) -> TleRecord:
    if record.immutable:
        raise HTTPException(status_code=409, detail="TLE is immutable after approval")
    if record.status not in ACTIVE_TLE_STATUSES:
        raise HTTPException(status_code=409, detail="TLE is not awaiting approval")

    body = dict(record.body)
    chain = list(body.get("approval_chain") or [])
    chain.append(
        {
            "approver": {"id": request.approver_id, "role": "Approver"},
            "status": request.status,
            "signed_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        }
    )
    body["approval_chain"] = chain
    signatures = list(body.get("signatures") or [])
    signatures.append(
        {
            "signer_id": request.approver_id,
            "signature_hash": request.signature_hash,
            "key_id": request.key_id,
        }
    )
    body["signatures"] = signatures

    needed = required_approvals()
    if len(chain) < needed:
        record.status = "PendingApproval"
        body["status"] = "PendingApproval"
        record.immutable = False
    else:
        record.status = request.status
        body["status"] = request.status
        record.immutable = True
        record.approved_at = datetime.now(timezone.utc)

    record.body = body
    return record


class TrustLedgerStore(Protocol):
    async def ingest_evidence(self, payload: EvidenceIngestRequest) -> EvidenceObject:
        ...

    async def get_evidence(self, evidence_id: str) -> EvidenceObject | None:
        ...

    async def list_evidence(self, limit: int) -> list[EvidenceObject]:
        ...

    async def register_connector(self, payload: ConnectorRegisterRequest) -> ConnectorObject:
        ...

    async def get_connector(self, connector_id: str) -> ConnectorObject | None:
        ...

    async def sync_connector(self, connector_id: str, payload: ConnectorSyncRequest) -> ConnectorObject:
        ...

    async def create_draft(self, request: TleDraftRequest) -> TleRecord:
        ...

    async def get_tle(self, tle_id: str) -> TleRecord | None:
        ...

    async def list_tles(self, status: str | None, limit: int) -> list[TleRecord]:
        ...

    async def approve_tle(self, tle_id: str, request: TleApproveRequest) -> TleRecord:
        ...


@dataclass
class InMemoryTrustLedgerStore:
    evidence: dict[str, EvidenceObject] = field(default_factory=dict)
    connectors: dict[str, ConnectorObject] = field(default_factory=dict)
    tles: dict[str, TleRecord] = field(default_factory=dict)

    async def ingest_evidence(self, payload: EvidenceIngestRequest) -> EvidenceObject:
        now = datetime.now(timezone.utc)
        obj = EvidenceObject(
            evidence_id=payload.evidence_id,
            source=payload.source,
            title=payload.title,
            hash=payload.hash,
            ingested_at=now,
            link=payload.link,
            sensitivity=payload.sensitivity,
            ingest_mode=payload.ingest_mode,
        )
        self.evidence[payload.evidence_id] = obj
        return obj

    async def get_evidence(self, evidence_id: str) -> EvidenceObject | None:
        return self.evidence.get(evidence_id)

    async def list_evidence(self, limit: int) -> list[EvidenceObject]:
        rows = sorted(self.evidence.values(), key=lambda e: e.ingested_at, reverse=True)
        return rows[:limit]

    async def register_connector(self, payload: ConnectorRegisterRequest) -> ConnectorObject:
        now = datetime.now(timezone.utc)
        obj = ConnectorObject(
            connector_id=payload.connector_id,
            type=payload.type,
            required_scopes=list(payload.required_scopes),
            ingest_mode=payload.ingest_mode,
            status="registered",
            registered_at=now,
            last_sync=None,
        )
        self.connectors[payload.connector_id] = obj
        return obj

    async def get_connector(self, connector_id: str) -> ConnectorObject | None:
        return self.connectors.get(connector_id)

    async def sync_connector(self, connector_id: str, payload: ConnectorSyncRequest) -> ConnectorObject:
        obj = self.connectors.get(connector_id)
        if obj is None:
            raise HTTPException(status_code=404, detail="Connector not found")
        now = datetime.now(timezone.utc)
        updated = ConnectorObject(
            connector_id=obj.connector_id,
            type=obj.type,
            required_scopes=obj.required_scopes,
            ingest_mode=obj.ingest_mode,
            status=payload.status,
            registered_at=obj.registered_at,
            last_sync=now,
        )
        self.connectors[connector_id] = updated
        return updated

    async def create_draft(self, request: TleDraftRequest) -> TleRecord:
        missing = [eid for eid in request.evidence_ids if eid not in self.evidence]
        if missing:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown evidence_id(s): {', '.join(missing)}",
            )
        evidence_rows = []
        for eid in request.evidence_ids:
            ev = self.evidence[eid]
            evidence_rows.append(
                {
                    "evidence_id": ev.evidence_id,
                    "source": ev.source,
                    "title": ev.title,
                    "metadata": {"hash": ev.hash},
                }
            )
        tle_id = f"tle-{date.today().isoformat()}-{uuid4().hex[:8]}"
        initial = _initial_tle_status()
        owner = {"id": request.owner_id or "owner-unset", "name": "Draft Owner", "role": "Owner"}
        body: dict[str, object] = {
            "tle_id": tle_id,
            "status": initial,
            "template_id": request.template_id,
            "decision": request.decision or "Draft decision pending",
            "date": request.date or date.today().isoformat(),
            "owner": owner,
            "evidence": evidence_rows,
            "approval_chain": [],
            "signatures": [],
        }
        _attach_confidence(body)
        now = datetime.now(timezone.utc)
        record = TleRecord(tle_id=tle_id, status=initial, body=body, created_at=now)
        self.tles[tle_id] = record
        return record

    async def get_tle(self, tle_id: str) -> TleRecord | None:
        return self.tles.get(tle_id)

    async def list_tles(self, status: str | None, limit: int) -> list[TleRecord]:
        rows = list(self.tles.values())
        if status:
            rows = [r for r in rows if r.status == status]
        rows.sort(key=lambda r: r.created_at or datetime.min.replace(tzinfo=timezone.utc), reverse=True)
        return rows[:limit]

    async def approve_tle(self, tle_id: str, request: TleApproveRequest) -> TleRecord:
        record = self.tles.get(tle_id)
        if record is None:
            raise HTTPException(status_code=404, detail="TLE not found")
        updated = _apply_approval(record, request)
        self.tles[tle_id] = updated
        return updated


class PostgresTrustLedgerStore:
    def __init__(self, database_url: str) -> None:
        self._database_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
        self._pool: asyncpg.Pool | None = None

    async def connect(self) -> None:
        if self._pool is None:
            self._pool = await asyncpg.create_pool(self._database_url)

    async def ingest_evidence(self, payload: EvidenceIngestRequest) -> EvidenceObject:
        await self.connect()
        assert self._pool is not None
        now = datetime.now(timezone.utc)
        async with self._pool.acquire() as conn:
            await conn.execute(
                """
                insert into noetfield.trust_ledger_evidence (
                  evidence_id, source, title, hash, link, sensitivity, ingest_mode, ingested_at
                ) values ($1, $2, $3, $4, $5, $6, $7, $8)
                on conflict (evidence_id) do update set
                  source = excluded.source,
                  title = excluded.title,
                  hash = excluded.hash,
                  link = excluded.link,
                  sensitivity = excluded.sensitivity,
                  ingest_mode = excluded.ingest_mode
                """,
                payload.evidence_id,
                payload.source,
                payload.title,
                payload.hash,
                payload.link,
                payload.sensitivity,
                payload.ingest_mode,
                now,
            )
        return EvidenceObject(
            evidence_id=payload.evidence_id,
            source=payload.source,
            title=payload.title,
            hash=payload.hash,
            ingested_at=now,
            link=payload.link,
            sensitivity=payload.sensitivity,
            ingest_mode=payload.ingest_mode,
        )

    async def get_evidence(self, evidence_id: str) -> EvidenceObject | None:
        await self.connect()
        assert self._pool is not None
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                select evidence_id, source, title, hash, link, sensitivity, ingest_mode, ingested_at
                from noetfield.trust_ledger_evidence where evidence_id = $1
                """,
                evidence_id,
            )
        if row is None:
            return None
        return EvidenceObject(**dict(row))

    async def list_evidence(self, limit: int) -> list[EvidenceObject]:
        await self.connect()
        assert self._pool is not None
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(
                """
                select evidence_id, source, title, hash, link, sensitivity, ingest_mode, ingested_at
                from noetfield.trust_ledger_evidence
                order by ingested_at desc
                limit $1
                """,
                limit,
            )
        return [EvidenceObject(**dict(r)) for r in rows]

    async def register_connector(self, payload: ConnectorRegisterRequest) -> ConnectorObject:
        await self.connect()
        assert self._pool is not None
        now = datetime.now(timezone.utc)
        async with self._pool.acquire() as conn:
            await conn.execute(
                """
                insert into noetfield.trust_ledger_connectors (
                  connector_id, type, required_scopes, ingest_mode, status, registered_at
                ) values ($1, $2, $3, $4, 'registered', $5)
                on conflict (connector_id) do update set
                  type = excluded.type,
                  required_scopes = excluded.required_scopes,
                  ingest_mode = excluded.ingest_mode
                """,
                payload.connector_id,
                payload.type,
                payload.required_scopes,
                payload.ingest_mode,
                now,
            )
        return ConnectorObject(
            connector_id=payload.connector_id,
            type=payload.type,
            required_scopes=list(payload.required_scopes),
            ingest_mode=payload.ingest_mode,
            status="registered",
            registered_at=now,
        )

    async def get_connector(self, connector_id: str) -> ConnectorObject | None:
        await self.connect()
        assert self._pool is not None
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                select connector_id, type, required_scopes, ingest_mode, status, registered_at, last_sync
                from noetfield.trust_ledger_connectors where connector_id = $1
                """,
                connector_id,
            )
        if row is None:
            return None
        return ConnectorObject(**dict(row))

    async def sync_connector(self, connector_id: str, payload: ConnectorSyncRequest) -> ConnectorObject:
        existing = await self.get_connector(connector_id)
        if existing is None:
            raise HTTPException(status_code=404, detail="Connector not found")
        now = datetime.now(timezone.utc)
        await self.connect()
        assert self._pool is not None
        async with self._pool.acquire() as conn:
            await conn.execute(
                """
                update noetfield.trust_ledger_connectors
                set last_sync = $2, status = $3
                where connector_id = $1
                """,
                connector_id,
                now,
                payload.status,
            )
        return ConnectorObject(
            connector_id=existing.connector_id,
            type=existing.type,
            required_scopes=existing.required_scopes,
            ingest_mode=existing.ingest_mode,
            status=payload.status,
            registered_at=existing.registered_at,
            last_sync=now,
        )

    async def create_draft(self, request: TleDraftRequest) -> TleRecord:
        evidence_rows: list[dict[str, object]] = []
        for eid in request.evidence_ids:
            ev = await self.get_evidence(eid)
            if ev is None:
                raise HTTPException(status_code=400, detail=f"Unknown evidence_id: {eid}")
            evidence_rows.append(
                {
                    "evidence_id": ev.evidence_id,
                    "source": ev.source,
                    "title": ev.title,
                    "metadata": {"hash": ev.hash},
                }
            )
        tle_id = f"tle-{date.today().isoformat()}-{uuid4().hex[:8]}"
        initial = _initial_tle_status()
        owner = {"id": request.owner_id or "owner-unset", "name": "Draft Owner", "role": "Owner"}
        body: dict[str, object] = {
            "tle_id": tle_id,
            "status": initial,
            "template_id": request.template_id,
            "decision": request.decision or "Draft decision pending",
            "date": request.date or date.today().isoformat(),
            "owner": owner,
            "evidence": evidence_rows,
            "approval_chain": [],
            "signatures": [],
        }
        _attach_confidence(body)
        await self.connect()
        assert self._pool is not None
        async with self._pool.acquire() as conn:
            await conn.execute(
                """
                insert into noetfield.tle_entries (tle_id, status, body)
                values ($1, $2, $3::jsonb)
                """,
                tle_id,
                initial,
                json.dumps(body, default=str),
            )
        return TleRecord(tle_id=tle_id, status=initial, body=body, created_at=datetime.now(timezone.utc))

    async def get_tle(self, tle_id: str) -> TleRecord | None:
        await self.connect()
        assert self._pool is not None
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                select tle_id, status, body, immutable, approved_at, created_at
                from noetfield.tle_entries where tle_id = $1
                """,
                tle_id,
            )
        if row is None:
            return None
        body = row["body"]
        if isinstance(body, str):
            body = json.loads(body)
        return TleRecord(
            tle_id=row["tle_id"],
            status=row["status"],
            body=body,
            immutable=row["immutable"],
            approved_at=row["approved_at"],
            created_at=row.get("created_at"),
        )

    async def list_tles(self, status: str | None, limit: int) -> list[TleRecord]:
        await self.connect()
        assert self._pool is not None
        async with self._pool.acquire() as conn:
            if status:
                rows = await conn.fetch(
                    """
                    select tle_id, status, body, immutable, approved_at, created_at
                    from noetfield.tle_entries
                    where status = $1
                    order by created_at desc
                    limit $2
                    """,
                    status,
                    limit,
                )
            else:
                rows = await conn.fetch(
                    """
                    select tle_id, status, body, immutable, approved_at, created_at
                    from noetfield.tle_entries
                    order by created_at desc
                    limit $1
                    """,
                    limit,
                )
        out: list[TleRecord] = []
        for row in rows:
            body = row["body"]
            if isinstance(body, str):
                body = json.loads(body)
            out.append(
                TleRecord(
                    tle_id=row["tle_id"],
                    status=row["status"],
                    body=body,
                    immutable=row["immutable"],
                    approved_at=row["approved_at"],
                    created_at=row.get("created_at"),
                )
            )
        return out

    async def approve_tle(self, tle_id: str, request: TleApproveRequest) -> TleRecord:
        record = await self.get_tle(tle_id)
        if record is None:
            raise HTTPException(status_code=404, detail="TLE not found")
        updated = _apply_approval(record, request)
        await self.connect()
        assert self._pool is not None
        async with self._pool.acquire() as conn:
            await conn.execute(
                """
                update noetfield.tle_entries
                set status = $2, body = $3::jsonb, immutable = $4, approved_at = $5
                where tle_id = $1 and immutable = false
                """,
                tle_id,
                updated.status,
                json.dumps(updated.body, default=str),
                updated.immutable,
                updated.approved_at,
            )
        return updated


@dataclass
class TrustLedgerDeps:
    store: TrustLedgerStore


def get_trust_ledger_deps(request: Request) -> TrustLedgerDeps:
    deps = getattr(request.app.state, "trust_ledger_deps", None)
    if deps is None:
        raise HTTPException(status_code=503, detail="Trust Ledger dependencies not initialized")
    return deps


def _record_to_entry(record: TleRecord) -> TrustLedgerEntry:
    body = dict(record.body)
    if "confidence_score" not in body:
        _attach_confidence(body)
    return TrustLedgerEntry.model_validate(body)


def _export_lines(record: TleRecord) -> list[str]:
    body = record.body
    lines = [
        f"TLE ID: {record.tle_id}",
        f"Status: {record.status}",
        f"Decision: {body.get('decision', '')}",
        f"Confidence: {body.get('confidence_score', 'n/a')}",
    ]
    evidence = body.get("evidence") or []
    if isinstance(evidence, list):
        for item in evidence:
            if isinstance(item, dict):
                lines.append(f"Evidence: {item.get('evidence_id', '')} — {item.get('title', '')}")
    chain = body.get("approval_chain") or []
    if isinstance(chain, list):
        for step in chain:
            if isinstance(step, dict):
                approver = step.get("approver") or {}
                if isinstance(approver, dict):
                    lines.append(f"Approver: {approver.get('id', '')} — {step.get('status', '')}")
    return lines


@router.post("/connectors", status_code=201)
async def register_connector(
    payload: ConnectorRegisterRequest,
    request: Request,
    auth: PilotAuthContext = Depends(require_pilot_auth),
    deps: TrustLedgerDeps = Depends(get_trust_ledger_deps),
) -> ConnectorObject:
    await check_governance_pilot_rate_limit(auth, request.url.path)
    return await deps.store.register_connector(payload)


@router.get("/connectors/{connector_id}")
async def get_connector(
    connector_id: str,
    auth: PilotAuthContext = Depends(require_pilot_auth),
    deps: TrustLedgerDeps = Depends(get_trust_ledger_deps),
) -> ConnectorObject:
    row = await deps.store.get_connector(connector_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Connector not found")
    return row


@router.post("/connectors/{connector_id}/sync")
async def sync_connector(
    connector_id: str,
    payload: ConnectorSyncRequest,
    request: Request,
    auth: PilotAuthContext = Depends(require_pilot_auth),
    deps: TrustLedgerDeps = Depends(get_trust_ledger_deps),
) -> ConnectorObject:
    await check_governance_pilot_rate_limit(auth, request.url.path)
    return await deps.store.sync_connector(connector_id, payload)


@router.post("/evidence/ingest", status_code=201)
async def ingest_evidence(
    payload: EvidenceIngestRequest,
    request: Request,
    auth: PilotAuthContext = Depends(require_pilot_auth),
    deps: TrustLedgerDeps = Depends(get_trust_ledger_deps),
) -> EvidenceObject:
    await check_governance_pilot_rate_limit(auth, request.url.path)
    return await deps.store.ingest_evidence(payload)


@router.get("/evidence")
async def list_evidence(
    limit: int = Query(default=50, ge=1, le=200),
    auth: PilotAuthContext = Depends(require_pilot_auth),
    deps: TrustLedgerDeps = Depends(get_trust_ledger_deps),
) -> EvidenceListResponse:
    items = await deps.store.list_evidence(limit)
    return EvidenceListResponse(items=items, count=len(items))


@router.get("/evidence/{evidence_id}")
async def get_evidence(
    evidence_id: str,
    auth: PilotAuthContext = Depends(require_pilot_auth),
    deps: TrustLedgerDeps = Depends(get_trust_ledger_deps),
) -> EvidenceObject:
    row = await deps.store.get_evidence(evidence_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Evidence not found")
    return row


@router.get("/tle")
async def list_tles(
    status: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    auth: PilotAuthContext = Depends(require_pilot_auth),
    deps: TrustLedgerDeps = Depends(get_trust_ledger_deps),
) -> TleListResponse:
    records = await deps.store.list_tles(status, limit)
    items = [_record_to_entry(r) for r in records]
    return TleListResponse(items=items, count=len(items))


@router.post("/tle/draft", status_code=201)
async def create_tle_draft(
    payload: TleDraftRequest,
    request: Request,
    auth: PilotAuthContext = Depends(require_pilot_auth),
    deps: TrustLedgerDeps = Depends(get_trust_ledger_deps),
) -> TrustLedgerEntry:
    await check_governance_pilot_rate_limit(auth, request.url.path)
    record = await deps.store.create_draft(payload)
    return _record_to_entry(record)


@router.get("/tle/{tle_id}/export")
async def export_tle(
    tle_id: str,
    auth: PilotAuthContext = Depends(require_pilot_auth),
    deps: TrustLedgerDeps = Depends(get_trust_ledger_deps),
) -> Response:
    record = await deps.store.get_tle(tle_id)
    if record is None:
        raise HTTPException(status_code=404, detail="TLE not found")
    if not record.immutable:
        raise HTTPException(status_code=409, detail="TLE must be fully approved before export")
    pdf = minimal_pdf(_export_lines(record), title=f"Trust Ledger — {tle_id}")
    return Response(content=pdf, media_type="application/pdf")


@router.get("/tle/{tle_id}")
async def get_tle(
    tle_id: str,
    auth: PilotAuthContext = Depends(require_pilot_auth),
    deps: TrustLedgerDeps = Depends(get_trust_ledger_deps),
) -> TrustLedgerEntry:
    record = await deps.store.get_tle(tle_id)
    if record is None:
        raise HTTPException(status_code=404, detail="TLE not found")
    return _record_to_entry(record)


@router.post("/tle/{tle_id}/approve")
async def approve_tle_route(
    tle_id: str,
    payload: TleApproveRequest,
    request: Request,
    auth: PilotAuthContext = Depends(require_pilot_auth),
    deps: TrustLedgerDeps = Depends(get_trust_ledger_deps),
) -> TrustLedgerEntry:
    await check_governance_pilot_rate_limit(auth, request.url.path)
    record = await deps.store.approve_tle(tle_id, payload)
    return _record_to_entry(record)
