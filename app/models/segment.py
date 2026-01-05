"""Segment model."""

from datetime import datetime
from typing import Any, Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, UUIDMixin


class Segment(Base, UUIDMixin):
    """Segment model representing text units extracted from documents."""

    __tablename__ = "segments"

    domain_id: Mapped[str] = mapped_column(
        ForeignKey("domains.id", ondelete="CASCADE"),
        nullable=False,
    )
    document_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("documents.id", ondelete="SET NULL"),
        nullable=True,
    )
    document_version_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("document_versions.id", ondelete="SET NULL"),
        nullable=True,
    )
    use_case: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    segment_type: Mapped[str] = mapped_column(String(50), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    position: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    meta_data: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False, name="metadata")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    domain: Mapped["Domain"] = relationship("Domain", back_populates="segments")
    document: Mapped[Optional["Document"]] = relationship("Document", back_populates="segments")
    document_version: Mapped[Optional["DocumentVersion"]] = relationship(
        "DocumentVersion", back_populates="segments"
    )
    dataset_items: Mapped[list["DatasetItem"]] = relationship(
        "DatasetItem",
        back_populates="segment",
    )

