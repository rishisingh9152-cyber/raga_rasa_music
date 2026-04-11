@echo off
REM RagaRasa Backend Quick Start - Windows

echo.
echo 🎵 RagaRasa Music Therapy Backend - Quick Start (Windows)
echo =========================================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3.11+
    exit /b 1
)

echo ✅ Python found
echo.

REM Check if we're in the right directory
if not exist "requirements.txt" (
    echo ❌ requirements.txt not found. Please run from backend directory.
    exit /b 1
)

REM Create virtual environment
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔌 Activating virtual environment...
call venv\Scripts\activate

REM Install dependencies
echo 📥 Installing dependencies...
pip install -r requirements.txt

echo.
echo 🗄️  MongoDB and Redis should be running separately!
echo    Start MongoDB: mongod
echo    Start Redis: redis-server
echo    Or use Docker:
echo    docker run -d -p 27017:27017 mongo:7.0
echo    docker run -d -p 6379:6379 redis:7-alpine
echo.

REM Seed data
echo 💾 Seeding initial data...
python seed_data.py

echo.
echo 🚀 Starting FastAPI backend...
echo =========================================================
echo Backend will be available at: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo =========================================================
echo.

REM Start backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

echo.
echo 👋 Backend stopped. Thank you for using RagaRasa!
pause
