@echo off
REM Start Backend (after setup.bat has run)

cd /d "C:\Major Project\backend"

call venv\Scripts\activate.bat

echo.
echo Starting Backend API...
echo.
echo Backend will be available at: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
echo Make sure MongoDB and Redis are running!
echo.
echo Press Ctrl+C to stop
echo.

python main.py
