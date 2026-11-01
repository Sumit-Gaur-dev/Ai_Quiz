"""AI Quiz Platform — RAG Service."""

from fastapi import FastAPI
from app.api.health import router as health_router

app = FastAPI(
    title="AI Quiz Platform — RAG Service",
    description="Private AI service for ingestion, retrieval, quiz generation, and evaluation.",
    version="0.1.0",
)

app.include_router(health_router)
