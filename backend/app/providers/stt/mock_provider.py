"""
Mock Speech-to-Text Provider.
Used for deterministic testing and local development without incurring API costs.
"""

import os
from typing import Optional
from backend.app.providers.stt.base import BaseSTTProvider
from backend.app.schemas.stt import STTResult, STTSegment


class MockSTTProvider(BaseSTTProvider):
    """Mock STT Provider generating synthetic transcription output."""

    DEFAULT_SEGMENTS = [
        ("Today we are going to talk about building scalable data pipelines.", 0.0, 4.5),
        ("First, let's understand how streaming architecture works with event brokers.", 4.5, 9.8),
        ("Next, we will look into transformation layers using modern compute engines.", 9.8, 15.2),
        ("Finally, we store the structured clean records for downstream analytical queries.", 15.2, 21.0),
    ]

    def transcribe(self, audio_file_path: str, language: Optional[str] = None) -> STTResult:
        if not os.path.exists(audio_file_path):
            raise FileNotFoundError(f"Audio file not found: {audio_file_path}")

        segments = [
            STTSegment(
                start_time=start,
                end_time=end,
                duration=round(end - start, 2),
                text=text,
                confidence=0.98,
                speaker="Speaker 1",
            )
            for text, start, end in self.DEFAULT_SEGMENTS
        ]

        full_text = " ".join([s.text for s in segments])

        return STTResult(
            full_text=full_text,
            language=language or "en",
            duration=21.0,
            segments=segments,
            provider_name="mock_stt",
        )
