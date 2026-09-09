@echo off
setlocal
cd /d "%~dp0"

set "TARGET=%~dp0start_auto_watcher.bat"
set "STARTUP=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "SHORTCUT=%STARTUP%\GoogleInterviewWatcher.lnk"

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$ws = New-Object -ComObject WScript.Shell; " ^
  "$s = $ws.CreateShortcut('%SHORTCUT%'); " ^
  "$s.TargetPath = '%TARGET%'; " ^
  "$s.WorkingDirectory = '%~dp0'; " ^
  "$s.WindowStyle = 7; " ^
  "$s.Save()"

echo.
echo Installed startup watcher:
echo %SHORTCUT%
echo.
echo It is restricted to the September 1 Google interview Meet only.
pause
