"""Small, readable answer chunks and microphone-progress tracking."""
from __future__ import annotations
import re

def words(text):
    return re.findall(r"[^\W_]+(?:['’][^\W_]+)?", (text or "").lower(), re.UNICODE)

def chunk_answer(answer: str, max_words: int = 28):
    sentences = re.split(r"(?<=[.!?])\s+", " ".join((answer or "").split()))
    chunks, current = [], []
    count = 0
    for sentence in sentences:
        tokens = sentence.split()
        if len(tokens) > max_words:
            if current: chunks.append(" ".join(current)); current, count = [], 0
            chunks.extend(" ".join(tokens[i:i+max_words]) for i in range(0, len(tokens), max_words))
            continue
        n = len(words(sentence))
        if current and count + n > max_words:
            chunks.append(" ".join(current)); current, count = [], 0
        current.append(sentence); count += n
    if current: chunks.append(" ".join(current))
    return chunks

class Teleprompter:
    def __init__(self, answer="", max_words=28):
        self.max_words = max_words
        self.chunks = chunk_answer(answer, max_words)
        self.index = 0
        self.heard = set()
    def set_answer(self, answer):
        self.chunks = chunk_answer(answer, self.max_words); self.index = 0; self.heard.clear()
    def current(self):
        return self.chunks[self.index] if self.chunks else ""
    def observe(self, transcript):
        self.heard.update(words(transcript))
        target = set(words(self.current()))
        if target and len(target & self.heard) / len(target) >= 0.70:
            if self.index < len(self.chunks) - 1:
                self.index += 1; self.heard.clear(); return True
        return False
    def advance(self):
        if self.index < len(self.chunks) - 1: self.index += 1; self.heard.clear(); return True
        return False
