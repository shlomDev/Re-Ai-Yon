#!/usr/bin/env python
import json
import re
import subprocess
import time
import threading
_browser_local = threading.local()

def close_answer_engine():
    client = getattr(_browser_local, "client", None)
    if client is not None:
        client.close()
        _browser_local.client = None

import urllib.request
from pathlib import Path
from runtime_data import text as load_text, json_data
from app_paths import settings_path

BASE = Path(__file__).resolve().parent
SETTINGS = json.loads(settings_path().read_text(encoding="utf-8-sig"))
PROFILE = load_text("candidate_profile.md", "No private candidate profile has been configured yet. Use only information provided in the question.")
GUIDANCE = load_text("interview_guidance.md", "Use direct technical reasoning. Use STAR only when the question is clearly behavioral.")
BANK = json_data("answer_bank.json", {})

QUESTION_STARTERS = (
    "what ", "why ", "how ", "when ", "where ", "who ", "which ",
    "can you ", "could you ", "would you ", "do you ", "did you ",
    "have you ", "tell me ", "describe ", "walk me ", "give me ",
    "explain ", "suppose ", "imagine ", "if a ", "if you ",
    "מה ", "למה ", "איך ", "כיצד ", "מתי ", "איפה ", "מי ", "האם ",
    "ספר לי ", "תאר ", "תסביר "
)

def normalize(text):
    return re.sub(r"\s+", " ", text or "").strip()

def looks_like_question(text):
    t = normalize(text).lower()
    if len(t) < SETTINGS["live"].get("question_min_chars", 12):
        return False
    # This is only a compatibility helper; live segmentation uses speech
    # boundaries and deliberately does not require interrogative keywords.
    return "?" in t or bool(t)

def fallback_answer(question):
    q = question.lower()
    if re.search(r"[\u0590-\u05ff]", q):
        if any(w in q for w in ("רשת", "תקשורת", "חיבור", "dhcp", "נגישות")):
            return ("הייתי מתחיל בהגדרת היקף התקלה ובדיקת השכבה הפיזית: כבל, נוריות קישור, NIC ופורט המתג. "
                    "אחר כך הייתי בודק ממשק, כתובת MAC, VLAN, IP או DHCP, נתיב ושער ברירת המחדל. "
                    "הייתי משווה לשרת תקין, בודק לוגים, משנה משתנה אחד בכל פעם, ולבסוף מאמת את החיבור מקצה לקצה.")
        return ("הייתי מגדיר את הבעיה וההשפעה שלה, אוסף מצב ולוגים לפני שינוי, עובד שכבה־שכבה, "
                "משווה למערכת תקינה, מבצע שינוי בטוח ומינימלי, ומאמת את התוצאה מקצה לקצה.")
    best = None
    best_score = 0
    for item in BANK.values():
        score = 0
        for pat in item.get("patterns", []):
            p = pat.lower()
            if p in q:
                score += max(3, len(p.split()))
            else:
                words = [w for w in re.findall(r"[a-z0-9]+", p) if len(w) > 3]
                score += sum(1 for w in words if w in q)
        if score > best_score:
            best_score = score
            best = item.get("answer")

    if best_score > 0 and best:
        return best

    if any(w in q for w in [
        "troubleshoot", "diagnose", "problem", "issue", "failure",
        "network", "server", "linux", "hardware"
    ]):
        return (
            "I’d start by defining the symptom and scope, then work from the lowest relevant "
            "layer upward. I’d collect current state and logs before changing anything, compare "
            "against a known-good system where possible, isolate one variable at a time, and make "
            "the smallest safe corrective change. I’d then verify the result end-to-end and document "
            "what caused the issue and what fixed it."
        )

    if any(w in q for w in [
        "example", "time when", "situation", "conflict", "challenge",
        "mistake", "failed", "leadership"
    ]):
        return (
            "Use one real example and structure it as STAR: explain the situation in one or two "
            "sentences, your specific responsibility, the actions you personally took, and the "
            "result. Finish with what you learned or what you changed afterward."
        )

    return (
        "Answer the question directly, then give one concrete example from your infrastructure "
        "experience. Keep it concise, explain your reasoning, and end with how you validated the "
        "result. Do not claim experience you do not have."
    )

def ollama_status():
    cfg = SETTINGS["local_ai"]
    try:
        with urllib.request.urlopen(cfg["url"] + "/api/tags", timeout=2) as r:
            data = json.loads(r.read().decode("utf-8"))
        names = [m.get("name", "") for m in data.get("models", [])]
        wanted = cfg["model"]
        present = any(n == wanted or n.startswith(wanted + ":") for n in names)
        return {"running": True, "model_present": present, "models": names}
    except Exception as e:
        return {"running": False, "model_present": False, "error": str(e), "models": []}

def ensure_ollama_running():
    st = ollama_status()
    if st["running"]:
        return st

    try:
        flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        subprocess.Popen(
            ["ollama", "serve"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=flags,
        )
    except Exception:
        return st

    for _ in range(20):
        time.sleep(0.5)
        st = ollama_status()
        if st["running"]:
            return st
    return st

def ollama_prompt(question):
    return f"""You are a real-time interview answer assistant.
SOURCE-OF-TRUTH CANDIDATE CONTEXT:\n{PROFILE}
INTERVIEWER-PROVIDED ANSWER GUIDANCE:\n{GUIDANCE}
INTERVIEWER QUESTION:\n{question}
Write only a concise spoken answer in the same language as the question. Never invent facts.
Technical questions: explain reasoning, assumptions, practical steps, trade-offs and validation.
Competency questions: use natural STARL only when appropriate. Keep it under 130 words."""

def ollama_answer(question):
    cfg = SETTINGS["local_ai"]
    prompt = ollama_prompt(question)
    """You are a real-time interview answer assistant.
The user is currently in a Data Center Technician / infrastructure interview.

SOURCE-OF-TRUTH CANDIDATE CONTEXT:
{PROFILE}

INTERVIEWER-PROVIDED ANSWER GUIDANCE:
{GUIDANCE}

INTERVIEWER QUESTION:
{question}

Write ONLY the suggested spoken answer.

Rules:
- Answer the exact question.
- Use only facts in the candidate context.
- Never invent experience, employers, certifications, numbers, incidents or achievements.
- Technical question: give a practical sequence and verification.
- Competency/behavioral question: use compact natural STARL based on a real example.
- Technical/problem-solving question: do not force STAR; explain reasoning,
  assumptions, steps, trade-offs, and validation.
- Prefer a specific real example from the context when one fits.
- Natural spoken language, not essay language.
- Answer in the same language as the interviewer question, including Hebrew,
  unless the interviewer clearly asks for another language.
- Around 60–110 words; never more than 130 words.
- No headings, no preamble, no commentary.
"""
    payload = json.dumps({
        "model": cfg["model"],
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.25,
            "num_predict": 220
        }
    }).encode("utf-8")

    req = urllib.request.Request(
        cfg["url"] + "/api/generate",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=cfg.get("timeout_seconds", 20)) as r:
        data = json.loads(r.read().decode("utf-8"))
    answer = normalize(data.get("response", ""))
    if not answer:
        raise RuntimeError("Local AI returned an empty answer.")
    return answer

def generate_answer(question):
    q = normalize(question)
    if not q:
        return "", "none"

    provider = SETTINGS.get("answer_engine", {}).get("provider", "built_in")
    if provider in ("anthropic", "openai_compatible"):
        try:
            prompt = ollama_prompt(q)
            from answer_providers import anthropic_answer, openai_compatible_answer
            cfg = SETTINGS.get(provider, {})
            fn = anthropic_answer if provider == "anthropic" else openai_compatible_answer
            answer = fn(prompt, cfg)
            if answer: return answer, provider
        except Exception:
            pass
    if provider == "claude_desktop":
        try:
            from claude_desktop import ClaudeDesktopClient
            title = ClaudeDesktopClient().submit_question(q)
            return ("Question sent automatically. Read the answer in the Claude window "
                    f"({title}).", "Claude Desktop")
        except Exception:
            return fallback_answer(q), "built-in fallback (Claude unavailable)"
    if provider == "chatgpt_windows":
        try:
            from chatgpt_windows import ChatGPTWindowsClient
            cfg = SETTINGS.get("chatgpt_windows", {})
            client = ChatGPTWindowsClient(
                open_shortcut=cfg.get("companion_shortcut", "% "),
                window_timeout=float(cfg.get("window_timeout_seconds", 5)),
            )
            title = client.submit_question(q)
            return (
                "Question sent automatically. Read the suggested answer in the "
                f"ChatGPT window on the right ({title}).",
                "ChatGPT Windows",
            )
        except Exception:
            # Never let an answer-backend failure interfere with the meeting.
            return fallback_answer(q), "built-in fallback (ChatGPT unavailable)"

    if provider == "chatgpt_browser":
        try:
            from chatgpt_browser import ChatGPTBrowserClient
            cfg = SETTINGS.get("chatgpt_browser", {})
            client = getattr(_browser_local, "client", None)
            if client is None:
                client = ChatGPTBrowserClient(url=cfg.get("url", "https://chatgpt.com/"), user_data_dir=cfg.get("user_data_dir") or None)
                _browser_local.client = client
            title = client.submit_question(q)
            return "Question sent automatically. Read the answer in the visible ChatGPT browser pane (" + title + ").", "ChatGPT browser"
        except Exception:
            return fallback_answer(q), "built-in fallback (ChatGPT browser unavailable)"

    if provider == "ollama":
        st = ensure_ollama_running()
        if st.get("running") and st.get("model_present"):
            try:
                return ollama_answer(q), "local AI"
            except Exception:
                pass

    return fallback_answer(q), "built-in fallback"

def ai_status():
    provider = SETTINGS.get("answer_engine", {}).get("provider", "built_in")
    if provider == "claude_desktop":
        try:
            from claude_desktop import ClaudeDesktopClient
            st = ClaudeDesktopClient().status()
            return {"provider": provider, "ready": st.ready, "fallback_ready": True,
                    "detail": st.detail, "window_title": st.window_title}
        except Exception as exc:
            return {"provider": provider, "ready": False, "fallback_ready": True, "detail": str(exc)}
    if provider in ("anthropic", "openai_compatible"):
        import os
        cfg = SETTINGS.get(provider, {})
        env_name = cfg.get("api_key_env", "ANTHROPIC_API_KEY" if provider == "anthropic" else "OPENAI_API_KEY")
        ready = bool(os.getenv(env_name))
        return {"provider": provider, "ready": ready, "fallback_ready": True,
                "detail": ("API key configured" if ready else f"Set {env_name}")}
    if provider == "chatgpt_windows":
        try:
            from chatgpt_windows import ChatGPTWindowsClient
            st = ChatGPTWindowsClient().status()
            return {
                "provider": provider,
                "running": st.ready,
                "model_present": st.ready,
                "ready": st.ready,
                "fallback_ready": True,
                "detail": st.detail,
                "window_title": st.window_title,
                "account_state": getattr(st, "account_state", "unknown"),
            }
        except Exception as exc:
            return {"provider": provider, "running": False, "model_present": False,
                    "ready": False, "fallback_ready": True, "detail": str(exc)}
    if provider == "chatgpt_browser":
        try:
            from chatgpt_browser import ChatGPTBrowserClient
            st = ChatGPTBrowserClient(url=SETTINGS.get("chatgpt_browser", {}).get("url", "https://chatgpt.com/")).status()
            return {"provider": provider, "ready": st.ready, "fallback_ready": True, "detail": st.detail, "url": st.url}
        except Exception as exc:
            return {"provider": provider, "ready": False, "fallback_ready": True, "detail": str(exc)}
    if provider == "ollama":
        return {"provider": provider, **ollama_status()}
    return {"provider": "built_in", "running": True, "model_present": True,
            "ready": True, "detail": "Built-in fallback ready"}

if __name__ == "__main__":
    import sys
    q = normalize(" ".join(sys.argv[1:]))
    if not q:
        q = input("Question: ").strip()
    ans, source = generate_answer(q)
    print(f"[{source}]")
    print(ans)
