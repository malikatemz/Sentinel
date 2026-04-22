from dataclasses import dataclass
from datetime import datetime


@dataclass
class SentinelClient:
    token: str
    ingest_url: str = "http://localhost:8000/v1/ingest/events"
    endpoint_name: str = "default"
    environment: str = "prod"

    def watch(self, app, token: str | None = None, endpoint_name: str | None = None, environment: str = "prod"):
        self.token = token or self.token
        self.endpoint_name = endpoint_name or self.endpoint_name
        self.environment = environment
        return app

    def scan(self, target: str) -> dict[str, str]:
        return {"status": "queued", "target": target}

    def report(self, report_type: str, start_at: datetime | None = None, end_at: datetime | None = None):
        return {
            "status": "queued",
            "type": report_type,
            "start_at": start_at.isoformat() if start_at else None,
            "end_at": end_at.isoformat() if end_at else None,
        }


class SentinelNamespace:
    def client(
        self,
        token: str,
        ingest_url: str = "http://localhost:8000/v1/ingest/events",
        endpoint_name: str = "default",
        environment: str = "prod",
    ) -> SentinelClient:
        return SentinelClient(
            token=token,
            ingest_url=ingest_url,
            endpoint_name=endpoint_name,
            environment=environment,
        )

    def watch(self, app, token: str, endpoint_name: str | None = None, environment: str = "prod"):
        return self.client(token=token, endpoint_name=endpoint_name or "default", environment=environment).watch(app)


sentinel = SentinelNamespace()
