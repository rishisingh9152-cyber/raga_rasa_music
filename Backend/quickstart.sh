#!/bin/bash

# RagaRasa Backend Quick Start Script

echo "🎵 RagaRasa Music Therapy Backend - Quick Start"
echo "=============================================="
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.11+"
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo "❌ requirements.txt not found. Please run this script from the backend directory."
    exit 1
fi

echo "✅ Python found: $(python3 --version)"
echo ""

# Virtual environment setup
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

echo "🔌 Activating virtual environment..."
source venv/bin/activate

echo "📥 Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "🗄️  Starting MongoDB (in background)..."
# Check if MongoDB is installed
if command -v mongod &> /dev/null; then
    mongod --fork --logpath mongodb.log
    sleep 2
    echo "✅ MongoDB started"
else
    echo "⚠️  MongoDB not installed. Using Docker..."
    docker run -d -p 27017:27017 --name raga-mongo mongo:7.0 2>/dev/null || echo "⚠️  Docker MongoDB might already be running"
    sleep 2
fi

echo ""
echo "🔴 Starting Redis (in background)..."
if command -v redis-server &> /dev/null; then
    redis-server --daemonize yes
    sleep 1
    echo "✅ Redis started"
else
    echo "⚠️  Redis not installed. Using Docker..."
    docker run -d -p 6379:6379 --name raga-redis redis:7-alpine 2>/dev/null || echo "⚠️  Docker Redis might already be running"
    sleep 1
fi

echo ""
echo "💾 Seeding initial data..."
python3 seed_data.py

echo ""
echo "🚀 Starting FastAPI backend..."
echo "==========================================="
echo "Backend will be available at: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo "==========================================="
echo ""

# Start backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

echo ""
echo "👋 Backend stopped. Thank you for using RagaRasa!"
