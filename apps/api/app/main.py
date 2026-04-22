from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .db import init_db
from .schemas import IngestRequest, ReportRequest, ScanRequest, SlackTestRequest, WebhookEnvelope
from .services import (
    dashboard_snapshot,
    generate_report,
    ingest_github_webhook,
    ingest_runtime_events,
    ingest_stripe_webhook,
    send_slack_test,
    trigger_scan,
)
from .settings import settings


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health() -> dict[str, str | bool]:
    return {"status": "ok", "database_ready": True}


@app.post("/v1/ingest/events")
async def ingest_events(payload: IngestRequest) -> dict[str, object]:
    return ingest_runtime_events(payload)


@app.get("/v1/alerts")
async def list_alerts(org_token: str | None = None) -> dict[str, object]:
    return dashboard_snapshot(org_token)


@app.post("/v1/reports")
async def request_report(payload: ReportRequest) -> dict[str, object]:
    return generate_report(payload)


@app.post("/v1/scans/trigger")
async def scan_target(payload: ScanRequest) -> dict[str, object]:
    return trigger_scan(payload)


@app.post("/v1/webhooks/github")
async def github_webhook(payload: WebhookEnvelope) -> dict[str, object]:
    return ingest_github_webhook(payload)


@app.post("/v1/webhooks/stripe")
async def stripe_webhook(payload: WebhookEnvelope) -> dict[str, object]:
    return ingest_stripe_webhook(payload)


@app.post("/v1/integrations/slack/test")
async def slack_test(payload: SlackTestRequest) -> dict[str, object]:
    return await send_slack_test(payload)
