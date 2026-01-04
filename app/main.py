"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.exceptions import VRForgeException
from app.core.logging import configure_logging, get_logger, get_request_id
from app.core.middleware import CORSLoggingMiddleware, LoggingMiddleware

settings = get_settings()
configure_logging(settings.LOG_LEVEL, settings.APP_ENV)
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    logger.info("Starting VRForge application", app_name=settings.APP_NAME, version="0.1.0")
    yield
    logger.info("Shutting down VRForge application")


app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    description="VRForge - Platform for forging VR AI models",
    lifespan=lifespan,
)

# Add logging middleware (must be first to capture all requests)
# Enable request body logging only in DEBUG mode
log_request_body = settings.LOG_LEVEL.upper() == "DEBUG"
app.add_middleware(
    LoggingMiddleware,
    log_request_body=log_request_body,
    log_response_body=False,  # Disabled by default, enable per-route if needed
)

# Add CORS logging middleware
app.add_middleware(CORSLoggingMiddleware)

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
async def vrforge_exception_handler(request: Request, exc: VRForgeException):
    """Handle VRForge exceptions with logging."""
    request_id = get_request_id()
    
    logger.error(
        "VRForge exception handled",
        exception_type=exc.__class__.__name__,
        message=exc.message,
        status_code=exc.status_code,
        details=exc.details,
        path=request.url.path,
        method=request.method,
    )
    
    response_data = {
        "error": exc.message,
        "details": exc.details,
    }
    
    if request_id:
        response_data["request_id"] = request_id
    
    return JSONResponse(
        status_code=exc.status_code,
        content=response_data,
        headers={"X-Request-ID": request_id} if request_id else {},
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions with logging."""
    request_id = get_request_id()
    
    logger.error(
        "Unhandled exception",
        exception_type=type(exc).__name__,
        exception_message=str(exc),
        path=request.url.path,
        method=request.method,
        exc_info=True,
    )
    
    response_data = {
        "error": "Internal server error",
        "details": {"message": str(exc)} if settings.DEBUG else {},
    }
    
    if request_id:
        response_data["request_id"] = request_id
    
    return JSONResponse(
        status_code=500,
        content=response_data,
        headers={"X-Request-ID": request_id} if request_id else {},
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

