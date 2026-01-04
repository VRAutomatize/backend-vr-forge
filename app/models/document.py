"""Document models."""

from typing import Any, Optional

from sqlalchemy import BigInteger, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin


class Document(Base, UUIDMixin, TimestampMixin):
    """Document model representing uploaded files."""

    __tablename__ = "documents"

    domain_id: Mapped[str] = mapped_column(
        ForeignKey("domains.id", ondelete="CASCADE"),
        nullable=False,
    )
    use_case: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    s3_key: Mapped[str] = mapped_column(String(500), nullable=False)
    content_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    file_size: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="uploaded", nullable=False)
    meta_data: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False, name="metadata")

    # Relationships
    domain: Mapped["Domain"] = relationship("Domain", back_populates="documents")
    versions: Mapped[list["DocumentVersion"]] = relationship(
        "DocumentVersion",
        back_populates="document",
        cascade="all, delete-orphan",
    )
    segments: Mapped[list["Segment"]] = relationship(
        "Segment",
        back_populates="document",
    )


class DocumentVersion(Base, UUIDMixin):
    """Document version model for tracking processed versions."""

    __tablename__ = "document_versions"

    document_id: Mapped[str] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
    )
    version_number: Mapped[int] = mapped_column(nullable=False)
    s3_key: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    extracted_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    processing_metadata: Mapped[dict[str, Any]] = mapped_column(
        JSONB, default=dict, nullable=False
    )

    # Relationships
    document: Mapped["Document"] = relationship("Document", back_populates="versions")
    segments: Mapped[list["Segment"]] = relationship(
        "Segment",
        back_populates="document_version",
    )

