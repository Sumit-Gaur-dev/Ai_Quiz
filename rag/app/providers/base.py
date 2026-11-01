"""Base abstraction for embedding model providers."""

from abc import ABC, abstractmethod
from typing import List
from langchain_core.embeddings import Embeddings


class BaseEmbeddingProvider(Embeddings, ABC):
    """Abstract base class for embedding providers.

    Conforms to LangChain's Embeddings interface so it can be seamlessly used
    with LangChain document loaders, splitters, vector stores, and retrievers.
    """

    @property
    @abstractmethod
    def model_name(self) -> str:
        """The identifier of the embedding model."""
        pass

    @property
    @abstractmethod
    def dimensions(self) -> int:
        """The output dimensionality of the generated vectors."""
        pass

    @abstractmethod
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a batch of document texts."""
        pass

    @abstractmethod
    def embed_query(self, text: str) -> List[float]:
        """Embed a single query text."""
        pass

