from datetime import datetime
from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel, Field

from .settings import settings

app = FastAPI(title=settings.app_name)


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


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/v1/ingest/events")
async def ingest_events(payload: IngestRequest) -> dict[str, int | str]:
    return {
        "status": "accepted",
        "received": len(payload.events),
    }


@app.get("/v1/alerts")
async def list_alerts() -> dict[str, list[dict[str, str]]]:
    return {
        "alerts": [
            {
                "severity": "critical",
                "title": "Placeholder alert",
                "description": "Wire this endpoint to Supabase and the worker pipeline.",
            }
        ]
    }


@app.post("/v1/reports")
async def request_report(payload: ReportRequest) -> dict[str, str]:
    return {
        "status": "queued",
        "type": payload.report_type,
    }
