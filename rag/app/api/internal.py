"""Internal protected endpoints requiring service authentication."""

from fastapi import APIRouter, Depends
from app.core.security import verify_internal_token

router = APIRouter(prefix="/internal")


@router.get("/auth-check")
async def verify_auth_status(token: str = Depends(verify_internal_token)):
    """Verifies that the caller has provided a valid INTERNAL_SERVICE_TOKEN."""
    return {
        "status": "authenticated",
        "message": "Valid internal service token provided",
    }
