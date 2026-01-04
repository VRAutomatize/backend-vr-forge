"""Export schemas."""

from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class ExportRequest(BaseModel):
    """Schema for export request."""

    format: str = Field("jsonl", description="Export format")
    approved_only: bool = Field(True, description="Export only approved items")
    filters: dict[str, Any] = Field(default_factory=dict, description="Additional filters")


class ExportResponse(BaseModel):
    """Schema for export response."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    dataset_id: str
    export_version: int
    format: str
    s3_key: str
    status: str
    item_count: int
    filters_applied: dict[str, Any]
    download_url: Optional[str] = None
    created_at: str

