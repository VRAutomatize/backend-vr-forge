"""Review schemas."""

from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class ReviewApprove(BaseModel):
    """Schema for approving a dataset item."""

    reviewer_id: Optional[str] = Field(None, max_length=100, description="Reviewer identifier")
    justification: Optional[str] = Field(None, description="Approval justification")


class ReviewReject(BaseModel):
    """Schema for rejecting a dataset item."""

    reviewer_id: Optional[str] = Field(None, max_length=100, description="Reviewer identifier")
    justification: str = Field(..., min_length=1, description="Rejection reason")


class ReviewEdit(BaseModel):
    """Schema for editing a dataset item."""

    reviewer_id: Optional[str] = Field(None, max_length=100, description="Reviewer identifier")
    instruction: Optional[str] = None
    input_text: Optional[str] = None
    ideal_response: Optional[str] = None
    bad_response: Optional[str] = None
    explanation: Optional[str] = None
    justification: Optional[str] = Field(None, description="Edit justification")


class ReviewResponse(BaseModel):
    """Schema for review response."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    dataset_item_id: str
    action: str
    reviewer_id: Optional[str]
    justification: Optional[str]
    previous_values: Optional[dict[str, Any]]
    new_values: Optional[dict[str, Any]]
    created_at: str


class PendingReviewItem(BaseModel):
    """Schema for pending review item."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    dataset_id: str
    dataset_name: str
    instruction: str
    input_text: Optional[str]
    ideal_response: str
    bad_response: Optional[str]
    explanation: Optional[str]
    quality_score: Optional[float]
    quality_flags: dict[str, Any]
    created_at: str  # Keep as string since it's not from a model directly

