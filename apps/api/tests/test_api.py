from importlib import reload
from pathlib import Path
import sys

from fastapi.testclient import TestClient

API_ROOT = Path(__file__).resolve().parents[1]
if str(API_ROOT) not in sys.path:
  sys.path.insert(0, str(API_ROOT))


def make_client(tmp_path, monkeypatch):
  monkeypatch.setenv("SENTINEL_DATABASE_PATH", str(tmp_path / "sentinel.db"))
  import app.settings as settings_module
  import app.db as db_module
  import app.security as security_module
  import app.services as services_module
  import app.main as main_module

  reload(settings_module)
  reload(db_module)
  reload(security_module)
  reload(services_module)
  reload(main_module)
  db_module.init_db()
  return TestClient(main_module.app)


def test_health(tmp_path, monkeypatch):
  client = make_client(tmp_path, monkeypatch)
  response = client.get("/health")
  assert response.status_code == 200
  assert response.json()["status"] == "ok"
  assert response.headers["x-content-type-options"] == "nosniff"


def test_ingest_creates_alerts_and_snapshot(tmp_path, monkeypatch):
  client = make_client(tmp_path, monkeypatch)
  response = client.post(
    "/v1/ingest/events",
    json={
      "org_token": "org_test_123",
      "endpoint_name": "auth-service",
      "events": [
        {
          "method": "POST",
          "path": "/auth/token",
          "status_code": 503,
          "latency_ms": 1810,
          "ip": "203.0.113.10",
          "user_agent": "pytest",
          "environment": "prod",
          "occurred_at": "2026-04-22T08:00:00",
        }
      ],
    },
  )
  assert response.status_code == 200
  payload = response.json()
  assert payload["received"] == 1
  assert payload["alerts_created"] >= 1

  snapshot = client.get("/v1/alerts", params={"org_token": "org_test_123"})
  assert snapshot.status_code == 200
  assert snapshot.json()["summary"]["alerts_total"] >= 1


def test_report_generation(tmp_path, monkeypatch):
  client = make_client(tmp_path, monkeypatch)
  client.post(
    "/v1/ingest/events",
    json={
      "org_token": "org_report_123",
      "endpoint_name": "billing-api",
      "events": [
        {
          "method": "GET",
          "path": "/billing/invoices",
          "status_code": 500,
          "latency_ms": 1200,
          "ip": "198.51.100.10",
          "user_agent": "pytest",
          "environment": "prod",
          "occurred_at": "2026-04-22T10:00:00",
        }
      ],
    },
  )
  report = client.post(
    "/v1/reports",
    json={
      "org_token": "org_report_123",
      "report_type": "soc2",
      "start_at": "2026-04-22T00:00:00",
      "end_at": "2026-04-22T23:59:59",
    },
  )
  assert report.status_code == 200
  assert report.json()["status"] == "drafted"
  assert "SOC 2" in report.json()["content"]


def test_github_webhook_detects_secret_pattern(tmp_path, monkeypatch):
  client = make_client(tmp_path, monkeypatch)
  response = client.post(
    "/v1/webhooks/github",
    json={
      "org_token": "org_secret_123",
      "event_type": "push",
      "payload": {
        "commits": [
          {
            "message": "accidental secret",
            "added": ["OPENAI_API_KEY=sk-abcdefghijklmnopqrstuvwxyz123456"],
          }
        ]
      },
    },
  )
  assert response.status_code == 200
  assert response.json()["findings_count"] >= 1


def test_rejects_short_token(tmp_path, monkeypatch):
  client = make_client(tmp_path, monkeypatch)
  response = client.post(
    "/v1/scans/trigger",
    json={
      "org_token": "short",
      "target": "redis.internal",
    },
  )
  assert response.status_code == 422


def test_rejects_invalid_github_signature(tmp_path, monkeypatch):
  monkeypatch.setenv("GITHUB_WEBHOOK_SECRET", "topsecret")
  client = make_client(tmp_path, monkeypatch)
  response = client.post(
    "/v1/webhooks/github",
    json={
      "org_token": "org_secret_123",
      "event_type": "push",
      "payload": {"message": "hello"},
    },
    headers={"X-Hub-Signature-256": "sha256=invalid"},
  )
  assert response.status_code == 401
