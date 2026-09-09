@echo off
setlocal
cd /d "%~dp0"

echo Installing local transcriber dependencies...
echo.

where py >nul 2>nul
if %errorlevel%==0 (
    py -m pip install --upgrade pip
    py -m pip install -r requirements.txt
) else (
    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt
)

echo.
echo Python setup complete.
echo.
echo NEXT - install the Chrome trigger once:
echo   1. Open Chrome
echo   2. Go to chrome://extensions
echo   3. Turn on Developer mode
echo   4. Click "Load unpacked"
echo   5. Choose:
echo      %~dp0chrome_extension
echo.
echo Then run start_auto_watcher.bat before the interview,
echo or run enable_watcher_at_login.bat once.
echo.
pause
