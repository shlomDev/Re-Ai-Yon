#!/usr/bin/env python
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import datetime as dt
import json
import subprocess
import sys
import threading
import time
import urllib.parse
from window_manager import LayoutSession
from app_paths import private_path
from runtime_state import read_state, request_next, write_json
from launcher import worker_command

HOST = "127.0.0.1"
PORT = 8765
HEARTBEAT_TIMEOUT = 12

BASE = Path(__file__).resolve().parent
CONFIG_FILE = private_path("interviews.json")
STATE_FILE = private_path("scheduled_test_state.json")
STOP_FILE = private_path("stop_transcriber")

last_call_heartbeat = {}
last_extension_health = None
transcriber_proc = None
assistant_gui_proc = None
active_interview_id = None
layout_session = None
selected_meeting = None
listening_paused = False
lock = threading.Lock()


def load_config():
    try:
        data = json.loads(CONFIG_FILE.read_text(encoding="utf-8-sig"))
        return data.get("interviews", [])
    except FileNotFoundError:
        return []
    except Exception as e:
        print(f"Config error: {e}", file=sys.stderr)
        return []


def parse_iso(value):
    d = dt.datetime.fromisoformat(value)
    if d.tzinfo is None:
        d = d.astimezone()
    return d


def now_for(d):
    return dt.datetime.now(d.tzinfo)


def interview_window(item):
    start = parse_iso(item["start"])
    end = parse_iso(item["end"])
    before = dt.timedelta(minutes=int(item.get("arm_before_minutes", 20)))
    after = dt.timedelta(minutes=int(item.get("arm_after_minutes", 30)))
    return start - before, end + after


def find_armed_interview(meeting_code):
    for item in load_config():
        if str(item.get("meeting_code", "")).lower() != meeting_code.lower():
            continue
        arm_start, arm_end = interview_window(item)
        now = now_for(arm_start)
        if arm_start <= now <= arm_end:
            return item
    return None

def find_armed_desktop_interview():
    """Detect an active Teams/Zoom/Webex desktop window during its configured window."""
    try:
        from pywinauto import Desktop
        titles = [w.window_text() for w in Desktop(backend="uia").windows() if w.is_visible()]
    except Exception:
        return None
    for item in load_config():
        provider = str(item.get("provider", "generic")).lower()
        if provider not in {"teams", "microsoft_teams", "zoom", "webex", "chime"}:
            continue
        arm_start, arm_end = interview_window(item)
        if not (arm_start <= now_for(arm_start) <= arm_end):
            continue
        patterns = {"teams": ("teams", "microsoft teams"), "microsoft_teams": ("teams", "microsoft teams"), "zoom": ("zoom",), "webex": ("webex",), "chime": ("chime",)}.get(provider, (provider,))
        if any(any(p in title.lower() for p in patterns) for title in titles):
            return item
    return None

def desktop_call_monitor():
    while True:
        try:
            item = find_armed_desktop_interview()
            if item is not None:
                interview_id = str(item.get("id"))
                last_call_heartbeat[interview_id] = time.monotonic()
                start_transcriber(item)
        except Exception as exc:
            print(f"Desktop meeting detection error: {exc}", file=sys.stderr)
        time.sleep(3)


def start_transcriber(item):
    global transcriber_proc, active_interview_id, layout_session

    with lock:
        if transcriber_proc is not None and transcriber_proc.poll() is None:
            return

        if STOP_FILE.exists():
            try:
                STOP_FILE.unlink()
            except OSError:
                pass

        import re
        for name in ('live_transcript.jsonl', 'candidate_transcript.jsonl'):
            private_path(name).write_text('', encoding='utf-8')
        private_path('stop_assistant').unlink(missing_ok=True)
        safe_id = re.sub(r"[^a-zA-Z0-9_-]", "_", str(item.get("id", "interview")))[:100]
        cmd = worker_command("transcriber") + [
            "--stop-file", str(STOP_FILE),
            "--output", str(private_path("recordings") / safe_id),
            "--model", "large-v3-turbo",
            "--language", "auto",
            "--chunk-seconds", "3",
        ]
        flags = getattr(subprocess, "CREATE_NEW_CONSOLE", 0)
        transcriber_proc = subprocess.Popen(cmd, creationflags=flags)
        global assistant_gui_proc
        try:
            if assistant_gui_proc is None or assistant_gui_proc.poll() is not None:
                assistant_gui_proc = subprocess.Popen(
                    worker_command("assistant"),
                    creationflags=flags
                )
        except Exception as e:
            print(f"[warning] Could not launch interview assistant GUI: {e}", file=sys.stderr)
        # Best effort only: layout failure must never interrupt the meeting.
        try:
            title_re = str(item.get("meeting_window_title_regex", "Meet|Teams|Zoom|Chime|Webex"))
            layout_session = LayoutSession(title_re)
            layout_session.arrange()
        except Exception as e:
            print(f"[warning] Window layout unavailable: {e}", file=sys.stderr)
        active_interview_id = safe_id
        print(f"Interview detected -> transcriber started: {item.get('title', safe_id)}", flush=True)


def request_stop():
    global transcriber_proc, layout_session
    with lock:
        if transcriber_proc is not None and transcriber_proc.poll() is None:
            STOP_FILE.touch()
        if assistant_gui_proc is not None and assistant_gui_proc.poll() is None:
            private_path('stop_assistant').touch()
        if layout_session is not None:
            try:
                layout_session.restore()
            except Exception:
                pass
        print("Configured Meet call no longer detected -> graceful stop requested.", flush=True)


def load_state():
    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8-sig"))
    except Exception:
        return {}


def save_state(state):
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def launch_self_test(item, label):
    cmd = worker_command("audio-test") + [
        "--label", f"{item.get('id', 'interview')}:{label}",
    ]
    flags = getattr(subprocess, "CREATE_NEW_CONSOLE", 0)
    subprocess.Popen(cmd, creationflags=flags)
    print(f"Self-test launched: {item.get('title')} / {label}", flush=True)


def scheduled_test_monitor():
    """Run relative tests. If Windows was asleep/off, run within catch-up window."""
    while True:
        try:
            state = load_state()
            changed = False
            for item in load_config():
                start = parse_iso(item["start"])
                now = now_for(start)
                for test in item.get("self_tests", []):
                    label = str(test["label"])
                    key = f"{item.get('id')}::{label}"
                    if state.get(key):
                        continue

                    due = start + dt.timedelta(minutes=int(test["offset_minutes"]))
                    catchup = dt.timedelta(minutes=int(test.get("catchup_minutes", 10)))
                    if due <= now <= due + catchup:
                        launch_self_test(item, label)
                        state[key] = {
                            "launched_at": now.isoformat(),
                            "due": due.isoformat(),
                        }
                        changed = True

            if changed:
                save_state(state)
        except Exception as e:
            print(f"Scheduled-test monitor error: {e}", file=sys.stderr)

        time.sleep(20)


def call_monitor():
    global active_interview_id
    while True:
        time.sleep(2)
        running = transcriber_proc is not None and transcriber_proc.poll() is None
        if not active_interview_id:
            continue
        if not running:
            request_stop()
            active_interview_id = None
            from runtime_state import publish
            publish({'state': 'CAPTURE STOPPED', 'question':'', 'answer':'', 'detail':'Capture process ended. Check its terminal for audio/model errors.'})
            continue

        last = last_call_heartbeat.get(active_interview_id)
        if last is None or time.monotonic() - last > HEARTBEAT_TIMEOUT:
            request_stop()
            active_interview_id = None


def status_payload():
    now_mono = time.monotonic()
    age = None
    if last_extension_health is not None:
        age = max(0.0, now_mono - last_extension_health)

    configured = []
    for item in load_config():
        arm_start, arm_end = interview_window(item)
        configured.append({
            "id": item.get("id"),
            "title": item.get("title"),
            "meeting_code": item.get("meeting_code"),
            "start": item.get("start"),
            "end": item.get("end"),
            "armed_now": arm_start <= now_for(arm_start) <= arm_end,
        })

    return {
        "ok": True,
        "watcher": "running",
        "extension_health_age_seconds": age,
        "configured_interviews": configured,
        "active_interview_id": active_interview_id,
    }


class Handler(BaseHTTPRequestHandler):
    def allowed(self):
        host = self.headers.get('Host', '')
        origin = self.headers.get('Origin', '')
        return host in ('127.0.0.1:8765', 'localhost:8765') and (
            not origin or origin in ('http://127.0.0.1:8765', 'http://localhost:8765') or origin.startswith('chrome-extension://'))

    def _cors(self):
        origin = self.headers.get('Origin', '')
        if origin.startswith('chrome-extension://'):
            self.send_header("Access-Control-Allow-Origin", origin)
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _json(self, code, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(code)
        self._cors()
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_GET(self):
        if not self.allowed():
            self._json(403, {"error": "Origin or host rejected"}); return
        if self.path == "/status":
            self._json(200, status_payload())
        elif self.path == "/panel-state":
            self._json(200, read_state())
        else:
            self._json(404, {"ok": False})

    def do_POST(self):
        global last_extension_health, selected_meeting, listening_paused
        if not self.allowed():
            self._json(403, {"error": "Origin or host rejected"}); return

        try: length = int(self.headers.get("Content-Length", "0") or 0)
        except ValueError:
            self._json(400, {"error": "Invalid length"}); return
        if not 0 <= length <= 16384:
            self._json(413, {"error": "Body too large"}); return
        raw = self.rfile.read(length)
        try:
            data = json.loads(raw.decode("utf-8")) if raw else {}
        except Exception:
            self._json(400, {"error": "Invalid JSON"}); return
        if not isinstance(data, dict):
            self._json(400, {"error": "Expected object"}); return

        if self.path == "/extension-health":
            last_extension_health = time.monotonic()
            self._json(200, {"ok": True})
            return

        if self.path == '/select-meeting':
            url = str(data.get('url', ''))
            parsed = urllib.parse.urlsplit(url)
            if parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password:
                self._json(400, {'error': 'Select an HTTPS meeting tab'}); return
            listening_paused = False
            selected_meeting = {'id': 'selected-browser-session', 'title': str(data.get('title', 'Interview'))[:200],
                                'meeting_url': url.split('#')[0]}
            self._json(200, {'ok': True}); return
        if self.path == '/stop':
            listening_paused = True
            selected_meeting = None
            request_stop()
            self._json(200, {'ok': True}); return

        if self.path == '/generate-report':
            state = read_state()
            report = {
                'title': 'ReAion Interview Summary',
                'summary': state.get('summary', {}),
                'generated_at': dt.datetime.now(dt.timezone.utc).isoformat(),
            }
            report_path = private_path('interview_report.json')
            write_json(report_path, report)
            self._json(200, {'ok': True, 'message': f'Report saved locally: {report_path.name}'})
            return

        if self.path == "/panel-next":
            request_next()
            self._json(200, {"ok": True})
            return

        if self.path != "/heartbeat":
            self._json(404, {"ok": False})
            return

        code = str(data.get("meet_code", "")).lower()
        in_call = bool(data.get("in_call", False)) and not listening_paused
        url = str(data.get('url', '')).split('#')[0]
        item = None
        if in_call:
            if selected_meeting and selected_meeting['meeting_url'] == url:
                item = selected_meeting
            else:
                for configured in load_config():
                    if configured.get('meeting_url', '').split('#')[0] != url: continue
                    try:
                        arm_start, arm_end = interview_window(configured)
                        if arm_start <= now_for(arm_start) <= arm_end: item = configured
                    except (ValueError, KeyError): continue

        if item is not None:
            interview_id = str(item.get("id"))
            last_call_heartbeat[interview_id] = time.monotonic()
            start_transcriber(item)
            self._json(200, {"ok": True, "armed": True, "interview_id": interview_id})
        else:
            self._json(200, {"ok": True, "armed": False})

    def log_message(self, *_):
        pass


def main():
    items = load_config()
    print("ReAion — Interview Assistant")
    print("----------------------------------")
    if not items:
        print("No interviews configured in interviews.json")
    else:
        print("Configured interviews:")
        for item in items:
            arm_start, arm_end = interview_window(item)
            print(f"  - {item.get('title')}")
            print(f"    Meet: {item.get('meeting_url')}")
            print(f"    Start: {item.get('start')}")
            print(f"    Armed: {arm_start.isoformat()} -> {arm_end.isoformat()}")
            for test in item.get("self_tests", []):
                start = parse_iso(item["start"])
                due = start + dt.timedelta(minutes=int(test["offset_minutes"]))
                print(f"    Test {test['label']}: {due.isoformat()}")
    print()
    print("Provider-independent meeting detection is active.")
    print("Waiting for configured meeting window or browser extension heartbeat...")

    threading.Thread(target=call_monitor, daemon=True).start()
    # Title-only desktop auto-start is disabled: it cannot prove a call is active.
    threading.Thread(target=scheduled_test_monitor, daemon=True).start()

    server = ThreadingHTTPServer((HOST, PORT), Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        request_stop()
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
