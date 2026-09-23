"""
Unit tests for TranscriptCleaner text normalization operations.
"""

import pytest
from backend.app.services.transcript_cleaner import TranscriptCleaner


@pytest.fixture
def cleaner():
    return TranscriptCleaner()


def test_remove_sound_artifacts(cleaner):
    """Verify removal of bracketed noise markers and subtitle prefix arrows."""
    raw = "[Music] >> Today we will discuss [Applause] PostgreSQL architecture. (cheering)"
    cleaned = cleaner.format_prose(raw)
    assert "[Music]" not in cleaned
    assert "[Applause]" not in cleaned
    assert "(cheering)" not in cleaned
    assert ">>" not in cleaned
    assert "Today we will discuss PostgreSQL architecture." == cleaned


def test_remove_fillers(cleaner):
    """Verify removal of speech fillers while keeping real words."""
    raw = "Um, today we are going to, uh, configure Redis cluster."
    cleaned = cleaner.format_prose(raw)
    assert "Um" not in cleaned
    assert "uh" not in cleaned
    assert "Today we are going to configure Redis cluster." in cleaned


def test_deduplicate_overlap(cleaner):
    """Verify boundary word overlap removal common in auto-captions."""
    prev = "So today we're going to"
    curr = "going to talk about data engineering"
    deduped = cleaner.deduplicate_overlap(prev, curr)
    assert deduped == "talk about data engineering"


def test_clean_segments_list(cleaner):
    """Verify segment list cleaning and deduplication."""
    raw_segments = [
        {"start_time": 0.0, "end_time": 2.5, "text": "[Music] Welcome to the course"},
        {"start_time": 2.5, "end_time": 5.0, "text": "the course on data modeling"},
        {"start_time": 5.0, "end_time": 8.0, "text": "um with SQL and Python"},
    ]

    cleaned = cleaner.clean_segments_list(raw_segments)
    assert len(cleaned) == 3
    assert cleaned[0]["text"] == "Welcome to the course"
    assert cleaned[1]["text"] == "on data modeling"
    assert "with SQL and Python" in cleaned[2]["text"]


def test_format_paragraphs(cleaner):
    """Verify continuous prose is grouped into multiple structured paragraphs."""
    prose = (
        "Data engineering is a vital part of modern technology. "
        "It handles collecting and processing vast amounts of information. "
        "Engineers build robust pipelines to transport data safely. "
        "These pipelines feed analytics and machine learning models. "
        "In this lecture, we will cover Snowflake and Apache Spark. "
        "Snowflake allows scalable cloud warehousing with ease. "
        "Spark enables distributed batch computation across large clusters. "
        "Together, they form a powerful foundation for data teams."
    )

    paragraphs = cleaner.format_paragraphs(prose, target_sentences_per_paragraph=4)
    assert len(paragraphs) == 2
    assert "Data engineering is a vital part" in paragraphs[0]
    assert "In this lecture, we will cover" in paragraphs[1]
