"""Application configuration loaded from environment variables using Pydantic Settings."""

from pathlib import Path
from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Locate .env file relative to the rag service root
RAG_ROOT = Path(__file__).resolve().parent.parent.parent
ENV_FILE = RAG_ROOT / ".env"


class Settings(BaseSettings):
    """RAG service configuration."""

    app_env: str = Field(
        default="development",
        validation_alias=AliasChoices("APP_ENV", "app_env"),
    )
    port: int = Field(
        default=8000,
        validation_alias=AliasChoices("PORT", "port"),
    )
    log_level: str = Field(
        default="INFO",
        validation_alias=AliasChoices("LOG_LEVEL", "log_level"),
    )

    # Internal service authentication
    internal_service_token: str = Field(
        default="",
        validation_alias=AliasChoices("INTERNAL_SERVICE_TOKEN", "internal_service_token"),
    )

    # Google Gemini & Embedding settings
    gemini_api_key: str = Field(
        default="",
        validation_alias=AliasChoices(
            "GEMINI_API_KEY",
            "gemini_api_key",
            "GOOGLE_API_KEY",
            "google_api_key",
            "LLM_API_KEY",
        ),
    )
    embedding_provider: str = Field(
        default="google",
        validation_alias=AliasChoices("EMBEDDING_PROVIDER", "embedding_provider"),
    )
    embedding_model: str = Field(
        default="gemini-embedding-2",
        validation_alias=AliasChoices("EMBEDDING_MODEL", "embedding_model"),
    )
    embedding_dimensions: int = Field(
        default=768,
        validation_alias=AliasChoices("EMBEDDING_DIMENSIONS", "embedding_dimensions"),
    )

    # Supabase (for storage and vector operations)
    supabase_url: str = Field(
        default="",
        validation_alias=AliasChoices("SUPABASE_URL", "supabase_url"),
    )
    supabase_service_role_key: str = Field(
        default="",
        validation_alias=AliasChoices(
            "SUPABASE_SERVICE_ROLE_KEY",
            "supabase_service_role_key",
            "SUPABASE_SECRET_KEY",
            "supabase_secret_key",
        ),
    )

    @property
    def supabase_secret_key(self) -> str:
        """Alias for backward compatibility."""
        return self.supabase_service_role_key

    model_config = SettingsConfigDict(
        env_file=[str(ENV_FILE), ".env"],
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )


settings = Settings()
