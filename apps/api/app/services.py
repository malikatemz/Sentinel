from __future__ import annotations

from collections import Counter
from dataclasses import asdict

import httpx

from .adapters import EventSignal
from .auth import generate_api_token, hash_token, slugify_org_name
from .detectors import PatternSecretDetector, PlaceholderPortScanner, RuleBasedTrafficDetector, now_iso
from .repository import (
  create_alert,
  create_api_token,
  create_report,
  list_alerts,
  list_endpoints,
  list_reports,
  recent_events_for_endpoint,
  save_event,
  save_scan,
  save_webhook_event,
  summarize_report_window,
  upsert_endpoint,
)
from .schemas import IngestRequest, ReportRequest, ScanRequest, SlackTestRequest, WebhookEnvelope
from .settings import settings

traffic_detector = RuleBasedTrafficDetector()
port_scanner = PlaceholderPortScanner()
secret_detector = PatternSecretDetector()


def ingest_runtime_events(payload: IngestRequest) -> dict[str, object]:
  environment = payload.events[0].environment if payload.events else "prod"
  endpoint_id = upsert_endpoint(payload.org_token, payload.endpoint_name, environment)
  created_alerts = 0

  for record in payload.events:
    event = EventSignal(
      method=record.method,
      path=record.path,
      status_code=record.status_code,
      latency_ms=record.latency_ms,
      ip=record.ip,
      user_agent=record.user_agent,
      occurred_at=record.occurred_at,
    )
    anomaly = traffic_detector.score_event(event)
    save_event(payload.org_token, endpoint_id, event, anomaly, record.environment)

    if anomaly.score >= 0.6:
      created_alerts += 1
      create_alert(
        payload.org_token,
        endpoint_id,
        severity=severity_from_score(anomaly.score),
        alert_type="anomaly",
        title=f"Anomalous traffic on {payload.endpoint_name}",
        description=build_alert_description(event, anomaly.reasons),
        remediation="Review recent requests, rate limits, and affected credentials for this endpoint.",
        source={
          "path": event.path,
          "status_code": event.status_code,
          "latency_ms": event.latency_ms,
          "reasons": anomaly.reasons,
        },
      )

  recent_events = recent_events_for_endpoint(payload.org_token, endpoint_id)
  baseline = traffic_detector.build_baseline(recent_events)
  ip_clusters = Counter(event.ip or "unknown" for event in recent_events)

  if ip_clusters and ip_clusters.most_common(1)[0][1] >= 5:
    hottest_ip, hottest_count = ip_clusters.most_common(1)[0]
    create_alert(
      payload.org_token,
      endpoint_id,
      severity="medium",
      alert_type="ip-cluster",
      title=f"Repeated traffic from {hottest_ip}",
      description=f"{hottest_count} recent requests came from the same IP cluster for {payload.endpoint_name}.",
      remediation="Confirm whether this traffic is expected or rate-limit the source.",
      source={"ip": hottest_ip, "count": hottest_count},
    )
    created_alerts += 1

  return {
    "status": "accepted",
    "received": len(payload.events),
    "alerts_created": created_alerts,
    "baseline": asdict(baseline),
  }


def trigger_scan(payload: ScanRequest) -> dict[str, object]:
  endpoint_id = None
  if payload.endpoint_name:
    endpoint_id = upsert_endpoint(payload.org_token, payload.endpoint_name, "prod")

  result = port_scanner.scan_target(payload.target)
  save_scan(payload.org_token, endpoint_id, result)

  if result.risks:
    create_alert(
      payload.org_token,
      endpoint_id,
      severity="high",
      alert_type="port",
      title=f"Scan findings for {payload.target}",
      description="; ".join(result.risks),
      remediation="Review ingress rules and close unintended public services.",
      source={"target": result.target, "open_ports": result.open_ports},
    )

  return {
    "status": "completed",
    "target": result.target,
    "open_ports": result.open_ports,
    "risks": result.risks,
  }


def generate_report(payload: ReportRequest) -> dict[str, object]:
  summary = summarize_report_window(
    payload.org_token,
    payload.start_at.isoformat(),
    payload.end_at.isoformat(),
  )
  alerts = list_alerts(payload.org_token, limit=10)
  headline = {
    "soc2": "SOC 2 security monitoring summary",
    "gdpr": "GDPR incident and access review summary",
    "iso27001": "ISO 27001 control evidence summary",
  }[payload.report_type]
  content = "\n".join(
    [
      headline,
      f"Window: {payload.start_at.isoformat()} to {payload.end_at.isoformat()}",
      f"Observed runtime events: {summary['events']}",
      f"Raised alerts: {summary['alerts']}",
      "",
      "Recent notable alerts:",
      *[
        f"- [{alert['severity']}] {alert['title']}: {alert['description']}"
        for alert in alerts[:5]
      ],
    ]
  )
  report_id = create_report(payload.org_token, payload.report_type, content, summary["alerts"])
  return {
    "status": "drafted",
    "report_id": report_id,
    "type": payload.report_type,
    "content": content,
  }


def ingest_github_webhook(envelope: WebhookEnvelope) -> dict[str, object]:
  findings = secret_detector.scan_github_event(envelope.payload)
  save_webhook_event(
    provider="github",
    payload=envelope.payload,
    event_type=envelope.event_type,
    org_token=envelope.org_token,
    findings_count=len(findings),
  )

  for finding in findings:
    create_alert(
      envelope.org_token or "unscoped",
      None,
      severity="critical",
      alert_type="credential",
      title=f"Potential {finding.secret_type} leak detected",
      description=f"Webhook payload matched a high-confidence {finding.secret_type} pattern.",
      remediation="Rotate the credential and scrub it from commits, CI logs, and deployment history.",
      source=asdict(finding),
    )

  return {
    "status": "processed",
    "findings_count": len(findings),
    "findings": [asdict(finding) for finding in findings],
  }


def ingest_stripe_webhook(envelope: WebhookEnvelope) -> dict[str, object]:
  save_webhook_event(
    provider="stripe",
    payload=envelope.payload,
    event_type=envelope.event_type,
    org_token=envelope.org_token,
  )
  return {
    "status": "processed",
    "event_type": envelope.event_type,
  }


async def send_slack_test(payload: SlackTestRequest) -> dict[str, object]:
  if not settings.slack_webhook_url:
    return {
      "status": "skipped",
      "message": "SLACK_WEBHOOK_URL is not configured.",
    }

  message = {
    "text": f"SentinelAPI test alert for {payload.org_token} at {now_iso()}",
  }
  async with httpx.AsyncClient(timeout=10) as client:
    response = await client.post(settings.slack_webhook_url, json=message)
    response.raise_for_status()

  return {
    "status": "sent",
    "channel_name": payload.channel_name or "default",
  }


def dashboard_snapshot(org_token: str | None = None) -> dict[str, object]:
  alerts = list_alerts(org_token, limit=20)
  endpoints = list_endpoints(org_token)
  reports = list_reports(org_token)
  return {
    "alerts": alerts,
    "endpoints": endpoints,
    "reports": reports,
    "summary": {
      "alerts_total": len(alerts),
      "critical_total": sum(1 for alert in alerts if alert["severity"] == "critical"),
      "endpoint_total": len(endpoints),
      "report_total": len(reports),
    },
  }


def severity_from_score(score: float) -> str:
  if score >= 0.85:
    return "critical"
  if score >= 0.65:
    return "high"
  if score >= 0.35:
    return "medium"
  return "low"


def build_alert_description(event: EventSignal, reasons: list[str]) -> str:
  reason_text = ", ".join(reasons) if reasons else "unexpected behavior"
  return (
    f"{event.method} {event.path} returned {event.status_code} in {event.latency_ms}ms "
    f"and matched: {reason_text}."
  )


def issue_api_token(org_name: str, token_name: str) -> dict[str, str]:
  org_key = slugify_org_name(org_name)
  token = generate_api_token()
  create_api_token(org_key, token_name, hash_token(token))
  return {
    "org_key": org_key,
    "token_name": token_name,
    "token": token,
  }
