@echo off
setlocal
cd /d "%~dp0"

echo ============================================================
echo FULL PRE-INTERVIEW TEST
echo ============================================================
echo.
echo Part 1: audio + microphone + Whisper
call run_self_test.bat full_v6_test

echo.
echo Part 2: automatic live-answer test
call test_live_answers.bat
