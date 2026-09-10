@echo off
setlocal
cd /d "%~dp0"

echo ============================================================
echo ReAion - Developer Setup
echo ============================================================
echo.

call install.bat
if %errorlevel% neq 0 exit /b 1

call enable_watcher_at_login.bat

echo.
echo ============================================================
echo CHROME EXTENSION - ONE-TIME STEP
echo ============================================================
echo 1. Open chrome://extensions
echo 2. Enable Developer mode
echo 3. Remove/reload the older Interview Auto Transcriber extension
echo 4. Click Load unpacked
echo 5. Select:
echo      %~dp0chrome_extension
echo.
echo Then run:
echo      run_full_test.bat
echo.
echo Open and sign into the official ChatGPT Windows app before testing.
echo.
pause
