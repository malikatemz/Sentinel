from __future__ import annotations

import json
from datetime import datetime

from .adapters import AnomalyResult, EventSignal, ScanResult, SecretFinding
from .db import get_connection


def upsert_endpoint(org_token: str, name: str, environment: str) -> int:
  with get_connection() as connection:
    connection.execute(
      """
      insert into endpoints (org_token, name, environment)
      values (?, ?, ?)
      on conflict(org_token, name, environment)
      do nothing
      """,
      (org_token, name, environment),
    )
    row = connection.execute(
      "select id from endpoints where org_token = ? and name = ? and environment = ?",
      (org_token, name, environment),
    ).fetchone()
    return int(row["id"])


def save_event(
  org_token: str,
  endpoint_id: int,
  event: EventSignal,
  anomaly: AnomalyResult,
  environment: str,
) -> None:
  with get_connection() as connection:
    connection.execute(
      """
      insert into events (
        org_token, endpoint_id, method, path, status_code, latency_ms, ip, user_agent,
        anomaly_score, anomaly_reasons, environment, occurred_at
      )
      values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
      """,
      (
        org_token,
        endpoint_id,
        event.method,
        event.path,
        event.status_code,
        event.latency_ms,
        event.ip,
        event.user_agent,
        anomaly.score,
        json.dumps(anomaly.reasons),
        environment,
        event.occurred_at.isoformat(),
      ),
    )


def create_alert(
  org_token: str,
  endpoint_id: int | None,
  severity: str,
  alert_type: str,
  title: str,
  description: str,
  remediation: str,
  source: dict[str, object],
) -> int:
  with get_connection() as connection:
    cursor = connection.execute(
      """
      insert into alerts (
        org_token, endpoint_id, severity, type, title, description, remediation, source
      )
      values (?, ?, ?, ?, ?, ?, ?, ?)
      """,
      (
        org_token,
        endpoint_id,
        severity,
        alert_type,
        title,
        description,
        remediation,
        json.dumps(source),
      ),
    )
    return int(cursor.lastrowid)


def list_alerts(org_token: str | None = None, limit: int = 50) -> list[dict[str, object]]:
  with get_connection() as connection:
    if org_token:
      rows = connection.execute(
        """
        select * from alerts
        where org_token = ?
        order by created_at desc, id desc
        limit ?
        """,
        (org_token, limit),
      ).fetchall()
    else:
      rows = connection.execute(
        "select * from alerts order by created_at desc, id desc limit ?",
        (limit,),
      ).fetchall()
  return [dict(row) for row in rows]


def recent_events_for_endpoint(org_token: str, endpoint_id: int, limit: int = 200) -> list[EventSignal]:
  with get_connection() as connection:
    rows = connection.execute(
      """
      select method, path, status_code, latency_ms, ip, user_agent, occurred_at
      from events
      where org_token = ? and endpoint_id = ?
      order by occurred_at desc, id desc
      limit ?
      """,
      (org_token, endpoint_id, limit),
    ).fetchall()

  return [
    EventSignal(
      method=row["method"],
      path=row["path"],
      status_code=row["status_code"],
      latency_ms=row["latency_ms"],
      ip=row["ip"],
      user_agent=row["user_agent"],
      occurred_at=datetime.fromisoformat(str(row["occurred_at"]).replace("Z", "")),
    )
    for row in rows
  ]


def save_scan(org_token: str, endpoint_id: int | None, result: ScanResult, status: str = "completed") -> int:
  with get_connection() as connection:
    cursor = connection.execute(
      """
      insert into scans (org_token, endpoint_id, target, status, open_ports, risks)
      values (?, ?, ?, ?, ?, ?)
      """,
      (
        org_token,
        endpoint_id,
        result.target,
        status,
        json.dumps(result.open_ports),
        json.dumps(result.risks),
      ),
    )
    return int(cursor.lastrowid)


def create_report(org_token: str, report_type: str, content: str, evidence_count: int) -> int:
  with get_connection() as connection:
    cursor = connection.execute(
      """
      insert into reports (org_token, report_type, status, content, evidence_count)
      values (?, ?, 'draft', ?, ?)
      """,
      (org_token, report_type, content, evidence_count),
    )
    return int(cursor.lastrowid)


def save_webhook_event(
  provider: str,
  payload: dict,
  event_type: str | None = None,
  org_token: str | None = None,
  findings_count: int = 0,
) -> int:
  with get_connection() as connection:
    cursor = connection.execute(
      """
      insert into webhook_events (org_token, provider, event_type, payload, findings_count)
      values (?, ?, ?, ?, ?)
      """,
      (org_token, provider, event_type, json.dumps(payload), findings_count),
    )
    return int(cursor.lastrowid)


def list_endpoints(org_token: str | None = None) -> list[dict[str, object]]:
  with get_connection() as connection:
    if org_token:
      rows = connection.execute(
        """
        select *
        from endpoints
        where org_token = ?
        order by created_at desc, id desc
        """,
        (org_token,),
      ).fetchall()
    else:
      rows = connection.execute(
        "select * from endpoints order by created_at desc, id desc"
      ).fetchall()
  return [dict(row) for row in rows]


def list_reports(org_token: str | None = None) -> list[dict[str, object]]:
  with get_connection() as connection:
    if org_token:
      rows = connection.execute(
        """
        select * from reports
        where org_token = ?
        order by created_at desc, id desc
        """,
        (org_token,),
      ).fetchall()
    else:
      rows = connection.execute(
        "select * from reports order by created_at desc, id desc"
      ).fetchall()
  return [dict(row) for row in rows]


def summarize_report_window(org_token: str, start_at: str, end_at: str) -> dict[str, int]:
  with get_connection() as connection:
    events_row = connection.execute(
      """
      select count(*) as count
      from events
      where org_token = ? and occurred_at >= ? and occurred_at <= ?
      """,
      (org_token, start_at, end_at),
    ).fetchone()
    alerts_row = connection.execute(
      """
      select count(*) as count
      from alerts
      where org_token = ? and created_at >= ? and created_at <= ?
      """,
      (org_token, start_at, end_at),
    ).fetchone()
  return {
    "events": int(events_row["count"]),
    "alerts": int(alerts_row["count"]),
  }

