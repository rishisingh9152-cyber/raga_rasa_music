@echo off
REM Backend Setup - Creates venv and installs all dependencies

cd /d "C:\Major Project\backend"

echo.
echo ========================================
echo  Backend - Setup (First Time)
echo ========================================
echo.

if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
    echo.
)

call venv\Scripts\activate.bat

echo Installing dependencies...
echo This may take 10-15 minutes. Please wait...
echo.

pip install --upgrade pip setuptools wheel -q 2>nul
pip install -r requirements.txt --no-cache-dir

echo.
echo ========================================
echo  Setup Complete!
echo ========================================
echo.
echo Next, run: backend_start.bat
echo.
pause
