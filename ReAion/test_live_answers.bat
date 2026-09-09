@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (
    py demo_live_answers.py
) else (
    python demo_live_answers.py
)
pause
