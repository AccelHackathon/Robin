from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str | None = None
    git_commit: str = "unknown"
    log_level: str = "INFO"

    anthropic_api_key: str | None = None
    telegram_bot_token: str | None = None
    agentmail_api_key: str | None = None
    elevenlabs_api_key: str | None = None

    public_base_url: str | None = None
    worker_enabled: bool = True
    worker_poll_seconds: float = 1.0


settings = Settings()
