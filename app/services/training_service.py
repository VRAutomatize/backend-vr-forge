"""Training job service."""

from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.core.logging import get_logger
from app.models.training_job import TrainingJob

logger = get_logger(__name__)


class TrainingService:
    """Service for training job operations."""

    @staticmethod
    async def create_job(
        db: AsyncSession,
        model_id: str,
        dataset_id: str,
        provider: str,
        dataset_export_id: Optional[str] = None,
        hyperparameters: Optional[dict[str, Any]] = None,
    ) -> TrainingJob:
        """Create a new training job.

        Args:
            db: Database session
            model_id: Model ID
            dataset_id: Dataset ID
            provider: Training provider
            dataset_export_id: Dataset export ID
            hyperparameters: Training hyperparameters

        Returns:
            Created training job

        Raises:
            NotFoundError: If model or dataset not found
        """
        # Verify model exists
        from app.services.model_service import ModelService
        await ModelService.get_by_id(db, model_id)

        # Verify dataset exists
        from app.models.dataset import Dataset
        result = await db.execute(select(Dataset).where(Dataset.id == dataset_id))
        dataset = result.scalar_one_or_none()
        if not dataset:
            raise NotFoundError("Dataset", dataset_id)

        job = TrainingJob(
            model_id=model_id,
            dataset_id=dataset_id,
            dataset_export_id=dataset_export_id,
            provider=provider,
            status="pending",
            hyperparameters=hyperparameters or {},
        )

        db.add(job)
        await db.commit()
        await db.refresh(job)

        logger.info("Training job created", job_id=job.id, model_id=model_id)
        return job

    @staticmethod
    async def get_by_id(db: AsyncSession, job_id: str) -> TrainingJob:
        """Get training job by ID.

        Args:
            db: Database session
            job_id: Job ID

        Returns:
            Training job

        Raises:
            NotFoundError: If job not found
        """
        result = await db.execute(select(TrainingJob).where(TrainingJob.id == job_id))
        job = result.scalar_one_or_none()
        if not job:
            raise NotFoundError("TrainingJob", job_id)
        return job

    @staticmethod
    async def list_all(
        db: AsyncSession,
        model_id: Optional[str] = None,
        status: Optional[str] = None,
    ) -> list[TrainingJob]:
        """List all training jobs.

        Args:
            db: Database session
            model_id: Filter by model
            status: Filter by status

        Returns:
            List of training jobs
        """
        query = select(TrainingJob)

        if model_id:
            query = query.where(TrainingJob.model_id == model_id)
        if status:
            query = query.where(TrainingJob.status == status)

        from sqlalchemy import desc
        result = await db.execute(query.order_by(desc(TrainingJob.created_at)))
        return list(result.scalars().all())

