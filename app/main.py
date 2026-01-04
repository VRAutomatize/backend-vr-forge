"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.exceptions import VRForgeException
from app.core.logging import configure_logging, get_logger

settings = get_settings()
configure_logging(settings.LOG_LEVEL)
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    logger.info("Starting VRForge application")
    yield
    logger.info("Shutting down VRForge application")


app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    description="VRForge - Platform for forging VR AI models",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(VRForgeException)
async def vrforge_exception_handler(request, exc: VRForgeException):
    """Handle VRForge exceptions."""
    from fastapi.responses import JSONResponse

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.message,
            "details": exc.details,
        },
    )


# Include routers
# Health check at root level (no prefix) for EasyPanel
from app.api.v1 import health
app.include_router(health.router, tags=["health"])
# API v1 routes
app.include_router(api_router, prefix="/api/v1")

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": settings.APP_NAME,
        "version": "0.1.0",
        "status": "running",
    }

