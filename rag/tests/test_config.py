"""Tests for application settings and configuration loading."""

from app.core.config import Settings


def test_settings_default_values():
    """Verify default configuration parameters."""
    settings = Settings(
        internal_service_token="test-token",
        gemini_api_key="test-api-key",
    )
    assert settings.app_env == "development"
    assert settings.port == 8000
    assert settings.embedding_provider == "google"
    assert settings.embedding_model == "gemini-embedding-2"
    assert settings.embedding_dimensions == 768


def test_settings_custom_values():
    """Verify custom environment values override defaults."""
    settings = Settings(
        app_env="production",
        port=9000,
        embedding_provider="google",
        embedding_model="gemini-embedding-2",
        embedding_dimensions=768,
        internal_service_token="secret-token-123",
        gemini_api_key="ai-key-456",
    )
    assert settings.app_env == "production"
    assert settings.port == 9000
    assert settings.internal_service_token == "secret-token-123"
    assert settings.gemini_api_key == "ai-key-456"
    assert settings.embedding_dimensions == 768

