"""
Unit tests for SegmentAligner and timestamp alignment operations.
"""

import pytest
from backend.app.services.segment_aligner import (
    SegmentAligner,
    format_seconds_to_timestamp,
)


@pytest.fixture
def aligner():
    return SegmentAligner()


def test_format_seconds_to_timestamp():
    """Verify conversion of float seconds to MM:SS and HH:MM:SS."""
    assert format_seconds_to_timestamp(0) == "00:00"
    assert format_seconds_to_timestamp(45) == "00:45"
    assert format_seconds_to_timestamp(75.8) == "01:15"
    assert format_seconds_to_timestamp(3665) == "01:01:05"


def test_group_micro_segments(aligner):
    """Verify grouping rapid micro-segments into structured timestamp blocks."""
    micro_segments = [
        {"start_time": 0.0, "end_time": 3.0, "text": "Welcome to the lesson."},
        {"start_time": 3.0, "end_time": 6.5, "text": "Today we talk about"},
        {"start_time": 6.5, "end_time": 10.0, "text": "database indexes."},
        {"start_time": 25.0, "end_time": 28.0, "text": "Indexes speed up queries."},  # After a long pause
    ]

    grouped = aligner.group_micro_segments(micro_segments, target_block_seconds=15.0)

    # Should group the first 3 segments into block 1 (0:00 - 0:10), and the 4th into block 2 (0:25 - 0:28)
    assert len(grouped) == 2
    assert grouped[0].formatted_start_time == "00:00"
    assert grouped[0].formatted_end_time == "00:10"
    assert "Welcome to the lesson. Today we talk about database indexes." in grouped[0].text
    assert grouped[1].formatted_start_time == "00:25"
    assert "Indexes speed up queries." in grouped[1].text


def test_build_processed_transcript(aligner):
    """Verify dual representation creation (Reading Mode vs Timestamp Mode)."""
    raw_segments = [
        {"start_time": 0.0, "end_time": 4.0, "text": "First concept is transactional isolation."},
        {"start_time": 4.0, "end_time": 8.0, "text": "It guarantees data integrity."},
    ]
    raw_text = "First concept is transactional isolation. It guarantees data integrity."

    processed = aligner.build_processed_transcript(
        raw_text=raw_text,
        raw_segments=raw_segments,
        language="en",
        duration=8,
    )

    assert processed.language == "en"
    assert processed.duration == 8
    # Reading mode check
    assert "First concept is transactional isolation. It guarantees data integrity." in processed.clean_text
    assert len(processed.paragraphs) >= 1
    # Timestamp mode check
    assert len(processed.segments) == 1
    assert processed.segments[0].formatted_start_time == "00:00"
    assert processed.segments[0].formatted_end_time == "00:08"
