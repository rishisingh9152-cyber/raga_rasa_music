@echo off
REM Setup Frontend
REM Run this once to install all dependencies

cd /d "C:\Major Project\raga-rasa-soul-main"

echo.
echo ========================================
echo  Frontend - Setup (First Time)
echo ========================================
echo.

if not exist "node_modules\" (
    echo Installing npm dependencies...
    echo This may take 2-3 minutes...
    echo.
    call npm install
    echo.
) else (
    echo npm dependencies already installed.
    echo.
)

echo.
echo ========================================
echo  Setup Complete!
echo ========================================
echo.
echo Next, run: frontend_start.bat
echo.
pause
