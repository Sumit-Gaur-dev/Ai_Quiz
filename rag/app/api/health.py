"""Health check endpoint."""

from datetime import datetime, timezone
from fastapi import APIRouter

router = APIRouter()


@router.get("/internal/health")
async def health_check():
    """Return service health status."""
    return {
        "status": "ok",
        "service": "ai-quiz-rag",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
