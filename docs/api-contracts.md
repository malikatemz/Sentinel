# API Contracts

## Runtime Event Ingestion

`POST /v1/ingest/events`

```json
{
  "org_token": "sentinel_live_xxx",
  "endpoint_name": "auth-service",
  "events": [
    {
      "method": "POST",
      "path": "/auth/token",
      "status_code": 401,
      "latency_ms": 143,
      "ip": "203.0.113.10",
      "user_agent": "curl/8.5.0",
      "environment": "prod",
      "occurred_at": "2026-04-21T12:30:00Z"
    }
  ]
}
```

## Report Request

`POST /v1/reports`

```json
{
  "org_token": "sentinel_live_xxx",
  "report_type": "soc2",
  "start_at": "2026-04-14T00:00:00Z",
  "end_at": "2026-04-21T00:00:00Z"
}
```

## Planned Webhooks

- `POST /v1/webhooks/github` for secret finding candidates from repository and CI activity
- `POST /v1/webhooks/stripe` for subscription state sync
- `POST /v1/integrations/slack/test` for validating outbound alert delivery

## Contract Notes

- Detection remains rule-driven even when AI summaries are enabled.
- AI is only used for triage text and report drafting, never as the source of truth for whether an incident exists.
- The legacy scanner and detector implementations should plug into the adapter interfaces in `apps/api/app/adapters.py`.
