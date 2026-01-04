"""Review endpoints."""

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db_session
from app.schemas.review import PendingReviewItem, ReviewApprove, ReviewEdit, ReviewReject, ReviewResponse
from app.services.review_service import ReviewService

router = APIRouter(prefix="/dataset/review", tags=["review"])


@router.get("/pending", response_model=List[PendingReviewItem])
async def list_pending(
    dataset_id: str = None,
    db: AsyncSession = Depends(get_db_session),
):
    """List pending review items."""
    items = await ReviewService.list_pending(db=db, dataset_id=dataset_id)

    # Format response
    result = []
    for item in items:
        from sqlalchemy import select
        from app.models.dataset import Dataset
        dataset_result = await db.execute(select(Dataset).where(Dataset.id == item.dataset_id))
        dataset = dataset_result.scalar_one()

        result.append(
            PendingReviewItem(
                id=item.id,
                dataset_id=item.dataset_id,
                dataset_name=dataset.name,
                instruction=item.instruction,
                input_text=item.input_text,
                ideal_response=item.ideal_response,
                bad_response=item.bad_response,
                explanation=item.explanation,
                quality_score=item.quality_score,
                quality_flags=item.quality_flags,
                created_at=item.created_at,
            )
        )

    return result


@router.post("/{item_id}/approve", response_model=ReviewResponse)
async def approve_item(
    item_id: str,
    approve_data: ReviewApprove,
    db: AsyncSession = Depends(get_db_session),
):
    """Approve a dataset item."""
    review = await ReviewService.approve(
        db=db,
        item_id=item_id,
        reviewer_id=approve_data.reviewer_id,
        justification=approve_data.justification,
    )
    return ReviewResponse.model_validate(review)


@router.post("/{item_id}/reject", response_model=ReviewResponse)
async def reject_item(
    item_id: str,
    reject_data: ReviewReject,
    db: AsyncSession = Depends(get_db_session),
):
    """Reject a dataset item."""
    review = await ReviewService.reject(
        db=db,
        item_id=item_id,
        reviewer_id=reject_data.reviewer_id,
        justification=reject_data.justification,
    )
    return ReviewResponse.model_validate(review)


@router.post("/{item_id}/edit", response_model=ReviewResponse)
async def edit_item(
    item_id: str,
    edit_data: ReviewEdit,
    db: AsyncSession = Depends(get_db_session),
):
    """Edit a dataset item."""
    review = await ReviewService.edit(
        db=db,
        item_id=item_id,
        instruction=edit_data.instruction,
        input_text=edit_data.input_text,
        ideal_response=edit_data.ideal_response,
        bad_response=edit_data.bad_response,
        explanation=edit_data.explanation,
        reviewer_id=edit_data.reviewer_id,
        justification=edit_data.justification,
    )
    return ReviewResponse.model_validate(review)


@router.get("/{item_id}/history", response_model=List[ReviewResponse])
async def get_review_history(
    item_id: str,
    db: AsyncSession = Depends(get_db_session),
):
    """Get review history for an item."""
    from sqlalchemy import select
    from app.models.review import DatasetReview

    result = await db.execute(
        select(DatasetReview).where(DatasetReview.dataset_item_id == item_id).order_by(DatasetReview.created_at)
    )
    reviews = list(result.scalars().all())
    return [ReviewResponse.model_validate(r) for r in reviews]

