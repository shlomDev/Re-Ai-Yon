"""End-of-turn question segmentation for Whisper fragments."""
from dataclasses import dataclass
import re
import time

@dataclass
class Segment:
    text: str
    emitted_at: float

class QuestionSegmenter:
    def __init__(self, min_chars=12, silence_seconds=1.0, duplicate_seconds=8.0):
        self.min_chars = min_chars
        self.silence_seconds = silence_seconds
        self.duplicate_seconds = duplicate_seconds
        self.parts = []
        self.last_seen = 0.0
        self.last_emitted = ""
        self.last_emitted_at = 0.0

    def add(self, text, now=None):
        text = " ".join((text or "").split()).strip()
        if not text:
            return None
        now = time.monotonic() if now is None else now
        self.parts.append(text)
        self.last_seen = now
        candidate = " ".join(self.parts)
        if len(candidate) < self.min_chars:
            return None
        # Whisper often repeats expanding fragments; wait for a real boundary.
        if not candidate.endswith(("?", ".")):
            return None
        normalized = candidate.lower()
        if normalized == self.last_emitted.lower() and now - self.last_emitted_at < self.duplicate_seconds:
            self.parts.clear()
            return None
        self.last_emitted, self.last_emitted_at = candidate, now
        self.parts.clear()
        return Segment(candidate, now)

    def flush_if_silent(self, now=None):
        now = time.monotonic() if now is None else now
        if not self.parts or now - self.last_seen < self.silence_seconds:
            return None
        candidate = " ".join(self.parts)
        self.parts.clear()
        if len(candidate) < self.min_chars:
            return None
        normalized = candidate.lower()
        if normalized == self.last_emitted.lower() and now - self.last_emitted_at < self.duplicate_seconds:
            return None
        self.last_emitted, self.last_emitted_at = candidate, now
        return Segment(candidate, now)
