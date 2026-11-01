"""Application configuration loaded from environment variables."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """RAG service settings."""

    app_env: str = "development"
    port: int = 8000
    supabase_url: str = ""
    supabase_service_role_key: str = ""
    internal_service_token: str = ""
    llm_provider: str = ""
    llm_model: str = ""
    llm_api_key: str = ""
    embedding_provider: str = ""
    embedding_model: str = ""
    embedding_dimensions: int = 0

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
