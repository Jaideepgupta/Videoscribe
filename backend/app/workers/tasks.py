"""
Celery Worker Tasks for Asynchronous Video Transcription Pipeline.
"""

import logging
import traceback
from typing import Optional
from backend.app.db.session import SessionLocal
from backend.app.models.video import Video, VideoStatus, PlatformType
from backend.app.models.transcript import Transcript, TranscriptSegment
from backend.app.models.job import TranscriptionJob, JobStatus
from backend.app.services.transcription_router import transcription_router, TranscriptionPayload
from backend.app.services.segment_aligner import segment_aligner
from backend.app.workers.celery_app import celery_app
from backend.app.workers.job_tracker import job_tracker

logger = logging.getLogger(__name__)


def execute_video_pipeline(job_id: str, local_upload_path: Optional[str] = None) -> bool:
    """
    Core business logic for processing a video transcription job.
    Called by the Celery task or directly in synchronous/test execution.
    """
    db = SessionLocal()
    try:
        job = db.query(TranscriptionJob).filter(TranscriptionJob.id == job_id).first()
        if not job:
            logger.error(f"Job not found for ID: {job_id}")
            return False

        video = db.query(Video).filter(Video.id == job.video_id).first()
        if not video:
            job_tracker.log_error(db, job_id, "VIDEO_NOT_FOUND", f"Associated video {job.video_id} not found.")
            return False

        # -------------------------------------------------------------
        # Step 1: Detecting (10%)
        # -------------------------------------------------------------
        job_tracker.update_progress(db, job_id, JobStatus.DETECTING, 10)
        video.status = VideoStatus.PROCESSING
        db.commit()

        # -------------------------------------------------------------
        # Step 2: Extracting & Transcribing (30% -> 60%)
        # -------------------------------------------------------------
        job_tracker.update_progress(db, job_id, JobStatus.EXTRACTING, 30)

        payload: TranscriptionPayload
        if video.source_url:
            payload = transcription_router.process_url(
                url=video.source_url,
                preferred_languages=[video.language, "en", "hi"],
            )
        elif local_upload_path:
            job_tracker.update_progress(db, job_id, JobStatus.TRANSCRIBING, 60)
            payload = transcription_router.process_uploaded_file(
                file_path=local_upload_path,
                filename=video.title or "Uploaded Video",
            )
        else:
            raise ValueError("Job has neither a valid source_url nor an uploaded media file path.")

        # Update video metadata if retrieved from source
        if payload.title:
            video.title = payload.title
        if payload.duration:
            video.duration = payload.duration
        if payload.language:
            video.language = payload.language
        if payload.platform:
            video.platform = payload.platform

        # -------------------------------------------------------------
        # Step 3: Cleaning & Paragraph Formatting (85%)
        # -------------------------------------------------------------
        job_tracker.update_progress(db, job_id, JobStatus.CLEANING, 85)

        raw_segments_dict = [
            {
                "start_time": s.start_time,
                "end_time": s.end_time,
                "duration": s.duration,
                "text": s.text,
                "speaker": s.speaker,
            }
            for s in payload.segments
        ]

        processed_transcript = segment_aligner.build_processed_transcript(
            raw_text=payload.raw_text,
            raw_segments=raw_segments_dict,
            language=payload.language,
            duration=payload.duration,
        )

        # -------------------------------------------------------------
        # Step 4: Persisting Transcript & Segments (100%)
        # -------------------------------------------------------------
        # Check if transcript already exists (for retries)
        transcript = db.query(Transcript).filter(Transcript.video_id == video.id).first()
        if not transcript:
            transcript = Transcript(
                video_id=video.id,
                raw_text=processed_transcript.raw_text,
                clean_text=processed_transcript.clean_text,
                language=processed_transcript.language,
            )
            db.add(transcript)
            db.flush()
        else:
            transcript.raw_text = processed_transcript.raw_text
            transcript.clean_text = processed_transcript.clean_text
            transcript.language = processed_transcript.language
            # Remove old segments on retry
            db.query(TranscriptSegment).filter(TranscriptSegment.transcript_id == transcript.id).delete()
            db.flush()

        # Insert new aligned segments
        segment_entities = [
            TranscriptSegment(
                transcript_id=transcript.id,
                start_time=seg.start_time,
                end_time=seg.end_time,
                text=seg.text,
                speaker=seg.speaker,
            )
            for seg in processed_transcript.segments
        ]
        db.add_all(segment_entities)

        # Finalize Video and Job state
        video.status = VideoStatus.COMPLETED
        job_tracker.update_progress(db, job_id, JobStatus.COMPLETED, 100)
        db.commit()

        logger.info(f"Successfully completed transcription pipeline for job {job_id} (video {video.id})")
        return True

    except Exception as exc:
        db.rollback()
        stack = traceback.format_exc()
        logger.error(f"Error processing video job {job_id}: {exc}\n{stack}")

        try:
            video_rec = db.query(Video).join(TranscriptionJob).filter(TranscriptionJob.id == job_id).first()
            if video_rec:
                video_rec.status = VideoStatus.FAILED
                db.commit()
        except Exception:
            pass

        user_friendly_message = str(exc)
        if "No transcript found" in user_friendly_message or "TranscriptsDisabled" in user_friendly_message:
            user_friendly_message = "Captions aren't available for this video. Please upload the video directly."

        job_tracker.log_error(
            db=db,
            job_id=job_id,
            error_code="PIPELINE_ERROR",
            message=user_friendly_message,
            stack_trace=stack,
        )
        return False
    finally:
        db.close()


@celery_app.task(name="backend.app.workers.tasks.process_video_job", bind=True, max_retries=2)
def process_video_job(self, job_id: str, local_upload_path: Optional[str] = None) -> bool:
    """
    Celery task entrypoint for processing video transcription jobs.
    """
    return execute_video_pipeline(job_id=job_id, local_upload_path=local_upload_path)
