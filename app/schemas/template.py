"""Generation template schemas."""

from typing import Any, Optional

from pydantic import BaseModel, Field

from app.schemas.common import BaseResponse


class TemplateCreate(BaseModel):
    """Schema for creating a generation template."""

    domain_id: str = Field(..., description="Domain ID")
    use_case: Optional[str] = Field(None, max_length=100, description="Use case")
    name: str = Field(..., min_length=1, max_length=100, description="Template name")
    system_prompt: str = Field(..., min_length=1, description="System prompt")
    user_prompt_template: str = Field(..., min_length=1, description="User prompt template")
    target_model_family: Optional[str] = Field(None, description="Target model family")
    config: dict[str, Any] = Field(default_factory=dict, description="Template configuration")


class TemplateUpdate(BaseModel):
    """Schema for updating a generation template."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    system_prompt: Optional[str] = None
    user_prompt_template: Optional[str] = None
    target_model_family: Optional[str] = None
    config: Optional[dict[str, Any]] = None
    is_active: Optional[bool] = None


class TemplateResponse(BaseResponse):
    """Schema for template response."""

    domain_id: str
    use_case: Optional[str]
    name: str
    system_prompt: str
    user_prompt_template: str
    target_model_family: Optional[str]
    config: dict[str, Any]
    is_active: bool

    class Config:
        from_attributes = True

