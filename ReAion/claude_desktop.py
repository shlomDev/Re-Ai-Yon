"""Guarded automation for a user-signed-in Claude Desktop window.

The user opens Claude Desktop and signs in normally (including the free plan).
This module only uses visible UI controls; it never reads cookies or tokens.
"""
from __future__ import annotations
import os, re, time
from dataclasses import dataclass

CLAUDE_TITLE_RE = re.compile(r"\bclaude\b", re.I)

def is_claude_title(title): return bool(CLAUDE_TITLE_RE.search(title or ""))

@dataclass
class ClaudeStatus:
    supported: bool
    ready: bool
    detail: str
    window_title: str = ""
    account_state: str = "unknown"

class ClaudeDesktopClient:
    def __init__(self, timeout=5): self.timeout = timeout
    @staticmethod
    def _desktop():
        from pywinauto import Desktop
        return Desktop(backend="uia")
    def _windows(self):
        return [w for w in self._desktop().windows() if w.is_visible() and is_claude_title(w.window_text())]
    def status(self):
        if os.name != "nt":
            return ClaudeStatus(False, False, "Claude Desktop UI automation currently requires Windows UI Automation")
        try: windows = self._windows()
        except ImportError: return ClaudeStatus(True, False, "pywinauto is not installed")
        except Exception as exc: return ClaudeStatus(True, False, f"UI Automation error: {exc}")
        if not windows: return ClaudeStatus(True, False, "Open Claude Desktop and sign in (Free plan is supported)")
        return ClaudeStatus(True, True, "Claude Desktop window found; account tier not inspected", windows[0].window_text(), "signed_in_or_usable_unknown_tier")
    def submit_question(self, question):
        if os.name != "nt": raise RuntimeError("Claude Desktop automation requires Windows")
        prompt = ("INTERVIEWER QUESTION: " + " ".join((question or "").split()) +
                  "\n\nGive only a concise suggested spoken answer in the same language. "
                  "Use my real background; never invent facts. Technical: explain reasoning, assumptions, steps and validation. "
                  "Competency: use STARL only when appropriate.")
        windows = self._windows()
        if not windows: raise RuntimeError("Claude Desktop window not found")
        window = windows[0]; window.set_focus(); time.sleep(.15)
        active = self._desktop().get_active(); title = active.window_text() if active else ""
        if not is_claude_title(title): raise RuntimeError(f"Refusing to type into active window {title!r}")
        import win32clipboard
        from pywinauto.keyboard import send_keys
        win32clipboard.OpenClipboard(); old = None
        try:
            try: old = win32clipboard.GetClipboardData(win32clipboard.CF_UNICODETEXT)
            except Exception: pass
            win32clipboard.EmptyClipboard(); win32clipboard.SetClipboardText(prompt, win32clipboard.CF_UNICODETEXT)
        finally: win32clipboard.CloseClipboard()
        try: send_keys("^v{ENTER}", pause=.03)
        finally:
            if old is not None:
                time.sleep(.1); win32clipboard.OpenClipboard()
                try: win32clipboard.EmptyClipboard(); win32clipboard.SetClipboardText(old, win32clipboard.CF_UNICODETEXT)
                finally: win32clipboard.CloseClipboard()
        return title
