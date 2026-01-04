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
            structlog.processors.add_logger_name
        )
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
            structlog.dev.ConsoleRenderer(colors=True),
        ])
    else:
        # Production: JSON output
        processors.append(structlog.processors.JSONRenderer())
    
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

