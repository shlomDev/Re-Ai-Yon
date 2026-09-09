# Target Architecture

## Principle

Separate **meeting detection** from the provider-independent processing pipeline.

```text
Calendar / Email Discovery
          |
          v
 Interview Registry / Scheduler
          |
          v
 Meeting Provider Adapter  <---- Google Meet / Teams / Zoom / Chime / Webex / Generic
          |
          v
 Windows Audio Capture
   |                 |
   |                 +---- Candidate microphone (recording/diagnostics only)
   |
   +---- Interviewer PC output
                |
                v
        Streaming Transcription
                |
                v
        Question Segmentation
                |
                v
        Answer Orchestration
                |
                v
       ChatGPT Windows App
                |
                v
        Large Answer Pane
```

## Suggested package direction

Do not move working prototype files until tests are in place. When refactoring, target something similar to:

```text
src/interview_copilot/
  app.py
  config.py
  registry.py

  discovery/
    calendar.py
    email.py
    classifier.py

  meetings/
    base.py
    google_meet.py
    teams.py
    zoom.py
    chime.py
    webex.py
    generic.py

  audio/
    windows_output.py
    microphone.py
    mixer.py

  transcription/
    engine.py
    segments.py

  questions/
    detector.py
    segmenter.py

  answers/
    base.py
    chatgpt_windows.py
    fallback.py

  ui/
    layout.py
    status.py

  scheduling/
    preflight.py
    watcher.py
```

## Provider adapter contract

Provider adapters should expose only provider-specific capabilities, for example:

```python
class MeetingAdapter(Protocol):
    def matches(self, context) -> bool: ...
    def is_call_active(self) -> bool: ...
    def meeting_id(self) -> str | None: ...
    def ensure_microphone_on(self) -> bool: ...
    def camera_state(self) -> str: ...
```

Audio capture must not depend on this interface.

## ChatGPT Windows backend

Goal: use the official ChatGPT Windows app that is already signed in to the user's Plus account.

Preferred implementation order:

1. Windows UI Automation / Accessibility tree
2. documented application shortcuts and standard window messages where reliable
3. keyboard/mouse automation only as a narrowly scoped fallback

Requirements:

- dedicated interview chat/session
- automatically focus ChatGPT input when a completed interviewer question is available
- paste/type a compact structured prompt
- submit automatically
- return focus/layout to side-by-side state if necessary
- keep ChatGPT response visible
- no cookie/token harvesting
- no reverse engineering of private network APIs

Do not make answer extraction from the ChatGPT UI a prerequisite. The ChatGPT window itself may be the answer pane.

## Question segmentation

Do not fire on every Whisper fragment.

Use a short rolling buffer and detect end-of-question using a combination of:

- question words / interrogative structure
- punctuation when available
- silence / end-of-utterance timing
- semantic continuation detection
- duplicate suppression

Goal: submit one coherent question rather than multiple partial fragments.

## UI

Default interview mode:

- meeting application left
- ChatGPT right
- no overlay
- transcript process hidden/background
- optional compact status strip only

Status items can include:

- interview armed
- PC audio active
- mic active
- question detector active
- ChatGPT ready

## Failure behavior

Never interrupt the call because the copilot failed.

If transcription/answer generation fails:

- keep meeting untouched
- show a compact warning
- continue recording only if recording mode is enabled
- retry components independently
