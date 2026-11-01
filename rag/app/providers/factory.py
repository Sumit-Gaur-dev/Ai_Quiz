"""Factory for instantiating embedding model providers."""

from typing import Optional
from app.core.config import settings
from app.core.exceptions import ConfigurationException
from app.providers.base import BaseEmbeddingProvider
from app.providers.gemini_embedding import GeminiEmbeddingProvider


def get_embedding_provider(
    provider_name: Optional[str] = None,
    api_key: Optional[str] = None,
    model_name: Optional[str] = None,
    dimensions: Optional[int] = None,
) -> BaseEmbeddingProvider:
    """Returns an embedding provider based on configuration or explicit parameters."""
    provider = (provider_name or settings.embedding_provider).lower()

    if provider in ("google", "gemini"):
        return GeminiEmbeddingProvider(
            api_key=api_key,
            model_name=model_name,
            dimensions=dimensions,
        )

    raise ConfigurationException(f"Unsupported embedding provider: {provider}")

