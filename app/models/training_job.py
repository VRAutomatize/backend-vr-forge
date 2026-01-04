"""Training job model."""

from typing import Any, Optional

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin


class TrainingJob(Base, UUIDMixin, TimestampMixin):
    """Training job model for tracking fine-tuning jobs."""

    __tablename__ = "training_jobs"

    model_id: Mapped[str] = mapped_column(
        ForeignKey("models.id", ondelete="CASCADE"),
        nullable=False,
    )
    dataset_id: Mapped[str] = mapped_column(
        ForeignKey("datasets.id", ondelete="CASCADE"),
        nullable=False,
    )
    dataset_export_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("dataset_exports.id", ondelete="SET NULL"),
        nullable=True,
    )
    status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False)
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    external_job_id: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    hyperparameters: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
    metrics: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    model: Mapped["Model"] = relationship("Model", back_populates="training_jobs")
    dataset: Mapped["Dataset"] = relationship("Dataset", back_populates="training_jobs")
    dataset_export: Mapped[Optional["DatasetExport"]] = relationship(
        "DatasetExport", back_populates="training_jobs"
    )

