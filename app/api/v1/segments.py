"""Segment endpoints."""

from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db_session
from app.schemas.segment import SegmentResponse
from app.services.segmenter_service import SegmenterService

router = APIRouter(prefix="/segments", tags=["segments"])


@router.get("", response_model=List[SegmentResponse])
async def list_segments(
    domain_id: str = Query(None),
    document_id: str = Query(None),
    use_case: str = Query(None),
    segment_type: str = Query(None),
    db: AsyncSession = Depends(get_db_session),
):
    """List segments with filters."""
    segments = await SegmenterService.get_segments(
        db=db,
        domain_id=domain_id,
        document_id=document_id,
        use_case=use_case,
        segment_type=segment_type,
    )
    return [SegmentResponse.model_validate(s) for s in segments]


@router.get("/{segment_id}", response_model=SegmentResponse)
async def get_segment(
    segment_id: str,
    db: AsyncSession = Depends(get_db_session),
):
    """Get segment by ID."""
    from sqlalchemy import select
    from app.core.exceptions import NotFoundError
    from app.models.segment import Segment

    result = await db.execute(select(Segment).where(Segment.id == segment_id))
    segment = result.scalar_one_or_none()
    if not segment:
        raise NotFoundError("Segment", segment_id)
    return SegmentResponse.model_validate(segment)

