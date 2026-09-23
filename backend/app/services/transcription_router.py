"""
Transcription Decision Router & Cost Optimization Pipeline.
Prioritizes native platform captions ($0 cost, instant) before falling back to Audio Extraction + Speech-to-Text.
"""

from typing import List, Optional, Union
from pydantic import BaseModel, Field
from backend.app.models.video import PlatformType
from backend.app.providers.platform_detector import PlatformDetector
from backend.app.providers.youtube import youtube_adapter
from backend.app.providers.stt import get_stt_provider, BaseSTTProvider
from backend.app.schemas.provider import RawCaptionSegment, VideoMetadata
from backend.app.services.audio_extractor import audio_extractor, AudioExtractor


class StandardSegment(BaseModel):
    """Unified timestamp segment across captions and STT providers."""
    start_time: float
    end_time: float
    duration: float
    text: str
    speaker: Optional[str] = None


class TranscriptionPayload(BaseModel):
    """Standardized output payload from transcription routing pipeline."""
    title: str
    duration: int
    language: str
    platform: PlatformType
    canonical_url: Optional[str] = None
    raw_text: str
    segments: List[StandardSegment]
    source_type: str = Field(..., description="'captions' (free) or 'stt_transcription'")
    provider_name: str


class TranscriptionRouter:
    """Orchestrates source detection, caption extraction, and STT fallback."""

    def __init__(
        self,
        stt_provider: Optional[BaseSTTProvider] = None,
        extractor: Optional[AudioExtractor] = None,
    ):
        self.stt_provider = stt_provider or get_stt_provider()
        self.extractor = extractor or audio_extractor

    def process_url(
        self,
        url: str,
        preferred_languages: Optional[List[str]] = None,
        stt_language: Optional[str] = None,
    ) -> TranscriptionPayload:
        """
        Process a video URL:
        1. Check if platform adapter has accessible native captions.
        2. If captions exist, extract captions ($0 STT cost).
        3. Otherwise, extract audio and transcribe with Speech-to-Text.
        """
        platform, video_id, canonical_url = PlatformDetector.detect(url)

        # 1. Attempt Native Caption Extraction for YouTube
        if platform == PlatformType.YOUTUBE and youtube_adapter.can_handle(url):
            metadata = youtube_adapter.get_metadata(url)
            caption_result = youtube_adapter.extract_captions(url, preferred_languages)

            if caption_result and caption_result.segments:
                segments = [
                    StandardSegment(
                        start_time=s.start_time,
                        end_time=s.end_time,
                        duration=s.duration,
                        text=s.text,
                    )
                    for s in caption_result.segments
                ]
                return TranscriptionPayload(
                    title=metadata.title,
                    duration=metadata.duration,
                    language=caption_result.language,
                    platform=PlatformType.YOUTUBE,
                    canonical_url=canonical_url,
                    raw_text=caption_result.raw_full_text,
                    segments=segments,
                    source_type="captions",
                    provider_name="youtube_captions",
                )

        # 2. Fallback: Extract Audio Stream + Transcribe with STT
        extracted_audio_path = None
        try:
            extracted_audio_path = self.extractor.extract_audio_from_url(canonical_url)
            stt_result = self.stt_provider.transcribe(extracted_audio_path, language=stt_language)

            segments = [
                StandardSegment(
                    start_time=s.start_time,
                    end_time=s.end_time,
                    duration=s.duration,
                    text=s.text,
                    speaker=s.speaker,
                )
                for s in stt_result.segments
            ]

            return TranscriptionPayload(
                title=f"Video from {platform.value.capitalize()}",
                duration=int(stt_result.duration),
                language=stt_result.language,
                platform=platform,
                canonical_url=canonical_url,
                raw_text=stt_result.full_text,
                segments=segments,
                source_type="stt_transcription",
                provider_name=stt_result.provider_name,
            )
        finally:
            if extracted_audio_path:
                self.extractor.cleanup_file(extracted_audio_path)

    def process_uploaded_file(
        self,
        file_path: str,
        filename: str,
        stt_language: Optional[str] = None,
    ) -> TranscriptionPayload:
        """
        Process an uploaded video/audio file:
        Extracts 16kHz mono audio via FFmpeg and routes to Speech-to-Text provider.
        """
        extracted_audio_path = None
        try:
            extracted_audio_path = self.extractor.extract_audio_from_file(file_path)
            stt_result = self.stt_provider.transcribe(extracted_audio_path, language=stt_language)

            segments = [
                StandardSegment(
                    start_time=s.start_time,
                    end_time=s.end_time,
                    duration=s.duration,
                    text=s.text,
                    speaker=s.speaker,
                )
                for s in stt_result.segments
            ]

            return TranscriptionPayload(
                title=filename,
                duration=int(stt_result.duration),
                language=stt_result.language,
                platform=PlatformType.UPLOAD,
                canonical_url=None,
                raw_text=stt_result.full_text,
                segments=segments,
                source_type="stt_transcription",
                provider_name=stt_result.provider_name,
            )
        finally:
            if extracted_audio_path:
                self.extractor.cleanup_file(extracted_audio_path)


transcription_router = TranscriptionRouter()
