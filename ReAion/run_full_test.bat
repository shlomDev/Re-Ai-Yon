@echo off
setlocal
cd /d "%~dp0"

echo ============================================================
echo FULL PRE-INTERVIEW TEST
echo ============================================================
echo.
echo Part 1: audio + microphone + Whisper
call run_self_test.bat full_development_test

echo.
echo Part 2: simulated answer-panel test (no live AI or audio)
call test_live_answers.bat
