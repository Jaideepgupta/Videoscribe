"""
Job Progress Tracking and Error Logging Helper for Celery Tasks.
"""

from typing import Optional
from sqlalchemy.orm import Session
from backend.app.models.job import TranscriptionJob, JobStatus
from backend.app.models.error import ProcessingError


class JobTracker:
    """Helper for atomic state updates on TranscriptionJob and ProcessingError models."""

    @staticmethod
    def update_progress(
        db: Session,
        job_id: str,
        status: JobStatus,
        progress: int,
        error_message: Optional[str] = None,
    ) -> Optional[TranscriptionJob]:
        """Update job status and numeric progress percentage."""
        job = db.query(TranscriptionJob).filter(TranscriptionJob.id == job_id).first()
        if not job:
            return None

        job.status = status
        job.progress = max(0, min(100, progress))
        if error_message:
            job.error_message = error_message

        db.commit()
        db.refresh(job)
        return job

    @staticmethod
    def log_error(
        db: Session,
        job_id: str,
        error_code: str,
        message: str,
        stack_trace: Optional[str] = None,
    ) -> ProcessingError:
        """Create a ProcessingError record and mark job as FAILED."""
        # Update job status
        JobTracker.update_progress(
            db=db,
            job_id=job_id,
            status=JobStatus.FAILED,
            progress=0,
            error_message=message,
        )

        error_entry = ProcessingError(
            job_id=job_id,
            error_code=error_code,
            message=message,
            stack_trace=stack_trace,
        )
        db.add(error_entry)
        db.commit()
        db.refresh(error_entry)
        return error_entry


job_tracker = JobTracker()
