@echo off
REM Test rasa model (with venv)

cd /d "C:\Major Project\backend"

if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
)

call venv\Scripts\activate.bat
pip install -q -r requirements.txt 2>nul

echo.
echo Testing Rasa Model...
echo.

python test_rasa_model.py

pause
