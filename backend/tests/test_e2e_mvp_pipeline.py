import io
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from backend.app.main import app
from backend.app.db.session import get_db
from backend.app.models.video import PlatformType
from backend.app.services.transcription_router import TranscriptionPayload, StandardSegment
from backend.app.workers.tasks import execute_video_pipeline


@pytest.fixture
def client_and_session(test_db_session: Session, monkeypatch):
    monkeypatch.setattr("backend.app.workers.tasks.SessionLocal", lambda: test_db_session)
    monkeypatch.setattr("backend.app.db.session.SessionLocal", lambda: test_db_session)

    def override_get_db():
        yield test_db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client, test_db_session
    app.dependency_overrides.clear()


def test_e2e_mvp_scenario_a_youtube_captions(client_and_session):
    """
    Scenario A: Public YouTube video with captions -> Fast extraction ($0 cost) -> Clean transcript.
    """
    client, session = client_and_session

    mock_payload = TranscriptionPayload(
        title="VideoScribe Masterclass",
        duration=120,
        language="en",
        platform=PlatformType.YOUTUBE,
        canonical_url="https://www.youtube.com/watch?v=sample123",
        raw_text="Hello and welcome to VideoScribe. Today we are building an end to end pipeline. It extracts spoken content automatically.",
        segments=[
            StandardSegment(start_time=0.0, end_time=2.5, duration=2.5, text="Hello and welcome to VideoScribe."),
            StandardSegment(start_time=2.5, end_time=5.5, duration=3.0, text="Today we are building an end to end pipeline."),
            StandardSegment(start_time=5.5, end_time=9.0, duration=3.5, text="It extracts spoken content automatically."),
        ],
        source_type="captions",
        provider_name="youtube_captions",
    )

    with patch("backend.app.api.v1.videos.process_video_job.delay"), \
         patch("backend.app.workers.tasks.transcription_router.process_url", return_value=mock_payload):

        # 1. User submits URL
        res = client.post("/api/v1/videos", json={"url": "https://www.youtube.com/watch?v=sample123"})
        assert res.status_code == 202
        job_data = res.json()
        job_id = job_data["job_id"]

        # 2. Worker executes pipeline
        success = execute_video_pipeline(job_id)
        assert success is True

        # 3. Client checks job status
        session.expire_all()
        job_res = client.get(f"/api/v1/jobs/{job_id}")
        assert job_res.status_code == 200
        job_info = job_res.json()
        assert job_info["status"] == "completed"
        assert job_info["progress"] == 100
        assert job_info["transcript_id"] is not None

        # 4. Client retrieves clean transcript
        transcript_id = job_info["transcript_id"]
        transcript_res = client.get(f"/api/v1/transcripts/{transcript_id}")
        assert transcript_res.status_code == 200
        data = transcript_res.json()

        assert data["title"] == "VideoScribe Masterclass"
        assert "Hello and welcome to VideoScribe" in data["clean_text"]
        assert len(data["segments"]) >= 1
        assert data["segments"][0]["timestamp_label"] == "00:00"


def test_e2e_mvp_scenario_b_file_upload_stt(client_and_session):
    """
    Scenario B: Uploaded video file -> Audio extraction & STT -> Clean transcript.
    """
    client, session = client_and_session

    mock_payload = TranscriptionPayload(
        title="interview.mp4",
        duration=65,
        language="en",
        platform=PlatformType.UPLOAD,
        raw_text="This is an uploaded video. We are testing Speech to Text transcription.",
        segments=[
            StandardSegment(start_time=0.0, end_time=3.0, duration=3.0, text="This is an uploaded video."),
            StandardSegment(start_time=3.0, end_time=6.5, duration=3.5, text="We are testing Speech to Text transcription."),
        ],
        source_type="audio_stt",
        provider_name="mock",
    )

    with patch("backend.app.api.v1.uploads.process_video_job.delay") as mock_delay, \
         patch("backend.app.workers.tasks.transcription_router.process_uploaded_file", return_value=mock_payload):

        # 1. User uploads file
        file_bytes = b"dummy video bytes"
        upload_res = client.post(
            "/api/v1/uploads",
            files={"file": ("interview.mp4", io.BytesIO(file_bytes), "video/mp4")},
        )
        assert upload_res.status_code == 202
        job_id = upload_res.json()["job_id"]

        # Extract local path passed to Celery
        called_args, called_kwargs = mock_delay.call_args
        local_path = called_kwargs.get("local_upload_path")

        # 2. Worker executes pipeline
        success = execute_video_pipeline(job_id, local_upload_path=local_path)
        assert success is True

        # 3. Client checks job status
        session.expire_all()
        job_res = client.get(f"/api/v1/jobs/{job_id}")
        assert job_res.status_code == 200
        job_info = job_res.json()
        assert job_info["status"] == "completed"

        # 4. Client retrieves transcript
        transcript_id = job_info["transcript_id"]
        t_res = client.get(f"/api/v1/transcripts/{transcript_id}")
        assert t_res.status_code == 200
        t_data = t_res.json()
        assert "This is an uploaded video." in t_data["clean_text"]
        assert len(t_data["segments"]) >= 1


def test_e2e_mvp_scenario_c_security_rejection(client_and_session):
    """
    Scenario C: Invalid / SSRF target URL is rejected immediately with 400.
    """
    client, _ = client_and_session
    res = client.post("/api/v1/videos", json={"url": "http://169.254.169.254/latest/meta-data"})
    assert res.status_code == 400
    assert "error" in res.json()
