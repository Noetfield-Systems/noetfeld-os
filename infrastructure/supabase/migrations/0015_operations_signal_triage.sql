-- Signal Factory triage verdicts for operations inbox signals (Gmail sweep → rubric → Telegram).

set search_path = noetfield, public;

create table if not exists operations_signal_triage (
  signal_id uuid primary key references signals(id) on delete cascade,
  verdict text not null
    check (verdict in ('PROCEED', 'REQUIRE_HUMAN_REVIEW', 'REJECT')),
  route text not null,
  label text not null,
  risk_score integer not null default 0
    check (risk_score >= 0 and risk_score <= 100),
  rubric jsonb not null default '{}'::jsonb,
  telegram_message_id bigint,
  triaged_at timestamptz not null default now()
);

create index if not exists idx_operations_signal_triage_verdict_at
  on operations_signal_triage (verdict, triaged_at desc);

create index if not exists idx_operations_signal_triage_route
  on operations_signal_triage (route, triaged_at desc);

comment on table operations_signal_triage is
  'Signal Factory rubric verdicts for operations_inbox_email signals — Telegram notify on triage.';
