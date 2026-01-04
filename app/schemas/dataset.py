"""Dataset schemas."""

from typing import Any, Optional

from pydantic import BaseModel, Field

from app.schemas.common import BaseResponse


class DatasetCreate(BaseModel):
    """Schema for creating a dataset."""

    domain_id: str = Field(..., description="Domain ID")
    template_id: Optional[str] = Field(None, description="Generation template ID")
    use_case: Optional[str] = Field(None, max_length=100, description="Use case")
    name: str = Field(..., min_length=1, max_length=200, description="Dataset name")
    description: Optional[str] = Field(None, description="Dataset description")
    provider: str = Field(..., description="LLM provider")
    target_model_family: Optional[str] = Field(None, description="Target model family")
    generation_config: dict[str, Any] = Field(default_factory=dict, description="Generation configuration")
    segment_filter: dict[str, Any] = Field(default_factory=dict, description="Segment filter criteria")


class DatasetGenerate(BaseModel):
    """Schema for generating dataset items."""

    dataset_id: str = Field(..., description="Dataset ID")
    segment_ids: Optional[list[str]] = Field(None, description="Specific segment IDs to use")
    max_items: Optional[int] = Field(None, ge=1, le=10000, description="Maximum items to generate")
    batch_size: int = Field(10, ge=1, le=100, description="Batch size for generation")


class DatasetResponse(BaseResponse):
    """Schema for dataset response."""

    domain_id: str
    template_id: Optional[str]
    use_case: Optional[str]
    name: str
    description: Optional[str]
    provider: str
    target_model_family: Optional[str]
    status: str
    version: int
    generation_config: dict[str, Any]
    segment_filter: dict[str, Any]
    total_items: int
    approved_items: int
    rejected_items: int
    pending_items: int

    class Config:
        from_attributes = True


class DatasetItemResponse(BaseModel):
    """Schema for dataset item response."""

    id: str
    dataset_id: str
    segment_id: Optional[str]
    source_provider: Optional[str]
    instruction: str
    input_text: Optional[str]
    ideal_response: str
    bad_response: Optional[str]
    explanation: Optional[str]
    status: str
    quality_score: Optional[float]
    quality_flags: dict[str, Any]
    metadata: dict[str, Any]
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True

