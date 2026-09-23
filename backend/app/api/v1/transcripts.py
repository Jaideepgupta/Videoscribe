"""
Transcripts API Router.
Retrieves complete transcript content, metadata, and timestamp segments.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.core.exceptions import TranscriptNotFoundException
from backend.app.db.session import get_db
from backend.app.models.transcript import Transcript, TranscriptSegment
from backend.app.models.video import Video
from backend.app.schemas.api import TranscriptResponse, TranscriptSegmentResponse
from backend.app.services.segment_aligner import format_seconds_to_timestamp

router = APIRouter(prefix="/transcripts", tags=["Transcripts"])


@router.get("/{id}", response_model=TranscriptResponse)
def get_transcript(
    id: str,
    db: Session = Depends(get_db),
):
    """
    Retrieve processed transcript by Transcript ID or Video ID.
    Returns metadata, readable prose paragraphs for Reading Mode, and timestamp segments for Timestamp Mode.
    """
    # Try finding by transcript.id or video_id
    transcript = db.query(Transcript).filter(
        (Transcript.id == id) | (Transcript.video_id == id)
    ).first()

    if not transcript:
        raise TranscriptNotFoundException(id)

    video = db.query(Video).filter(Video.id == transcript.video_id).first()

    # Load and format segments
    segments = db.query(TranscriptSegment).filter(
        TranscriptSegment.transcript_id == transcript.id
    ).order_by(TranscriptSegment.start_time).all()

    formatted_segments = [
        TranscriptSegmentResponse(
            id=seg.id,
            start_time=seg.start_time,
            end_time=seg.end_time,
            duration=round(seg.end_time - seg.start_time, 2),
            timestamp_label=seg.formatted_start_time,
            text=seg.text,
            speaker=seg.speaker,
        )
        for seg in segments
    ]

    # Paragraphs for Reading Mode
    paragraphs = [p.strip() for p in transcript.clean_text.split("\n\n") if p.strip()]
    if not paragraphs:
        paragraphs = [transcript.clean_text]

    video_duration = video.duration if video else 0

    return TranscriptResponse(
        id=transcript.id,
        video_id=transcript.video_id,
        title=video.title if video else "Untitled Video",
        source_url=video.source_url if video else None,
        platform=video.platform if video else None,
        duration=video_duration,
        duration_formatted=format_seconds_to_timestamp(video_duration),
        language=transcript.language,
        raw_text=transcript.raw_text,
        clean_text=transcript.clean_text,
        paragraphs=paragraphs,
        segments=formatted_segments,
        created_at=transcript.created_at,
    )
