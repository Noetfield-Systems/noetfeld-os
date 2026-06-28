"""First-party public analytics store and admin traction rollups."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

import asyncpg


@dataclass
class AnalyticsEvent:
    event_id: str
    event_name: str
    created_at: str
    request_id: str | None = None
    session_id: str | None = None
    page_path: str | None = None
    page_url: str | None = None
    referrer: str | None = None
    utm_source: str | None = None
    utm_medium: str | None = None
    utm_campaign: str | None = None
    component: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class InMemoryAnalyticsStore:
    def __init__(self) -> None:
        self._events: list[AnalyticsEvent] = []
        self._sessions: dict[str, dict[str, Any]] = {}
        self._conversions: list[dict[str, Any]] = []
        self._leads: dict[str, dict[str, Any]] = {}

    async def record(self, event: AnalyticsEvent) -> AnalyticsEvent:
        self._events.append(event)
        if event.session_id:
            self._sessions[event.session_id] = _session_payload(event)
        conversion_type = _conversion_type(event)
        lead_id = _lead_id(event)
        if conversion_type:
            self._conversions.append(_conversion_payload(event, conversion_type, lead_id))
        if lead_id:
            self._leads[lead_id] = _lead_payload(event, lead_id)
        return event

    async def recent(self, *, limit: int = 50) -> list[dict[str, Any]]:
        cap = max(1, min(limit, 100))
        return [_event_to_dict(event) for event in self._events[-cap:]][::-1]

    async def summary(self, *, days: int = 30) -> dict[str, Any]:
        del days
        events = [_event_to_dict(event) for event in self._events]
        return {
            "totals": {
                "events": len(events),
                "sessions": len(self._sessions),
                "conversions": len(self._conversions),
                "leads": len(self._leads),
                "form_submits": sum(1 for event in events if event["event_name"] == "form_submit"),
                "chat_messages": sum(1 for event in events if event["event_name"] == "chat_message_sent"),
                "cta_clicks": sum(1 for event in events if event["event_name"] == "cta_click"),
            },
            "funnel": _funnel(events, self._conversions, self._leads),
            "events_by_name": _count_dicts([event["event_name"] for event in events], "event_name"),
            "top_pages": _count_dicts([event["page_path"] for event in events if event["page_path"]], "page_path"),
            "source_pages": _count_dicts(
                [session.get("landing_page") for session in self._sessions.values() if session.get("landing_page")],
                "landing_page",
            ),
            "conversions_by_type": _count_dicts(
                [conversion["conversion_type"] for conversion in self._conversions],
                "conversion_type",
            ),
            "recent_leads": list(self._leads.values())[-50:][::-1],
            "recent_conversions": self._conversions[-50:][::-1],
            "recent_events": events[-100:][::-1],
        }


class PostgresAnalyticsStore:
    def __init__(self, database_url: str) -> None:
        self._database_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
        self._pool: asyncpg.Pool | None = None

    async def connect(self) -> None:
        if self._pool is None:
            self._pool = await asyncpg.create_pool(self._database_url)

    async def close(self) -> None:
        if self._pool is not None:
            await self._pool.close()
            self._pool = None

    async def record(self, event: AnalyticsEvent) -> AnalyticsEvent:
        await self.connect()
        assert self._pool is not None
        async with self._pool.acquire() as connection:
            async with connection.transaction():
                await connection.execute(
                    """
                    insert into noetfield.analytics_events (
                      event_id, event_name, request_id, session_id, page_path, page_url,
                      referrer, utm_source, utm_medium, utm_campaign, component, metadata
                    )
                    values ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12::jsonb)
                    """,
                    event.event_id,
                    event.event_name,
                    event.request_id,
                    event.session_id,
                    event.page_path,
                    event.page_url,
                    event.referrer,
                    event.utm_source,
                    event.utm_medium,
                    event.utm_campaign,
                    event.component,
                    json.dumps(event.metadata, default=str),
                )
                if event.session_id:
                    await _upsert_session(connection, event)
                conversion_type = _conversion_type(event)
                lead_id = _lead_id(event)
                if conversion_type:
                    await _insert_conversion(connection, event, conversion_type, lead_id)
                if lead_id:
                    await _upsert_lead(connection, event, lead_id)
        return event

    async def recent(self, *, limit: int = 50) -> list[dict[str, Any]]:
        await self.connect()
        assert self._pool is not None
        cap = max(1, min(limit, 100))
        async with self._pool.acquire() as connection:
            rows = await connection.fetch(
                """
                select event_id, event_name, created_at, request_id, session_id, page_path,
                       page_url, referrer, utm_source, utm_medium, utm_campaign, component, metadata
                from noetfield.analytics_events
                order by created_at desc
                limit $1
                """,
                cap,
            )
        return [_row_to_dict(row) for row in rows]

    async def summary(self, *, days: int = 30) -> dict[str, Any]:
        await self.connect()
        assert self._pool is not None
        window_days = max(1, min(days, 365))
        async with self._pool.acquire() as connection:
            totals = await connection.fetchrow(
                """
                select
                  (select count(*) from noetfield.analytics_events where created_at >= now() - ($1::int * interval '1 day')) as events,
                  (select count(*) from noetfield.visitor_sessions where last_seen_at >= now() - ($1::int * interval '1 day')) as sessions,
                  (select count(*) from noetfield.conversion_events where created_at >= now() - ($1::int * interval '1 day')) as conversions,
                  (select count(*) from noetfield.lead_profiles where last_seen_at >= now() - ($1::int * interval '1 day')) as leads,
                  (select count(*) from noetfield.analytics_events where event_name = 'form_submit' and created_at >= now() - ($1::int * interval '1 day')) as form_submits,
                  (select count(*) from noetfield.analytics_events where event_name = 'chat_message_sent' and created_at >= now() - ($1::int * interval '1 day')) as chat_messages,
                  (select count(*) from noetfield.analytics_events where event_name = 'cta_click' and created_at >= now() - ($1::int * interval '1 day')) as cta_clicks
                """,
                window_days,
            )
            events_by_name = await _group_count(connection, "analytics_events", "event_name", "created_at", window_days)
            top_pages = await _group_count(connection, "analytics_events", "coalesce(nullif(page_path, ''), '(unknown)')", "created_at", window_days, "page_path")
            source_pages = await _group_count(connection, "visitor_sessions", "coalesce(nullif(landing_page, ''), '(unknown)')", "last_seen_at", window_days, "landing_page")
            conversions_by_type = await _group_count(connection, "conversion_events", "conversion_type", "created_at", window_days)
            recent_leads = await connection.fetch(
                """
                select lead_id, primary_email, organization, contact_name, status, source_session_id,
                       first_request_id, latest_request_id, first_seen_at, last_seen_at, lead_score, tags, metadata
                from noetfield.lead_profiles
                order by last_seen_at desc
                limit 50
                """
            )
            recent_conversions = await connection.fetch(
                """
                select conversion_id, event_id, session_id, request_id, conversion_type, conversion_value,
                       currency, page_path, source_event_name, lead_id, metadata, created_at
                from noetfield.conversion_events
                order by created_at desc
                limit 50
                """
            )
            recent_events = await connection.fetch(
                """
                select event_id, event_name, created_at, request_id, session_id, page_path,
                       page_url, referrer, utm_source, utm_medium, utm_campaign, component, metadata
                from noetfield.analytics_events
                order by created_at desc
                limit 100
                """
            )
        plain_events = [_row_to_dict(row) for row in recent_events]
        plain_conversions = [_record_to_plain(row) for row in recent_conversions]
        plain_leads = [_record_to_plain(row) for row in recent_leads]
        return {
            "totals": {key: int(totals[key] or 0) for key in totals.keys()},
            "funnel": _funnel(plain_events, plain_conversions, {lead["lead_id"]: lead for lead in plain_leads}),
            "events_by_name": [_record_to_plain(row) for row in events_by_name],
            "top_pages": [_record_to_plain(row) for row in top_pages],
            "source_pages": [_record_to_plain(row) for row in source_pages],
            "conversions_by_type": [_record_to_plain(row) for row in conversions_by_type],
            "recent_leads": plain_leads,
            "recent_conversions": plain_conversions,
            "recent_events": plain_events,
        }


def build_analytics_event(
    *,
    event_name: str,
    request_id: str | None = None,
    session_id: str | None = None,
    page_path: str | None = None,
    page_url: str | None = None,
    referrer: str | None = None,
    utm_source: str | None = None,
    utm_medium: str | None = None,
    utm_campaign: str | None = None,
    component: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> AnalyticsEvent:
    return AnalyticsEvent(
        event_id="AE-" + uuid4().hex[:16].upper(),
        event_name=event_name.strip().lower(),
        created_at=datetime.now(UTC).isoformat(),
        request_id=(request_id or "").strip() or None,
        session_id=(session_id or "").strip() or None,
        page_path=(page_path or "").strip()[:512] or None,
        page_url=(page_url or "").strip()[:1000] or None,
        referrer=(referrer or "").strip()[:1000] or None,
        utm_source=(utm_source or "").strip()[:120] or None,
        utm_medium=(utm_medium or "").strip()[:120] or None,
        utm_campaign=(utm_campaign or "").strip()[:180] or None,
        component=(component or "").strip()[:160] or None,
        metadata=metadata or {},
    )


async def _group_count(connection: asyncpg.Connection, table: str, expr: str, time_col: str, days: int, alias: str | None = None) -> list[asyncpg.Record]:
    label = alias or expr
    return await connection.fetch(
        f"""
        select {expr} as {label}, count(*)::int as count
        from noetfield.{table}
        where {time_col} >= now() - ($1::int * interval '1 day')
        group by {expr}
        order by count desc, {label}
        limit 30
        """,
        days,
    )


def _row_to_dict(row: asyncpg.Record) -> dict[str, Any]:
    meta = row["metadata"]
    if isinstance(meta, str):
        meta = json.loads(meta)
    created = row["created_at"]
    return {
        "event_id": row["event_id"],
        "event_name": row["event_name"],
        "created_at": created.isoformat() if hasattr(created, "isoformat") else str(created),
        "request_id": row["request_id"],
        "session_id": row["session_id"],
        "page_path": row["page_path"],
        "page_url": row["page_url"],
        "referrer": row["referrer"],
        "utm_source": row["utm_source"],
        "utm_medium": row["utm_medium"],
        "utm_campaign": row["utm_campaign"],
        "component": row["component"],
        "metadata": dict(meta or {}),
    }


def _event_to_dict(event: AnalyticsEvent) -> dict[str, Any]:
    return {
        "event_id": event.event_id,
        "event_name": event.event_name,
        "created_at": event.created_at,
        "request_id": event.request_id,
        "session_id": event.session_id,
        "page_path": event.page_path,
        "page_url": event.page_url,
        "referrer": event.referrer,
        "utm_source": event.utm_source,
        "utm_medium": event.utm_medium,
        "utm_campaign": event.utm_campaign,
        "component": event.component,
        "metadata": event.metadata,
    }


def _record_to_plain(row: asyncpg.Record | dict[str, Any]) -> dict[str, Any]:
    source = row if isinstance(row, dict) else {key: row[key] for key in row.keys()}
    plain: dict[str, Any] = {}
    for key, value in source.items():
        if hasattr(value, "isoformat"):
            plain[key] = value.isoformat()
        elif key == "metadata":
            plain[key] = json.loads(value) if isinstance(value, str) else dict(value or {})
        else:
            plain[key] = value
    return plain


def _metadata_text(event: AnalyticsEvent, key: str) -> str | None:
    value = event.metadata.get(key)
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _lead_id(event: AnalyticsEvent) -> str | None:
    email = _metadata_text(event, "contact_email") or _metadata_text(event, "email")
    if email and "@" in email:
        return "LEAD-" + email.lower()
    if event.request_id and event.event_name in {"form_submit", "intake_submitted", "pilot_apply"}:
        return "LEAD-RID-" + event.request_id.upper()
    return None


def _conversion_type(event: AnalyticsEvent) -> str | None:
    if event.event_name in {"form_submit", "intake_submitted"}:
        return str(event.metadata.get("vector") or "form_submit")[:80]
    if event.event_name == "chat_message_sent":
        return "chat_engagement"
    if event.event_name == "cta_click":
        text = str(event.metadata.get("text") or event.metadata.get("href") or "").lower()
        if any(term in text for term in ("apply", "pilot", "intake", "demo", "pricing", "brief", "contact")):
            return "cta_click"
    return None


def _lead_score(event: AnalyticsEvent) -> int:
    if event.event_name in {"form_submit", "intake_submitted"}:
        return 70
    if event.event_name == "chat_message_sent":
        return 20
    if event.event_name == "cta_click":
        return 10
    return 1


def _session_payload(event: AnalyticsEvent) -> dict[str, Any]:
    return {
        "session_id": event.session_id,
        "request_id": event.request_id,
        "landing_page": event.page_path,
        "last_page": event.page_path,
        "referrer": event.referrer,
        "utm_source": event.utm_source,
        "utm_medium": event.utm_medium,
        "utm_campaign": event.utm_campaign,
        "user_agent": _metadata_text(event, "user_agent"),
        "metadata": event.metadata,
    }


def _conversion_payload(event: AnalyticsEvent, conversion_type: str, lead_id: str | None) -> dict[str, Any]:
    return {
        "conversion_id": "CV-" + uuid4().hex[:16].upper(),
        "event_id": event.event_id,
        "session_id": event.session_id,
        "request_id": event.request_id,
        "conversion_type": conversion_type,
        "page_path": event.page_path,
        "source_event_name": event.event_name,
        "lead_id": lead_id,
        "metadata": event.metadata,
    }


def _lead_payload(event: AnalyticsEvent, lead_id: str) -> dict[str, Any]:
    return {
        "lead_id": lead_id,
        "primary_email": _metadata_text(event, "contact_email") or _metadata_text(event, "email"),
        "organization": _metadata_text(event, "organization") or _metadata_text(event, "org"),
        "contact_name": _metadata_text(event, "contact_name") or _metadata_text(event, "name"),
        "source_session_id": event.session_id,
        "first_request_id": event.request_id,
        "latest_request_id": event.request_id,
        "lead_score": _lead_score(event),
        "metadata": event.metadata,
    }


def _funnel(events: list[dict[str, Any]], conversions: list[dict[str, Any]], leads: dict[str, Any]) -> list[dict[str, Any]]:
    page_views = sum(1 for event in events if event.get("event_name") == "page_view")
    cta_clicks = sum(1 for event in events if event.get("event_name") == "cta_click")
    form_steps = sum(1 for event in events if str(event.get("event_name", "")).startswith("form_step_"))
    form_submits = sum(1 for event in events if event.get("event_name") == "form_submit")
    return [
        {"stage": "Page views", "count": page_views or len(events)},
        {"stage": "CTA clicks", "count": cta_clicks},
        {"stage": "Form step activity", "count": form_steps},
        {"stage": "Form submits", "count": form_submits},
        {"stage": "Conversions", "count": len(conversions)},
        {"stage": "Leads", "count": len(leads)},
    ]


def _count_dicts(values: list[str | None], key: str) -> list[dict[str, Any]]:
    counts: dict[str, int] = {}
    for value in values:
        label = str(value or "(unknown)")
        counts[label] = counts.get(label, 0) + 1
    return [{key: label, "count": count} for label, count in sorted(counts.items(), key=lambda item: (-item[1], item[0]))]


async def _upsert_session(connection: asyncpg.Connection, event: AnalyticsEvent) -> None:
    await connection.execute(
        """
        insert into noetfield.visitor_sessions (
          session_id, request_id, landing_page, last_page, referrer,
          utm_source, utm_medium, utm_campaign, user_agent, metadata
        )
        values ($1, $2, $3, $3, $4, $5, $6, $7, $8, $9::jsonb)
        on conflict (session_id) do update set
          last_seen_at = now(),
          last_page = coalesce(excluded.last_page, noetfield.visitor_sessions.last_page),
          request_id = coalesce(noetfield.visitor_sessions.request_id, excluded.request_id),
          utm_source = coalesce(noetfield.visitor_sessions.utm_source, excluded.utm_source),
          utm_medium = coalesce(noetfield.visitor_sessions.utm_medium, excluded.utm_medium),
          utm_campaign = coalesce(noetfield.visitor_sessions.utm_campaign, excluded.utm_campaign),
          metadata = noetfield.visitor_sessions.metadata || excluded.metadata
        """,
        event.session_id,
        event.request_id,
        event.page_path,
        event.referrer,
        event.utm_source,
        event.utm_medium,
        event.utm_campaign,
        _metadata_text(event, "user_agent"),
        json.dumps(event.metadata, default=str),
    )


async def _insert_conversion(connection: asyncpg.Connection, event: AnalyticsEvent, conversion_type: str, lead_id: str | None) -> None:
    await connection.execute(
        """
        insert into noetfield.conversion_events (
          conversion_id, event_id, session_id, request_id, conversion_type,
          page_path, source_event_name, lead_id, metadata
        )
        values ($1, $2, $3, $4, $5, $6, $7, $8, $9::jsonb)
        """,
        "CV-" + uuid4().hex[:16].upper(),
        event.event_id,
        event.session_id,
        event.request_id,
        conversion_type,
        event.page_path,
        event.event_name,
        lead_id,
        json.dumps(event.metadata, default=str),
    )


async def _upsert_lead(connection: asyncpg.Connection, event: AnalyticsEvent, lead_id: str) -> None:
    payload = _lead_payload(event, lead_id)
    await connection.execute(
        """
        insert into noetfield.lead_profiles (
          lead_id, primary_email, organization, contact_name, source_session_id,
          first_request_id, latest_request_id, lead_score, metadata
        )
        values ($1, $2, $3, $4, $5, $6, $7, $8, $9::jsonb)
        on conflict (lead_id) do update set
          last_seen_at = now(),
          latest_request_id = coalesce(excluded.latest_request_id, noetfield.lead_profiles.latest_request_id),
          organization = coalesce(noetfield.lead_profiles.organization, excluded.organization),
          contact_name = coalesce(noetfield.lead_profiles.contact_name, excluded.contact_name),
          source_session_id = coalesce(noetfield.lead_profiles.source_session_id, excluded.source_session_id),
          lead_score = greatest(noetfield.lead_profiles.lead_score, excluded.lead_score),
          metadata = noetfield.lead_profiles.metadata || excluded.metadata
        """,
        payload["lead_id"],
        payload["primary_email"],
        payload["organization"],
        payload["contact_name"],
        payload["source_session_id"],
        payload["first_request_id"],
        payload["latest_request_id"],
        payload["lead_score"],
        json.dumps(payload["metadata"], default=str),
    )
