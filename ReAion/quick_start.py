#!/usr/bin/env python
"""Simple one-click launcher UI for ReAion.

The meeting URL is armed first. ReAion does not start transcription until the
browser extension reports that the user is actually inside the call.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import time
import tkinter as tk
from tkinter import messagebox
import urllib.error
import urllib.parse
import urllib.request
import webbrowser

BASE = Path(__file__).resolve().parent
WATCHER_URL = "http://127.0.0.1:8765/status"
ARM_URL = "http://127.0.0.1:8765/select-meeting"
SUPPORTED_HOSTS = (
    "meet.google.com",
    "teams.microsoft.com",
    "teams.live.com",
    "zoom.us",
    "webex.com",
    "app.chime.aws",
)


def _request_json(url: str, method: str = "GET", payload: dict | None = None, timeout: float = 2.0):
    data = None
    headers = {}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def watcher_running() -> bool:
    try:
        return bool(_request_json(WATCHER_URL).get("ok"))
    except Exception:
        return False


def start_watcher() -> bool:
    if watcher_running():
        return True
    flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    subprocess.Popen(
        [sys.executable, str(BASE / "auto_meet_watch.py")],
        cwd=str(BASE),
        creationflags=flags,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    deadline = time.time() + 10
    while time.time() < deadline:
        if watcher_running():
            return True
        time.sleep(0.25)
    return False


def normalize_meeting_url(raw: str) -> str:
    raw = raw.strip()
    if not raw:
        raise ValueError("Paste your interview link first.")
    parsed = urllib.parse.urlsplit(raw)
    if parsed.scheme.lower() != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("Use a valid HTTPS interview link.")
    host = parsed.hostname.lower().rstrip(".")
    if not any(host == allowed or host.endswith("." + allowed) for allowed in SUPPORTED_HOSTS):
        raise ValueError("Supported links: Google Meet, Microsoft Teams, Zoom, Webex, and Amazon Chime.")
    return urllib.parse.urlunsplit(("https", parsed.netloc, parsed.path or "/", parsed.query, ""))


def arm_meeting(url: str) -> None:
    result = _request_json(ARM_URL, method="POST", payload={"url": url, "title": "Interview"})
    if not result.get("ok"):
        raise RuntimeError(result.get("error") or "ReAion could not arm the meeting.")


def open_in_chrome(url: str) -> None:
    candidates = []
    local = os.environ.get("LOCALAPPDATA")
    program_files = os.environ.get("PROGRAMFILES")
    program_files_x86 = os.environ.get("PROGRAMFILES(X86)")
    if local:
        candidates.append(Path(local) / "Google/Chrome/Application/chrome.exe")
    if program_files:
        candidates.append(Path(program_files) / "Google/Chrome/Application/chrome.exe")
    if program_files_x86:
        candidates.append(Path(program_files_x86) / "Google/Chrome/Application/chrome.exe")
    for chrome in candidates:
        if chrome.exists():
            subprocess.Popen([str(chrome), url])
            return
    webbrowser.open(url, new=1)


def main() -> int:
    if not start_watcher():
        messagebox.showerror("ReAion", "ReAion could not start its local watcher on port 8765.")
        return 1

    root = tk.Tk()
    root.title("ReAion")
    root.geometry("560x215")
    root.resizable(False, False)
    root.configure(bg="#202124")

    title = tk.Label(root, text="Start interview", bg="#202124", fg="white", font=("Segoe UI", 18, "bold"))
    title.pack(anchor="w", padx=24, pady=(22, 6))
    subtitle = tk.Label(
        root,
        text="Paste the interview link. ReAion opens it now, but listens only after you join the call.",
        bg="#202124", fg="#c9c9cf", font=("Segoe UI", 10), wraplength=500, justify="left"
    )
    subtitle.pack(anchor="w", padx=24)

    entry = tk.Entry(root, font=("Segoe UI", 11), bg="#303134", fg="white", insertbackground="white", relief="flat")
    entry.pack(fill="x", padx=24, pady=(16, 12), ipady=8)
    entry.focus_set()

    status = tk.StringVar(value="Waiting for interview link")
    status_label = tk.Label(root, textvariable=status, bg="#202124", fg="#b9a7ff", font=("Segoe UI", 9))
    status_label.pack(anchor="w", padx=24)

    def launch(_event=None):
        try:
            url = normalize_meeting_url(entry.get())
            status.set("Arming meeting...")
            root.update_idletasks()
            arm_meeting(url)
            open_in_chrome(url)
            status.set("Meeting opened — waiting for you to join before listening")
            root.after(1600, root.destroy)
        except (ValueError, RuntimeError, urllib.error.URLError) as exc:
            status.set("Ready")
            messagebox.showerror("ReAion", str(exc))

    button = tk.Button(
        root, text="Start Interview", command=launch,
        bg="#8b5cf6", fg="white", activebackground="#7c3aed", activeforeground="white",
        relief="flat", font=("Segoe UI", 10, "bold"), padx=18, pady=8, cursor="hand2"
    )
    button.place(relx=1.0, rely=1.0, x=-24, y=-18, anchor="se")
    root.bind("<Return>", launch)
    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
