"""Training job endpoints."""

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db_session
from app.schemas.training_job import TrainingJobCreate, TrainingJobResponse
from app.services.training_service import TrainingService

router = APIRouter(prefix="/training-jobs", tags=["training-jobs"])


@router.post("", response_model=TrainingJobResponse, status_code=201)
async def create_training_job(
    job_data: TrainingJobCreate,
    db: AsyncSession = Depends(get_db_session),
):
    """Create a new training job."""
    job = await TrainingService.create_job(
        db=db,
        model_id=job_data.model_id,
        dataset_id=job_data.dataset_id,
        provider=job_data.provider,
        dataset_export_id=job_data.dataset_export_id,
        hyperparameters=job_data.hyperparameters,
    )
    return TrainingJobResponse.model_validate(job)


@router.get("", response_model=List[TrainingJobResponse])
async def list_training_jobs(
    model_id: str = None,
    status: str = None,
    db: AsyncSession = Depends(get_db_session),
):
    """List training jobs."""
    jobs = await TrainingService.list_all(db=db, model_id=model_id, status=status)
    return [TrainingJobResponse.model_validate(j) for j in jobs]


@router.get("/{job_id}", response_model=TrainingJobResponse)
async def get_training_job(
    job_id: str,
    db: AsyncSession = Depends(get_db_session),
):
    """Get training job by ID."""
    job = await TrainingService.get_by_id(db=db, job_id=job_id)
    return TrainingJobResponse.model_validate(job)

