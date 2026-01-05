"""Database session management."""

from typing import AsyncGenerator
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings

settings = get_settings()


def _clean_database_url_for_asyncpg(url: str) -> str:
    """Remove query parameters incompatible with asyncpg from database URL.
    
    The asyncpg driver doesn't support 'sslmode' parameter (which is specific
    to psycopg2). This function removes it and other incompatible parameters.
    
    Args:
        url: Database URL string
        
    Returns:
        Cleaned URL string compatible with asyncpg
    """
    parsed = urlparse(url)
    
    # Parse query parameters
    query_params = parse_qs(parsed.query)
    
    # Remove incompatible parameters
    incompatible_params = ['sslmode']
    for param in incompatible_params:
        query_params.pop(param, None)
    
    # Rebuild query string
    new_query = urlencode(query_params, doseq=True)
    
    # Reconstruct URL
    cleaned_url = urlunparse((
        parsed.scheme,
        parsed.netloc,
        parsed.path,
        parsed.params,
        new_query,
        parsed.fragment
    ))
    
    return cleaned_url


# Process database URL to remove incompatible parameters
cleaned_database_url = _clean_database_url_for_asyncpg(settings.DATABASE_URL)

# Create async engine
engine = create_async_engine(
    cleaned_database_url,
    echo=settings.DEBUG,
    future=True,
    pool_pre_ping=True,
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

