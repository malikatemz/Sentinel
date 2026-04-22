from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "SentinelAPI"
    environment: str = "development"
    openai_api_key: str | None = None
    supabase_url: str | None = None
    supabase_service_role_key: str | None = None
    redis_url: str | None = None
    slack_webhook_url: str | None = None
    sendgrid_api_key: str | None = None
    github_webhook_secret: str | None = None


settings = Settings()
