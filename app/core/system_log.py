"""Service for persisting logs to database."""

from typing import Any, Dict, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger, get_request_id
from app.models.system_log import SystemLog

logger = get_logger(__name__)


class SystemLogService:
    """Service for persisting important logs to database."""

    @staticmethod
    async def log_to_database(
        db: AsyncSession,
        level: str,
        module: str,
        action: str,
        details: Optional[Dict[str, Any]] = None,
        entity_id: Optional[str] = None,
        entity_type: Optional[str] = None,
        request_id: Optional[str] = None,
    ) -> SystemLog:
        """Persist a log entry to the database.
        
        Args:
            db: Database session
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            module: Module/component name
            action: Action description
            details: Additional details as dictionary
            entity_id: Related entity ID (optional)
            entity_type: Related entity type (optional)
            request_id: Request ID (optional, auto-filled if available)
            
        Returns:
            Created SystemLog instance
        """
        # Auto-fill request_id if not provided
        if request_id is None:
            request_id = get_request_id()
        
        log_entry = SystemLog(
            level=level.upper(),
            module=module,
            action=action,
            entity_id=entity_id,
            entity_type=entity_type,
            request_id=request_id,
            details=details or {},
        )
        
        db.add(log_entry)
        await db.commit()
        await db.refresh(log_entry)
        
        return log_entry


async def log_error_to_database(
    db: AsyncSession,
    error: Exception,
    module: str,
    action: str,
    details: Optional[Dict[str, Any]] = None,
    entity_id: Optional[str] = None,
    entity_type: Optional[str] = None,
) -> SystemLog:
    """Convenience function to log errors to database.
    
    Args:
        db: Database session
        error: Exception instance
        module: Module/component name
        action: Action description
        details: Additional details
        entity_id: Related entity ID
        entity_type: Related entity type
        
    Returns:
        Created SystemLog instance
    """
    error_details = {
        "error_type": type(error).__name__,
        "error_message": str(error),
        **(details or {}),
    }
    
    return await SystemLogService.log_to_database(
        db=db,
        level="ERROR",
        module=module,
        action=action,
        details=error_details,
        entity_id=entity_id,
        entity_type=entity_type,
    )

