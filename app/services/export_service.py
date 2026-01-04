"""Export service for exporting datasets."""

import io
import json
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.core.logging import get_logger
from app.integrations.s3_client import S3Client
from app.models.dataset import Dataset
from app.models.dataset_export import DatasetExport
from app.models.dataset_item import DatasetItem

logger = get_logger(__name__)


class ExportService:
    """Service for exporting datasets."""

    def __init__(self):
        """Initialize export service."""
        self.s3_client = S3Client()

    async def export_jsonl(
        self,
        db: AsyncSession,
        dataset_id: str,
        approved_only: bool = True,
        filters: Optional[dict] = None,
    ) -> DatasetExport:
        """Export dataset to JSONL format (Together AI).

        Args:
            db: Database session
            dataset_id: Dataset ID
            approved_only: Export only approved items
            filters: Additional filters

        Returns:
            Created export record

        Raises:
            NotFoundError: If dataset not found
        """
        # Get dataset
        result = await db.execute(select(Dataset).where(Dataset.id == dataset_id))
        dataset = result.scalar_one_or_none()
        if not dataset:
            raise NotFoundError("Dataset", dataset_id)

        # Get items
        query = select(DatasetItem).where(DatasetItem.dataset_id == dataset_id)

        if approved_only:
            query = query.where(DatasetItem.status == "approved")

        result = await db.execute(query)
        items = list(result.scalars().all())

        # Generate JSONL content
        jsonl_lines = []
        for item in items:
            # Format as Together AI messages format
            messages = []

            # Add system message if instruction exists
            if item.instruction:
                messages.append({"role": "system", "content": item.instruction})

            # Add user message
            user_content = item.input_text if item.input_text else item.instruction
            messages.append({"role": "user", "content": user_content})

            # Add assistant message
            messages.append({"role": "assistant", "content": item.ideal_response})

            jsonl_lines.append(json.dumps({"messages": messages}))

        jsonl_content = "\n".join(jsonl_lines)

        # Get next export version
        from sqlalchemy import desc
        result = await db.execute(
            select(DatasetExport)
            .where(DatasetExport.dataset_id == dataset_id)
            .order_by(desc(DatasetExport.export_version))
        )
        last_export = result.scalar_one_or_none()
        export_version = (last_export.export_version + 1) if last_export else 1

        # Upload to S3
        s3_key = f"exports/{dataset_id}/v{export_version}.jsonl"
        await self.s3_client.upload_file(
            file_content=jsonl_content.encode("utf-8"),
            s3_key=s3_key,
            content_type="application/jsonl",
        )

        # Create export record
        export = DatasetExport(
            dataset_id=dataset_id,
            export_version=export_version,
            format="jsonl",
            s3_key=s3_key,
            status="completed",
            item_count=len(items),
            filters_applied=filters or {},
        )

        db.add(export)
        await db.commit()
        await db.refresh(export)

        logger.info(
            "Dataset exported",
            dataset_id=dataset_id,
            export_version=export_version,
            item_count=len(items),
        )

        return export

