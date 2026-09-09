"""Best-effort interview window arrangement and restoration."""
from __future__ import annotations
import os
from dataclasses import dataclass
from window_layout import arrange_windows

@dataclass
class LayoutSession:
    meeting_title_pattern: str
    answer_title_pattern: str = "ChatGPT"
    arranged: bool = False
    _original: dict = None

    def arrange(self):
        if os.name != "nt":
            return {"supported": False, "changed": False, "detail": "Windows only"}
        from pywinauto import Desktop
        desktop = Desktop(backend="uia")
        meeting = desktop.window(title_re=self.meeting_title_pattern)
        answer = desktop.window(title_re=self.answer_title_pattern)
        if not meeting.exists(timeout=2) or not answer.exists(timeout=2):
            raise RuntimeError("meeting or ChatGPT window not found")
        self._original = {"meeting": meeting.rectangle(), "answer": answer.rectangle()}
        result = arrange_windows(self.meeting_title_pattern, self.answer_title_pattern)
        self.arranged = bool(result.get("changed"))
        return result

    def restore(self):
        if os.name != "nt" or not self._original:
            return {"supported": os.name == "nt", "changed": False, "detail": "No captured layout"}
        from pywinauto import Desktop
        desktop = Desktop(backend="uia")
        for key, pattern in (("meeting", self.meeting_title_pattern), ("answer", self.answer_title_pattern)):
            window = desktop.window(title_re=pattern)
            if window.exists(timeout=1):
                rect = self._original[key]
                window.move_window(rect.left, rect.top, rect.width(), rect.height(), repaint=True)
        self.arranged = False
        return {"supported": True, "changed": True, "detail": "Original window positions restored"}
