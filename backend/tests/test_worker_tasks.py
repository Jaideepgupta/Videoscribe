"""
Unit and integration tests for Celery background tasks and transcription pipeline execution.
"""

from unittest.mock import MagicMock, patch
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from backend.app.models import (
    Base,
    Video,
    PlatformType,
    VideoStatus,
    TranscriptionJob,
    JobStatus,
    Transcript,
    TranscriptSegment,
    ProcessingError,
)
from backend.app.services.transcription_router import TranscriptionPayload, StandardSegment
from backend.app.workers.tasks import execute_video_pipeline


@pytest.fixture
def test_db_session(monkeypatch):
    """Create test SQLite database with StaticPool so all sessions share the in-memory database."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine, expire_on_commit=False)

    # Monkeypatch SessionLocal in tasks and db.session modules
    monkeypatch.setattr("backend.app.workers.tasks.SessionLocal", TestingSession)
    monkeypatch.setattr("backend.app.db.session.SessionLocal", TestingSession)

    session = TestingSession()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


def test_execute_video_pipeline_url_success(test_db_session):
    """Verify complete pipeline execution for URL video with captions."""
    # Seed Video and Job
    video = Video(
        source_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        platform=PlatformType.YOUTUBE,
        title="Rick Astley - Never Gonna Give You Up",
        duration=212,
        language="en",
        status=VideoStatus.PENDING,
    )
    test_db_session.add(video)
    test_db_session.commit()

    job = TranscriptionJob(
        video_id=video.id,
        status=JobStatus.QUEUED,
        progress=0,
    )
    test_db_session.add(job)
    test_db_session.commit()

    # Mock TranscriptionRouter output
    mock_payload = TranscriptionPayload(
        title="Rick Astley - Never Gonna Give You Up",
        duration=212,
        language="en",
        platform=PlatformType.YOUTUBE,
        canonical_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        raw_text="We're no strangers to love. You know the rules and so do I.",
        segments=[
            StandardSegment(start_time=0.0, end_time=3.5, duration=3.5, text="We're no strangers to love."),
            StandardSegment(start_time=3.5, end_time=7.0, duration=3.5, text="You know the rules and so do I."),
        ],
        source_type="captions",
        provider_name="youtube_captions",
    )

    with patch("backend.app.workers.tasks.transcription_router.process_url", return_value=mock_payload):
        success = execute_video_pipeline(job.id)
        assert success is True

    # Refresh records from database
    test_db_session.expire_all()
    refreshed_job = test_db_session.query(TranscriptionJob).filter(TranscriptionJob.id == job.id).first()
    refreshed_video = test_db_session.query(Video).filter(Video.id == video.id).first()
    transcript = test_db_session.query(Transcript).filter(Transcript.video_id == video.id).first()
    segments = test_db_session.query(TranscriptSegment).filter(TranscriptSegment.transcript_id == transcript.id).all()

    assert refreshed_job.status == JobStatus.COMPLETED
    assert refreshed_job.progress == 100
    assert refreshed_video.status == VideoStatus.COMPLETED
    assert transcript is not None
    assert "We're no strangers to love." in transcript.clean_text
    assert len(segments) >= 1


def test_execute_video_pipeline_upload_success(test_db_session, tmp_path):
    """Verify pipeline execution for uploaded video file."""
    dummy_video = tmp_path / "upload_test.mp4"
    dummy_video.write_bytes(b"dummy video stream")

    video = Video(
        platform=PlatformType.UPLOAD,
        title="Lecture Recording",
        duration=60,
        status=VideoStatus.PENDING,
    )
    test_db_session.add(video)
    test_db_session.commit()

    job = TranscriptionJob(
        video_id=video.id,
        status=JobStatus.QUEUED,
        progress=0,
    )
    test_db_session.add(job)
    test_db_session.commit()

    mock_payload = TranscriptionPayload(
        title="Lecture Recording",
        duration=60,
        language="en",
        platform=PlatformType.UPLOAD,
        raw_text="Welcome to the database architecture seminar.",
        segments=[
            StandardSegment(start_time=0.0, end_time=5.0, duration=5.0, text="Welcome to the database architecture seminar."),
        ],
        source_type="stt_transcription",
        provider_name="mock_stt",
    )

    with patch("backend.app.workers.tasks.transcription_router.process_uploaded_file", return_value=mock_payload):
        success = execute_video_pipeline(job.id, local_upload_path=str(dummy_video))
        assert success is True

    test_db_session.expire_all()
    refreshed_job = test_db_session.query(TranscriptionJob).filter(TranscriptionJob.id == job.id).first()
    assert refreshed_job.status == JobStatus.COMPLETED


def test_execute_video_pipeline_failure_handling(test_db_session):
    """Verify graceful failure handling and error logging in ProcessingError table."""
    video = Video(
        source_url="https://youtube.com/watch?v=broken123",
        platform=PlatformType.YOUTUBE,
        title="Broken Video",
    )
    test_db_session.add(video)
    test_db_session.commit()

    job = TranscriptionJob(
        video_id=video.id,
        status=JobStatus.QUEUED,
    )
    test_db_session.add(job)
    test_db_session.commit()

    with patch("backend.app.workers.tasks.transcription_router.process_url", side_effect=RuntimeError("Extraction failed")):
        success = execute_video_pipeline(job.id)
        assert success is False

    test_db_session.expire_all()
    refreshed_job = test_db_session.query(TranscriptionJob).filter(TranscriptionJob.id == job.id).first()
    refreshed_video = test_db_session.query(Video).filter(Video.id == video.id).first()
    errors = test_db_session.query(ProcessingError).filter(ProcessingError.job_id == job.id).all()

    assert refreshed_job.status == JobStatus.FAILED
    assert refreshed_video.status == VideoStatus.FAILED
    assert len(errors) == 1
    assert errors[0].error_code == "PIPELINE_ERROR"
