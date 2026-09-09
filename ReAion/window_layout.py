#!/usr/bin/env python
"""Provider-independent Windows side-by-side layout."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Rect:
    left: int
    top: int
    width: int
    height: int


def split_work_area(left: int, top: int, width: int, height: int,
                    meeting_ratio: float = 0.63) -> tuple[Rect, Rect]:
    if width <= 0 or height <= 0:
        raise ValueError("work area must be positive")
    if not 0.50 <= meeting_ratio <= 0.80:
        raise ValueError("meeting_ratio must be between 0.50 and 0.80")
    meeting_width = round(width * meeting_ratio)
    answer_width = width - meeting_width
    return (
        Rect(left, top, meeting_width, height),
        Rect(left + meeting_width, top, answer_width, height),
    )


def arrange_windows(meeting_title_pattern: str, answer_title_pattern: str = "ChatGPT",
                    meeting_ratio: float = 0.63) -> dict:
    if os.name != "nt":
        return {"supported": False, "changed": False, "detail": "Windows only"}

    from pywinauto import Desktop
    desktop = Desktop(backend="uia")
    meeting = desktop.window(title_re=meeting_title_pattern)
    answer = desktop.window(title_re=answer_title_pattern)
    if not meeting.exists(timeout=2):
        raise RuntimeError("Meeting window not found")
    if not answer.exists(timeout=2):
        raise RuntimeError("ChatGPT answer window not found")

    # Use the work area of the monitor containing the meeting window.
    import win32api
    import win32con
    monitor = win32api.MonitorFromWindow(meeting.handle, win32con.MONITOR_DEFAULTTONEAREST)
    info = win32api.GetMonitorInfo(monitor)
    l, t, r, b = info["Work"]
    meeting_rect, answer_rect = split_work_area(l, t, r - l, b - t, meeting_ratio)

    meeting.restore()
    answer.restore()
    meeting.move_window(**meeting_rect.__dict__, repaint=True)
    answer.move_window(**answer_rect.__dict__, repaint=True)
    return {
        "supported": True,
        "changed": True,
        "meeting": meeting_rect.__dict__,
        "answer": answer_rect.__dict__,
    }

