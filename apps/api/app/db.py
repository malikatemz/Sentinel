from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from .settings import settings


SCHEMA = """
create table if not exists api_tokens (
  id integer primary key autoincrement,
  org_key text not null,
  token_name text not null,
  token_hash text not null unique,
  created_at text not null default current_timestamp,
  last_used_at text
);

create table if not exists endpoints (
  id integer primary key autoincrement,
  org_token text not null,
  name text not null,
  environment text not null default 'prod',
  created_at text not null default current_timestamp,
  unique(org_token, name, environment)
);

create table if not exists events (
  id integer primary key autoincrement,
  org_token text not null,
  endpoint_id integer not null references endpoints(id),
  method text not null,
  path text not null,
  status_code integer not null,
  latency_ms integer not null,
  ip text,
  user_agent text,
  anomaly_score real not null default 0,
  anomaly_reasons text,
  environment text not null,
  occurred_at text not null
);

create table if not exists alerts (
  id integer primary key autoincrement,
  org_token text not null,
  endpoint_id integer references endpoints(id),
  severity text not null,
  type text not null,
  title text not null,
  description text,
  remediation text,
  source text,
  resolved integer not null default 0,
  created_at text not null default current_timestamp
);

create table if not exists scans (
  id integer primary key autoincrement,
  org_token text not null,
  endpoint_id integer references endpoints(id),
  target text not null,
  status text not null default 'queued',
  open_ports text not null default '[]',
  risks text not null default '[]',
  created_at text not null default current_timestamp
);

create table if not exists reports (
  id integer primary key autoincrement,
  org_token text not null,
  report_type text not null,
  status text not null default 'draft',
  content text,
  evidence_count integer not null default 0,
  created_at text not null default current_timestamp
);

create table if not exists webhook_events (
  id integer primary key autoincrement,
  org_token text,
  provider text not null,
  event_type text,
  payload text not null,
  findings_count integer not null default 0,
  created_at text not null default current_timestamp
);
"""


def ensure_parent_directory() -> None:
  Path(settings.database_path).parent.mkdir(parents=True, exist_ok=True)


def init_db() -> None:
  ensure_parent_directory()
  with sqlite3.connect(settings.database_path) as connection:
    connection.executescript(SCHEMA)
    connection.commit()


@contextmanager
def get_connection() -> Iterator[sqlite3.Connection]:
  ensure_parent_directory()
  connection = sqlite3.connect(settings.database_path)
  connection.row_factory = sqlite3.Row
  try:
    yield connection
    connection.commit()
  finally:
    connection.close()
