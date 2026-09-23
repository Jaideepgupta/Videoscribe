"""
Transcript Cleaner and Normalization Pipeline.
Converts noisy subtitle fragments and raw caption entries into clean, readable prose
without altering the original spoken wording or technical entities.
"""

import re
from typing import List


class TranscriptCleaner:
    """Rule-based text cleaning and formatting pipeline for captions and transcripts."""

    # Patterns for sound artifacts and caption markers
    ARTIFACT_PATTERNS = [
        re.compile(r"\[(music|applause|laughter|cheering|inaudible|screaming|snickers|sighs|crosstalk|groans|applause/cheering)\]", re.IGNORECASE),
        re.compile(r"\((music|applause|laughter|cheering|inaudible|screaming)\)", re.IGNORECASE),
        re.compile(r"[♪♫🎵🎶]", re.UNICODE),  # Musical notes common in video captions
        re.compile(r"\[\s*\]|\(\s*\)", re.IGNORECASE),  # Empty brackets left after artifact stripping
        re.compile(r">>+", re.IGNORECASE),  # Subtitle speaker change indicators anywhere
        re.compile(r"^\s*-\s*", re.MULTILINE),  # Subtitle dash prefixes
    ]

    # Filler word patterns handling commas and sentence boundaries
    FILLER_PATTERN = re.compile(
        r"(?:^|(?<=\s)|,\s*)\b(um+|uh+|er+|ah+)\b(?:\s*,\s*|\s*[.]\s*|\s*)",
        re.IGNORECASE,
    )

    def remove_artifacts(self, text: str) -> str:
        """Remove bracketed sound markers, caption arrows, and common filler artifacts."""
        cleaned = text
        for pattern in self.ARTIFACT_PATTERNS:
            cleaned = pattern.sub(" ", cleaned)
        return cleaned

    def remove_fillers(self, text: str) -> str:
        """Strip standalone speech fillers like 'um,', 'uh'."""
        cleaned = self.FILLER_PATTERN.sub(" ", text)
        # Clean any remaining double commas or orphaned commas before punctuation
        cleaned = re.sub(r",\s*,", ",", cleaned)
        cleaned = re.sub(r",\s*([.!?])", r"\1", cleaned)
        cleaned = re.sub(r"^\s*,\s*", "", cleaned)
        return cleaned

    def deduplicate_overlap(self, prev_text: str, curr_text: str) -> str:
        """
        Detects and removes overlapping word sequences at boundary of consecutive subtitle chunks.
        Example:
            prev: "today we are going to"
            curr: "going to talk about Snowflake"
            result for curr -> "talk about Snowflake"
        """
        prev_words = prev_text.strip().split()
        curr_words = curr_text.strip().split()

        if not prev_words or not curr_words:
            return curr_text.strip()

        # Check overlaps from longest possible match down to 2 words
        max_overlap = min(len(prev_words), len(curr_words), 8)
        for k in range(max_overlap, 1, -1):
            prev_tail = [w.lower().strip(".,?!") for w in prev_words[-k:]]
            curr_head = [w.lower().strip(".,?!") for w in curr_words[:k]]
            if prev_tail == curr_head:
                return " ".join(curr_words[k:])

        return curr_text.strip()

    def clean_segment_text(self, text: str) -> str:
        """Clean an individual caption segment string."""
        cleaned = self.remove_artifacts(text)
        cleaned = self.remove_fillers(cleaned)
        # Normalize whitespace and newlines
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        return cleaned

    def clean_segments_list(self, raw_segments: List[dict]) -> List[dict]:
        """
        Deduplicates and cleans a list of segment dictionaries:
        [{'start_time': ..., 'end_time': ..., 'text': ...}, ...]
        """
        cleaned_segments = []
        prev_text = ""

        for seg in raw_segments:
            seg_text = seg.get("text", "")
            cleaned_text = self.clean_segment_text(seg_text)

            if not cleaned_text:
                continue

            # Remove boundary overlap with previous segment
            deduped_text = self.deduplicate_overlap(prev_text, cleaned_text)
            if not deduped_text:
                continue

            prev_text = cleaned_text

            cleaned_segments.append({
                "start_time": seg.get("start_time", 0.0),
                "end_time": seg.get("end_time", 0.0),
                "duration": seg.get("duration", 0.0),
                "text": deduped_text,
                "speaker": seg.get("speaker"),
            })

        return cleaned_segments

    def format_prose(self, raw_text: str) -> str:
        """
        Converts raw caption text with arbitrary line breaks into continuous, well-punctuated prose.
        """
        cleaned = self.remove_artifacts(raw_text)
        cleaned = self.remove_fillers(cleaned)

        # Replace multiple spaces / newlines with single space
        prose = re.sub(r"\s+", " ", cleaned).strip()

        # Fix spacing around punctuation marks
        prose = re.sub(r"\s+([.,!?;:])", r"\1", prose)
        prose = re.sub(r"([.,!?;:])(?=[A-Za-z])", r"\1 ", prose)
        prose = re.sub(r",\s*,+", ",", prose)
        prose = re.sub(r"^\s*,\s*", "", prose)

        # Ensure first character is capitalized
        if prose and prose[0].islower():
            prose = prose[0].upper() + prose[1:]

        return prose

    def format_paragraphs(self, full_text: str, target_sentences_per_paragraph: int = 4) -> List[str]:
        """
        Splits continuous clean text into structured readable paragraphs (3-5 sentences each).
        """
        cleaned_prose = self.format_prose(full_text)
        if not cleaned_prose:
            return []

        # Sentence splitter handling abbreviations gracefully
        sentence_endings = re.compile(r'(?<=[.?!])\s+(?=[A-Z0-9"\'])')
        sentences = [s.strip() for s in sentence_endings.split(cleaned_prose) if s.strip()]

        if not sentences:
            return [cleaned_prose]

        paragraphs: List[str] = []
        current_chunk: List[str] = []
        word_count = 0

        for sentence in sentences:
            current_chunk.append(sentence)
            word_count += len(sentence.split())

            # Group into paragraphs when sentence count >= 4 or word count >= 75
            if len(current_chunk) >= target_sentences_per_paragraph or word_count >= 75:
                paragraphs.append(" ".join(current_chunk))
                current_chunk = []
                word_count = 0

        if current_chunk:
            paragraphs.append(" ".join(current_chunk))

        return paragraphs


transcript_cleaner = TranscriptCleaner()
