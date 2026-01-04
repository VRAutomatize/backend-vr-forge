"""Segmenter service for breaking documents into segments."""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.models.segment import Segment

logger = get_logger(__name__)


class SegmenterService:
    """Service for segmenting documents."""

    @staticmethod
    async def create_segments_from_text(
        db: AsyncSession,
        domain_id: str,
        document_id: str,
        document_version_id: str,
        text: str,
        segment_type: str,
        use_case: Optional[str] = None,
        segment_config: Optional[dict] = None,
    ) -> list[Segment]:
        """Create segments from extracted text.

        Args:
            db: Database session
            domain_id: Domain ID
            document_id: Document ID
            document_version_id: Document version ID
            text: Extracted text
            segment_type: Type of segments
            use_case: Use case
            segment_config: Segment configuration

        Returns:
            List of created segments
        """
        # Simple segmentation by paragraphs for now
        # Can be extended with more sophisticated logic
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

        segments = []
        for position, content in enumerate(paragraphs):
            segment = Segment(
                domain_id=domain_id,
                document_id=document_id,
                document_version_id=document_version_id,
                use_case=use_case,
                segment_type=segment_type,
                content=content,
                position=position,
                meta_data=segment_config or {},
            )
            segments.append(segment)
            db.add(segment)

        await db.commit()

        for segment in segments:
            await db.refresh(segment)

        logger.info(
            "Segments created",
            count=len(segments),
            document_id=document_id,
            segment_type=segment_type,
        )

        return segments

    @staticmethod
    async def get_segments(
        db: AsyncSession,
        domain_id: Optional[str] = None,
        document_id: Optional[str] = None,
        use_case: Optional[str] = None,
        segment_type: Optional[str] = None,
    ) -> list[Segment]:
        """Get segments with filters.

        Args:
            db: Database session
            domain_id: Filter by domain
            document_id: Filter by document
            use_case: Filter by use case
            segment_type: Filter by segment type

        Returns:
            List of segments
        """
        query = select(Segment)

        if domain_id:
            query = query.where(Segment.domain_id == domain_id)
        if document_id:
            query = query.where(Segment.document_id == document_id)
        if use_case:
            query = query.where(Segment.use_case == use_case)
        if segment_type:
            query = query.where(Segment.segment_type == segment_type)

        result = await db.execute(query)
        return list(result.scalars().all())

