# ReAion

**ReAion** (pronounced *reh-ah-yon*) means **interview** — ראיון — in Hebrew.

ReAion is a browser-first live interview assistant. It listens to the
interviewer, detects completed questions, generates a suggested answer, and
shows it beside the meeting in a large, readable teleprompter.

![Illustrative ReAion browser layout with the meeting on the left and the assistant on the right](ReAion_demo_fluent.gif)

*Illustrative mockup with simulated content. ReAion is currently development
source, not a verified live-interview release or one-click installer.*

## What the tool does

- Keeps the browser meeting visible while the assistant occupies the side panel.
- Detects supported meeting links automatically and offers **Open meeting in ReAion** from Chrome's context menu; no URL textbox is required.
- Shows the detected question and suggested answer in large text.
- Breaks long answers into short teleprompter chunks and follows the candidate's
  speech; candidate microphone audio cannot trigger a new answer.
- Keeps the app open after the interview and shows a summary of questions,
  weak-answer review flags, STAR opportunities and confidence, with report,
  PDF-print and practice actions.
- Transcribes locally with Whisper and supports multilingual text, including
  right-to-left Hebrew.
- Targets Meet, Teams, Zoom, Webex, Chime and a generic browser fallback through
  provider adapters.
- Supports API-based answer engines and Ollama in the panel. Experimental
  ChatGPT/Claude UI automation leaves replies in their own visible AI window.
- Keeps personal profiles, transcripts and recordings out of the repository.

The Chrome panel, shared session pipeline and deterministic mock are implemented
and covered by automated tests. Real meeting audio, AI accounts, cross-platform
capture and packaged installers still require live validation. See
[PROJECT_STATE.md](ReAion/PROJECT_STATE.md) for verified status.

## Repository guide

| Location | Purpose |
| --- | --- |
| [`ReAion/`](ReAion/) | Current application source and developer instructions |
| [`ReAion/chrome_extension/`](ReAion/chrome_extension/) | Browser meeting controls and answer panel |
| [`ReAion/live_session.py`](ReAion/live_session.py) | Provider-independent live session pipeline |
| [`ReAion/answer_providers.py`](ReAion/answer_providers.py) | AI provider adapters |
| [`ReAion/tests/`](ReAion/tests/) | Automated component and regression tests |
| [`ReAion/PROJECT_STATE.md`](ReAion/PROJECT_STATE.md) | What works, limitations and the next step |
