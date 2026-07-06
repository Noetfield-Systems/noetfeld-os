-- Seed operations inbox tenant/org for Gmail sweep + signal triage (idempotent).

set search_path = noetfield, public;

insert into organizations (id, name, legal_name, primary_domain)
values (
  '00000000-0000-4000-8000-000000000002',
  'Noetfield Operations',
  'Noetfield Systems',
  'noetfield.com'
)
on conflict (id) do nothing;

insert into tenants (id, organization_id, name, deployment_mode, data_region, status)
values (
  '00000000-0000-4000-8000-000000000001',
  '00000000-0000-4000-8000-000000000002',
  'operations-inbox',
  'saas',
  'default',
  'active'
)
on conflict (id) do nothing;
