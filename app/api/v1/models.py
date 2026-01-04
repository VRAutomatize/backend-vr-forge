"""Model endpoints."""

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db_session
from app.schemas.model import ModelCreate, ModelResponse
from app.services.model_service import ModelService

router = APIRouter(prefix="/models", tags=["models"])


@router.post("", response_model=ModelResponse, status_code=201)
async def create_model(
    model_data: ModelCreate,
    db: AsyncSession = Depends(get_db_session),
):
    """Register a new model."""
    model = await ModelService.create(
        db=db,
        domain_id=model_data.domain_id,
        name=model_data.name,
        base_model=model_data.base_model,
        provider=model_data.provider,
        model_family=model_data.model_family,
        version=model_data.version,
        config=model_data.config,
        capabilities=model_data.capabilities,
    )
    return ModelResponse.model_validate(model)


@router.get("", response_model=List[ModelResponse])
async def list_models(
    domain_id: str = None,
    provider: str = None,
    db: AsyncSession = Depends(get_db_session),
):
    """List models."""
    models = await ModelService.list_all(db=db, domain_id=domain_id, provider=provider)
    return [ModelResponse.model_validate(m) for m in models]


@router.get("/{model_id}", response_model=ModelResponse)
async def get_model(
    model_id: str,
    db: AsyncSession = Depends(get_db_session),
):
    """Get model by ID."""
    model = await ModelService.get_by_id(db=db, model_id=model_id)
    return ModelResponse.model_validate(model)

