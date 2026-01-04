"""Model schemas."""

from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common import BaseResponse


class ModelCreate(BaseModel):
    """Schema for creating a model."""

    domain_id: Optional[str] = Field(None, description="Domain ID")
    name: str = Field(..., min_length=1, max_length=200, description="Model name")
    base_model: str = Field(..., description="Base model identifier")
    provider: str = Field(..., description="Model provider")
    model_family: Optional[str] = Field(None, description="Model family")
    version: Optional[str] = Field(None, description="Model version")
    config: dict[str, Any] = Field(default_factory=dict, description="Model configuration")
    capabilities: dict[str, Any] = Field(default_factory=dict, description="Model capabilities")


class ModelResponse(BaseResponse):
    """Schema for model response."""

    model_config = ConfigDict(from_attributes=True)

    domain_id: Optional[str]
    name: str
    base_model: str
    provider: str
    model_family: Optional[str]
    version: Optional[str]
    status: str
    config: dict[str, Any]
    capabilities: dict[str, Any]

