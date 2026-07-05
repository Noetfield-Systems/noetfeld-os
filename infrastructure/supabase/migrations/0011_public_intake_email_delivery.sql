-- Resend archive email delivery status (webhook: email.delivered / email.bounced).

set search_path = noetfield, public;

alter table public_intakes
  add column if not exists email_archive_status text,
  add column if not exists email_archive_updated_at timestamptz,
  add column if not exists email_archive_detail text;

create index if not exists idx_public_intakes_email_archive_status
  on public_intakes (email_archive_status)
  where email_archive_status is not null;

comment on column public_intakes.email_archive_status is 'Resend archive lane: delivered | bounced';
comment on column public_intakes.email_archive_detail is 'Bounce reason or provider detail from Resend webhook';
