"""Review service for human review of dataset items."""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.core.logging import get_logger
from app.models.dataset import Dataset
from app.models.dataset_item import DatasetItem
from app.models.review import DatasetReview

logger = get_logger(__name__)


class ReviewService:
    """Service for reviewing dataset items."""

    @staticmethod
    async def list_pending(
        db: AsyncSession,
        dataset_id: Optional[str] = None,
    ) -> list[DatasetItem]:
        """List pending review items.

        Args:
            db: Database session
            dataset_id: Filter by dataset ID

        Returns:
            List of pending items
        """
        query = select(DatasetItem).where(DatasetItem.status == "pending_review")

        if dataset_id:
            query = query.where(DatasetItem.dataset_id == dataset_id)

        result = await db.execute(query.order_by(DatasetItem.created_at))
        return list(result.scalars().all())

    @staticmethod
    async def approve(
        db: AsyncSession,
        item_id: str,
        reviewer_id: Optional[str] = None,
        justification: Optional[str] = None,
    ) -> DatasetReview:
        """Approve a dataset item.

        Args:
            db: Database session
            item_id: Dataset item ID
            reviewer_id: Reviewer identifier
            justification: Approval justification

        Returns:
            Created review record

        Raises:
            NotFoundError: If item not found
        """
        result = await db.execute(select(DatasetItem).where(DatasetItem.id == item_id))
        item = result.scalar_one_or_none()
        if not item:
            raise NotFoundError("DatasetItem", item_id)

        # Create review record
        review = DatasetReview(
            dataset_item_id=item_id,
            action="approve",
            reviewer_id=reviewer_id,
            justification=justification,
            previous_values={"status": item.status},
            new_values={"status": "approved"},
        )

        # Update item status
        old_status = item.status
        item.status = "approved"

        # Update dataset stats
        dataset_result = await db.execute(
            select(Dataset).where(Dataset.id == item.dataset_id)
        )
        dataset = dataset_result.scalar_one()
        dataset.pending_items = max(0, dataset.pending_items - 1)
        dataset.approved_items += 1

        db.add(review)
        await db.commit()
        await db.refresh(review)

        logger.info("Item approved", item_id=item_id, reviewer_id=reviewer_id)
        return review

    @staticmethod
    async def reject(
        db: AsyncSession,
        item_id: str,
        reviewer_id: Optional[str] = None,
        justification: str = "",
    ) -> DatasetReview:
        """Reject a dataset item.

        Args:
            db: Database session
            item_id: Dataset item ID
            reviewer_id: Reviewer identifier
            justification: Rejection reason

        Returns:
            Created review record

        Raises:
            NotFoundError: If item not found
        """
        result = await db.execute(select(DatasetItem).where(DatasetItem.id == item_id))
        item = result.scalar_one_or_none()
        if not item:
            raise NotFoundError("DatasetItem", item_id)

        # Create review record
        review = DatasetReview(
            dataset_item_id=item_id,
            action="reject",
            reviewer_id=reviewer_id,
            justification=justification,
            previous_values={"status": item.status},
            new_values={"status": "rejected"},
        )

        # Update item status
        item.status = "rejected"

        # Update dataset stats
        dataset_result = await db.execute(
            select(Dataset).where(Dataset.id == item.dataset_id)
        )
        dataset = dataset_result.scalar_one()
        dataset.pending_items = max(0, dataset.pending_items - 1)
        dataset.rejected_items += 1

        db.add(review)
        await db.commit()
        await db.refresh(review)

        logger.info("Item rejected", item_id=item_id, reviewer_id=reviewer_id)
        return review

    @staticmethod
    async def edit(
        db: AsyncSession,
        item_id: str,
        instruction: Optional[str] = None,
        input_text: Optional[str] = None,
        ideal_response: Optional[str] = None,
        bad_response: Optional[str] = None,
        explanation: Optional[str] = None,
        reviewer_id: Optional[str] = None,
        justification: Optional[str] = None,
    ) -> DatasetReview:
        """Edit a dataset item.

        Args:
            db: Database session
            item_id: Dataset item ID
            instruction: New instruction
            input_text: New input text
            ideal_response: New ideal response
            bad_response: New bad response
            explanation: New explanation
            reviewer_id: Reviewer identifier
            justification: Edit justification

        Returns:
            Created review record

        Raises:
            NotFoundError: If item not found
        """
        result = await db.execute(select(DatasetItem).where(DatasetItem.id == item_id))
        item = result.scalar_one_or_none()
        if not item:
            raise NotFoundError("DatasetItem", item_id)

        # Store previous values
        previous_values = {
            "instruction": item.instruction,
            "input_text": item.input_text,
            "ideal_response": item.ideal_response,
            "bad_response": item.bad_response,
            "explanation": item.explanation,
        }

        # Update values
        new_values = {}
        if instruction is not None:
            item.instruction = instruction
            new_values["instruction"] = instruction
        if input_text is not None:
            item.input_text = input_text
            new_values["input_text"] = input_text
        if ideal_response is not None:
            item.ideal_response = ideal_response
            new_values["ideal_response"] = ideal_response
        if bad_response is not None:
            item.bad_response = bad_response
            new_values["bad_response"] = bad_response
        if explanation is not None:
            item.explanation = explanation
            new_values["explanation"] = explanation

        # Create review record
        review = DatasetReview(
            dataset_item_id=item_id,
            action="edit",
            reviewer_id=reviewer_id,
            justification=justification,
            previous_values=previous_values,
            new_values=new_values,
        )

        db.add(review)
        await db.commit()
        await db.refresh(review)

        logger.info("Item edited", item_id=item_id, reviewer_id=reviewer_id)
        return review

