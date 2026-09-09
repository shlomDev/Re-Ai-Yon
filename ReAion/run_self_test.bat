@echo off
setlocal
cd /d "%~dp0"
set "LABEL=%~1"
if "%LABEL%"=="" set "LABEL=manual"

where py >nul 2>nul
if %errorlevel%==0 (
    py audio_self_test.py --label "%LABEL%"
) else (
    python audio_self_test.py --label "%LABEL%"
)
