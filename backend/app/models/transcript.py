"""
Transcript and TranscriptSegment ORM Models.
"""

import uuid
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import String, Text, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from backend.app.models.video import Video


class Transcript(Base, TimestampMixin):
    """Full transcript record for a processed video."""
    __tablename__ = "transcripts"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    video_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("videos.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    clean_text: Mapped[str] = mapped_column(Text, nullable=False)
    language: Mapped[str] = mapped_column(String(10), default="en", nullable=False)

    # Relationships
    video: Mapped["Video"] = relationship("Video", back_populates="transcript")
    segments: Mapped[List["TranscriptSegment"]] = relationship(
        "TranscriptSegment",
        back_populates="transcript",
        order_by="TranscriptSegment.start_time",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Transcript id={self.id} video_id={self.video_id}>"


class TranscriptSegment(Base):
    """Individual timestamped segment within a transcript."""
    __tablename__ = "transcript_segments"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    transcript_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("transcripts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    start_time: Mapped[float] = mapped_column(Float, nullable=False, index=True)  # Seconds
    end_time: Mapped[float] = mapped_column(Float, nullable=False)  # Seconds
    text: Mapped[str] = mapped_column(Text, nullable=False)
    speaker: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Relationships
    transcript: Mapped["Transcript"] = relationship("Transcript", back_populates="segments")

    @property
    def formatted_start_time(self) -> str:
        """Convert float seconds to HH:MM:SS or MM:SS."""
        total_seconds = int(self.start_time)
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        return f"{minutes:02d}:{seconds:02d}"

    def __repr__(self) -> str:
        return f"<TranscriptSegment id={self.id} start={self.start_time} end={self.end_time}>"
