"""Generation template model."""

from typing import Any, Optional

from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin


class GenerationTemplate(Base, UUIDMixin, TimestampMixin):
    """Generation template model for dataset generation prompts."""

    __tablename__ = "generation_templates"

    domain_id: Mapped[str] = mapped_column(
        ForeignKey("domains.id", ondelete="CASCADE"),
        nullable=False,
    )
    use_case: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    system_prompt: Mapped[str] = mapped_column(Text, nullable=False)
    user_prompt_template: Mapped[str] = mapped_column(Text, nullable=False)
    target_model_family: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    config: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    domain: Mapped["Domain"] = relationship("Domain", back_populates="generation_templates")
    datasets: Mapped[list["Dataset"]] = relationship(
        "Dataset",
        back_populates="template",
    )

