> Development notes. Current verified status and blockers are in PROJECT_STATE.md.

# Optional Local AI

Local AI is optional and is no longer the configured primary answer path.
The normal path uses the signed-in official ChatGPT Windows app. Set
`answer_engine.provider` to `ollama` in `assistant_settings.json` only if you
explicitly want to use the local model instead.

On Linux and macOS, the built-in fallback is the reliable default unless you
provide a platform-specific, accessibility-approved ChatGPT adapter.

The live answer pane works without any external service using the included
interview answer bank and fallback logic.

If Ollama is already running locally on http://127.0.0.1:11434 with the model
qwen2.5:7b-instruct, the answer engine uses it automatically.

If Ollama is unavailable, it falls back immediately to the built-in answer engine.
