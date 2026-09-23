"""
OpenAI Whisper Speech-to-Text Provider.
Transcribes audio files using OpenAI's Whisper model with verbose segment timestamps.
"""

import os
from typing import Optional
import httpx
from backend.app.config import settings
from backend.app.providers.stt.base import BaseSTTProvider
from backend.app.schemas.stt import STTResult, STTSegment


class WhisperSTTProvider(BaseSTTProvider):
    """OpenAI Whisper API implementation."""

    OPENAI_TRANSCRIPTION_URL = "https://api.openai.com/v1/audio/transcriptions"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.OPENAI_API_KEY

    def transcribe(self, audio_file_path: str, language: Optional[str] = None) -> STTResult:
        if not os.path.exists(audio_file_path):
            raise FileNotFoundError(f"Audio file not found: {audio_file_path}")

        if not self.api_key:
            raise ValueError(
                "OpenAI API key is missing. Set OPENAI_API_KEY in environment or switch STT_PROVIDER to 'mock'."
            )

        headers = {
            "Authorization": f"Bearer {self.api_key}",
        }

        data = {
            "model": "whisper-1",
            "response_format": "verbose_json",
        }
        if language:
            data["language"] = language

        with open(audio_file_path, "rb") as audio_file:
            files = {
                "file": (os.path.basename(audio_file_path), audio_file, "audio/mpeg"),
            }

            response = httpx.post(
                self.OPENAI_TRANSCRIPTION_URL,
                headers=headers,
                data=data,
                files=files,
                timeout=600.0,
            )

        if response.status_code != 200:
            raise RuntimeError(
                f"OpenAI Whisper API error ({response.status_code}): {response.text[:300]}"
            )

        payload = response.json()
        raw_segments = payload.get("segments", [])
        full_text = payload.get("text", "").strip()
        detected_language = payload.get("language", language or "en")
        duration = float(payload.get("duration", 0.0))

        segments = []
        for s in raw_segments:
            start = float(s.get("start", 0.0))
            end = float(s.get("end", 0.0))
            text = s.get("text", "").strip()
            if not text:
                continue

            segments.append(
                STTSegment(
                    start_time=round(start, 3),
                    end_time=round(end, 3),
                    duration=round(end - start, 3),
                    text=text,
                    confidence=float(s.get("avg_logprob", 0.0)) if "avg_logprob" in s else None,
                )
            )

        return STTResult(
            full_text=full_text,
            language=detected_language,
            duration=duration,
            segments=segments,
            provider_name="openai_whisper",
        )
