"""Tests for internal service authentication and protection."""

from fastapi.testclient import TestClient
from app.core.config import settings
from app.main import app

client = TestClient(app)


def test_protected_route_without_token():
    """Protected routes must reject requests with no token header."""
    response = client.get("/internal/auth-check")
    assert response.status_code == 401
    data = response.json()
    assert data["error"]["code"] == "UNAUTHORIZED"


def test_protected_route_with_invalid_token():
    """Protected routes must reject requests with an incorrect token."""
    response = client.get(
        "/internal/auth-check",
        headers={"X-Internal-Service-Token": "invalid-wrong-token"},
    )
    assert response.status_code == 401
    data = response.json()
    assert data["error"]["code"] == "UNAUTHORIZED"


def test_protected_route_with_valid_x_header():
    """Protected routes must accept requests with valid X-Internal-Service-Token."""
    response = client.get(
        "/internal/auth-check",
        headers={"X-Internal-Service-Token": settings.internal_service_token},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "authenticated"


def test_protected_route_with_valid_bearer_token():
    """Protected routes must accept requests with valid Authorization: Bearer <token>."""
    response = client.get(
        "/internal/auth-check",
        headers={"Authorization": f"Bearer {settings.internal_service_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "authenticated"

