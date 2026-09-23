"""
Videos API Router.
Handles submission of public video URLs for transcription.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.models.video import Video, VideoStatus, PlatformType
from backend.app.models.job import TranscriptionJob, JobStatus
from backend.app.providers.platform_detector import PlatformDetector
from backend.app.schemas.api import VideoSubmitRequest, JobResponse
from backend.app.services.url_validator import validate_url
from backend.app.workers.tasks import process_video_job

router = APIRouter(prefix="/videos", tags=["Videos"])


@router.post("", response_model=JobResponse, status_code=status.HTTP_202_ACCEPTED)
def submit_video_url(
    payload: VideoSubmitRequest,
    db: Session = Depends(get_db),
):
    """
    Submit a public video URL for transcription.
    Validates URL, initializes job tracking, and queues background processing worker.
    """
    clean_url = validate_url(payload.url)
    platform, video_id, canonical_url = PlatformDetector.detect(clean_url)

    # 1. Create Video record
    video = Video(
        source_url=canonical_url,
        platform=platform,
        title=f"{platform.value.capitalize()} Video",
        duration=0,
        language="en",
        status=VideoStatus.PENDING,
    )
    db.add(video)
    db.flush()

    # 2. Create TranscriptionJob record
    job = TranscriptionJob(
        video_id=video.id,
        status=JobStatus.QUEUED,
        progress=0,
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    # 3. Enqueue background processing
    try:
        process_video_job.delay(job.id)
    except Exception:
        # If Celery/Redis broker is offline in local dev, run asynchronously in background thread
        import threading
        from backend.app.workers.tasks import execute_video_pipeline

        thread = threading.Thread(target=execute_video_pipeline, args=(job.id,), daemon=True)
        thread.start()

    return JobResponse(
        job_id=job.id,
        status=job.status,
        progress=job.progress,
        error_message=job.error_message,
        video_id=video.id,
        transcript_id=None,
        created_at=job.created_at,
        updated_at=job.updated_at,
    )
