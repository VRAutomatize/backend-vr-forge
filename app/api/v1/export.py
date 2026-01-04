"""Export endpoints."""

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db_session
from app.schemas.export import ExportRequest, ExportResponse
from app.services.export_service import ExportService

router = APIRouter(prefix="/datasets", tags=["export"])

export_service = ExportService()


@router.post("/{dataset_id}/export", response_model=ExportResponse)
async def export_dataset(
    dataset_id: str,
    export_data: ExportRequest,
    db: AsyncSession = Depends(get_db_session),
):
    """Export dataset to JSONL."""
    export = await export_service.export_jsonl(
        db=db,
        dataset_id=dataset_id,
        approved_only=export_data.approved_only,
        filters=export_data.filters,
    )

    # Generate download URL
    download_url = export_service.s3_client.generate_presigned_url(export.s3_key)

    response = ExportResponse.model_validate(export)
    response.download_url = download_url
    return response


@router.get("/{dataset_id}/exports", response_model=List[ExportResponse])
async def list_exports(
    dataset_id: str,
    db: AsyncSession = Depends(get_db_session),
):
    """List exports for a dataset."""
    from sqlalchemy import select
    from app.models.dataset_export import DatasetExport

    result = await db.execute(
        select(DatasetExport).where(DatasetExport.dataset_id == dataset_id)
    )
    exports = list(result.scalars().all())
    return [ExportResponse.model_validate(e) for e in exports]


@router.get("/exports/{export_id}/download")
async def get_download_url(
    export_id: str,
    db: AsyncSession = Depends(get_db_session),
):
    """Get download URL for an export."""
    from sqlalchemy import select
    from app.core.exceptions import NotFoundError
    from app.models.dataset_export import DatasetExport

    result = await db.execute(select(DatasetExport).where(DatasetExport.id == export_id))
    export = result.scalar_one_or_none()
    if not export:
        raise NotFoundError("DatasetExport", export_id)

    download_url = export_service.s3_client.generate_presigned_url(export.s3_key)
    return {"download_url": download_url}

