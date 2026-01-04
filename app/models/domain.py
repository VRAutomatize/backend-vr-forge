"""Domain model."""

from typing import Any, Optional

from sqlalchemy import Boolean, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin


class Domain(Base, UUIDMixin, TimestampMixin):
    """Domain model representing a business domain (VR Chat, VR Code, etc.)."""

    __tablename__ = "domains"

    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    config: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    documents: Mapped[list["Document"]] = relationship(
        "Document",
        back_populates="domain",
        cascade="all, delete-orphan",
    )
    segments: Mapped[list["Segment"]] = relationship(
        "Segment",
        back_populates="domain",
        cascade="all, delete-orphan",
    )
    datasets: Mapped[list["Dataset"]] = relationship(
        "Dataset",
        back_populates="domain",
        cascade="all, delete-orphan",
    )
    models: Mapped[list["Model"]] = relationship(
        "Model",
        back_populates="domain",
        cascade="all, delete-orphan",
    )
    generation_templates: Mapped[list["GenerationTemplate"]] = relationship(
        "GenerationTemplate",
        back_populates="domain",
        cascade="all, delete-orphan",
    )

