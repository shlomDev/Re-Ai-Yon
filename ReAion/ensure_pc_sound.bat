@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (
    py ensure_pc_sound.py
) else (
    python ensure_pc_sound.py
)
echo.
pause
