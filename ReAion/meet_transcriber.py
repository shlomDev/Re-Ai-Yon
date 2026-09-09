#!/usr/bin/env python
"""
Automatic interview recorder/transcriber.

Windows:
- captures default speaker output via WASAPI loopback = interviewer
- captures default microphone separately = candidate
- writes mixed.wav, interviewer.wav and microphone.wav
- live-transcribes the interviewer channel only for low-latency question detection

The watcher starts/stops this automatically.
"""

import argparse
import datetime as dt
import json
import queue
import signal
import sys
import threading
import time
import wave
from pathlib import Path

import numpy as np
import soundcard as sc
from scipy.signal import resample_poly
from faster_whisper import WhisperModel

from windows_audio import ensure_pc_sound_available

CAPTURE_RATE = 48000
WHISPER_RATE = 16000
BLOCK_SECONDS = 1
BLOCK_FRAMES = CAPTURE_RATE * BLOCK_SECONDS
BASE = Path(__file__).resolve().parent
from app_paths import private_path
LIVE_FEED = private_path("live_transcript.jsonl")
MIC_FEED = private_path("candidate_transcript.jsonl")


def mono(x):
    x = np.asarray(x, dtype=np.float32)
    if x.ndim == 1:
        return x
    return np.mean(x, axis=1).astype(np.float32)


def pad_to(a, n):
    if len(a) < n:
        a = np.pad(a, (0, n - len(a)))
    return a


def mix(a, b):
    n = max(len(a), len(b))
    a, b = pad_to(a, n), pad_to(b, n)
    y = 0.5 * a + 0.5 * b
    pk = float(np.max(np.abs(y))) if len(y) else 0.0
    if pk > 0.98:
        y *= 0.98 / pk
    return y.astype(np.float32)


def to_pcm16(x):
    return (np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes()


class CaptureThread(threading.Thread):
    def __init__(self, source, out_queue, stop_event, name):
        super().__init__(daemon=True)
        self.source = source
        self.out_queue = out_queue
        self.stop_event = stop_event
        self.name = name
        self.error = None

    def run(self):
        try:
            with self.source.recorder(samplerate=CAPTURE_RATE) as rec:
                while not self.stop_event.is_set():
                    data = mono(rec.record(numframes=BLOCK_FRAMES))
                    try:
                        self.out_queue.put(data, timeout=2)
                    except queue.Full:
                        raise RuntimeError("Audio capture queue overflow; processing cannot keep up")
        except Exception as e:
            self.error = e
            self.stop_event.set()


class InterviewerTranscriber(threading.Thread):
    def __init__(self, model, audio_queue, transcript_path, stop_event, language, speaker="interviewer", model_lock=None):
        super().__init__(daemon=True)
        self.model = model
        self.audio_queue = audio_queue
        self.transcript_path = transcript_path
        self.stop_event = stop_event
        self.language = language
        self.speaker = speaker
        self.model_lock = model_lock or threading.Lock()
        self.error = None

    def run(self):
        try:
            with self.transcript_path.open("a", encoding="utf-8", buffering=1) as f:
                while True:
                    try:
                        item = self.audio_queue.get(timeout=0.5)
                    except queue.Empty:
                        if self.stop_event.is_set() and self.audio_queue.empty():
                            break
                        continue

                    if item is None:
                        break

                    start_sec, audio = item
                    if len(audio) == 0:
                        continue

                    with self.model_lock:
                        segments, _ = self.model.transcribe(
                            audio, language=self.language, beam_size=2,
                            vad_filter=True, condition_on_previous_text=False)
                        segments = list(segments)

                    for seg in segments:
                        text = seg.text.strip()
                        if not text:
                            continue

                        absolute = start_sec + float(seg.start)
                        stamp = str(dt.timedelta(seconds=int(absolute)))
                        line = f"[{stamp}] {self.speaker.upper()}: {text}"
                        print(line, flush=True)
                        f.write(line + "\n")

                        try:
                            with (LIVE_FEED if self.speaker == "interviewer" else MIC_FEED).open("a", encoding="utf-8") as lf:
                                lf.write(json.dumps({
                                    "stamp": stamp,
                                    "speaker": self.speaker,
                                    "text": text,
                                    "ts": time.time()
                                }, ensure_ascii=False) + "\n")
                        except Exception:
                            pass
        except Exception as e:
            self.error = e
            self.stop_event.set()


def choose_devices():
    speaker = sc.default_speaker()
    mic = sc.default_microphone()

    if speaker is None:
        raise RuntimeError("No default Windows speaker/output device found.")
    if mic is None:
        raise RuntimeError("No default microphone found.")

    loopback = sc.get_microphone(str(speaker.name), include_loopback=True)
    if loopback is None:
        raise RuntimeError("Could not open WASAPI loopback for the default output.")

    return speaker, loopback, mic


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="large-v3-turbo")
    ap.add_argument("--language", default="auto", help="language code (he, en, ...), or auto")
    ap.add_argument("--chunk-seconds", type=int, default=5)
    ap.add_argument("--output", default=str(private_path("recordings")))
    ap.add_argument("--stop-file", default="")
    ap.add_argument("--record-only", action="store_true")
    args = ap.parse_args()

    if args.language.lower() == "auto":
        args.language = None

    stop_file = Path(args.stop_file).resolve() if args.stop_file else None
    if stop_file and stop_file.exists():
        stop_file.unlink()

    try:
        LIVE_FEED.write_text("", encoding="utf-8")
        MIC_FEED.write_text("", encoding="utf-8")
    except Exception:
        pass

    stamp = dt.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    out_dir = Path(args.output) / stamp
    out_dir.mkdir(parents=True, exist_ok=True)

    mixed_path = out_dir / "mixed.wav"
    interviewer_path = out_dir / "interviewer.wav"
    microphone_path = out_dir / "microphone.wav"
    transcript_path = out_dir / "interviewer_transcript.txt"

    stop_event = threading.Event()

    def request_stop(*_):
        stop_event.set()

    signal.signal(signal.SIGINT, request_stop)
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, request_stop)

    try:
        state = ensure_pc_sound_available()
        if state.get("supported"):
            new_pct = round((state.get("new_volume") or 0) * 100)
            print(f"Windows sound : ready, unmuted at {new_pct}%")
    except Exception as e:
        print(f"[warning] Windows master-sound check failed: {e}", file=sys.stderr)

    speaker, loopback, mic = choose_devices()

    print("INTERVIEW ASSISTANT STARTED")
    print(f"Output       : {out_dir.resolve()}")
    print(f"Interviewer  : {speaker.name} (WASAPI loopback)")
    print(f"Microphone   : {mic.name}")

    tx_queue = queue.Queue(maxsize=12)
    tx_thread = None

    if not args.record_only:
        print(f"Whisper      : {args.model}")
        model = WhisperModel(args.model, device="cpu", compute_type="int8")
        model_lock = threading.Lock()
        tx_thread = InterviewerTranscriber(
            model, tx_queue, transcript_path, stop_event, args.language, model_lock=model_lock
        )
        tx_thread.start()

    speaker_q = queue.Queue(maxsize=8)
    mic_q = queue.Queue(maxsize=8)
    mic_tx_q = queue.Queue(maxsize=4)
    mic_tx_thread = None
    if not args.record_only:
        mic_tx_thread = InterviewerTranscriber(model, mic_tx_q, out_dir / 'candidate_transcript.txt',
                                             stop_event, args.language, 'candidate', model_lock)
        mic_tx_thread.start()
    mic_buffer = []
    mic_samples = 0

    speaker_thread = CaptureThread(loopback, speaker_q, stop_event, "interviewer")
    mic_thread = CaptureThread(mic, mic_q, stop_event, "candidate")
    speaker_thread.start()
    mic_thread.start()

    whisper_buffer = []
    buffer_samples = 0
    chunk_samples = args.chunk_seconds * WHISPER_RATE
    chunk_start_sec = 0.0

    with wave.open(str(mixed_path), "wb") as mixed_wf, \
         wave.open(str(interviewer_path), "wb") as int_wf, \
         wave.open(str(microphone_path), "wb") as mic_wf:

        for wf in (mixed_wf, int_wf, mic_wf):
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(CAPTURE_RATE)

        while not stop_event.is_set():
            if stop_file and stop_file.exists():
                print("\nCall ended. Finalizing...")
                stop_event.set()
                break

            try:
                spk = speaker_q.get(timeout=1.5)
                mic_audio = mic_q.get(timeout=1.5)
            except queue.Empty:
                continue

            n = max(len(spk), len(mic_audio))
            spk = pad_to(spk, n)
            mic_audio = pad_to(mic_audio, n)
            combined = mix(spk, mic_audio)

            int_wf.writeframes(to_pcm16(spk))
            mic_wf.writeframes(to_pcm16(mic_audio))
            mixed_wf.writeframes(to_pcm16(combined))

            if not args.record_only:
                # LIVE transcription uses only PC output. That means the candidate's
                # microphone speech cannot trigger the suggested-answer engine.
                down = resample_poly(spk, 1, 3).astype(np.float32)
                whisper_buffer.append(down)
                buffer_samples += len(down)

                if buffer_samples >= chunk_samples:
                    audio_chunk = np.concatenate(whisper_buffer)
                    try:
                        tx_queue.put((chunk_start_sec, audio_chunk), timeout=1)
                    except queue.Full:
                        print("[warning] live Whisper is behind; recordings remain complete.")
                    chunk_start_sec += len(audio_chunk) / WHISPER_RATE
                    whisper_buffer = []
                    buffer_samples = 0

            # Separate channel and background worker: never transcribe in the capture loop.
            if not args.record_only:
                down_mic = resample_poly(mic_audio, 1, 3).astype(np.float32)
                mic_buffer.append(down_mic)
                mic_samples += len(down_mic)
                if mic_samples >= chunk_samples:
                    try: mic_tx_q.put_nowait((0, np.concatenate(mic_buffer)))
                    except queue.Full:
                        print('[warning] Candidate speech skipped: teleprompter processing is behind.', file=sys.stderr)
                    mic_buffer, mic_samples = [], 0

    if not args.record_only and whisper_buffer:
        try:
            tx_queue.put((chunk_start_sec, np.concatenate(whisper_buffer)), timeout=2)
        except queue.Full:
            pass

    if not args.record_only:
        try:
            tx_queue.put(None, timeout=2)
        except queue.Full:
            pass
        tx_thread.join(timeout=20)
        try: mic_tx_q.put(None, timeout=1)
        except queue.Full: pass
        mic_tx_thread.join(timeout=5)

    speaker_thread.join(timeout=3)
    mic_thread.join(timeout=3)

    if stop_file and stop_file.exists():
        try:
            stop_file.unlink()
        except OSError:
            pass

    for worker in (speaker_thread, mic_thread, tx_thread, mic_tx_thread):
        if worker is not None and worker.error:
            raise RuntimeError(f'{worker.name}: {worker.error}')
    print("\nSaved:")
    print(f"  Mixed audio       : {mixed_path.resolve()}")
    print(f"  Interviewer audio : {interviewer_path.resolve()}")
    print(f"  Microphone audio  : {microphone_path.resolve()}")
    if not args.record_only:
        print(f"  Live transcript   : {transcript_path.resolve()}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
