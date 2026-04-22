from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import asdict
from datetime import datetime

from .adapters import (
  AnomalyResult,
  BaselineSnapshot,
  EventSignal,
  ScanResult,
  SecretDetector,
  SecretFinding,
  TrafficDetector,
)


SECRET_PATTERNS: dict[str, re.Pattern[str]] = {
  "openai_api_key": re.compile(r"\bsk-[A-Za-z0-9]{20,}\b"),
  "github_pat": re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"),
  "aws_access_key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
  "stripe_secret": re.compile(r"\bsk_(live|test)_[A-Za-z0-9]{16,}\b"),
}


class RuleBasedTrafficDetector(TrafficDetector):
  def score_event(self, event: EventSignal) -> AnomalyResult:
    score = 0.0
    reasons: list[str] = []

    if event.status_code >= 500:
      score += 0.7
      reasons.append("server_error")
    elif event.status_code >= 400:
      score += 0.25
      reasons.append("client_error")

    if event.latency_ms >= 1500:
      score += 0.45
      reasons.append("high_latency")
    elif event.latency_ms >= 800:
      score += 0.2
      reasons.append("elevated_latency")

    risky_paths = ("/auth", "/admin", "/token", "/login", "/billing")
    if any(path in event.path.lower() for path in risky_paths):
      score += 0.15
      reasons.append("sensitive_path")

    if event.method.upper() in {"DELETE", "PATCH"}:
      score += 0.1
      reasons.append("mutable_operation")

    return AnomalyResult(score=min(score, 1.0), reasons=reasons)

  def build_baseline(self, events: list[EventSignal]) -> BaselineSnapshot:
    if not events:
      return BaselineSnapshot(
        request_rate=0,
        error_rate=0,
        latency_p95=0,
        top_ip_clusters=[],
      )

    sorted_events = sorted(events, key=lambda item: item.occurred_at)
    duration_seconds = max(
      (sorted_events[-1].occurred_at - sorted_events[0].occurred_at).total_seconds(),
      60,
    )
    request_rate = round(len(events) / (duration_seconds / 60), 2)
    error_rate = round(
      sum(1 for event in events if event.status_code >= 400) / len(events),
      3,
    )

    latencies = sorted(event.latency_ms for event in events)
    percentile_index = min(len(latencies) - 1, max(0, math.ceil(len(latencies) * 0.95) - 1))
    top_ip_clusters = [
      ip
      for ip, _count in Counter(event.ip or "unknown" for event in events).most_common(3)
    ]

    return BaselineSnapshot(
      request_rate=request_rate,
      error_rate=error_rate,
      latency_p95=float(latencies[percentile_index]),
      top_ip_clusters=top_ip_clusters,
    )


class PlaceholderPortScanner:
  def scan_target(self, target: str) -> ScanResult:
    lowered = target.lower()
    risks: list[str] = []
    open_ports: list[int] = []

    if "redis" in lowered:
      open_ports.append(6379)
      risks.append("Public Redis exposure suspected from target naming.")
    if "postgres" in lowered or "db" in lowered:
      open_ports.append(5432)
      risks.append("Database-adjacent target should be reviewed for public ingress.")
    if not open_ports:
      open_ports = [443]
      risks.append("Legacy scanner not restored yet. This is a placeholder scan result.")

    return ScanResult(target=target, open_ports=open_ports, risks=risks)


class PatternSecretDetector(SecretDetector):
  def scan_github_event(self, payload: dict) -> list[SecretFinding]:
    serialized = stringify_payload(payload)
    findings: list[SecretFinding] = []

    for secret_type, pattern in SECRET_PATTERNS.items():
      for match in pattern.findall(serialized):
        findings.append(
          SecretFinding(
            provider="github",
            location="payload",
            secret_type=secret_type,
            confidence=0.95,
          )
        )
        if len(findings) >= 10:
          return findings

    return findings


def stringify_payload(payload: dict) -> str:
  flattened: list[str] = []

  def walk(value: object) -> None:
    if isinstance(value, dict):
      for nested in value.values():
        walk(nested)
      return
    if isinstance(value, list):
      for nested in value:
        walk(nested)
      return
    flattened.append(str(value))

  walk(payload)
  return " ".join(flattened)


def serialize_baseline(snapshot: BaselineSnapshot) -> dict[str, object]:
  return asdict(snapshot)


def now_iso() -> str:
  return datetime.utcnow().isoformat() + "Z"

