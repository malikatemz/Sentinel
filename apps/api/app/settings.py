import os
from pathlib import Path

from pydantic import BaseModel


def _csv_env(name: str, default: str = "") -> list[str]:
    raw = os.getenv(name, default)
    return [item.strip() for item in raw.split(",") if item.strip()]


class Settings(BaseModel):
    app_name: str = os.getenv("APP_NAME", "SentinelAPI")
    environment: str = os.getenv("APP_ENVIRONMENT", "development")
    app_host: str = os.getenv("APP_HOST", "127.0.0.1")
    app_port: int = int(os.getenv("APP_PORT", "8000"))
    database_path: str = os.getenv(
        "SENTINEL_DATABASE_PATH",
        str(Path(__file__).resolve().parents[1] / "data" / "sentinel.db"),
    )
    allowed_origins: list[str] = _csv_env(
        "ALLOWED_ORIGINS",
        "http://127.0.0.1:3000,http://localhost:3000",
    )
    allowed_hosts: list[str] = _csv_env(
        "ALLOWED_HOSTS",
        "127.0.0.1,localhost,testserver",
    )
    dev_org_tokens: list[str] = _csv_env(
        "SENTINEL_DEV_TOKENS",
        "sentinel_demo_token,org_test_123,org_report_123,org_secret_123",
    )
    rate_limit_window_seconds: int = int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60"))
    rate_limit_requests: int = int(os.getenv("RATE_LIMIT_REQUESTS", "120"))
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
    supabase_url: str | None = os.getenv("SUPABASE_URL")
    supabase_service_role_key: str | None = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    redis_url: str | None = os.getenv("REDIS_URL")
    slack_webhook_url: str | None = os.getenv("SLACK_WEBHOOK_URL")
    sendgrid_api_key: str | None = os.getenv("SENDGRID_API_KEY")
    github_webhook_secret: str | None = os.getenv("GITHUB_WEBHOOK_SECRET")
    stripe_webhook_secret: str | None = os.getenv("STRIPE_WEBHOOK_SECRET")


settings = Settings()
