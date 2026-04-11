@echo off
REM Master Setup Script - Run this FIRST to set up all services
REM This needs to be run only once

echo.
echo ============================================================
echo  RagaRasa Platform - Initial Setup (Run ONCE)
echo ============================================================
echo.
echo This will set up all 3 services:
echo   1. Emotion Recognition Service
echo   2. Backend API
echo   3. Frontend React App
echo.
echo This will take 10-15 minutes. Leave it running!
echo.
pause

echo.
echo ============================================================
echo Step 1: Setting up Emotion Service
echo ============================================================
echo.
start "Emotion Service Setup" cmd /k "cd /d C:\projects\emotion_recognition && call setup.bat"

timeout /t 5

echo.
echo ============================================================
echo Step 2: Setting up Backend
echo ============================================================
echo.
start "Backend Setup" cmd /k "cd /d \"C:\Major Project\backend\" && call setup.bat"

timeout /t 5

echo.
echo ============================================================
echo Step 3: Setting up Frontend
echo ============================================================
echo.
start "Frontend Setup" cmd /k "cd /d \"C:\Major Project\raga-rasa-soul-main\" && call setup.bat"

echo.
echo ============================================================
echo  Setup Started!
echo ============================================================
echo.
echo New windows have opened. Wait for all of them to complete.
echo.
echo Once all setup windows close, run: START_ALL_SERVICES.bat
echo.
pause
