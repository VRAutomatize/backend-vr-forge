"""HTTP middleware for request logging and tracking."""

import time
import uuid
from typing import Callable, Optional

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.core.config import get_settings
from app.core.logging import get_logger, set_request_id, clear_request_context

logger = get_logger(__name__)
settings = get_settings()


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging HTTP requests and responses."""

    def __init__(self, app: ASGIApp, log_request_body: bool = False, log_response_body: bool = False):
        """Initialize logging middleware.
        
        Args:
            app: ASGI application
            log_request_body: Whether to log request body (default: False, only in DEBUG)
            log_response_body: Whether to log response body (default: False)
        """
        super().__init__(app)
        self.log_request_body = log_request_body
        self.log_response_body = log_response_body

    def _get_route_name(self, request: Request) -> Optional[str]:
        """Try to identify the API route being called.
        
        Args:
            request: FastAPI request object
            
        Returns:
            Route name or None if not identifiable
        """
        # Try to get route from scope
        route = request.scope.get("route")
        if route:
            if hasattr(route, "path"):
                return route.path
            if hasattr(route, "name"):
                return route.name
        
        # Fallback: use path
        return request.url.path
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and log details.
        
        Args:
            request: FastAPI request object
            call_next: Next middleware/handler
            
        Returns:
            Response object
        """
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        set_request_id(request_id)
        
        # Start timing
        start_time = time.time()
        
        # Extract request details
        method = request.method
        path = request.url.path
        query_params = dict(request.query_params)
        client_ip = request.client.host if request.client else "unknown"
        
        # Get full URL
        full_url = str(request.url)
        
        # Try to identify route
        route_name = self._get_route_name(request)
        
        # Extract headers
        headers = dict(request.headers)
        sensitive_headers = {"authorization", "cookie", "x-api-key", "x-auth-token"}
        filtered_headers = {
            k: "***REDACTED***" if k.lower() in sensitive_headers else v
            for k, v in headers.items()
        }
        
        # Extract User-Agent and Referer if configured
        user_agent = headers.get("user-agent") if settings.LOG_USER_AGENT else None
        referer = headers.get("referer") if settings.LOG_REFERER else None
        origin = headers.get("origin")
        
        # Build log data based on detail level
        log_detail_level = settings.LOG_REQUEST_DETAILS.lower()
        
        if log_detail_level == "minimal":
            log_data = {
                "method": method,
                "path": path,
                "client_ip": client_ip,
            }
        elif log_detail_level == "verbose":
            log_data = {
                "method": method,
                "path": path,
                "url": full_url,
                "route": route_name,
                "client_ip": client_ip,
                "user_agent": user_agent,
                "referer": referer,
                "origin": origin,
                "headers": filtered_headers,
            }
            if query_params:
                log_data["query_params"] = query_params
        else:  # standard
            log_data = {
                "method": method,
                "path": path,
                "url": full_url,
                "route": route_name,
                "client_ip": client_ip,
            }
            if user_agent:
                log_data["user_agent"] = user_agent
            if referer:
                log_data["referer"] = referer
            if origin:
                log_data["origin"] = origin
            if query_params:
                log_data["query_params"] = query_params
        
        # Log request body if enabled (and in DEBUG mode)
        if self.log_request_body:
            try:
                # Read body without consuming it
                body_bytes = await request.body()
                if body_bytes:
                    # Try to decode as JSON, fallback to string
                    try:
                        import json
                        log_data["body"] = json.loads(body_bytes.decode())
                    except:
                        log_data["body"] = body_bytes.decode()[:500]  # Limit size
                    # Re-create request with body for downstream handlers
                    async def receive():
                        return {"type": "http.request", "body": body_bytes}
                    request._receive = receive
            except Exception as e:
                log_data["body_error"] = str(e)
        
        logger.info("Request received", **log_data)
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000
            
            # Extract response details
            status_code = response.status_code
            
            # Determine log level based on status code
            if status_code >= 500:
                log_level = "error"
            elif status_code >= 400:
                log_level = "warning"
            else:
                log_level = "info"
            
            # Log response
            log_detail_level = settings.LOG_REQUEST_DETAILS.lower()
            
            if log_detail_level == "minimal":
                response_log = {
                    "method": method,
                    "path": path,
                    "status_code": status_code,
                    "duration_ms": round(duration_ms, 2),
                }
            elif log_detail_level == "verbose":
                response_log = {
                    "method": method,
                    "path": path,
                    "url": full_url,
                    "route": route_name,
                    "status_code": status_code,
                    "duration_ms": round(duration_ms, 2),
                }
                # Add response headers (filtered)
                response_headers = dict(response.headers)
                filtered_response_headers = {
                    k: "***REDACTED***" if k.lower() in sensitive_headers else v
                    for k, v in response_headers.items()
                }
                response_log["response_headers"] = filtered_response_headers
            else:  # standard
                response_log = {
                    "method": method,
                    "path": path,
                    "url": full_url,
                    "route": route_name,
                    "status_code": status_code,
                    "duration_ms": round(duration_ms, 2),
                }
            
            # Log response body if enabled
            if self.log_response_body:
                # Note: This requires reading the response body, which consumes it
                # Only use for debugging specific routes
                pass
            
            # Log with appropriate level
            getattr(logger, log_level)("Request completed", **response_log)
            
            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            
            return response
            
        except Exception as e:
            # Calculate duration even on error
            duration_ms = (time.time() - start_time) * 1000
            
            # Build error log based on detail level
            log_detail_level = settings.LOG_REQUEST_DETAILS.lower()
            
            if log_detail_level == "minimal":
                error_log = {
                    "method": method,
                    "path": path,
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "duration_ms": round(duration_ms, 2),
                }
            else:
                error_log = {
                    "method": method,
                    "path": path,
                    "url": full_url,
                    "route": route_name,
                    "client_ip": client_ip,
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "duration_ms": round(duration_ms, 2),
                }
            
            logger.error("Request failed", **error_log, exc_info=True)
            
            # Re-raise exception
            raise
        finally:
            # Clear context
            clear_request_context()


class CORSLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging CORS-related events."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and log CORS events.
        
        Args:
            request: FastAPI request object
            call_next: Next middleware/handler
            
        Returns:
            Response object
        """
        origin = request.headers.get("origin")
        method = request.method
        
        # Check if this is a CORS preflight request
        if method == "OPTIONS":
            logger.debug(
                "CORS preflight request",
                origin=origin,
                method=method,
                access_control_request_method=request.headers.get("access-control-request-method"),
                access_control_request_headers=request.headers.get("access-control-request-headers"),
            )
        
        response = await call_next(request)
        
        # Log CORS response headers
        cors_headers = {
            k: v for k, v in response.headers.items()
            if k.lower().startswith("access-control-")
        }
        
        if cors_headers:
            logger.debug(
                "CORS headers set",
                origin=origin,
                cors_headers=cors_headers,
            )
        
        # Check if CORS might have been blocked (no CORS headers on cross-origin request)
        if origin and origin != request.url.netloc:
            if not cors_headers and response.status_code == 200:
                logger.warning(
                    "Possible CORS issue",
                    origin=origin,
                    method=method,
                    path=request.url.path,
                    message="Cross-origin request without CORS headers",
                )
        
        return response

