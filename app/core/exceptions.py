"""Custom exceptions for VRForge."""

from typing import Any, Dict, Optional


class VRForgeException(Exception):
    """Base exception for VRForge."""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class NotFoundError(VRForgeException):
    """Resource not found exception."""

    def __init__(self, resource: str, identifier: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"{resource} with id '{identifier}' not found",
            status_code=404,
            details=details,
        )


class ValidationError(VRForgeException):
    """Validation error exception."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=422,
            details=details,
        )


class ExternalServiceError(VRForgeException):
    """External service error exception."""

    def __init__(self, service: str, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"Error calling {service}: {message}",
            status_code=502,
            details=details,
        )


class StorageError(VRForgeException):
    """Storage operation error exception."""

    def __init__(self, operation: str, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"Storage {operation} failed: {message}",
            status_code=500,
            details=details,
        )


class ProcessingError(VRForgeException):
    """Document processing error exception."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"Processing failed: {message}",
            status_code=500,
            details=details,
        )

