"""
Unit tests for SQLAlchemy models, relationships, and constraints.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.models import (
    Base,
    User,
    Video,
    PlatformType,
    VideoStatus,
    Transcript,
    TranscriptSegment,
    TranscriptionJob,
    JobStatus,
    ProcessingError,
)


@pytest.fixture
def db_session():
    """Create an in-memory SQLite database session for unit testing."""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


def test_create_user_and_video(db_session):
    """Test user and video creation with relationship linking."""
    user = User(email="test@example.com", name="Test User")
    db_session.add(user)
    db_session.commit()

    video = Video(
        user_id=user.id,
        source_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        platform=PlatformType.YOUTUBE,
        title="Rick Astley - Never Gonna Give You Up",
        duration=212,
        language="en",
        status=VideoStatus.COMPLETED,
    )
    db_session.add(video)
    db_session.commit()

    assert video.id is not None
    assert video.user.email == "test@example.com"
    assert len(user.videos) == 1
    assert user.videos[0].title == "Rick Astley - Never Gonna Give You Up"


def test_transcript_and_segments_relationship(db_session):
    """Test transcript and segment creation with cascades."""
    video = Video(
        source_url="https://youtube.com/watch?v=123",
        platform=PlatformType.YOUTUBE,
        title="Sample Lecture",
        duration=120,
    )
    db_session.add(video)
    db_session.commit()

    transcript = Transcript(
        video_id=video.id,
        raw_text="00:01 Hello world. 00:05 Welcome to data engineering.",
        clean_text="Hello world. Welcome to data engineering.",
        language="en",
    )
    db_session.add(transcript)
    db_session.commit()

    seg1 = TranscriptSegment(
        transcript_id=transcript.id,
        start_time=1.0,
        end_time=4.5,
        text="Hello world.",
    )
    seg2 = TranscriptSegment(
        transcript_id=transcript.id,
        start_time=5.0,
        end_time=9.2,
        text="Welcome to data engineering.",
        speaker="Speaker 1",
    )
    db_session.add_all([seg1, seg2])
    db_session.commit()

    # Verify relationships and formatted timestamp
    assert video.transcript.id == transcript.id
    assert len(transcript.segments) == 2
    assert transcript.segments[0].formatted_start_time == "00:01"
    assert transcript.segments[1].formatted_start_time == "00:05"


def test_transcription_job_and_error(db_session):
    """Test job status transitions and error logging."""
    video = Video(title="Job Test", duration=60)
    db_session.add(video)
    db_session.commit()

    job = TranscriptionJob(
        video_id=video.id,
        status=JobStatus.QUEUED,
        progress=0,
    )
    db_session.add(job)
    db_session.commit()

    # Progress to transcribing
    job.status = JobStatus.TRANSCRIBING
    job.progress = 60
    db_session.commit()

    # Progress to failed with error
    job.status = JobStatus.FAILED
    job.error_message = "Audio stream extraction timed out."
    error = ProcessingError(
        job_id=job.id,
        error_code="EXTRACTION_TIMEOUT",
        message="Failed after 300s",
        stack_trace="Traceback (most recent call last)...",
    )
    db_session.add(error)
    db_session.commit()

    assert job.status == JobStatus.FAILED
    assert len(job.errors) == 1
    assert job.errors[0].error_code == "EXTRACTION_TIMEOUT"
