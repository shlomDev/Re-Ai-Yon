"""Optional API-backed answer providers. Secrets come only from environment variables."""
from __future__ import annotations
import json, os, urllib.request

def _post(url, payload, headers, timeout=20):
    req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())

def anthropic_answer(prompt, cfg):
    key = os.getenv(cfg.get("api_key_env", "ANTHROPIC_API_KEY"))
    if not key: raise RuntimeError("Anthropic API key environment variable is not set")
    data = _post(cfg.get("url", "https://api.anthropic.com/v1/messages"), {
        "model": cfg.get("model", "claude-sonnet-4-20250514"), "max_tokens": cfg.get("max_tokens", 300),
        "temperature": 0.2, "messages": [{"role": "user", "content": prompt}]},
        {"x-api-key": key, "anthropic-version": "2023-06-01", "content-type": "application/json"}, cfg.get("timeout_seconds", 20))
    return "".join(x.get("text", "") for x in data.get("content", [])).strip()

def openai_compatible_answer(prompt, cfg):
    key = os.getenv(cfg.get("api_key_env", "OPENAI_API_KEY"))
    if not key: raise RuntimeError("OpenAI-compatible API key environment variable is not set")
    data = _post(cfg["url"].rstrip("/") + "/chat/completions", {
        "model": cfg["model"], "temperature": 0.2, "max_tokens": cfg.get("max_tokens", 300),
        "messages": [{"role": "user", "content": prompt}]},
        {"Authorization": "Bearer " + key, "Content-Type": "application/json"}, cfg.get("timeout_seconds", 20))
    return data["choices"][0]["message"]["content"].strip()
