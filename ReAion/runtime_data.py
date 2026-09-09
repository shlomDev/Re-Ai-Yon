"""Load private interview data from local files without requiring them in Git."""
from __future__ import annotations
import json
from pathlib import Path
from app_paths import PROJECT_DIR, private_path

BASE = Path(__file__).resolve().parent

def text(name: str, default: str = "") -> str:
    path = private_path(name)
    try:
        return path.read_text(encoding="utf-8-sig")
    except (FileNotFoundError, OSError):
        return default

def json_data(name: str, default):
    path = private_path(name)
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return default
