@echo off
REM Admin Setup Script for Raga Rasa Soul
REM This script will help you get admin access

echo.
echo ================================================
echo   RAGA RASA SOUL - ADMIN SETUP SCRIPT
echo ================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

echo Python is installed
echo.

REM Check if MongoDB is running
timeout /t 2 /nobreak >nul

echo Checking MongoDB connection...
python -c "from pymongo import MongoClient; MongoClient('mongodb://localhost:27017', serverSelectionTimeoutMS=1000).admin.command('ping')" 2>nul
if errorlevel 1 (
    echo WARNING: MongoDB may not be running
    echo Make sure MongoDB is running on localhost:27017
    echo.
)

echo.
echo ================================================
echo   STEP 1: Starting Backend Server
echo ================================================
echo.
echo The backend will start in a new window...
echo Wait for message: "[Database] Database initialization complete"
echo.

REM Start backend in new window
start "Raga Rasa Backend" cmd /k "cd Backend && python main.py"

echo Waiting for backend to start (30 seconds)...
timeout /t 30 /nobreak

echo.
echo ================================================
echo   STEP 2: Setting Up Admin Account
echo ================================================
echo.
echo Creating admin with:
echo   Email: rishisingh9152@gmail.com
echo   Password: Ripra@2622
echo.

python setup_admin.py

if errorlevel 1 (
    echo.
    echo ERROR: Admin setup failed!
    echo.
    echo Make sure:
    echo   1. Backend is running (check the backend window)
    echo   2. MongoDB is running
    echo   3. No other process is using port 8080
    echo.
    pause
    exit /b 1
)

echo.
echo ================================================
echo   STEP 3: Starting Frontend Server
echo ================================================
echo.
echo The frontend will start in a new window...
echo You can then access the app at: http://localhost:5173
echo.

cd raga-rasa-soul-main
start "Raga Rasa Frontend" cmd /k "npm run dev"

echo.
echo ================================================
echo   ✅ SETUP COMPLETE!
echo ================================================
echo.
echo Your admin account is ready:
echo   Email: rishisingh9152@gmail.com
echo   Password: Ripra@2622
echo.
echo Access your application:
echo   Frontend: http://localhost:5173
echo   Login: http://localhost:5173/login
echo   Admin Dashboard: http://localhost:5173/admin
echo.
echo Backend API:
echo   http://localhost:8080
echo   Docs: http://localhost:8080/docs
echo.
echo ================================================
echo.
pause
