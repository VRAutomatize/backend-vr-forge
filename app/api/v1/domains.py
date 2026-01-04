"""Domain endpoints."""

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db_session
from app.schemas.common import PaginatedResponse, PaginationParams
from app.schemas.domain import DomainCreate, DomainResponse, DomainUpdate
from app.services.domain_service import DomainService

router = APIRouter(prefix="/domains", tags=["domains"])


@router.post("", response_model=DomainResponse, status_code=201)
async def create_domain(
    domain_data: DomainCreate,
    db: AsyncSession = Depends(get_db_session),
):
    """Create a new domain."""
    domain = await DomainService.create(
        db=db,
        name=domain_data.name,
        slug=domain_data.slug,
        description=domain_data.description,
        config=domain_data.config,
    )
    return DomainResponse.model_validate(domain)


@router.get("", response_model=List[DomainResponse])
async def list_domains(
    active_only: bool = True,
    db: AsyncSession = Depends(get_db_session),
):
    """List all domains."""
    domains = await DomainService.list_all(db=db, active_only=active_only)
    return [DomainResponse.model_validate(d) for d in domains]


@router.get("/{domain_id}", response_model=DomainResponse)
async def get_domain(
    domain_id: str,
    db: AsyncSession = Depends(get_db_session),
):
    """Get domain by ID."""
    domain = await DomainService.get_by_id(db=db, domain_id=domain_id)
    return DomainResponse.model_validate(domain)


@router.put("/{domain_id}", response_model=DomainResponse)
async def update_domain(
    domain_id: str,
    domain_data: DomainUpdate,
    db: AsyncSession = Depends(get_db_session),
):
    """Update domain."""
    domain = await DomainService.update(
        db=db,
        domain_id=domain_id,
        name=domain_data.name,
        slug=domain_data.slug,
        description=domain_data.description,
        config=domain_data.config,
        is_active=domain_data.is_active,
    )
    return DomainResponse.model_validate(domain)

