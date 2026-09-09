@echo off
powershell -NoProfile -Command ^
  "try { (Invoke-RestMethod http://127.0.0.1:8765/status) | ConvertTo-Json -Depth 6 } catch { Write-Host 'Watcher is not running.' -ForegroundColor Red }"
echo.
if exist "%~dp0last_self_test.json" type "%~dp0last_self_test.json"
echo.
pause
