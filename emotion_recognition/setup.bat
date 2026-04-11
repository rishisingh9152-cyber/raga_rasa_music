@echo off
REM Setup Emotion Service
REM Run this once to install all dependencies

echo.
echo ========================================
echo  Emotion Service - Setup (First Time)
echo ========================================
echo.

cd /d "C:\projects\emotion_recognition"

if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
    echo.
)

call venv\Scripts\activate.bat

echo Installing dependencies... This may take 5-10 minutes
echo (Downloading torch, torchvision, OpenCV, etc.)
echo.

pip install --upgrade pip setuptools wheel -q 2>nul
pip install -r requirements.txt

echo.
echo ========================================
echo  Setup Complete!
echo ========================================
echo.
echo Next, run: emotion_service_start.bat
echo.
pause
