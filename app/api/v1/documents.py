"""Document endpoints."""

from typing import List

from fastapi import APIRouter, Depends, File, Query, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db_session
from app.schemas.document import DocumentProcess, DocumentResponse, DocumentUpload
from app.services.ingestion_service import IngestionService
from app.services.segmenter_service import SegmenterService

router = APIRouter(prefix="/documents", tags=["documents"])

ingestion_service = IngestionService()


@router.post("/upload", response_model=DocumentResponse, status_code=201)
async def upload_document(
    file: UploadFile = File(...),
    domain_id: str = Query(...),
    use_case: str = Query(None),
    db: AsyncSession = Depends(get_db_session),
):
    """Upload a document."""
    file_content = await file.read()
    document = await ingestion_service.upload_document(
        db=db,
        domain_id=domain_id,
        file_content=file_content,
        filename=file.filename or "unknown",
        content_type=file.content_type or "application/octet-stream",
        use_case=use_case,
    )
    return DocumentResponse.model_validate(document)


@router.get("", response_model=List[DocumentResponse])
async def list_documents(
    domain_id: str = None,
    db: AsyncSession = Depends(get_db_session),
):
    """List documents."""
    from sqlalchemy import select
    from app.models.document import Document

    query = select(Document)
    if domain_id:
        query = query.where(Document.domain_id == domain_id)

    result = await db.execute(query)
    documents = list(result.scalars().all())
    return [DocumentResponse.model_validate(d) for d in documents]


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str,
    db: AsyncSession = Depends(get_db_session),
):
    """Get document by ID."""
    from sqlalchemy import select
    from app.core.exceptions import NotFoundError
    from app.models.document import Document

    result = await db.execute(select(Document).where(Document.id == document_id))
    document = result.scalar_one_or_none()
    if not document:
        raise NotFoundError("Document", document_id)
    return DocumentResponse.model_validate(document)


@router.post("/{document_id}/process", status_code=202)
async def process_document(
    document_id: str,
    process_data: DocumentProcess,
    db: AsyncSession = Depends(get_db_session),
):
    """Process a document: extract text and create segments."""
    # Process document
    version = await ingestion_service.process_document(
        db=db,
        document_id=document_id,
        segment_type=process_data.segment_type,
        segment_config=process_data.segment_config,
    )

    # Get document to access domain_id
    from sqlalchemy import select
    from app.models.document import Document
    doc_result = await db.execute(select(Document).where(Document.id == document_id))
    document = doc_result.scalar_one()

    # Create segments
    await SegmenterService.create_segments_from_text(
        db=db,
        domain_id=document.domain_id,
        document_id=document_id,
        document_version_id=version.id,
        text=version.extracted_text or "",
        segment_type=process_data.segment_type,
        use_case=document.use_case,
        segment_config=process_data.segment_config,
    )

    return {"status": "processing", "version_id": version.id}

