"""
Video ORM Model.
"""

import enum
import uuid
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import String, Integer, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from backend.app.models.user import User
    from backend.app.models.transcript import Transcript
    from backend.app.models.job import TranscriptionJob


class PlatformType(str, enum.Enum):
    YOUTUBE = "youtube"
    UPLOAD = "upload"
    VIMEO = "vimeo"
    DIRECT = "direct"
    OTHER = "other"


class VideoStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Video(Base, TimestampMixin):
    """Video entity model."""
    __tablename__ = "videos"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    user_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    source_url: Mapped[Optional[str]] = mapped_column(String(2048), nullable=True, index=True)
    platform: Mapped[PlatformType] = mapped_column(
        SQLEnum(PlatformType, name="platform_type", native_enum=False),
        default=PlatformType.YOUTUBE,
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(512), default="Untitled Video", nullable=False)
    duration: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # In seconds
    language: Mapped[str] = mapped_column(String(10), default="en", nullable=False)
    status: Mapped[VideoStatus] = mapped_column(
        SQLEnum(VideoStatus, name="video_status", native_enum=False),
        default=VideoStatus.PENDING,
        nullable=False,
    )

    # Relationships
    user: Mapped[Optional["User"]] = relationship("User", back_populates="videos")
    transcript: Mapped[Optional["Transcript"]] = relationship(
        "Transcript",
        back_populates="video",
        uselist=False,
        cascade="all, delete-orphan",
    )
    jobs: Mapped[List["TranscriptionJob"]] = relationship(
        "TranscriptionJob",
        back_populates="video",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Video id={self.id} title={self.title} platform={self.platform}>"
