create extension if not exists pgcrypto;

create table if not exists orgs (
  id uuid primary key default gen_random_uuid(),
  clerk_org_id text unique not null,
  name text not null,
  plan text not null default 'starter',
  stripe_customer_id text,
  created_at timestamptz not null default now()
);

create table if not exists api_tokens (
  id uuid primary key default gen_random_uuid(),
  org_id uuid not null references orgs(id) on delete cascade,
  name text not null,
  token_hash text not null,
  environment text not null default 'prod',
  last_used_at timestamptz,
  created_at timestamptz not null default now()
);

create table if not exists endpoints (
  id uuid primary key default gen_random_uuid(),
  org_id uuid not null references orgs(id) on delete cascade,
  name text not null,
  framework text not null,
  url text not null,
  environment text not null default 'prod',
  active boolean not null default true,
  created_at timestamptz not null default now()
);

create table if not exists events (
  id uuid primary key default gen_random_uuid(),
  org_id uuid not null references orgs(id) on delete cascade,
  endpoint_id uuid not null references endpoints(id) on delete cascade,
  method text not null,
  path text not null,
  status_code int not null,
  latency_ms int not null,
  ip text,
  user_agent text,
  anomaly_score double precision not null default 0,
  environment text not null default 'prod',
  created_at timestamptz not null default now()
);

create table if not exists baseline_snapshots (
  id uuid primary key default gen_random_uuid(),
  org_id uuid not null references orgs(id) on delete cascade,
  endpoint_id uuid not null references endpoints(id) on delete cascade,
  request_rate double precision not null default 0,
  error_rate double precision not null default 0,
  latency_p95 double precision not null default 0,
  top_ip_clusters jsonb not null default '[]'::jsonb,
  window_start timestamptz not null,
  window_end timestamptz not null,
  created_at timestamptz not null default now()
);

create table if not exists alerts (
  id uuid primary key default gen_random_uuid(),
  org_id uuid not null references orgs(id) on delete cascade,
  endpoint_id uuid references endpoints(id) on delete set null,
  severity text not null,
  type text not null,
  title text not null,
  description text,
  remediation text,
  source jsonb not null default '{}'::jsonb,
  resolved boolean not null default false,
  created_at timestamptz not null default now(),
  resolved_at timestamptz
);

create table if not exists scans (
  id uuid primary key default gen_random_uuid(),
  org_id uuid not null references orgs(id) on delete cascade,
  endpoint_id uuid references endpoints(id) on delete set null,
  target text not null,
  status text not null default 'queued',
  open_ports jsonb not null default '[]'::jsonb,
  risks jsonb not null default '[]'::jsonb,
  created_at timestamptz not null default now(),
  completed_at timestamptz
);

create table if not exists secret_findings (
  id uuid primary key default gen_random_uuid(),
  org_id uuid not null references orgs(id) on delete cascade,
  provider text not null default 'github',
  location text not null,
  secret_type text not null,
  confidence double precision not null default 0,
  status text not null default 'open',
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create table if not exists reports (
  id uuid primary key default gen_random_uuid(),
  org_id uuid not null references orgs(id) on delete cascade,
  type text not null,
  status text not null default 'queued',
  content text,
  evidence jsonb not null default '[]'::jsonb,
  created_at timestamptz not null default now(),
  completed_at timestamptz
);

create table if not exists integrations (
  id uuid primary key default gen_random_uuid(),
  org_id uuid not null references orgs(id) on delete cascade,
  kind text not null,
  enabled boolean not null default false,
  config jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists subscriptions (
  id uuid primary key default gen_random_uuid(),
  org_id uuid not null unique references orgs(id) on delete cascade,
  stripe_subscription_id text unique,
  plan text not null default 'starter',
  status text not null default 'trialing',
  billing_interval text not null default 'monthly',
  current_period_end timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists idx_api_tokens_org_id on api_tokens(org_id);
create index if not exists idx_endpoints_org_id on endpoints(org_id);
create index if not exists idx_events_org_endpoint_created_at on events(org_id, endpoint_id, created_at desc);
create index if not exists idx_alerts_org_resolved_created_at on alerts(org_id, resolved, created_at desc);
create index if not exists idx_scans_org_created_at on scans(org_id, created_at desc);
create index if not exists idx_secret_findings_org_created_at on secret_findings(org_id, created_at desc);
create index if not exists idx_reports_org_created_at on reports(org_id, created_at desc);
create index if not exists idx_integrations_org_kind on integrations(org_id, kind);
