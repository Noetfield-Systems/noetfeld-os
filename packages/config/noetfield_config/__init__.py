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
    openrouter_model: str = "google/gemini-2.5-flash"
    public_chat_provider: Literal["auto", "gemini", "openrouter"] = "auto"
    public_chat_enabled: bool = True
    public_chat_cors_origins: str = (
        "https://www.noetfield.com,https://noetfield.com,http://localhost:8080,http://127.0.0.1:8080"
    )
    public_chat_telemetry_enabled: bool = Field(
        default=True,
        description="Persist public chat prompts/replies/errors for behavior analysis.",
    )
    public_chat_telemetry_path: str = Field(
        default="var/public_chat_telemetry.jsonl",
        description="JSONL path for public chat telemetry. Use a durable mount in production.",
    )
    public_chat_telemetry_max_chars: int = Field(
        default=4000,
        ge=200,
        le=12000,
        description="Maximum stored characters per public chat prompt or reply.",
    )

    public_intake_enabled: bool = True
    intake_persistence: Literal["auto", "memory", "postgres"] = "auto"
    intake_ops_webhook_url: str | None = Field(
        default=None,
        description="Slack-compatible webhook URL for new intake notifications.",
    )
    intake_email_notify_enabled: bool = True
    intake_email_from: str = Field(
        default="Noetfield Intake <notifications@noetfield.com>",
        description="From address for intake inbox + auto-ack emails (Resend/SMTP verified domain).",
    )
    intake_email_to: str = Field(
        default="operations@noetfield.com",
        description="Operations inbox that receives every POST /api/intake.",
    )
    intake_auto_ack_enabled: bool = Field(
        default=True,
        description="Send submitter an instant receipt email when intake email delivery is configured.",
    )
    casl_mailing_address: str = Field(
        default="7816 Windsor St\nVancouver, BC, V5X 4A8\nCanada",
        description="Physical mailing address included in CASL-compliant commercial email footers.",
    )
    resend_api_key: SecretStr | None = Field(
        default=None,
        description="Resend API key — preferred intake email transport (server-side only).",
    )
    intake_smtp_host: str | None = Field(
        default=None,
        description="SMTP host fallback when RESEND_API_KEY is unset (e.g. smtp.gmail.com).",
    )
    intake_smtp_port: int = Field(default=587, ge=1, le=65535)
    intake_smtp_user: str | None = None
    intake_smtp_password: SecretStr | None = None
    intake_smtp_use_tls: bool = True
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
    admin_dashboard_secret: SecretStr | None = Field(
        default=None,
        description="Internal admin dashboard secret for X-Admin-Secret protected operations views.",
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

    sandbox_enabled: bool = Field(
        default=True,
        description="Enable POST /api/sandbox/* self-serve developer sandbox.",
    )
    sandbox_evaluate_limit: int = Field(
        default=50,
        ge=1,
        le=500,
        description="Max evaluate calls per sandbox session.",
    )
    sandbox_trial_days: int = Field(
        default=14,
        ge=1,
        le=90,
        description="Sandbox session TTL in days.",
    )
    sandbox_provision_rate_limit_per_hour: int = Field(
        default=10,
        ge=0,
        description="Max sandbox provisions per client IP per hour (0 = disabled).",
    )
    sandbox_block_free_email: bool = Field(
        default=True,
        description="Reject common consumer email domains for sandbox signup.",
    )
    sandbox_copilot_pack_intake_url: str = Field(
        default="/trust-brief/intake/?interest=pilot&vector=copilot-governance",
        description="Upgrade CTA path for sandbox export moment (RID appended client-side).",
    )
    stripe_secret_key: SecretStr | None = Field(
        default=None,
        description="Stripe secret key — server-side only; commercial licensing checkout fulfillment.",
    )
    stripe_webhook_secret: SecretStr | None = Field(
        default=None,
        description="Stripe webhook signing secret for checkout.session.completed fulfillment.",
    )
    stripe_publishable_key: str | None = Field(
        default=None,
        description="Stripe publishable key — only if embedding Checkout client-side (optional).",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
