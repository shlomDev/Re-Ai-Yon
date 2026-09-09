"""Runtime capability matrix for Windows, macOS and Linux."""
from __future__ import annotations
import os
import platform

def capabilities() -> dict:
    system = platform.system().lower()
    return {
        "platform": system,
        "audio_capture": True,
        "gui": True,
        "whisper": True,
        "provider_detection": True,
        "chatgpt_desktop_uia": system == "windows",
        "windows_master_volume": system == "windows",
        "win32_window_layout": system == "windows",
        "manual_layout_required": system != "windows",
    }

def summary() -> str:
    c = capabilities()
    if c["platform"] == "windows":
        return "Windows: integration code present; audio, login and live meeting require testing"
    if c["platform"] == "darwin":
        return "macOS: experimental; audio/GUI/transcription require testing; desktop ChatGPT automation requires a signed-in app and accessibility adapter"
    return "Linux: experimental; audio/GUI/transcription require testing; desktop ChatGPT automation requires an accessibility adapter"
