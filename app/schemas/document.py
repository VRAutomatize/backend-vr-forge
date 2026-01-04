"""Document schemas."""

from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class DocumentUpload(BaseModel):
    """Schema for document upload request."""

    model_config = ConfigDict(protected_namespaces=())

    domain_id: str = Field(..., description="Domain ID")
    use_case: Optional[str] = Field(None, max_length=100, description="Use case")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class DocumentProcess(BaseModel):
    """Schema for document processing request."""

    segment_type: str = Field(..., description="Type of segments to create")
    segment_config: dict[str, Any] = Field(default_factory=dict, description="Segment configuration")


class DocumentResponse(BaseModel):
    """Schema for document response."""

    model_config = ConfigDict(protected_namespaces=(), from_attributes=True)

    id: str
    domain_id: str
    use_case: Optional[str]
    filename: str
    original_filename: str
    s3_key: str
    content_type: Optional[str]
    file_size: Optional[int]
    status: str
    metadata: dict[str, Any] = Field(alias="meta_data")
    created_at: str
    updated_at: str


class DocumentVersionResponse(BaseModel):
    """Schema for document version response."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    document_id: str
    version_number: int
    s3_key: Optional[str]
    extracted_text: Optional[str]
    processing_metadata: dict[str, Any]
    created_at: str

