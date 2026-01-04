"""Segment schemas."""

from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class SegmentResponse(BaseModel):
    """Schema for segment response."""

    model_config = ConfigDict(protected_namespaces=(), from_attributes=True)

    id: str
    domain_id: str
    document_id: Optional[str]
    document_version_id: Optional[str]
    use_case: Optional[str]
    segment_type: str
    content: str
    position: int
    metadata: dict[str, Any] = Field(alias="meta_data")
    created_at: str


class SegmentFilter(BaseModel):
    """Schema for filtering segments."""

    domain_id: Optional[str] = None
    document_id: Optional[str] = None
    use_case: Optional[str] = None
    segment_type: Optional[str] = None

