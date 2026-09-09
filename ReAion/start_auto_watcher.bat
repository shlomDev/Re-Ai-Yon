@echo off
setlocal
cd /d "%~dp0"

where py >nul 2>nul
if %errorlevel%==0 (
    py auto_meet_watch.py
) else (
    python auto_meet_watch.py
)
pause
