# ReAion project state — 0.2.0 development milestone (2026-09-09)

## Verified now
- 40 Python unit/regression tests pass in Linux/Python 3.12.
- Deterministic mock_interview.py uses the real segmentation, session controller,
  teleprompter, atomic state writer and HTTP panel endpoint. Synthetic Q&A only.
- Node runtime fixture verifies selected active-call microphone handling; pre-join
  and unselected calls are untouched. All extension scripts pass syntax checks.
- Python sources compile. Missing selected ChatGPT provider returns health failure
  and nonzero exit, even when fallback text is available.
- BOM-aware config reads; private profile no longer falls back to shared source files.

## Changes in this milestone
- Shared LiveSession pipeline used by desktop view and Chrome side panel.
- Each complete transcript line is consumed once; partial lines are retained.
- Candidate speech advances chunks and cannot enter question detection.
- Actual question/answer/state/Next lines wired to browser panel. Empty/error states
  clear previous answers. External AI submission is labeled SENT TO AI WINDOW.
- Chrome panel can select the current HTTPS meeting without editing interviews.json.
  Detection scripts cover Meet, Teams, Zoom, Webex and Chime hosts; selected generic
  tabs can receive the same conservative leave-control detector via activeTab.
- One initial microphone enable after a selected active-call signal; later manual
  muting is respected. Camera requires the in-page prompt; Join is never clicked.
- Unsafe title-only desktop auto-start disabled. Generic Chrome process no longer
  wins over a Teams URL. Manual Stop pauses automatic heartbeat starts.
- Experimental ChatGPT browser client reused on its owning worker thread; checks
  destination, protects drafts, checks sent-message acknowledgement and never
  blindly retries an uncertain send. No private APIs, cookies or response scraping.
- Candidate transcription moved out of capture loop into a bounded worker queue;
  model calls serialize. Model performance and hardware behavior unverified.
- Runtime feeds/reports/recordings use per-user paths. Recordings still remain local
  by default; a retention UI and opt-in recording policy are outstanding.
- Windows-only dependency markers and frozen worker dispatch corrected. Spec now
  produces the onedir layout expected by the Windows installer.

## Architecture decisions
Browser interviews are the primary experience. Chrome side panel + local companion
share a provider-independent session controller. This is NOT a browser-only app:
Whisper and system loopback still run locally. Native desktop view uses the same
controller. UI automation is experimental and is not a supported ChatGPT API.
ChatGPT replies stay in its own visible window. API/Ollama/fallback responses can
be displayed in the custom teleprompter. No claim to load all account history.

## Known problems / release blockers
- No end-to-end live audio or signed-in ChatGPT test passed. Cloud Meet pre-join
  reported microphone and speaker missing. Cloud browser also refused localhost
  preview with ERR_BLOCKED_BY_CLIENT; HTTP tests ran directly instead.
- Extension host/control fixtures do not prove current real provider DOM support.
  Labels/localization/SPA URL changes may require adaptation. Generic detection
  requires an identifiable leave-call control.
- System-wide loopback is still used; selected-tab capture is not implemented.
  Unrelated playback/echo can contaminate interviewer audio. Use headphones.
- Question segmentation remains heuristic; sentence punctuation can split a long
  prompt, and small talk can produce an answer. No semantic accuracy claim.
- No tested Windows EXE, macOS app or Linux installer is included. Browser binaries,
  Whisper downloads, clean-machine setup and packaging need release engineering.
- ChatGPT sign-in still needs user action in the dedicated browser profile. The
  health CLI cannot verify another process's live composer; no false readiness.
- Stop/recovery/device hot-plug and cross-platform audio need native testing.
- Full preflight, OAuth discovery, recording retention and multi-user onboarding
  remain incomplete. Existing older scripts are development tools.

## Exact next step
On a Windows test PC, build/run the development source, connect the dedicated
ChatGPT profile, load the extension, select a private Meet room, and join from a
second device using headphones. Verify one interviewer question produces exactly
one submitted prompt, candidate speech produces none, Stop stops capture, and
leave-call restores layout. Record hardware/model latency and failure evidence.
Do not publish a stable release until this gate passes. Repeat on Linux/macOS
before advertising those platforms as supported.

## Branding update

Project and tool renamed to ReAion (reh-ah-yon; ראיון). UI, extension, launchers,
workspace and executable build names use ReAion. Legacy per-user data paths,
environment variables and installer AppId remain compatible.
