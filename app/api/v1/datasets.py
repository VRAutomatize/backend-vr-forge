"""Dataset endpoints."""

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db_session
from app.schemas.dataset import DatasetCreate, DatasetGenerate, DatasetResponse
from app.services.synthetic_generator import SyntheticGeneratorService

router = APIRouter(prefix="/datasets", tags=["datasets"])


@router.post("", response_model=DatasetResponse, status_code=201)
async def create_dataset(
    dataset_data: DatasetCreate,
    db: AsyncSession = Depends(get_db_session),
):
    """Create a new dataset."""
    from app.models.dataset import Dataset

    dataset = Dataset(
        domain_id=dataset_data.domain_id,
        template_id=dataset_data.template_id,
        use_case=dataset_data.use_case,
        name=dataset_data.name,
        description=dataset_data.description,
        provider=dataset_data.provider,
        target_model_family=dataset_data.target_model_family,
        generation_config=dataset_data.generation_config,
        segment_filter=dataset_data.segment_filter,
    )

    db.add(dataset)
    await db.commit()
    await db.refresh(dataset)

    return DatasetResponse.model_validate(dataset)


@router.get("", response_model=List[DatasetResponse])
async def list_datasets(
    domain_id: str = None,
    db: AsyncSession = Depends(get_db_session),
):
    """List datasets."""
    from sqlalchemy import select
    from app.models.dataset import Dataset

    query = select(Dataset)
    if domain_id:
        query = query.where(Dataset.domain_id == domain_id)

    result = await db.execute(query)
    datasets = list(result.scalars().all())
    return [DatasetResponse.model_validate(d) for d in datasets]


@router.get("/{dataset_id}", response_model=DatasetResponse)
async def get_dataset(
    dataset_id: str,
    db: AsyncSession = Depends(get_db_session),
):
    """Get dataset by ID."""
    from sqlalchemy import select
    from app.core.exceptions import NotFoundError
    from app.models.dataset import Dataset

    result = await db.execute(select(Dataset).where(Dataset.id == dataset_id))
    dataset = result.scalar_one_or_none()
    if not dataset:
        raise NotFoundError("Dataset", dataset_id)
    return DatasetResponse.model_validate(dataset)


@router.post("/generate", status_code=202)
async def generate_dataset(
    generate_data: DatasetGenerate,
    db: AsyncSession = Depends(get_db_session),
):
    """Generate synthetic dataset items."""
    items = await SyntheticGeneratorService.generate_items(
        db=db,
        dataset_id=generate_data.dataset_id,
        segment_ids=generate_data.segment_ids,
        max_items=generate_data.max_items,
        batch_size=generate_data.batch_size,
    )
    return {"status": "generating", "items_created": len(items)}

