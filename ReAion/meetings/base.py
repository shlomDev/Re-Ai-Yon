from dataclasses import dataclass
from typing import Protocol
import re

@dataclass(frozen=True)
class MeetingContext:
    title: str = ""
    url: str = ""
    process_name: str = ""

class MeetingAdapter(Protocol):
    name: str
    def matches(self, context: MeetingContext) -> bool: ...
    def is_call_active(self, context: MeetingContext) -> bool: ...

class PatternAdapter:
    def __init__(self, name, url_pattern, process_patterns=()):
        self.name = name
        self.url_re = re.compile(url_pattern, re.I)
        self.process_res = [re.compile(p, re.I) for p in process_patterns]
    def matches(self, context):
        return bool(self.url_re.search(context.url or "")) or any(
            p.search(context.process_name or "") for p in self.process_res)
    def is_call_active(self, context):
        return False  # A URL or process match does not establish an active call.

ADAPTERS = [
    PatternAdapter("google_meet", r"https?://meet\.google\.com/", ()),
    PatternAdapter("teams", r"https?://teams\.microsoft\.com/", (r"teams",)),
    PatternAdapter("zoom", r"https?://(?:[\w-]+\.)?zoom\.us/", (r"zoom",)),
    PatternAdapter("chime", r"https?://app\.chime\.aws/", (r"chime",)),
    PatternAdapter("webex", r"https?://(?:[\w-]+\.)?webex\.com/", (r"webex",)),
    PatternAdapter("generic", r"$^", ()),
]

def detect_provider(context):
    for adapter in ADAPTERS[:-1]:
        if adapter.matches(context):
            return adapter.name
    return "generic"
