from __future__ import annotations
import re
from urllib.parse import urlparse

PROVIDERS = {
    "google_meet": re.compile(r"meet\.google\.com", re.I),
    "teams": re.compile(r"teams\.microsoft\.com|teams\.live\.com", re.I),
    "zoom": re.compile(r"(?:zoom\.us|zoom\.com)", re.I),
    "chime": re.compile(r"app\.chime\.aws", re.I),
    "webex": re.compile(r"webex\.com", re.I),
}

def extract_meeting_url(text: str) -> tuple[str, str] | None:
    for raw in re.findall(r"https?://[^\s<>\]\)\"']+", text or ""):
        raw = raw.rstrip(".,;!?")
        parsed = urlparse(raw)
        if not parsed.netloc:
            continue
        for provider, pattern in PROVIDERS.items():
            if pattern.search(parsed.netloc + parsed.path):
                return provider, raw
    return None

def validate_interview(item: dict) -> list[str]:
    errors = []
    for key in ("id", "title", "start", "end"):
        if not item.get(key): errors.append(f"missing {key}")
    if not item.get("meeting_url") and not item.get("meeting_code"):
        errors.append("missing meeting_url or meeting_code")
    return errors
