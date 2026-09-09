"""One executable entry point with explicit worker dispatch."""
import sys
from pathlib import Path

def worker_command(mode):
    if getattr(sys, "frozen", False):
        return [sys.executable, "--worker", mode]
    return [sys.executable, str(Path(__file__).with_name("launcher.py")), "--worker", mode]

def main():
    mode = "watcher"
    if len(sys.argv) >= 3 and sys.argv[1] == "--worker":
        mode = sys.argv[2]
        del sys.argv[1:3]
    if mode == "transcriber":
        from meet_transcriber import main as run
    elif mode == "assistant":
        from interview_assistant_gui import main as run
    elif mode == "audio-test":
        from audio_self_test import main as run
    elif mode == "watcher":
        from auto_meet_watch import main as run
    else:
        raise SystemExit("Unknown worker mode")
    return run()

if __name__ == "__main__":
    raise SystemExit(main())
