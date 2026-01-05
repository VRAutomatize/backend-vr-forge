"""Custom logging handler for Gunicorn to capture invalid HTTP requests with context."""

import logging
import re
from typing import Optional

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()


class GunicornLogHandler(logging.Handler):
    """Custom handler to intercept Gunicorn logs and add context.
    
    This handler specifically targets "Invalid HTTP request" warnings
    and attempts to extract any available context information.
    """
    
    def __init__(self):
        """Initialize the Gunicorn log handler."""
        super().__init__()
        # Pattern to match invalid HTTP request warnings
        self.invalid_request_pattern = re.compile(
            r"Invalid HTTP request",
            re.IGNORECASE
        )
        
    def emit(self, record: logging.LogRecord) -> None:
        """Process log record and enhance with context if needed.
        
        Args:
            record: Log record from Gunicorn
        """
        # Only process if logging invalid requests is enabled
        if not settings.LOG_INVALID_REQUESTS:
            return
        
        # Get the log message
        message = record.getMessage()
        
        # Check if this is an "Invalid HTTP request" warning
        if record.levelno == logging.WARNING and self.invalid_request_pattern.search(message):
            # Try to extract context from the record
            context = self._extract_context(record)
            
            # Log with our structured logger
            logger.warning(
                "Invalid HTTP request detected",
                gunicorn_message=message,
                gunicorn_level=logging.getLevelName(record.levelno),
                **context
            )
        elif record.levelno >= logging.ERROR:
            # Also log errors from Gunicorn with context
            context = self._extract_context(record)
            logger.error(
                "Gunicorn error",
                gunicorn_message=message,
                gunicorn_level=logging.getLevelName(record.levelno),
                **context
            )
    
    def _extract_context(self, record: logging.LogRecord) -> dict:
        """Extract available context from log record.
        
        Args:
            record: Log record
            
        Returns:
            Dictionary with extracted context
        """
        context = {}
        
        # Extract process/worker info if available
        if hasattr(record, "process"):
            context["process_id"] = record.process
        if hasattr(record, "thread"):
            context["thread_id"] = record.thread
        
        # Extract filename and line number
        if hasattr(record, "pathname"):
            context["source_file"] = record.pathname
        if hasattr(record, "lineno"):
            context["source_line"] = record.lineno
        
        # Extract function name if available
        if hasattr(record, "funcName"):
            context["function"] = record.funcName
        
        # Try to extract any additional info from the message
        message = record.getMessage()
        
        # Look for IP addresses in the message
        ip_pattern = re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b')
        ips = ip_pattern.findall(message)
        if ips:
            context["detected_ips"] = ips
        
        # Look for port numbers
        port_pattern = re.compile(r':(\d{4,5})\b')
        ports = port_pattern.findall(message)
        if ports:
            context["detected_ports"] = ports
        
        return context


def setup_gunicorn_logging() -> None:
    """Setup custom logging handler for Gunicorn.
    
    This function should be called during application startup
    to intercept Gunicorn logs and enhance them with context.
    """
    if not settings.LOG_INVALID_REQUESTS:
        return
    
    # Get the Gunicorn logger
    gunicorn_logger = logging.getLogger("gunicorn.error")
    
    # Add our custom handler
    handler = GunicornLogHandler()
    handler.setLevel(logging.WARNING)  # Only capture warnings and above
    
    # Remove any existing handlers of the same type to avoid duplicates
    for existing_handler in gunicorn_logger.handlers[:]:
        if isinstance(existing_handler, GunicornLogHandler):
            gunicorn_logger.removeHandler(existing_handler)
    
    # Add our handler
    gunicorn_logger.addHandler(handler)
    
    logger.info("Gunicorn logging handler configured", log_invalid_requests=settings.LOG_INVALID_REQUESTS)

