#!/usr/bin/env python
import argparse
import datetime as dt
import json
import math
import os
import sys
import threading
import time
import urllib.request
from pathlib import Path

import numpy as np
import soundcard as sc
from scipy.signal import resample_poly
from faster_whisper import WhisperModel
from windows_audio import ensure_pc_sound_available

RATE = 48000
WHISPER_RATE = 16000
BASE = Path(__file__).resolve().parent
from app_paths import private_path
STATUS_FILE = private_path("last_self_test.json")


def rms(x):
    x = np.asarray(x, dtype=np.float32)
    if x.size == 0:
        return 0.0
    return float(np.sqrt(np.mean(np.square(x))))


def peak(x):
    x = np.asarray(x, dtype=np.float32)
    return float(np.max(np.abs(x))) if x.size else 0.0


def mono(x):
    x = np.asarray(x, dtype=np.float32)
    if x.ndim == 1:
        return x
    return np.mean(x, axis=1).astype(np.float32)


def report_line(lines, name, ok, detail):
    status = "PASS" if ok is True else ("WARN" if ok is None else "FAIL")
    line = f"{status:4}  {name}: {detail}"
    print(line, flush=True)
    lines.append(line)


def get_watcher_status():
    try:
        with urllib.request.urlopen("http://127.0.0.1:8765/status", timeout=2) as r:
            return json.loads(r.read().decode("utf-8"))
    except Exception:
        return None


def wait_for_enter(timeout=120):
    """Windows-friendly timeout. Enter starts the microphone speech test."""
    print()
    print("MICROPHONE TEST")
    print("Press ENTER, then say clearly:")
    print('  "Google interview microphone test. My microphone is working."')
    print(f"You have {timeout} seconds to start. If you are away, this part will be skipped.")
    print()

    if os.name != "nt":
        try:
            input()
            return True
        except EOFError:
            return False

    import msvcrt
    start = time.time()
    while time.time() - start < timeout:
        if msvcrt.kbhit():
            ch = msvcrt.getwch()
            if ch in ("\r", "\n"):
                return True
        time.sleep(0.1)
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--label", default="manual")
    ap.add_argument("--model", default="large-v3-turbo")
    ap.add_argument("--voice-wait-seconds", type=int, default=120)
    ap.add_argument("--no-pause", action="store_true")
    args = ap.parse_args()

    started = dt.datetime.now().astimezone()
    stamp = started.strftime("%Y-%m-%d_%H-%M-%S")
    report_dir = private_path("test_reports") / stamp
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / "report.txt"
    lines = []

    print("=" * 66)
    print("GOOGLE INTERVIEW TRANSCRIBER - FULL SELF TEST")
    print(f"Test: {args.label}")
    print(f"Time: {started.isoformat()}")
    print("=" * 66)
    print()

    failures = 0

    # Windows master playback safety.
    try:
        sound_state = ensure_pc_sound_available()
        if sound_state.get("supported"):
            old_pct = round((sound_state.get("old_volume") or 0) * 100)
            new_pct = round((sound_state.get("new_volume") or 0) * 100)
            ok = not sound_state.get("is_muted") and new_pct >= 20
            detail = f"unmuted, volume={new_pct}%"
            if sound_state.get("was_muted"):
                detail += " (auto-unmuted)"
            elif old_pct < 20:
                detail += f" (raised from {old_pct}%)"
            report_line(lines, "Windows master sound", ok, detail)
            if not ok:
                failures += 1
        else:
            report_line(lines, "Windows master sound", None, "non-Windows: skipped")
    except Exception as e:
        report_line(lines, "Windows master sound", False, str(e))
        failures += 1

    # Watcher / Chrome extension health.
    status = get_watcher_status()
    if status:
        report_line(lines, "Local watcher", True, "running on 127.0.0.1:8765")
        ext_age = status.get("extension_health_age_seconds")
        if ext_age is None:
            report_line(
                lines, "Chrome extension", None,
                "not seen yet; open Chrome after loading the extension"
            )
        elif ext_age <= 180:
            report_line(lines, "Chrome extension", True, f"health ping {ext_age:.0f}s ago")
        else:
            report_line(
                lines, "Chrome extension", None,
                f"last health ping {ext_age:.0f}s ago; open/restart Chrome"
            )
    else:
        report_line(
            lines, "Local watcher", False,
            "not reachable. Run start_auto_watcher.bat / enable watcher at login."
        )
        report_line(lines, "Chrome extension", None, "cannot check without watcher")
        failures += 1

    # Devices.
    try:
        speaker = sc.default_speaker()
        mic = sc.default_microphone()
        if speaker is None:
            raise RuntimeError("no default speaker")
        if mic is None:
            raise RuntimeError("no default microphone")
        loopback = sc.get_microphone(str(speaker.name), include_loopback=True)
        if loopback is None:
            raise RuntimeError("could not open speaker loopback")
        report_line(lines, "Default speaker", True, speaker.name)
        report_line(lines, "Default microphone", True, mic.name)
        report_line(lines, "WASAPI loopback", True, loopback.name)
    except Exception as e:
        report_line(lines, "Audio devices", False, str(e))
        failures += 1
        report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        STATUS_FILE.write_text(json.dumps({
            "time": started.isoformat(), "label": args.label,
            "result": "FAIL", "report": str(report_path)
        }, indent=2), encoding="utf-8")
        if not args.no_pause:
            input("\nPress ENTER to close...")
        return 2

    # Speaker-loopback test: play a known tone and capture it from loopback.
    print()
    print("Testing system audio / speaker loopback...")
    tone_seconds = 1.5
    t = np.arange(int(RATE * tone_seconds), dtype=np.float32) / RATE
    tone = (0.12 * np.sin(2 * np.pi * 880.0 * t)).astype(np.float32)

    def play_tone():
        time.sleep(0.35)
        try:
            speaker.play(tone, samplerate=RATE)
        except Exception as exc:
            print(f"Tone playback error: {exc}", file=sys.stderr)

    try:
        th = threading.Thread(target=play_tone, daemon=True)
        th.start()
        with loopback.recorder(samplerate=RATE) as rec:
            captured = mono(rec.record(numframes=int(RATE * 2.5)))
        th.join(timeout=3)
        lrms, lpeak = rms(captured), peak(captured)
        loop_ok = lpeak >= 0.01 or lrms >= 0.002
        report_line(
            lines, "System-audio capture", loop_ok,
            f"RMS={lrms:.5f}, peak={lpeak:.5f}"
        )
        if not loop_ok:
            failures += 1
    except Exception as e:
        report_line(lines, "System-audio capture", False, str(e))
        failures += 1

    # Load the exact Whisper model used by the interview transcriber.
    print()
    print(f"Loading Whisper model '{args.model}'...")
    try:
        model = WhisperModel(args.model, device="cpu", compute_type="int8")
        report_line(lines, "Whisper model", True, f"{args.model} loaded")
    except Exception as e:
        model = None
        report_line(lines, "Whisper model", False, str(e))
        failures += 1

    # Interactive microphone + speech transcription test.
    do_voice = wait_for_enter(args.voice_wait_seconds)
    if not do_voice:
        report_line(lines, "Microphone speech test", None, "skipped - user did not start test")
    else:
        print("Recording microphone for 8 seconds... SPEAK NOW.")
        try:
            with mic.recorder(samplerate=RATE) as rec:
                mic_audio = mono(rec.record(numframes=RATE * 8))
            mrms, mpeak = rms(mic_audio), peak(mic_audio)
            mic_ok = mpeak >= 0.01 or mrms >= 0.002
            report_line(
                lines, "Microphone capture", mic_ok,
                f"RMS={mrms:.5f}, peak={mpeak:.5f}"
            )
            if not mic_ok:
                failures += 1

            if model is not None and mic_ok:
                down = resample_poly(mic_audio, 1, 3).astype(np.float32)
                segments, _ = model.transcribe(
                    down,
                    language="en",
                    beam_size=3,
                    vad_filter=True,
                    condition_on_previous_text=False,
                )
                text = " ".join(seg.text.strip() for seg in segments if seg.text.strip()).strip()
                (report_dir / "microphone_transcript.txt").write_text(text + "\n", encoding="utf-8")
                transcript_ok = len(text) >= 5
                report_line(
                    lines, "Speech transcription", transcript_ok,
                    text if text else "no speech recognized"
                )
                if not transcript_ok:
                    failures += 1
        except Exception as e:
            report_line(lines, "Microphone speech test", False, str(e))
            failures += 1

    # Live answer-engine check.
    try:
        from answer_engine import ai_status, generate_answer
        st = ai_status()
        provider = st.get("provider", "unknown")
        if not st.get("ready", st.get("running", False)):
            report_line(
                lines, "AI answer backend", False,
                f"{provider} unavailable: {st.get('detail', 'not ready')}"
            )
            failures += 1
        else:
            answer, source = generate_answer(
                "How would you troubleshoot a server that lost network connectivity?"
            )
            ok = len(answer) >= 25 and "fallback" not in source
            report_line(
                lines, "AI answer backend", ok,
                f"{source}; request path completed"
            )
            if not ok:
                failures += 1
    except Exception as e:
        report_line(lines, "AI answer backend", False, str(e))
        failures += 1

    result = "PASS" if failures == 0 else "FAIL"
    print()
    print("=" * 66)
    print(f"FINAL RESULT: {result}")
    print("=" * 66)

    lines.append("")
    lines.append(f"FINAL RESULT: {result}")
    lines.append(f"Report folder: {report_dir}")
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    STATUS_FILE.write_text(json.dumps({
        "time": started.isoformat(),
        "label": args.label,
        "result": result,
        "report": str(report_path)
    }, indent=2), encoding="utf-8")

    print(f"Report: {report_path}")
    if result == "FAIL":
        print("Send me this report before the interview so we can fix the failing item.")
    else:
        print("Core recording/transcription path is ready.")

    if not args.no_pause:
        try:
            input("\nPress ENTER to close...")
        except EOFError:
            pass
    return 0 if result == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
