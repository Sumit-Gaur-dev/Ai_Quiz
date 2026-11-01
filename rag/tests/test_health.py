"""Tests for GET /internal/health endpoint."""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_internal_health_endpoint():
    """Verify that GET /internal/health returns 200 OK with expected schema."""
    response = client.get("/internal/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "ai-quiz-rag"
    assert "timestamp" in data
    assert data["embedding_provider"] == "google"
    assert data["embedding_model"] == "gemini-embedding-2"
    assert data["embedding_dimensions"] == 768

