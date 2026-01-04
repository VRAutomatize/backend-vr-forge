"""Decorators for enhanced route logging."""

import functools
from typing import Any, Callable, Optional

from fastapi import Request

from app.core.logging import get_logger

logger = get_logger(__name__)


def log_route(
    log_request_body: bool = False,
    log_response_body: bool = False,
    log_level: str = "info",
):
    """Decorator to enhance logging for specific routes.
    
    Args:
        log_request_body: Whether to log request body (default: False)
        log_response_body: Whether to log response body (default: False)
        log_level: Log level for route entry (default: "info")
    
    Example:
        @router.post("/documents/upload")
        @log_route(log_request_body=True, log_response_body=False)
        async def upload_document(...):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Extract request if available
            request: Optional[Request] = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            
            if request:
                # Log route entry with enhanced details
                log_data = {
                    "route": func.__name__,
                    "path": request.url.path,
                    "method": request.method,
                }
                
                if log_request_body:
                    try:
                        body_bytes = await request.body()
                        if body_bytes:
                            import json
                            try:
                                log_data["request_body"] = json.loads(body_bytes.decode())
                            except:
                                log_data["request_body"] = body_bytes.decode()[:1000]
                            # Re-create request with body for downstream handlers
                            async def receive():
                                return {"type": "http.request", "body": body_bytes}
                            request._receive = receive
                    except Exception as e:
                        log_data["request_body_error"] = str(e)
                
                getattr(logger, log_level)("Route handler called", **log_data)
            
            # Call original function
            result = await func(*args, **kwargs)
            
            # Log response if enabled
            if log_response_body and request:
                try:
                    import json
                    if hasattr(result, "body"):
                        response_body = result.body
                        if isinstance(response_body, bytes):
                            log_data = {"response_body": json.loads(response_body.decode())}
                        else:
                            log_data = {"response_body": response_body}
                        logger.debug("Route response", **log_data)
                except Exception as e:
                    logger.debug("Route response logging failed", error=str(e))
            
            return result
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            # For sync functions (shouldn't happen in FastAPI, but just in case)
            return func(*args, **kwargs)
        
        # Return appropriate wrapper
        if functools.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    
    return decorator

