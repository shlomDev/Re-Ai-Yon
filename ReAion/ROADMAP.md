# Roadmap

## Completed in 0.2.0 (development)
- [x] BOM configuration regression and truthful selected-provider health.
- [x] Real shared session state for panel and desktop UI.
- [x] Incremental mic feed, channel separation and bounded answer chunks.
- [x] Current-meeting selection without schedule file editing.
- [x] Browser lifecycle safeguards and explicit external answer display status.
- [x] Deterministic pipeline and HTTP regression tests.

## Required before live pilot
- [ ] Real Meet + microphone + system audio + Whisper + ChatGPT repeated-question test.
- [ ] Authenticate before starting the interview; actionable readiness UI.
- [ ] Selected-tab capture with explicit Chrome permission, independent mic channel.
- [ ] Real DOM tests on Teams/Zoom/Webex/Chime and Hebrew interfaces.
- [ ] Silence/VAD-based speech turns with accuracy and latency measurements.
- [ ] Crash recovery, device changes, busy AI and disconnect tests.
- [ ] Complete preflight and local recording consent/retention controls.

## Required before public release
- [ ] Build, sign and test Windows installer on a clean VM.
- [ ] Build and test Linux package and macOS signed/notarized application.
- [ ] Secure extension distribution and companion installation/onboarding.
- [ ] Google OAuth Calendar/Gmail discovery and recruiter attachments.
- [ ] Production privacy/security review and no personal practice content.
- [ ] Supported provider capability matrix based on observed tests.

Keep development versions below 1.0 until release acceptance gates pass.
