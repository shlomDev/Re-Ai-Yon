#!/usr/bin/env python
"""Non-destructive readiness test for every configured answer provider."""
import json, os
from pathlib import Path
from answer_engine import ai_status

BASE = Path(__file__).resolve().parent

def check_provider(name, cfg):
    if name == "ollama":
        from answer_engine import ollama_status
        st = ollama_status()
        return bool(st.get("running") and st.get("model_present")), st.get("error", "model missing") + "; local mode has no paid account"
    if name == "chatgpt_windows":
        from chatgpt_windows import ChatGPTWindowsClient
        st = ChatGPTWindowsClient().status()
        return st.ready, st.detail + f"; account_state={st.account_state}"
    if name == "claude_desktop":
        from claude_desktop import ClaudeDesktopClient
        st = ClaudeDesktopClient().status()
        return st.ready, st.detail + f"; account_state={st.account_state}"
    if name in ("anthropic", "openai_compatible"):
        env = cfg.get("api_key_env", "ANTHROPIC_API_KEY" if name == "anthropic" else "OPENAI_API_KEY")
        return bool(os.getenv(env)), ("API key configured" if os.getenv(env) else f"missing {env}")
    return True, "offline built-in fallback"

def main():
    settings = json.loads((BASE / "assistant_settings.json").read_text(encoding="utf-8-sig"))
    providers = {
        "chatgpt_windows": settings.get("chatgpt_windows", {}),
        "claude_desktop": settings.get("claude_desktop", {}),
        "anthropic": settings.get("anthropic", {}),
        "openai_compatible": settings.get("openai_compatible", {}),
        "ollama": settings.get("local_ai", {}),
        "built_in": {},
    }
    selected = settings.get("answer_engine", {}).get("provider")
    failures = 0
    for name, cfg in providers.items():
        try: ok, detail = check_provider(name, cfg)
        except Exception as exc: ok, detail = False, str(exc)
        marker = "SELECTED" if name == selected else "available option"
        print(f"{name:18} {'READY' if ok else 'NOT READY':11} [{marker}] {detail}")
        if name == selected and not ok: failures += 1
    print("Selected provider:", selected)
    print("Fallback:", "READY" if ai_status().get("fallback_ready", True) else "NOT READY")
    return 0 if failures == 0 else 2

if __name__ == "__main__": raise SystemExit(main())
