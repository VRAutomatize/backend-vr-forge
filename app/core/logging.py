"""Structured logging configuration."""

import logging
import sys
from datetime import datetime
from typing import Any, Optional

import structlog
from structlog.processors import CallsiteParameter


def _add_timestamp(logger, method_name, event_dict):
    """Add ISO 8601 timestamp to log event."""
    event_dict["timestamp"] = datetime.utcnow().isoformat() + "Z"
    return event_dict


def _colorize_level(logger, method_name, event_dict):
    """Add color to log level for better readability."""
    level = event_dict.get("level", "").upper()
    colors = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",   # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",   # Red
        "CRITICAL": "\033[35m",  # Magenta
    }
    reset = "\033[0m"
    if level in colors:
        event_dict["level"] = f"{colors[level]}{level}{reset}"
    return event_dict


def _format_request_id(logger, method_name, event_dict):
    """Format request_id for better visibility."""
    if "request_id" in event_dict:
        event_dict["request_id"] = f"[req:{event_dict['request_id'][:8]}]"
    return event_dict


def _format_request_log(logger, method_name, event_dict):
    """Format HTTP request logs for better readability in development."""
    # Only format if this is a request-related log
    event = event_dict.get("event", "")
    if "request" in event.lower() or "HTTP" in event.upper() or "invalid" in event.lower():
        # Extract key information
        method = event_dict.get("method", "")
        path = event_dict.get("path", "")
        url = event_dict.get("url", "")
        route = event_dict.get("route", "")
        status_code = event_dict.get("status_code")
        duration_ms = event_dict.get("duration_ms")
        client_ip = event_dict.get("client_ip", "")
        
        # Build formatted message with better structure
        parts = []
        if method and path:
            if url:
                # Show full URL if available
                parts.append(f"{method} {url}")
            else:
                parts.append(f"{method} {path}")
        
        if route and route != path:
            parts.append(f"Route: {route}")
        
        if client_ip and client_ip != "unknown":
            parts.append(f"Client: {client_ip}")
        
        if status_code is not None:
            if 200 <= status_code < 300:
                status_text = "OK"
            elif status_code >= 400:
                status_text = "ERROR"
            else:
                status_text = ""
            if status_text:
                parts.append(f"Status: {status_code} {status_text}")
            else:
                parts.append(f"Status: {status_code}")
        
        if duration_ms is not None:
            parts.append(f"Duration: {duration_ms}ms")
        
        # Add formatted info to event_dict for console renderer
        if parts:
            # Create a more readable format
            formatted_msg = " → ".join(parts)
            event_dict["_formatted"] = formatted_msg
    
    return event_dict


def _format_url(logger, method_name, event_dict):
    """Extract and format URL information."""
    url = event_dict.get("url")
    if url:
        # Try to extract components
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            if parsed.scheme and parsed.netloc:
                event_dict["url_scheme"] = parsed.scheme
                event_dict["url_host"] = parsed.netloc
                event_dict["url_path"] = parsed.path
                if parsed.query:
                    event_dict["url_query"] = parsed.query
        except Exception:
            pass  # Ignore parsing errors
    
    return event_dict


def configure_logging(log_level: str = "INFO", app_env: str = "development") -> None:
    """Configure structured logging for the application.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        app_env: Application environment (development, production)
    """
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper()),
    )

    # Determine if we're in development mode
    is_dev = app_env.lower() == "development" or log_level.upper() == "DEBUG"
    
    # Base processors
    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]
    
    # Add call site info in debug mode
    if is_dev:
        processors.append(
            structlog.processors.CallsiteParameterAdder(
                parameters=[CallsiteParameter.FILENAME, CallsiteParameter.LINENO]
            )
        )
    
    # Add timestamp processor
    processors.append(_add_timestamp)
    
    # Choose renderer based on environment
    if is_dev:
        # Development: Pretty console output with colors
        processors.extend([
            _colorize_level,
            _format_request_id,
            _format_request_log,
            _format_url,
            structlog.dev.ConsoleRenderer(colors=True),
        ])
    else:
        # Production: JSON output
        processors.extend([
            _format_url,
            structlog.processors.JSONRenderer(),
        ])
    
    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, log_level.upper())
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> Any:
    """Get a structured logger instance.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Structured logger instance
    """
    return structlog.get_logger(name)


def set_request_id(request_id: str) -> None:
    """Set request ID in context for structured logging.
    
    Args:
        request_id: Unique request identifier (UUID)
    """
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(request_id=request_id)


def get_request_id() -> Optional[str]:
    """Get current request ID from context.
    
    Returns:
        Current request ID or None
    """
    context = structlog.contextvars.get_contextvars()
    return context.get("request_id")


def clear_request_context() -> None:
    """Clear request context variables."""
    structlog.contextvars.clear_contextvars()

