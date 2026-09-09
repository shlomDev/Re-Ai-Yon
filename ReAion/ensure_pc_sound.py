#!/usr/bin/env python
from windows_audio import ensure_pc_sound_available

s = ensure_pc_sound_available()

if not s.get("supported"):
    print("Windows audio control is only needed on Windows.")
else:
    old = round((s.get("old_volume") or 0) * 100)
    new = round((s.get("new_volume") or 0) * 100)
    if s.get("was_muted"):
        print(f"PC sound was muted. It is now UNMUTED at {new}%.")
    elif old < 20:
        print(f"PC sound was only {old}%. It is now {new}%.")
    else:
        print(f"PC sound is ready: unmuted at {new}%.")
