@echo off
setlocal
cd /d "%~dp0"

echo ============================================================
echo Interview Assistant - Local AI Setup
echo ============================================================
echo.
echo This installs/uses Ollama locally and downloads:
echo   qwen2.5:3b-instruct
echo.
echo The model runs on this PC. No OpenAI API key is required.
echo.

where ollama >nul 2>nul
if %errorlevel% neq 0 (
    echo Ollama is not installed.
    where winget >nul 2>nul
    if %errorlevel% neq 0 (
        echo ERROR: winget was not found.
        echo Install Ollama manually, then run this file again.
        pause
        exit /b 1
    )

    echo Installing Ollama...
    winget install --id Ollama.Ollama -e --accept-source-agreements --accept-package-agreements
    if %errorlevel% neq 0 (
        echo ERROR: Ollama installation failed.
        pause
        exit /b 1
    )

    rem Refresh PATH for the current process where possible.
    set "PATH=%LOCALAPPDATA%\Programs\Ollama;%PATH%"
)

echo.
echo Starting Ollama if needed...
start "" /min ollama serve
timeout /t 3 /nobreak >nul

echo.
echo Downloading/checking local interview model...
ollama pull qwen2.5:3b-instruct
if %errorlevel% neq 0 (
    echo ERROR: Model download failed.
    pause
    exit /b 1
)

echo.
echo Running a quick AI test...
ollama run qwen2.5:3b-instruct "Reply with exactly: INTERVIEW AI READY"
echo.
echo Setup complete.
pause
