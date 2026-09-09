# Development Instructions

When modifying this project:

- Prefer the simplest working solution.
- Make minimal, focused changes; do not refactor unrelated code.
- State assumptions when they affect behavior.
- Define success criteria before large changes.
- Verify changes with an executable test whenever possible.
- Preserve existing working behavior unless the task explicitly changes it.
- Keep meeting-provider logic separate from audio/transcription/answer logic.
- Do not hard-code secrets.
- Do not commit recordings, transcripts, cookies, authentication tokens, or browser profiles.
- Do not implement ChatGPT integration by stealing cookies/session tokens or calling undocumented private endpoints.
- Prefer supported Windows UI Automation/accessibility for the official ChatGPT application.
- Do not silently enable the camera; ask first.
- Do not let copilot failures interfere with the actual meeting application.
- Treat the answer pane as the primary UI and transcription as secondary/background.
