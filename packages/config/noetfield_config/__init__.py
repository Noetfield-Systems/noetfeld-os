"""Runtime configuration for Noetfield services."""

from noetfield_config.intake import (
    CANONICAL_INTAKE_EMAIL,
    COMPLIANCE_REMEDIATION_TIP,
    LEGACY_INTAKE_ALIASES,
)

from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Environment-backed settings shared by the modular monolith."""

    model_config = SettingsConfigDict(env_file=".env", env_prefix="", extra="ignore")

    noetfield_env: Literal["local", "dev", "staging", "prod"] = "local"
    noetfield_service_name: str = "noetfield-platform"
    noetfield_log_level: str = "INFO"

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/noetfield"
    supabase_url: str | None = None
    supabase_anon_key: SecretStr | None = None
    supabase_service_role_key: SecretStr | None = None
    redis_url: str = "redis://localhost:6379/0"

    opa_url: str = "http://localhost:8181"
    langfuse_host: str | None = None
    langfuse_public_key: SecretStr | None = None
    langfuse_secret_key: SecretStr | None = None

    ai_provider: str = "ollama"
    ollama_base_url: str = "http://localhost:11434"
    openai_api_key: SecretStr | None = None
    anthropic_api_key: SecretStr | None = None
    azure_openai_endpoint: str | None = None
    azure_openai_api_key: SecretStr | None = None

    gemini_api_key: SecretStr | None = Field(
        default=None,
        description="Google Gemini API key — server-side only; never expose to browsers.",
    )
    gemini_model: str = "gemini-2.0-flash"
    openrouter_api_key: SecretStr | None = Field(
        default=None,
        description="OpenRouter API key — server-side only; routes to Gemini/other models via OpenRouter.",
    )
    openrouter_model: str = "google/gemini-2.0-flash-001"
    public_chat_provider: Literal["auto", "gemini", "openrouter"] = "auto"
    public_chat_enabled: bool = True
    public_chat_cors_origins: str = (
        "https://www.noetfield.com,https://noetfield.com,http://localhost:8080,http://127.0.0.1:8080"
    )

    public_intake_enabled: bool = True
    intake_persistence: Literal["auto", "memory", "postgres"] = "auto"
    intake_ops_webhook_url: str | None = Field(
        default=None,
        description="Slack-compatible webhook URL for new intake notifications.",
    )
    redis_sessions_enabled: bool = True

    telegram_bot_enabled: bool = True
    telegram_bot_token: SecretStr | None = Field(
        default=None,
        description="Telegram Bot API token — server-side only; never expose to browsers.",
    )
    telegram_webhook_secret: SecretStr | None = Field(
        default=None,
        description="Optional secret_token for Telegram setWebhook (X-Telegram-Bot-Api-Secret-Token).",
    )
    telegram_webhook_base_url: str | None = Field(
        default=None,
        description="Public HTTPS base for webhook registration, e.g. https://platform.noetfield.com",
    )

    event_integrity_secret: SecretStr = Field(
        default=SecretStr("replace-with-kms-managed-secret"),
        description="Use KMS or a secrets manager outside local development.",
    )
    runtime_event_store: Literal["memory", "postgres"] = "postgres"

    governance_pilot_auth_required: bool = Field(
        default=False,
        description="When true, /api/v1/governance/* requires a pilot API key (set in production).",
    )
    governance_pilot_api_keys: str = Field(
        default="",
        description=(
            "Comma-separated pilot keys. Optional tenant binding: "
            "tenant_uuid:secret or bare secret (any tenant in body)."
        ),
    )
    governance_pilot_rate_limit_per_min: int = Field(
        default=120,
        ge=0,
        description="Max governance v1 calls per pilot key per minute (0 = disabled).",
    )
    governance_workspace_ui_rate_limit_per_min: int = Field(
        default=60,
        ge=0,
        description="Max Trust Ledger workspace UI API calls per pilot key per minute (0 = disabled).",
    )
    governance_webhook_urls: str = Field(
        default="",
        description="Comma-separated HTTPS URLs for governance.decision.recorded webhooks (pilot).",
    )
    governance_webhook_secret: SecretStr | None = Field(
        default=None,
        description="Optional HMAC secret for webhook signatures (X-Noetfield-Signature).",
    )
    public_status_page_url: str = Field(
        default="https://www.noetfield.com/status/",
        description="Canonical institutional status page linked from API health payloads.",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
