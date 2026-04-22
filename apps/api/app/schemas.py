from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field, StringConstraints
from typing_extensions import Annotated


TokenString = Annotated[str, StringConstraints(min_length=12, max_length=128, strip_whitespace=True)]
EndpointName = Annotated[str, StringConstraints(min_length=2, max_length=80, strip_whitespace=True)]
PathString = Annotated[str, StringConstraints(min_length=1, max_length=2048, strip_whitespace=True)]
EnvironmentString = Annotated[str, StringConstraints(min_length=2, max_length=24, strip_whitespace=True)]
TargetString = Annotated[str, StringConstraints(min_length=3, max_length=255, strip_whitespace=True)]


class EventRecord(BaseModel):
  method: Annotated[str, StringConstraints(min_length=3, max_length=10, to_upper=True, strip_whitespace=True)]
  path: PathString
  status_code: int = Field(ge=100, le=599)
  latency_ms: int = Field(ge=0, le=120000)
  ip: str | None = Field(default=None, max_length=128)
  user_agent: str | None = Field(default=None, max_length=512)
  environment: EnvironmentString = "prod"
  occurred_at: datetime = Field(default_factory=datetime.utcnow)


class IngestRequest(BaseModel):
  org_token: TokenString
  endpoint_name: EndpointName
  events: list[EventRecord] = Field(min_length=1, max_length=100)


class ReportRequest(BaseModel):
  org_token: TokenString
  report_type: Literal["soc2", "gdpr", "iso27001"]
  start_at: datetime
  end_at: datetime


class ScanRequest(BaseModel):
  org_token: TokenString
  endpoint_name: EndpointName | None = None
  target: TargetString


class SlackTestRequest(BaseModel):
  org_token: TokenString
  channel_name: str | None = Field(default=None, max_length=120)


class WebhookEnvelope(BaseModel):
  org_token: TokenString | None = None
  event_type: str | None = Field(default=None, max_length=120)
  payload: dict[str, Any]
