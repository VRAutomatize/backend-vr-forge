"""Dataset export model."""

from typing import Any

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, UUIDMixin


class DatasetExport(Base, UUIDMixin):
    """Dataset export model for tracking exported files."""

    __tablename__ = "dataset_exports"

    dataset_id: Mapped[str] = mapped_column(
        ForeignKey("datasets.id", ondelete="CASCADE"),
        nullable=False,
    )
    export_version: Mapped[int] = mapped_column(nullable=False)
    format: Mapped[str] = mapped_column(String(20), default="jsonl", nullable=False)
    s3_key: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="completed", nullable=False)
    item_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    filters_applied: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)

    # Relationships
    dataset: Mapped["Dataset"] = relationship("Dataset", back_populates="exports")
    training_jobs: Mapped[list["TrainingJob"]] = relationship(
        "TrainingJob",
        back_populates="dataset_export",
    )

