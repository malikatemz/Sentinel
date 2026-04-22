insert into orgs (clerk_org_id, name, plan)
values ('org_beta_demo', 'Sentinel Beta Org', 'pro')
on conflict (clerk_org_id) do nothing;

with target_org as (
  select id from orgs where clerk_org_id = 'org_beta_demo'
)
insert into endpoints (org_id, name, framework, url, environment)
select id, 'auth-service', 'fastapi', 'https://api.sentinel.local/auth', 'prod'
from target_org
on conflict do nothing;

with target_org as (
  select id from orgs where clerk_org_id = 'org_beta_demo'
),
target_endpoint as (
  select e.id as endpoint_id, o.id as org_id
  from endpoints e
  join target_org o on e.org_id = o.id
  where e.name = 'auth-service'
  limit 1
)
insert into alerts (org_id, endpoint_id, severity, type, title, description, remediation, source)
select
  org_id,
  endpoint_id,
  'critical',
  'credential',
  'Potential API key leak detected',
  'A high-confidence secret pattern was detected during beta seeding.',
  'Rotate the key and remove it from exposed history.',
  '{"provider":"seed","kind":"demo"}'::jsonb
from target_endpoint;
