@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (
    py mock_interview.py --serve
) else (
    python mock_interview.py --serve
)
pause
