#!/usr/bin/env python
"""Desktop view over the same live state used by the Chrome side panel."""
import threading
import tkinter as tk

from live_session import run
from app_paths import private_path
from runtime_state import read_state, request_next


COLORS = {
    "bg": "#171717",
    "surface": "#202020",
    "text": "#f8f7fb",
    "muted": "#b9b4c2",
    "violet": "#7442cf",
    "violet_hover": "#8655dd",
    "amber": "#ffc400",
}


class App:
    def __init__(self, root):
        self.root = root
        self.stop = threading.Event()
        root.title("ReAion")
        root.geometry("600x760")
        root.minsize(380, 500)
        root.configure(bg=COLORS["bg"])

        frame = tk.Frame(root, bg=COLORS["bg"], padx=20, pady=20)
        frame.pack(fill="both", expand=True)
        header = tk.Frame(frame, bg=COLORS["bg"])
        header.pack(fill="x", pady=(0, 4))
        tk.Label(header, text="↑", bg=COLORS["violet"], fg="white", font=("Segoe UI", 18, "bold"), width=2, pady=4).pack(side="left", padx=(0, 10))
        title = tk.Frame(header, bg=COLORS["bg"])
        title.pack(side="left")
        tk.Label(title, text="ReAion", bg=COLORS["bg"], fg=COLORS["text"], font=("Segoe UI", 16, "bold")).pack(anchor="w")
        tk.Label(title, text="Live interview assistant", bg=COLORS["bg"], fg=COLORS["muted"], font=("Segoe UI", 9)).pack(anchor="w")
        self.status = tk.StringVar()
        tk.Label(header, textvariable=self.status, bg=COLORS["bg"], fg=COLORS["amber"], font=("Segoe UI", 9, "bold")).pack(side="right")
        tk.Frame(frame, bg=COLORS["amber"], height=4).pack(fill="x", pady=(8, 18))

        tk.Label(frame, text="DETECTED QUESTION", bg=COLORS["bg"], fg=COLORS["amber"], font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 7))
        self.question = tk.StringVar()
        self.question_label = tk.Label(frame, textvariable=self.question, bg=COLORS["surface"], fg=COLORS["text"], font=("Segoe UI", 20, "bold"), wraplength=520, justify="left", anchor="w", padx=16, pady=16, highlightbackground=COLORS["violet"], highlightthickness=2)
        self.question_label.pack(fill="x", pady=(0, 18))

        tk.Label(frame, text="SUGGESTED ANSWER · TELEPROMPTER", bg=COLORS["bg"], fg=COLORS["amber"], font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 7))
        answer_frame = tk.Frame(frame, bg=COLORS["amber"], padx=1, pady=1)
        answer_frame.pack(fill="both", expand=True)
        self.answer = tk.Text(answer_frame, wrap="word", font=("Segoe UI", 26), height=8, state="disabled", bg=COLORS["surface"], fg=COLORS["text"], insertbackground=COLORS["text"], relief="flat", padx=16, pady=16)
        self.answer.pack(fill="both", expand=True, pady=(4, 0))

        controls = tk.Frame(frame, bg=COLORS["bg"])
        controls.pack(fill="x", pady=(12, 0))
        self.detail = tk.StringVar()
        tk.Label(controls, textvariable=self.detail, wraplength=390, justify="left", bg=COLORS["bg"], fg=COLORS["muted"], font=("Segoe UI", 9)).pack(side="left", fill="x", expand=True)
        tk.Button(controls, text="Next lines  ↑", command=request_next, bg=COLORS["violet"], activebackground=COLORS["violet_hover"], fg="white", activeforeground="white", font=("Segoe UI", 10, "bold"), relief="flat", padx=16, pady=8, cursor="hand2").pack(side="right")

        frame.bind("<Configure>", lambda e: self.question_label.configure(wraplength=max(300, e.width - 72)))
        root.protocol("WM_DELETE_WINDOW", self.close)
        self.worker = threading.Thread(target=run, args=(self.stop,), daemon=True)
        self.worker.start()
        self.previous = None
        self.poll()

    def poll(self):
        if private_path("stop_assistant").exists():
            self.close()
            return
        data = read_state()
        self.status.set(data.get("state", "NOT LISTENING") + "  " + data.get("progress", ""))
        self.question.set(data.get("question", ""))
        answer = data.get("answer", "")
        if answer != self.previous:
            self.answer.configure(state="normal")
            self.answer.delete("1.0", "end")
            self.answer.insert("1.0", answer)
            self.answer.configure(state="disabled")
            self.previous = answer
        self.detail.set(data.get("detail", "") or data.get("source", ""))
        self.root.after(250, self.poll)

    def close(self):
        self.stop.set()
        self.root.destroy()


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()
    return 0


if __name__ == "__main__":
    main()
