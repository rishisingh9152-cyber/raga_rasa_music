# Integration Setup & Testing Guide

## Prerequisites Checklist

- [ ] Emotion Recognition Service project at: `C:\projects\emotion_recognition`
- [ ] Rasa model file uploaded to: `C:\Major Project\backend\models\rasa_classification\model.h5` ✅

## Step 1: Start Emotion Recognition Service

```bash
cd C:\projects\emotion_recognition

# If first time, install dependencies
pip install -r requirements.txt

# Start the Flask service
python api.py
```

You should see:
```
[API] http://localhost:5000
```

The service provides:
- `GET /health` - Health check
- `POST /detect` - Emotion detection from base64 image

## Step 2: Set Up Backend Environment (with venv)

```bash
cd "C:\Major Project\backend"

# Create virtual environment (if not exists)
python -m venv venv

# Activate virtual environment
venv\Scripts\activate.bat

# Install dependencies
pip install -r requirements.txt
```

The backend will automatically load:
- External emotion service client (configured in `.env`)
- Rasa classification model from `models/rasa_classification/model.h5` ✅

**NOTE: Always activate venv before running Python commands:**
```bash
venv\Scripts\activate.bat
```

## Step 3: Start Backend Services

You need MongoDB and Redis running. Options:

### Option A: Using Docker (Recommended)

```bash
# Make sure you're in the backend directory
cd "C:\Major Project\backend"

# Start MongoDB + Redis + Backend
docker-compose up
```

This starts:
- MongoDB on port 27017
- Redis on port 6379
- FastAPI backend on port 8000

### Option B: Manual Setup

If you have MongoDB and Redis installed locally:

```bash
# Terminal 1: Start MongoDB
mongod

# Terminal 2: Start Redis
redis-server

# Terminal 3: Start Backend (with venv)
cd "C:\Major Project\backend"
venv\Scripts\activate.bat
python main.py
```

## Step 4: Start Frontend

```bash
cd "C:\Major Project\raga-rasa-soul-main"

# Install dependencies (if not already done)
npm install

# Start development server
npm run dev
```

The frontend will be available at `http://localhost:5173` (or 3000, depending on Vite config)

## Configuration Files

### Backend `.env` (Updated for external service)
Location: `C:\Major Project\backend\.env`

```env
# External Emotion Service - CONFIGURED
EMOTION_SERVICE_URL=http://localhost:5000
EMOTION_SERVICE_ENDPOINT=/detect
USE_EXTERNAL_EMOTION_SERVICE=True

# Rasa Model - CONFIGURED
RASA_MODEL_PATH=./models/rasa_classification/
USE_RASA_MODEL=True
```

### Model Location - CONFIGURED
✅ Model uploaded to: `C:\Major Project\backend\models\rasa_classification\model.h5`

## Testing the Integration

### 1. Test Emotion Service (with venv)

**Option A: Using batch script**
```bash
cd "C:\Major Project\backend"
test_emotion_service.bat
```

**Option B: Manual**
```bash
cd "C:\Major Project\backend"
venv\Scripts\activate.bat
python test_emotion_service.py
```

Expected output:
```
✅ Emotion service is healthy!
Status: 200
Response: {
  "emotions": {...},
  "dominant": "Happy 😊",
  "raw_dominant": "happy",
  "is_brave": false
}
```

### 2. Test Rasa Model (with venv)

**Option A: Using batch script**
```bash
cd "C:\Major Project\backend"
test_rasa_model.bat
```

**Option B: Manual**
```bash
cd "C:\Major Project\backend"
venv\Scripts\activate.bat
python test_rasa_model.py
```

Expected output:
```
✅ Rasa model loaded successfully!
Model type: keras

Emotion       | Rasa      | Confidence | Method
Happy         | Shringar  | 95.2%      | model
Sad           | Shok      | 88.1%      | model
...
```

### 3. Full End-to-End Test

```bash
# Start emotion service (in terminal 1)
cd C:\projects\emotion_recognition
python api.py

# Start backend (in terminal 2)
cd "C:\Major Project\backend"
docker-compose up
# OR if manual setup:
# python main.py

# Run end-to-end test (in terminal 3)
cd "C:\Major Project\backend"
python -m pytest tests/test_integration.py -v
```

### 4. Manual API Test

Test with curl:

```bash
# Test 1: Start session
curl -X POST http://localhost:8000/session/start \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test_user"}'

# You'll get: {"session_id": "abc123def456"}

# Test 2: Detect emotion from image
curl -X POST http://localhost:8000/detect-emotion \
  -H "Content-Type: application/json" \
  -d '{"image_base64":"<your_base64_image>", "session_id":"abc123def456"}'

# Test 3: Get recommendations
curl -X POST http://localhost:8000/recommend/live \
  -H "Content-Type: application/json" \
  -d '{"emotion":"happy", "session_id":"abc123def456", "cognitive_data":{}}'
```

## Integration Flow

```
User Image
    ↓
Backend /detect-emotion
    ↓
External Emotion Service (http://localhost:5000/detect)
    ├─ Input: {image: "base64_string"}
    └─ Output: {emotions: {...}, raw_dominant: "happy", ...}
    ↓
Rasa Classification Model
    ├─ Input: emotion = "happy"
    ├─ Process: One-hot encode emotion → Model prediction
    └─ Output: {rasa: "Shringar", confidence: 0.95}
    ↓
Recommendation Engine
    ├─ Input: rasa + session_id + cognitive_data
    └─ Output: Song[] with Shringar ragas
    ↓
Frontend Music Player
    └─ Display recommended songs
```

## Troubleshooting

### "Connection refused" on emotion service
- Is Flask running at `http://localhost:5000`?
- Run: `python C:\projects\emotion_recognition\api.py`

### "ModuleNotFoundError" in backend
- Make sure venv is activated
- Run: `pip install -r requirements.txt`

### Rasa model not loading
- Check file exists: `C:\Major Project\backend\models\rasa_classification\model.h5` ✅
- Check file size: ~39.7 MB ✅
- Check TensorFlow is installed: `pip list | grep tensorflow`

### MongoDB/Redis not running (if using manual setup)
- MongoDB: `mongod` should be in PATH
- Redis: `redis-server` should be in PATH
- Or use Docker: `docker-compose up`

## What's Ready

✅ **Configured**:
- Backend endpoints (7 API routes)
- External emotion service integration
- Rasa model loading infrastructure
- Configuration files (.env)
- Model uploaded

⏳ **Next Steps**:
1. Start emotion service: `python C:\projects\emotion_recognition\api.py`
2. Start backend (Docker or manual)
3. Start frontend: `npm run dev`
4. Access at `http://localhost:5173`
5. Test full workflow

---

**Quick Start (Copy & Paste - with venv):**

```bash
# Terminal 1: Emotion Service (with venv)
cd C:\projects\emotion_recognition
python -m venv venv
venv\Scripts\activate.bat
pip install -r requirements.txt
python api.py

# Terminal 2: Backend (with venv)
cd "C:\Major Project\backend"
python -m venv venv
venv\Scripts\activate.bat
pip install -r requirements.txt
python main.py

# Terminal 3: Frontend (no venv needed)
cd "C:\Major Project\raga-rasa-soul-main"
npm run dev

# Then open http://localhost:5173 in browser
```

**Or use the batch scripts:**

```bash
# Terminal 1: Emotion Service
cd C:\projects\emotion_recognition
venv\Scripts\activate.bat
python api.py

# Terminal 2: Backend
cd "C:\Major Project\backend"
run_backend.bat

# Terminal 3: Frontend
cd "C:\Major Project\raga-rasa-soul-main"
npm run dev
```
