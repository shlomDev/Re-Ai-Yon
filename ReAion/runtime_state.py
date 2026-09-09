"""Atomic, per-user IPC for the desktop view and browser side panel."""
import json
import os
import tempfile
import time
import uuid
from app_paths import private_path


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(dir=path.parent, prefix='.copilot-', suffix='.tmp')
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as stream:
            json.dump(data, stream, ensure_ascii=False)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary): os.unlink(temporary)


def read_json(path, default):
    try:
        return json.loads(path.read_text(encoding='utf-8-sig'))
    except (OSError, ValueError):
        return default


def publish(state):
    write_json(private_path('panel_state.json'), dict(state, updated_at=time.time()))


def read_state():
    data = read_json(private_path('panel_state.json'), {})
    if time.time() - data.get('updated_at', 0) > 10:
        return {'state': 'NOT LISTENING', 'question': '', 'answer': '', 'progress': '',
                'detail': 'Start an interview session. No current assistant heartbeat.'}
    return data


def request_next():
    state = read_state()
    write_json(private_path('panel_next.json'), {'id': uuid.uuid4().hex, 'generation': state.get('generation')})
