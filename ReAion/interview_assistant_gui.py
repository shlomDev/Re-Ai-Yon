#!/usr/bin/env python
"""Desktop view over the same live state used by the Chrome side panel."""
import threading
import tkinter as tk
from tkinter import ttk
from live_session import run
from app_paths import private_path
from runtime_state import read_state, request_next

class App:
    def __init__(self, root):
        self.root = root
        self.stop = threading.Event()
        root.title('ReAion')
        root.geometry('600x760')
        root.minsize(380, 500)
        frame = ttk.Frame(root, padding=20)
        frame.pack(fill='both', expand=True)
        self.status = tk.StringVar()
        ttk.Label(frame, textvariable=self.status).pack(anchor='w')
        self.question = tk.StringVar()
        self.question_label = ttk.Label(frame, textvariable=self.question, font=('Arial', 20, 'bold'), wraplength=540)
        self.question_label.pack(fill='x', pady=20)
        self.answer = tk.Text(frame, wrap='word', font=('Arial', 26), height=8, state='disabled')
        self.answer.pack(fill='both', expand=True)
        self.detail = tk.StringVar()
        ttk.Label(frame, textvariable=self.detail, wraplength=540).pack(fill='x', pady=12)
        ttk.Button(frame, text='Next lines', command=request_next).pack(anchor='e')
        frame.bind('<Configure>', lambda e: self.question_label.configure(wraplength=max(300, e.width - 40)))
        root.protocol('WM_DELETE_WINDOW', self.close)
        self.worker = threading.Thread(target=run, args=(self.stop,), daemon=True)
        self.worker.start()
        self.previous = None
        self.poll()

    def poll(self):
        if private_path("stop_assistant").exists():
            self.close(); return
        data = read_state()
        self.status.set(data.get('state', 'NOT LISTENING') + '  ' + data.get('progress', ''))
        self.question.set(data.get('question', ''))
        answer = data.get('answer', '')
        if answer != self.previous:
            self.answer.configure(state='normal')
            self.answer.delete('1.0', 'end')
            self.answer.insert('1.0', answer)
            self.answer.configure(state='disabled')
            self.previous = answer
        self.detail.set(data.get('detail', '') or data.get('source', ''))
        self.root.after(250, self.poll)

    def close(self):
        self.stop.set()
        self.root.destroy()

def main():
    root = tk.Tk()
    App(root)
    root.mainloop()
    return 0

if __name__ == '__main__': main()
