"""Google Gemini embedding provider using the official Google Gen AI Python SDK."""

from typing import List, Optional
from google import genai
from google.genai import types
from app.core.config import settings
from app.core.exceptions import ConfigurationException, ProviderException
from app.core.logging import logger
from app.providers.base import BaseEmbeddingProvider


class GeminiEmbeddingProvider(BaseEmbeddingProvider):
    """Embedding provider implementation for Google Gemini models (e.g. gemini-embedding-2).

    Uses the official google-genai SDK and supports custom output dimensionality (e.g. 768).
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: Optional[str] = None,
        dimensions: Optional[int] = None,
    ):
        if api_key is not None:
            self._api_key = api_key
        else:
            self._api_key = settings.gemini_api_key

        if not self._api_key:
            raise ConfigurationException("GEMINI_API_KEY is not configured.")

        self._model = model_name or settings.embedding_model
        self._dimensions = dimensions or settings.embedding_dimensions
        self._client = genai.Client(api_key=self._api_key)

    @property
    def model_name(self) -> str:
        return self._model

    @property
    def dimensions(self) -> int:
        return self._dimensions

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embeds a list of document chunks for retrieval indexing."""
        if not texts:
            return []

        embeddings: List[List[float]] = []
        batch_size = 50

        config = types.EmbedContentConfig(
            output_dimensionality=self._dimensions,
            task_type="RETRIEVAL_DOCUMENT",
        )

        try:
            for i in range(0, len(texts), batch_size):
                batch = texts[i : i + batch_size]
                response = self._client.models.embed_content(
                    model=self._model,
                    contents=batch,
                    config=config,
                )

                if not response.embeddings:
                    raise ProviderException(
                        f"Empty embedding response returned by model {self._model}"
                    )

                for emb in response.embeddings:
                    embeddings.append(list(emb.values))

            return embeddings
        except Exception as exc:
            if isinstance(exc, ProviderException):
                raise
            logger.error("Failed to generate document embeddings: %s", str(exc))
            raise ProviderException(
                f"Gemini embedding API error: {str(exc)}"
            ) from exc

    def embed_query(self, text: str) -> List[float]:
        """Embeds a single search query text."""
        if not text:
            return [0.0] * self._dimensions

        config = types.EmbedContentConfig(
            output_dimensionality=self._dimensions,
            task_type="RETRIEVAL_QUERY",
        )

        try:
            response = self._client.models.embed_content(
                model=self._model,
                contents=text,
                config=config,
            )

            if not response.embeddings or not response.embeddings[0].values:
                raise ProviderException(
                    f"Empty embedding response returned for query by model {self._model}"
                )

            return list(response.embeddings[0].values)
        except Exception as exc:
            if isinstance(exc, ProviderException):
                raise
            logger.error("Failed to generate query embedding: %s", str(exc))
            raise ProviderException(
                f"Gemini query embedding API error: {str(exc)}"
            ) from exc
