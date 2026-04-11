@echo off
REM Start Emotion Service (after setup.bat has run)

cd /d "C:\projects\emotion_recognition"

call venv\Scripts\activate.bat

echo.
echo Starting Emotion Recognition Service...
echo.
echo Service will be available at: http://localhost:5000
echo.
echo Health Check: http://localhost:5000/health
echo Detect Emotion: POST http://localhost:5000/detect
echo.
echo Press Ctrl+C to stop
echo.

python api.py
