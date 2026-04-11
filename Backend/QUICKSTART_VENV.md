# Quick Start Guide - With venv

## Terminal 1: Start Emotion Service (No venv needed)

```bash
cd C:\projects\emotion_recognition

# If first time, create venv there too
python -m venv venv
venv\Scripts\activate.bat

# Install dependencies
pip install -r requirements.txt

# Start the service
python api.py
```

You should see: `[API] http://localhost:5000`

---

## Terminal 2: Start MongoDB & Redis (Using Docker)

```bash
cd "C:\Major Project\backend"

# Start MongoDB and Redis containers
docker-compose up
```

**OR if you don't have Docker, start MongoDB and Redis manually:**

Terminal 2a (MongoDB):
```bash
mongod
```

Terminal 2b (Redis):
```bash
redis-server
```

---

## Terminal 3: Start Backend

```bash
cd "C:\Major Project\backend"

# Create virtual environment (first time only)
python -m venv venv

# Activate it
venv\Scripts\activate.bat

# Install dependencies
pip install -r requirements.txt

# Start backend
python main.py
```

You should see: `Uvicorn running on http://0.0.0.0:8000`

---

## Terminal 4: Start Frontend

```bash
cd "C:\Major Project\raga-rasa-soul-main"

# Install dependencies (if not already done)
npm install

# Start frontend
npm run dev
```

You should see: `VITE v... ready in ... ms`

---

## Quick Testing (After Everything is Running)

### Test 1: Emotion Service Health
```bash
cd "C:\Major Project\backend"
venv\Scripts\activate.bat
python test_emotion_service.py
```

### Test 2: Rasa Model
```bash
cd "C:\Major Project\backend"
venv\Scripts\activate.bat
python test_rasa_model.py
```

### Test 3: Full API (curl)
```bash
# Start session
curl -X POST http://localhost:8000/session/start -H "Content-Type: application/json" -d "{\"user_id\":\"test_user\"}"

# Should return: {"session_id":"abc123..."}
```

---

## One-Command Setup (After first time)

Create a batch file `run_all.bat`:

```batch
@echo off
echo Starting all services...
echo.

REM Terminal 1: Emotion Service
start "Emotion Service" cmd /k "cd C:\projects\emotion_recognition && venv\Scripts\activate.bat && python api.py"

REM Terminal 2: Backend
start "Backend" cmd /k "cd \"C:\Major Project\backend\" && venv\Scripts\activate.bat && python main.py"

REM Terminal 3: Frontend (if you have Node.js)
start "Frontend" cmd /k "cd \"C:\Major Project\raga-rasa-soul-main\" && npm run dev"

echo.
echo All services starting...
echo - Emotion Service: http://localhost:5000
echo - Backend: http://localhost:8000
echo - Frontend: http://localhost:5173
echo.
```

Then just run: `run_all.bat`

---

## File Locations Reference

```
Emotion Service:    C:\projects\emotion_recognition\
Backend:            C:\Major Project\backend\
Frontend:           C:\Major Project\raga-rasa-soul-main\
Rasa Model:         C:\Major Project\backend\models\rasa_classification\model.h5 ✅
```

## Environment Status

✅ **Configured & Ready:**
- External emotion service (port 5000)
- Backend API (port 8000)
- Rasa model loaded
- All 7 endpoints ready

⏳ **Waiting For:**
- You to activate venv and run services

---

## If You Get Errors

### "ModuleNotFoundError"
Make sure venv is activated:
```bash
cd "C:\Major Project\backend"
venv\Scripts\activate.bat
```

### "Connection refused" on emotion service
Check if Flask is running:
```bash
cd C:\projects\emotion_recognition
venv\Scripts\activate.bat
python api.py
```

### "MongoDB connection failed"
Make sure MongoDB is running (either via Docker or `mongod`)

---

## Next: Access the Application

Once all 4 services are running:

1. Open: `http://localhost:5173` (or your frontend port)
2. Click "Start Session"
3. Upload a photo
4. Get emotion detected + music recommendations
5. Done! 🎵
