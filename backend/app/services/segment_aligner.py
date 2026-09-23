"""
Timestamp & Segment Alignment Engine.
Aligns cleaned text fragments with timestamps, formats timestamp labels,
and groups micro-segments into readable timestamp blocks for Timestamp Mode.
"""

from typing import List, Optional
from backend.app.schemas.transcript import ProcessedSegment, ProcessedTranscript
from backend.app.services.transcript_cleaner import transcript_cleaner, TranscriptCleaner


def format_seconds_to_timestamp(seconds: float) -> str:
    """Converts float seconds into formatted HH:MM:SS or MM:SS."""
    total_sec = max(0, int(seconds))
    hours = total_sec // 3600
    minutes = (total_sec % 3600) // 60
    secs = total_sec % 60

    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


class SegmentAligner:
    """Aligns, cleans, and groups caption/STT segments into dual-mode representations."""

    def __init__(self, cleaner: Optional[TranscriptCleaner] = None):
        self.cleaner = cleaner or transcript_cleaner

    def group_micro_segments(
        self,
        raw_segments: List[dict],
        target_block_seconds: float = 20.0,
        max_words_per_block: int = 40,
    ) -> List[ProcessedSegment]:
        """
        Groups rapid, fragmented 1-2 second subtitle lines into coherent 15-30s timestamp blocks.
        """
        if not raw_segments:
            return []

        # Step 1: Clean and deduplicate segment list
        cleaned_raw = self.cleaner.clean_segments_list(raw_segments)
        if not cleaned_raw:
            return []

        grouped: List[ProcessedSegment] = []
        current_texts: List[str] = []
        block_start = cleaned_raw[0]["start_time"]
        block_end = cleaned_raw[0]["end_time"]
        current_speaker = cleaned_raw[0].get("speaker")

        for seg in cleaned_raw:
            seg_text = seg["text"]
            seg_start = seg["start_time"]
            seg_end = seg["end_time"]
            seg_speaker = seg.get("speaker")

            # Check if we should flush current block:
            # 1. Speaker changed
            # 2. Block duration exceeds target_block_seconds
            # 3. Word count exceeds max_words_per_block
            # 4. Long pause (> 4 seconds) between segments
            speaker_changed = seg_speaker is not None and seg_speaker != current_speaker
            time_exceeded = (seg_end - block_start) >= target_block_seconds
            word_count = sum(len(t.split()) for t in current_texts)
            words_exceeded = word_count >= max_words_per_block
            long_pause = (seg_start - block_end) > 4.0

            if current_texts and (speaker_changed or time_exceeded or words_exceeded or long_pause):
                combined_text = self.cleaner.format_prose(" ".join(current_texts))
                if combined_text:
                    grouped.append(
                        ProcessedSegment(
                            start_time=round(block_start, 2),
                            end_time=round(block_end, 2),
                            duration=round(block_end - block_start, 2),
                            text=combined_text,
                            formatted_start_time=format_seconds_to_timestamp(block_start),
                            formatted_end_time=format_seconds_to_timestamp(block_end),
                            speaker=current_speaker,
                        )
                    )
                current_texts = [seg_text]
                block_start = seg_start
                block_end = seg_end
                current_speaker = seg_speaker
            else:
                current_texts.append(seg_text)
                block_end = max(block_end, seg_end)

        # Flush final remaining block
        if current_texts:
            combined_text = self.cleaner.format_prose(" ".join(current_texts))
            if combined_text:
                grouped.append(
                    ProcessedSegment(
                        start_time=round(block_start, 2),
                        end_time=round(block_end, 2),
                        duration=round(block_end - block_start, 2),
                        text=combined_text,
                        formatted_start_time=format_seconds_to_timestamp(block_start),
                        formatted_end_time=format_seconds_to_timestamp(block_end),
                        speaker=current_speaker,
                    )
                )

        return grouped

    def build_processed_transcript(
        self,
        raw_text: str,
        raw_segments: List[dict],
        language: str = "en",
        duration: int = 0,
    ) -> ProcessedTranscript:
        """
        Produces the full dual-mode transcript payload:
        - clean_text & paragraphs for Reading Mode
        - grouped segments for Timestamp Mode
        """
        # 1. Build grouped timestamp segments
        aligned_segments = self.group_micro_segments(raw_segments)

        # 2. Extract full text from aligned segments or raw_text
        if aligned_segments:
            combined_raw = " ".join([s.text for s in aligned_segments])
        else:
            combined_raw = raw_text

        # 3. Format into structured paragraphs for Reading Mode
        paragraphs = self.cleaner.format_paragraphs(combined_raw)
        clean_reading_text = "\n\n".join(paragraphs)

        calculated_duration = duration
        if not calculated_duration and aligned_segments:
            calculated_duration = int(aligned_segments[-1].end_time)

        return ProcessedTranscript(
            raw_text=raw_text,
            clean_text=clean_reading_text,
            paragraphs=paragraphs,
            segments=aligned_segments,
            language=language,
            duration=calculated_duration,
        )


segment_aligner = SegmentAligner()
