#!/usr/bin/env python
"""Supported-session ChatGPT Windows companion integration.

This module never reads browser data or authentication material. It uses the
official app's documented Companion Window shortcut and ordinary Windows UI
Automation. The ChatGPT window remains the answer surface; responses are not
scraped back into this process.
"""

from __future__ import annotations

import os
import re
import time
from dataclasses import dataclass
from platform_support import capabilities


CHATGPT_TITLE_RE = re.compile(r"\bchatgpt\b", re.IGNORECASE)


def is_chatgpt_title(title: str) -> bool:
    return bool(CHATGPT_TITLE_RE.search(title or ""))


def build_interview_prompt(question: str) -> str:
    question = " ".join((question or "").split()).strip()
    if not question:
        raise ValueError("question is empty")
    return (
        "INTERVIEWER QUESTION: " + question + "\n\n"
        "Use only candidate facts available in this conversation or supplied profile. "
        "Do not assume access to other chats or a resume. Prefer a verified real example.\n\n"
        "Give only a concise suggested spoken answer (about 45–90 seconds). "
        "Use my real background and prior interview context; never invent facts. "
        "For technical questions answer directly with practical steps and validation. "
        "For behavioral questions use a natural compact STAR answer. Make it easy to scan."
    )


@dataclass
class ChatGPTStatus:
    supported: bool
    ready: bool
    detail: str
    window_title: str = ""
    account_state: str = "unknown"


class ChatGPTWindowsClient:
    """Submit a question to an already signed-in official ChatGPT app."""

    def __init__(self, open_shortcut: str = "% ", window_timeout: float = 5.0):
        self.open_shortcut = open_shortcut
        self.window_timeout = window_timeout

    @staticmethod
    def _desktop():
        from pywinauto import Desktop
        return Desktop(backend="uia")

    def _windows(self):
        return [
            w for w in self._desktop().windows()
            if w.is_visible() and is_chatgpt_title(w.window_text())
        ]

    def status(self) -> ChatGPTStatus:
        if os.name != "nt":
            system = capabilities()["platform"]
            return ChatGPTStatus(
                False, False,
                f"{system}: desktop ChatGPT UI Automation adapter not implemented; use built-in fallback"
            )
        try:
            windows = self._windows()
        except ImportError:
            return ChatGPTStatus(True, False, "pywinauto is not installed")
        except Exception as exc:
            return ChatGPTStatus(True, False, f"UI Automation error: {exc}")
        if not windows:
            return ChatGPTStatus(
                True, False,
                "ChatGPT window not found; open the official app and sign in"
            )
        title = windows[0].window_text()
        return ChatGPTStatus(True, True, "ChatGPT window found; account tier not inspected", title, "signed_in_or_usable_unknown_tier")

    def _open_companion(self):
        from pywinauto.keyboard import send_keys
        send_keys(self.open_shortcut)
        deadline = time.monotonic() + self.window_timeout
        while time.monotonic() < deadline:
            windows = self._windows()
            if windows:
                return windows[0]
            time.sleep(0.15)
        raise RuntimeError("ChatGPT Companion Window did not appear")

    @staticmethod
    def _clipboard_paste_and_submit(prompt: str):
        import win32clipboard
        from pywinauto.keyboard import send_keys

        previous = None
        win32clipboard.OpenClipboard()
        try:
            try:
                previous = win32clipboard.GetClipboardData(win32clipboard.CF_UNICODETEXT)
            except Exception:
                previous = None
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardText(prompt, win32clipboard.CF_UNICODETEXT)
        finally:
            win32clipboard.CloseClipboard()

        try:
            send_keys("^v{ENTER}", pause=0.03)
        finally:
            if previous is not None:
                time.sleep(0.1)
                win32clipboard.OpenClipboard()
                try:
                    win32clipboard.EmptyClipboard()
                    win32clipboard.SetClipboardText(previous, win32clipboard.CF_UNICODETEXT)
                finally:
                    win32clipboard.CloseClipboard()

    def submit_question(self, question: str) -> str:
        if os.name != "nt":
            raise RuntimeError("ChatGPT Windows integration requires Windows")
        prompt = build_interview_prompt(question)
        window = self._open_companion()
        window.set_focus()
        time.sleep(0.15)

        # Safety invariant: never type unless focus is still on a ChatGPT window.
        foreground = self._desktop().get_active()
        title = foreground.window_text() if foreground else ""
        if not is_chatgpt_title(title):
            raise RuntimeError(f"Refusing to type: active window is not ChatGPT ({title!r})")

        self._clipboard_paste_and_submit(prompt)
        return title
