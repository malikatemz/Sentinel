import os
from pathlib import Path

from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = os.getenv("APP_NAME", "SentinelAPI")
    environment: str = os.getenv("APP_ENVIRONMENT", "development")
    database_path: str = os.getenv(
        "SENTINEL_DATABASE_PATH",
        str(Path(__file__).resolve().parents[1] / "data" / "sentinel.db"),
    )
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
    supabase_url: str | None = os.getenv("SUPABASE_URL")
    supabase_service_role_key: str | None = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    redis_url: str | None = os.getenv("REDIS_URL")
    slack_webhook_url: str | None = os.getenv("SLACK_WEBHOOK_URL")
    sendgrid_api_key: str | None = os.getenv("SENDGRID_API_KEY")
    github_webhook_secret: str | None = os.getenv("GITHUB_WEBHOOK_SECRET")


settings = Settings()
