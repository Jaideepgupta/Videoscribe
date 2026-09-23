"""
YouTube Platform Adapter.
Extracts metadata and captions from YouTube videos using youtube-transcript-api and yt-dlp.
"""

from typing import List, Optional
import yt_dlp
from youtube_transcript_api import (
    YouTubeTranscriptApi,
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable,
)
from backend.app.models.video import PlatformType
from backend.app.providers.base import BasePlatformAdapter
from backend.app.providers.platform_detector import PlatformDetector
from backend.app.schemas.provider import VideoMetadata, CaptionExtractionResult, RawCaptionSegment


class YouTubeAdapter(BasePlatformAdapter):
    """Adapter for extracting YouTube video metadata and captions."""

    DEFAULT_LANGUAGES = ["en", "hi", "en-US", "en-GB", "es", "fr", "de"]

    def __init__(self):
        self.api = YouTubeTranscriptApi()

    def can_handle(self, url: str) -> bool:
        return PlatformDetector.extract_youtube_id(url) is not None

    def get_video_id(self, url: str) -> str:
        video_id = PlatformDetector.extract_youtube_id(url)
        if not video_id:
            raise ValueError(f"Could not extract YouTube video ID from URL: {url}")
        return video_id

    def get_metadata(self, url: str) -> VideoMetadata:
        """Fetch video metadata using yt-dlp without downloading media."""
        video_id = self.get_video_id(url)
        canonical_url = f"https://www.youtube.com/watch?v={video_id}"

        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,
            "extract_flat": False,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(canonical_url, download=False)
                if not info:
                    raise ValueError(f"Unable to fetch info for video: {canonical_url}")

                has_caps = bool(info.get("subtitles") or info.get("automatic_captions"))
                duration = int(info.get("duration") or 0)
                title = info.get("title") or f"YouTube Video ({video_id})"
                author = info.get("uploader") or info.get("channel")
                thumbnail = info.get("thumbnail")
                desc = info.get("description", "")[:500] if info.get("description") else None
                lang = info.get("language") or "en"

                return VideoMetadata(
                    title=title,
                    duration=duration,
                    platform=PlatformType.YOUTUBE,
                    canonical_url=canonical_url,
                    author=author,
                    thumbnail_url=thumbnail,
                    description=desc,
                    language=lang,
                    has_captions=has_caps,
                )
        except Exception as e:
            # Fallback metadata if network / yt-dlp fails
            return VideoMetadata(
                title=f"YouTube Video ({video_id})",
                duration=0,
                platform=PlatformType.YOUTUBE,
                canonical_url=canonical_url,
                has_captions=self.has_captions(url),
            )

    def _get_transcript_list(self, video_id: str):
        """Retrieve TranscriptList using available API method."""
        if hasattr(self.api, "list"):
            return self.api.list(video_id)
        elif hasattr(YouTubeTranscriptApi, "list_transcripts"):
            return YouTubeTranscriptApi.list_transcripts(video_id)
        raise AttributeError("No transcript list method found on YouTubeTranscriptApi")

    def has_captions(self, url: str) -> bool:
        """Check if youtube-transcript-api can list transcripts for video."""
        try:
            video_id = self.get_video_id(url)
            transcript_list = self._get_transcript_list(video_id)
            return bool(list(transcript_list))
        except (TranscriptsDisabled, NoTranscriptFound, VideoUnavailable, Exception):
            return False

    def extract_captions(
        self,
        url: str,
        preferred_languages: Optional[List[str]] = None,
    ) -> Optional[CaptionExtractionResult]:
        """
        Extract subtitles via youtube-transcript-api.
        Tries manually created transcripts first, then falls back to auto-generated transcripts.
        """
        video_id = self.get_video_id(url)
        langs = preferred_languages or self.DEFAULT_LANGUAGES

        try:
            transcript_list = self._get_transcript_list(video_id)
        except (TranscriptsDisabled, NoTranscriptFound, VideoUnavailable, Exception):
            return None

        chosen_transcript = None
        is_generated = False

        # 1. Try to find a manually created transcript in preferred languages
        try:
            chosen_transcript = transcript_list.find_manually_created_transcript(langs)
            is_generated = False
        except Exception:
            pass

        # 2. Try to find generated transcript in preferred languages
        if not chosen_transcript:
            try:
                chosen_transcript = transcript_list.find_generated_transcript(langs)
                is_generated = True
            except Exception:
                pass

        # 3. Fallback to any transcript available
        if not chosen_transcript:
            try:
                for t in transcript_list:
                    chosen_transcript = t
                    is_generated = getattr(t, "is_generated", False)
                    break
            except Exception:
                return None

        if not chosen_transcript:
            return None

        # Fetch actual caption segments
        raw_entries = chosen_transcript.fetch()
        segments: List[RawCaptionSegment] = []
        full_text_pieces: List[str] = []

        for entry in raw_entries:
            if isinstance(entry, dict):
                text = entry.get("text", "").strip()
                start = float(entry.get("start", 0.0))
                dur = float(entry.get("duration", 0.0))
            else:
                text = getattr(entry, "text", "").strip()
                start = float(getattr(entry, "start", 0.0))
                dur = float(getattr(entry, "duration", 0.0))

            if not text:
                continue

            end = round(start + dur, 3)

            segments.append(
                RawCaptionSegment(
                    start_time=round(start, 3),
                    end_time=end,
                    duration=round(dur, 3),
                    text=text,
                )
            )
            full_text_pieces.append(text)

        language_code = getattr(chosen_transcript, "language_code", "en")

        return CaptionExtractionResult(
            language=language_code,
            is_generated=is_generated,
            segments=segments,
            raw_full_text=" ".join(full_text_pieces),
        )


youtube_adapter = YouTubeAdapter()
