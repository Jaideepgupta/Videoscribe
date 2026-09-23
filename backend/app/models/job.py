"""
TranscriptionJob ORM Model.
"""

from datetime import datetime, timezone
import enum
import uuid
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import String, Integer, Text, ForeignKey, DateTime, Enum as SQLEnum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.db.base import Base, TimestampMixin, get_utc_now

if TYPE_CHECKING:
    from backend.app.models.video import Video
    from backend.app.models.error import ProcessingError


class JobStatus(str, enum.Enum):
    QUEUED = "queued"
    DETECTING = "detecting"
    EXTRACTING = "extracting"
    TRANSCRIBING = "transcribing"
    CLEANING = "cleaning"
    COMPLETED = "completed"
    FAILED = "failed"


class TranscriptionJob(Base, TimestampMixin):
    """Asynchronous background processing job tracking entity."""
    __tablename__ = "transcription_jobs"

    id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
        default=lambda: f"job_{uuid.uuid4().hex[:16]}",
    )
    video_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("videos.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status: Mapped[JobStatus] = mapped_column(
        SQLEnum(JobStatus, name="job_status", native_enum=False),
        default=JobStatus.QUEUED,
        nullable=False,
        index=True,
    )
    progress: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # 0 to 100
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=get_utc_now,
        onupdate=get_utc_now,
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    video: Mapped["Video"] = relationship("Video", back_populates="jobs")
    errors: Mapped[List["ProcessingError"]] = relationship(
        "ProcessingError",
        back_populates="job",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<TranscriptionJob id={self.id} status={self.status} progress={self.progress}%>"
