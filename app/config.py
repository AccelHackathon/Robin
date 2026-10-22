from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str | None = None
    git_commit: str = "unknown"
    log_level: str = "INFO"

    openai_api_key: str | None = None                    # the only LLM provider used by the project
    openai_model: str = "gpt-4o"
    openai_base_url: str | None = None                   # OpenAI-compatible endpoint (e.g. local Ollama http://localhost:11434/v1)
    telegram_bot_token: str | None = None

    # Workstream A — email (AgentMail)
    agentmail_api_key: str | None = None
    agentmail_webhook_secret: str | None = None          # whsec_... from the webhook endpoint
    agentmail_domain: str = "agentmail.to"
    agentmail_shared_inbox: str = "robin-agent@agentmail.to"   # fallback when the plan's inbox limit is reached
    simulated_insurer_email: str | None = None           # mailbox with role simulated_insurer

    # Workstream A — voice (ElevenLabs Agents + Twilio)
    elevenlabs_api_key: str | None = None
    elevenlabs_agent_id: str | None = None
    elevenlabs_phone_number_id: str | None = None
    elevenlabs_webhook_secret: str | None = None
    twilio_account_sid: str | None = None
    twilio_auth_token: str | None = None
    twilio_phone_number: str | None = None
    insurer_test_phone: str | None = None                # verified number of the teammate playing the insurer

    # Workstream D — Risk Sentinel (continuous monitoring, Keenable web search)
    keenable_api_key: str | None = None
    keenable_search_mode: str = "realtime"               # realtime (fast, 1 credit) | pro (deeper)
    sentinel_enabled: bool = True
    sentinel_interval_minutes: int = 15                  # sweep cadence per watched account
    sentinel_lookback_hours: int = 48                    # freshness window for news
    sentinel_min_severity_to_notify: str = "medium"      # low | medium | high | critical

    public_base_url: str | None = None
    internal_api_token: str | None = None                # bearer for /internal/* operator endpoints
    telegram_mode: str = "polling"            # polling | webhook  (C)
    telegram_bot_username: str | None = None  # B's deep link
    session_secret: str | None = None
    intake_model: str = "gpt-4o"
    worker_enabled: bool = True
    worker_poll_seconds: float = 1.0


settings = Settings()
