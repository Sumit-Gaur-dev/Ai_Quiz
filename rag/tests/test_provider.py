"""Tests for embedding provider abstraction and factory."""

import pytest
from app.core.exceptions import ConfigurationException
from app.providers.factory import get_embedding_provider
from app.providers.gemini_embedding import GeminiEmbeddingProvider


def test_gemini_provider_properties():
    """Verify Gemini provider properties and dimensions."""
    provider = GeminiEmbeddingProvider(
        api_key="test-api-key",
        model_name="gemini-embedding-2",
        dimensions=768,
    )
    assert provider.model_name == "gemini-embedding-2"
    assert provider.dimensions == 768


def test_gemini_provider_missing_api_key():
    """Verify provider raises ConfigurationException when API key is missing."""
    with pytest.raises(ConfigurationException):
        GeminiEmbeddingProvider(api_key="", model_name="gemini-embedding-2")


def test_provider_factory_google():
    """Verify factory returns GeminiEmbeddingProvider for 'google'."""
    provider = get_embedding_provider(
        provider_name="google",
        api_key="test-key",
        model_name="gemini-embedding-2",
        dimensions=768,
    )
    assert isinstance(provider, GeminiEmbeddingProvider)
    assert provider.dimensions == 768


def test_provider_factory_unsupported():
    """Verify factory raises ConfigurationException for unknown providers."""
    with pytest.raises(ConfigurationException, match="Unsupported embedding provider"):
        get_embedding_provider(provider_name="unknown_provider", api_key="test")

