"""Health check API endpoints."""

from datetime import datetime, timezone
from fastapi import APIRouter
from app.core.config import settings
from app.schemas.health import HealthResponse

router = APIRouter()


@router.get("/internal/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Returns the operational health and model configuration of the RAG service."""
    return HealthResponse(
        status="ok",
        service="ai-quiz-rag",
        timestamp=datetime.now(timezone.utc).isoformat(),
        embedding_provider=settings.embedding_provider,
        embedding_model=settings.embedding_model,
        embedding_dimensions=settings.embedding_dimensions,
    )
