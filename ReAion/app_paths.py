"""Per-user paths and privacy boundaries for installed ReAion."""
from __future__ import annotations
import os
from pathlib import Path

APP_NAME = "InterviewCopilot"
PROJECT_DIR = Path(__file__).resolve().parent

def user_data_dir() -> Path:
    override = os.getenv("INTERVIEWCOPILOT_DATA_DIR")
    if override:
        path = Path(override).expanduser()
    elif os.name == "nt":
        path = Path(os.getenv("LOCALAPPDATA", Path.home() / "AppData/Local")) / APP_NAME
    elif os.sys.platform == "darwin":
        path = Path.home() / "Library/Application Support" / APP_NAME
    else:
        path = Path(os.getenv("XDG_DATA_HOME", Path.home() / ".local/share")) / APP_NAME
    path.mkdir(parents=True, exist_ok=True)
    return path

def private_path(name: str) -> Path:
    return user_data_dir() / name

def settings_path() -> Path:
    return private_path("assistant_settings.json") if private_path("assistant_settings.json").exists() else PROJECT_DIR / "assistant_settings.json"
