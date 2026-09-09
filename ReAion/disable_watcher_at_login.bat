@echo off
setlocal
set "SHORTCUT=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\GoogleInterviewWatcher.lnk"
if exist "%SHORTCUT%" del "%SHORTCUT%"
echo Startup watcher removed.
pause
