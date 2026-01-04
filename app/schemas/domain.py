"""Domain schemas."""

from typing import Any, Optional

from pydantic import BaseModel, Field

from app.schemas.common import BaseResponse


class DomainCreate(BaseModel):
    """Schema for creating a domain."""

    name: str = Field(..., min_length=1, max_length=100, description="Domain name")
    slug: str = Field(..., min_length=1, max_length=100, description="Domain slug")
    description: Optional[str] = Field(None, description="Domain description")
    config: dict[str, Any] = Field(default_factory=dict, description="Domain configuration")


class DomainUpdate(BaseModel):
    """Schema for updating a domain."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    slug: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    config: Optional[dict[str, Any]] = None
    is_active: Optional[bool] = None


class DomainResponse(BaseResponse):
    """Schema for domain response."""

    name: str
    slug: str
    description: Optional[str]
    config: dict[str, Any]
    is_active: bool

    class Config:
        from_attributes = True

