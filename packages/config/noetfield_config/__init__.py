"""Runtime configuration for Noetfield services."""

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

    event_integrity_secret: SecretStr = Field(
        default=SecretStr("replace-with-kms-managed-secret"),
        description="Use KMS or a secrets manager outside local development.",
    )
    runtime_event_store: Literal["memory", "postgres"] = "postgres"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
