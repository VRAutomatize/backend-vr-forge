"""Dataset item model."""

from typing import Any, Optional

from sqlalchemy import Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin


class DatasetItem(Base, UUIDMixin, TimestampMixin):
    """Dataset item model representing a single training example."""

    __tablename__ = "dataset_items"

    dataset_id: Mapped[str] = mapped_column(
        ForeignKey("datasets.id", ondelete="CASCADE"),
        nullable=False,
    )
    segment_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("segments.id", ondelete="SET NULL"),
        nullable=True,
    )
    source_provider: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    instruction: Mapped[str] = mapped_column(Text, nullable=False)
    input_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ideal_response: Mapped[str] = mapped_column(Text, nullable=False)
    bad_response: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    explanation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        String(50), default="pending_review", nullable=False
    )
    quality_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    quality_flags: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
    metadata: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)

    # Relationships
    dataset: Mapped["Dataset"] = relationship("Dataset", back_populates="items")
    segment: Mapped[Optional["Segment"]] = relationship("Segment", back_populates="dataset_items")
    reviews: Mapped[list["DatasetReview"]] = relationship(
        "DatasetReview",
        back_populates="dataset_item",
        cascade="all, delete-orphan",
    )

