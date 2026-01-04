"""Training job schemas."""

from typing import Any, Optional

from pydantic import BaseModel, Field

from app.schemas.common import BaseResponse


class TrainingJobCreate(BaseModel):
    """Schema for creating a training job."""

    model_id: str = Field(..., description="Model ID")
    dataset_id: str = Field(..., description="Dataset ID")
    dataset_export_id: Optional[str] = Field(None, description="Dataset export ID")
    provider: str = Field(..., description="Training provider")
    hyperparameters: dict[str, Any] = Field(default_factory=dict, description="Hyperparameters")


class TrainingJobResponse(BaseResponse):
    """Schema for training job response."""

    model_id: str
    dataset_id: str
    dataset_export_id: Optional[str]
    status: str
    provider: str
    external_job_id: Optional[str]
    hyperparameters: dict[str, Any]
    metrics: dict[str, Any]
    error_message: Optional[str]
    started_at: Optional[str]
    completed_at: Optional[str]

    class Config:
        from_attributes = True

