@echo off
REM Master startup script - starts all services in separate terminals
REM IMPORTANT: Run SETUP_ALL.bat FIRST if this is your first time!

setlocal enabledelayedexpansion

echo.
echo ================================================
echo  RagaRasa Platform - Starting All Services
echo ================================================
echo.
echo If this is your FIRST TIME, close this and run:
echo   C:\Major Project\SETUP_ALL.bat
echo.
echo Otherwise, this will start:
echo   1. Emotion Recognition Service (port 5000)
echo   2. Backend API (port 8000)  
echo   3. Frontend (port 5173)
echo.
echo Press Enter to continue...
echo.
pause

REM Terminal 1: Emotion Service
echo Starting Emotion Service...
start "Emotion Service - http://localhost:5000" cmd /k "cd /d C:\projects\emotion_recognition && call emotion_service_start.bat"

timeout /t 3 /nobreak

REM Terminal 2: Backend
echo Starting Backend API...
start "Backend API - http://localhost:8000" cmd /k "cd /d \"C:\Major Project\backend\" && call backend_start.bat"

timeout /t 3 /nobreak

REM Terminal 3: Frontend
echo Starting Frontend...
start "Frontend - http://localhost:5173" cmd /k "cd /d \"C:\Major Project\raga-rasa-soul-main\" && call frontend_start.bat"

timeout /t 3 /nobreak

echo.
echo ================================================
echo Services are starting in separate terminals...
echo.
echo Once all are running:
echo   Open: http://localhost:5173 in your browser
echo.
echo Services:
echo   - Emotion Service: http://localhost:5000/health
echo   - Backend: http://localhost:8000/docs
echo   - Frontend: http://localhost:5173
echo.
echo Press Ctrl+C in any terminal to stop that service
echo ================================================
echo.
pause

endlocal
