@echo off
REM Setup and run backend with venv

cd /d "C:\Major Project\backend"

REM Check if venv exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate venv
call venv\Scripts\activate.bat

REM Install requirements
echo Installing dependencies...
pip install -r requirements.txt -q

REM Run the backend
echo.
echo Starting backend on http://localhost:8000
echo.
python main.py
