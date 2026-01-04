"""Generation template endpoints."""

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db_session
from app.schemas.template import TemplateCreate, TemplateResponse, TemplateUpdate

router = APIRouter(prefix="/templates", tags=["templates"])


@router.post("", response_model=TemplateResponse, status_code=201)
async def create_template(
    template_data: TemplateCreate,
    db: AsyncSession = Depends(get_db_session),
):
    """Create a new generation template."""
    from app.models.generation_template import GenerationTemplate

    template = GenerationTemplate(
        domain_id=template_data.domain_id,
        use_case=template_data.use_case,
        name=template_data.name,
        system_prompt=template_data.system_prompt,
        user_prompt_template=template_data.user_prompt_template,
        target_model_family=template_data.target_model_family,
        config=template_data.config,
    )

    db.add(template)
    await db.commit()
    await db.refresh(template)

    return TemplateResponse.model_validate(template)


@router.get("", response_model=List[TemplateResponse])
async def list_templates(
    domain_id: str = None,
    use_case: str = None,
    db: AsyncSession = Depends(get_db_session),
):
    """List templates."""
    from sqlalchemy import select
    from app.models.generation_template import GenerationTemplate

    query = select(GenerationTemplate).where(GenerationTemplate.is_active == True)  # noqa: E712

    if domain_id:
        query = query.where(GenerationTemplate.domain_id == domain_id)
    if use_case:
        query = query.where(GenerationTemplate.use_case == use_case)

    result = await db.execute(query)
    templates = list(result.scalars().all())
    return [TemplateResponse.model_validate(t) for t in templates]


@router.get("/{template_id}", response_model=TemplateResponse)
async def get_template(
    template_id: str,
    db: AsyncSession = Depends(get_db_session),
):
    """Get template by ID."""
    from sqlalchemy import select
    from app.core.exceptions import NotFoundError
    from app.models.generation_template import GenerationTemplate

    result = await db.execute(
        select(GenerationTemplate).where(GenerationTemplate.id == template_id)
    )
    template = result.scalar_one_or_none()
    if not template:
        raise NotFoundError("GenerationTemplate", template_id)
    return TemplateResponse.model_validate(template)

