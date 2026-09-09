#!/usr/bin/env python
import json
import subprocess
import sys
import time
from pathlib import Path

BASE = Path(__file__).resolve().parent
FEED = BASE / "live_transcript.jsonl"

FEED.write_text("", encoding="utf-8")

flags = getattr(subprocess, "CREATE_NEW_CONSOLE", 0)
gui = subprocess.Popen(
    [sys.executable, str(BASE / "interview_assistant_gui.py")],
    creationflags=flags
)

questions = [
    "Tell me about yourself.",
    "How would you troubleshoot a server that suddenly lost network connectivity?",
    "Can you describe a difficult hardware problem you investigated?",
    "How do you use Redfish or BMC tools in your work?"
]

print("Live-answer demo started.")
print("Watch the Interview Live Assistant window.")
time.sleep(2)

for i, q in enumerate(questions):
    print("INTERVIEWER:", q)
    with FEED.open("a", encoding="utf-8") as f:
        f.write(json.dumps({
            "stamp": f"0:00:{i*8:02d}",
            "speaker": "interviewer",
            "text": q,
            "ts": time.time()
        }) + "\n")
    time.sleep(8)

print()
print("Demo complete. The GUI may remain open for review.")
