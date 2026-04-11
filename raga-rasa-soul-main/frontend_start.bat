@echo off
REM Start Frontend (after setup.bat has run)

cd /d "C:\Major Project\raga-rasa-soul-main"

echo.
echo Starting Frontend...
echo.
echo Frontend will be available at: http://localhost:5173
echo.
echo Press Ctrl+C to stop
echo.

call npm run dev
