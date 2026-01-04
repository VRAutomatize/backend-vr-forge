"""Dataset review model."""

from typing import Any, Optional

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, UUIDMixin


class DatasetReview(Base, UUIDMixin):
    """Dataset review model for tracking human reviews."""

    __tablename__ = "dataset_reviews"

    dataset_item_id: Mapped[str] = mapped_column(
        ForeignKey("dataset_items.id", ondelete="CASCADE"),
        nullable=False,
    )
    action: Mapped[str] = mapped_column(String(20), nullable=False)  # approve, reject, edit
    reviewer_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    justification: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    previous_values: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    new_values: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONB, nullable=True)

    # Relationships
    dataset_item: Mapped["DatasetItem"] = relationship("DatasetItem", back_populates="reviews")

