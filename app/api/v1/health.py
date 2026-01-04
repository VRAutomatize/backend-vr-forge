"""Health check endpoints."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check():
    """Health check endpoint for EasyPanel."""
    return {"status": "healthy"}


@router.get("/health/detailed")
async def health_check_detailed():
    """Detailed health check endpoint."""
    return {
        "status": "healthy",
        "service": "VRForge",
        "version": "0.1.0",
    }

