"""
Integration tests for FastAPI REST endpoints.
"""

from unittest.mock import patch
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from backend.app.db.base import Base
from backend.app.db.session import get_db
from backend.app.main import app
from backend.app.models import (
    Video,
    PlatformType,
    VideoStatus,
    TranscriptionJob,
    JobStatus,
    Transcript,
    TranscriptSegment,
)


@pytest.fixture
def client_and_session():
    """Create in-memory SQLite database and test client with overridden dependency."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine, expire_on_commit=False)

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    session = TestingSession()
    client = TestClient(app)

    yield client, session

    app.dependency_overrides.clear()
    session.close()
    Base.metadata.drop_all(bind=engine)


def test_root_and_health(client_and_session):
    """Verify root endpoint and health check."""
    client, _ = client_and_session
    res_root = client.get("/")
    assert res_root.status_code == 200
    assert res_root.json()["service"] == "Video2Content"

    res_health = client.get("/api/v1/health")
    assert res_health.status_code == 200
    assert res_health.json()["status"] == "healthy"


def test_submit_video_url_valid(client_and_session):
    """Verify POST /api/v1/videos with valid YouTube URL."""
    client, session = client_and_session

    with patch("backend.app.api.v1.videos.process_video_job.delay") as mock_celery:
        response = client.post(
            "/api/v1/videos",
            json={"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"},
        )
        assert response.status_code == 202
        data = response.json()
        assert data["status"] == "queued"
        assert data["job_id"].startswith("job_")
        assert data["video_id"] is not None
        mock_celery.assert_called_once_with(data["job_id"])


def test_submit_video_url_invalid_and_ssrf(client_and_session):
    """Verify POST /api/v1/videos with SSRF or invalid URL returns 400."""
    client, _ = client_and_session

    # SSRF URL
    res_ssrf = client.post("/api/v1/videos", json={"url": "http://127.0.0.1:8000/media.mp4"})
    assert res_ssrf.status_code == 400
    assert "error" in res_ssrf.json()

    # Invalid URL
    res_invalid = client.post("/api/v1/videos", json={"url": "ftp://example.com/video.mp4"})
    assert res_invalid.status_code == 400
    assert "error" in res_invalid.json()


def test_upload_file_endpoint(client_and_session, tmp_path):
    """Verify POST /api/v1/uploads accepts media file."""
    client, _ = client_and_session

    file_content = b"fake video bytes"
    files = {"file": ("test_lecture.mp4", file_content, "video/mp4")}

    with patch("backend.app.api.v1.uploads.process_video_job.delay") as mock_celery:
        response = client.post("/api/v1/uploads", files=files)
        assert response.status_code == 202
        data = response.json()
        assert data["status"] == "queued"
        assert data["filename"] == "test_lecture.mp4"
        mock_celery.assert_called_once()


def test_upload_file_invalid_extension(client_and_session):
    """Verify POST /api/v1/uploads rejects unsupported extensions."""
    client, _ = client_and_session
    files = {"file": ("malicious.exe", b"binary", "application/octet-stream")}
    response = client.post("/api/v1/uploads", files=files)
    assert response.status_code == 400


def test_get_job_status(client_and_session):
    """Verify GET /api/v1/jobs/{job_id}."""
    client, session = client_and_session

    video = Video(title="Job Test Video", platform=PlatformType.YOUTUBE)
    session.add(video)
    session.commit()

    job = TranscriptionJob(video_id=video.id, status=JobStatus.TRANSCRIBING, progress=60)
    session.add(job)
    session.commit()

    # Existing job
    res = client.get(f"/api/v1/jobs/{job.id}")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "transcribing"
    assert data["progress"] == 60

    # Non-existent job
    res_404 = client.get("/api/v1/jobs/non_existent_job_id")
    assert res_404.status_code == 404


def test_get_transcript(client_and_session):
    """Verify GET /api/v1/transcripts/{id}."""
    client, session = client_and_session

    video = Video(
        title="Postgres Indexing Deep Dive",
        platform=PlatformType.YOUTUBE,
        source_url="https://youtube.com/watch?v=abc",
        duration=185,
        status=VideoStatus.COMPLETED,
    )
    session.add(video)
    session.commit()

    transcript = Transcript(
        video_id=video.id,
        raw_text="Today we talk about B-tree indexes.",
        clean_text="Today we talk about B-tree indexes.\n\nIndexes allow logarithmic lookups.",
        language="en",
    )
    session.add(transcript)
    session.commit()

    seg1 = TranscriptSegment(
        transcript_id=transcript.id,
        start_time=0.0,
        end_time=5.0,
        text="Today we talk about B-tree indexes.",
    )
    session.add(seg1)
    session.commit()

    # Query by transcript ID
    res = client.get(f"/api/v1/transcripts/{transcript.id}")
    assert res.status_code == 200
    data = res.json()
    assert data["title"] == "Postgres Indexing Deep Dive"
    assert data["duration_formatted"] == "03:05"
    assert len(data["paragraphs"]) == 2
    assert len(data["segments"]) == 1
    assert data["segments"][0]["timestamp_label"] == "00:00"

    # Query by video ID (convenience alias)
    res_video_id = client.get(f"/api/v1/transcripts/{video.id}")
    assert res_video_id.status_code == 200

    # Query non-existent
    res_404 = client.get("/api/v1/transcripts/non_existent_transcript_id")
    assert res_404.status_code == 404
