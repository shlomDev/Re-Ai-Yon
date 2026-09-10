# ReAion

**ReAion** — pronounced **reh-ah-yon**; Hebrew: **ראיון** (interview).

**0.2.0 development source — not a verified live-interview release or an installer.**
Browser interviews are primary. A Chrome side panel works with a local companion;
the optional desktop view uses the same live session logic.

## Product overview and example

See the [detailed repository overview](../README.md) for the workflow, answer-engine comparison, language support, platform status and privacy behavior.

![Illustrative ReAion browser layout](docs/images/answer-panel-example.png)

AI-generated layout mockup with simulated content, not an actual screenshot or proof of live integration. ChatGPT replies stay in its own window; the pictured custom-panel answer applies to engines that return text. Run the mock below to see the actual implemented panel.

## Test the mock first (no AI account or audio devices)

```
python mock_interview.py
python mock_interview.py --serve
```

The first command checks synthetic question -> fixture answer -> HTTP panel ->
spoken progress. The second opens the actual panel at http://127.0.0.1:8765.
Its simulated answer is clearly labeled. Use Next lines to advance. Close with
Ctrl+C. Stop any existing watcher first because both use port 8765.
This is a text pipeline test, not a live audio or AI test.

## Developer setup and real Meet test

The existing install/launch scripts remain developer tooling. This archive does
not satisfy the one-click installer goal yet. Do not run .bat files with Python.
On Windows, run install.bat directly; install Playwright Chromium in the same
Python environment if not already installed. The build script prepares its own
build environment, which is separate from your runtime environment.

1. Run the watcher using start_auto_watcher.bat (Windows), or the existing shell
   launcher on Linux/macOS. Those operating systems have not passed audio tests.
2. In chrome://extensions enable Developer mode, Load unpacked, and select the
   chrome_extension folder. This is a development-only distribution method.
3. Open your private Meet link in Chrome. Open the ReAion extension
   panel and click **Use current meeting**. No interviews.json editing is required.
4. Join normally. The app never clicks Join. Once visible leave-call controls are
   detected, the selected session starts local capture. Camera needs approval.
5. A second device/participant asks a non-personal technical mock question. Use
   headphones. Candidate microphone speech should advance only the teleprompter.
6. Click Stop listening or leave the call. Confirm capture stops. Inspect errors
   in the terminal. Do not use the build for an interview until these checks pass.

ChatGPT browser integration is experimental UI automation. Sign in yourself in
its dedicated browser window; no credentials are extracted. A question is marked
sent only after a user-message acknowledgement. The real reply stays in ChatGPT's
window; it is not mirrored into our panel. API/Ollama engines can return text to
our custom panel, but require their own configuration and live testing. Signing
in does not give this tool access to all your chats or resume.

## Verification

```
python -m unittest discover -s tests -v
python -m compileall -q .
node tests/test_extension_runtime.cjs
python health_check.py
```

Health exits 1 if the selected AI provider is not ready. Built-in fallback does
not turn failure into PASS. The current container correctly fails ChatGPT health
because Playwright is absent. See PROJECT_STATE.md for all observed evidence and
remaining limitations. VS Code includes mock, unit-test and launch tasks.

## Privacy

Personal profiles, answer banks and interviews are loaded only from the per-user
data directory (or INTERVIEWCOPILOT_DATA_DIR override), never from shared source.
Use setup_private_profile.py to create blank templates there. No personal data is
included in this source archive. Runtime transcripts, reports and recordings stay
local in the per-user directory. Recording is still enabled by default; delete
local test recordings when no longer needed. Do not commit runtime data.

## Platforms and packaging

Windows integration and cross-platform core code exist. Linux/macOS capture and
permissions remain experimental. ReAion.spec and launcher.py address
worker dispatch and onedir layout; the Windows installer has NOT been built or
tested in this environment. No EXE/DMG/AppImage is supplied or claimed working.

## Upgrade compatibility

Existing private data stays in the InterviewCopilot per-user directory. The
INTERVIEWCOPILOT_DATA_DIR environment override and installer AppId are preserved
to avoid orphaning profiles or creating a second installation identity.

## Repository layout

The repository contains this current ReAion source directory and a root overview.
Old ZIP distributions and obsolete prototype files were removed; use Git history
for historical versions. Current Windows build recipes remain development-only.
