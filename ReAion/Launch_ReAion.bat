@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title ReAion - One Click Launch

where py >nul 2>nul
if %errorlevel%==0 (set "PY=py") else (
  where python >nul 2>nul
  if %errorlevel%==0 (set "PY=python") else (
    echo Python 3 is required. Install it from https://www.python.org/downloads/windows/
    echo Enable "Add Python to PATH" during installation, then run this launcher again.
    pause
    exit /b 1
  )
)

if not exist ".venv\Scripts\python.exe" (
  echo [1/4] Creating private Python environment...
  %PY% -m venv .venv || goto :fail
)
set "VPY=%~dp0.venv\Scripts\python.exe"

if not exist ".venv\.dependencies-ready" (
  echo [2/4] Installing ReAion dependencies...
  "%VPY%" -m pip install --upgrade pip || goto :fail
  "%VPY%" -m pip install -r requirements.txt || goto :fail
  "%VPY%" -m playwright install chromium || goto :fail
  type nul > ".venv\.dependencies-ready"
)

echo [3/4] Preparing private user profile...
"%VPY%" setup_private_profile.py || goto :fail
echo [4/4] Starting ReAion...
"%VPY%" health_check.py
"%VPY%" auto_meet_watch.py
exit /b 0

:fail
echo.
echo Setup failed. The detailed error is above.
echo Fix the issue and run Launch_ReAion.bat again.
pause
exit /b 1
