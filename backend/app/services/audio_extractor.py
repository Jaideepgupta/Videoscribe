"""
Audio Extraction Service.
Extracts audio from video URLs (yt-dlp) and uploaded media files (ffmpeg)
formatted as 16kHz mono audio optimized for Speech-to-Text engines.
"""

import os
import shutil
import subprocess
import uuid
from typing import Optional
import yt_dlp
from backend.app.config import settings


class AudioExtractionError(Exception):
    """Raised when audio extraction fails."""
    pass


class AudioExtractor:
    """Handles audio stream extraction from URLs and uploaded media files."""

    def __init__(self, temp_dir: Optional[str] = None):
        self.temp_dir = temp_dir or settings.TEMP_MEDIA_DIR
        os.makedirs(self.temp_dir, exist_ok=True)

    def extract_audio_from_file(self, input_file_path: str, output_filename: Optional[str] = None) -> str:
        """
        Extracts 16kHz mono MP3 from an uploaded video/audio file using ffmpeg.
        Returns the path to the extracted audio file.
        """
        if not os.path.exists(input_file_path):
            raise AudioExtractionError(f"Input media file not found: {input_file_path}")

        file_id = output_filename or f"audio_{uuid.uuid4().hex[:12]}.mp3"
        output_path = os.path.join(self.temp_dir, file_id)

        # ffmpeg command: -vn (no video), -ac 1 (mono), -ar 16000 (16kHz), -b:a 64k (64kbps)
        cmd = [
            "ffmpeg",
            "-y",  # Overwrite output file
            "-i", input_file_path,
            "-vn",
            "-acodec", "libmp3lame",
            "-ar", "16000",
            "-ac", "1",
            "-b:a", "64k",
            output_path,
        ]

        try:
            process = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=300,  # 5 min timeout
                check=False,
            )
            if process.returncode != 0:
                err_msg = process.stderr.decode("utf-8", errors="ignore")
                raise AudioExtractionError(f"FFmpeg audio extraction failed: {err_msg[:300]}")

            if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
                raise AudioExtractionError("FFmpeg produced an empty or missing audio file.")

            return output_path
        except subprocess.TimeoutExpired:
            raise AudioExtractionError("FFmpeg audio extraction timed out after 300 seconds.")
        except FileNotFoundError:
            raise AudioExtractionError("FFmpeg executable not found on system PATH.")

    def extract_audio_from_url(self, url: str, output_filename: Optional[str] = None) -> str:
        """
        Downloads and extracts audio stream from remote URL using yt-dlp.
        Returns the path to the 16kHz mono MP3.
        """
        file_id = output_filename or f"audio_{uuid.uuid4().hex[:12]}"
        output_template = os.path.join(self.temp_dir, f"{file_id}.%(ext)s")
        final_mp3_path = os.path.join(self.temp_dir, f"{file_id}.mp3")

        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": output_template,
            "quiet": True,
            "no_warnings": True,
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "64",
                }
            ],
            "postprocessor_args": [
                "-ar", "16000",
                "-ac", "1",
            ],
            "max_filesize": settings.max_upload_size_bytes,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            if os.path.exists(final_mp3_path) and os.path.getsize(final_mp3_path) > 0:
                return final_mp3_path

            # If extension was preserved differently
            for ext in (".mp3", ".wav", ".m4a", ".webm"):
                candidate = os.path.join(self.temp_dir, f"{file_id}{ext}")
                if os.path.exists(candidate) and os.path.getsize(candidate) > 0:
                    return candidate

            raise AudioExtractionError(f"Extracted audio file not found for URL: {url}")
        except Exception as e:
            raise AudioExtractionError(f"yt-dlp audio download failed: {str(e)}")

    def cleanup_file(self, file_path: Optional[str]) -> None:
        """Safely remove a temporary media file from disk."""
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except OSError:
                pass


audio_extractor = AudioExtractor()
