"""Shared live pipeline; candidate speech only advances the teleprompter.

The answer function is injectable so deterministic mock tests require no login,
recording or external service. One worker thread owns the answer provider.
"""
import json
import time
from app_paths import private_path
from question_segmenter import QuestionSegmenter
from teleprompter import Teleprompter
from runtime_state import publish, read_json


class JsonlReader:
    def __init__(self, path):
        self.path, self.offset = path, 0

    def read(self):
        try:
            with self.path.open('rb') as f:
                if self.path.stat().st_size < self.offset: self.offset = 0
                f.seek(self.offset)
                result = []
                while True:
                    line = f.readline()
                    if not line or not line.endswith(b'\n'): break
                    self.offset = f.tell()
                    try: result.append(json.loads(line.decode('utf-8-sig')))
                    except (UnicodeError, ValueError): continue
                return result
        except FileNotFoundError:
            return []


class LiveSession:
    def __init__(self, answer_fn, sink=publish):
        self.answer_fn, self.sink = answer_fn, sink
        self.segmenter = QuestionSegmenter()
        self.prompter = Teleprompter()
        self.state = dict(state='LISTENING', question='', answer='', progress='',
                          source='', detail='', generation=0)

    def emit(self):
        self.state['answer'] = self.prompter.current()
        self.state['progress'] = (f'{self.prompter.index + 1} / {len(self.prompter.chunks)}'
                                  if self.prompter.chunks else '')
        self.sink(dict(self.state))

    def ingest(self, item):
        text = str(item.get('text', '')).strip()
        if not text: return
        if item.get('speaker') == 'candidate':
            if self.state['state'] in ('ANSWER READY', 'FALLBACK ANSWER'):
                self.prompter.observe(text)
                self.emit()
            return
        if item.get('speaker') != 'interviewer': return
        segment = self.segmenter.add(text)
        if segment: self.answer(segment.text)

    def flush(self):
        segment = self.segmenter.flush_if_silent()
        if segment: self.answer(segment.text)

    def answer(self, question):
        self.prompter.set_answer('')
        self.state.update(state='GENERATING ANSWER', question=question, source='', detail='',
                          generation=self.state['generation'] + 1)
        self.emit()
        try:
            answer, source = self.answer_fn(question)
            external = source in ('ChatGPT browser', 'ChatGPT Windows', 'Claude desktop')
            fallback = 'fallback' in source.lower() or source == 'built-in fallback'
            self.state.update(source=source, state='SENT TO AI WINDOW' if external else
                              'FALLBACK ANSWER' if fallback else 'ANSWER READY')
            if external:
                self.state['detail'] = answer
            else:
                self.prompter.set_answer(answer)
        except Exception as exc:
            self.state.update(state='ANSWER ERROR', detail=str(exc))
        self.emit()

    def advance(self):
        self.prompter.advance()
        self.emit()


def run(stop_event):
    from answer_engine import generate_answer, close_answer_engine
    session = LiveSession(generate_answer)
    readers = [JsonlReader(private_path(name)) for name in
               ('live_transcript.jsonl', 'candidate_transcript.jsonl')]
    command_id = read_json(private_path('panel_next.json'), {}).get('id')
    session.emit()
    # Keep liveness visible while the provider call blocks the processing thread.
    import threading
    heartbeat_stop = threading.Event()
    def heartbeat():
        while not heartbeat_stop.wait(2): session.emit()
    heartbeat_thread = threading.Thread(target=heartbeat, daemon=True)
    heartbeat_thread.start()
    try:
        while not stop_event.wait(0.2):
            for reader in readers:
                for item in reader.read(): session.ingest(item)
            session.flush()
            command = read_json(private_path('panel_next.json'), {})
            if command.get('id') != command_id:
                command_id = command.get('id')
                if command.get('generation') == session.state['generation']: session.advance()
            session.emit()
    finally:
        heartbeat_stop.set()
        heartbeat_thread.join(timeout=3)
        close_answer_engine()
        session.state.update(state='STOPPED', question='', detail='Session stopped')
        session.prompter.set_answer('')
        session.emit()
