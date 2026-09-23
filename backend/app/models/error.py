"""
ProcessingError ORM Model.
"""

import uuid
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from backend.app.models.job import TranscriptionJob


class ProcessingError(Base, TimestampMixin):
    """Detailed error log entity for failed video processing pipelines."""
    __tablename__ = "processing_errors"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    job_id: Mapped[Optional[str]] = mapped_column(
        String(64),
        ForeignKey("transcription_jobs.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    error_code: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    stack_trace: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    job: Mapped[Optional["TranscriptionJob"]] = relationship("TranscriptionJob", back_populates="errors")

    def __repr__(self) -> str:
        return f"<ProcessingError id={self.id} code={self.error_code}>"
