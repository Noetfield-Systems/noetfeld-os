"""Trust Ledger v1 pilot API — /api/v1/evidence/* and /api/v1/tle/*."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from typing import Literal, Protocol
from uuid import uuid4

import asyncpg
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, ConfigDict, Field

from noetfield_governance.governance_pilot_limits import check_governance_pilot_rate_limit
from noetfield_governance.pilot_auth import PilotAuthContext, require_pilot_auth

router = APIRouter(prefix="/api/v1", tags=["trust-ledger-v1"])

TerminalStatus = Literal["Approved", "Rejected", "Conditional"]


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


@dataclass
class TleRecord:
    tle_id: str
    status: str
    body: dict[str, object]
    immutable: bool = False
    approved_at: datetime | None = None


class TrustLedgerStore(Protocol):
    async def ingest_evidence(self, payload: EvidenceIngestRequest) -> EvidenceObject:
        ...

    async def get_evidence(self, evidence_id: str) -> EvidenceObject | None:
        ...

    async def create_draft(self, request: TleDraftRequest) -> TleRecord:
        ...

    async def get_tle(self, tle_id: str) -> TleRecord | None:
        ...

    async def approve_tle(self, tle_id: str, request: TleApproveRequest) -> TleRecord:
        ...


@dataclass
class InMemoryTrustLedgerStore:
    evidence: dict[str, EvidenceObject] = field(default_factory=dict)
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
        owner = {"id": request.owner_id or "owner-unset", "name": "Draft Owner", "role": "Owner"}
        body: dict[str, object] = {
            "tle_id": tle_id,
            "status": "Draft",
            "template_id": request.template_id,
            "decision": request.decision or "Draft decision pending",
            "date": request.date or date.today().isoformat(),
            "owner": owner,
            "evidence": evidence_rows,
            "approval_chain": [],
            "signatures": [],
        }
        record = TleRecord(tle_id=tle_id, status="Draft", body=body)
        self.tles[tle_id] = record
        return record

    async def get_tle(self, tle_id: str) -> TleRecord | None:
        return self.tles.get(tle_id)

    async def approve_tle(self, tle_id: str, request: TleApproveRequest) -> TleRecord:
        record = self.tles.get(tle_id)
        if record is None:
            raise HTTPException(status_code=404, detail="TLE not found")
        if record.immutable:
            raise HTTPException(status_code=409, detail="TLE is immutable after approval")
        if record.status != "Draft":
            raise HTTPException(status_code=409, detail="TLE is not in Draft status")
        body = dict(record.body)
        body["status"] = request.status
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
        record.body = body
        record.status = request.status
        record.immutable = True
        record.approved_at = datetime.now(timezone.utc)
        self.tles[tle_id] = record
        return record


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
        owner = {"id": request.owner_id or "owner-unset", "name": "Draft Owner", "role": "Owner"}
        body: dict[str, object] = {
            "tle_id": tle_id,
            "status": "Draft",
            "template_id": request.template_id,
            "decision": request.decision or "Draft decision pending",
            "date": request.date or date.today().isoformat(),
            "owner": owner,
            "evidence": evidence_rows,
            "approval_chain": [],
            "signatures": [],
        }
        await self.connect()
        assert self._pool is not None
        async with self._pool.acquire() as conn:
            await conn.execute(
                """
                insert into noetfield.tle_entries (tle_id, status, body)
                values ($1, 'Draft', $2::jsonb)
                """,
                tle_id,
                json.dumps(body, default=str),
            )
        return TleRecord(tle_id=tle_id, status="Draft", body=body)

    async def get_tle(self, tle_id: str) -> TleRecord | None:
        await self.connect()
        assert self._pool is not None
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(
                "select tle_id, status, body, immutable, approved_at from noetfield.tle_entries where tle_id = $1",
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
        )

    async def approve_tle(self, tle_id: str, request: TleApproveRequest) -> TleRecord:
        record = await self.get_tle(tle_id)
        if record is None:
            raise HTTPException(status_code=404, detail="TLE not found")
        if record.immutable:
            raise HTTPException(status_code=409, detail="TLE is immutable after approval")
        if record.status != "Draft":
            raise HTTPException(status_code=409, detail="TLE is not in Draft status")
        body = dict(record.body)
        body["status"] = request.status
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
        approved_at = datetime.now(timezone.utc)
        await self.connect()
        assert self._pool is not None
        async with self._pool.acquire() as conn:
            await conn.execute(
                """
                update noetfield.tle_entries
                set status = $2, body = $3::jsonb, immutable = true, approved_at = $4
                where tle_id = $1 and immutable = false and status = 'Draft'
                """,
                tle_id,
                request.status,
                json.dumps(body, default=str),
                approved_at,
            )
        return TleRecord(
            tle_id=tle_id,
            status=request.status,
            body=body,
            immutable=True,
            approved_at=approved_at,
        )


@dataclass
class TrustLedgerDeps:
    store: TrustLedgerStore


def get_trust_ledger_deps(request: Request) -> TrustLedgerDeps:
    deps = getattr(request.app.state, "trust_ledger_deps", None)
    if deps is None:
        raise HTTPException(status_code=503, detail="Trust Ledger dependencies not initialized")
    return deps


def _record_to_entry(record: TleRecord) -> TrustLedgerEntry:
    return TrustLedgerEntry.model_validate(record.body)


@router.post("/evidence/ingest", status_code=201)
async def ingest_evidence(
    payload: EvidenceIngestRequest,
    request: Request,
    auth: PilotAuthContext = Depends(require_pilot_auth),
    deps: TrustLedgerDeps = Depends(get_trust_ledger_deps),
) -> EvidenceObject:
    await check_governance_pilot_rate_limit(auth, request.url.path)
    return await deps.store.ingest_evidence(payload)


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
async def approve_tle(
    tle_id: str,
    payload: TleApproveRequest,
    request: Request,
    auth: PilotAuthContext = Depends(require_pilot_auth),
    deps: TrustLedgerDeps = Depends(get_trust_ledger_deps),
) -> TrustLedgerEntry:
    await check_governance_pilot_rate_limit(auth, request.url.path)
    record = await deps.store.approve_tle(tle_id, payload)
    return _record_to_entry(record)
