@echo off
REM Test emotion service (with venv)

cd /d "C:\Major Project\backend"

if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
)

call venv\Scripts\activate.bat
pip install -q requests 2>nul

echo.
echo Testing Emotion Service...
echo.

python test_emotion_service.py

pause
