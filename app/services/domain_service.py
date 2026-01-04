"""Domain service."""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.core.logging import get_logger
from app.models.domain import Domain

logger = get_logger(__name__)


class DomainService:
    """Service for domain operations."""

    @staticmethod
    async def create(
        db: AsyncSession,
        name: str,
        slug: str,
        description: Optional[str] = None,
        config: Optional[dict] = None,
    ) -> Domain:
        """Create a new domain.

        Args:
            db: Database session
            name: Domain name
            slug: Domain slug
            description: Domain description
            config: Domain configuration

        Returns:
            Created domain
        """
        domain = Domain(
            name=name,
            slug=slug,
            description=description,
            config=config or {},
        )
        db.add(domain)
        await db.commit()
        await db.refresh(domain)
        logger.info("Domain created", domain_id=domain.id, name=name)
        return domain

    @staticmethod
    async def get_by_id(db: AsyncSession, domain_id: str) -> Domain:
        """Get domain by ID.

        Args:
            db: Database session
            domain_id: Domain ID

        Returns:
            Domain

        Raises:
            NotFoundError: If domain not found
        """
        result = await db.execute(select(Domain).where(Domain.id == domain_id))
        domain = result.scalar_one_or_none()
        if not domain:
            raise NotFoundError("Domain", domain_id)
        return domain

    @staticmethod
    async def get_by_slug(db: AsyncSession, slug: str) -> Optional[Domain]:
        """Get domain by slug.

        Args:
            db: Database session
            slug: Domain slug

        Returns:
            Domain or None
        """
        result = await db.execute(select(Domain).where(Domain.slug == slug))
        return result.scalar_one_or_none()

    @staticmethod
    async def list_all(db: AsyncSession, active_only: bool = True) -> list[Domain]:
        """List all domains.

        Args:
            db: Database session
            active_only: Return only active domains

        Returns:
            List of domains
        """
        query = select(Domain)
        if active_only:
            query = query.where(Domain.is_active == True)  # noqa: E712
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def update(
        db: AsyncSession,
        domain_id: str,
        name: Optional[str] = None,
        slug: Optional[str] = None,
        description: Optional[str] = None,
        config: Optional[dict] = None,
        is_active: Optional[bool] = None,
    ) -> Domain:
        """Update domain.

        Args:
            db: Database session
            domain_id: Domain ID
            name: New name
            slug: New slug
            description: New description
            config: New config
            is_active: New active status

        Returns:
            Updated domain

        Raises:
            NotFoundError: If domain not found
        """
        domain = await DomainService.get_by_id(db, domain_id)

        if name is not None:
            domain.name = name
        if slug is not None:
            domain.slug = slug
        if description is not None:
            domain.description = description
        if config is not None:
            domain.config = config
        if is_active is not None:
            domain.is_active = is_active

        await db.commit()
        await db.refresh(domain)
        logger.info("Domain updated", domain_id=domain_id)
        return domain

