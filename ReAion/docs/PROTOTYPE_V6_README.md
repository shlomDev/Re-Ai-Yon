> Development notes. Current verified status and blockers are in PROJECT_STATE.md.

# Interview Auto Transcriber v6 — Fully Automatic Live Answers

This build is designed for the interview workflow requested:

**Interviewer speaks -> PC audio capture -> Whisper -> question detection ->
local AI -> suggested answer appears automatically.**

There is no Ask button and no click is required during the call.

## Important architecture improvement

The interviewer and candidate are no longer treated as one mixed transcription stream.

The program records:

- `interviewer.wav` — Windows/Meet output
- `microphone.wav` — your microphone
- `mixed.wav` — both together

Only `interviewer.wav` is used for **live question detection**.

This prevents your own answers from being mistaken for new interviewer questions.

## Live answer latency

The interviewer stream is sent to Whisper in approximately 5-second chunks.

When a question is recognized, the answer engine runs automatically and replaces
the Suggested Answer pane as soon as the response is ready.

Actual latency depends on CPU/GPU performance.

## Local AI

v6 uses a local Ollama model by default:

`qwen2.5:3b-instruct`

Run once:

`setup_local_ai.bat`

or use the complete installer:

`setup_everything.bat`

The setup downloads the local model before interview day, so the interview does
not depend on a model download.

No Codex installation and no OpenAI API key are required.

If local AI is unavailable, the built-in answer bank still produces an answer,
but the scheduled self-test reports the missing local AI as a failure so it can
be fixed before the real interview.

## Candidate knowledge

`candidate_profile.md` contains the interview-specific professional context used
by the local model.

It includes infrastructure, Linux/Windows, BMC/IPMI/Redfish, firmware, networking,
Python/Bash automation, Kubernetes/KubeVirt, and concrete troubleshooting examples.

The prompt explicitly tells the model not to invent experience.

## One-time setup

Run:

`setup_everything.bat`

Then in Chrome:

1. Open `chrome://extensions`
2. Enable Developer mode
3. Remove/reload the previous Interview Auto Transcriber extension
4. Click **Load unpacked**
5. Select the included `chrome_extension` folder

## Test right now

Run:

`run_full_test.bat`

It tests:

- Windows sound is unmuted
- speaker output / loopback capture
- microphone
- Whisper
- Chrome watcher/extension
- local AI availability
- automatic question -> answer behavior

You can test only the no-click answer path with:

`test_live_answers.bat`

The demo feeds several sample interviewer questions into the exact live-answer
GUI. The answers should appear automatically.

## Interview behavior

When the configured Meet call is active:

1. Windows PC output is made audible if muted.
2. Meet microphone is automatically unmuted by the Chrome helper.
3. Camera remains user-controlled and asks before enabling.
4. Recorder starts automatically.
5. The Interview Live Assistant window opens automatically.
6. Interviewer speech is transcribed live.
7. Questions are detected automatically.
8. Suggested answers are generated automatically.
9. Leaving the configured meeting stops/finalizes the recording.

## Pre-interview tests

The existing schedule remains:

- 24 hours before the interview
- 30 minutes before the interview

The self-test now also verifies that the local AI model can produce a real
interview answer.

## ChatGPT account

This automatic path intentionally does not scrape or automate the signed-in
ChatGPT web session. Instead, the relevant professional context is stored in
`candidate_profile.md` and supplied directly to the local model for every answer.

That keeps the interview path automatic and independent of browser session/authentication.

## Next step

The next project step is automatic interview discovery:

Calendar/Gmail -> detect recruiter/interview event -> extract Meet/Teams/Zoom URL ->
create interview config -> schedule tests -> arm the correct call automatically.
