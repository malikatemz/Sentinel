from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from .alerts import AlertResponse
from .endpoints import EndpointResponse


class SummaryCards(BaseModel):
    total_endpoints: int = 0
    endpoints_up: int = 0
    endpoints_down: int = 0
    avg_response_ms: float = 0
    total_alerts_24h: int = 0
    overall_uptime: float = 0


class ResponseDataPoint(BaseModel):
    checked_at: datetime
    latency_ms: int
    endpoint_name: str


class DashboardResponse(BaseModel):
    summary: SummaryCards
    recent_alerts: list[AlertResponse] = []
    endpoints: list[EndpointResponse] = []
    response_history: list[ResponseDataPoint] = []
