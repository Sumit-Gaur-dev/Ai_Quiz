"""Health check schemas."""

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Schema for health check response."""

    status: str = Field(default="ok", description="Service operational status")
    service: str = Field(default="ai-quiz-rag", description="Service identifier")
    timestamp: str = Field(description="Current UTC timestamp in ISO 8601 format")
    embedding_provider: str = Field(description="Configured embedding provider")
    embedding_model: str = Field(description="Configured embedding model")
    embedding_dimensions: int = Field(description="Configured vector dimensions")

