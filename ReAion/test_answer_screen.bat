@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (
    start "" py interview_assistant_gui.py
    py answer_engine.py "How would you troubleshoot a server with no network connectivity?"
) else (
    start "" python interview_assistant_gui.py
    python answer_engine.py "How would you troubleshoot a server with no network connectivity?"
)
echo.
pause
