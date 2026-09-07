# PyInstaller onedir build. Runtime data stays outside the install directory.
from pathlib import Path
root = Path(SPECPATH)
datas = [
    (str(root / 'assistant_settings.json'), '.'),
    (str(root / 'candidate_profile.example.md'), '.'),
    (str(root / 'answer_bank.example.json'), '.'),
    (str(root / 'interview_guidance.example.md'), '.'),
    (str(root / 'interviews.example.json'), '.'),
    (str(root / 'meet_transcriber.py'), '.'),
    (str(root / 'interview_assistant_gui.py'), '.'),
    (str(root / 'audio_self_test.py'), '.'),
    (str(root / 'window_manager.py'), '.'),
    (str(root / 'window_layout.py'), '.'),
    (str(root / 'platform_support.py'), '.'),
]
a = Analysis(
    ['auto_meet_watch.py'], pathex=[str(root)], datas=datas,
    hiddenimports=['tkinter', 'soundcard', 'faster_whisper', 'pywinauto'],
    excludes=[],
)
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, a.binaries, a.datas, [], name='InterviewCopilot', console=True)
