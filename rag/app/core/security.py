"""Security and authentication utilities for internal service-to-service communication."""

import hmac
from typing import Optional
from fastapi import Header, Request
from app.core.config import settings
from app.core.exceptions import AuthenticationException


def verify_internal_token(
    x_internal_service_token: Optional[str] = Header(None, alias="X-Internal-Service-Token"),
    authorization: Optional[str] = Header(None, alias="Authorization"),
) -> str:
    """Verifies that the request carries a valid INTERNAL_SERVICE_TOKEN.

    Accepts the token via either 'X-Internal-Service-Token' header or
    'Authorization: Bearer <token>' header.
    """
    configured_token = settings.internal_service_token

    if not configured_token:
        raise AuthenticationException(
            "Service authentication is unconfigured. Set INTERNAL_SERVICE_TOKEN."
        )

    token = None

    if x_internal_service_token:
        token = x_internal_service_token.strip()
    elif authorization and authorization.startswith("Bearer "):
        token = authorization[7:].strip()

    if not token:
        raise AuthenticationException("Missing internal service authentication token")

    # Constant-time comparison to prevent timing attacks
    if not hmac.compare_digest(token, configured_token):
        raise AuthenticationException("Invalid internal service authentication token")

    return token

