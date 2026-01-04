"""API dependencies."""

from typing import AsyncGenerator

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_request_id
from app.db.session import get_db


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session dependency."""
    async for session in get_db():
        yield session


async def get_request(request: Request) -> Request:
    """Get FastAPI request object.
    
    This dependency can be used to access request details in route handlers.
    The request_id is automatically available via get_request_id() from logging module.
    
    Example:
        @router.get("/example")
        async def example(request: Request = Depends(get_request)):
            request_id = get_request_id()
            ...
    """
    return request

