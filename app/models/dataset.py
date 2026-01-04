"""Dataset model."""

from typing import Any, Optional

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin


class Dataset(Base, UUIDMixin, TimestampMixin):
    """Dataset model representing a collection of training data items."""

    __tablename__ = "datasets"

    domain_id: Mapped[str] = mapped_column(
        ForeignKey("domains.id", ondelete="CASCADE"),
        nullable=False,
    )
    template_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("generation_templates.id", ondelete="SET NULL"),
        nullable=True,
    )
    use_case: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    target_model_family: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="draft", nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    generation_config: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
    segment_filter: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
    total_items: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    approved_items: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    rejected_items: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    pending_items: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Relationships
    domain: Mapped["Domain"] = relationship("Domain", back_populates="datasets")
    template: Mapped[Optional["GenerationTemplate"]] = relationship(
        "GenerationTemplate", back_populates="datasets"
    )
    items: Mapped[list["DatasetItem"]] = relationship(
        "DatasetItem",
        back_populates="dataset",
        cascade="all, delete-orphan",
    )
    exports: Mapped[list["DatasetExport"]] = relationship(
        "DatasetExport",
        back_populates="dataset",
        cascade="all, delete-orphan",
    )
    training_jobs: Mapped[list["TrainingJob"]] = relationship(
        "TrainingJob",
        back_populates="dataset",
    )

