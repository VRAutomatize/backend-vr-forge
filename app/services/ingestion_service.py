"""Document ingestion service."""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, ProcessingError
from app.core.logging import get_logger
from app.integrations.s3_client import S3Client
from app.integrations.text_extractors.factory import get_extractor
from app.models.document import Document, DocumentVersion
from app.services.domain_service import DomainService

logger = get_logger(__name__)


class IngestionService:
    """Service for document ingestion."""

    def __init__(self):
        """Initialize ingestion service."""
        self.s3_client = S3Client()

    async def upload_document(
        self,
        db: AsyncSession,
        domain_id: str,
        file_content: bytes,
        filename: str,
        content_type: str,
        use_case: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> Document:
        """Upload document to S3 and create database record.

        Args:
            db: Database session
            domain_id: Domain ID
            file_content: File content as bytes
            filename: Original filename
            content_type: File content type
            use_case: Use case
            metadata: Additional metadata

        Returns:
            Created document

        Raises:
            NotFoundError: If domain not found
        """
        # Verify domain exists
        await DomainService.get_by_id(db, domain_id)

        # Generate S3 key
        s3_key = f"documents/{domain_id}/{uuid.uuid4()}/{filename}"

        # Upload to S3
        await self.s3_client.upload_file(
            file_content=file_content,
            s3_key=s3_key,
            content_type=content_type,
        )

        # Create document record
        document = Document(
            domain_id=domain_id,
            use_case=use_case,
            filename=filename,
            original_filename=filename,
            s3_key=s3_key,
            content_type=content_type,
            file_size=len(file_content),
            status="uploaded",
            meta_data=metadata or {},
        )

        db.add(document)
        await db.commit()
        await db.refresh(document)

        logger.info("Document uploaded", document_id=document.id, filename=filename)
        return document

    async def process_document(
        self,
        db: AsyncSession,
        document_id: str,
        segment_type: str,
        segment_config: Optional[dict] = None,
    ) -> DocumentVersion:
        """Process document: extract text and create version.

        Args:
            db: Database session
            document_id: Document ID
            segment_type: Type of segments to create
            segment_config: Segment configuration

        Returns:
            Created document version

        Raises:
            NotFoundError: If document not found
            ProcessingError: If processing fails
        """
        # Get document
        from sqlalchemy import select
        result = await db.execute(select(Document).where(Document.id == document_id))
        document = result.scalar_one_or_none()
        if not document:
            raise NotFoundError("Document", document_id)

        # Update status
        document.status = "processing"
        await db.commit()

        try:
            # Download file from S3
            file_content = await self.s3_client.download_file(document.s3_key)

            # Extract text
            extractor = get_extractor(document.content_type or "")
            extracted_text = await extractor.extract(file_content)

            # Get next version number
            from sqlalchemy import select, desc
            result = await db.execute(
                select(DocumentVersion)
                .where(DocumentVersion.document_id == document_id)
                .order_by(desc(DocumentVersion.version_number))
            )
            last_version = result.scalar_one_or_none()
            version_number = (last_version.version_number + 1) if last_version else 1

            # Create document version
            document_version = DocumentVersion(
                document_id=document_id,
                version_number=version_number,
                extracted_text=extracted_text,
                processing_metadata={
                    "segment_type": segment_type,
                    "segment_config": segment_config or {},
                    "extracted_at": datetime.utcnow().isoformat(),
                },
            )

            db.add(document_version)
            document.status = "processed"
            await db.commit()
            await db.refresh(document_version)

            logger.info(
                "Document processed",
                document_id=document_id,
                version_number=version_number,
            )

            return document_version

        except Exception as e:
            document.status = "failed"
            await db.commit()
            logger.error("Document processing failed", document_id=document_id, error=str(e))
            raise ProcessingError(f"Failed to process document: {str(e)}") from e

