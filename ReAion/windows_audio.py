"""
Windows master-output safety helper.

Uses pycaw to:
- unmute the default playback endpoint
- ensure master volume is not effectively zero

It never raises the volume above MIN_VOLUME unless it was already higher.
"""

MIN_VOLUME = 0.20  # 20%

def ensure_pc_sound_available(min_volume=MIN_VOLUME):
    """
    Return a dict describing what was found/changed.

    On non-Windows platforms this is a no-op.
    """
    import os
    result = {
        "supported": os.name == "nt",
        "was_muted": None,
        "is_muted": None,
        "old_volume": None,
        "new_volume": None,
        "changed": False,
    }

    if os.name != "nt":
        return result

    from pycaw.pycaw import AudioUtilities

    device = AudioUtilities.GetSpeakers()
    endpoint = device.EndpointVolume

    was_muted = bool(endpoint.GetMute())
    old_volume = float(endpoint.GetMasterVolumeLevelScalar())

    if was_muted:
        endpoint.SetMute(0, None)
        result["changed"] = True

    new_volume = float(endpoint.GetMasterVolumeLevelScalar())

    if new_volume < min_volume:
        endpoint.SetMasterVolumeLevelScalar(float(min_volume), None)
        new_volume = float(endpoint.GetMasterVolumeLevelScalar())
        result["changed"] = True

    result.update(
        was_muted=was_muted,
        is_muted=bool(endpoint.GetMute()),
        old_volume=old_volume,
        new_volume=new_volume,
    )
    return result
