"""Fast, non-invasive readiness checks used before an interview."""
from __future__ import annotations
import json
from pathlib import Path
from discovery.registry import validate_interview
from meetings.base import MeetingContext, detect_provider
from app_paths import private_path

BASE = Path(__file__).resolve().parent

def run_preflight(item: dict) -> list[dict]:
    results = []
    errors = validate_interview(item)
    results.append({"name": "interview configuration", "ok": not errors,
                    "detail": "; ".join(errors) if errors else "valid"})
    provider = detect_provider(MeetingContext(url=item.get("meeting_url", "")))
    results.append({"name": "meeting provider", "ok": provider != "generic",
                    "detail": provider})
    try:
        from answer_engine import ai_status
        st = ai_status()
        results.append({"name": "answer provider", "ok": bool(st.get("ready")),
                        "detail": st.get("detail", st.get("provider", "unknown"))})
    except Exception as exc:
        results.append({"name": "answer provider", "ok": False, "detail": str(exc)})
    return results

def main():
    path = private_path("interviews.json")
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
        interviews = data.get('interviews', [])
        if not interviews:
            print('FAIL: no scheduled interviews. Use the browser panel to select a session.')
            return 1
        ok = True
        for interview in interviews:
            print(interview.get('title'))
            for row in run_preflight(interview):
                print(('PASS' if row['ok'] else 'FAIL'), row['name'], '-', row['detail'])
                ok = ok and row['ok']
        return 0 if ok else 1
    except (OSError, ValueError, AttributeError) as exc:
        print('FAIL interview configuration:', exc)
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
