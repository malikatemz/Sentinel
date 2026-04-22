from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from .db import init_db
from .schemas import BootstrapTokenRequest, IngestRequest, ReportRequest, ScanRequest, SlackTestRequest, WebhookEnvelope
from .security import (
    attach_security_headers,
    enforce_body_size,
    enforce_rate_limit,
    http_exception_response,
    parse_json_body,
    require_bootstrap_key,
    validate_org_token,
    verify_github_signature,
    verify_stripe_signature,
)
from .services import (
    dashboard_snapshot,
    generate_report,
    ingest_github_webhook,
    ingest_runtime_events,
    ingest_stripe_webhook,
    issue_api_token,
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
    TrustedHostMiddleware,
    allowed_hosts=settings.allowed_hosts or ["127.0.0.1", "localhost"],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "X-Hub-Signature-256", "Stripe-Signature"],
)


@app.middleware("http")
async def security_middleware(request: Request, call_next):
    client_host = request.client.host if request.client else "unknown"
    try:
        enforce_rate_limit(f"{client_host}:{request.url.path}")
        response = await call_next(request)
    except HTTPException as exc:
        return http_exception_response(request, exc)

    attach_security_headers(request, response)
    return response

@app.get("/health")
async def health() -> dict[str, str | bool]:
    return {"status": "ok", "database_ready": True}


@app.post("/v1/ingest/events")
async def ingest_events(payload: IngestRequest) -> dict[str, object]:
    auth_context = validate_org_token(payload.org_token)
    return ingest_runtime_events(payload.model_copy(update={"org_token": auth_context.org_key}))


@app.get("/v1/alerts")
async def list_alerts(org_token: str) -> dict[str, object]:
    auth_context = validate_org_token(org_token)
    return dashboard_snapshot(auth_context.org_key)


@app.post("/v1/reports")
async def request_report(payload: ReportRequest) -> dict[str, object]:
    auth_context = validate_org_token(payload.org_token)
    return generate_report(payload.model_copy(update={"org_token": auth_context.org_key}))


@app.post("/v1/scans/trigger")
async def scan_target(payload: ScanRequest) -> dict[str, object]:
    auth_context = validate_org_token(payload.org_token)
    return trigger_scan(payload.model_copy(update={"org_token": auth_context.org_key}))


@app.post("/v1/webhooks/github")
async def github_webhook(request: Request) -> dict[str, object]:
    body = await request.body()
    enforce_body_size(body)
    verify_github_signature(body, request.headers.get("x-hub-signature-256"))
    payload = WebhookEnvelope.model_validate(parse_json_body(body))
    if not payload.org_token:
        raise HTTPException(status_code=400, detail="GitHub webhooks must include org_token.")
    auth_context = validate_org_token(payload.org_token)
    return ingest_github_webhook(payload.model_copy(update={"org_token": auth_context.org_key}))


@app.post("/v1/webhooks/stripe")
async def stripe_webhook(request: Request) -> dict[str, object]:
    body = await request.body()
    enforce_body_size(body)
    verify_stripe_signature(body, request.headers.get("stripe-signature"))
    payload = WebhookEnvelope.model_validate(parse_json_body(body))
    if not payload.org_token:
        raise HTTPException(status_code=400, detail="Stripe webhooks must include org_token.")
    auth_context = validate_org_token(payload.org_token)
    return ingest_stripe_webhook(payload.model_copy(update={"org_token": auth_context.org_key}))


@app.post("/v1/integrations/slack/test")
async def slack_test(payload: SlackTestRequest) -> dict[str, object]:
    auth_context = validate_org_token(payload.org_token)
    return await send_slack_test(payload.model_copy(update={"org_token": auth_context.org_key}))


@app.post("/v1/tokens/bootstrap")
async def bootstrap_token(payload: BootstrapTokenRequest, request: Request) -> dict[str, str]:
    require_bootstrap_key(request.headers.get("x-sentinel-bootstrap-key"))
    return issue_api_token(payload.org_name, payload.token_name)
