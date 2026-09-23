"""
Jobs API Router.
Handles status polling and progress monitoring for transcription jobs.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.core.exceptions import JobNotFoundException
from backend.app.db.session import get_db
from backend.app.models.job import TranscriptionJob
from backend.app.models.transcript import Transcript
from backend.app.schemas.api import JobResponse

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.get("/{job_id}", response_model=JobResponse)
def get_job_status(
    job_id: str,
    db: Session = Depends(get_db),
):
    """
    Poll processing status, progress percentage, and error details for a given job.
    When completed, provides the transcript_id for immediate navigation.
    """
    job = db.query(TranscriptionJob).filter(TranscriptionJob.id == job_id).first()
    if not job:
        raise JobNotFoundException(job_id)

    # If completed, locate transcript ID
    transcript_id = None
    transcript = db.query(Transcript).filter(Transcript.video_id == job.video_id).first()
    if transcript:
        transcript_id = transcript.id

    return JobResponse(
        job_id=job.id,
        status=job.status,
        progress=job.progress,
        error_message=job.error_message,
        video_id=job.video_id,
        transcript_id=transcript_id,
        created_at=job.created_at,
        updated_at=job.updated_at,
    )
