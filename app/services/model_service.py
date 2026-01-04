"""Model service."""

from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.core.logging import get_logger
from app.models.model import Model

logger = get_logger(__name__)


class ModelService:
    """Service for model operations."""

    @staticmethod
    async def create(
        db: AsyncSession,
        domain_id: Optional[str],
        name: str,
        base_model: str,
        provider: str,
        model_family: Optional[str] = None,
        version: Optional[str] = None,
        config: Optional[dict[str, Any]] = None,
        capabilities: Optional[dict[str, Any]] = None,
    ) -> Model:
        """Create a new model.

        Args:
            db: Database session
            domain_id: Domain ID
            name: Model name
            base_model: Base model identifier
            provider: Model provider
            model_family: Model family
            version: Model version
            config: Model configuration
            capabilities: Model capabilities

        Returns:
            Created model
        """
        model = Model(
            domain_id=domain_id,
            name=name,
            base_model=base_model,
            provider=provider,
            model_family=model_family,
            version=version,
            config=config or {},
            capabilities=capabilities or {},
        )

        db.add(model)
        await db.commit()
        await db.refresh(model)

        logger.info("Model created", model_id=model.id, name=name)
        return model

    @staticmethod
    async def get_by_id(db: AsyncSession, model_id: str) -> Model:
        """Get model by ID.

        Args:
            db: Database session
            model_id: Model ID

        Returns:
            Model

        Raises:
            NotFoundError: If model not found
        """
        result = await db.execute(select(Model).where(Model.id == model_id))
        model = result.scalar_one_or_none()
        if not model:
            raise NotFoundError("Model", model_id)
        return model

    @staticmethod
    async def list_all(
        db: AsyncSession,
        domain_id: Optional[str] = None,
        provider: Optional[str] = None,
    ) -> list[Model]:
        """List all models.

        Args:
            db: Database session
            domain_id: Filter by domain
            provider: Filter by provider

        Returns:
            List of models
        """
        query = select(Model)

        if domain_id:
            query = query.where(Model.domain_id == domain_id)
        if provider:
            query = query.where(Model.provider == provider)

        result = await db.execute(query)
        return list(result.scalars().all())

