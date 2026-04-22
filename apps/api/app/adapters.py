from dataclasses import dataclass
from datetime import datetime
from typing import Protocol


@dataclass
class EventSignal:
    method: str
    path: str
    status_code: int
    latency_ms: int
    ip: str | None
    user_agent: str | None
    occurred_at: datetime


@dataclass
class AnomalyResult:
    score: float
    reasons: list[str]


@dataclass
class BaselineSnapshot:
    request_rate: float
    error_rate: float
    latency_p95: float
    top_ip_clusters: list[str]


@dataclass
class ScanResult:
    target: str
    open_ports: list[int]
    risks: list[str]


@dataclass
class SecretFinding:
    provider: str
    location: str
    secret_type: str
    confidence: float


class PortScanner(Protocol):
    def scan_target(self, target: str) -> ScanResult: ...


class TrafficDetector(Protocol):
    def score_event(self, event: EventSignal) -> AnomalyResult: ...

    def build_baseline(self, events: list[EventSignal]) -> BaselineSnapshot: ...


class SecretDetector(Protocol):
    def scan_github_event(self, payload: dict) -> list[SecretFinding]: ...

