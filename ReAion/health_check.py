"""Machine-readable readiness check for support and fleet deployment."""
from __future__ import annotations
import json, platform, sys
from app_paths import user_data_dir, settings_path


def health():
    try:
        from answer_engine import ai_status
        ai = ai_status()
        return {"ok": bool(ai.get("ready")), "version": "0.2.0", "platform": platform.platform(), "python": sys.version.split()[0], "data_dir": str(user_data_dir()), "settings": str(settings_path()), "answer_engine": ai}
    except Exception as exc:
        return {"ok": False, "error": str(exc), "platform": platform.platform()}

if __name__ == "__main__":
    result = health()
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["ok"] else 1)
