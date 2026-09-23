"""
Uploads API Router.
Handles direct media file uploads for transcription.
"""

import os
import shutil
import uuid
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.config import settings
from backend.app.db.session import get_db
from backend.app.models.video import Video, VideoStatus, PlatformType
from backend.app.models.job import TranscriptionJob, JobStatus
from backend.app.schemas.api import UploadResponse
from backend.app.workers.tasks import process_video_job

router = APIRouter(prefix="/uploads", tags=["Uploads"])

ALLOWED_EXTENSIONS = {".mp4", ".mov", ".webm", ".mkv", ".mp3", ".wav", ".m4a"}


@router.post("", response_model=UploadResponse, status_code=status.HTTP_202_ACCEPTED)
async def upload_video_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Upload a video or audio file for speech-to-text processing.
    Validates file extension, stores temporary file, and enqueues worker task.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="Uploaded file must have a valid filename.")

    _, ext = os.path.splitext(file.filename)
    if ext.lower() not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format '{ext}'. Allowed formats: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
        )

    # Save to temp media scratch folder
    os.makedirs(settings.TEMP_MEDIA_DIR, exist_ok=True)
    temp_filename = f"upload_{uuid.uuid4().hex[:12]}{ext.lower()}"
    temp_file_path = os.path.join(settings.TEMP_MEDIA_DIR, temp_filename)

    with open(temp_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Create Video record
    video = Video(
        platform=PlatformType.UPLOAD,
        title=file.filename,
        duration=0,
        language="en",
        status=VideoStatus.PENDING,
    )
    db.add(video)
    db.flush()

    # Create TranscriptionJob record
    job = TranscriptionJob(
        video_id=video.id,
        status=JobStatus.QUEUED,
        progress=0,
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    # Enqueue worker task
    try:
        process_video_job.delay(job.id, local_upload_path=temp_file_path)
    except Exception:
        # If Celery/Redis broker is offline in local dev, run asynchronously in background thread
        import threading
        from backend.app.workers.tasks import execute_video_pipeline

        thread = threading.Thread(
            target=execute_video_pipeline,
            args=(job.id,),
            kwargs={"local_upload_path": temp_file_path},
            daemon=True,
        )
        thread.start()

    return UploadResponse(
        job_id=job.id,
        status=job.status,
        filename=file.filename,
    )
