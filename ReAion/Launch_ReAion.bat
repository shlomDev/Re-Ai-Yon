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
  echo [1/3] First-time setup: creating private Python environment...
  %PY% -m venv .venv || goto :fail
)
set "VPY=%~dp0.venv\Scripts\python.exe"

if not exist ".venv\.dependencies-ready" (
  echo [2/3] First-time setup: installing ReAion dependencies...
  "%VPY%" -m pip install --upgrade pip || goto :fail
  "%VPY%" -m pip install -r requirements.txt || goto :fail
  "%VPY%" -m playwright install chromium || goto :fail
  type nul > ".venv\.dependencies-ready"
)

echo [3/3] Starting ReAion...
"%VPY%" setup_private_profile.py || goto :fail
"%VPY%" quick_start.py || goto :fail
exit /b 0

:fail
echo.
echo ReAion could not start. The detailed error is above.
pause
exit /b 1
