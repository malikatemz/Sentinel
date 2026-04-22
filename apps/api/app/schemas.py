from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class EventRecord(BaseModel):
  method: str
  path: str
  status_code: int
  latency_ms: int
  ip: str | None = None
  user_agent: str | None = None
  environment: str = "prod"
  occurred_at: datetime = Field(default_factory=datetime.utcnow)


class IngestRequest(BaseModel):
  org_token: str
  endpoint_name: str
  events: list[EventRecord]


class ReportRequest(BaseModel):
  org_token: str
  report_type: Literal["soc2", "gdpr", "iso27001"]
  start_at: datetime
  end_at: datetime


class ScanRequest(BaseModel):
  org_token: str
  endpoint_name: str | None = None
  target: str


class SlackTestRequest(BaseModel):
  org_token: str
  channel_name: str | None = None


class WebhookEnvelope(BaseModel):
  org_token: str | None = None
  event_type: str | None = None
  payload: dict[str, Any]

